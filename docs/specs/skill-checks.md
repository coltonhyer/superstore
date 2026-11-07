---
type: spec
title: "Skill checks"
description: "Signal on a skill file without an eval run, from a skill review checklist in REVIEW.md, command tests, and rumdl in a required CI check, plus eval runs that go side by side."
status: stable
verified: { by: human:Colton Hyer, at: 2026-11-08T05:27:38Z }
tags: [agent-skills, skill-evals, verification, continuous-integration]
---

# Skill checks

## Summary

Add checks that give signal on a skill file without an eval: a checklist in
REVIEW.md that a model reads a skill against, unit tests that run the skills'
shell commands, and rumdl, with the tests and rumdl in a GitHub Actions
workflow that `main` requires. Make eval runs faster by running hosts side by
side and several cases per host at once. Run the checklist over every current
skill once and record what it finds; fix nothing in the skills.

## Context and motivation

- An eval run is the only signal on a skill file today. The 2026-11-02 full
  run took about an hour, because the runner runs one host after another and
  one case at a time.
- REVIEW.md asks reviewers to run every changed shell snippet by hand. The
  skills' commands have only run under mawk; BSD and macOS `awk` and `find`
  never ran them (Limitations in `docs/handoffs/okf-documents-pkqymxxw.md`).
- Nothing checks whether a skill's text is instructive or distracting, though
  agentskills.io publishes best practices for exactly that.

## Goals and non-goals

Goals, in order of value:

1. A skill review checklist in REVIEW.md, built from agentskills.io.
2. Command tests for every shell block in the skills.
3. Parallel eval runs.
4. rumdl.
5. A required CI check on every pull request to `main` that runs 2 and 4.
6. One pass of the checklist over all ten current skills, with the findings
   recorded.

Non-goals:

- Fixing what the checks find in the current skills. Each fix is a later
  change. This one changes no file under `plugins/*/skills/`, so it needs no
  version bump and no skill eval rerun.
- Vale, until a headache repeats. Baseline runs, until a skill is heavily
  rewritten. Bundled scripts that replace inline commands, since they change
  skill text.
- `claude plugin validate`: all four plugins pass, and the unit tests already
  check the manifests.
- A token-count check: the 240-line limit keeps every skill near 3,000
  tokens or less.
- Linting `docs/` or `evals/notebook/`.
- Any eval run beyond one run of the existing library suite, which tests the
  changed eval script. That run is not graded.

## Requirements and expected behavior

### Skill review checklist

`REVIEW.md` gains a `## Skill text quality` section between `## Always check`
and `## Summary`. It holds a checklist a model reads one skill against: its
`SKILL.md` and each file that `SKILL.md` links, except the vendored OKF copies
(`okf-spec.md` and `okf-LICENSE.md`), which are never edited. Each item cites
the agentskills.io page and section it comes from:

| Item | What to ask of each passage | Source |
| --- | --- | --- |
| Earns its place | Would the agent get this wrong without it? If not, cut it; if unsure, mark it "test it". | Best practices: Add what the agent lacks, omit what it knows |
| Moderate detail | Edge cases the agent's judgment handles are left to it. | Best practices: Aim for moderate detail |
| Coherent unit | The skill does one job, needs no other skill for its core task, and covers no second job. | Best practices: Design coherent units |
| When to load | Each reference link says when to read it, and references are one level deep. | Best practices: Structure large skills with progressive disclosure; Specification: File references |
| Specificity matches fragility | Exact commands where an operation is fragile; elsewhere the reason, not rigid steps. | Best practices: Match specificity to fragility |
| Defaults, not menus | One default, with alternatives named briefly. | Best practices: Provide defaults, not menus |
| Procedure, not answer | It teaches a method for the class of task, not one instance's answer. | Best practices: Favor procedures over declarations |
| Gotchas up front | Corrections to mistakes the agent would otherwise make sit in `SKILL.md`, before the step they affect. | Best practices: Gotchas sections |
| Template for output | Output with a required shape has a template, not a prose description. | Best practices: Templates for output format |
| Checkable gates | Multi-step work with gates has a checklist or a validation step. | Best practices: Checklists for multi-step workflows; Validation loops; Plan-validate-execute |
| Script candidate | A command the agent must rebuild or adapt on every run. | Best practices: Bundling reusable scripts |
| Specific, not generic | No advice every agent already follows, such as "handle errors appropriately". | Best practices: Start from real expertise |
| Description | It says what the skill does and when to use it, in terms of what the user wants, in a few sentences. | Specification: `description` field; Optimizing skill descriptions: Writing effective descriptions |

