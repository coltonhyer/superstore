---
type: spec
title: "Plans, execution, and handoff history"
description: "Defines per-change implementation plans, committed-document readiness gates, blob-pinned handoff notes, and implementation execution and review checks in the delivery plugin."
status: stable
verified: { by: human:Colton Hyer, at: 2026-11-22T01:42:41Z }
tags: [delivery-plugin, implementation-planning, code-review, verification, agent-skills]
supersedes: docs/specs/spec-to-integration-plugin.md
references: [docs/specs/okf-documents.md, docs/specs/specifications.md, docs/specs/review-loop.md, docs/specs/autonomous-execution.md]
---

# Plans, execution, and handoff history

## Summary

Plans and handoff notes record per-change history alongside living specifications (`docs/specs/specifications.md`). This spec owns planning, readiness gating, implementation execution checks, implementation review checks, and handoff recording across `plans`, `implementing-plans`, `subagent-execution`, `reviewing-implementation`, and `verifying-changes` in the `delivery` plugin.

Document format, folder resolution, blob-hash computation and lookup commands, and OKF metadata rules live in `docs/specs/okf-documents.md`; review loop and disposition rules live in `docs/specs/review-loop.md`; interactive and autonomous gate rules live in `docs/specs/autonomous-execution.md`.

## Goals and non-goals

Goals:

- Keep change-scoped motivation, task definitions, file paths, and verification commands in plans and handoffs rather than crowding living specs.
- Keep committed plan and handoff citations valid across history curation, rebase, and squash-merge.
- Require committed, approved specs and plans before downstream planning or execution, and catch moved-symbol leftovers, inaccurate user docs, and tangled incidental fixes during review.

Non-goals:

- Pushing, creating pull or merge requests, merging, deploying, or publishing.
- Collapsing `implementing-plans`, `subagent-execution`, and `verifying-changes` into one implementation skill.

## Requirements and expected behavior

### Plans and readiness gates

- **R1:** Each plan carries the per-change context (brief motivation and approach), exact tasks, relevant file paths and conventions, and concrete completion checks.
- **R2:** New plans default to `YYYY-MM-DD-<name>.md` using the current date when first drafted (existing undated plans remain valid and edit in place). When a plan targets multiple specs, or targets an existing living spec that already has an earlier plan, give the new plan a change-scoped slug (`YYYY-MM-DD-<change-slug>.md`) so each change preserves its own plan and handoff history instead of overwriting earlier plans.
- **R3:** An uncommitted or dirty repository spec is not plan-ready, and an uncommitted or dirty repository plan (or any repository spec it implements) is not execution-ready; each must be committed before a downstream plan or handoff pins its blob (non-repository specs and plans omit the blob hash).
- **R4:** Committed plans and handoff notes never cite branch or pre-merge commit hashes, Jujutsu change IDs, or revision ranges; they pin cited repository specs and plans by repository path and 12-character Git blob hash (`<path>`, blob `<12-char hash>`), computed only from the post-approval committed blob per `docs/specs/okf-documents.md` (uncommitted execution scratch directories may still use revision identifiers).
- **R5:** When any cited spec or plan is revised in place before merge, refresh its blob citation to the final committed blob; a mechanical citation-only refresh on a `stable` plan whose tasks and content are unchanged commits without flipping the plan to `draft` or re-requesting approval, and refreshes the plan's blob in any downstream handoff.

### Implementation execution and review checks

- **R6:** Implementation review flags any leftover re-export shim or importer still referencing a moved symbol's old path, except shims explicitly required by an approved compatibility requirement.
- **R7:** Implementation review verifies factual claims made by changed user-facing documentation against the code.
- **R8:** Only when a pre-existing defect blocks the task or is explicitly authorized (following the scope-fit rule in `docs/specs/review-loop.md` and the autonomous intent rule in `docs/specs/autonomous-execution.md` for any observable behavior change), execution lands the incidental fix in its own commit and calls it out separately in the handoff so history curation can split it cleanly; implementation review verifies that commit separation.

### Handoff notes and skill boundaries

- **R9:** Handoff notes resolve their folder through `docs/specs/okf-documents.md` (user path, then `AGENTS.md`/`CLAUDE.md` for handoffs or else notes, defaulting to `docs/notes/`) and are named `<plan-slug>-handoff.md` — prefixing `YYYY-MM-DD-` using the current execution date when `<plan-slug>` does not already start with `YYYY-MM-DD-` (including non-repository plans) — with no revision suffix, appending `-2`, `-3`, and so on before `.md` if a prior handoff with that filename already exists.
- **R10:** Each handoff note cites its plan and every implemented repository spec by repository path and committed blob hash (when repository files), identifies the change on a `Change` line (issue, pull/merge request, or short description) rather than commit or revision ranges, and references review findings by finding ID and disposition without commit hashes or scratch paths.
- **R11:** Each handoff note includes fixed `## Decisions for review` and `## Tactical decisions` headings (writing `none` when empty), classifying entries per `docs/specs/autonomous-execution.md`.
- **R12:** `plans`, `implementing-plans`, `subagent-execution`, `reviewing-implementation`, and `verifying-changes` treat sibling skills in `delivery` as part of the same plugin without missing-sibling-plugin hedging, and load shared workflow rules from plugin-level shared references (`docs/specs/okf-documents.md`).

### Verification before recording

- **R13:** Implementation execution verifies each scoped task change through `verifying-changes` before recording the task locally, and verifies the assembled whole change before final handoff; failed checks return to the implementation loop, and missing or stale evidence never counts as a passing result.
