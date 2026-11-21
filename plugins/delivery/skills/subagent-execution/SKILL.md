---
name: subagent-execution
description: Use when a primary agent is executing an approved implementation plan with available delegated implementers or needs evidence-based recovery from stalled delegated work.
---

# Subagent Execution

The supervisor coordinates one approved task at a time. It does not implement,
review its own task work, publish, merge, or turn a report into completion.

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

Before coordination, confirm a **committed and clean** repository plan carrying
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

Read [the execution state](../implementing-plans/references/execution-state.md),
[implementation report contract](../implementing-plans/references/implementation-report.md),
[implementer brief](references/implementer-brief.md),
[the shared review loop](../../references/review-loop.md), and, when diagnosis
is justified, [diagnostic assignment](references/diagnostic-assignment.md). Load
[the OKF commit reference](../../references/okf-commit.md) when computing
committed 12-character Git blob hashes via step 5 and when running the two-step
mechanical blob-citation refresh on in-place revisions before merge. At review
and verification gates, load
[reviewing-implementation](../reviewing-implementation/SKILL.md) and
[verifying-changes](../verifying-changes/SKILL.md), respectively.

## Dispatch

Before creating execution scratch (normally `.agents/execution/<run-id>/`),
add its exact directory to the local VCS exclusion. Initialize or restore
execution state from the committed, clean plan and spec files, pinning
repository artifacts as `<path>, blob <12-char hash>` via step 5 of
[the OKF commit reference](../../references/okf-commit.md) and carrying over any
prior-stage `Decisions for review` and `Tactical decisions`. Establish the
starting revision (for local recovery and whole-change diff verification) and
separate pre-existing working-copy changes. On resumption, reconcile every
recorded revision, report, evidence location, and finding with repository state;
do not repeat a completed task solely because session context was lost.

When subagent creation is available and inline work was not requested, dispatch
one fresh implementer with only the assigned task, exact applicable committed
plan/spec excerpts, required interfaces and earlier decisions, workspace,
report path, and the
[implementing-plans](../implementing-plans/SKILL.md) instructions. Do not
require a new worker worktree unless repository instructions require it. Keep
unrelated history, the whole plan, and supervisor state out of the worker
context. Do not fork or share your conversation with any worker or reviewer
(`fork_turns: "none"` where supported), even when the host offers to;
everything it needs goes in its brief.

Set model and reasoning effort explicitly on every dispatch when the host
exposes those controls; omitting them inherits yours, which is usually the
costliest option. Work that a stronger agent will check can run cheaper than
its check. A small mechanical change goes to the smallest model at low effort.
Ordinary implementation from a complete brief, a repair for a named finding,
and a verification run go to a mid-tier model. Each task review runs one tier
above the work it checks and no higher, or at the strongest tier when the work
already ran there. Keep the strongest available tier for diagnosis,
whole-change review, and work where a defect is costly to reverse, such as
authentication, secrets, cryptography, data migration, or public contracts. A
routine role or permission check is ordinary work. When replacing a worker
after a repeated unresolved defect, raise its tier or effort when a higher one
is available rather than repeating the same level; at the ceiling, follow
Recovery instead of retrying. This skill names no models; choose from those the
host lists.

Authorize a pre-existing defect fix only when it blocks the task or is
explicitly authorized (following scope-fit rules in
[the shared review loop](../../references/review-loop.md), and obtaining explicit
user intent — or conservative autonomous resolution under `Decisions for review`
per [the autonomous mode reference](../../references/autonomous-mode.md) — for
any observable behavior change). Ensure any incidental fix lands in its own
separate commit (never bundled with task commits; implementation review verifies
commit separation) and record it distinctly for `## Incidental fixes`.

