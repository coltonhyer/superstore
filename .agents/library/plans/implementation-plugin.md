---
title: Implementation Plugin Plan
status: approved
topics: [agent-skills, marketplace, implementation-planning, code-review, verification]
implements: specs/spec-to-integration-plugin.md
---

# Implementation Plugin Plan

## Goal and approved basis

Build `implementation`, a five-skill plugin taking an approved spec through
reviewed planning and implementation to verified, recorded local changes.
Deliver the complete plugin as one independently integrable change set, with
five sequential implementation tasks and local review boundaries.

**Specification:** *Spec-to-Integration Plugin*, original source
`docs/specs/spec-to-integration-plugin.md`, archived in `.agents/ledger.db` as
document `8df7440e-52c1-4dcd-a671-d6784dda1d1e`, SHA-256
`f48424998d7d0a25e14c34b7c8eb7fedcffa33c7ee1af775d791bc0cc4332fe5`.
Section names below refer to that exact approved document. The managing agent
loads it through Library and supplies relevant verified text to workers.

**Subsequent approved naming decision:** `implementation` is the marketplace
name, `plugins/implementation/` the directory, and
`implementation@superstore` the marketplace identifier. This resolves the
spec's deferred name without altering its archived payload.

**Execution preference for this development effort:** delegate sequentially,
using available 5.6 models for routine implementation and proportionate review;
reserve Astra for work whose reasoning demands warrant it. These are session
preferences, not model names to embed in the distributed plugin.

The existing `.agents/ledger.db` modification contains the preserved spec and
remains a separate, uncommitted preservation change. Do not include it in task
commits. This plan also requires explicit approval and preservation before
implementation; its text is not an execution progress checklist.

## Approach and shared contracts

Implement Markdown skills and private references using the repository's existing
plugin and evaluation conventions. Start without plugin runtime scripts, hooks,
persistent runtime state, new dependencies, or a Superpowers dependency. Task 4
extends the existing evaluation runner only enough to supply a case-local
optional-skill fixture. Follow the spec's authority, review, recording, recovery,
and cleanup rules throughout.

Each public skill lives at
`plugins/implementation/skills/<skill-name>/SKILL.md`, with behavioral cases at
`evals/evals.json` and fixtures beneath that skill's `evals/files/`. Keep these
private references with their owning skills:

| Owner | References | Consumers |
| --- | --- | --- |
| `plans` | `plan-template.md`, `plan-review.md` | Plan author and fresh plan reviewer |
| `implementing-plans` | `implementation-report.md`, `execution-state.md` | Workers read the report contract; inline coordinator and supervisor read execution state |
| `subagent-execution` | `implementer-brief.md`, `diagnostic-assignment.md` | Supervisor preparing scoped dispatches |
| `reviewing-implementation` | `review-contract.md` | Task, fix, and whole-change reviewers |

All listed references are under their owner's `references/` directory.
`verifying-changes` can keep its short evidence contract in `SKILL.md`.
Use sibling skill-relative paths for shared references so they resolve in both
the installed plugin and `.eval/skills/`. Eval cases must include the sibling
skills whose instructions or references they need.

Settle the contracts before their downstream consumers:

- Verification returns the checked intent and change scope, code state,
  actual commands/results or observations, and failures or gaps.
- Review returns the reviewed scope/state, material findings with evidence and
  impact, and verification gaps or an explicit no-material-findings result.
  The coordinator supplies dispositions; the reviewer does not adjudicate.
- Implementation reports bind the assigned task and approved context to the
  recorded changes, verification evidence, concerns, and blockers.
- Execution state binds one workspace/execution to the exact plan/spec,
  starting revision, task status and agent, report/evidence locations, revision
  ranges, review dispositions, decisions, pending preservation, and next action.
- A diagnostic assignment supplies the failure and previous evidence, and
  requests supported causes, uncertainty, conflicts, and a correction/check.
  It contains no alternate debugging method.

The public skill entry points must distinguish the primary agent executing a
whole plan from a delegated worker executing an assigned excerpt. Coordinating
instructions are loaded only by the primary agent or supervisor. Do not require
the full plan or shared progress document in each worker's context.

## Verification during implementation

Use `tests/test_marketplace.py`, `tests/test_eval_runner.py`, and the existing
`scripts/run_skill_evals.py` interfaces. For every task, inspect the relevant
diff and resolve task review findings before advancing. Structural checks
validate artifacts; they do not prove behavioral compliance.

Author cases with grounded fixtures, observable expectations, and fixed replies
only for unresolved choices or approval. Reuse existing `baseline` and `working`
fixture states. Each skill's `skill_name` must match its directory, and case IDs
must be unique within the skill. Shared skill dependencies belong in the case's
`skills` inventory. Task 4's optional case-local source mapping changes where a
listed test skill comes from, not which inventory the subject is told to use.

