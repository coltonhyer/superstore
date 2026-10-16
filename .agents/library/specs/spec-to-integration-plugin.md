---
title: Spec-to-Integration Plugin
status: approved
topics: [agent-skills, marketplace, implementation-planning, code-review, verification]
---

# Spec-to-Integration Plugin

## Summary

Add a marketplace plugin that takes an approved specification through an
approved implementation plan, implementation, review, and verification. It
ends with recorded local changes ready for a human to request an MR.

The plugin has five public skills: `plans`, `implementing-plans`,
`subagent-execution`, `reviewing-implementation`, and `verifying-changes`.
The marketplace name remains deliberately deferred; this document's title is
a descriptive label, not a naming decision.

## Context and motivation

The existing Planning plugin owns requirements gathering and specification
creation. Its terminal artifact is an approved, preserved spec. The next
plugin must tell an agent what to do with that artifact without recreating
Planning or assuming Superpowers is installed.

Plans provide stable task definitions for isolated implementers. Execution
progress must survive context loss without changing the approved plan.
Verification establishes what the changes actually do; independent review
examines whether the implementation and its tests satisfy the intended work.

## Goals and non-goals

### Goals

- Produce a written, proportionally sized plan for every implementation.
- Make tasks extractable with enough context for an isolated implementer.
- Support sequential delegation by default and complete inline execution.
- Separate implementation, coordination, review, and verification duties.
- Recover from stalled attempts using evidence and explicit adjudication.
- Preserve approved design artifacts while keeping execution scratch temporary.
- Follow repository conventions and work across the marketplace's supported
  hosts: Codex, Claude Code, and Antigravity.

### Non-goals

- Requirements elicitation or specification authorship, which remain Planning's
  responsibility.
- Push, MR/PR creation, merge, deployment, or a branch-finishing menu.
- Parallel implementation or integration between worker workspaces.
- A second debugging methodology or a required Debugging installation.
- Hooks, always-on rules, dedicated agent definitions, a workflow engine,
  or separate committing and finishing skills in the initial version.
- Mandatory test-first ordering, coverage percentages, or fixed plan lengths.
- A permanent execution ledger or mandatory completion document.

## Requirements and expected behavior

### Entry, routing, and authority

`plans` consumes an approved spec. Execution consumes an approved, preserved
plan and the spec it implements. Preserve any approval and execution choices
already supplied by the user; file existence alone is not evidence of approval.
An execution request supplied with only an approved spec routes through
`plans`, including its approval and preservation gates, before implementation.
If an approved spec is missing, use Planning when available or request that
input; do not invent approval or begin implementation.

The spec owns requirements, rationale, and acceptance criteria. The plan owns
implementation approach, task boundaries, ordering, dependencies, relevant
files and patterns, and task completion checks. Tasks refer to the spec rather
than maintaining another copy of its requirements. A task brief may include
exact spec excerpts to give an isolated worker the context it needs.

Plan creation alone does not authorize execution. After preservation, report
the plan's exact locator and either hand it back or continue an execution
request the user already authorized. Preservation failures stop that handoff.

Material changes to approved scope or approach require revision and explicit
user approval before affected work proceeds. A supervisor can resolve tactical
details consistent with the approved artifacts and record the decision in
execution progress. A conflicting plan instruction never overrides the spec.

### `plans`

Inspect relevant repository behavior and conventions before drafting. Write
under `docs/plans` unless the repository or user specifies another location.
Follow established naming and document conventions; otherwise use a
descriptive slug. Small changes may have one short task; no implementation
skips the written plan because it is small.

Each plan identifies the approved spec by its exact repository or archive
locator, describes the overall approach, and assigns stable task identifiers.
Each task contains:

- The intended deliverable and referenced spec sections or requirements.
- Prerequisites and ordering, including interfaces supplied by earlier tasks.
- Relevant files, existing patterns, and implementation constraints.
- A concrete completion check, with commands where the repository makes them
  known and the behavior or result the check must establish.

Do not prescribe complete implementation code or manufacture tasks merely to
fill a template. One plan describes one independently integrable change. If a
spec cannot fit a coherent, reasonably sized plan, recommend separate plans
whose deliverables can each be developed, reviewed, verified, and integrated
independently; identify dependencies between those plans. Their actual remote
integration remains outside this plugin.

