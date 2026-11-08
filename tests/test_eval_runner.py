import base64
from collections import Counter
import contextlib
from datetime import datetime, timedelta, timezone
import io
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tempfile
import threading
import time
import unittest
from unittest import mock

from scripts import run_skill_evals as runner
from scripts.skill_eval_core import EvalCase, Fixture, run_text
from scripts.skill_eval_hosts import TurnResult


ROOT = Path(__file__).resolve().parents[1]
PLANNING = ROOT / "plugins/planning"
IMPLEMENTATION = ROOT / "plugins/implementation"
MAINTENANCE = ROOT / "plugins/maintenance"
REVIEW_SESSION_ID = "01a04fb2-ec55-7110-9805-d36e97f4c50d"
MARKDOWN_LINK = re.compile(r"\]\(([^)]+\.md)\)")


def response_item(item_type: str, **fields) -> dict:
    return {"type": "response_item", "payload": {"type": item_type, **fields}}


REVIEW_ROLLOUT = (
    response_item(
        "function_call",
        name="spawn_agent",
        call_id="spawn-1",
        arguments=json.dumps(
            {
                "task_name": "spec_review",
                "fork_turns": "all",
                "message": "encrypted-review-prompt",
            }
        ),
    ),
    response_item(
        "function_call_output",
        call_id="spawn-1",
        output='{"task_name":"/root/spec_review"}',
    ),
    response_item(
        "function_call",
        name="wait_agent",
        call_id="wait-1",
        arguments='{"timeout_ms":120000}',
    ),
    response_item(
        "function_call_output",
        call_id="wait-1",
        output='{"message":"Wait completed.","timed_out":false}',
    ),
    response_item(
        "agent_message",
        content=[
            {
                "type": "input_text",
                "text": (
                    "Message Type: FINAL_ANSWER\n"
                    "Sender: /root/spec_review\n"
                    "Payload:\nNo material findings."
                ),
            }
        ],
    ),
)


def write_codex_review_rollout(
    state: Path, records: tuple[dict, ...] = REVIEW_ROLLOUT
) -> None:
    rollout = (
        state
        / ".codex/sessions/2026/08/29"
        / f"rollout-{REVIEW_SESSION_ID}.jsonl"
    )
    rollout.parent.mkdir(parents=True, exist_ok=True)
    rollout.write_text(
        "\n".join(json.dumps(record) for record in records),
        encoding="utf-8",
    )


def eval_case(**overrides) -> EvalCase:
    values = {
        "skill": "specs",
        "identifier": 1,
        "prompt": "Prompt",
        "expected_output": "Expected",
        "expectations": ("Criterion",),
        "skills": ("specs",),
        "fixtures": (),
        "replies": (),
    }
    values.update(overrides)
    return EvalCase(**values)


def planning_case(skill: str, identifier: int) -> EvalCase:
    return next(
        case
        for case in runner.load_cases(PLANNING)
        if (case.skill, case.identifier) == (skill, identifier)
    )


def write_test_auth(host: str, state: Path, token: str) -> None:
    path = state / runner.AUTH_FILES[host]
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"access_token": token}), encoding="utf-8")


