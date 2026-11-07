---
type: plan
title: "Skill checks plan"
description: "Seven tasks that add the skill review checklist to REVIEW.md, command tests, parallel eval runs, rumdl, and a required CI check, then test the runner once, review every skill, and land the change through a pull request."
status: stable
verified: { by: human:Colton Hyer, at: 2026-11-08T05:27:38Z }
tags: [agent-skills, skill-evals, verification, continuous-integration]
implements: docs/specs/skill-checks.md
---

# Skill checks plan

## Approved specification

- **Locator:** `docs/specs/skill-checks.md@umypuunv`

## Approach

Build the checks in the spec's order of value: the checklist, the command
tests, then the parallel runner. rumdl and the CI workflow come next, once
there are tests for CI to run. The two tasks that use model sessions follow:
one run of the library suite to test the runner, and one review of every skill
against the new checklist. The last task opens the pull request, makes both
CI runs green, and only then makes `main` require them.

Every task leaves `python3 -m unittest discover -s tests` passing. No task
edits a file under `plugins/*/skills/` or a manifest, so no version changes.
All work stays on the `skill-checks` bookmark above `umypuunv`, and nothing
is pushed to `main`. A fix to work from an earlier task goes into that task's
commit, as `REVIEW.md` requires. The execution's handoff note follows T7, as
the execution skills require, and is pushed to the same bookmark under T7's
instruction, so the pull request includes it.

## Tasks

### T1: Add the skill review checklist to REVIEW.md

- **Spec references:** Requirements and expected behavior, Skill review
  checklist; Verification, Checklist and first pass.
- **Deliverable:**
  - `REVIEW.md` gains a new `## Skill text quality` section between
    `## Always check` and `## Summary`, holding the spec's thirteen items.
    Each item asks its question and cites its agentskills.io page and section,
    as in the spec's table.
  - The section states the checklist's scope: a skill's `SKILL.md` and each
    file that `SKILL.md` links, except `okf-spec.md` and `okf-LICENSE.md`.
  - It also states the spec's rules for using it: it leaves out what tests
    and rumdl enforce; findings use the one-line format; in a change review,
    findings are Nits within the cap of five; findings are advisory; and an
    on-demand review lists every finding.
- **Prerequisites and order:** None. First task.
- **Relevant paths and patterns:**
  - Item sources, which the spec's table names:
    - `https://agentskills.io/skill-creation/best-practices`
    - `https://agentskills.io/specification`
    - `https://agentskills.io/skill-creation/optimizing-descriptions`
  - Write in `REVIEW.md`'s register: short imperative bullets, no preamble.
  - The commit message says the new section sits outside the sections that
    `AGENTS.md` ties to recorded failures.
- **Completion check:**
  - Every checklist item names a page and a section heading that exists on
    that page.
  - `REVIEW.md` has the section between `## Always check` and `## Summary`.
  - `python3 -m unittest discover -s tests` passes.

### T2: Test the skills' shell commands

- **Spec references:** Requirements and expected behavior, Command tests;
  Verification, Unit tests (command tests) and Mutation spot-check.
- **Deliverable:**
  - `tests/test_skill_commands.py` finds every fenced `sh`, `bash`, or
    `shell` block, indented or not, in `plugins/*/skills/*/SKILL.md` and
    `plugins/*/skills/*/references/*.md`. It removes the fence's indentation
    and keys each block by file and first line.
  - It asserts that it finds ten blocks, that each one has a test, and that
    each test's key has a block.
  - It runs each block against fixtures built at run time, with the
    environment, `awk` matrix, and exact expected output the spec sets.
  - It runs the Pin and compare lines in a scratch colocated repository.
  - It runs the library and requirements skills' inline `grep` patterns,
    after asserting that each appears verbatim in its skill.
  - `REVIEW.md`'s "Run every changed shell snippet" bullet narrows to the
    snippets the test doesn't run, and names the test.