Run one independent plan review before requesting explicit user approval.
Its private review contract checks spec coverage, feasible assumptions, task
boundaries and ordering, sufficient delegation context, and completion checks.
The managing agent adjudicates findings as `Addressed`, `Elevated`, or
`Dismissed`, with evidence or reasons. Resolve every material finding before
approval. Re-review only when corrections materially alter the approach or
task structure. If independent review is unavailable, disclose self-review;
if an attempted reviewer fails to return usable output, disclose that fallback
instead of claiming independence.

Preserve the approved plan immediately through the same Archive-or-Keep
contract as Planning's `specs` skill:

- Honor an existing choice. Otherwise, when Library is available, ask for
  Archive or Keep. Default to Keep when it is unavailable.
- Archive through `archiving-documentation`, following its confirmation,
  integrity, deletion, and failure boundaries. Return the exact archive
  locator and report that Library's ledger change remains uncommitted. Do not
  silently commit it or fall back to Keep on failure.
- Keep records only the approved plan through the active repository workflow.
  Approval authorizes that recording, not inclusion of unrelated changes.
- When recording is unavailable or fails, preserve the approved document and
  report the incomplete outcome rather than claim a preserved, execution-ready
  plan.

Approved plans are stable task definitions, not mutable checklists. Revisions
retain an explicit relationship to the earlier approved version and require
appropriate review, approval, and preservation. Execution identifies the
approved version it follows.

### Execution context and progress

The managing agent resolves the exact plan and spec once for dispatch context.
For archived documents, use available `read-archive` capabilities to select and
verify the exact content. Do not hand a worker broad archive exploration. If
required content cannot be read, obtain it before dispatching affected work.

Use one scratch directory per execution, associated with its workspace and
exact plan version. Follow an existing repository convention; otherwise use
`.agents/execution/<execution-id>/`. The directory holds execution progress,
task briefs, implementation reports, review results, and diagnostic reports
when needed. Keep it out of implementation commits through the active VCS's
local exclusion mechanism before creating scratch files.

The supervisor owns the progress record. Record enough to resume: plan/spec
identity, starting revision, task status, assigned agent when applicable,
recorded task revisions, verification evidence references, review findings and
dispositions, tactical decisions, blockers, and the next action. Clearly
distinguish implementation reported, awaiting review, blocked, and complete.

If preservation left a Library database change uncommitted, identify it in
execution context as a separate pending preservation change, including its
database path and affected document locators. It remains outside the
implementation recording gate even when planning and execution occur in one
session. Carry that status through resumption and the final handoff; execution
does not implicitly authorize recording it.

On resumption, reconcile this record with actual repository state before
dispatch. Do not repeat completed tasks from lost conversation memory or
accept a checkbox as proof when the referenced changes are missing or altered.
Keep Library's archive database distinct from this temporary execution record.

### `implementing-plans`

This skill supports a whole approved plan inline or one assigned task as a
delegated implementer. It inspects the relevant code, implements the scoped
work, follows repository testing conventions, and invokes `verifying-changes`
before recording the task's changes locally. Failed checks return to the
implementation loop; missing evidence is not a passing result.

Recording is part of implementation, not verification. Follow the repository's
active VCS workflow, including Jujutsu when configured, and identify the exact
recorded result. Normally a task produces one logical change. Review fixes
produce recorded follow-ups according to repository conventions; do not impose
automatic history rewriting or squash policy. Preserve unrelated work and
record only the assigned changes. If recording fails, report that state and
do not declare the task complete.

The implementer's report names the task and approved context, changes made,
recorded revision identifiers, checks and actual results, concerns, and any
missing context or blockers. Tests alone do not imply review acceptance.
Delegated implementers write their own reports; they do not update supervisor
progress, approve their work, or dispatch additional workers or reviewers.
They return to the supervisor for review and steering.

In inline mode, the primary agent also owns coordination: it maintains the
same progress information, arranges independent review when subagents are
available, adjudicates findings, and invokes final review and verification.
That coordination is performed by the primary agent, not recursively by an
implementer subagent. Without subagents, it performs and discloses self-review
using the same review contract. Inline mode retains all approval, verification,
recording, recovery, and completion requirements.

### `subagent-execution`

Default to delegation when the host supports it, unless the user requests
inline work. Honor repository workspace instructions without requiring a new
worker worktree for each task. Establish the starting revision and distinguish
pre-existing changes from this execution's work before dispatch.

