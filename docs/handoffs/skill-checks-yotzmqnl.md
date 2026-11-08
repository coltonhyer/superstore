---
type: handoff
title: "Skill checks execution"
description: "Added the skill review checklist to REVIEW.md, command tests, rumdl, a required CI check on Ubuntu and macOS, and parallel eval runs, in the range umypuunv..ztoplkrt."
tags: [agent-skills, skill-evals, verification, continuous-integration]
implements: docs/plans/skill-checks.md
---

# Skill checks execution

- **Plan:** `docs/plans/skill-checks.md@umypuunv`
- **Spec:** `docs/specs/skill-checks.md@umypuunv`
- **Start:** `umypuunv` **Result:** `umypuunv..ztoplkrt`

## Whole-change checks

- `python3 -m unittest discover -s tests`: 73 tests OK at `ztoplkrt` under
  Python 3.12 and 3.13. Locally the gawk and BusyBox awk subtests skip
  (22), since only mawk is installed.
- Pull request #11, CI run 42454937802 on the final head:
  - Ubuntu: 73 tests OK with no skips, so mawk, gawk, and BusyBox awk all
    ran the command tests.
  - macOS: 73 tests OK, 33 skipped (the three awks macOS lacks, across 11
    command tests); BSD awk ran all 11.
  - rumdl passed on both.
- `uvx rumdl@0.3.2 check --no-cache .`: no issues in 29 files.
- Mutation spot-check, in a scratch copy of `plugins/` and `tests/`:
  removing `-H` from the library Find commands fails 8 tests, and removing
  the `\r` strip fails 4; the unmodified copy passes. During T2, the same
  edits made in the working copy and undone with `jj restore` failed 4 and
  3 tests.
- Live run of the library suite on claude, codex, and agy with the parallel
  runner: 30 of 30 captured, 0 errors, 162.4 s against 880.6 s of summed
  case time. See `evals/notebook/writeups/2026-11-08-parallel-runner.md`.
- First pass of the checklist over the ten skills: 129 findings, recorded
  as ten drafts titled `Skill review: <plugin>/<skill>` on the Superstore
  project. No skill file changed.
- `main`'s protection requires `checks (ubuntu-latest)` and
  `checks (macos-latest)`, without strict up-to-date branches; its other
  settings are unchanged.
- No plugin version bump: no file under `plugins/*/skills/` and no manifest
  changed. Under `plugins/`, only `plugins/planning/README.md` changed.

## Review outcomes and dispositions

### Spec and plan reviews

- Spec review: findings 1 to 6 and 8 Addressed. Finding 7 (`--jobs 1`) was
  Elevated; the user chose hosts side by side, then asked who wanted the
  flag at all, and the flag was removed for a fixed cap of four per host.
- Plan review: F1 to F5 and both nits Addressed. F1 made T7 wait for the
  user's push instruction.

### Task reviews