For each skill as it is created, list its cases with
`python3 scripts/run_skill_evals.py --plugin plugins/implementation --skill <skill-name> --list`.
At the task's verification point, select and run the focused behavioral cases
that establish its completion conditions using the repository's `skill-evals`
workflow. Confirm the exact case/host/model scope before spending live quota
unless already authorized, and retain evidence under an explicit output path.
Unavailable runs leave behavioral validation outstanding; do not substitute
JSON parsing or a reviewer's confidence for observed behavior.

The live invocation pattern is
`python3 scripts/run_skill_evals.py --plugin plugins/implementation --skill <skill-name> --host <approved-host> --output <retained-artifact-directory>`.
Use `--case` to select the agreed focused subset when appropriate. Task 5 closes
the remaining spec coverage across supported hosts, reusing unchanged evidence
rather than repeating already supported runs without reason.

## Task 1: Verification and implementation-review contracts

**Depends on:** none.

**Spec references:** `reviewing-implementation`, `verifying-changes`, and
Verification / Execution, review, and verification behavior.

**Create:**

- `plugins/implementation/skills/verifying-changes/SKILL.md`
- `plugins/implementation/skills/verifying-changes/evals/evals.json`
- `plugins/implementation/skills/reviewing-implementation/SKILL.md`
- `plugins/implementation/skills/reviewing-implementation/references/review-contract.md`
- `plugins/implementation/skills/reviewing-implementation/evals/evals.json`
- Focused fixtures under those two skills' `evals/files/` directories.

**Implementation shape:** Define reusable procedures for standalone use and
execution callers. Verification examines intended versus actual behavior and
returns evidence without fixing, committing, or declaring a task complete.
Review handles task, whole-change, and fix scopes; inspect meaningful coverage
and redundancy, and distinguish implementer claims from evidence. Permit
focused additional checks for concrete doubts without a mandatory full rerun.
Keep dispositions with the managing agent.

**Behavioral fixtures:** Include an uncommitted change matching intent, a
passing test hiding a behavior gap, stale results after a code edit, and an
unavailable required check. Review fixtures include weak assertions, missing
boundary/failure behavior, a mock hiding a defect, genuinely redundant tests,
and similar tests that protect different contracts. A fix-range case supplies
prior findings and checks resolution plus newly introduced breakage without
turning into an unrelated fresh review.

**Completion check:** Case discovery succeeds for both skills. Focused runs
identify seeded defects and evidence gaps while preserving implementation and
VCS state. A valid change receives supported evidence; a passing but inadequate
test does not receive an unsupported correctness verdict. Additional test
demands identify the concrete behavior they would establish. Task review
confirms the two contracts are usable by later execution callers.

**Produces:** Evidence and review contracts consumed by Tasks 3 and 4.

## Task 2: Approved-spec to approved-plan workflow

**Depends on:** Task 1's evidence and material-review conventions.

**Spec references:** Entry, routing, and authority; `plans`; Verification /
Planning and preservation behavior.

**Create:**

- `plugins/implementation/skills/plans/SKILL.md`
- `plugins/implementation/skills/plans/references/plan-template.md`
- `plugins/implementation/skills/plans/references/plan-review.md`
- `plugins/implementation/skills/plans/evals/evals.json`
- Fixtures under `plugins/implementation/skills/plans/evals/files/`.

**Implementation shape:** Use `plugins/planning/skills/specs/SKILL.md` as the
existing pattern for approval, actual review-result receipt, dispositions,
review fallback, and Archive-or-Keep semantics. Implement the new planning
responsibility in this plugin; do not alter the existing Planning skills.
Make plans small enough for their deliverable, with stable task IDs, exact
spec references, dependencies, relevant paths/patterns, and completion checks.
Keep mutable progress out of the plan template. Distinguish plan creation from
authorization to execute it, and retain exact locators for archived artifacts.

**Behavioral fixtures:** Cover missing/unapproved specs, one-task work,
dependency ordering, oversized independently deliverable work, unsupported
repository assumptions, and a plan with a missing spec requirement. Exercise
independent review, disclosed self-review, and unusable reviewer output.
Multi-turn cases establish no preservation before approval, Keep excluding
unrelated work, Archive following Library confirmation, preservation failure,
material revisions, and Library absence. Supply archive fixtures and existing
Library skills only to the cases that need them.

**Completion check:** Discovery succeeds. Focused runs produce grounded,
delegatable task definitions and expose the seeded plan defects. Explicit
approval precedes preservation; Archive returns a document locator and pending
database status, while Keep records only the approved plan. A plan-only
request never starts implementation. Missing or failed preservation never
becomes an execution-ready result.