- **Prerequisites and order:** None; after T1 so that both `REVIEW.md` edits
  sit in separate commits.
- **Relevant paths and patterns:**
  - The blocks:
    - `plugins/library/skills/library/SKILL.md`, at lines 109, 128, 162, and
      205;
    - `plugins/library/skills/library/references/pin-and-compare.md`, five
      blocks;
    - `plugins/planning/skills/requirements/SKILL.md`, at line 42.
  - The inline patterns are on lines 140 to 145 of the library skill, and in
    the requirements skill's sentence after its block.
  - Follow `tests/test_marketplace.py` and `tests/test_eval_runner.py`: plain
    `unittest`, with `subTest` for each block and each `awk` implementation.
    Tests that need jj use `skipUnless(shutil.which("jj"), ...)`.
  - Use the fixture list in the spec as written:
    - the symbolic-linked `docs/plans/` holds a stable plan that the expected
      output includes;
    - `docs/notes/` is absent;
    - files with CRLF endings and symbolic links are created in the test.
  - Commands run under `sh -c`, with stdin from `/dev/null`,
    `JJ_CONFIG=/dev/null`, `JJ_EDITOR=false`, `GIT_EDITOR=false`, and a
    scratch `HOME`.
  - To build the scratch repository, pass identity as flags: `--config` for
    `jj`, `-c user.name=... -c user.email=...` for `git`.
  - The commit message names the test as the reason the `REVIEW.md` bullet
    narrowed.
- **Completion check:**
  - `python3 -m unittest tests.test_skill_commands -v` passes under every
    `awk` present.
  - In a scratch copy of the library skill, removing `-H` from a Find command,
    or its `\r` strip, makes a test fail, and restoring it passes. Make the
    edit in the working copy and undo it with `jj restore <path>`, so no diff
    under `plugins/*/skills/` remains. The result goes in the task report and
    the handoff note.

### T3: Run eval cases in parallel

- **Spec references:** Requirements and expected behavior, Parallel eval
  runs; Verification, Unit tests (runner).
- **Deliverable:** `scripts/run_skill_evals.py` with:
  - **Plugins:** `--plugin` that repeats, defaulting to `plugins/planning`
    when none is given. The run refuses to start when two selected plugins
    share a skill name.
  - **At once:** hosts run side by side, with at most four sessions per host
    at once, set by one constant, and each host starts its cases in case
    order.
  - **Login safety,** exactly as the spec states:
    - each host's first case runs alone;
    - a later case runs alongside others only while its window holds;
    - a host whose rule can't be read or confirmed runs one case at a time,
      and the run says so;
    - a refresh during a parallel case drops that host to one case at a time,
      with a warning;
    - write-backs to the home directory happen under a lock per host.
  - **Each host's refresh rule** goes in a comment table in the runner, with
    its source, confirmed for the CLI versions pinned in `evals/Dockerfile`.
    Any host not confirmed there is marked one case at a time.
  - **Output:** progress lines print whole. A final line gives the counts and
    wall time. `summary.json` gains `started_at`, `wall_seconds`, and
    `refreshed_login` for each result, and lists results by host, then case
    order.
  - **Interrupts:** SIGINT and SIGTERM stop new cases and remove every
    tracked container. Running cases still finish their cleanup, and the run
    exits nonzero with no `summary.json`.
  - **Tests:** new tests in `tests/test_eval_runner.py` cover each behavior
    the spec's Verification lists for the runner.
  - **Docs:** the Validation section of `plugins/planning/README.md` documents
    repeated `--plugin` and that hosts and cases run at once.
