---
type: spec
title: "Opt-in autonomous execution and decision triage"
description: "Defines interactive approval defaults, explicit autonomous execution opt-in, gate stand-ins, machine-confirmed verification, and Decisions for review carry-over across delivery."
status: stable
verified: { by: human:Colton Hyer, at: 2026-11-22T00:33:29Z }
tags: [delivery-plugin, autonomous-execution, specifications, implementation-planning, agent-skills]
references: [docs/specs/okf-documents.md, docs/specs/specifications.md, docs/specs/review-loop.md, docs/specs/plan-execution.md]
---

# Opt-in autonomous execution and decision triage

## Summary

This spec defines the boundary between interactive human-gated execution (the default) and explicitly authorized unattended execution across the `delivery` plugin, together with how unresolved intent choices are triaged and carried forward to human review. Shared autonomous gate stand-in rules live in plugin-level shared references bundled with `delivery` rather than duplicated across skills.

## Goals and non-goals

Goals:

- Keep interactive human approval strictly the default at every gate unless the user explicitly authorizes unattended execution.
- Support explicitly authorized unattended runs from vetted requirements to a recorded local change without waiving independent agent review.
- Surface every autonomous intent resolution and out-of-scope delivery choice prominently for post-run human review.

Non-goals:

- Pushing, creating pull or merge requests, merging, deploying, or publishing after an autonomous run finishes.
- Waiving independent agent review or promoting drafts on author self-review in autonomous mode.

## Requirements and expected behavior

### Approval default and opt-in boundary

- **R1:** Interactive human approval is the default at every gate; autonomous mode applies only when the user explicitly authorizes unattended end-to-end execution (for example, explicitly delegating spec, plan, and execution approvals in advance). Ordinary multi-stage requests (*"implement this ticket end-to-end"*, *"take this spec to code"*, *"preserve"*, *"save"*, *"commit"*) never waive interactive approval.

### Gate and event stand-ins

| ID | Gate or event | Interactive mode (default) | Opt-in autonomous mode |
| --- | --- | --- | --- |
| R2 | Requirements input | Approved via `requirements` summary; an issue or rough request is not approval. | Vetted requirements explicitly supplied as approved with the autonomous authorization skip elicitation; contradictory or incomplete requirements halt. |
| R3 | Spec or plan approval | Explicit user approval sets `status: stable` and writes `verified: { by: human:<approver>, at: <UTC> }` (omitting `verified` when the configured VCS user name is empty or contains reserved YAML punctuation per `docs/specs/okf-documents.md`). | A clean independent review round (`docs/specs/review-loop.md`) sets `status: stable` and writes `verified: { by: process:delivery-autonomous, at: <UTC> }` (OKF `machine-confirmed`, never `human:`). No agent review is waived. |
| R4 | Downstream consumption of machine-confirmed docs | An interactive gate encountering a `status: stable` spec or plan verified only by a non-`human:` actor flags it and routes confirmation through the owning workflow (`specs` or `plans`) to obtain explicit user approval, update `verified` per R3 (removing `verified` with a note if VCS `user.name` is empty or invalid), and commit without re-running review when content is unchanged (refreshing any dependent plan's spec blob per `docs/specs/plan-execution.md`). | Proceeds within the authorized autonomous run. |
| R5 | Execution authorization | Requires explicit execution authorization separate from plan approval. | Authorized up front by the autonomous opt-in once the plan passes its clean independent review round. |
| R6 | Choice or finding requiring user intent | `Elevated` (`docs/specs/review-loop.md`); blocks approval until the user answers. | Resolve with the most conservative option satisfying the requirements, record under `Decisions for review`, and never mark as human-approved. |
| R7 | Spec or plan revision during execution | Pause affected work until user re-approves. | Resume after the revised document passes its clean independent review round. |
| R8 | Unconverged gate, unrecovered reviewer failure (`docs/specs/review-loop.md`), or contradictory requirements | Stop before promotion; leave draft as uncommitted `draft`, retain execution scratch if any, and report the blocker. | Halt before promotion; leave draft as uncommitted `draft` (never promote to `stable`), retain execution scratch if any, and report the blocker with all accumulated `Decisions for review`. |
| R9 | Unresolved verification failure (when task fix-and-reverify cannot clear a check) or commit/recording failure | Stop immediately and do not proceed downstream; retain execution scratch for execution or handoff failures; for a spec or plan commit failure after promotion edits, leave every file the commit step changed in place with its new status and report them uncommitted and not downstream-ready. | Same halt and file-preservation rule, plus emit all accumulated `Decisions for review` in the halt report. |

### Decision carry-over and classification

- **R10:** Autonomous `specs` and `plans` emit `Decisions for review` in their stage reports; execution records both prior-stage and execution `Decisions for review` in execution state alongside `Tactical decisions`; any autonomous halt report or spec/plan-only autonomous run emits all accumulated `Decisions for review` alongside its status or blocker.
- **R11:** `Decisions for review` holds only choices that change what the change delivers — an out-of-scope addition (excluding tests and docs of the change itself), a departure from a requirement, any intent choice or finding not resolved by the user, or an unstated caller- or operator-visible behavior that does not follow directly from a stated requirement — each framed as one plain question with options considered, chosen option, reason, and evidence.
- **R12:** `Tactical decisions` holds everything else — test mechanics, internal code structure, review-process steps, and observable effects that follow directly from a stated requirement — one line each with evidence.
