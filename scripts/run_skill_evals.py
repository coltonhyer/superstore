#!/usr/bin/env python3
"""Run portable skill eval cases against local agent CLIs."""

from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import uuid

if __package__:
    from .skill_eval_core import (
        EVAL_USER_EMAIL,
        EVAL_USER_NAME,
        EvalCase,
        build_prompt,
        collect_evidence,
        load_cases,
        prepare_workspace,
    )
    from .skill_eval_hosts import (
        HOSTS,
        build_command,
        build_resume_command,
        extract_result,
    )
else:
    from skill_eval_core import (  # type: ignore[no-redef]
        EVAL_USER_EMAIL,
        EVAL_USER_NAME,
        EvalCase,
        build_prompt,
        collect_evidence,
        load_cases,
        prepare_workspace,
    )
    from skill_eval_hosts import (  # type: ignore[no-redef]
        HOSTS,
        build_command,
        build_resume_command,
        extract_result,
    )


ROOT = Path(__file__).resolve().parents[1]
IMAGE = "superstore-skill-evals:dev"
CONTAINER_WORKSPACE = Path("/workspace")
AUTH_FILES = {
    "codex": Path(".codex/auth.json"),
    "claude": Path(".claude/.credentials.json"),
    "agy": Path(".gemini/antigravity-cli/antigravity-oauth-token"),
}

# Hosts run side by side; one host runs at most this many cases at once.
MAX_SESSIONS_PER_HOST = 4
# A case's window ends this long after its worst end (start + turns x
# (timeout + TURN_OVERHEAD_SECONDS)); the login must stay valid until then
# for the case to run alongside other cases of its host.
WINDOW_MARGIN_SECONDS = 600
TURN_OVERHEAD_SECONDS = 30

# Login refresh rules of the CLIs pinned in evals/Dockerfile, confirmed by
# reading each CLI. A host runs cases side by side only when its rule here
# is time-based on the expiry the runner reads; every other host runs one
# case at a time. Each rule refreshes well inside WINDOW_MARGIN_SECONDS.
#
# host    version  rule                                    source
# claude  2.1.251  refresh when Date.now() + 300000 >=     the native `claude` binary of the npm
#                  claudeAiOauth.expiresAt (within 5 min   package in the image (2.1.251 ships no
#                  of expiry, or past it)                  cli.js); its embedded JS: the predicate
#                                                          behind checkAndRefreshOAuthTokenIfNeeded
# codex   0.155.0  refresh when the access_token JWT exp   openai/codex tag rust-v0.155.0,
#                  <= now + 5 min; with no exp claim, when codex-rs/login/src/auth/manager.rs,
#                  last_refresh is older than 8 days       should_refresh_proactively and the
#                  (TOKEN_REFRESH_INTERVAL)                constants above it
# agy     1.4.0    refresh when token.expiry is within     /usr/local/bin/agy in the image links
#                  5 min (ReuseTokenSourceWithExpiry with  google3/third_party/golang/oauth2, the
#                  a 300 s delta) when saving the stored   vendored golang.org/x/oauth2; its
#                  token, and within 10 s (the default     function table and disassembly of
#                  expiryDelta) when validating it         codeassistclient.RefreshingTokenSource,
#                                                          auth.ValidateStoredToken, Token.expired
REFRESH_RULE_CONFIRMED = frozenset({"claude", "codex", "agy"})
CODEX_REFRESH_INTERVAL = timedelta(days=8)

PRINT_LOCK = threading.Lock()
WRITE_LOCKS = {host: threading.Lock() for host in AUTH_FILES}
TRACKED_CONTAINERS: set[str] = set()
STOP = threading.Event()  # set on interrupt: no further turn or case starts


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def say(message: str, file=None) -> None:
    with PRINT_LOCK:
        print(message, file=file or sys.stdout, flush=True)


def terminate_on_signal(signum: int, _frame: object) -> None:
    raise SystemExit(128 + signum)