| Task | Outcome |
| --- | --- |
| T1 | T1-R1 (the `<change>` list closed by dropping "such as") Addressed; a pronoun nit applied. |
| T2 | T2-R1 (the `END` clause unprotected) and T2-R2 (the REVIEW.md bullet claimed more than the test runs) Addressed; T2-N1 and T2-N2 applied. |
| T3 | T3-R1 (one-shot interrupt sweep) Addressed; T3-N1 applied; T3-N2 Dismissed, since the extra summary fields predate the change. |
| T4 | T4-R1 (root Markdown files listed by name) Addressed with `./*.md`. |
| T5 | T5-R1 (a column's numbers did not match its stated source) Addressed; T5-N1 applied. |
| T6 | Checked by script: ten drafts, each body equal to its file. |

### Whole-change review

0 Important, 4 Nits:

- W-N1 (two rumdl comments name the rule, not a reason): Dismissed; the spec
  lists those two rules the same way.
- W-N2 (a truncated quote in the writeup): Addressed.
- W-N3 (a scheduling test asserts at least two at once, not four): Dismissed;
  it is loose on purpose, and the cap itself is asserted.
- W-N4 (the README omitted a fallback): Addressed.

### Pull-request CI repairs

The first CI run failed two tests.

- **C1 (both runners):** the interrupt test left a container unremoved.
  Root cause: on CPython 3.12, a signal that interrupts a timed
  `Thread.join` leaves `is_alive()` False while the thread still runs, so
  the cleanup loop ended early. Python 3.13, used locally, does not do this.
  Its fix reviews found more, each Addressed in `qwtwnozo`:
  - F1: a signal could lose a completion count and hang cleanup.
  - F2: a signal could skip cleanup while a host ran.
  - I1: the regression test for F1 fired at thread start instead.
  - Cleanup missed failures that were not signals; it now catches every
    exception.
  - The nits were applied, including making one new test deterministic.
- **C2 (macOS only):** a test that predates the change expected `/tmp`
  where macOS resolves `/private/tmp`. Fixed in the test, in `wrwrklmp`.
- The CI job gained `timeout-minutes: 15`, so a hanging test fails fast.

### Codex review on the pull request

- One P2 finding: two new runner tests ran `jj` through the real workspace
  setup without the skip guard the other jj tests carry, so the suite errored
  instead of skipping on a machine without jj.
- Addressed in `qwtwnozo`: both tests now skip without jj. With jj off
  `PATH`, 73 tests ran with 41 skipped and no errors; with jj, both run
  again, and the only skips are the 22 gawk and BusyBox awk subtests.

## Limitations

### Open or deferred

- The 129 first-pass findings are recorded, not fixed, by the user's
  decision. Each fix is its own change, with its eval suite.
- Vale, baseline runs, bundled scripts for the skills' commands, an install
  test, and a reviewer-isolation marker check are out of this change.

### Login safety

- The refresh rules are confirmed for the CLI versions pinned in
  `evals/Dockerfile`:
  - claude from the native binary's embedded JavaScript;
  - codex from its source at the matching release;
  - agy by disassembling a stripped binary.
- A CLI update can change them. A CLI that rewrites its credential file
  without refreshing would drop that host to one case at a time, the safe
  direction. The live run showed neither.
- The interrupt path is tested with fakes only; a real `docker rm --force`
  racing `docker run` was not exercised.

### Incident during T3

- An early draft of an interrupt test leaked a thread that ran real claude
  eval sessions for specs cases with the real login. The worker killed
  them, and the login file was not rewritten.
- Eight `/tmp/superstore-eval-state-*` folders, each private to the user
  and holding a copy of the credential, and three `/tmp/tmp*` result
  folders remained. The worker's sandbox refused their removal, and the
  user was asked to delete them; that is not confirmed here.

### Measurement and tooling

- The 2026-11-07 one-at-a-time library runs kept no timing, so the
  speed-up is measured against the run's own summed case time.
- One on-demand review against the checklist added explanation to each
  finding and also read the skill's eval cases, which the checklist does
  not ask for.
- `main`'s required checks are matched by name, not pinned to the GitHub
  Actions app.

## Tactical decisions

- **Execution id:** `skill-checks-yotzmqnl`, kept after the plan's revision
  was folded into `umypuunv`, as `okf-documents-pkqymxxw` was.
- **Tiers:** T3, its reviews, and the whole-change review ran at the
  strongest tier, because T3 handles login credentials. The other tasks
  used a mid-tier model, with reviews one tier up.
- **T5:** the supervisor ran the eval command itself, because the run
  outlasts a worker's foreground command limit. A worker wrote the record.
- **One checklist file (2026-11-08, the user's decision):** the separate
  `SKILL-REVIEW.md` was folded into REVIEW.md's "Skill text quality"
  section. The spec and plan were revised and re-approved for it.
- **History:**
  - each fix went into the commit that introduced the text;
  - the CI fixes for macOS went into the commit that added macOS to CI;
  - the spec and plan approvals were folded into one commit at the user's
    request.