**Produces:** Approved plan structure and preservation handoff consumed by
Tasks 3 and 4. The plan-review contract remains private to this skill.

## Task 3: Implementer workflow and inline coordination

**Depends on:** Tasks 1 and 2.

**Spec references:** Entry, routing, and authority; Execution context and
progress; `implementing-plans`; Completion and cleanup.

**Create:**

- `plugins/implementation/skills/implementing-plans/SKILL.md`
- `plugins/implementation/skills/implementing-plans/references/implementation-report.md`
- `plugins/implementation/skills/implementing-plans/references/execution-state.md`
- `plugins/implementation/skills/implementing-plans/evals/evals.json`
- Fixtures under `plugins/implementation/skills/implementing-plans/evals/files/`.

**Implementation shape:** Implement two explicit entry contexts: a delegated
worker receives one approved task brief and returns its implementation report;
an inline primary agent handles the whole plan and coordination. Both use
Task 1's verification before recording changes. The worker never dispatches
reviewers or edits supervisor progress. The inline primary invokes independent
review when available and discloses self-review otherwise.

Define execution state once in the private reference for reuse by the later
supervisor. Use local exclusions before creating plan-associated scratch.
Specify restoration of working context from exact approved plan/spec content,
progress reconciliation with the repository, whole-change checks, pending
Library changes, and cleanup only after successful completion. Respect active
VCS conventions and isolate task recording from unrelated changes.

**Behavioral fixtures:** A delegated one-task brief with unrelated dirty files
must yield verified, recorded changes and a report without worker delegation
or progress writes. Inline cases cover a multi-task plan, failed checks,
review fixes, recording failure, interrupted progress, unavailable subagents,
and material scope escalation. A completed inline fixture checks final
verification, handoff, and scratch cleanup; a blocked fixture retains scratch.

**Completion check:** Discovery succeeds. Focused trajectories establish
edit → verify → record ordering, complete task revision reporting, and no
false task completion on failure. Inline work reaches the final handoff through
the required review and assembled-change verification. Relevant existing
working-copy changes survive without entering task commits.

**Produces:** The worker and inline procedures, report format, and execution
state contract consumed by Task 4. Default delegation routing is connected and
tested once Task 4 supplies the supervisor skill.

## Task 4: Sequential supervisor and diagnostic recovery

**Depends on:** Tasks 1–3.

**Spec references:** Execution context and progress; `subagent-execution`;
Stalled progress and optional Debugging integration; Completion and cleanup.

**Create:**

- `plugins/implementation/skills/subagent-execution/SKILL.md`
- `plugins/implementation/skills/subagent-execution/references/implementer-brief.md`
- `plugins/implementation/skills/subagent-execution/references/diagnostic-assignment.md`
- `plugins/implementation/skills/subagent-execution/evals/evals.json`
- Fixtures under `plugins/implementation/skills/subagent-execution/evals/files/`.

**Modify:**

- `plugins/implementation/skills/implementing-plans/SKILL.md` and its cases only
  as needed to connect default delegation and verify the complete routing paths.
- `scripts/skill_eval_core.py` for case-local skill-fixture sources.
- `tests/test_eval_runner.py` for that source selection and inventory behavior.

**Implementation shape:** Use Task 3's execution state and report contracts,
and Task 1's review and verification procedures. Dispatch one fresh implementer
with only the assigned task, applicable spec excerpts, interfaces, and context.
Read its report and full task change range, arrange review, adjudicate findings,
and send fixes back to implementers. Mark completion only after findings and
verification gaps are resolved. Reconcile progress on resumption before
dispatching again. Finish with whole-change review, verification, and scoped
scratch cleanup. The supervisor never implements or publishes changes.

Add the diagnostic assignment as an input/output contract. It optionally
invokes an applicable installed Debugging skill; absent that skill, use agent
judgment under the same assignment. No investigative methodology or public
debugging skill is added. Findings guide steering, replacement, or user
escalation without fixed retry counts or dismissal of unresolved real defects.

**Behavioral fixtures:** A layered two-task plan checks sequential dispatch,
context isolation, task review/fixes, complete ranges, and final behavior.
Resume fixtures include a completed task, a pending review, and a missing or
altered referenced revision. Recovery fixtures cover missing context, a
repeated defect, a plan/code conflict, and inconclusive diagnosis. To exercise
the optional-plugin-present branch before Debugging exists, use a case-local
test skill with an observable diagnostic report and no invented production
method. Keep it under eval fixtures so it is not a sixth public skill or runtime
dependency. Pair it with an absent-plugin case using the same assignment.