def codex_rollout_trace(state: Path, session_id: str) -> list[dict]:
    """Return the collaboration evidence omitted by Codex v2's JSON stream."""
    if not session_id:
        return []
    calls: dict[str, str] = {}
    trace: list[dict] = []
    collaboration_calls = {
        "close_agent",
        "followup_task",
        "interrupt_agent",
        "list_agents",
        "send_message",
        "spawn_agent",
        "wait_agent",
    }

    def object_value(value: object) -> dict:
        if isinstance(value, dict):
            return value
        if not isinstance(value, str):
            return {}
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    for rollout in sorted((state / ".codex/sessions").rglob(f"*{session_id}.jsonl")):
        for line in rollout.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("type") != "response_item":
                continue
            payload = record.get("payload", {})
            item_type = payload.get("type")
            if item_type == "function_call":
                name = payload.get("name")
                if name not in collaboration_calls:
                    continue
                calls[payload.get("call_id", "")] = name
                arguments = object_value(payload.get("arguments"))
                trace.append(
                    {
                        "event": name,
                        **{
                            key: value
                            for key, value in arguments.items()
                            if key not in {"message", "prompt"}
                        },
                    }
                )
            elif item_type == "function_call_output":
                name = calls.get(payload.get("call_id", ""))
                if not name:
                    continue
                trace.append(
                    {
                        "event": f"{name}_result",
                        **object_value(payload.get("output")),
                    }
                )
            elif item_type == "agent_message":
                texts = [
                    item.get("text", "")
                    for item in payload.get("content", ())
                    if item.get("type") == "input_text" and item.get("text")
                ]
                if texts:
                    trace.append(
                        {"event": "reviewer_message", "text": "\n".join(texts)}
                    )
    return trace


def agy_brain_trace(state: Path, seen: set[str]) -> list[dict]:
    """Return Antigravity subagent transcripts and inter-agent messages.

    The stream-json output records that a subagent was invoked but not what it
    said; the CLI keeps that under the disposable state's ``brain`` directory.
    """
    brain = state / ".gemini/antigravity-cli/brain"
    trace: list[dict] = []
    for conversation in sorted(brain.glob("*")) if brain.is_dir() else []:
        logs = conversation / ".system_generated/logs"
        transcript = logs / "transcript_full.jsonl"
        if not transcript.is_file():
            transcript = logs / "transcript.jsonl"
        if transcript.is_file():
            for line in transcript.read_text(encoding="utf-8", errors="replace").splitlines():
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                key = f"{conversation.name}:step:{record.get('step_index')}"
                if key in seen:
                    continue
                seen.add(key)
                trace.append({"event": "transcript_step", "conversation": conversation.name, **record})
        for message in sorted((conversation / ".system_generated/messages").glob("*.json")):
            key = f"message:{message.name}"
            if key in seen:
                continue
            try:
                record = json.loads(message.read_text(encoding="utf-8", errors="replace"))
            except json.JSONDecodeError:
                continue
            if not isinstance(record, dict) or "content" not in record:
                continue
            seen.add(key)
            trace.append(
                {
                    "event": "message",
                    "sender": record.get("sender"),
                    "recipient": record.get("recipient"),
                    "title": (record.get("renderDetails") or {}).get("messageTitle"),
                    "content": record.get("content"),
                }
            )
    return trace


def seed_auth(host: str, state: Path, home: Path | None = None) -> None:
    relative = AUTH_FILES[host]
    source = (home or Path.home()).expanduser().resolve() / relative
    if not source.is_file():
        raise ValueError(f"existing {host} CLI credential is unavailable: {source}")
    destination = state / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    destination.chmod(0o600)


def persist_auth(host: str, state: Path, home: Path | None = None) -> None:
    relative = AUTH_FILES[host]
    source = state / relative
    if not source.is_file():
        raise ValueError(f"subject credential disappeared during the eval: {source}")
    destination = (home or Path.home()).expanduser().resolve() / relative
    with WRITE_LOCKS[host]:
        if not destination.is_file():
            raise ValueError(f"existing {host} CLI credential disappeared: {destination}")
        if source.stat().st_mtime_ns <= destination.stat().st_mtime_ns:
            return
        temporary = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.tmp")
        try:
            shutil.copy2(source, temporary)
            temporary.chmod(0o600)
            os.replace(temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)


