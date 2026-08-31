"""Agent CLI commands and event-stream normalization for skill evals."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class HostConfig:
    model: str
    effort: str


@dataclass(frozen=True)
class TurnResult:
    response: str
    session_id: str


HOSTS = {
    "codex": HostConfig("gpt-5.6-terra", "high"),
    "claude": HostConfig("claude-sonnet-5", "high"),
    "agy": HostConfig("gemini-3.7-flash-high", "high"),
}

def build_command(
    host: str,
    workspace: Path,
    prompt: str,
    timeout: int,
    *,
    model: str | None = None,
    effort: str | None = None,
    persistent: bool = False,
) -> list[str]:
    config = HOSTS[host]
    model, effort = model or config.model, effort or config.effort

    if host == "codex":
        command = [
            "codex", "exec", "--json", "--ignore-user-config", "--ignore-rules",
            "--enable", "multi_agent_v2",
            "--dangerously-bypass-approvals-and-sandbox",
            "--skip-git-repo-check", "-m", model, "-c",
            f'model_reasoning_effort="{effort}"', "-C", str(workspace),
        ]
        return [*command, prompt]

    if host == "claude":
        command = [
            "claude", "-p", "--output-format", "stream-json", "--verbose",
            "--safe-mode",
            "--dangerously-skip-permissions", "--model", model, "--effort", effort,
        ]
        return [*command, *([] if persistent else ["--no-session-persistence"]), prompt]

    if host == "agy":
        return [
            "agy", "--new-project", "--agent", "superstore-eval",
            "--disable-slash-commands", "--output-format", "stream-json",
            "--model", model, "--effort", effort, "--mode", "accept-edits",
            "--sandbox", "--dangerously-skip-permissions", "--print-timeout",
            f"{timeout}s", "--print", prompt,
        ]
    raise ValueError(f"unsupported host: {host}")


def build_resume_command(
    host: str,
    session_id: str,
    reply: str,
    timeout: int,
    *,
    model: str | None = None,
    effort: str | None = None,
) -> list[str]:
    config = HOSTS[host]
    model, effort = model or config.model, effort or config.effort

    if host == "codex":
        return [
            "codex", "exec", "resume", "--json",
            "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check",
            "--enable", "multi_agent_v2",
            "--dangerously-bypass-approvals-and-sandbox",
            "-m", model, "-c",
            f'model_reasoning_effort="{effort}"', session_id, reply,
        ]
    if host == "claude":
        return [
            "claude", "-p", "--resume", session_id, "--output-format",
            "stream-json", "--verbose", "--safe-mode",
            "--dangerously-skip-permissions", "--model",
            model, "--effort", effort, reply,
        ]
    if host == "agy":
        return [
            "agy", "--conversation", session_id, "--disable-slash-commands",
            "--output-format", "stream-json", "--model", model, "--effort",
            effort, "--mode", "accept-edits", "--sandbox",
            "--dangerously-skip-permissions", "--print-timeout", f"{timeout}s",
            "--print", reply,
        ]
    raise ValueError(f"unsupported host: {host}")


def parse_events(output: str) -> list[dict]:
    events = []
    for line in output.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            events.append(value)
    return events


def extract_result(host: str, output: str) -> TurnResult:
    session_id = response = ""
    for event in parse_events(output):
        if host == "codex":
            if event.get("type") == "thread.started":
                session_id = event.get("thread_id", session_id)
            item = event.get("item", {})
            if event.get("type") == "item.completed" and item.get("type") == "agent_message":
                response = item.get("text", response)
        elif host == "claude":
            session_id = event.get("session_id", session_id)
            if event.get("type") == "result":
                response = event.get("result", response)
        elif host == "agy":
            session_id = event.get("conversation_id", session_id)
            if event.get("event") == "result":
                result = event.get("result", {})
                session_id = result.get("conversation_id", session_id)
                response = result.get("response", response)
        else:
            raise ValueError(f"unsupported host: {host}")

    if not response:
        raise ValueError(f"no final response found in {host} output")
    return TurnResult(response.strip(), session_id)
