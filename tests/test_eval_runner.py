import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tempfile
import unittest
from unittest import mock

from scripts import run_skill_evals as runner
from scripts.skill_eval_core import EvalCase, Fixture, run_text
from scripts.skill_eval_hosts import TurnResult


ROOT = Path(__file__).resolve().parents[1]
PLANNING = ROOT / "plugins/planning"
IMPLEMENTATION = ROOT / "plugins/implementation"
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
            skills=("requirements", "read-archive"),
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
        self.assertIn(".eval/skills/read-archive/SKILL.md", prompt)
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
        self.assertIn("gemini-3.7-flash-high", agy)
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