class EvalCaseTests(unittest.TestCase):
    def test_load_cases_rejects_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as temporary:
            plugin = Path(temporary)
            evals = plugin / "skills/requirements/evals"
            evals.mkdir(parents=True)
            (evals / "evals.json").write_text(
                json.dumps(
                    {
                        "skill_name": "requirements",
                        "evals": [
                            self.case(1),
                            self.case(1),
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "duplicate eval id"):
                runner.load_cases(plugin)

    def test_prompt_exposes_skills_and_fixtures_but_not_review_guidance(self):
        case = EvalCase(
            skill="requirements",
            identifier=2,
            prompt="Inspect the attached repository context.",
            expected_output="SECRET EXPECTED OUTPUT",
            expectations=("SECRET CRITERION",),
            skills=("requirements", "library"),
            fixtures=(
                Fixture(
                    source=Path("files/project.toml"),
                    target=Path("project.toml"),
                    state="baseline",
                ),
            ),
            replies=(),
        )

        prompt = runner.build_prompt(case)

        self.assertIn(".eval/skills/requirements/SKILL.md", prompt)
        self.assertIn(".eval/skills/library/SKILL.md", prompt)
        self.assertIn("project.toml", prompt)
        self.assertIn("uses Jujutsu", prompt)
        self.assertIn(case.prompt, prompt)
        self.assertNotIn(case.expected_output, prompt)
        self.assertNotIn(case.expectations[0], prompt)

    def test_review_context_marks_author_guidance_as_advisory(self):
        case = eval_case(
            prompt="Review this behavior.",
            expected_output="One plausible outcome.",
            expectations=("Check the workflow boundary",),
            replies=("Approved.",),
        )

        self.assertEqual(
            runner.review_context(case),
            {
                "case": "specs/1",
                "request": "Review this behavior.",
                "replies": ["Approved."],
                "author_guidance": {
                    "authority": "advisory",
                    "intended_behavior": "One plausible outcome.",
                    "review_questions": ["Check the workflow boundary"],
                },
            },
        )

    def test_additional_skills_are_scoped_to_the_declaring_case(self):
        self.assertEqual(
            planning_case("specs", 1).skills,
            ("specs", "requirements"),
        )
        self.assertEqual(planning_case("specs", 2).skills, ("specs",))

    def test_coding_standards_check_fixture_depends_on_source_content(self):
        fixture = (
            MAINTENANCE
            / "skills/reviewing-coding-standards/evals/files/checks"
        )
        command = [
            "python3",
            str(fixture / "standards_check.py"),
            "--config",
            str(fixture / "standards-check.json"),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "subject.py"
            source.write_text("EXPLICIT_BAD = 1\nWARN_BAD = 2\n", encoding="utf-8")

            failing = subprocess.run(
                [*command, str(source)], text=True, capture_output=True, check=False
            )
            source.write_text("GOOD = 1\n", encoding="utf-8")
            passing = subprocess.run(
                [*command, str(source)], text=True, capture_output=True, check=False
            )

        self.assertEqual(failing.returncode, 1)
        self.assertIn("subject.py:1: explicit-obligation [warn]", failing.stdout)
        self.assertIn("subject.py:2: configured-warn [warn]", failing.stdout)
        self.assertEqual((passing.returncode, passing.stdout), (0, ""))

    @staticmethod
    def case(identifier):
        return {
            "id": identifier,
            "prompt": "Prompt",
            "expected_output": "Expected",
            "files": [],
            "expectations": ["Criterion"],
        }


@unittest.skipUnless(shutil.which("jj"), "Jujutsu is required")
class WorkspaceTests(unittest.TestCase):
    def test_maintenance_cases_prepare_fixtures_prompts_and_private_links(self):
        cases = runner.load_cases(MAINTENANCE)
        setup = [
            case for case in cases if case.skill == "setting-up-coding-standards"
        ]
        audits = [
            case for case in cases if case.skill == "reviewing-coding-standards"
        ]
        self.assertEqual([case.identifier for case in setup], list(range(1, 17)))
        self.assertEqual([case.identifier for case in audits], list(range(1, 11)))
        self.assertTrue(
            all("setting-up-coding-standards" in case.skills for case in audits)
        )
        for case in cases:
            with tempfile.TemporaryDirectory() as temporary, self.subTest(case=case.key):
                prepared = runner.prepare_workspace(
                    ROOT, MAINTENANCE, case, Path(temporary) / "workspace"
                )
                final_sources = {item.target: item.source for item in case.fixtures}
                for target, source in final_sources.items():
                    self.assertEqual(
                        (prepared.workspace / target).read_bytes(),
                        (case.definition_dir / source).read_bytes(),
                        str(target),
                    )
                prompt = runner.build_prompt(case)
                self.assertTrue(prompt.endswith(case.prompt))
                for fixture in case.fixtures:
                    self.assertIn(str(fixture.target), prompt)
                working = [
                    fixture.target
                    for fixture in case.fixtures
                    if fixture.state == "working"
                ]
                if working:
                    status = runner.collect_evidence(prepared)["status"]
                    for target in working:
                        self.assertIn(str(target), status)
                skills = prepared.workspace / ".eval/skills"
                self.assertFalse(list(skills.rglob("evals")))
                for markdown in skills.rglob("*.md"):
                    prose = re.sub(
                        r"(?ms)^(`{3,})[^\n]*\n.*?^\1\s*$", "",
                        markdown.read_text(encoding="utf-8"),
                    )
                    for target in MARKDOWN_LINK.findall(prose):
                        self.assertTrue(
                            (markdown.parent / target).is_file(),
                            f"{markdown.relative_to(skills)} -> {target}",
                        )

    def test_implementation_case_skill_links_resolve_in_copied_layout(self):
        for case in runner.load_cases(IMPLEMENTATION):
            with tempfile.TemporaryDirectory() as temporary, self.subTest(case=case.key):
                prepared = runner.prepare_workspace(
                    ROOT, IMPLEMENTATION, case, Path(temporary) / "workspace"
                )
                skills = prepared.workspace / ".eval/skills"
                for markdown in skills.rglob("*.md"):
                    for target in MARKDOWN_LINK.findall(markdown.read_text(encoding="utf-8")):
                        self.assertTrue(
                            (markdown.parent / target).is_file(),
                            f"{markdown.relative_to(skills)} -> {target}",
                        )

    def test_case_local_skill_fixture_replaces_only_its_listed_skill(self):
        with tempfile.TemporaryDirectory() as temporary:
            plugin = Path(temporary) / "plugin"
            definition_dir = plugin / "skills/specs/evals"
            fixture = definition_dir / "files/debugging"
            fixture.mkdir(parents=True)
            (fixture / "SKILL.md").write_text(
                "---\nname: debugging\ndescription: Test fixture.\n---\n\n# Fixture\n",
                encoding="utf-8",
            )
            (definition_dir / "evals.json").write_text(
                json.dumps(
                    {
                        "skill_name": "specs",
                        "evals": [{
                            "id": 1,
                            "prompt": "Prompt",
                            "expected_output": "Expected",
                            "expectations": ["Criterion"],
                            "skills": ["debugging"],
                            "skill_fixtures": {"debugging": "files/debugging"},
                        }],
                    }
                ),
                encoding="utf-8",
            )
            case = runner.load_cases(plugin)[0]

            prepared = runner.prepare_workspace(
                ROOT, PLANNING, case, Path(temporary) / "workspace"
            )

            self.assertIn("# Fixture", (prepared.workspace / ".eval/skills/debugging/SKILL.md").read_text(encoding="utf-8"))
            self.assertTrue((prepared.workspace / ".eval/skills/specs/SKILL.md").is_file())
            self.assertIn("- debugging: .eval/skills/debugging/SKILL.md", runner.build_prompt(case))

    def test_case_local_skill_fixture_is_absent_from_following_case(self):
        with tempfile.TemporaryDirectory() as temporary:
            first_definition = Path(temporary) / "first"
            fixture = first_definition / "files/debugging"
            fixture.mkdir(parents=True)
            (fixture / "SKILL.md").write_text("# Fixture\n", encoding="utf-8")
            first = eval_case(
                skills=("specs", "debugging"),
                definition_dir=first_definition,
                skill_fixtures={"debugging": Path("files/debugging")},
            )
            runner.prepare_workspace(ROOT, PLANNING, first, Path(temporary) / "first-workspace")
            second = eval_case(skills=("specs",))

            prepared = runner.prepare_workspace(
                ROOT, PLANNING, second, Path(temporary) / "second-workspace"
            )

            self.assertFalse((prepared.workspace / ".eval/skills/debugging").exists())
            self.assertNotIn("debugging", runner.build_prompt(second))

    def test_case_local_skill_fixture_rejects_invalid_and_escaping_sources(self):
        with tempfile.TemporaryDirectory() as temporary:
            plugin = Path(temporary) / "plugin"
            evals = plugin / "skills/specs/evals"
            evals.mkdir(parents=True)

            def definition(mapping):
                return {
                    "skill_name": "specs",
                    "evals": [{
                        "id": 1,
                        "prompt": "Prompt",
                        "expected_output": "Expected",
                        "expectations": ["Criterion"],
                        "skills": ["debugging"],
                        "skill_fixtures": mapping,
                    }],
                }

            for mapping, message in (
                ({"other": "files/debugging"}, "not in the case inventory"),
                ({"../debugging": "files/debugging"}, "unsafe skill fixture name"),
                ({"debugging": "../debugging"}, "relative path"),
            ):
                (evals / "evals.json").write_text(
                    json.dumps(definition(mapping)), encoding="utf-8"
                )
                with self.assertRaisesRegex(ValueError, message):
                    runner.load_cases(plugin)

            outside = Path(temporary) / "outside"
            outside.mkdir()
            (outside / "SKILL.md").write_text("# Outside\n", encoding="utf-8")
            linked = evals / "files/debugging"
            linked.parent.mkdir()
            linked.symlink_to(outside, target_is_directory=True)
            (evals / "evals.json").write_text(
                json.dumps(definition({"debugging": "files/debugging"})),
                encoding="utf-8",
            )
            case = runner.load_cases(plugin)[0]
            with self.assertRaisesRegex(ValueError, "escapes the case directory"):
                runner.prepare_workspace(ROOT, PLANNING, case, Path(temporary) / "workspace")

            linked.unlink()
            linked.mkdir()
            (linked / "SKILL.md").symlink_to(outside / "SKILL.md")
            with self.assertRaisesRegex(ValueError, "escapes the case directory"):
                runner.prepare_workspace(ROOT, PLANNING, case, Path(temporary) / "linked-workspace")

            (linked / "SKILL.md").unlink()
            with self.assertRaisesRegex(ValueError, "missing SKILL.md"):
                runner.prepare_workspace(ROOT, PLANNING, case, Path(temporary) / "missing-workspace")

    def test_unmapped_case_skills_keep_production_resolution(self):
        case = eval_case(skills=("specs", "requirements"))

        with tempfile.TemporaryDirectory() as temporary:
            prepared = runner.prepare_workspace(
                ROOT, PLANNING, case, Path(temporary) / "workspace"
            )

            self.assertEqual(
                (prepared.workspace / ".eval/skills/requirements/SKILL.md").read_text(encoding="utf-8"),
                (ROOT / "plugins/planning/skills/requirements/SKILL.md").read_text(encoding="utf-8"),
            )

    def test_prepare_workspace_configures_eval_reviewer_identity(self):
        name, email = "Eval Reviewer", "eval-reviewer@example.invalid"
        case = planning_case("specs", 7)

        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            prepared = runner.prepare_workspace(ROOT, PLANNING, case, temp / "workspace")
            (temp / "state").mkdir()

            for key, value in (("user.name", name), ("user.email", email)):
                self.assertEqual(
                    run_text(["git", "config", key], prepared.workspace).strip(), value
                )

            for revision in ("@-", "@"):
                self.assertEqual(
                    run_text(
                        ["jj", "log", "-r", revision, "--no-graph", "-T",
                         'author.name() ++ " " ++ author.email()'],
                        prepared.workspace,
                    ).strip(),
                    f"{name} {email}",
                )

            argv = runner.container_command(
                ["true"], prepared.workspace, temp / "state", container_name="x"
            )
            self.assertIn(f"--env=JJ_USER={name}", argv)
            self.assertIn(f"--env=JJ_EMAIL={email}", argv)

            # Mirror the container: a HOME with no jj config plus the env flags.
            (temp / "home").mkdir()
            env = {
                "HOME": str(temp / "home"),
                "PATH": os.environ["PATH"],
                **dict(
                    arg[len("--env=") :].split("=", 1)
                    for arg in argv
                    if arg.startswith("--env=JJ_")
                ),
            }
            for key, value in (("user.name", name), ("user.email", email)):
                result = subprocess.run(
                    ["jj", "config", "get", key],
                    cwd=prepared.workspace,
                    env=env,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                self.assertEqual(result.stdout.strip(), value)

    def test_prepare_workspace_commits_baseline_and_leaves_working_fixtures(self):
        case = planning_case("specs", 7)

        with tempfile.TemporaryDirectory() as temporary:
            prepared = runner.prepare_workspace(
                ROOT, PLANNING, case, Path(temporary) / "workspace"
            )

            self.assertTrue(
                (prepared.workspace / ".eval/skills/specs/SKILL.md").is_file()
            )
            self.assertFalse(
                (prepared.workspace / ".eval/skills/requirements/SKILL.md").is_file()
            )
            self.assertFalse(
                (prepared.workspace / ".eval/skills/specs/evals").exists()
            )
            self.assertTrue(
                (prepared.workspace / "docs/specs/approved-spec.md").is_file()
            )
            self.assertTrue((prepared.workspace / "README.md").is_file())
            self.assertTrue(prepared.baseline_commit)

            evidence = runner.collect_evidence(prepared)

            self.assertIn("docs/specs/approved-spec.md", evidence["status"])
            self.assertIn("README.md", evidence["status"])
            self.assertNotIn(".eval/skills", evidence["status"])

    def test_evidence_distinguishes_commits_from_remaining_work(self):
        case = planning_case("specs", 7)

        with tempfile.TemporaryDirectory() as temporary:
            prepared = runner.prepare_workspace(
                ROOT, PLANNING, case, Path(temporary) / "workspace"
            )
            run_text(
                [
                    "jj",
                    "commit",
                    "docs/specs/approved-spec.md",
                    "-m",
                    "preserve approved spec",
                ],
                prepared.workspace,
            )

            evidence = runner.collect_evidence(prepared)

            self.assertIn("preserve approved spec", evidence["committed_after_baseline"])
            self.assertIn("README.md", evidence["status"])
            self.assertNotIn("docs/specs/approved-spec.md", evidence["status"])

    def test_agy_workspace_disables_inherited_customizations(self):
        case = planning_case("requirements", 1)

        with tempfile.TemporaryDirectory() as temporary:
            prepared = runner.prepare_workspace(
                ROOT,
                PLANNING,
                case,
                Path(temporary) / "workspace",
                "agy",
            )
            agent = (
                prepared.workspace
                / ".agents/agents/superstore-eval/agent.md"
            ).read_text(encoding="utf-8")

            self.assertIn("inheritCustomizations: false", agent)
            self.assertNotIn("superstore-eval", runner.collect_evidence(prepared)["status"])

    def test_run_case_redacts_credential_leaks_and_discards_workspace(self):
        case = planning_case("requirements", 1)
        secret = "subscription-token-123456"

        def fake_seed(host, state, home):
            write_test_auth(host, state, secret)
            write_test_auth(host, home, secret)

        def fake_turn(command, workspace, timeout, *, container_name=None):
            (workspace / "leaked.txt").write_text(secret, encoding="utf-8")
            stdout = "\n".join(
                (
                    '{"type":"thread.started","thread_id":"thread-1"}',
                    json.dumps(
                        {
                            "type": "item.completed",
                            "item": {
                                "type": "agent_message",
                                "text": f"token={secret}",
                            },
                        }
                    ),
                )
            )
            return 0, stdout, "", 0.1

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "results"
            home = Path(temporary) / "home"
            with (
                mock.patch.object(runner, "seed_auth", side_effect=fake_seed),
                mock.patch.object(runner, "run_turn", side_effect=fake_turn),
            ):
                result = runner.run_case(
                    ROOT,
                    PLANNING,
                    case,
                    "codex",
                    output,
                    60,
                    home=home,
                )

            result_dir = output / "codex/requirements-1"
            retained = "".join(
                path.read_text(encoding="utf-8", errors="replace")
                for path in result_dir.rglob("*")
                if path.is_file()
            )
            self.assertEqual(result["status"], "error")
            self.assertIn("credential_error", result["turns"][0])
            self.assertNotIn(secret, retained)
            self.assertFalse((result_dir / "workspace").exists())

    def test_run_case_retains_codex_reviewer_provenance(self):
        case = eval_case(
            skill="requirements",
            skills=("requirements",),
            replies=("Approved.",),
        )
        turn_number = 0

        def fake_seed(host, state, home):
            write_test_auth(host, state, "test-token")
            write_test_auth(host, home, "test-token")

        def fake_turn(command, workspace, timeout, *, container_name=None):
            nonlocal turn_number
            turn_number += 1
            mount = next(
                item
                for item in command
                if item.startswith("--mount=type=bind,src=")
                and item.endswith(",dst=/state")
            )
            state = Path(
                mount.removeprefix("--mount=type=bind,src=").removesuffix(
                    ",dst=/state"
                )
            )
            records = REVIEW_ROLLOUT
            if turn_number == 2:
                records = (
                    *records,
                    response_item(
                        "function_call",
                        name="list_agents",
                        call_id="list-1",
                        arguments="{}",
                    ),
                    response_item(
                        "function_call_output",
                        call_id="list-1",
                        output='{"agents":[]}',
                    ),
                )
            write_codex_review_rollout(state, records)
            events = []
            if turn_number == 1:
                events.append(
                    {"type": "thread.started", "thread_id": REVIEW_SESSION_ID}
                )
            events.append(
                {
                    "type": "item.completed",
                    "item": {
                        "type": "agent_message",
                        "text": f"Requirements response {turn_number}",
                    },
                }
            )
            stdout = "\n".join(json.dumps(event) for event in events)
            return 0, stdout, "", 0.1

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "results"
            with (
                mock.patch.object(runner, "seed_auth", side_effect=fake_seed),
                mock.patch.object(runner, "run_turn", side_effect=fake_turn),
            ):
                result = runner.run_case(
                    ROOT,
                    PLANNING,
                    case,
                    "codex",
                    output,
                    60,
                    home=Path(temporary) / "home",
                )

            first_trace = result["turns"][0]["provider_trace"]
            second_trace = result["turns"][1]["provider_trace"]
            self.assertEqual(first_trace[0]["event"], "spawn_agent")
            self.assertIn("No material findings.", first_trace[-1]["text"])
            self.assertEqual(
                second_trace,
                [
                    {"event": "list_agents"},
                    {"event": "list_agents_result", "agents": []},
                ],
            )
            self.assertTrue(
                (output / "codex/requirements-1/turn-01.provider.json").is_file()
            )
            review_context = json.loads(
                (output / "codex/requirements-1/review-context.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(review_context["author_guidance"]["authority"], "advisory")
            self.assertEqual(
                json.loads(
                    (output / "codex/requirements-1/turn-02.provider.json").read_text(
                        encoding="utf-8"
                    )
                ),
                second_trace,
            )


def fake_jwt(exp: datetime) -> str:
    """A syntactically valid JWT carrying only an `exp` claim; not a token."""
    def segment(value: dict) -> str:
        raw = json.dumps(value).encode()
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")

    return f"{segment({'alg': 'none'})}.{segment({'exp': int(exp.timestamp())})}.sig"


def write_expiry(host: str, home: Path, expiry: datetime, last_refresh: datetime | None = None) -> None:
    """Write a fake credential holding only the expiry fields the runner reads."""
    if host == "claude":
        data = {"claudeAiOauth": {"expiresAt": int(expiry.timestamp() * 1000)}}
    elif host == "codex":
        data = {"tokens": {"access_token": fake_jwt(expiry)}}
        if last_refresh:
            data["last_refresh"] = last_refresh.isoformat().replace("+00:00", "Z")
    else:
        data = {"token": {"expiry": expiry.strftime("%Y-%m-%dT%H:%M:%S.%f000Z")}}
    path = home / runner.AUTH_FILES[host]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def scheduling_cases(count: int) -> list[EvalCase]:
    return [
        eval_case(identifier=index, definition_dir=PLANNING / "skills/specs/evals")
        for index in range(1, count + 1)
    ]


class FakeRuns:
    """A `run_case` stand-in that records how cases overlapped."""

    def __init__(self, duration=0.05, refresh=None):
        self.duration = duration
        self.refresh = refresh or (lambda case, host: False)
        self.lock = threading.Lock()
        self.running: Counter = Counter()
        self.peak: Counter = Counter()
        self.others_at_start: dict[tuple[str, int], int] = {}
        self.hosts_overlapped = False
        self.calls: list[tuple[str, str, Path]] = []

    def __call__(self, repo_root, plugin_root, case, host, output, timeout,
                 model=None, effort=None, home=None):
        with self.lock:
            self.running[host] += 1
            self.peak[host] = max(self.peak[host], self.running[host])
            self.others_at_start[(host, case.identifier)] = self.running[host] - 1
            self.hosts_overlapped |= sum(1 for count in self.running.values() if count) > 1
            self.calls.append((host, case.key, plugin_root))
        duration = self.duration(case) if callable(self.duration) else self.duration
        time.sleep(duration)
        with self.lock:
            self.running[host] -= 1
        return {"status": "captured", "refreshed_login": self.refresh(case, host)}


class ParallelRunnerTests(unittest.TestCase):
    FAR = datetime.now(timezone.utc) + timedelta(hours=2)

    def run_all(self, hosts, cases, runs, home, timeout=60, **patches):
        args = runner.parse_args([flag for host in hosts for flag in ("--host", host)] + ["--timeout", str(timeout)])
        stdout, stderr = io.StringIO(), io.StringIO()
        with (
            tempfile.TemporaryDirectory() as temporary,
            mock.patch.object(runner, "run_case", side_effect=runs),
            mock.patch.object(runner, "seed_auth", side_effect=AssertionError("real run_case reached")),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
            contextlib.ExitStack() as stack,
        ):
            for name, value in patches.items():
                stack.enter_context(mock.patch.object(runner, name, value))
            results = runner.run_all(args, cases, Path(temporary), home)
        return results, stdout.getvalue(), stderr.getvalue()

    def test_hosts_overlap_and_no_host_exceeds_the_session_cap(self):
        cases = scheduling_cases(8)
        runs = FakeRuns(duration=0.05)
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            for host in ("codex", "claude"):
                write_expiry(host, home, self.FAR)

            results, stdout, _ = self.run_all(["codex", "claude"], cases, runs, home)

        for host in ("codex", "claude"):
            self.assertLessEqual(runs.peak[host], runner.MAX_SESSIONS_PER_HOST)
            self.assertGreaterEqual(runs.peak[host], 2, host)
            self.assertEqual(runs.others_at_start[(host, 1)], 0, "first case runs alone")
        self.assertTrue(runs.hosts_overlapped)
        self.assertEqual(
            sorted(Counter((host, key) for host, key, _ in runs.calls).values()),
            [1] * 16,
        )
        self.assertTrue(all(plugin_root == PLANNING for _, _, plugin_root in runs.calls))
        self.assertEqual(
            [(result["host"], result["case"]) for result in results],
            [(host, case.key) for host in ("codex", "claude") for case in cases],
        )
        self.assertEqual(stdout.count("Running specs/"), 16)

    def test_load_plugin_cases_refuses_a_skill_two_plugins_share(self):
        with tempfile.TemporaryDirectory() as temporary:
            roots = []
            for name in ("first", "second"):
                evals = Path(temporary) / name / "skills/specs/evals"
                evals.mkdir(parents=True)
                (evals / "evals.json").write_text(
                    json.dumps({"skill_name": "specs", "evals": [EvalCaseTests.case(1)]}),
                    encoding="utf-8",
                )
                roots.append(Path(temporary) / name)

            with self.assertRaisesRegex(SystemExit, "skill specs is in both"):
                runner.load_plugin_cases(roots)
            self.assertEqual(len(runner.load_plugin_cases([roots[0], roots[0]])), 1)

    def test_short_lived_login_runs_its_cases_alone(self):
        runs = FakeRuns(duration=0.03)
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            write_expiry("claude", home, datetime.now(timezone.utc) + timedelta(minutes=5))

            results, stdout, _ = self.run_all(["claude"], scheduling_cases(4), runs, home)

        self.assertEqual(runs.peak["claude"], 1)
        self.assertEqual(len(results), 4)
        self.assertNotIn("one case at a time", stdout)

    def test_unreadable_login_expiry_runs_one_case_at_a_time(self):
        runs = FakeRuns(duration=0.03)
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            path = home / runner.AUTH_FILES["codex"]
            path.parent.mkdir(parents=True)
            path.write_text('{"tokens": {}}', encoding="utf-8")

            _, stdout, _ = self.run_all(["codex"], scheduling_cases(4), runs, home)

        self.assertEqual(runs.peak["codex"], 1)
        self.assertIn("codex runs one case at a time: its login expiry cannot be read", stdout)

    def test_unconfirmed_refresh_rule_runs_one_case_at_a_time(self):
        runs = FakeRuns(duration=0.03)
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            write_expiry("agy", home, self.FAR)

            _, stdout, _ = self.run_all(
                ["agy"], scheduling_cases(4), runs, home,
                REFRESH_RULE_CONFIRMED=frozenset({"claude", "codex"}),
            )

        self.assertEqual(runs.peak["agy"], 1)
        self.assertIn("agy runs one case at a time: its login refresh rule is not confirmed", stdout)

    def test_refresh_during_a_parallel_case_drops_the_host_to_one_at_a_time(self):
        runs = FakeRuns(
            duration=lambda case: 0.01 if case.identifier == 2 else 0.1,
            refresh=lambda case, host: case.identifier == 2,
        )
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            write_expiry("claude", home, self.FAR)

            results, _, stderr = self.run_all(["claude"], scheduling_cases(7), runs, home)

        self.assertGreater(runs.peak["claude"], 1)
        self.assertGreaterEqual(runs.others_at_start[("claude", 2)], 0)
        for identifier in (6, 7):
            self.assertEqual(runs.others_at_start[("claude", identifier)], 0, identifier)
        self.assertIn("WARNING claude refreshed its login during a parallel case", stderr)
        self.assertEqual([result["refreshed_login"] for result in results][1], True)

    @unittest.skipUnless(shutil.which("jj"), "Jujutsu is required")
    def test_run_case_records_whether_the_login_was_refreshed(self):
        case = eval_case(skill="requirements", skills=("requirements",))

        def fake_seed(host, state, home):
            write_test_auth(host, state, "test-token")
            os.utime(state / runner.AUTH_FILES[host], ns=(1_000_000_000, 1_000_000_000))
            write_test_auth(host, home, "test-token")

        def fake_turn(bump):
            def turn(command, workspace, timeout, *, container_name=None):
                if bump:
                    mount = next(item for item in command if item.endswith(",dst=/state"))
                    state = Path(mount.removeprefix("--mount=type=bind,src=").removesuffix(",dst=/state"))
                    os.utime(state / runner.AUTH_FILES["codex"], ns=(2_000_000_000, 2_000_000_000))
                stdout = "\n".join((
                    '{"type":"thread.started","thread_id":"thread-1"}',
                    '{"type":"item.completed","item":{"type":"agent_message","text":"Done"}}',
                ))
                return 0, stdout, "", 0.1
            return turn

        for bump in (True, False):
            with tempfile.TemporaryDirectory() as temporary, self.subTest(bump=bump):
                with (
                    mock.patch.object(runner, "seed_auth", side_effect=fake_seed),
                    mock.patch.object(runner, "run_turn", side_effect=fake_turn(bump)),
                    mock.patch.object(runner, "persist_auth"),
                ):
                    result = runner.run_case(
                        ROOT, PLANNING, case, "codex", Path(temporary) / "results", 60,
                        home=Path(temporary) / "home",
                    )
                self.assertEqual(result["refreshed_login"], bump)

    def test_write_backs_wait_for_the_host_lock_and_keep_the_newest_login(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / "home"
            existing = home / ".codex/auth.json"
            existing.parent.mkdir(parents=True)
            existing.write_text('{"token":"before"}', encoding="utf-8")
            os.utime(existing, ns=(1_000_000_000, 1_000_000_000))
            states = []
            for index in range(1, 4):
                state = root / f"state-{index}"
                runner.seed_auth("codex", state, home)
                refreshed = state / ".codex/auth.json"
                refreshed.write_text(json.dumps({"token": f"eval-{index}"}), encoding="utf-8")
                os.utime(refreshed, ns=(index * 1_000_000_000 + 1, index * 1_000_000_000 + 1))
                states.append(state)
            threads = [
                threading.Thread(target=runner.persist_auth, args=("codex", state, home))
                for state in reversed(states)
            ]

            with runner.WRITE_LOCKS["codex"]:
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join(0.2)
                self.assertTrue(all(thread.is_alive() for thread in threads), "write-backs wait for the lock")
                self.assertEqual(existing.read_text(encoding="utf-8"), '{"token":"before"}')
            for thread in threads:
                thread.join(5)
            self.assertFalse(any(thread.is_alive() for thread in threads))

            self.assertEqual(json.loads(existing.read_text(encoding="utf-8")), {"token": "eval-3"})
            self.assertEqual(sorted(home.joinpath(".codex").iterdir()), [existing])

    @unittest.skipUnless(shutil.which("jj"), "Jujutsu is required")
    def test_run_case_starts_no_turn_after_an_interrupt(self):
        case = eval_case(skill="requirements", skills=("requirements",), replies=("Approved.",))
        self.addCleanup(runner.STOP.clear)

        def fake_seed(host, state, home):
            write_test_auth(host, state, "test-token")
            write_test_auth(host, home, "test-token")

        def fake_turn(command, workspace, timeout, *, container_name=None):
            runner.STOP.set()  # the interrupt lands while turn 1 runs
            stdout = "\n".join((
                '{"type":"thread.started","thread_id":"thread-1"}',
                '{"type":"item.completed","item":{"type":"agent_message","text":"Done"}}',
            ))
            return 0, stdout, "", 0.1

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "results"
            with (
                mock.patch.object(runner, "seed_auth", side_effect=fake_seed),
                mock.patch.object(runner, "run_turn", side_effect=fake_turn) as turns,
                mock.patch.object(runner, "persist_auth") as persisted,
            ):
                result = runner.run_case(
                    ROOT, PLANNING, case, "codex", output, 60, home=Path(temporary) / "home"
                )
            self.assertTrue((output / "codex/requirements-1/result.json").is_file())

        self.assertEqual(turns.call_count, 1)
        self.assertEqual((result["status"], len(result["turns"])), ("error", 1))
        self.assertTrue(persisted.called, "the login write-back still runs")
        self.assertEqual(runner.TRACKED_CONTAINERS, set())

    def test_login_expiry_reads_only_the_expiry_fields(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            write_expiry("claude", home, now + timedelta(hours=1))
            write_expiry("agy", home, now + timedelta(hours=2))
            write_expiry("codex", home, now + timedelta(hours=3), last_refresh=now - timedelta(days=8, hours=1))

            self.assertEqual(runner.login_expiry("claude", home), now + timedelta(hours=1))
            self.assertEqual(runner.login_expiry("agy", home), now + timedelta(hours=2))
            self.assertEqual(runner.login_expiry("codex", home), now - timedelta(hours=1))

            write_expiry("codex", home, now + timedelta(hours=3), last_refresh=now)
            self.assertEqual(runner.login_expiry("codex", home), now + timedelta(hours=3))
            (home / runner.AUTH_FILES["agy"]).write_text('{"token": {"expiry": "soon"}}', encoding="utf-8")
            self.assertIsNone(runner.login_expiry("agy", home))
            self.assertIsNone(runner.login_expiry("claude", home / "missing"))

    def main_with_fakes(self, arguments, runs, output):
        stdout, stderr = io.StringIO(), io.StringIO()
        handlers = {sig: signal.getsignal(sig) for sig in (signal.SIGTERM, signal.SIGINT)}
        try:
            with (
                mock.patch.object(runner, "run_case", side_effect=runs),
                mock.patch.object(runner, "seed_auth", side_effect=AssertionError("real run_case reached")),
                mock.patch.object(runner, "build_image"),
                mock.patch.object(runner.shutil, "which", return_value="/usr/bin/true"),
                mock.patch.object(runner, "login_expiry", return_value=self.FAR),
                contextlib.redirect_stdout(stdout),
                contextlib.redirect_stderr(stderr),
            ):
                code = runner.main([*arguments, "--output", str(output)])
        finally:
            for sig, handler in handlers.items():
                signal.signal(sig, handler)
        return code, stdout.getvalue()

    def test_summary_has_the_new_fields_in_host_then_case_order(self):
        runs = FakeRuns(duration=lambda case: 0.01 * (4 - case.identifier))
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "results"
            code, stdout = self.main_with_fakes(
                ["--skill", "specs", "--case", "1", "--case", "2", "--case", "3",
                 "--host", "claude", "--host", "codex"],
                runs, output,
            )
            summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))

        self.assertEqual(code, 0)
        self.assertEqual(
            [(result["host"], result["case"]) for result in summary["results"]],
            [(host, f"specs/{index}") for host in ("claude", "codex") for index in (1, 2, 3)],
        )
        for key in ("started_at", "completed_at", "wall_seconds", "errors"):
            self.assertIn(key, summary)
        for result in summary["results"]:
            for key in ("status", "started_at", "wall_seconds", "refreshed_login"):
                self.assertIn(key, result)
        self.assertEqual(summary["errors"], 0)
        self.assertRegex(stdout, r"Captured 6, errors 0, wall \d+s")

    def interrupted_run_all(self, hosts, cases, runs, remove, expect=SystemExit,
                            login_expiry=None, **patches):
        """Run `run_all` with an injected failure; return (exception, seconds)."""
        self.addCleanup(runner.STOP.clear)
        args = runner.parse_args([flag for host in hosts for flag in ("--host", host)])
        handlers = {sig: signal.getsignal(sig) for sig in (signal.SIGTERM, signal.SIGINT)}
        started = time.monotonic()
        with (
            tempfile.TemporaryDirectory() as temporary,
            mock.patch.object(runner, "run_case", side_effect=runs),
            mock.patch.object(runner, "seed_auth", side_effect=AssertionError("real run_case reached")),
            mock.patch.object(runner, "remove_container", side_effect=remove),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.ExitStack() as stack,
        ):
            stack.enter_context(mock.patch.object(
                runner, "login_expiry", login_expiry or (lambda host, home=None: None)
            ))
            for target, name, value in patches.values():
                stack.enter_context(mock.patch.object(target, name, value))
            try:
                with self.assertRaises(expect) as raised:
                    runner.run_all(args, cases, Path(temporary))
            finally:
                for sig, handler in handlers.items():
                    signal.signal(sig, handler)
        seconds = time.monotonic() - started
        # `done.set()` runs in the thread's finally, just before it leaves the
        # active list, so give a slow thread a moment to disappear.
        for thread in threading.enumerate():
            if thread.name in hosts:
                thread.join(1)
        self.assertEqual([t.name for t in threading.enumerate() if t.name in hosts], [],
                         "every host thread ended before run_all re-raised")
        return raised.exception, seconds

    def test_interrupt_right_after_a_host_finished_still_ends_cleanup(self):
        # The signal handler runs after run_all's completion wait (the only
        # Event.wait with timeout 0.2) returned True, before the main thread
        # acted on it; the host's completion must not be lost.
        sites = []

        class LeakyEvent(threading.Event):
            def wait(self, timeout=None):
                flag = super().wait(timeout)
                if flag and timeout == 0.2 and not sites:
                    sites.append("completion wait")
                    raise SystemExit(143)
                return flag

        removed = []

        def tracked_run(*arguments, **keywords):
            runner.TRACKED_CONTAINERS.add("superstore-eval-finished")
            try:
                time.sleep(0.1)
            finally:
                runner.TRACKED_CONTAINERS.discard("superstore-eval-finished")
            return {"status": "captured", "refreshed_login": False}

        error, seconds = self.interrupted_run_all(
            ["claude"], scheduling_cases(1), tracked_run, removed.append,
            event=(threading, "Event", LeakyEvent),
        )

        self.assertEqual(sites, ["completion wait"])
        self.assertEqual(error.code, 143)
        self.assertLess(seconds, 3, "cleanup ended promptly instead of waiting forever")
        self.assertEqual(runner.TRACKED_CONTAINERS, set())

    def test_failure_while_starting_a_host_still_sweeps_the_others(self):
        # Not a signal: the second host's login read raises once the first
        # host's case is provably running with a container tracked.
        removed, released, tracked = [], threading.Event(), threading.Event()

        def tracked_run(*arguments, **keywords):
            runner.TRACKED_CONTAINERS.add("superstore-eval-started")
            tracked.set()
            try:
                released.wait(5)  # like a container, ends when the run removes it
            finally:
                runner.TRACKED_CONTAINERS.discard("superstore-eval-started")
            return {"status": "captured", "refreshed_login": False}

        def remove(name):
            removed.append(name)
            released.set()

        def login_expiry(host, home=None):
            if host == "codex":
                self.assertTrue(tracked.wait(5), "claude's case is running before the failure")
                raise RuntimeError("credential store unavailable")
            return None

        error, seconds = self.interrupted_run_all(
            ["claude", "codex"], scheduling_cases(2), tracked_run, remove,
            expect=RuntimeError, login_expiry=login_expiry,
        )

        self.assertEqual(str(error), "credential store unavailable")
        self.assertTrue(runner.STOP.is_set())
        self.assertEqual(removed, ["superstore-eval-started"])
        self.assertLess(seconds, 3)
        self.assertEqual(runner.TRACKED_CONTAINERS, set())

    def test_interrupt_right_after_a_host_thread_started_still_sweeps_it(self):
        # The signal handler runs after Thread.start() returned but before the
        # main thread recorded the host; its containers must still be swept.
        class StartThenInterrupt(threading.Thread):
            fired = False

            def start(self):
                super().start()
                if not StartThenInterrupt.fired:
                    StartThenInterrupt.fired = True
                    raise SystemExit(143)

        removed, released = [], threading.Event()

        def tracked_run(*arguments, **keywords):
            runner.TRACKED_CONTAINERS.add("superstore-eval-unrecorded")
            try:
                released.wait(5)  # like a container, ends when the run removes it
            finally:
                runner.TRACKED_CONTAINERS.discard("superstore-eval-unrecorded")
            return {"status": "captured", "refreshed_login": False}

        def remove(name):
            removed.append(name)
            released.set()

        error, seconds = self.interrupted_run_all(
            ["claude"], scheduling_cases(2), tracked_run, remove,
            thread=(threading, "Thread", StartThenInterrupt),
        )

        self.assertEqual(error.code, 143)
        self.assertEqual(removed, ["superstore-eval-unrecorded"])
        self.assertLess(seconds, 3)
        self.assertEqual(runner.TRACKED_CONTAINERS, set())

    def test_sigterm_removes_tracked_containers_and_writes_no_summary(self):
        released = {name: threading.Event() for name in ("superstore-eval-turn-1", "superstore-eval-turn-2")}
        signalled = threading.Event()
        removed = []
        self.addCleanup(runner.STOP.clear)

        def interrupted_run(repo_root, plugin_root, case, host, output, timeout,
                            model=None, effort=None, home=None):
            # Two turns: each container ends when the run removes it, and the
            # second is tracked only after the first is gone.
            for name, event in released.items():
                runner.TRACKED_CONTAINERS.add(name)
                try:
                    if not signalled.is_set():
                        signalled.set()
                        time.sleep(0.05)  # let the main thread reach its join loop
                        os.kill(os.getpid(), signal.SIGTERM)
                    event.wait(5)
                finally:
                    runner.TRACKED_CONTAINERS.discard(name)
            return {"status": "captured", "refreshed_login": False}

        def fake_remove(container_name):
            removed.append(container_name)
            released[container_name].set()

        runs = mock.Mock(side_effect=interrupted_run)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "results"
            with (
                mock.patch.object(runner, "remove_container", side_effect=fake_remove),
                self.assertRaises(SystemExit) as raised,
            ):
                self.main_with_fakes(["--skill", "specs", "--host", "claude"], runs, output)
            self.assertFalse((output / "summary.json").exists())

        self.assertEqual(raised.exception.code, 128 + signal.SIGTERM)
        self.assertEqual(set(removed), set(released), "every tracked container is removed")
        self.assertTrue(all(event.is_set() for event in released.values()))
        self.assertEqual(runs.call_count, 1, "no new case starts after the signal")
        self.assertTrue(runner.STOP.is_set())


class HostCommandTests(unittest.TestCase):
    def test_sigterm_uses_normal_cleanup_path(self):
        with self.assertRaisesRegex(SystemExit, "143"):
            runner.terminate_on_signal(signal.SIGTERM, None)

    def test_container_command_exposes_only_workspace_and_disposable_state(self):
        workspace = Path("/tmp/eval-workspace")
        state = Path("/tmp/eval-state")

        command = runner.container_command(
            ["codex", "exec", "prompt"],
            workspace,
            state,
            container_name="superstore-eval-test",
        )

        self.assertEqual(command[:3], ["docker", "run", "--rm"])
        self.assertIn("--read-only", command)
        self.assertIn("--cap-drop=ALL", command)
        self.assertIn("--security-opt=no-new-privileges", command)
        self.assertIn("--name=superstore-eval-test", command)
        self.assertIn(f"--user={os.getuid()}:{os.getgid()}", command)
        self.assertIn(f"--mount=type=bind,src={workspace},dst=/workspace", command)
        self.assertIn(f"--mount=type=bind,src={state},dst=/state", command)
        self.assertEqual(
            command[-8:],
            [
                runner.IMAGE,
                "timeout",
                "--signal=TERM",
                "--kill-after=15s",
                "600s",
                "codex",
                "exec",
                "prompt",
            ],
        )

    def test_seed_auth_copies_only_the_selected_existing_credential(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / "home"
            state = root / "state"
            source = home / ".codex/auth.json"
            source.parent.mkdir(parents=True)
            source.write_text('{"token":"secret"}', encoding="utf-8")

            runner.seed_auth("codex", state, home)

            copied = state / ".codex/auth.json"
            self.assertEqual(copied.read_text(encoding="utf-8"), source.read_text())
            self.assertEqual(copied.stat().st_mode & 0o777, 0o600)
            self.assertIn("secret", runner.credential_values(copied))
            self.assertEqual(
                [path.relative_to(state) for path in state.rglob("*") if path.is_file()],
                [Path(".codex/auth.json")],
            )

    def test_newer_refreshed_credential_replaces_the_existing_login(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / "home"
            state = root / "state"
            source = home / ".codex/auth.json"
            source.parent.mkdir(parents=True)
            source.write_text('{"token":"before"}', encoding="utf-8")
            os.utime(source, ns=(1_000_000_000, 1_000_000_000))
            runner.seed_auth("codex", state, home)
            refreshed = state / ".codex/auth.json"
            refreshed.write_text(
                '{"token":"after"}', encoding="utf-8"
            )
            os.utime(refreshed, ns=(2_000_000_000, 2_000_000_000))

            runner.persist_auth("codex", state, home)

            self.assertEqual(source.read_text(encoding="utf-8"), '{"token":"after"}')

    def test_older_eval_credential_does_not_replace_a_newer_existing_login(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / "home"
            state = root / "state"
            existing = home / ".codex/auth.json"
            existing.parent.mkdir(parents=True)
            existing.write_text('{"token":"before"}', encoding="utf-8")
            os.utime(existing, ns=(1_000_000_000, 1_000_000_000))
            runner.seed_auth("codex", state, home)
            refreshed = state / ".codex/auth.json"
            refreshed.write_text('{"token":"eval"}', encoding="utf-8")
            os.utime(refreshed, ns=(2_000_000_000, 2_000_000_000))
            existing.write_text('{"token":"host"}', encoding="utf-8")
            os.utime(existing, ns=(3_000_000_000, 3_000_000_000))

            runner.persist_auth("codex", state, home)

            self.assertEqual(existing.read_text(encoding="utf-8"), '{"token":"host"}')

    def test_credential_values_are_redacted_and_detected_in_workspace(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            secret = "subscription-token-123456"
            (workspace / "leaked.txt").write_text(secret, encoding="utf-8")

            sanitized = runner.redact_credentials(
                {"stdout": f"token={secret}", "items": [secret]}, {secret}
            )

            self.assertNotIn(secret, json.dumps(sanitized))
            self.assertEqual(
                runner.find_credential_files(workspace, {secret}), ["leaked.txt"]
            )

    def test_credential_paths_are_redacted_and_detected_in_workspace(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            secret = "subscription-token-123456"
            (workspace / f"directory-{secret}").mkdir()
            (workspace / f"file-{secret}.txt").write_text("benign", encoding="utf-8")

            self.assertEqual(
                runner.find_credential_files(workspace, {secret}),
                ["directory-[REDACTED]", "file-[REDACTED].txt"],
            )

    def test_codex_rollout_trace_preserves_reviewer_provenance(self):
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary)
            write_codex_review_rollout(state)

            trace = runner.codex_rollout_trace(state, REVIEW_SESSION_ID)

            self.assertEqual(
                trace,
                [
                    {
                        "event": "spawn_agent",
                        "task_name": "spec_review",
                        "fork_turns": "all",
                    },
                    {
                        "event": "spawn_agent_result",
                        "task_name": "/root/spec_review",
                    },
                    {"event": "wait_agent", "timeout_ms": 120000},
                    {
                        "event": "wait_agent_result",
                        "message": "Wait completed.",
                        "timed_out": False,
                    },
                    {
                        "event": "reviewer_message",
                        "text": (
                            "Message Type: FINAL_ANSWER\n"
                            "Sender: /root/spec_review\n"
                            "Payload:\nNo material findings."
                        ),
                    },
                ],
            )
            self.assertNotIn("encrypted-review-prompt", json.dumps(trace))

    def test_agy_brain_trace_returns_subagent_transcript_and_messages_once(self):
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary)
            brain = state / ".gemini/antigravity-cli/brain"
            reviewer = brain / "sub-1/.system_generated"
            (reviewer / "logs").mkdir(parents=True)
            (reviewer / "logs/transcript_full.jsonl").write_text(
                json.dumps({"step_index": 0, "type": "USER_INPUT", "content": "review this"})
                + "\n"
                + json.dumps({"step_index": 1, "type": "PLANNER_RESPONSE", "content": "done"})
                + "\n",
                encoding="utf-8",
            )
            primary = brain / "main-1/.system_generated/messages"
            primary.mkdir(parents=True)
            (primary / "m1.json").write_text(
                json.dumps(
                    {
                        "sender": "sub-1",
                        "recipient": "main-1",
                        "renderDetails": {"messageTitle": "Message from reviewer"},
                        "content": "No material findings",
                    }
                ),
                encoding="utf-8",
            )
            (primary / "read.json").write_text("[]", encoding="utf-8")

            seen: set[str] = set()
            trace = runner.agy_brain_trace(state, seen)

            self.assertEqual(
                trace,
                [
                    {
                        "event": "message",
                        "sender": "sub-1",
                        "recipient": "main-1",
                        "title": "Message from reviewer",
                        "content": "No material findings",
                    },
                    {"event": "transcript_step", "conversation": "sub-1", "step_index": 0, "type": "USER_INPUT", "content": "review this"},
                    {"event": "transcript_step", "conversation": "sub-1", "step_index": 1, "type": "PLANNER_RESPONSE", "content": "done"},
                ],
            )
            self.assertEqual(runner.agy_brain_trace(state, seen), [])
            self.assertEqual(runner.agy_brain_trace(state / "missing", set()), [])

    def test_codex_rollout_trace_requires_session_id(self):
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary)
            write_codex_review_rollout(state)

            self.assertEqual(runner.codex_rollout_trace(state, ""), [])

    def test_run_turn_removes_its_container_after_timeout(self):
        timeout = subprocess.TimeoutExpired(
            ["docker", "run"], 1, output="partial", stderr="late"
        )
        removed = mock.Mock(returncode=0, stdout="", stderr="")
        with mock.patch.object(
            runner.subprocess, "run", side_effect=[timeout, removed]
        ) as run:
            code, stdout, stderr, _ = runner.run_turn(
                ["docker", "run"],
                Path("/tmp"),
                1,
                container_name="superstore-eval-timeout",
            )

        self.assertEqual((code, stdout, stderr), (124, "partial", "late"))
        self.assertEqual(
            run.call_args_list[1].args[0],
            ["docker", "rm", "--force", "superstore-eval-timeout"],
        )

    def test_commands_pin_the_approved_models_and_effort(self):
        workspace = Path("/tmp/eval-workspace")

        codex = runner.build_command("codex", workspace, "prompt", 300)
        claude = runner.build_command("claude", workspace, "prompt", 300)
        agy = runner.build_command("agy", workspace, "prompt", 300)

        self.assertIn("gpt-5.6-terra", codex)
        self.assertIn('model_reasoning_effort="high"', codex)
        self.assertNotIn("--ephemeral", codex)
        self.assertIn("--enable", codex)
        self.assertEqual(codex[codex.index("--enable") + 1], "multi_agent_v2")
        self.assertFalse(any("wait_timeout_ms" in argument for argument in codex))
        self.assertNotIn("--sandbox", codex)
        self.assertIn("--dangerously-bypass-approvals-and-sandbox", codex)
        self.assertNotIn("--approve-for-me", codex)
        self.assertNotIn("--add-dir", codex)
        self.assertEqual(codex[-1], "prompt")
        self.assertIn("claude-sonnet-5", claude)
        self.assertIn("--safe-mode", claude)
        self.assertNotIn("--setting-sources", claude)
        self.assertNotIn("--mcp-config", claude)
        self.assertIn("--no-session-persistence", claude)
        self.assertIn("gemini-3.8-flash-high", agy)
        self.assertNotIn("--effort", agy)
        self.assertIn("--new-project", agy)
        self.assertIn("superstore-eval", agy)
        self.assertEqual(agy[-2:], ["--print", "prompt"])

    def test_resume_commands_keep_session_model_and_effort(self):
        for host, session_flag in (
            ("codex", None),
            ("claude", "--resume"),
            ("agy", "--conversation"),
        ):
            command = runner.build_resume_command(
                host,
                "session-1",
                "Approved.",
                300,
            )
            self.assertIn("session-1", command)
            self.assertIn(runner.HOSTS[host].model, command)
            self.assertIn(runner.HOSTS[host].effort, " ".join(command))
            if session_flag:
                self.assertIn(session_flag, command)

        codex = runner.build_resume_command(
            "codex", "session-1", "Approved.", 300
        )
        self.assertEqual(codex[:3], ["codex", "exec", "resume"])
        self.assertIn("--dangerously-bypass-approvals-and-sandbox", codex)
        self.assertIn("--enable", codex)
        self.assertEqual(codex[codex.index("--enable") + 1], "multi_agent_v2")
        self.assertFalse(any("wait_timeout_ms" in argument for argument in codex))
        self.assertNotIn("--approve-for-me", codex)
        self.assertNotIn("--add-dir", codex)
        self.assertEqual(codex[-1], "Approved.")
        claude = runner.build_resume_command(
            "claude", "session-1", "Approved.", 300
        )
        agy = runner.build_resume_command(
            "agy", "session-1", "Approved.", 300
        )
        self.assertEqual(claude[-1], "Approved.")
        self.assertIn("--safe-mode", claude)
        self.assertNotIn("--setting-sources", claude)
        self.assertNotIn("--mcp-config", claude)
        self.assertEqual(agy[-2:], ["--print", "Approved."])

    def test_extract_result_normalizes_each_event_stream(self):
        codex = "\n".join(
            (
                '{"type":"thread.started","thread_id":"thread-1"}',
                '{"type":"item.completed","item":{"type":"agent_message","text":"Codex answer"}}',
            )
        )
        claude = "\n".join(
            (
                '{"type":"system","subtype":"init","session_id":"session-1"}',
                '{"type":"result","result":"Claude answer","session_id":"session-1"}',
            )
        )
        agy = "\n".join(
            (
                '{"event":"init","conversation_id":"conversation-1"}',
                '{"event":"result","result":{"conversation_id":"conversation-1","response":"Agy answer"}}',
            )
        )

        self.assertEqual(
            runner.extract_result("codex", codex),
            TurnResult("Codex answer", "thread-1"),
        )
        self.assertEqual(
            runner.extract_result("claude", claude),
            TurnResult("Claude answer", "session-1"),
        )
        self.assertEqual(
            runner.extract_result("agy", agy),
            TurnResult("Agy answer", "conversation-1"),
        )

if __name__ == "__main__":
    unittest.main()