def parse_rfc3339(value: str) -> datetime:
    """Parse an RFC 3339 time, trimming fractional seconds beyond microseconds."""
    value = re.sub(r"\.(\d{6})\d+", r".\1", value.strip())
    if value.endswith(("Z", "z")):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def jwt_expiry(token: str) -> datetime | None:
    """Return a JWT's `exp` claim, decoded locally without verification."""
    parts = token.split(".")
    if len(parts) != 3:
        return None
    payload = parts[1] + "=" * (-len(parts[1]) % 4)
    claims = json.loads(base64.urlsafe_b64decode(payload))
    exp = claims.get("exp") if isinstance(claims, dict) else None
    if isinstance(exp, bool) or not isinstance(exp, (int, float)):
        return None
    return datetime.fromtimestamp(exp, timezone.utc)


def login_expiry(host: str, home: Path | None = None) -> datetime | None:
    """Return when the host's login in the home directory expires, if readable.

    Only the expiry fields are read; token values never leave this function.
    """
    path = (home or Path.home()).expanduser().resolve() / AUTH_FILES[host]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if host == "claude":
            expires_at = data["claudeAiOauth"]["expiresAt"]
            if isinstance(expires_at, bool) or not isinstance(expires_at, (int, float)):
                return None
            return datetime.fromtimestamp(expires_at / 1000, timezone.utc)
        if host == "codex":
            candidates = []
            access_token = data.get("tokens", {}).get("access_token")
            if isinstance(access_token, str):
                exp = jwt_expiry(access_token)
                if exp:
                    candidates.append(exp)
            last_refresh = data.get("last_refresh")
            if isinstance(last_refresh, str):
                candidates.append(parse_rfc3339(last_refresh) + CODEX_REFRESH_INTERVAL)
            return min(candidates) if candidates else None
        if host == "agy":
            return parse_rfc3339(data["token"]["expiry"])
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None
    return None


def credential_values(path: Path) -> set[str]:
    """Return exact values worth removing from retained eval artifacts."""
    try:
        raw = path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return set()
    if not raw:
        return set()

    values = {raw}

    def collect(value: object, sensitive: bool = False) -> None:
        if isinstance(value, str):
            if sensitive and value:
                values.add(value)
        elif isinstance(value, dict):
            for key, item in value.items():
                normalized = "".join(
                    character
                    for character in key.lower()
                    if character.isalnum()
                )
                collect(
                    item,
                    any(
                        marker in normalized
                        for marker in (
                            "token",
                            "secret",
                            "password",
                            "apikey",
                            "credential",
                        )
                    )
                    and normalized != "tokentype",
                )
        elif isinstance(value, list):
            for item in value:
                collect(item, sensitive)

    try:
        parsed = json.loads(raw)
        collect(parsed, isinstance(parsed, str))
    except json.JSONDecodeError:
        pass
    return values


def credential_patterns(values: set[str]) -> list[str]:
    patterns = set(values)
    patterns.update(json.dumps(value)[1:-1] for value in values)
    return sorted((item for item in patterns if item), key=len, reverse=True)


def redact_credentials(value: object, credentials: set[str]) -> object:
    if isinstance(value, str):
        for pattern in credential_patterns(credentials):
            value = value.replace(pattern, "[REDACTED]")
        return value
    if isinstance(value, dict):
        return {
            key: redact_credentials(item, credentials)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_credentials(item, credentials) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_credentials(item, credentials) for item in value)
    return value


def find_credential_files(workspace: Path, credentials: set[str]) -> list[str]:
    patterns = credential_patterns(credentials)
    if not patterns or not workspace.is_dir():
        return []
    encoded_patterns = [item.encode() for item in patterns]
    leaked = []
    for path in workspace.rglob("*"):
        relative = path.relative_to(workspace).as_posix()
        path_leak = any(pattern in relative for pattern in patterns)
        content_leak = False
        if not path.is_symlink() and path.is_file():
            try:
                content = path.read_bytes()
            except OSError:
                content = b""
            content_leak = any(pattern in content for pattern in encoded_patterns)
        if path_leak or content_leak:
            safe_relative = redact_credentials(relative, credentials)
            assert isinstance(safe_relative, str)
            leaked.append(safe_relative)
    return sorted(leaked)