- The checklist leaves out what a test or rumdl enforces, such as the 240-line
  limit (`test_skill_files_fit_one_codex_read`) and links that resolve.
- Each finding is one line,
  `<file>:<line> | <item> | "<quoted text>" | <change>`, where `<change>`
  names the change in a few words, such as cut, move to a reference with a
  when-to-load line, pick a default, or test it.
- Findings are advisory and block nothing. When the same text is also one of
  REVIEW.md's Important classes, REVIEW.md's own rules apply to it.
- For a change to skill text, a reviewer reads each changed skill against the
  checklist and reports its findings as Nits, within REVIEW.md's cap of five.
  The section sits outside the two sections that `AGENTS.md` ties to recorded
  failures, because its items come from agentskills.io.
- Asked on demand to review a skill against the checklist, a model lists every
  finding.

### Command tests

`tests/test_skill_commands.py` runs the skills' shell commands.

- **Coverage.** Every fenced block tagged `sh`, `bash`, or `shell` in
  `plugins/*/skills/*/SKILL.md` and `plugins/*/skills/*/references/*.md` is
  covered. A fence may be indented, as inside a list item, and the block's
  lines then lose the fence's indentation. Today that is ten blocks in three
  files, and the coverage test asserts that count. The inline `grep`
  patterns that the library and requirements skills pair with their
  frontmatter extractor also run: the test asserts each appears verbatim in
  its skill, then pipes the extractor into it.
- **Read from the skill.** Each block is read from its skill file at run time
  and keyed by file and first line. A block with no test, or a key whose
  block is gone, fails the suite.
- **Non-interactive.** Commands run under `sh -c` with stdin from
  `/dev/null`, `JJ_CONFIG=/dev/null`, `JJ_EDITOR=false`, `GIT_EDITOR=false`, a
  scratch `HOME`, and a timeout. A command that waits for an editor or for
  input fails.
- **Every awk.** A command that uses `awk` runs once for each implementation
  present among mawk, gawk, BusyBox `awk`, and the system `/usr/bin/awk`
  (BSD `awk` on macOS), through a folder with an `awk` link placed first on
  `PATH`. Each run is a subtest named after its implementation.
- **Fixtures.** They are built in a temporary folder at run time, so CRLF
  bytes and symbolic links don't depend on checkout settings:
  - `docs/specs/`: stable, draft, deprecated, and status-less documents; a
    draft whose body holds a fenced example frontmatter block with
    `type: spec` and `status: stable`; an empty file; a file with no
    frontmatter; a stable document with CRLF line endings; `index.md` and
    `log.md` with frontmatter; documents tagged `auth` and `auth-sessions`; a
    `status: approved` document; and a `.txt` file.
  - `docs/plans/`: a symbolic link to a folder outside `docs/` that holds a
    stable plan, which the expected output includes.
  - `docs/notes/`: absent.
  - `docs/reviews/`: a typed document, an untyped one, an empty one, and one
    whose only `type:` line is in its body.
- **Exact output.** Each command's expected stdout is exact. With a folder
  absent, the test also checks that the command still prints the other
  folders' hits.
- **Pin and compare.** The commands run line by line in a scratch colocated
  Jujutsu and Git repository whose history adds `docs/specs/auth-sessions.md`
  in a commit described "auth sessions", changes it, and then moves it.
  `<rev>`, `<old>`, `<new>`, `<old path>`, and `<new path>` are replaced with
  that history's revisions and paths. Each line exits 0 and prints the
  expected revision or content.
- **REVIEW.md.** Its "Run every changed shell snippet" bullet narrows to the
  snippets the command tests don't run, and names the test.

### rumdl

- `.rumdl.toml` at the root checks the Markdown under `plugins/` and the root
  Markdown files. It excludes eval fixtures (`plugins/*/skills/*/evals/`), the
  vendored OKF files (`okf-spec.md` and `okf-LICENSE.md`), and `CLAUDE.md`,
  which is a one-line import.
