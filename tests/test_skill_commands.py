import functools
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = "plugins/library/skills/library/SKILL.md"
PIN = "plugins/library/skills/library/references/pin-and-compare.md"
REQUIREMENTS = "plugins/planning/skills/requirements/SKILL.md"
BLOCK_COUNT = 10

OPEN_FENCE = re.compile(r"^(?P<indent>[ \t]*)```(?:sh|bash|shell)[ \t]*$")
CLOSE_FENCE = re.compile(r"^[ \t]*```[ \t]*$")

FIND_STABLE = (
    "find -H docs/specs -maxdepth 1 -name '*.md' ! -name index.md "
    "! -name log.md \\"
)
FIND_UNMIGRATED = (
    "find -H docs/specs docs/plans docs/handoffs docs/notes -maxdepth 1 "
    "-name '*.md' ! -name index.md ! -name log.md \\"
)
FIND_REVIEWS = (
    "find -H docs/reviews -maxdepth 1 -name '*.md' ! -name index.md "
    "! -name log.md \\"
)
FIND_REQUIREMENTS = (
    "find -H docs/specs docs/plans -maxdepth 1 -name '*.md' "
    "! -name index.md ! -name log.md \\"
)
STABLE_TAIL = "| grep ': status: stable$'"
REQUIREMENTS_TAIL = "| grep -E ': (status|tags): '"
# Inline patterns that the skills give in prose; each must appear verbatim.
TAGS_PATTERN = "grep ': tags: .*[[, ]auth[],]'"
TITLE_PATTERN = "grep ': title: '"
SUPERSEDES_PATTERN = "grep ': supersedes: docs/specs/auth-sessions.md'"
SLUG_PATTERN = "': tags: .*[[, ]<slug>[],]'"

PIN_RESOLVE = (
    "jj log -r 'description(substring:\"auth sessions\")' --no-graph "
    "-T 'change_id.short() ++ \" \" ++ commit_id.short() ++ \"\\n\"'"
)
PIN_READ = "jj file show -r <rev> docs/specs/auth-sessions.md"
PIN_COMPARE = "jj diff --from <old> --to <new> docs/specs/auth-sessions.md"
PIN_HISTORY = "jj log docs/specs/auth-sessions.md"
PIN_MOVED = "jj log <old path>"


def shell_blocks():
    """Return {(file, first line): text} for every fenced shell block."""
    paths = sorted(ROOT.glob("plugins/*/skills/*/SKILL.md")) + sorted(
        ROOT.glob("plugins/*/skills/*/references/*.md")
    )
    blocks = {}
    for path in paths:
        name = path.relative_to(ROOT).as_posix()
        lines = path.read_text(encoding="utf-8").split("\n")
        i = 0
        while i < len(lines):
            opening = OPEN_FENCE.match(lines[i])
            i += 1
            if not opening:
                continue
            indent = opening["indent"]
            body = []
            while i < len(lines) and not CLOSE_FENCE.match(lines[i]):
                line = lines[i]
                body.append(
                    line[len(indent):] if line.startswith(indent) else line.lstrip()
                )
                i += 1
            i += 1
            key = (name, body[0])
            if key in blocks:
                raise AssertionError(f"two shell blocks share the key {key!r}")
            blocks[key] = "\n".join(body) + "\n"
    return blocks


def block(name, first_line):
    try:
        return shell_blocks()[(name, first_line)]
    except KeyError:
        raise AssertionError(
            f"{name} has no shell block that starts with {first_line!r}"
        ) from None


COVERED = []


def covers(name, first_line):
    """Register a test for one block and hand it the block's current text."""

    def decorate(test):
        COVERED.append((name, first_line))

        @functools.wraps(test)
        def run(self):
            return test(self, block(name, first_line))

        return run

    return decorate


def discover_awks():
    """Return [(label, executable or None)] for each distinct awk."""
    busybox = shutil.which("busybox")
    if busybox:
        applets = subprocess.run(
            [busybox, "--list"], capture_output=True, text=True
        ).stdout.split()
        busybox = busybox if "awk" in applets else None
    system = "/usr/bin/awk" if os.access("/usr/bin/awk", os.X_OK) else None
    awks, seen = [], set()
    for label, exe in (
        ("mawk", shutil.which("mawk")),
        ("gawk", shutil.which("gawk")),
        ("busybox", busybox),
        ("system", system),
    ):
        if exe is None:
            awks.append((label, None))
        elif os.path.realpath(exe) not in seen:
            seen.add(os.path.realpath(exe))
            awks.append((label, exe))
    return awks