def container_command(
    command: list[str],
    workspace: Path,
    state: Path,
    *,
    container_name: str,
    timeout: int = 600,
) -> list[str]:
    return [
        "docker",
        "run",
        "--rm",
        f"--name={container_name}",
        "--init",
        "--read-only",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges",
        f"--user={os.getuid()}:{os.getgid()}",
        "--pids-limit=512",
        "--tmpfs=/tmp:rw,nosuid,nodev",
        f"--mount=type=bind,src={workspace.resolve()},dst=/workspace",
        f"--mount=type=bind,src={state.resolve()},dst=/state",
        "--env=HOME=/state",
        f"--env=JJ_USER={EVAL_USER_NAME}",
        f"--env=JJ_EMAIL={EVAL_USER_EMAIL}",
        "--workdir=/workspace",
        IMAGE,
        "timeout",
        "--signal=TERM",
        "--kill-after=15s",
        f"{timeout}s",
        *command,
    ]


def build_image() -> None:
    completed = subprocess.run(
        ["docker", "build", "--quiet", "--tag", IMAGE, "."],
        cwd=ROOT / "evals",
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(f"eval image build failed:\n{completed.stderr}")


def review_context(case: EvalCase) -> dict:
    return {
        "case": case.key,
        "request": case.prompt,
        "replies": list(case.replies),
        "author_guidance": {
            "authority": "advisory",
            "intended_behavior": case.expected_output,
            "review_questions": list(case.expectations),
        },
    }


def output_text(value: str | bytes | None) -> str:
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return value or ""


def remove_container(container_name: str) -> None:
    try:
        subprocess.run(
            ["docker", "rm", "--force", container_name],
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        pass


def remove_tracked_containers() -> None:
    for container_name in sorted(TRACKED_CONTAINERS):
        remove_container(container_name)


def run_turn(
    command: list[str],
    workspace: Path,
    timeout: int,
    *,
    container_name: str | None = None,
) -> tuple[int, str, str, float]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=workspace,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        code, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
    except subprocess.TimeoutExpired as error:
        code = 124
        stdout, stderr = output_text(error.stdout), output_text(error.stderr)
    finally:
        if container_name:
            remove_container(container_name)
    return code, stdout, stderr, round(time.monotonic() - started, 3)


def public_turn(turn: dict) -> dict:
    return {
        key: value
        for key, value in turn.items()
        if key not in {"stdout", "stderr", "evidence"}
    }


def run_case(
    repo_root: Path,
    plugin_root: Path,
    case: EvalCase,
    host: str,
    output_root: Path,
    timeout: int,
    model: str | None = None,
    effort: str | None = None,
    home: Path | None = None,
) -> dict:
    result_dir = output_root / host / f"{case.skill}-{case.identifier}"
    result_dir.mkdir(parents=True, exist_ok=False)
    prepared = prepare_workspace(
        repo_root, plugin_root, case, result_dir / "workspace", host
    )
    initial_evidence = collect_evidence(prepared)
    write_json(result_dir / "initial.evidence.json", initial_evidence)
    prompt = build_prompt(case)

    turns, session_id, status = [], "", "captured"
    codex_trace_seen = 0
    agy_trace_seen: set[str] = set()
    credentials: set[str] = set()
    discard_workspace = False
    refreshed_login = False
    with tempfile.TemporaryDirectory(prefix="superstore-eval-state-") as temporary:
        state = Path(temporary)
        seed_auth(host, state, home)
        auth_path = state / AUTH_FILES[host]
        seeded_mtime_ns = auth_path.stat().st_mtime_ns
        credentials.update(credential_values(auth_path))
        try:
            for index, user_message in enumerate(
                (case.prompt, *case.replies), start=1
            ):
                if STOP.is_set():
                    status = "error"
                    break
                if index == 1:
                    command = build_command(
                        host,
                        CONTAINER_WORKSPACE,
                        prompt,
                        timeout,
                        model=model,
                        effort=effort,
                        persistent=bool(case.replies),
                    )
                    (result_dir / "prompt.txt").write_text(
                        command[-1], encoding="utf-8"
                    )
                elif session_id:
                    command = build_resume_command(
                        host,
                        session_id,
                        user_message,
                        timeout,
                        model=model,
                        effort=effort,
                    )
                else:
                    status = "error"
                    break

                container_name = f"superstore-eval-{uuid.uuid4().hex}"
                TRACKED_CONTAINERS.add(container_name)
                try:
                    code, raw_stdout, raw_stderr, duration = run_turn(
                        container_command(
                            command,
                            prepared.workspace,
                            state,
                            container_name=container_name,
                            timeout=timeout,
                        ),
                        prepared.workspace,
                        timeout + TURN_OVERHEAD_SECONDS,
                        container_name=container_name,
                    )
                finally:
                    TRACKED_CONTAINERS.discard(container_name)
                credentials.update(credential_values(auth_path))
                persist_auth(host, state, home)
                parsed = None
                parse_error = ""
                if not code:
                    try:
                        parsed = extract_result(host, raw_stdout)
                    except ValueError as error:
                        parse_error = str(error)
                if host == "codex":
                    trace_session_id = parsed.session_id if parsed else ""
                    trace_session_id = trace_session_id or session_id
                    cumulative_trace = codex_rollout_trace(state, trace_session_id)
                    provider_trace = cumulative_trace[codex_trace_seen:]
                    codex_trace_seen = len(cumulative_trace)
                elif host == "agy":
                    provider_trace = agy_brain_trace(state, agy_trace_seen)
                else:
                    provider_trace = []
                evidence = collect_evidence(prepared)
                raw_artifacts = {
                    "stdout": raw_stdout,
                    "stderr": raw_stderr,
                    "provider_trace": provider_trace,
                    "evidence": evidence,
                }
                artifacts = redact_credentials(raw_artifacts, credentials)
                assert isinstance(artifacts, dict)
                leaked_locations = (
                    ["retained artifacts"] if artifacts != raw_artifacts else []
                )
                leaked_files = find_credential_files(
                    prepared.workspace, credentials
                )
                if leaked_files:
                    leaked_locations.append("workspace: " + ", ".join(leaked_files))

                stdout = artifacts["stdout"]
                stderr = artifacts["stderr"]
                provider_trace = artifacts["provider_trace"]
                evidence = artifacts["evidence"]
                assert isinstance(stdout, str)
                assert isinstance(stderr, str)
                assert isinstance(provider_trace, list)
                assert isinstance(evidence, dict)

                prefix = f"turn-{index:02d}"
                (result_dir / f"{prefix}.stdout.jsonl").write_text(
                    stdout, encoding="utf-8"
                )
                (result_dir / f"{prefix}.stderr.txt").write_text(
                    stderr, encoding="utf-8"
                )
                if host in ("codex", "agy"):
                    write_json(
                        result_dir / f"{prefix}.provider.json", provider_trace
                    )
                write_json(result_dir / f"{prefix}.evidence.json", evidence)
                turn = {
                    "turn": index,
                    "user": user_message,
                    "returncode": code,
                    "duration_seconds": duration,
                    "stdout": stdout,
                    "stderr": stderr,
                    "provider_trace": provider_trace,
                    "evidence": evidence,
                }
                if leaked_locations:
                    turn["credential_error"] = leaked_locations
                    discard_workspace = True
                    status = "error"
                elif code:
                    status = "error"
                elif parse_error:
                    turn["parse_error"], status = parse_error, "error"
                else:
                    assert parsed is not None
                    turn["assistant"] = parsed.response
                    session_id = parsed.session_id or session_id
                turns.append(turn)
                if status == "error":
                    break
        finally:
            credentials.update(credential_values(auth_path))
            try:
                refreshed_login = (
                    auth_path.is_file()
                    and auth_path.stat().st_mtime_ns > seeded_mtime_ns
                )
                persist_auth(host, state, home)
            finally:
                if find_credential_files(prepared.workspace, credentials):
                    discard_workspace = True
                if discard_workspace and prepared.workspace.exists():
                    shutil.rmtree(prepared.workspace)

    write_json(result_dir / "review-context.json", review_context(case))
    result = {
        "case": case.key,
        "host": host,
        "model": model or HOSTS[host].model,
        "effort": effort or HOSTS[host].effort,
        "status": status,
        "session_id": session_id,
        "refreshed_login": refreshed_login,
        "turns": [public_turn(turn) for turn in turns],
    }
    write_json(result_dir / "result.json", result)
    return result


def plugin_root_of(case: EvalCase) -> Path:
    """Return the plugin a case belongs to: `<plugin>/skills/<skill>/evals`."""
    return case.definition_dir.parents[2]


def load_plugin_cases(plugin_roots: list[Path]) -> list[EvalCase]:
    """Load every plugin's cases, refusing a skill name two plugins share."""
    cases: list[EvalCase] = []
    owners: dict[str, Path] = {}
    for plugin_root in dict.fromkeys(plugin_roots):
        for case in load_cases(plugin_root):
            owner = owners.setdefault(case.skill, plugin_root)
            if owner != plugin_root:
                raise SystemExit(
                    f"skill {case.skill} is in both {owner} and {plugin_root}; "
                    "their result folders would collide"
                )
            cases.append(case)
    return sorted(cases, key=lambda case: (case.skill, case.identifier))


@dataclass
class Lane:
    """One host's scheduling state."""

    host: str
    serial: bool = False
    condition: threading.Condition = field(default_factory=threading.Condition)
    running: int = 0
    alone: bool = False


def window_holds(case: EvalCase, timeout: int, expiry: datetime | None) -> bool:
    if expiry is None:
        return False
    turns = 1 + len(case.replies)
    worst_end = datetime.now(timezone.utc) + timedelta(
        seconds=turns * (timeout + TURN_OVERHEAD_SECONDS)
    )
    return expiry >= worst_end + timedelta(seconds=WINDOW_MARGIN_SECONDS)


def run_one(
    lane: Lane,
    case: EvalCase,
    alone: bool,
    args: argparse.Namespace,
    output: Path,
    home: Path | None,
    slot: list,
) -> None:
    host = lane.host
    model = getattr(args, f"{host}_model")
    effort = getattr(args, f"{host}_effort")
    started = datetime.now(timezone.utc)
    clock = time.monotonic()
    result = None
    try:
        say(f"Running {case.key} on {host} ({model}, {effort})...")
        try:
            result = run_case(
                ROOT,
                plugin_root_of(case),
                case,
                host,
                output,
                args.timeout,
                model,
                effort,
                home,
            )
        except (OSError, RuntimeError, ValueError) as error:
            say(f"ERROR {case.key} on {host}: {error}", file=sys.stderr)
        else:
            say(f"{result['status'].upper()} {case.key} on {host}")
            slot[0] = {
                "case": case.key,
                "host": host,
                "status": result["status"],
                "started_at": started.isoformat(),
                "wall_seconds": round(time.monotonic() - clock, 3),
                "refreshed_login": bool(result.get("refreshed_login")),
            }
    finally:
        with lane.condition:
            lane.running -= 1
            if alone:
                lane.alone = False
            if result and result.get("refreshed_login") and not alone and not lane.serial:
                lane.serial = True
                say(
                    f"WARNING {host} refreshed its login during a parallel case; "
                    "it now runs one case at a time",
                    file=sys.stderr,
                )
            lane.condition.notify_all()


def run_host(
    lane: Lane,
    cases: list[EvalCase],
    args: argparse.Namespace,
    output: Path,
    home: Path | None,
    stop: threading.Event,
    results: list,
) -> None:
    workers = []
    for index, case in enumerate(cases):
        with lane.condition:
            while True:
                if stop.is_set():
                    break
                alone = (
                    index == 0
                    or lane.serial
                    or not window_holds(case, args.timeout, login_expiry(lane.host, home))
                )
                if alone and lane.running == 0:
                    break
                if not alone and not lane.alone and lane.running < MAX_SESSIONS_PER_HOST:
                    break
                lane.condition.wait()
            if stop.is_set():
                break
            lane.running += 1
            lane.alone = alone
        worker = threading.Thread(
            target=run_one,
            args=(lane, case, alone, args, output, home, results[index]),
            name=f"{lane.host}-{case.key}",
        )
        worker.start()
        workers.append(worker)
    for worker in workers:
        worker.join()


def run_all(
    args: argparse.Namespace,
    cases: list[EvalCase],
    output: Path,
    home: Path | None = None,
) -> list[dict]:
    """Run every case on every host; return results by host, then case order."""
    stop = STOP
    stop.clear()
    lanes, slots = [], {}
    # Each host thread sets its own `done` event when it ends. The main thread
    # only reads these, so a signal landing anywhere costs at most one wait
    # interval, never a count. Thread.is_alive() is not usable here: on
    # CPython 3.12 a signal that interrupts a timed join leaves the thread
    # marked stopped while it still runs.
    hosts: list[tuple[threading.Thread, threading.Event]] = []

    def host_thread(done: threading.Event, *host_args) -> None:
        try:
            run_host(*host_args)
        finally:
            done.set()

    try:
        for host in dict.fromkeys(args.host):
            lane = Lane(host)
            if host not in REFRESH_RULE_CONFIRMED:
                lane.serial = True
                say(f"{host} runs one case at a time: its login refresh rule is not confirmed")
            elif login_expiry(host, home) is None:
                lane.serial = True
                say(f"{host} runs one case at a time: its login expiry cannot be read")
            lanes.append(lane)
            slots[host] = [[None] for _ in cases]
            done = threading.Event()
            thread = threading.Thread(
                target=host_thread,
                args=(done, lane, cases, args, output, home, stop, slots[host]),
                name=host,
            )
            hosts.append((thread, done))  # recorded before it can start
            thread.start()
        for _thread, done in hosts:
            while not done.wait(0.2):  # a timed wait lets the main thread handle signals
                pass
    except BaseException:
        # An interrupt, or any failure while starting hosts. Finish cleanup
        # even if another signal arrives: stop new cases and turns, keep
        # dropping containers until every host thread has ended, which is
        # after its cases wrote back and discarded their workspaces.
        # A recorded thread that never started (ident None) has nothing to
        # clean up; one that starts later sees `stop` and runs no case.
        for signum in (signal.SIGTERM, signal.SIGINT):
            signal.signal(signum, signal.SIG_IGN)
        stop.set()
        for lane in lanes:
            with lane.condition:
                lane.condition.notify_all()
        while True:
            remove_tracked_containers()
            pending = [
                done for thread, done in hosts
                if thread.ident is not None and not done.is_set()
            ]
            if not pending:
                break
            pending[0].wait(0.5)
        raise
    return [slot[0] for host in slots for slot in slots[host] if slot[0]]


def parse_args(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plugin",
        action="append",
        type=Path,
        help="plugin directory containing skill evals (repeatable; default plugins/planning)",
    )
    parser.add_argument("--host", action="append", choices=sorted(HOSTS))
    parser.add_argument("--skill", action="append")
    parser.add_argument("--case", action="append", type=int, dest="case_ids")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--list", action="store_true", dest="list_cases")
    for host, config in HOSTS.items():
        parser.add_argument(f"--{host}-model", default=config.model)
        parser.add_argument(f"--{host}-effort", default=config.effort)
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    signal.signal(signal.SIGTERM, terminate_on_signal)
    signal.signal(signal.SIGINT, terminate_on_signal)
    args = parse_args(arguments or sys.argv[1:])
    plugin_roots = [
        plugin.resolve() for plugin in (args.plugin or [ROOT / "plugins/planning"])
    ]
    cases = load_plugin_cases(plugin_roots)
    if args.skill:
        cases = [case for case in cases if case.skill in args.skill]
    if args.case_ids:
        cases = [case for case in cases if case.identifier in args.case_ids]

    if args.list_cases:
        for case in cases:
            turns = 1 + len(case.replies)
            print(f"{case.key}\t{turns} turn{'s' if turns != 1 else ''}")
        return 0
    if not args.host:
        raise SystemExit("at least one --host is required unless --list is used")
    if not cases:
        raise SystemExit("no eval cases matched")
    required = {"docker", "jj"}
    for command in sorted(required):
        if not shutil.which(command):
            raise SystemExit(f"required command is unavailable: {command}")

    print(f"Building {IMAGE}...", flush=True)
    try:
        build_image()
    except RuntimeError as error:
        raise SystemExit(str(error)) from error

    output = (
        args.output or Path(tempfile.mkdtemp(prefix="superstore-evals-"))
    ).resolve()
    output.mkdir(parents=True, exist_ok=True)
    print(f"Results: {output}", flush=True)

    started = datetime.now(timezone.utc)
    clock = time.monotonic()
    results = run_all(args, cases, output)
    wall = round(time.monotonic() - clock, 3)
    captured = sum(result["status"] == "captured" for result in results)
    errors = len(cases) * len(dict.fromkeys(args.host)) - captured
    say(f"Captured {captured}, errors {errors}, wall {wall:.0f}s")

    write_json(
        output / "summary.json",
        {
            "started_at": started.isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "wall_seconds": wall,
            "errors": errors,
            "results": results,
        },
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