- It keeps rumdl's default rules except four, each disabled with a comment
  giving the reason:
  - MD013, line length.
  - MD038, spaces in code spans: the skills quote `grep` patterns that start
    or end with a space.
  - MD048, fence style: the requirements skill wraps its Markdown template in
    `~~~`.
  - MD076, blank lines between list items.
- It runs with `--no-cache`. While this spec was drafted, a stale
  `.rumdl_cache` reported an existing heading as missing.
- The version is pinned to 0.3.2, in CI and in the local command.
- The files it checks pass unchanged. A run with these settings on 2026-11-07
  found no issues in 29 files.

### CI

- `.github/workflows/checks.yml` runs on every pull request to `main`, with
  read-only repository permissions and actions pinned to full commit SHAs.
- A job named `checks` runs on `ubuntu-latest` and `macos-latest`:
  1. It installs a pinned Python, jj 0.44.0 from its release archive with a
     SHA-256 check (the Linux checksum matches `evals/Dockerfile`), and gawk
     on Ubuntu.
  2. It runs `python3 -m unittest discover -s tests`. With jj installed, the
     tests that need jj run instead of skipping. A test that fails on macOS
     because of a platform difference is fixed, not skipped.
  3. It installs rumdl 0.3.2 and runs `rumdl check --no-cache .`.
- After the workflow's first green run on this change's pull request, `main`'s
  protection requires both `checks` runs, Ubuntu and macOS, without requiring
  branches to be up to date. Its other settings stay: a pull request required,
  no approvals needed, admins included, no force pushes, and no deletions.
- `AGENTS.md` gains a "Checks" section with the two local commands,
  `python3 -m unittest discover -s tests` and
  `uvx rumdl@0.3.2 check --no-cache .`. It also says when evals run: a skill
  change merges on these checks and a review against REVIEW.md's skill
  checklist, without an eval run. The eval suites run after a heavy rewrite of a skill,
  or after a batch of changes before installed plugins are updated, and the
  eval notebook records which changes each run covered.

### Parallel eval runs

- **Plugins.** `--plugin` may repeat; with none given, it stays
  `plugins/planning`. The run takes the cases of every selected plugin,
  filtered by `--skill` and `--case` as today. It refuses to start when two
  selected plugins share a skill name, since their result folders would
  collide.
- **At once.** Hosts run side by side, and at most four sessions of one host
  run at once, a constant in the runner rather than a flag. Each host starts
  its cases in case order.
- **Cases unchanged.** Each case still runs through `run_case`, with its own
  result folder, state folder, and containers, so prompts, workspaces, and
  evidence don't change.
- **Login safety**, per host:
  - The host's first case runs alone, so a refresh due at startup happens
    once.
  - A later case starts alongside other cases of its host only when the
    login's access token, as recorded in the home directory, stays valid
    until 10 minutes past the case's worst end: its start plus
    `timeout + 30` seconds per turn. Otherwise the case waits until no other
    case of its host is running, then runs alone.
  - The expiry comes from `claudeAiOauth.expiresAt` for claude and
    `token.expiry` for agy. For codex it is the earlier of the `exp` claim of
    `tokens.access_token` and `last_refresh` plus the pinned Codex CLI's
    refresh interval. A host whose expiry can't be read runs one case at a
    time, and the run says so.
  - This rests on each pinned CLI refreshing only when that time says so. The
    plan confirms each CLI's rule before relying on it, and a host whose rule
    isn't confirmed runs one case at a time. A CLI that refreshes some other
    way is caught by the next check, after at most one overlapping refresh
    per host per run.
  - When a case that ran alongside others still refreshed its login, because
    its state copy ends newer than the copy it was seeded with, the host runs
    one case at a time for the rest of the run, and the run prints a warning
    naming the host.
  - Writing a refreshed login back to the home directory stays as today (the
    newer file time wins, by atomic replace), now under a per-host lock.
- **Output.** Progress lines stay as today and print whole. The run ends with
  one line giving the captured and error counts and the wall time.
  `summary.json` gains `started_at` and `wall_seconds`, lists
  results by host, then case order, and notes for each result whether the
  case refreshed its host's login. Result folders keep the layout
  `<output>/<host>/<skill>-<id>/`.