def scratch_env(home, path):
    return {
        "PATH": path,
        "HOME": str(home),
        "LC_ALL": "C",
        "TZ": "UTC",
        "JJ_CONFIG": "/dev/null",
        "JJ_EDITOR": "false",
        "GIT_EDITOR": "false",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_NOSYSTEM": "1",
    }


def sh(command, cwd, env):
    done = subprocess.run(
        ["sh", "-c", command],
        cwd=cwd,
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        timeout=30,
    )
    return done.returncode, done.stdout.decode(), done.stderr.decode()


def exact_lines(output):
    """Split on newlines only, so a stray carriage return stays visible."""
    if output == "":
        return []
    assert output.endswith("\n"), f"output does not end in a newline: {output!r}"
    return output[:-1].split("\n")


def by_file(output):
    """Group lines by file, keeping each file's line order."""
    return sorted(exact_lines(output), key=lambda line: line.split(": ", 1)[0])


def doc(*front, body="# Body\n"):
    return ("---\n" + "\n".join(front) + "\n---\n" + body).encode()


SPECS = {
    "stable.md": doc(
        "type: spec", "status: stable", "title: Billing", "tags: [billing]"
    ),
    "draft.md": doc(
        "type: spec", "status: draft", "title: Draft", "tags: [billing]"
    ),
    "deprecated.md": doc("type: spec", "status: deprecated", "title: Old"),
    "nostatus.md": doc("type: spec"),
    "body-example.md": doc(
        "type: spec",
        "status: draft",
        "title: Example doc",
        body=(
            "Example:\n\n```yaml\n---\ntype: spec\nstatus: stable\n"
            "title: Example\ntags: [auth]\n---\n```\n"
        ),
    ),
    "empty.md": b"",
    "nofm.md": b"# No frontmatter\n\ntype: spec\nstatus: stable\n",
    "crlf.md": doc(
        "type: spec", "status: stable", "title: Windows"
    ).replace(b"\n", b"\r\n"),
    "index.md": doc("type: index", "status: stable", "title: Index"),
    "log.md": doc("type: log", "status: stable", "title: Log"),
    "auth.md": doc(
        "type: spec", "status: stable", "title: Auth", "tags: [auth, login]"
    ),
    "auth-sessions.md": doc(
        "type: spec",
        "status: stable",
        "title: Auth sessions",
        "tags: [auth-sessions, pre-auth]",
    ),
    "approved.md": doc("type: spec", "status: approved", "title: Approved"),
    "bodytype.md": doc("title: Body type", body="type: spec\n"),
    "legacy.md": doc("title: Legacy", "status: wip"),
    "notes.txt": doc("type: spec", "status: stable"),
}
PLANS = {
    "plan.md": doc(
        "type: plan",
        "status: stable",
        "title: Plan",
        "tags: [auth]",
        "supersedes: docs/specs/auth-sessions.md",
    ),
    "legacy-plan.md": doc("tags: [legacy]"),
}
REVIEWS = {
    "typed.md": doc("type: review", "title: Typed"),
    "untyped.md": doc("title: Untyped"),
    "empty.md": b"",
    "bodytype.md": doc("title: Body type", body="type: review\n"),
}

# Expected output, in the order by_file() gives.
STABLE_SPECS = [
    "docs/specs/auth-sessions.md: status: stable",
    "docs/specs/auth.md: status: stable",
    "docs/specs/crlf.md: status: stable",
    "docs/specs/stable.md: status: stable",
]
STABLE_PLAN = ["docs/plans/plan.md: status: stable"]
TAGGED_AUTH = [
    "docs/plans/plan.md: tags: [auth]",
    "docs/specs/auth.md: tags: [auth, login]",
]
TITLES = [
    "docs/plans/plan.md: title: Plan",
    "docs/specs/approved.md: title: Approved",
    "docs/specs/auth-sessions.md: title: Auth sessions",
    "docs/specs/auth.md: title: Auth",
    "docs/specs/body-example.md: title: Example doc",
    "docs/specs/bodytype.md: title: Body type",
    "docs/specs/crlf.md: title: Windows",
    "docs/specs/deprecated.md: title: Old",
    "docs/specs/draft.md: title: Draft",
    "docs/specs/legacy.md: title: Legacy",
    "docs/specs/stable.md: title: Billing",
]
SUPERSEDING = ["docs/plans/plan.md: supersedes: docs/specs/auth-sessions.md"]
UNMIGRATED = [
    "docs/plans/legacy-plan.md",
    "docs/specs/approved.md",
    "docs/specs/bodytype.md",
    "docs/specs/empty.md",
    "docs/specs/legacy.md",
    "docs/specs/nofm.md",
]
UNTYPED_REVIEWS = [
    "docs/reviews/bodytype.md",
    "docs/reviews/empty.md",
    "docs/reviews/untyped.md",
]
STATUS_AND_TAGS = [
    "docs/plans/legacy-plan.md: tags: [legacy]",
    "docs/plans/plan.md: status: stable",
    "docs/plans/plan.md: tags: [auth]",
    "docs/specs/approved.md: status: approved",
    "docs/specs/auth-sessions.md: status: stable",
    "docs/specs/auth-sessions.md: tags: [auth-sessions, pre-auth]",
    "docs/specs/auth.md: status: stable",
    "docs/specs/auth.md: tags: [auth, login]",
    "docs/specs/body-example.md: status: draft",
    "docs/specs/crlf.md: status: stable",
    "docs/specs/deprecated.md: status: deprecated",
    "docs/specs/draft.md: status: draft",
    "docs/specs/draft.md: tags: [billing]",
    "docs/specs/legacy.md: status: wip",
    "docs/specs/stable.md: status: stable",
    "docs/specs/stable.md: tags: [billing]",
]


