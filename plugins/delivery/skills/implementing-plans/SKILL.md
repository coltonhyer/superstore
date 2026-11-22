---
name: implementing-plans
description: Use when an approved, preserved implementation plan is authorized for execution, either as one delegated task brief or inline across the whole plan.
---

# Implementing Plans

Interactive human approval and separate execution authorization are strictly
the default; ordinary multi-stage prompts (*"implement this ticket
end-to-end"*, *"take this spec to code"*, *"preserve"*, *"save"*, *"commit"*)
never waive interactive approval or authorize execution. Preserve approval and
execution choices already supplied by the user. Load
[the autonomous mode reference](../../references/autonomous-mode.md) when
explicitly authorized unattended execution applies (where upfront autonomous
opt-in authorizes execution once the plan passes clean independent review and
commits).

A repository document is **committed and clean** only when: with Jujutsu,
`jj diff -r @ <path>` prints nothing and `jj file list -r @- <path>` prints
`<path>`; with Git, `git status --porcelain <path>` prints nothing and
`git ls-tree --name-only HEAD -- <path>` prints `<path>` (never use
`jj log -r @- <path>` for readiness checks).

Whole-plan execution requires a **committed and clean** repository plan carrying
`status: stable` (a plan whose `status` is `draft` or `deprecated`, that has no
`status` line, or that is uncommitted or dirty is not execution-ready — route
it back through `plans`; non-repository plans require explicit user approval and
execution authorization and omit blob hashes) AND every repository spec named in
`implements` (scalar `<path>` or inline list `[path-a, path-b]`) **committed and
clean**, carrying `status: stable` OR explicitly approved when supplied without
a `status` line or without `type: spec` frontmatter (rejecting `draft` or
`deprecated` specs). An uncommitted or dirty repository plan or spec is not
execution-ready and routes back through `plans` (or `specs`); non-repository
specs omit blob hashes. In interactive mode, if the `status: stable` plan or
any implemented `status: stable` spec carries `verified` only from a
non-`human:` actor (e.g., `process:delivery-autonomous`), flag it and route
confirmation through `plans` or `specs` per
[the autonomous mode reference](../../references/autonomous-mode.md) before
executing; a `status: stable` plan or spec with no `verified` line (such as a
migrated historical doc or one approved without a valid VCS `user.name`) is
**not** treated as non-`human:` machine-confirmed. If required inputs or
authorization are missing, route through `plans` (or `specs`) or request the
missing context; do not begin implementation. The spec remains authoritative
when it conflicts with a plan.

Load [the OKF commit reference](../../references/okf-commit.md) when computing
committed 12-character Git blob hashes via step 5 and when running the two-step
mechanical blob-citation refresh on in-place revisions before merge.

Choose the entry context before acting.

## Delegated worker: one task brief

Use this path only for one assigned, approved task brief containing the exact
authorized plan/spec context needed for that task. Read
[the implementation report contract](references/implementation-report.md).

1. Inspect the assigned paths and the relevant repository conventions. Change
   only the task scope; preserve unrelated working-copy changes. Work strictly
   from the brief: do not open the full plan, other tasks, or execution state.
   If the brief lacks something the task needs, report the gap instead. Fix a
   pre-existing defect only when it blocks the task or is explicitly authorized
   in the brief; because a delegated worker cannot obtain user intent or record
   autonomous `Decisions for review` itself, stop and report `blocked` whenever
   a blocking pre-existing fix would change observable behavior without explicit
   authorization. Land any incidental fix in its own separate commit (never
   bundled with task commits) and call it out separately in the implementation
   report.
2. Invoke [verifying-changes](../verifying-changes/SKILL.md) on the actual task
   change before recording it. Failed, stale, or unavailable required evidence
   is not completion: correct the task when authorized, or report the gap.
3. Record only the verified assigned change through the active VCS workflow
   (keeping any incidental fix in its own commit), and apply the
   recording check below before claiming completion. A recording failure leaves
   the task incomplete even if verification passed.
4. Write and return the implementation report. Return to the supervisor for
   review and steering.

Do not dispatch workers or reviewers, edit supervisor execution state, approve
your work, adjudicate findings, or perform whole-plan completion.

## Recording check

Describing the working-copy change is not a recording. With Jujutsu,
`jj commit -m '<message>' <paths>` moves the change into a finished revision;
confirm that `jj diff -r @ <paths>` prints nothing and `jj log -r @- <paths>`
shows a revision newer than the one you started from (this covers creations,
edits, and deletions; readiness checks on pre-existing plans and specs use
`jj diff -r @ <path>` and `jj file list -r @- <path>` instead). With Git,
`git add <paths> && git commit -m '<message>' <paths>`; confirm that
`git status --porcelain <paths>` prints nothing and `git log -1 -- <paths>`
shows the new commit. Claim a recording only when the active-VCS checks hold.
The same check applies to the handoff note and any incidental fix commit.

## Inline primary: whole plan

Use this path only when executing the whole approved plan. Read
[execution state](references/execution-state.md),
[the implementation report contract](references/implementation-report.md), and
[the shared review loop](../../references/review-loop.md) before coordination.

When subagent creation is available and the user has not requested inline work,
read [subagent-execution](../subagent-execution/SKILL.md) and supervise its
one-task sequence. The primary coordinates reports, review, dispositions,
recovery, and whole-change checks; it does not implement delegated task changes.
Use the remaining inline procedure only when subagent creation is unavailable
or inline work was explicitly requested.

Before creating plan-associated scratch, add its exact execution directory to
the active VCS's local exclusion mechanism. Use one directory per workspace and
plan version, normally `.agents/execution/<run-id>/` (`<run-id>` may use a run
or revision identifier; committed handoff notes carry no revision identifier).

Initialize or restore execution state from the committed, clean plan and spec
files (never bypass dirty repository files via `@revision` — dirty plans or
specs are refused at the execution gate), pinning repository artifacts as
`<path>, blob <12-char hash>` via step 5 of
[the OKF commit reference](../../references/okf-commit.md) and carrying over any
prior-stage `Decisions for review` and `Tactical decisions`. Do not send
workers broad exploration of the repository's documents. On resumption,
reconcile recorded task revisions, evidence, and findings with repository state
before repeating or dispatching work; a status checkbox without matching
revision and evidence is not proof of completion.

For each task, make the scoped change, invoke
[verifying-changes](../verifying-changes/SKILL.md) before recording, record the
verified logical change, and retain its report and evidence location in state.
Fix a pre-existing defect only when it blocks the task or is explicitly
authorized (following scope-fit rules in
[the shared review loop](../../references/review-loop.md), and requiring
explicit user intent — or conservative autonomous resolution recorded under
`Decisions for review` per
[the autonomous mode reference](../../references/autonomous-mode.md) — for any
observable behavior change); land any incidental fix in its own separate commit
(never tangled with task commits) and record it distinctly for the handoff's
`## Incidental fixes` section.

Arrange an independent task review using
[reviewing-implementation](../reviewing-implementation/SKILL.md) (when subagent
creation is available) with fresh context (`fork_turns: "none"` where supported)
per [the shared review loop](../../references/review-loop.md) (bounded 3-round
loop plus step-back final round; wait for a running reviewer and require
`usable` output). Follow
[the shared review loop](../../references/review-loop.md) reviewer-failure
fallbacks: in interactive mode, use disclosed self-review across rounds when
subagent creation is unavailable, or once per gate per missing role without
retrying a failed dispatch when subagent creation is available (halting if
fallback or a later round fails); in explicitly authorized autonomous mode, halt
immediately when an independent reviewer is unavailable, fails, or returns
unusable output — never fall back to self-review, retain scratch, and emit each
accumulated `Decisions for review` entry in full (`Question`, `Options considered`,
`Chosen option`, `Reason`, `Evidence`). Assign every finding one disposition in
conversation or execution state/report (never inside specs or plans):
`Addressed` (fixing every instance of the defect class; optional `Non-blocking`
code edits still require fresh verification and recording), `Elevated` (blocking
interactive approval until answered, or resolved conservatively under
`Decisions for review` in autonomous mode — never marked human-approved),
`Dismissed` with exact checkable evidence, or `Declined` for `Non-blocking`
only. Review fixes are separately verified, recorded, and fix-reviewed.

When a material revision to the plan or an implemented spec is needed after
execution starts, pause affected work and revise the authoritative document in
place (`specs` or `plans`): in interactive mode, obtain required review (when
material) and explicit user re-approval before committing; in explicitly
authorized autonomous mode, pause affected work while revising in place and
resume only after the revised document passes its clean independent review
round and commits per
[the OKF commit reference](../../references/okf-commit.md). Refresh cited
12-character Git blob hashes via the two-step mechanical refresh in
[the OKF commit reference](../../references/okf-commit.md) whenever any cited
spec or plan is revised in place before merge. Record tactical choices under
`Tactical decisions` and autonomous intent or scope choices under
`Decisions for review`.

After all tasks and fix reviews, run whole-change verification
([verifying-changes](../verifying-changes/SKILL.md)) and whole-change review
([reviewing-implementation](../reviewing-implementation/SKILL.md)) per
[the shared review loop](../../references/review-loop.md). Do not claim
readiness if required checks remain unavailable, stale, or failed, or if any
`Blocking` finding remains unresolved after the final round (halt progression,
retain scratch, and emit each accumulated `Decisions for review` entry in full
(all five fields) in autonomous mode). Do not push, create a PR/MR, merge, or deploy.

After whole-change checks pass, write the handoff note at
`<notes/handoffs folder>/<handoff-slug>.md` (`<plan-slug>-handoff.md` when
`<plan-slug>` starts with `YYYY-MM-DD-`, or `YYYY-MM-DD-<plan-slug>-handoff.md`
when undated, resolving the folder — default `docs/notes/` — and appending `-2`,
`-3`, ... on collision per [execution state](references/execution-state.md)),
citing the committed plan and every implemented repository spec by
`<path>, blob <12-char hash>` (omitting blob hashes for non-repository docs), a `Change` line (no commit hashes,
Jujutsu change IDs, revision ranges, or scratch paths), whole-change checks,
review outcomes by finding ID and disposition, `## Incidental fixes`,
`## Limitations`, `## Decisions for review`, and `## Tactical decisions` (writing
`none` when empty). Record the handoff note as its own separate revision
through the active VCS workflow and apply the recording check to the note's
path. If recording the note fails, leave the note in place, report the failure
(emitting each accumulated `Decisions for review` entry in full (all five
fields) in autonomous mode), retain scratch, and do not claim completion. Clean
up only this execution's scratch after the handoff note is recorded; retain
scratch (and emit each accumulated `Decisions for review` entry in full (all
five fields) in autonomous mode) for incomplete, blocked,
awaiting-decision, failed-recording, verification-failure, unconverged-gate,
note-recording-failure, or cleanup-failure states.
