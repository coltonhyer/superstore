---
type: spec
title: "Review loop and finding dispositions"
description: "Defines parallel two-reviewer spec review, the shared bounded review loop across delivery gates, reviewer-failure fallbacks, and checkable finding dispositions."
status: stable
verified: { by: human:Colton Hyer, at: 2026-11-22T00:15:14Z }
tags: [delivery-plugin, code-review, specifications, implementation-planning, agent-skills]
supersedes: [docs/specs/planning-plugin.md, docs/specs/spec-to-integration-plugin.md]
references: [docs/specs/specifications.md, docs/specs/plan-execution.md, docs/specs/autonomous-execution.md, docs/specs/okf-documents.md]
---

# Review loop and finding dispositions

## Summary

This spec owns independent review across `delivery` gates — parallel two-reviewer spec review, plan review, per-task implementation review, and whole-change implementation review — along with checkable finding dispositions. Shared review-loop and disposition rules live in plugin-level shared references bundled with `delivery` rather than duplicated across skills.

## Goals and non-goals

Goals:

- Catch spec defects against both approved requirements and live repository code before approval.
- Guarantee that every review loop converges within a hard bound instead of churning indefinitely.
- Require checkable evidence before dismissing review findings without turning minor observations into endless edit loops.

Non-goals:

- A standalone invocable `review-loop` skill.
- Redesigning model-tier or named-model selection guidance.

## Requirements and expected behavior

### Two-reviewer spec review

- **R1:** Before spec approval, launch Reviewer A and Reviewer B in parallel as fresh, read-only reviewers, except on interactive mode's fast-path when the user explicitly approves a spec they describe as already reviewed.

| ID | Reviewer | Inputs | Checks |
| --- | --- | --- | --- |
| R2 | Reviewer A (requirements and spec) | Approved requirements and spec draft only (reads no repository code and browses no other repository documents) | Requirement coverage and contradictions; ambiguity (would two readers build the same thing?); scope fit; and **ask for less** (flag internal implementation file paths, line numbers, test names, or change-story bloat, exempting OKF frontmatter and externally observable contract paths). |
| R3 | Reviewer B (spec and code) | Spec draft and read-only repository access | Every claim about current code is true (cited or not); changed symbols or values are traced to all consumers (including stored data or operational effects when relevant); **hollow guarantees and footguns** (normal production triggers reach and satisfy the practical goal rather than being blocked or bypassed); and optional testability verification of specified behaviors on a temporary copy of the source without mutating the repository. |

### Reviewer-failure fallbacks

| ID | Scenario | Expected outcome |
| --- | --- | --- |
| R4 | Interactive mode on a host without subagent creation | Use disclosed self-review across rounds of the gate, bounded by the normal round cap and escalation rules. |
| R5 | Interactive mode on a host with subagent creation, when any reviewer at a single- or multi-reviewer gate fails or returns unusable output | Fall back once per gate to a disclosed self-review for each missing role without retrying the failed dispatch; if that fallback cannot complete or a later round fails after the one-time fallback is spent, halt and escalate to the user. |
| R6 | Autonomous mode when an independent reviewer is unavailable, fails, or returns unusable output | Halt immediately per `docs/specs/autonomous-execution.md`; never promote a spec or plan to `stable` on author self-review. |

### Shared review loop

These rules apply across spec, plan, task, and whole-change reviews:

- **R7:** Every reviewer starts with fresh context and no parent conversation history; on hosts exposing a history-forking control, the caller explicitly disables parent history (for example, `fork_turns: "none"`).
- **R8:** Every reviewer tags each finding `Blocking` (correctness, requirement or scope gap, false code claim, consumer breakage, hollow guarantee, or contract/gate defect) or `Non-blocking` (minor polish or optional improvement).
- **R9:** Every finding names both a one-line defect class and the specific instance; addressing a finding fixes every instance of that class in the artifact or change under review.
- **R10:** Reviewers that receive approved requirements or intent classify any addition beyond approved requirements as *serves the ask* (non-behavior-changing support work such as tests, documentation, or internal structure directly serving the ask — the managing agent may keep it) or as *unnecessary* or *conflicts* (the managing agent removes it without escalating); any addition that changes observable behavior or delivered scope still requires user intent (or `Decisions for review` per `docs/specs/autonomous-execution.md`).
- **R11:** Rounds 1 and 2 review the full artifact or change; from round 3 onward, the reviewer receives the diff since the prior round, prior findings and dispositions, and classes already fixed, scoped to checking that diff, newly introduced regressions, and whether each fix resolved its class (with targeted reads of the artifact or repository allowed only to verify class-wide fixes or code claims).
- **R12:** A round is clean only when every reviewer at the gate produces no blocking edits; any blocking edit at a multi-reviewer gate re-runs all reviewers for that gate, while non-blocking findings are recorded without forcing another round.
- **R13:** If round 3 still does not finish clean, stop ordinary rounds, step back to reconsider the approach (whether scope grew beyond requirements or a recurring class signals a design flaw), apply any redesign, and run one final round (diff-only for targeted edits; full artifact when a redesign was applied).
- **R14:** After the final round, record remaining non-blocking findings; if the final round does not finish clean — meaning any blocking finding is not `Dismissed` with checkable evidence (including any finding that would require a blocking edit or remains `Elevated`) — do not apply an unreviewed fix or run another round; halt progression at that gate and escalate to the user (including halting autonomous mode rather than promoting to `stable`).

### Checkable finding dispositions

The managing agent (never the reviewer) assigns every finding one disposition in the conversation or report, never inside the spec or plan:

| ID | Disposition | When allowed | Required record |
| --- | --- | --- | --- |
| R15 | `Addressed` | Finding holds and is fixed (mandatory for `Blocking`; optional for `Non-blocking`; optional code edits still require fresh verification and recording) | Where the artifact or code changed and how the defect class was resolved. |
| R16 | `Elevated` | Resolution requires user intent or depends on facts outside every file the reviewer could read | The open question for the user; blocks interactive approval (or resolves conservatively under `docs/specs/autonomous-execution.md` in autonomous mode). |
| R17 | `Dismissed` | Finding is wrong based on checkable evidence the reviewer could have read (a file and symbol, or a decision recorded in the artifact) | Exact checkable evidence. *"This was intentional"* is never valid; a fresh reader's inability to follow a spec or plan is never dismissed. |
| R18 | `Declined` | `Non-blocking` finding only — true but minor (never allowed for blocking correctness, requirement, or contract defects) | Short rationale; recorded without editing and without triggering another review round. |

- **R19:** Never add prose to a spec or plan solely to satisfy a reviewer when a human reader does not need it.
