"""Portable eval cases, temporary workspaces, and repository evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess


AGY_EVAL_AGENT = """---
name: superstore-eval
description: Primary agent for behavioral skill evaluations.
mainAgent: true
subagent: false
inheritCustomizations: false
tools:
  - define_subagent
  - finish
  - grep_search
  - invoke_subagent
  - list_dir
  - replace_file_content
  - run_command
  - view_file
  - wait
  - write_to_file
---

Work only inside the current workspace and follow the user's supplied skill files.
"""


@dataclass(frozen=True)
class Fixture:
    source: Path
    target: Path
    state: str = "baseline"


@dataclass(frozen=True)
class EvalCase:
    skill: str
    identifier: int
    prompt: str
    expected_output: str
    expectations: tuple[str, ...]
    skills: tuple[str, ...]
    fixtures: tuple[Fixture, ...]
    replies: tuple[str, ...]
    definition_dir: Path = Path(".")
    skill_fixtures: dict[str, Path] = field(default_factory=dict)

    @property
    def key(self) -> str:
        return f"{self.skill}/{self.identifier}"


@dataclass(frozen=True)
class PreparedCase:
    case: EvalCase
    workspace: Path
    baseline_commit: str


def safe_relative(value: str, field: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{field} must be a relative path: {value}")
    return path


def safe_skill_fixture_name(name: object) -> str:
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
        raise ValueError(f"unsafe skill fixture name: {name}")
    return name


def parse_skill_fixtures(raw: object, skills: tuple[str, ...]) -> dict[str, Path]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("skill_fixtures must be an object")

    fixtures = {}
    for raw_name, raw_source in raw.items():
        name = safe_skill_fixture_name(raw_name)
        if name not in skills:
            raise ValueError(f"skill fixture {name} is not in the case inventory")
        if not isinstance(raw_source, str):
            raise ValueError(f"skill fixture source for {name} must be a path")
        fixtures[name] = safe_relative(raw_source, "skill fixture source")
    return fixtures


def parse_fixture(raw: str | dict) -> Fixture:
    if isinstance(raw, str):
        source = safe_relative(raw, "fixture source")
        return Fixture(source, Path(source.name))
    if not isinstance(raw, dict):
        raise ValueError("fixture must be a path or object")

    state = raw.get("state", "baseline")
    if state not in {"baseline", "working"}:
        raise ValueError(f"unsupported fixture state: {state}")
    return Fixture(
        safe_relative(raw["source"], "fixture source"),
        safe_relative(raw["target"], "fixture target"),
        state,
    )


def load_cases(plugin_root: Path) -> list[EvalCase]:
    cases = []
    seen = set()
    for path in sorted((plugin_root / "skills").glob("*/evals/evals.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        skill = data["skill_name"]
        if skill != path.parents[1].name:
            raise ValueError(f"skill_name does not match {path}")

        for raw in data["evals"]:
            key = (skill, raw["id"])
            if key in seen:
                raise ValueError(f"duplicate eval id: {skill}/{raw['id']}")
            seen.add(key)
            expectations = tuple(raw.get("expectations", ()))
            if not expectations:
                raise ValueError(f"eval has no expectations: {skill}/{raw['id']}")

            skills = [skill]
            skills.extend(raw.get("skills", ()))
            skills = tuple(dict.fromkeys(skills))
            cases.append(
                EvalCase(
                    skill,
                    raw["id"],
                    raw["prompt"],
                    raw["expected_output"],
                    expectations,
                    skills,
                    tuple(parse_fixture(item) for item in raw.get("files", ())),
                    tuple(raw.get("replies", ())),
                    path.parent,
                    parse_skill_fixtures(raw.get("skill_fixtures"), skills),
                )
            )
    return sorted(cases, key=lambda case: (case.skill, case.identifier))


def find_skill(repo_root: Path, plugin_root: Path, name: str) -> Path:
    preferred = plugin_root / "skills" / name
    if preferred.is_dir():
        return preferred
    matches = sorted((repo_root / "plugins").glob(f"*/skills/{name}"))
    if len(matches) != 1:
        raise ValueError(f"expected one source for skill {name}, found {len(matches)}")
    return matches[0]


def fixture_skill_source(case: EvalCase, name: str) -> Path:
    safe_skill_fixture_name(name)
    if name not in case.skills:
        raise ValueError(f"skill fixture {name} is not in the case inventory")
    relative = safe_relative(str(case.skill_fixtures[name]), "skill fixture source")
    root = case.definition_dir.resolve()
    source = case.definition_dir / relative

    def check_tree(path: Path) -> None:
        resolved = path.resolve()
        if not resolved.is_relative_to(root):
            raise ValueError(f"skill fixture {name} escapes the case directory")
        if path.is_symlink():
            raise ValueError(f"skill fixture {name} may not contain symlinks")
        if not path.is_dir():
            return
        for child in path.iterdir():
            check_tree(child)

    if not source.is_dir():
        raise ValueError(f"skill fixture directory does not exist: {source}")
    check_tree(source)
    if not (source / "SKILL.md").is_file():
        raise ValueError(f"skill fixture is missing SKILL.md: {source}")
    return source


def run_text(command: list[str], cwd: Path, check: bool = True) -> str:
    completed = subprocess.run(
        command, cwd=cwd, text=True, capture_output=True, check=False
    )
    if check and completed.returncode:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stdout={completed.stdout}\nstderr={completed.stderr}"
        )
    return completed.stdout


def copy_fixture(case: EvalCase, fixture: Fixture, workspace: Path) -> None:
    source = case.definition_dir / fixture.source
    if not source.is_file():
        raise ValueError(f"fixture does not exist: {source}")
    target = workspace / fixture.target
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def prepare_workspace(
    repo_root: Path,
    plugin_root: Path,
    case: EvalCase,
    destination: Path,
    host: str | None = None,
) -> PreparedCase:
    if destination.exists():
        raise ValueError(f"workspace already exists: {destination}")
    destination.mkdir(parents=True)
    run_text(["jj", "git", "init", "--colocate", "."], destination)

    if host == "agy":
        agent = destination / ".agents/agents/superstore-eval/agent.md"
        agent.parent.mkdir(parents=True)
        agent.write_text(AGY_EVAL_AGENT, encoding="utf-8")

    for name in case.skills:
        source = (
            fixture_skill_source(case, name)
            if name in case.skill_fixtures
            else find_skill(repo_root, plugin_root, name)
        )
        shutil.copytree(
            source,
            destination / ".eval/skills" / name,
            ignore=shutil.ignore_patterns("evals"),
        )
    for fixture in case.fixtures:
        if fixture.state == "baseline":
            copy_fixture(case, fixture, destination)

    run_text(["jj", "commit", "-m", "eval fixture"], destination)
    baseline = run_text(
        ["jj", "log", "-r", "@-", "--no-graph", "-T", "commit_id"],
        destination,
    ).strip()
    for fixture in case.fixtures:
        if fixture.state == "working":
            copy_fixture(case, fixture, destination)
    return PreparedCase(case, destination, baseline)


def build_prompt(case: EvalCase) -> str:
    inventory = "\n".join(
        f"- {name}: .eval/skills/{name}/SKILL.md" for name in case.skills
    )
    attachments = "\n".join(f"- {item.target.as_posix()}" for item in case.fixtures)
    return (
        "You are running one behavioral evaluation in a temporary repository.\n"
        "Read every listed SKILL.md completely before acting and follow the skill "
        "that applies to the request. Treat this list as the complete active skill "
        "inventory for the run; do not infer skills from other directories.\n\n"
        f"Active skill inventory:\n{inventory}\n\n"
        f"Attached repository files:\n{attachments or '- None'}\n\n"
        "This repository uses Jujutsu for version control. Use `jj`, not Git, "
        "for status, history, and commits.\n\n"
        "Complete only the request below. Work naturally: do not discuss the eval "
        "harness, inspect evaluation definitions, or invent unavailable skills.\n\n"
        f"User request:\n{case.prompt}"
    )


def file_manifest(workspace: Path) -> list[dict]:
    files = []
    for path in sorted(item for item in workspace.rglob("*") if item.is_file()):
        relative = path.relative_to(workspace)
        if relative.parts[0] in {".eval", ".git", ".jj"}:
            continue
        if relative.parts[:3] == (".agents", "agents", "superstore-eval"):
            continue
        raw = path.read_bytes()
        files.append(
            {
                "path": relative.as_posix(),
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    return files


def collect_evidence(prepared: PreparedCase) -> dict:
    run_text(["jj", "git", "import"], prepared.workspace, check=False)
    baseline = prepared.baseline_commit
    commands = {
        "status": ["jj", "status"],
        "committed_after_baseline": [
            "jj", "log", "-r", f"{baseline}..@-", "--no-graph", "-T",
            'commit_id.short() ++ " " ++ description.first_line() ++ "\\n"',
        ],
        "diff": ["jj", "diff", "--from", baseline, "--to", "@"],
    }
    evidence = {
        name: run_text(command, prepared.workspace, check=False)
        for name, command in commands.items()
    }
    evidence["files"] = file_manifest(prepared.workspace)
    return evidence
