# OKF documents evaluations — 2026-11-02

This writeup records the live validation run for the OKF documents change:
the change that made the Library skill read and write Open Knowledge Format
documents under `docs/`, and moved Planning and Implementation onto status,
`verified`, and handoff notes in that format. The specification is
`.agents/library/specs/okf-documents.md@xknlouww` and the plan is
`.agents/library/plans/okf-documents.md@pkqymxxw`. The repository has since
moved both to `docs/specs/okf-documents.md` and `docs/plans/okf-documents.md`.
The skill text under test is the tree recorded at `lptmrtkx`
(commit `3412f167`); the working copy equalled it for every run. Original
observations are immutable; dispositions are recorded as separate evidence.
Assessments use the [notebook policy](../BOOK.md#interpretation).

Correction, added with the [follow-up runs](#follow-up-runs): commit
`3412f167` is no longer an ancestor of the branch, because later repairs and a
fold rewrote it, and `lptmrtkx` now holds later text. The text the 183 matrix
runs saw is identified by checksum under [Tested text](#tested-text), and the
sentence above is kept as the original observation.

Correction, 2026-11-07: the plan's approval revision `pkqymxxw` was squashed
into the spec's approval revision `xknlouww`, so the plan now reads at
`.agents/library/plans/okf-documents.md@xknlouww`. The plan locator above
is kept as the original text.

Correction, 2026-11-07: the spec's later revisions and their approvals were
folded into `xknlouww` as well, so the spec locator above now reads the final
approved spec. The 183 matrix runs were checked against the original approved
text, `sha256:a33217c0aadb0915…`, which is no longer in history.

The retained artifact root is
`.agents/eval-results/2026-11-01-okf-documents/`, excluded from version
control. Layout: `<stage>-<host>/<suite>/<host>/<suite>-<n>/`, with stages
`stage1-claude`, `stage2-codex`, and `stage2-agy`. Each run holds the prompt,
result record, raw event stream, provider trace where the host supplies one,
before and after repository evidence, and the final workspace. Each suite
directory also holds the runner's `summary.json`. The assessment reports that
the counts below come from were written by delegated reviewers and are in the
execution scratch, not retained here.

Subjects (the runner defaults in `scripts/skill_eval_hosts.py`): Claude Code
`claude-sonnet-5` at high effort; Codex `gpt-5.6-terra` at high effort;
Antigravity `gemini-3.8-flash-high`, where the effort is part of the model
id. The eval container is built from `evals/Dockerfile`, which pins jj 0.44.0,
Codex 0.155.0, Claude Code 2.1.251, and Antigravity CLI 1.4.0.

## Matrix

The approved matrix was every case of the six affected suites on all three
hosts, one run per case, in two stages: stage 1 ran the six suites on `claude`
(2026-11-01, about 23:16 to 23:42 UTC); stage 2 ran them on `codex` and `agy`
(about 23:43 UTC on 2026-11-01 to 00:20 UTC on 2026-11-02). Within a stage the
suites ran concurrently; each run has its own container and state directory.

| Suite | Cases |
| --- | --- |
| library | 9 |
| specs | 14 |
| requirements | 6 |
| plans | 12 |
| implementing-plans | 10 |
| subagent-execution | 10 |

That is 61 cases × 3 hosts = 183 runs. All 183 have a `result.json` with
status `captured`, and every `summary.json` reports 0 errors. No run was
`Invalid evaluation`.

Correction: the 61 cases include library cases 1 to 9 only. `library/10`,
whose bodies carry example frontmatter, was added after this matrix and is
covered only by the follow-up runs.

Commands, one process per suite and host, run from the repository root:

```sh
python3 scripts/run_skill_evals.py --plugin plugins/<plugin> --skill <suite> --host <host> --output .agents/eval-results/2026-11-01-okf-documents/<stage>-<host>/<suite>
```

Deviation: the plan called for `--output .../<plugin>`. The output went per
suite instead, because each runner process writes `summary.json` at its output
root and the suites ran concurrently, so per-plugin roots (`planning` holds
two suites in this matrix, `implementation` holds three) would have overwritten one another.
Tactical, no effect on the runs.

No material failure traced to a rule this change introduced or altered in
substance, so no skill text was corrected and no follow-up runs were made. Every material failure is recorded
as a finding below.

Correction: that held for the 183 matrix runs. The whole-change verification
and review that followed found F10, and the follow-up runs below found F11 and
F12, so skill text was corrected and 127 follow-up runs were made. See
[Follow-up runs](#follow-up-runs).

## Results by suite and host

`S/MF/I` means Supported / Material failure / Inconclusive, as originally
observed.

| Suite | claude (stage 1) | codex (stage 2) | agy (stage 2) |
| --- | --- | --- | --- |
| library | 9/0/0 | 7/2/0 | 9/0/0 |
| specs | 11/2/1 | 12/1/1 | 14/0/0 |
| requirements | 5/1/0 | 6/0/0 | 6/0/0 |
| plans | 11/1/0 | 11/1/0 | 12/0/0 |
| implementing-plans | 9/1/0 | 10/0/0 | 10/0/0 |
| subagent-execution | 7/3/0 | 8/2/0 | 8/2/0 |
| **Total** | **52/8/1** | **54/6/1** | **59/2/0** |

Totals as originally observed: 165/16/2 across the 183 matrix runs.

The 127 follow-up runs are not in this table; they are counted under
[Follow-up runs](#follow-up-runs).

Runs that were not Supported:

- claude: specs/2, specs/12 (MF); specs/11 (I); requirements/1 (MF); plans/3
  (MF); implementing-plans/9 (MF); subagent-execution/1, 2, 4 (MF).
- codex: library/4, library/8 (MF); specs/4 (MF); specs/9 (I); plans/10 (MF);
  subagent-execution/2, 4 (MF).
- agy: subagent-execution/5, 6 (MF).

## Findings ledger

Each finding lists every run that shows its behavior, so a run with two
failures appears under both. F1, F2, F3, and F4 recur findings of the
[2026-10-17 writeup](2026-10-17-library-retrofit.md) (its F7, F1, F10, and the
whole-change part of F10), and are cross-referenced by those ids. Run references name the host and the
case, for example claude specs/2 is
`stage1-claude/specs/claude/specs-2/`. States: Open, Resolved, Accepted.

| Id | Behavior | Where seen | Decision or change | Validation | Status |
| --- | --- | --- | --- | --- | --- |
| F1 | Reviewer, diagnosis, or whole-change dispatch below the skill's tier rule. Claude: reviewer on `haiku` for ordinary work (specs/2, specs/12, plans/3); task reviewers on the implementers' own tier and whole-change review not at the strongest tier (subagent-execution/1); whole-change review on `sonnet` while `opus` was available (subagent-execution/2). Codex: an authentication spec reviewed at medium effort, the same as ordinary cases (specs/4); whole-change review sent as a follow-up to the existing `gpt-6-sol` task reviewer (subagent-execution/4) | claude specs/2, specs/12, plans/3, subagent-execution/1, subagent-execution/2; codex specs/4, subagent-execution/4 | None in this changeset. Recurs F7 of 2026-10-17, whose note is "the tier wording predates the retrofit"; the tier sentences were not edited here | — | Open |
| F2 | Codex read document bodies in the same first shell call that loaded the skill, before any frontmatter filter. library/4 ran a body `rg` that printed the `docs/notes/ci-runners.md` decoy; library/8 printed both listed spec bodies including the type-less `legacy-export.md`. The selection and the answer were correct in both | codex library/4, library/8 | None. Recurs F1 of 2026-10-17, which Accepted it for codex library/4. Skill text cannot prevent a read issued before the subject has read the skill | — | Accepted: correct read set and answer, wrong order, driven by the call that bundles the skill read with repository reads |
| F3 | Scratch exclusion written to a new tracked `.gitignore` and committed as an extra revision outside the note's Result range, although `.git/info/exclude` existed. Codex and agy used `.git/info/exclude` in the same cases | claude implementing-plans/9, subagent-execution/4 | None in this changeset. Recurs F10 of 2026-10-17; the rule ("the active VCS's local exclusion mechanism") predates this change | — | Open |
| F4 | No whole-change review or verification arranged after the only task; the supervisor ran the test itself and wrote "Whole-change checks" from that run | claude subagent-execution/4 | None; the Finish contract predates this change. Recurs the whole-change part of F10 of 2026-10-17 | — | Open |
| F5 | Self-review of a material plan revision (task split) with no independent reviewer attempted and no stated unavailability; the sibling plans cases on the same host spawned reviewers | codex plans/10 | None; the reviewer-availability rule predates this change. The reviewer notes the harness does not record the tool inventory, so this would be Inconclusive if availability is treated as unknowable | — | Open |
| F6 | Diagnosis done inline although subagent dispatch was available, with no disclosure (6) or a disclosure that cited the no-capability exception (5) | agy subagent-execution/5, subagent-execution/6 | None. Both prompts are ambiguous about dispatch ("Prepare a fresh diagnostic assignment ... Return supported causes"), so whether the case should say "dispatch it" is an evaluation question, recorded below. Codex subagent-execution/5 and /8 and claude subagent-execution/8 also diagnosed inline and were assessed Supported with a judgment concern; agy subagent-execution/8 gave a grounded reason | — | Open |
| F7 | Requirements asked the user to say which of two meanings "excludes scheduled exports" has, although the request supplied it as a decision and said to start from the decisions. Borderline: the skill names "scope boundary" as a valid question, and the reviewer would downgrade to Supported with a judgment concern on a more generous reading | claude requirements/1 | None; subject judgment. Codex and agy passed the same case, and it passed on all hosts on 2026-08-31 | — | Open |
| F8 | Handoff note shape. The title kept "plan" ("Resume plan execution", where the rule maps a plan titled "Resume plan" to "Resume execution"): Material failure in claude subagent-execution/2 and codex subagent-execution/2; a judgment concern in claude implementing-plans/2, 8, 9 and subagent-execution/4. The Plan and Spec locators were written with a status, `@stable`, instead of a revision: claude subagent-execution/2, and implementing-plans/8 as a concern | claude subagent-execution/2, codex subagent-execution/2 (MF); claude implementing-plans/2, 8, 9, subagent-execution/4 (concerns) | None in this changeset. The rule is in `references/execution-state.md`. Its mapping (plan subject plus " execution") predates this change; this change (`pszoypnn`) reflowed the sentence into the new field list without changing the mapping, so compare against `xzqwoqyn`, the revision before this execution. The same title and locator errors occurred before the change. The 2026-10-16 artifacts show claude doing both before this change: titles "Sequence plan execution" and "Context plan execution" (`followup3-claude` subagent-execution-1 and -4) and an `@approved` locator (`stage1-claude` implementing-plans-8). Proposed: a one-line wording fix as a follow-up change | — | Open |
| F9 | The one scripted "Approved." reply cannot serve the Elevated-finding branch. In claude specs/11 it landed on an open Elevated question and the subject asked again, so the commit path was never exercised. In codex specs/9 the subject read it as both the answer and the approval and committed text the user had not seen. Agy gave a clean approval request in both cases, so the reply fit there | claude specs/11, codex specs/9 (I) | None; an evaluation defect, not a subject failure. Needs a case-design change: a reply that adapts to the question, a fixture that leaves no reviewable ambiguity, or a second scripted reply | — | Open |
| F10 | Frontmatter filters matched body lines. The whole-file `grep` filters matched example frontmatter inside document bodies. On this repository the status check reported `docs/specs/library-retrofit.md` (body line `status: approved`) as not yet migrated, and the `auth` and `status: draft` filters returned `docs/specs/okf-documents.md` from fenced examples. Found by the whole-change verification and review, not by any of the 183 runs, because no fixture had example frontmatter in a body | none of the 183 runs; whole-change verification and review | A frontmatter-only extractor (a `find -H` and `awk` command piped to `grep`) in the library and requirements skills, plus case `library/10`. Landed in `wmupovrm` (library skill, README, `library/10`, reference) and `outznpqn` (requirements) | `library/10` Supported on claude, codex, and agy in follow-up 1 and again in follow-up 5 | Resolved |
| F11 | Write rules unread by codex. Codex library/9 wrote `docs/reviews/<slug>.md` after the folder check listed another tool's reports (7 runs: 4 of 4 at `sha256:20a25d56…`, follow-up 1 once and follow-up 2 three times, and 3 of 3 at the intermediate `sha256:04e198e0…`, follow-up 4), and library/6 appended to the existing `docs/notes/onboarding.md` instead of creating a note (follow-up 3 once, follow-up 4 three times, committed in two). Cause: codex read `SKILL.md` with `sed -n '1,240p'` and often stopped there; all 7 library/9 failures read only lines 1 to 240 and all 4 passes (stage 2 and follow-up 3, three runs) read past 240, while the Write section began at line 248 (line 222 at `3412f167`) | codex library/9 (follow-up 1, follow-up 2 r1 to r3, follow-up 4 r1 to r3), codex library/6 (follow-up 3, follow-up 4 r1 to r3) | A self-contained Write folder check with a separate stop paragraph; `SKILL.md` cut to 239 lines by moving the Pin and compare commands to `references/pin-and-compare.md`, removing the spec example, and moving the construction notes to the README; the unit test `test_skill_files_fit_one_codex_read`, which requires every plugin `SKILL.md` within 240 lines; the spec revised. Landed in `wmupovrm` (the skill and the test) and `xknlouww` (the spec, moved into `docs/` by `lptmrtkx`) | Follow-up 5: codex 16 of 16 Supported, whole `SKILL.md` read in all 16, library/9 and library/6 passed 3 of 3 each; claude and agy passed library/9 in follow-ups 2, 3, and 4 | Resolved |
| F12 | Claude opens files the prompt lists as attached instead of filtering first. Library/5 opened the deprecated `design/specs/audit-retention-old.md` in 2 of 8 runs at the repaired texts: 1 of 4 at `sha256:20a25d56…` (follow-up 1 failed, follow-up 2 passed 3 of 3), 0 of 3 at the intermediate `sha256:31c0f715…` (follow-up 3, checked afterwards from the Read calls in the transcripts), and 1 of 1 at `sha256:8dc09ff1…` (follow-up 5); library/8 in follow-up 5 read the first lines of both attached files instead of filtering. Answers were correct. Cause: Find step 1, "When the task names a document or locator, read that file directly and skip discovery", is read as covering the prompt's attached-file list | claude library/5 (follow-up 1, follow-up 5), claude library/8 (follow-up 5) | None in this changeset. A sentence for step 1 was tried and withdrawn after review, because it would also stop an agent from reading a file a user attaches on purpose. The three follow-up 3 runs carried the withdrawn sentence and did not open the deprecated spec. Claude library/5 also passed 3 of 3 without it in follow-up 2, so these runs cannot separate the sentence's effect from run variance. Proposed: a net-zero-line rewording of step 1 in a later change | — | Open |
| F8 follow-up | The title rule in `references/execution-state.md` now reads "the plan's title without its trailing word `plan`, matched in any letter case (`plan`, `Plan`), followed by ` execution`". The original F8 row stays as observed; this row records the fix that landed afterwards, in `pszoypnn` | — | The title wording fix, landed in this changeset | None. The seven planned handoff-title reruns were dropped by the user's decision | Open: fix landed, not validated |

## Follow-up runs

After the matrix, the whole-change verification and review found F10, and 127
follow-up runs found F11 and F12 and validated the corrections. All 127 have a
`result.json` with status `captured`, and none had a runner error. Grading
used the run directories, with the transcript and the before and after
evidence, under `.agents/eval-results/2026-11-01-okf-documents/`. Run
directories are `followup<k>-<host>[-r<n>]/<suite>/<host>/<suite>-<n>/`. The
commands were those in the Matrix section with `--case <n>`, into the
`followup<k>-<host>` roots.

### Tested text

Commits were rewritten by later repairs and a fold, so each run set's skill
text is identified by SHA-256 (first 16 hex digits), computed on 2026-11-07
before this writeup was folded. Every `sha256:` value in this section and in
the ledger is a file checksum, not a revision, and `jj log` does not resolve
it. The commit column is the id as recorded during the runs; none of the
earlier ids is still on the branch.

| Runs | Commit | library `SKILL.md` | `references/pin-and-compare.md` | requirements `SKILL.md` |
| --- | --- | --- | --- | --- |
| `stage1-*` and `stage2-*` (183 runs) | `3412f167` | `sha256:4e002507d9613c46` | absent | `sha256:2738d69cbc4bc6c3` |
| `followup1-*` and `followup2-*` | `80be9372` | `sha256:20a25d5640b185de` | absent | `sha256:fc9a26fac4f745ca` |
| `followup3-*` | `ff4a77b5` | `sha256:31c0f7154475a937` | absent | `sha256:fc9a26fac4f745ca` |
| `followup4-*` | `b07a08d4` | `sha256:04e198e0e3aab8ab` | absent | `sha256:fc9a26fac4f745ca` |
| `followup5-*` | `560220bf` | `sha256:8dc09ff1eb449e07` | `sha256:100699bb29de10cc` | `sha256:fc9a26fac4f745ca` |

The shipped text equals the follow-up 5 text: `sha256sum` on the working copy
gives `sha256:8dc09ff1eb449e07` for `plugins/library/skills/library/SKILL.md`,
`sha256:100699bb29de10cc` for its `references/pin-and-compare.md`, and
`sha256:fc9a26fac4f745ca` for `plugins/planning/skills/requirements/SKILL.md`. The
follow-up 3 and 4 texts were intermediate and superseded.

### Run sets

| Run set | Cases | Text | Runs |
| --- | --- | --- | --- |
| `followup1-{claude,codex,agy}` | library 1 to 10 and requirements/4 | `sha256:20a25d56…` | 33 |
| `followup2-<host>-r1` to `r3` | library/9 on all hosts, library/5 on claude | `sha256:20a25d56…` | 12 |
| `followup3-*` | library suite on three hosts; claude 5 and 9 twice more; codex 9 twice more | `sha256:31c0f715…`, superseded | 36 |
| `followup4-*` | library 6 and 9: claude, agy, codex three times | `sha256:04e198e0…` | 10 |
| `followup5-*` | library suite on three hosts; codex 2, 6, and 9 twice more | `sha256:8dc09ff1…` | 36 |

That is 127 runs. `S/MF/I` below is Supported / Material failure /
Inconclusive, as above; a run assessed Supported with a judgment concern
counts as Supported and is named in the bullets.

| Run set | claude | codex | agy |
| --- | --- | --- | --- |
| follow-up 1 (11 each) | 10/1/0 | 10/1/0 | 11/0/0 |
| follow-up 5 (10 on claude and agy, 16 on codex) | 9/1/0 | 16/0/0 | 10/0/0 |

Follow-ups 2 to 4 have no suite table. Follow-up 2 graded library/9 from the
files written, in each run's `turn-01.evidence.json`, and claude library/5
from the transcripts' tool calls, which show whether `audit-retention-old.md`
was opened. Follow-up 3 ran the library suite but graded only library/6 and
library/9, from the evidence files. Follow-up 4 ran only library/6 and
library/9, graded from the evidence files.

- **Follow-up 1.**
  - agy: all 11 Supported.
  - codex: 10 Supported, with F2 recurrences (Accepted) in 6 of them
    (library/1, 4, 5, 7, 8, 10); library/9 Material failure, because it wrote
    `docs/reviews/<slug>.md` after the folder check listed another tool's
    reports, and it also showed an F2 recurrence.
  - claude: 10 Supported, two with judgment concerns (library/6, library/9);
    library/5 Material failure, because it opened the deprecated attached
    spec.
- **Follow-up 2.**
  - codex library/9 wrote into `docs/reviews` in 3 of 3 runs, so 4 of 4 with
    follow-up 1.
  - claude and agy library/9 wrote nothing and asked, 3 of 3 each.
  - claude library/5 filtered first and did not open the deprecated body in
    3 of 3, so it failed in 1 of 4 at this text.
- **Follow-up 3** (intermediate text; only library/6 and library/9 graded).
  - library/9 wrote nothing: codex 3 of 3, claude 3 of 3, agy 1 of 1.
  - library/6: claude and agy created a new note; codex appended to the
    existing `docs/notes/onboarding.md`, 1 of 1.
- **Follow-up 4** (intermediate text).
  - claude and agy passed library/6 and library/9.
  - codex library/9 wrote `docs/reviews/ci-setup.md` in 3 of 3.
  - codex library/6 appended to `docs/notes/onboarding.md` in 3 of 3 and
    committed it in 2.
- **Root cause.** Codex read `SKILL.md` with `sed -n '1,240p'` and often
  stopped. All 7 codex library/9 failures (follow-up 1, follow-up 2 three
  times, follow-up 4 three times) read only lines 1 to 240; all 4 passes
  (stage 2 and follow-up 3 three times) read past line 240. The Write section
  began at line 248; it was at line 222 at `3412f167`. See F11.
- **Follow-up 5** (final text).
  - codex: 16 of 16 Supported, with F2 recurrences (Accepted). It read the
    whole `SKILL.md` in all 16 runs and `pin-and-compare.md` in 3 of 3
    library/2 runs; library/9 and library/6 passed 3 of 3 each.
  - agy: 10 of 10 Supported, with judgment notes on library/6 and library/9.
  - claude: 9 Supported, two with judgment concerns (library/6, library/8);
    library/5 Material failure, because it opened the deprecated attached
    spec. Library/8 read the first lines of both attached files instead of
    filtering. Library/6 was assessed a judgment concern because the Write
    folder check did not run.
  - Disposition of claude library/6, separate from the observation above: the
    folder check applies only to the first document of a type, and
    `docs/notes` already holds a note, so the skipped check is consistent with
    the skill and not a failure.

### Corrections and where they landed

By change id, which survives the folds that rewrote commit ids; each resolves
with `jj log -r <id>`.

| Change | Holds |
| --- | --- |
| `wmupovrm` | library skill, README, `library/10`, `references/pin-and-compare.md`, and `test_skill_files_fit_one_codex_read` (F10, F11) |
| `outznpqn` | requirements skill (F10) |
| `pszoypnn` | execution-state title rule (F8 follow-up) |
| `xknlouww` | the final approved spec, which `lptmrtkx` moves to `docs/specs/` (F11) |

## What held

Every behavior this change introduced passed on every host that reached it.
The two exceptions are the approval branch of claude specs/11 and codex
specs/9, recorded under F9: claude's was not exercised, and codex's wrote
correct mechanics (stable, `verified`, one-file commit) but on an ambiguous
approval.

- Current-document selection by OKF status: a `draft` or `deprecated`
  document, and a draft's `supersedes`, did not retire or replace the stable
  document (library/1, library/4, library/8, requirements/4).
- Folder resolution from `AGENTS.md`: `design/specs/` for Find and for draft
  placement, nothing written under `docs/specs/` (library/5, specs/12).
- Writing a note uncommitted, with `type: note` and no `status` or `verified`
  (library/6).
- Opening the copied OKF spec for an index question (library/7).
- The not-yet-migrated report: `legacy-export.md` named and excluded, its
  figure unused (library/8). Codex library/8 conveyed it in substance without
  the phrase.
- The folder-clash question: the subject asked where review documents should
  go and wrote nothing (library/9).
- Approval writes `verified: { by: human:Eval Reviewer, at: <UTC> }` after
  `status: stable`, commits only the document, and runs the recording check
  (specs/6, 7, 8, 9, 11, 13, 14; plans/7 to 10, 12). The approver came from
  `jj config get user.name`. A refused commit left the file in place and was
  reported uncommitted (specs/8, plans/9).
- A replacement deprecates its target in the same commit (specs/13, plans/12).
- Re-approval committed only the spec when the target was already deprecated
  (specs/14).
- Revision returned the document to `draft` with `verified` removed (specs/11
  turn 1 on all hosts, plans/10 turn 1).
- Refusal of a `draft` spec (plans/11), a `draft` plan (implementing-plans/10),
  and a `deprecated` plan (subagent-execution/10).
- Handoff notes at `docs/handoffs/<execution-id>.md` with `type: handoff`
  frontmatter, recorded as their own revision before scratch removal
  (implementing-plans/2, 8, 9; subagent-execution/1, 2, 4), with a failed
  recording leaving the note in place and scratch retained
  (subagent-execution/9).

## Operational notes

- In Antigravity runs the subject's first sandboxed shell command failed with
  `fork/exec /usr/local/bin/agy: operation not permitted`, and the subject
  recovered by retrying with `BypassSandbox`. This is operational, not a
  subject failure; the 2026-10-17 writeup recorded the same thing.
- In Codex implementing-plans cases 2, 3, 4, 8, and 9 the sandbox rejected
  `rm` commands (`turn-01.stderr.txt`); the subjects switched to `unlink` and
  `rmdir`.
- No runs errored or needed a rerun.
- Minor deviations that changed no assessment: read-only `git` commands from
  agy and claude subjects despite the prompt's "use jj, not Git"; agy
  subagent-execution/4 truncated `.git/info/exclude` while probing; codex
  subagent-execution/1 let an implementer record its scratch report in
  history and cleaned it up with an extra revision; several runs left a
  stray `__pycache__` in the working copy.

## Evaluation issues

Case and harness problems the reviewers found, separate from subject behavior.

- specs/9 and specs/11: one scripted "Approved." reply assumes a review with
  no Elevated finding (F9).
- agy subagent-execution/5 and /6 and codex /5 and /8: the prompts do not say
  a fresh-investigator dispatch is wanted, while the author guidance expects one
  (F6). The reviewers differ on whether "return" means the assignment or the
  findings.
- The harness records no model inventory and no reviewer or implementer brief
  text. `provider_trace` is empty for every claude turn (66 of 66) and
  non-empty for every agy turn; for codex it is non-empty only in runs that
  dispatched agents (17 of 66 turns), where it records the spawn `model` and
  `reasoning_effort` and the returned review text, not the input brief.
  Tier-ladder questions (F1) rest on the claude `Agent` call and those spawn
  arguments, and "task-only context" is unobservable. The Codex subjects chose
  ids (`gpt-6-sol`, `gpt-6-luna`) that `plugins/planning/README.md` does not
  list (it lists `gpt-6-astra`), and agy exposes only `flash`,
  `pro`, `flash_lite`, and `inherit`.
- The reviewer-tier author question is applied unevenly: claude specs/12 has
  none, and several questions assume a strongest-tier subject, which none of
  the three is.
- implementing-plans 2, 3, 5, 6, and 7 pre-seed `.git/info/exclude`, so the
  exclude-before-create gate is unobserved there; subagent-execution/4's
  attached-file list omits the exclusion file, unlike cases 1 to 3.
- The commit-policy rejection in plans/9, specs/8, and subagent-execution/9
  exists only in the prompt, and the subagent-execution/9 fixture note carries
  literal placeholders (`<revision described "eval fixture">`) in its Plan,
  Spec, and Start lines. subagent-execution/2 and /9 use synthetic
  single-revision ranges.
- requirements/3: the request's "but" supports a reading with no
  contradiction, so the case's expectation assumes one branch.
- The `evidence.json` diff is cumulative from the baseline, so it lists
  uncommitted working-copy files beside a commit (plans/8).
