---
name: implementing-plans
description: Use when an approved, preserved implementation plan is authorized for execution, either as one delegated task brief or inline across the whole plan.
---

# Implementing Plans

Execution needs an approved, preserved plan, the spec it implements, and
execution authorization. A plan alone is not authorization. If those inputs are
missing, route an approved spec through `plans` or request the missing context;
do not begin implementation. The spec remains authoritative when it conflicts
with a plan.

Choose the entry context before acting.

## Delegated worker: one task brief

Use this path only for one assigned, approved task brief containing the exact
plan/spec context needed for that task. Read
[the implementation report contract](references/implementation-report.md).

1. Inspect the assigned paths and the relevant repository conventions. Change
   only the task scope; preserve unrelated working-copy changes.
2. Invoke [verifying-changes](../verifying-changes/SKILL.md) on the actual task
   change before recording it. Failed, stale, or unavailable required evidence
   is not completion: correct the task when authorized, or report the gap.
3. Record only the verified assigned change through the active VCS workflow.
   Identify its exact revision or revision range. A recording failure leaves the
   task incomplete even if verification passed.
4. Write and return the implementation report. Return to the supervisor for
   review and steering.

Do not dispatch workers or reviewers, edit supervisor execution state, approve
your work, adjudicate findings, or perform whole-plan completion.

## Inline primary: whole plan

Use this path only when executing the whole approved plan. Read
[execution state](references/execution-state.md) and the implementation report
contract before coordination.

When delegation is available and the user has not requested inline work, read
[subagent-execution](../subagent-execution/SKILL.md) and supervise its one-task
sequence. The primary coordinates reports, review, dispositions, recovery, and
whole-change checks; it does not implement delegated task changes. Use the
remaining inline procedure only when delegation is unavailable or inline work
was explicitly requested.

Before creating plan-associated scratch, add its exact execution directory to
the active VCS's local exclusion mechanism. Use one directory per workspace and
exact plan version, normally `.agents/execution/<execution-id>/`. Preserve any
uncommitted Library database change as a separately pending preservation change;
never put it in an implementation recording.

Initialize or restore execution state from the exact approved plan/spec content
and locators. For archived artifacts, use available `read-archive` capability
to select and verify that exact content before task work; do not send workers
broad archive exploration. On resumption, reconcile recorded task revisions,
evidence, and findings with repository state before repeating or dispatching
work. A status checkbox without a matching revision/evidence is not proof of
completion.

For each task, make the scoped change, invoke
[verifying-changes](../verifying-changes/SKILL.md) before recording, record the
verified logical change, and retain its report and evidence location in state.
Arrange an independent task review when available using
[reviewing-implementation](../reviewing-implementation/SKILL.md), read its
usable returned contract result, and only then assign findings. If independent
review is unavailable or returns no usable result, perform and disclose
self-review using the same contract. The primary agent assigns every material
finding `Addressed`, `Elevated`, or `Dismissed` with evidence; review fixes are
separately verified, recorded, and fix-reviewed.

Stop affected work and obtain an approved revision plus explicit user approval
when a change is material to approved scope or approach. Tactical details
consistent with the approved artifacts may be decided and recorded in state.

After all tasks and fix reviews, review and verify the assembled change set.
Final handoff identifies the plan/spec, starting revision and resulting change
set, task and whole-change evidence, review outcomes/dispositions, limitations,
and separately pending preservation. Do not claim readiness if required checks
remain unavailable, stale, or failed. Do not push, create a PR/MR, merge, or
deploy.

Clean up only this execution's scratch after successful completion and after
material outcomes are preserved or surfaced. Keep scratch for incomplete,
blocked, awaiting-decision, failed-recording, or cleanup-failure states.