def write_all(folder, documents):
    folder.mkdir(parents=True)
    for name, data in documents.items():
        (folder / name).write_bytes(data)


def build_docs(work, shared_plans):
    write_all(work / "docs/specs", SPECS)
    write_all(work / "docs/specs/archive", {"old.md": doc("type: spec", "status: stable")})
    write_all(work / "docs/reviews", REVIEWS)
    write_all(work / "docs/solo", {"only.md": doc("title: Only")})
    write_all(shared_plans, PLANS)
    os.symlink(shared_plans, work / "docs/plans")
    # docs/notes and docs/handoffs are absent on purpose.


class SkillCommandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        scratch = tempfile.TemporaryDirectory()
        cls.addClassCleanup(scratch.cleanup)
        root = Path(scratch.name).resolve()
        cls.work = root / "work"
        build_docs(cls.work, root / "shared-plans")
        home = root / "home"
        home.mkdir()
        cls.plain_env = scratch_env(home, os.environ["PATH"])
        cls.awk_envs = []
        for label, exe in discover_awks():
            if exe is None:
                cls.awk_envs.append((label, None))
                continue
            link = root / "awk" / label
            link.mkdir(parents=True)
            os.symlink(os.path.realpath(exe), link / "awk")
            path = f"{link}{os.pathsep}{os.environ['PATH']}"
            cls.awk_envs.append((label, scratch_env(home, path)))

    def each_awk(self, check):
        ran = 0
        for label, env in self.awk_envs:
            with self.subTest(awk=label):
                if env is None:
                    self.skipTest(f"{label} awk is not installed")
                ran += 1
                check(env)
        self.assertGreater(ran, 0, "no awk implementation was found")

    def check_output(self, command, env, expected, group=True, stderr_has=None):
        code, out, err = sh(command, self.work, env)
        self.assertEqual(code, 0, err)
        self.assertEqual(by_file(out) if group else exact_lines(out), expected)
        if stderr_has is None:
            self.assertEqual(err, "")
        else:
            for name in stderr_has:
                self.assertIn(name, err)

    def test_every_block_has_a_test_and_every_test_a_block(self):
        keys = set(shell_blocks())
        self.assertEqual(len(keys), BLOCK_COUNT)
        self.assertEqual(sorted(keys - set(COVERED)), [], "blocks with no test")
        self.assertEqual(sorted(set(COVERED) - keys), [], "tests with no block")
        self.assertEqual(len(COVERED), len(set(COVERED)))

    @covers(LIBRARY, "ls docs/specs/")
    def test_scope_lists_the_folder(self, text):
        code, out, err = sh(text, self.work, self.plain_env)
        names = sorted([*SPECS, "archive"])
        self.assertEqual((code, out, err), (0, "".join(f"{n}\n" for n in names), ""))

    @covers(LIBRARY, FIND_STABLE)
    def test_find_stable(self, text):
        self.assertTrue(text.endswith(f" {STABLE_TAIL}\n"))
        self.each_awk(
            lambda env: self.check_output(text, env, STABLE_SPECS)
        )

    def test_find_stable_with_absent_and_linked_folders(self):
        text = block(LIBRARY, FIND_STABLE)
        # CRLF, the symbolic-link folder, and a missing folder in one run.
        command = text.replace(
            "find -H docs/specs ", "find -H docs/specs docs/notes docs/plans ", 1
        )
        self.each_awk(
            lambda env: self.check_output(
                command, env, STABLE_PLAN + STABLE_SPECS, stderr_has=["docs/notes"]
            )
        )

    def test_inline_patterns_appear_in_the_skills(self):
        library = (ROOT / LIBRARY).read_text(encoding="utf-8")
        for pattern in (TAGS_PATTERN, TITLE_PATTERN, SUPERSEDES_PATTERN):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, library)
        requirements = (ROOT / REQUIREMENTS).read_text(encoding="utf-8")
        self.assertIn(SLUG_PATTERN, requirements)

    def extractor(self):
        text = block(LIBRARY, FIND_STABLE)
        self.assertTrue(text.endswith(f" {STABLE_TAIL}\n"))
        return text[: -len(STABLE_TAIL) - 1]

    def test_extractor_piped_into_the_inline_patterns(self):
        extractor = self.extractor()
        cases = (
            (TAGS_PATTERN, "docs/specs docs/plans", TAGGED_AUTH),
            (TITLE_PATTERN, "docs/specs docs/plans", TITLES),
            (
                SUPERSEDES_PATTERN,
                "docs/specs docs/plans docs/handoffs docs/notes",
                SUPERSEDING,
            ),
        )
        for pattern, folders, expected in cases:
            command = extractor.replace(
                "find -H docs/specs ", f"find -H {folders} ", 1
            ) + f"| {pattern}\n"
            with self.subTest(pattern=pattern):
                self.each_awk(
                    lambda env: self.check_output(
                        command,
                        env,
                        expected,
                        stderr_has=[f for f in ("docs/notes", "docs/handoffs") if f in folders]
                        or None,
                    )
                )

    @covers(LIBRARY, FIND_UNMIGRATED)
    def test_find_unmigrated(self, text):
        # docs/handoffs and docs/notes are absent; the other hits still print.
        self.each_awk(
            lambda env: self.check_output(
                text,
                env,
                UNMIGRATED,
                group=False,
                stderr_has=["docs/handoffs", "docs/notes"],
            )
        )

    def test_find_unmigrated_reports_the_last_file(self):
        # Only the END clause can report a lone untyped file.
        text = block(LIBRARY, FIND_UNMIGRATED)
        command = text.replace(
            "docs/specs docs/plans docs/handoffs docs/notes ", "docs/solo ", 1
        )
        self.each_awk(
            lambda env: self.check_output(
                command, env, ["docs/solo/only.md"], group=False
            )
        )

    def test_write_check_reports_the_last_file(self):
        text = block(LIBRARY, FIND_REVIEWS)
        command = text.replace("find -H docs/reviews ", "find -H docs/solo ", 1)
        self.each_awk(
            lambda env: self.check_output(
                command, env, ["docs/solo/only.md"], group=False
            )
        )

    @covers(LIBRARY, FIND_REVIEWS)
    def test_write_check_lists_untyped_reviews(self, text):
        self.each_awk(
            lambda env: self.check_output(text, env, UNTYPED_REVIEWS, group=False)
        )

    @covers(REQUIREMENTS, FIND_REQUIREMENTS)
    def test_requirements_extractor(self, text):
        self.assertTrue(text.endswith(f" {REQUIREMENTS_TAIL}\n"))
        self.each_awk(
            lambda env: self.check_output(text, env, STATUS_AND_TAGS)
        )
        slug = SLUG_PATTERN.replace("<slug>", "auth")
        command = text[: -len(REQUIREMENTS_TAIL) - 1] + f"| grep -E {slug}\n"
        self.each_awk(
            lambda env: self.check_output(command, env, TAGGED_AUTH)
        )