- **Prerequisites and order:** None; after T2.
- **Relevant paths and patterns:**
  - Leave `run_case` unchanged except for the hooks the scheduler needs:
    tracking container names, the per-host write-back lock, and recording a
    refresh.
  - `persist_auth` already lets the newer file time win. Keep it, and add the
    lock around it.
  - Use threads: each case's work is a `docker` subprocess.
  - Read expiry from the home credential:
    - claude: `claudeAiOauth.expiresAt`, in milliseconds;
    - codex: the `exp` claim of the JWT `tokens.access_token`, decoded
      locally without verification, and `last_refresh` plus the interval;
    - agy: `token.expiry`, an RFC 3339 string that may carry nanoseconds.
  - A case's window ends 10 minutes after `start + turns × (timeout + 30)`
    seconds.
  - To confirm each rule, read the pinned CLI where its code is readable:
    - claude: `cli.js` in `@anthropic-ai/claude-code@2.1.251`, inside the eval
      image;
    - codex: the public `openai/codex` source at the release matching
      `0.155.0`;
    - agy: whether the binary in the image links `golang.org/x/oauth2`, whose
      tokens refresh 10 seconds before `expiry`.
  - Never print or log token values. Read only the expiry fields.
  - Run each case with its own plugin root, derived from
    `case.definition_dir` (`<plugin>/skills/<skill>/evals`), not one root for
    the whole run.
  - Mock `run_turn`, `seed_auth`, and `persist_auth` as the two `run_case`
    tests in `WorkspaceTests` do
    (`test_run_case_redacts_credential_leaks_and_discards_workspace` and
    `test_run_case_retains_codex_reviewer_provenance`), or mock `run_case`
    itself for scheduling tests.
- **Completion check:**
  - `python3 -m unittest discover -s tests` passes, including the new runner
    tests.
  - `python3 scripts/run_skill_evals.py --plugin plugins/library --list`
    still lists ten cases.
  - Repeating `--plugin` lists both plugins' cases.
  - The task report names, for each host, whether its refresh rule was
    confirmed and from which source, and which hosts run one case at a time.

### T4: Add rumdl, the CI workflow, and the Checks section

- **Spec references:** Requirements and expected behavior, rumdl and CI;
  Verification, rumdl and Docs.
- **Deliverable:**
  - **`.rumdl.toml`** checks Markdown under `plugins/` and at the root, and
    excludes what the spec names. It disables MD013, MD038, MD048, and MD076,
    each with a comment giving the spec's reason.
  - **`.github/workflows/checks.yml`** runs on pull requests to `main` with
    `contents: read`. Its job `checks` runs on `ubuntu-latest` and
    `macos-latest`, and each run:
    1. installs a pinned Python version (3.10 or later) and jj 0.44.0, with a
       SHA-256 check, plus gawk on Ubuntu;
    2. runs `python3 -m unittest discover -s tests`;
    3. installs rumdl 0.3.2 and runs `rumdl check --no-cache .`.
  - **`AGENTS.md`** gains a "Checks" section with the two local commands, and
    the spec's statement of when evals run.
- **Prerequisites and order:** T2 and T3, so that CI runs their tests.
- **Relevant paths and patterns:**
  - The Linux jj archive and checksum match `evals/Dockerfile`:
    - `jj-v0.44.0-x86_64-unknown-linux-musl.tar.gz`
    - `0a07bab4641a55fd2bc2fd1563ba3a3f9a577584086ad74086a1c5b69b3ffce9`
  - For the macOS archive, `jj-v0.44.0-aarch64-apple-darwin.tar.gz`, compute
    the SHA-256 from a download and commit it in the workflow.
  - Pin `actions/checkout` and `actions/setup-python` to the full commit SHA
    of a release tag, found with `git ls-remote`, with the tag in a comment.
    Set `persist-credentials: false` on checkout.
  - Install rumdl with `python -m pip install rumdl==0.3.2`.
  - Locally, `uvx rumdl@0.3.2 check --no-cache .` must pass, with no checked
    file edited.
- **Completion check:**
  - `uvx rumdl@0.3.2 check --no-cache .` reports no issues.
  - `python3 -m unittest discover -s tests` passes.
  - The task's revision changes only `.rumdl.toml`, the workflow, and
    `AGENTS.md`.
  - The CI runs themselves are checked in T7.

### T5: Run the library suite once with the parallel runner

