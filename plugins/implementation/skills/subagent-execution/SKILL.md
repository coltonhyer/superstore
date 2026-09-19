---
name: subagent-execution
description: Use when a primary agent is executing an approved implementation plan with available delegated implementers or needs evidence-based recovery from stalled delegated work.
---

# Subagent Execution

The supervisor coordinates one approved task at a time. It does not implement,
review its own task work, publish, merge, or turn a report into completion.

Before coordination, confirm the preserved approved plan, authoritative spec,
and execution authorization. Read [the execution state](../implementing-plans/references/execution-state.md),
[implementation report contract](../implementing-plans/references/implementation-report.md),
[implementer brief](references/implementer-brief.md), and, when diagnosis is
justified, [diagnostic assignment](references/diagnostic-assignment.md). At
review and verification gates, load [reviewing-implementation](../reviewing-implementation/SKILL.md)
and [verifying-changes](../verifying-changes/SKILL.md), respectively.

## Dispatch

Before creating execution scratch, add its exact directory to the local VCS
exclusion. Establish the starting revision and separate pre-existing
working-copy changes, including any pending Library preservation. That database
change remains outside task ranges and the final recording gate. On resumption,
reconcile every recorded revision, report, evidence location, and finding with
repository state; do not repeat a completed task solely because session context
was lost.

When delegation is available and inline work was not requested, dispatch one
fresh implementer with only the assigned task, exact applicable plan/spec
excerpts, required interfaces and earlier decisions, workspace, report path,
and the implementing-plans instructions. Do not require a new worker worktree
unless repository instructions require it. Keep unrelated history, the whole
plan, and supervisor state out of the worker context. Do not fork or share your
conversation with any worker or reviewer, even when the host offers to;
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

Read the returned report and inspect the full recorded task range and cited
evidence. Then dispatch `reviewing-implementation` for that exact range. Read
the actual returned review before assigning findings. Send required corrections
and fix verification back to an implementer; do not edit the task yourself.
Only move to the next task after current verification and every material finding
or verification gap is resolved. Record evidence-based dispositions in
execution state; a report or review alone never establishes completion.

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
An inconclusive diagnosis does not authorize a blind retry or a scope change.

## Finish

After all tasks, arrange whole-change review and verification against the
approved spec. Readiness requires covered approved requirements, resolved
material findings, final-applicable evidence, recorded intended changes, and no
unresolved conflict. Before cleanup, incorporate every approved material
plan/spec decision into its preserved authoritative artifact and retain any
lasting diagnostic or report outside scratch. Hand off the plan/spec, start and
resulting ranges, evidence, review outcomes and dispositions, limitations, and
any separately pending preservation change. Remove only this execution's scratch
after those preservation and handoff gates succeed; retain it for incomplete,
blocked, or awaiting-decision work.