Run one implementation task at a time. Give a fresh implementer the exact
task excerpt, applicable spec context, required interfaces and earlier
decisions, workspace, report destination, and `implementing-plans` instructions.
Keep unrelated session history out of its context. Select capabilities through
the host's available controls; do not hard-code model or agent names.

Read the returned report, confirm the recorded changes and evidence are
available, and dispatch `reviewing-implementation` against the exact task
range. Include all task revisions, not just the last commit. Read the actual
review result before adjudicating or declaring review complete.

Resolve task findings and verify fixes before marking the task complete and
moving to the next task. The supervisor handles coordination and adjudication;
it sends implementation and fixes to implementers rather than editing the
implementation itself. After all tasks, arrange whole-change review and
verification against the approved spec. A standalone task's completion does
not establish that the assembled change works.

### `reviewing-implementation`

Accept a scoped task change, the complete change set, or a fix range, together
with the applicable approved intent and available verification evidence. Review
implementation and tests for correctness, missing or extra behavior, unsupported
assumptions, fragile design, and material maintenance problems.

Test review checks assertion quality, meaningful branch and boundary coverage,
failure cases, mocks hiding the behavior under test, brittleness, and redundant
checks. A missing-coverage finding names the behavior and defect that could
escape. Similar tests protecting distinct contracts are not automatically
redundant. Avoid percentage targets and unsupported requests for more tests.

Inspect relevant code beyond a supplied diff when a concrete question requires
it. Run additional focused checks when existing evidence leaves a meaningful
doubt; do not blindly repeat every implementer test. Review leaves the
implementation and repository history unchanged and returns findings with
evidence, impact, and unresolved verification gaps, or an explicit result of
no material findings. It does not fix code or mark execution progress complete.

The managing agent assigns each material finding exactly one disposition:

- `Addressed`: implement and verify the correction; review its resolution.
- `Elevated`: user intent is required; affected progress remains blocked.
- `Dismissed`: evidence supports no change; record the reason.

Adjudicate when findings arrive, not after a mandatory number of retries.
Known material defects cannot be dismissed merely because attempts are
exhausted. Fix reviews check the reported defects and new breakage introduced
by the correction. Whole-change review examines spec coverage and interactions
that task reviews cannot establish independently.

### `verifying-changes`

This skill is a reusable procedure, not a required separate agent. The
implementer uses it before recording changes; the managing agent uses it for
the final assembled result. It also accepts standalone verification requests.

Given intended behavior and an explicit change scope, compare the actual diff
with that intent and run appropriate checks using existing repository tools.
Report what was established, commands or observations supporting it, failures,
untested behavior, and uncertainty. Evidence identifies the code state it
applies to, including uncommitted changes when verification precedes recording.

Choose meaningful checks for the surface: behavioral tests for code,
regression checks for reproducible bugs where practical, validation for
configuration, and structural or behavioral evaluation for documentation and
skills. Red-green evidence is useful for demonstrating that a regression test
catches the original bug, but universal test-first ordering is not required.

Verification does not fix implementation, commit, or mark tasks complete.
Checks may produce normal test outputs or scratch evidence; this does not
authorize changes to the implementation under verification. Return control to
the caller to act on failures. Missing tools or an unavailable check are
reported gaps, not success.

Final verification covers the assembled behavior and applicable integration
checks after review fixes. Retain still-applicable task evidence and rerun
checks where changes or unresolved concerns invalidate it. Neither a stale
passing run nor review approval alone establishes final correctness.

### Stalled progress and optional Debugging integration

Repeated unresolved defects, contradictory results, or conflicts between the
plan and repository can justify a diagnostic pass. The supervisor judges the
evidence rather than applying fixed retry counts or diagnosing every failed
check. Missing task context should first be supplied directly.

Give a fresh diagnostic subagent the failure, relevant approved context,
changes, verification results, previous attempts, and expected report. If an
applicable Debugging skill is in the active inventory, use it; do not assume
availability from plugin directories. Without it, the agent uses its own
investigative judgment under the same assignment. This plugin contains no
fallback debugging methodology. Without subagents, the inline agent performs
the diagnostic assignment and discloses the lack of a fresh investigator.

The assignment leaves implementation untouched and requests supported causes,
evidence, competing hypotheses or missing information, conflicts with approved
intent, why prior attempts failed, and a recommended correction and check.
The supervisor may steer the existing implementer, dispatch a replacement, or
elevate a consequential decision. An inconclusive report does not justify a
blind retry. Diagnosis itself never authorizes scope changes.

### Completion and cleanup