V1 = b"# Auth sessions\n\nSessions never expire.\n"
V2 = b"# Auth sessions\n\nRotate tokens on every request.\n"
OLD_PATH = "docs/specs/auth-sessions.md"
NEW_PATH = "docs/specs/sessions.md"


@unittest.skipUnless(
    shutil.which("jj") and shutil.which("git"), "Jujutsu and Git are required"
)
class PinAndCompareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        scratch = tempfile.TemporaryDirectory()
        cls.addClassCleanup(scratch.cleanup)
        root = Path(scratch.name).resolve()
        home = root / "home"
        home.mkdir()
        cls.env = scratch_env(home, os.environ["PATH"])
        cls.repo = root / "repo"
        cls.repo.mkdir()

        def jj(*args):
            command = [
                "jj", "--config", "user.name=Test",
                "--config", "user.email=test@example.com", *args,
            ]
            done = subprocess.run(
                command, cwd=cls.repo, env=cls.env, stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=30,
            )
            assert done.returncode == 0, done.stderr
            return done.stdout

        jj("git", "init", "--colocate", ".")
        spec = cls.repo / OLD_PATH
        spec.parent.mkdir(parents=True)
        spec.write_bytes(V1)
        jj("commit", "-m", "auth sessions")
        spec.write_bytes(V2)
        jj("commit", "-m", "tighten expiry")
        os.rename(spec, cls.repo / NEW_PATH)
        jj("commit", "-m", "rename to sessions")
        ids = jj(
            "log", "-r", "::@-", "--no-graph", "--reversed",
            "-T", 'commit_id ++ " " ++ change_id ++ "\\n"',
        ).split("\n")
        (cls.first, cls.first_change), (cls.second, _), (cls.third, _) = (
            line.split() for line in ids[1:4]
        )  # ids[0] is the root commit
        cls.short = sh(f"git rev-parse --short {cls.first}", cls.repo, cls.env)[1].strip()
        cls.short2 = sh(f"git rev-parse --short {cls.second}", cls.repo, cls.env)[1].strip()
        cls.short3 = sh(f"git rev-parse --short {cls.third}", cls.repo, cls.env)[1].strip()

    def run_lines(self, text):
        """Run each line with its placeholders filled; return the stdout list."""
        outputs = []
        for line in text.splitlines():
            for placeholder, value in (
                ("<old path>", OLD_PATH),
                ("<new path>", NEW_PATH),
                ("<rev>", self.first),
                ("<old>", self.first),
                ("<new>", self.second),
            ):
                line = line.replace(placeholder, value)
            with self.subTest(line=line):
                code, out, err = sh(line, self.repo, self.env)
                self.assertEqual(code, 0, err)
                outputs.append(out)
        return outputs

    @covers(PIN, PIN_RESOLVE)
    def test_resolve_a_revision(self, text):
        jj_out, git_out = self.run_lines(text)
        self.assertEqual(jj_out, f"{self.first_change[:12]} {self.first[:12]}\n")
        self.assertEqual(git_out, f"{self.short} auth sessions\n")

    @covers(PIN, PIN_READ)
    def test_read_at_a_revision(self, text):
        jj_out, git_out = self.run_lines(text)
        self.assertEqual((jj_out, git_out), (V1.decode(), V1.decode()))

    @covers(PIN, PIN_COMPARE)
    def test_compare_revisions(self, text):
        jj_pair, jj_working, git_pair, git_working = self.run_lines(text)
        for out in (jj_pair, jj_working):
            self.assertIn(f"regular file {OLD_PATH}:", out)
        self.assertIn("Sessions never expire.", jj_pair)
        self.assertIn("Rotate tokens on every request.", jj_pair)
        # The path moved, so the working copy has it deleted.
        self.assertIn("Sessions never expire.", jj_working)
        self.assertNotIn("Rotate tokens", jj_working)
        changed = lambda out: [l for l in out.splitlines() if l[:1] in "+-" and l[:3] not in ("+++", "---")]
        self.assertEqual(
            changed(git_pair),
            ["-Sessions never expire.", "+Rotate tokens on every request."],
        )
        self.assertEqual(
            changed(git_working),
            ["-# Auth sessions", "-", "-Sessions never expire."],
        )

    @covers(PIN, PIN_HISTORY)
    def test_list_history(self, text):
        jj_out, git_out = self.run_lines(text)
        for subject in ("rename to sessions", "tighten expiry", "auth sessions"):
            self.assertIn(subject, jj_out)
        self.assertEqual(
            git_out,
            f"{self.short3} rename to sessions\n"
            f"{self.short2} tighten expiry\n"
            f"{self.short} auth sessions\n",
        )

    @covers(PIN, PIN_MOVED)
    def test_follow_a_move(self, text):
        jj_out, git_out = self.run_lines(text)
        for subject in ("rename to sessions", "tighten expiry", "auth sessions"):
            self.assertIn(subject, jj_out)
        self.assertEqual(
            git_out,
            f"{self.short3} rename to sessions\n"
            f"{self.short2} tighten expiry\n"
            f"{self.short} auth sessions\n",
        )
        # jj log on the new path stops at the move; git --follow does not.
        code, out, err = sh(
            f"jj log --no-graph -T 'description.first_line() ++ \"\\n\"' {NEW_PATH}",
            self.repo, self.env,
        )
        self.assertEqual((code, out), (0, "rename to sessions\n"), err)


if __name__ == "__main__":
    unittest.main()