- **Interrupts.** On SIGINT or SIGTERM, the runner starts no more cases,
  removes every container it started that is still running, lets running
  cases finish their cleanup (login write-back and workspace discard), and
  exits nonzero without writing `summary.json`, as today.
- **Docs.** The Validation section of `plugins/planning/README.md` documents
  a repeated `--plugin` and that hosts and cases run at once.

### First pass

- With the checklist in place, one fresh reviewer reads each of the ten skills
  against it.
- Each skill with findings gets one draft item on the Superstore project,
  titled `Skill review: <plugin>/<skill>`. It lists the findings and the
  SHA-256 of the `SKILL.md` that was reviewed.
- The CI run is rumdl's first pass. It finds nothing under the committed
  settings.

### Version bumps

None. The change touches no skill, reference, or manifest, and changes to
READMEs, `REVIEW.md`, and `AGENTS.md` need no bump.

## Verification

### Unit tests (`python3 -m unittest discover -s tests`)

- **Command tests:**
  - Every block runs against the fixtures under each `awk` present, with
    exact output.
  - These behave as the skills claim: a missing folder, a symbolic-link
    folder, CRLF, empty files, frontmatter in a body, `index.md` and `log.md`,
    hyphenated tags, and an invalid status.
  - The Pin and compare lines run in the scratch repository.
  - The coverage test fails for a block with no test and for a key with no
    block.
- **Runner**, with fake hosts (`run_turn`, `seed_auth`, and `persist_auth`
  mocked):
  - No host exceeds four sessions at once, hosts overlap, and every selected
    case runs once.
  - A skill name shared by two plugins is refused.
  - The expiry rule runs a short-lived login's case alone, and a login whose
    expiry can't be read one case at a time.
  - A refresh during a parallel case drops its host to one case at a time.
  - A write-back never replaces a newer login.
  - SIGTERM removes every container the run tracked.
  - `summary.json` has the new fields and order.
- **Existing:** the 42 existing tests still pass.

### Mutation spot-check (recorded in the handoff note)

- Removing `-H` from a library Find command, or its `\r` strip, makes a
  command test fail, and restoring it makes the test pass again.

### rumdl

- `rumdl check --no-cache .` at 0.3.2 passes with the committed settings, and
  no checked file changed.

### CI

- The workflow passes on Ubuntu and macOS on this change's pull request.
- `gh api repos/coltonhyer/superstore/branches/main/protection` lists both
  `checks` runs as required and the other settings unchanged.

### Live run

- `python3 scripts/run_skill_evals.py --plugin plugins/library --host claude
  --host codex --host agy --output <new root>` finishes with no error
  results.
- The eval notebook records the command, wall time, and counts, next to the
  latest one-at-a-time library run's time. For each host it also records
  whether its cases ran at once and any drop to one case at a time.

### Checklist and first pass

- Every checklist item in `REVIEW.md` names its source page and section.
- `REVIEW.md` has the "Skill text quality" section and the narrowed snippet
  bullet.
- The Superstore project has one draft per skill with findings, each finding
  in the stated format.
- The change's diff from `main` touches no file under `plugins/*/skills/`.

### Docs

- `AGENTS.md`'s Checks section matches the workflow and states when evals
  run, and the Planning README's runner section matches the runner.

## Alternatives and consequential decisions

- **`claude plugin eval`** runs cases concurrently and has a no-plugin
  baseline, but only on Claude; the suites need codex and agy. It is worth a
  look for Claude baselines later.
- **Commands copied into tests** would drift from the skills, so the tests
  read them from the skill files.
- **Committed fixture files** would depend on checkout settings for CRLF and
  symbolic links, so the fixtures are built at run time.
- **Locking token refreshes** isn't possible from outside the containers,
  where the CLIs refresh, so the runner schedules around token expiry instead.
- **Blocking findings** would turn judgment calls into merge gates, and
  agentskills.io says to test what reading can't settle.
- **A separate `SKILL-REVIEW.md`** was dropped (the user's decision on
  2026-11-08). AGENTS.md's precedent rule covers only two sections of
  REVIEW.md, so the checklist fits there. Every reviewer already reads
  REVIEW.md, so the checklist can't be skipped the way a pointer to a second
  file can.
- **No flag for the cap.** Nobody asked for one, and the login rules already
  fall back to one case at a time. If an account allows fewer than four
  sessions at once, the constant changes.