Finish only when approved requirements are covered, all task and whole-change
material findings are resolved, verification evidence applies to the final
implementation, and all intended implementation changes are recorded locally
without unresolved conflicts. Account for every change belonging to this execution;
unrelated pre-existing work must remain separate. Do not silently include
uncommitted Library database changes in an implementation commit.

The final handoff identifies the plan/spec, starting revision and resulting
change set, verification results, review outcomes and consequential
dispositions, remaining limitations, and any separately pending preservation
change. Readiness describes the recorded implementation; it does not assert
that the entire working copy is clean or the archive database is recorded.
Disclose self-review or unavailable checks accurately. A required acceptance
check that remains unverified blocks a claim of readiness. No publishing action
follows automatically.

After successful completion, remove only this execution's temporary artifacts.
Before removal, incorporate material approved changes into the preserved plan
or spec, ensure implementation and tests are recorded, and surface outcomes
and dispositions in the handoff. Preserve a specific diagnostic or report when
it contains lasting information those artifacts do not capture. There is no
mandatory separate completion document. Report cleanup failures without
claiming deletion succeeded.

Keep scratch when execution is incomplete, blocked, or awaiting a decision;
a session ending is not permission to clean it up. Scratch cleanup never
removes the repository workspace, unrelated files, or another execution's data.

## Technical design and constraints

Package the five skills under the new plugin's `skills` directory. Use private
references for plan structure and review, execution/report contracts, and
delegation instructions. Share contracts through references where needed;
keep coordinating rules out of worker instructions. No additional public
skills or Superpowers dependency are required.

Use existing native host tools for agents, messages, and repository operations.
Add scripts only where reliable mechanical extraction or state handling needs
them; a script must not become a new scheduling or workflow runtime.

Mirror existing plugin packaging: a README, Codex and Claude manifests,
Antigravity `plugin.json`, entries in both marketplace indexes, and a root
README link. Document direct use, default delegation, inline fallback,
approval gates, optional Library and Debugging use, and the final boundary.
Choosing the marketplace name is required before packaging, but does not
alter these workflow contracts.

## Verification

### Packaging and structural checks

Extend the existing marketplace tests where necessary to cover the new plugin's
five skills, manifests, index parity, README links, and valid JSON. Validate
private reference paths both in the installed plugin and the evaluation
runner's copied skill layout, including needed sibling skills in case
inventories. Any introduced mechanical helper receives focused tests of its
actual behavior. Do not treat prose-matching assertions as proof that agents
follow a workflow.

### Planning and preservation behavior

Evaluate missing or unapproved specs, small one-task plans, larger ordered
plans, justified decomposition, missing coverage, unsupported assumptions,
independent plan review and disclosed fallback, material revisions, and explicit
approval before preservation or execution. Exercise Archive and Keep, Library
absence, preservation failures, exact archived context retrieval, and isolation
of unrelated changes. Verify that a pending archive database change remains
separate from implementation commits and is reported in the final handoff.

### Execution, review, and verification behavior

Evaluate sequential delegation and inline execution against the same approved
plan. Observe scoped briefs, actor ownership, verify-before-record ordering,
complete task revision ranges, no worker delegation, actual reviewer output,
evidence-based dispositions, fix reviews, and final cross-task verification.

Seed tests that pass while missing behavior, weak assertions, deceptive mocks,
and genuinely redundant tests. Check that review identifies concrete logical
gaps without rejecting useful similar tests or demanding arbitrary coverage.
Exercise verification failures, unavailable checks, stale evidence, and local
recording failures; none may produce false completion.

### Recovery, integration boundaries, and cleanup behavior

Evaluate resumed execution against repository state, persistent task findings,
missing context, a diagnostic pass with and without the optional Debugging
skill, inconclusive diagnosis, and user escalation for scope conflicts. Check
that no duplicate debugging method is required and blocked executions retain
their scratch.

Observe that successful cleanup removes only the execution's temporary files
after required outcomes are surfaced or preserved. Verify that unrelated work
survives and that no push, MR creation, merge, or deployment occurs.

### Evaluation delivery

Place focused cases beside each skill in `evals/evals.json`, with fixtures and
explicit approval replies as appropriate. Reuse the existing evaluation runner
and review workflow across Codex, Claude Code, and Antigravity. Inspect tool
trajectories, repository state, and returned review text rather than relying
on completion claims. Report unsupported host capabilities and inconclusive
evidence honestly; do not introduce a second evaluation framework.
