# Autonomous execution mode and decision surfacing

This reference defines the opt-in boundary, interactive vs. autonomous gate
rules, `machine-confirmed` re-confirmation routing, halt behavior, and decision
surfacing contracts across `requirements`, `specs`, `plans`, and execution.

## Scope, defaults, and non-goals

- **Default:** Interactive human approval is strictly the default at every
  gate (`requirements`, `specs`, `plans`, and execution).
- **Opt-in scope:** Autonomous mode supports explicitly authorized unattended
  runs from vetted approved requirements to a recorded local change without
  waiving independent agent review.
- **Post-run visibility:** Every autonomous intent resolution and out-of-scope
  delivery choice must be surfaced prominently for post-run human review.
- **Non-goals:** Autonomous mode never pushes, creates pull or merge requests,
  merges, deploys, or publishes after a run finishes. It never waives
  independent agent review or promotes drafts on author self-review.

## Opt-in and gate behavior (R1–R9)

**R1 — Explicit authorization required:** Autonomous mode applies only when the
user explicitly authorizes unattended end-to-end execution (for example,
explicitly delegating `specs`, `plans`, and execution approvals in advance).
Ordinary multi-stage requests (*"implement this ticket end-to-end"*, *"take this
spec to code"*, *"preserve"*, *"save"*, *"commit"*) never waive interactive
approval.

| ID | Gate or event | Interactive mode (default) | Opt-in autonomous mode |
| --- | --- | --- | --- |
| **R2** | Approved requirements | Require approval via a `requirements` summary; an issue, rough request, or unapproved draft is not approval. | Vetted requirements explicitly supplied as approved with the autonomous authorization skip `requirements` elicitation; if supplied requirements are contradictory or incomplete, halt immediately before drafting or promoting anything and report the blocker. |
| **R3** | Promotion and `verified` metadata | Explicit user approval sets `status: stable` and writes `verified: { by: human:<approver>, at: <UTC> }` per `okf-commit.md` (omitting `verified` — and removing any existing `verified` line — when configured VCS `user.name` is unset, empty, or contains `,` `[` `]` `{` `}` `#` `:`). | A clean independent review round (see `review-loop.md`) sets `status: stable` and writes `verified: { by: process:delivery-autonomous, at: <UTC> }` per `okf-commit.md` (OKF `machine-confirmed`, never `human:`). Independent agent review is never waived, and drafts never promote on author self-review. |
| **R4** | Encountering `machine-confirmed` `stable` documents later | Flag any `status: stable` spec or plan verified only by a non-`human:` actor (for example, `verified: { by: process:delivery-autonomous, at: ... }`) and route confirmation through the owning workflow (`specs` or `plans`): obtain explicit user approval, update `verified` per R3 and step 1 of `okf-commit.md` (removing any existing `verified` line with an omission note if VCS `user.name` is empty or invalid), and commit via steps 3–5 of `okf-commit.md` without re-running review when content is unchanged. When confirming a `stable` spec leaves dependent `stable` plan(s) citing the old spec blob, refresh each dependent plan's cited spec blob hash(es) per the mechanical blob-citation-only refresh in `okf-commit.md`. | Proceeds within the authorized autonomous run without pausing for human confirmation. |
| **R5** | Execution authorization | Requires explicit execution authorization separate from plan approval. | Authorized up front by the autonomous opt-in once the plan passes its clean independent review round and is promoted and committed. |
| **R6** | `Elevated` findings and intent choices | `Elevated`; blocks approval until the user answers. | Resolve with the most conservative option satisfying the approved requirements, integrate the resolution and complete required re-review per `review-loop.md`, record the choice under `Decisions for review`, and never mark it as human-approved. |
| **R7** | Spec or plan revisions after downstream start | Pause affected work until the revised document is reviewed (when material) and explicitly re-approved by the user. | Pause affected work while revising in place, and resume only after the revised document passes its clean independent review round and is promoted and committed per `okf-commit.md`. |
| **R8** | Unconverged gate, reviewer failure/unavailability, or contradictory requirements | For reviewer failure or unavailability, follow the disclosed self-review fallback rules in `review-loop.md`; on an unrecovered failure, unconverged gate, or contradictory/incomplete requirements, stop before promotion, leave the draft as an uncommitted `draft`, retain execution scratch if any, and report the blocker. | Triggers whenever a gate does not converge, supplied requirements are contradictory/incomplete, or an independent reviewer is unavailable, fails, or returns unusable output (per `review-loop.md`): halt immediately before promotion with zero fallback to author self-review, leave the draft as an uncommitted `draft` (never promote to `stable`), retain execution scratch if any, and report the blocker while emitting each accumulated `Decisions for review` entry in full with all five R11 fields (`Question`, `Options considered`, `Chosen option`, `Reason`, `Evidence`). |
| **R9** | Unresolved verification failure (when task fix-and-reverify cannot clear a check) or commit/recording failure | Stop immediately and do not proceed downstream; retain execution scratch for execution or handoff failures; for a spec or plan commit failure after promotion edits, leave every file the commit step changed in place with its new status (and updated fields) and report them uncommitted and not downstream-ready. | Follow the same immediate halt, scratch retention, and file-preservation rule, plus emit each accumulated `Decisions for review` entry in full with all five R11 fields in the halt report. |

**`R4` clarification (no `verified` line):** A `status: stable` document with no
`verified` line (such as a migrated historical spec or one approved
interactively without a valid VCS `user.name`) is **not** treated as
non-`human:` machine-confirmed and does not trigger confirmation routing.

## Surfacing decisions (R10–R12 and `specifications:R5`)

### R10 — Where decisions appear

- Autonomous `specs` and `plans` stages emit `Decisions for review` and
  `Tactical decisions` in their stage reports.
- Autonomous execution records both prior-stage and execution
  `Decisions for review` in execution state alongside `Tactical decisions`,
  and surfaces them in the final handoff note.
- Any autonomous halt report or spec-only / plan-only autonomous run emits each
  accumulated `Decisions for review` entry in full with all five R11 fields
  (`Question`, `Options considered`, `Chosen option`, `Reason`, `Evidence`)
  alongside its status or blocker (plus any `Tactical decisions`).

### R11 — `Decisions for review`

Include **only** choices that change what the change delivers:

- an out-of-scope addition (excluding tests and docs of the change itself),
- a departure from a requirement,
- any intent choice or `Elevated` finding not resolved by the user, or
- an unstated caller- or operator-visible behavior that does not follow
  directly from a stated requirement.

Frame each entry with these five fields:

- **Question:** one plain question for post-run human review.
- **Options considered:** viable alternatives evaluated.
- **Chosen option:** the conservative option applied (never marked
  human-approved).
- **Reason:** why it is the most conservative choice satisfying requirements.
- **Evidence:** checkable file, symbol, requirement ID, or command output.

### R12 and `specifications:R5` — `Tactical decisions`

Include everything else: test mechanics, internal code structure,
review-process steps, genuinely internal spec or plan choices with what they
traded away (`specifications:R5`), and observable effects that follow directly
from a stated requirement.

- Record one concise line each with checkable evidence (and trade-off when an
  author resolves an internal spec or plan choice without asking).
- Never bury internal spec choices silently in prose: in interactive runs list
  them with trade-offs in the review and approval summary; in autonomous runs
  list them under `Tactical decisions` in the stage report and handoff note.
