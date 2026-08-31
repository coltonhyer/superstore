#!/usr/bin/env python3
"""Run portable skill eval cases against local agent CLIs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid

if __package__:
    from .skill_eval_core import (
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


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


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
    credentials: set[str] = set()
    discard_workspace = False
    with tempfile.TemporaryDirectory(prefix="superstore-eval-state-") as temporary:
        state = Path(temporary)
        seed_auth(host, state, home)
        auth_path = state / AUTH_FILES[host]
        credentials.update(credential_values(auth_path))
        try:
            for index, user_message in enumerate(
                (case.prompt, *case.replies), start=1
            ):
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
                code, raw_stdout, raw_stderr, duration = run_turn(
                    container_command(
                        command,
                        prepared.workspace,
                        state,
                        container_name=container_name,
                        timeout=timeout,
                    ),
                    prepared.workspace,
                    timeout + 30,
                    container_name=container_name,
                )
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
                if host == "codex":
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
        "turns": [public_turn(turn) for turn in turns],
    }
    write_json(result_dir / "result.json", result)
    return result


def parse_args(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plugin",
        type=Path,
        default=ROOT / "plugins/planning",
        help="plugin directory containing skill evals",
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
    args = parse_args(arguments or sys.argv[1:])
    plugin_root = args.plugin.resolve()
    cases = load_cases(plugin_root)
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
    print(f"Results: {output}")

    errors, results = 0, []
    for host in dict.fromkeys(args.host):
        model = getattr(args, f"{host}_model")
        effort = getattr(args, f"{host}_effort")
        for case in cases:
            print(f"Running {case.key} on {host} ({model}, {effort})...", flush=True)
            try:
                result = run_case(
                    ROOT,
                    plugin_root,
                    case,
                    host,
                    output,
                    args.timeout,
                    model,
                    effort,
                )
            except (OSError, RuntimeError, ValueError) as error:
                errors += 1
                print(f"ERROR {case.key} on {host}: {error}", file=sys.stderr)
                continue
            print(f"{result['status'].upper()} {case.key} on {host}")
            errors += result["status"] == "error"
            results.append(
                {
                    "case": case.key,
                    "host": host,
                    "status": result["status"],
                }
            )

    write_json(
        output / "summary.json",
        {
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "errors": errors,
            "results": results,
        },
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
