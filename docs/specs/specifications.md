---
type: spec
title: "Living specifications"
description: "Defines how the delivery plugin turns approved requirements into short, present-tense living specifications organized by enduring domain."
status: stable
verified: { by: human:Colton Hyer, at: 2026-11-20T23:33:47Z }
tags: [delivery-plugin, specifications, requirements, agent-skills]
supersedes: docs/specs/planning-plugin.md
references: [docs/specs/okf-documents.md, docs/specs/review-loop.md, docs/specs/plan-execution.md, docs/specs/autonomous-execution.md]
---

# Living specifications

## Summary

Specs are the target of the code: present-tense intended behavior, non-goals, and constraints for an enduring capability or domain. Code is the current truth. Plans and handoff notes are the per-change history.

This spec owns how `requirements` and `specs` in the `delivery` plugin structure, scope, revise, and split living specifications. Document format, folder resolution, status and verification metadata, and commit checks live in `docs/specs/okf-documents.md`; spec review lives in `docs/specs/review-loop.md`; autonomous approval stand-ins live in `docs/specs/autonomous-execution.md`.

## Goals and non-goals

Goals:

- Keep specs short, present-tense, and purely behavioral so a reader who does not know the code can restate what must be true and why.
- Keep each enduring capability in one living spec rather than scattering overlapping deltas across per-change specs.
- Surface every author-resolved trade-off explicitly rather than burying behavioral choices in prose.

Non-goals:

- Requiring a bulk upfront migration or compression of historical specs in existing repositories.
- Standalone `drift-report` or multi-reviewer brainstorm challenge skills.
- Redesigning model-tier or named-model selection guidance.

## Requirements and expected behavior

### Domain lifecycle and author choices

| ID | Scenario | Expected outcome |
| --- | --- | --- |
| R1 | A change alters behavior already owned by a current spec | Revise that spec in place (flip to `draft`, drop `verified`, run spec review per `docs/specs/review-loop.md`, re-approve or complete the autonomous approval gate in `docs/specs/autonomous-execution.md`, commit as `stable`); create no new spec file. |
| R2 | No current spec's `description` owns the capability | Create a new spec named after the domain (noun), not the change (verb), and state in the review and approval summary (or autonomous stage report and handoff note) why no existing spec covers it. |
| R3 | Adding a change would stretch a spec's one-sentence `description` to an unrelated concern or make it unwieldy to verify in one sitting | Propose splitting the spec along the domain seam using `supersedes` rather than appending unrelated behavior. |
| R4 | A choice changes observable behavior, skipped or performed work, or caller-visible trade-offs | Require user intent (or follow the autonomous intent-resolution rule in `docs/specs/autonomous-execution.md`); never treat it as a silent internal choice. |
| R5 | The author resolves a genuinely internal choice without asking | List it explicitly with what it traded away in the review and approval summary (or under `Tactical decisions` in the autonomous stage report and handoff note), never buried silently in spec prose. |

### Format and content constraints

- **R6:** Each spec describes present-tense target behavior, non-goals, and constraints for one enduring capability, with flat, individually verifiable requirements (`R1`, `R2`, ...); plans, handoffs, and review findings cite requirements as `<spec-slug>:R#` against a pinned spec blob, while sibling living specs reference one another by path and capability rather than requirement number.
- **R7:** Behavior that varies across runtime triggers, inputs, or states leads with a compact `Scenario | Expected outcome` table instead of burying branches in prose; standalone triggered behaviors use Given / When / Then where clear (with `Then` describing an externally observable outcome), and triggerless rules sit in a short list.
- **R8:** A spec names no internal implementation file paths, line numbers, or test names, includes no separate `Verification` section, and has no mandatory `Deployment and data effects` section; externally observable contract paths and OKF frontmatter paths are allowed.
- **R9:** Approved observable acceptance criteria from requirements (`Definition of done`) live inline under requirements and expected behavior; change-scoped narrative (why this delta happens now, migration steps, exact files, and concrete test commands) belongs in the plan (`docs/specs/plan-execution.md`), and alternatives appear only when their rationale has lasting value.
- **R10:** Existing historical specs in a repository require no upfront compression; a domain consolidates into a living spec when a change touches it.
- **R11:** `requirements` and `specs` treat sibling skills in `delivery` as part of the same plugin without missing-sibling-plugin hedging, and load shared workflow rules from plugin-level shared references (`docs/specs/okf-documents.md`).