- **Spec references:** Non-goals (one ungraded library run); Verification,
  Live run.
- **Deliverable:**
  - One run of
    `python3 scripts/run_skill_evals.py --plugin plugins/library --host claude --host codex --host agy --output <new root>`
    that ends with no error results.
  - A writeup at `evals/notebook/writeups/<run date>-parallel-runner.md`, and
    a `BOOK.md` row marked not graded. They record:
    - the command, wall time, and counts;
    - for each host, whether its cases ran at once, each login refresh, and
      any drop to one case at a time;
    - the comparison time.
- **Prerequisites and order:** T3.
- **Relevant paths and patterns:**
  - Use `--output .agents/eval-results/<run date>-parallel-runner`, and add
    `/.agents/eval-results/<run date>-parallel-runner/` to
    `.git/info/exclude`, as earlier runs did. The writeup names it as the
    retained artifact root.
  - The latest one-at-a-time library runs, on 2026-11-07, kept no timing.
    The comparison is therefore what one at a time would take: the run's own
    case durations, summed per host and across hosts. The writeup says so.
  - Follow the existing writeups for layout, and REVIEW.md's notebook rules.
  - An error result is diagnosed before any rerun. A runner bug is fixed in
    T3's commit.
- **Completion check:**
  - `summary.json` shows ten results per host with status `captured`.
  - The writeup and the `BOOK.md` row agree on the counts.

### T6: Review every skill against the checklist

- **Spec references:** Requirements and expected behavior, First pass;
  Verification, Checklist and first pass.
- **Deliverable:**
  - One fresh reviewer for each of the ten skills reads it against the
    checklist in `REVIEW.md`.
  - Each skill with findings gets a draft item on the Superstore project
    (`gh project item-create 3 --owner coltonhyer`), titled
    `Skill review: <plugin>/<skill>`. Its body lists the findings, one line
    each in the spec's format, and the SHA-256 of the `SKILL.md` reviewed.
- **Prerequisites and order:** T1.
- **Relevant paths and patterns:**
  - Give each reviewer the checklist and the skill's folder, and nothing from
    this conversation.
  - Reviewers report findings only. They don't edit.
  - No repository file changes in this task.
- **Completion check:**
  - `gh project item-list 3 --owner coltonhyer` shows one draft for each
    skill with findings, each finding line in the stated format.
  - `jj diff --from main --stat` lists no path under `plugins/*/skills/`.

### T7: Open the pull request and require its checks

- **Spec references:** Requirements and expected behavior, CI; Verification,
  CI.
- **Deliverable:**
  - The `skill-checks` bookmark is pushed, and a pull request to `main` is
    open.
  - Both `checks` runs pass on its latest commit.
  - After the first green run, `main`'s protection requires
    `checks (ubuntu-latest)` and `checks (macos-latest)`, without strict
    up-to-date branches. Every other protection setting stays as it is.
- **Prerequisites and order:** T1 to T6, and the user's explicit instruction
  to push, given when execution reaches T7. Approving this plan is not that
  instruction. This is the one place the plan departs from
  `implementing-plans`' "Do not push, create a PR/MR", and the protection
  change waits for the same instruction.
- **Relevant paths and patterns:**
  - Push with `jj git push --bookmark skill-checks`, and open the pull
    request with `gh pr create --base main`. The body ends with the Claude
    Code footer.
  - A CI failure is root-caused. Fix it in the commit that introduced it,
    then push again. A test that fails on macOS for a platform reason is
    fixed, never skipped.
  - Set protection with
    `gh api -X PUT repos/coltonhyer/superstore/branches/main/protection`,
    sending every current setting along with the new required checks. Never
    merge the pull request; that is the user's call.
- **Completion check:**
  - `gh pr checks` shows both `checks` runs passing on the pull request's
    latest commit, which includes the handoff note.
  - `gh api repos/coltonhyer/superstore/branches/main/protection` lists both
    as required, with the other settings unchanged.