Support an optional `skill_fixtures` mapping in a case from an explicitly listed
skill name to a case-relative fixture directory containing `SKILL.md`. Workspace
preparation copies that declared fixture into `.eval/skills/<name>` instead of
resolving a production skill. Keep prompt inventory generation unchanged and
retain ordinary production resolution for every unmapped skill. Reject names
not in the case inventory, unsafe names or paths, escaping source directories,
and missing skill files. The mapping is scoped to its declaring case.
Test successful copying and inventory exposure, invalid mappings, unchanged
production resolution, and absence of fixture skills in subsequent cases.

**Completion check:** Discovery and
`python3 -m unittest discover -s tests -p test_eval_runner.py` succeed. The
prepared present-branch workspace contains the test skill and lists it in the
active inventory; the absent branch contains and advertises neither. Focused
runs establish sequential
ownership, actual received review results, evidence-based adjudication, and
recovery without redoing completed work. Both diagnostic branches return the
same usable information; uncertainty does not trigger an unsupported retry.
Final handoff identifies recorded work and separate pending preservation.
Only successfully completed execution scratch is removed, and no publishing
or worker-workspace integration occurs.

**Produces:** The complete five-skill workflow ready for packaging and
cross-host validation.

## Task 5: Package, validate, and prepare the local handoff

**Depends on:** Tasks 1–4.

**Spec references:** Technical design and constraints; all Verification
surfaces; Completion and cleanup.

**Create:**

- `plugins/implementation/README.md`
- `plugins/implementation/.codex-plugin/plugin.json`
- `plugins/implementation/.claude-plugin/plugin.json`
- `plugins/implementation/plugin.json`

**Modify:**

- `.agents/plugins/marketplace.json`
- `.claude-plugin/marketplace.json`
- `README.md`
- `tests/test_marketplace.py`
- `tests/test_eval_runner.py` where copied-layout validation belongs.
- Earlier skill cases or references only to close demonstrated integration gaps.

**Implementation shape:** Mirror Planning's manifests and installation
documentation with the approved `implementation` identity and initial version
`0.1.0` where a version is required. Explain the five entry points, sequential
default, inline fallback, approval/preservation, optional Library/Debugging,
and local endpoint. Keep detailed SOPs in their owning skills and references.

Extend deterministic checks for exactly the intended public skill set,
marketplace parity, manifest names, README links, valid JSON, existing fixture
sources, and reference resolution in the installed and copied eval layouts.
Use existing workspace preparation helpers for copied-layout checks. Do not
introduce tests that infer agent compliance from words appearing in SKILL.md.

List the full behavioral inventory and map every spec verification surface to
its cases. Complete the agreed live matrix across Codex, Claude Code, and
Antigravity with retained evidence, including missing capabilities, optional
integrations, inline and delegated paths, and no-publishing boundaries. Review
trajectories under `skill-evals`; distinguish contract failures, judgment
concerns, missing evidence, and faulty fixtures. Correct demonstrated defects
and rerun affected cases, without coaching fixtures to force a preferred answer.
Reuse applicable evidence gathered in Tasks 1–4. Do not create a second runner.

**Completion checks:**

- `python3 -m unittest discover -s tests` passes, including new structural and
  copied-layout checks.
- `python3 -m unittest discover -s plugins/library/tests` passes for the final
  assembled repository's existing Library integration baseline.
- `python3 scripts/run_skill_evals.py --plugin plugins/implementation --list`
  discovers every authored case under the correct skill and task coverage map.
- Reviewed live evidence covers the agreed matrix and all spec behavior
  surfaces. Any unavailable or inconclusive required evidence remains explicit
  unfinished validation rather than being reported as a pass.
- Whole-change review and final verification establish the five skills compose
  correctly. Intended implementation changes are recorded locally, material
  findings are resolved, and unrelated/preservation work is accounted for.

**Produces:** The local Implementation plugin, installation documentation,
tests, behavioral cases and reviewed evidence, and an integration-ready handoff.
It does not push, open an MR, merge, or commit the separate archive database.

## Task handoff and completion

The supervisor provides each implementer its task section, the referenced
spec text, relevant shared contracts, actual predecessor interfaces, and an
explicit report destination. Use a separate execution record for this plan;
do not check tasks off in the preserved document. Execute using available
host tools and the agreed contracts, not an assumption that the unfinished
plugin is already installed or verified enough to supervise its own creation.

Normally record one logical local change per task through this repository's
Jujutsu workflow, preserving `.agents/ledger.db` outside those task changes.
Review fixes are verified and recorded follow-ups. After the final review and
verification, report the actual change range, test/eval evidence, dispositions,
limitations, and the pending preservation change. Keep incomplete execution
scratch; clean up only this execution's disposable documents after success.