Read the returned report and inspect the full recorded task range and cited
evidence. Then dispatch
[reviewing-implementation](../reviewing-implementation/SKILL.md) with fresh
context (`fork_turns: "none"` where supported) for that exact range per
[the shared review loop](../../references/review-loop.md) (bounded 3-round loop
plus step-back final round; wait for a running reviewer and require `usable`
output). Follow
[the shared review loop](../../references/review-loop.md) reviewer-failure
fallbacks: in interactive mode, fall back once per gate to disclosed
self-review for a failed or unusable reviewer without retrying the failed
dispatch (halting if fallback or a later round fails); in explicitly authorized
autonomous mode, halt immediately when an independent reviewer is unavailable,
fails, or returns unusable output — never fall back to self-review, retain
scratch, and emit each accumulated `Decisions for review` entry in full
(`Question`, `Options considered`, `Chosen option`, `Reason`, `Evidence`). Assign every finding
one disposition in conversation or execution state/report (never inside specs
or plans): `Addressed` (fixing every instance of the defect class; optional
`Non-blocking` code edits require fresh verification and recording), `Elevated`
(blocking interactive approval until answered, or resolved conservatively under
`Decisions for review` in autonomous mode — never marked human-approved),
`Dismissed` with exact checkable evidence, or `Declined` for `Non-blocking`
only. Send required corrections and fix verification back to an implementer; do
not edit the task yourself. Only move to the next task after current
verification and every material finding or verification gap is resolved.

## Recovery

Supply missing task context directly before diagnosing. A repeated unresolved
defect, contradictory evidence, or plan/code conflict can justify a fresh
diagnostic assignment. If an applicable Debugging skill is in the active
inventory, include it; otherwise the diagnostic agent uses judgment under the
same assignment. Do not add a fallback debugging procedure.

Without subagent capability, the inline agent performs the diagnostic assignment
and discloses that no fresh investigator was available. That exception does not
turn diagnosis into implementation or authorize a scope change.

Use supported causes, uncertainty, conflicts, and the proposed correction/check
to steer the current implementer, replace it, or raise a consequential decision.
An inconclusive diagnosis does not authorize a blind retry or a scope change. If
a review gate still fails to finish clean after the step-back final round, halt
and escalate rather than advancing, retaining scratch and emitting each
accumulated `Decisions for review` entry in full (all five fields) in autonomous
mode.

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
spec or plan is revised in place before merge.

## Finish

After all tasks, arrange whole-change review
([reviewing-implementation](../reviewing-implementation/SKILL.md)) and
verification ([verifying-changes](../verifying-changes/SKILL.md)) against the
approved spec(s) per [the shared review loop](../../references/review-loop.md).
Readiness requires covered approved requirements, resolved material findings,
final-applicable evidence, recorded intended changes, and no unresolved
conflict. Do not push, create a PR/MR, merge, or deploy.

Retain any lasting diagnostic or report outside scratch, for example in the
handoff note's `## Limitations` or `## Tactical decisions` sections.

After whole-change checks pass, write the handoff note at
`<handoffs folder>/<plan-slug>.md` (resolving the folder and appending `-2`,
`-3`, ... if a prior handoff for that slug exists per
[the execution state](../implementing-plans/references/execution-state.md)) in
the shape the execution state gives — citing the committed plan and every
implemented repository spec by `<path>, blob <12-char hash>` (omitting blob
hashes for non-repository docs), a `Change` line (no commit hashes, Jujutsu
change IDs, revision ranges, or scratch paths), whole-change checks, review
outcomes by finding ID and disposition, `## Incidental fixes`,
`## Limitations`, `## Decisions for review`, and `## Tactical decisions` (writing
`none` when empty). Record the handoff note as its own separate revision
through the active VCS workflow, applying
[implementing-plans](../implementing-plans/SKILL.md)'s recording check to the
note's path (`jj diff -r @ <path>` empty and `jj log -r @- <path>` showing
the new revision; or Git equivalents). Remove only this execution's scratch
after the note is recorded. If recording the
note fails, leave the note in place, report the failure (emitting each
accumulated `Decisions for review` entry in full (all five fields) in
autonomous mode), retain scratch, and do not claim completion; also retain
scratch (and emit each accumulated `Decisions for review` entry in full (all
five fields) in autonomous mode) for incomplete, blocked,
failed-recording, verification-failure, unconverged-gate, awaiting-decision,
note-recording-failure, or cleanup-failure states.
