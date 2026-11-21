---
name: specs
description: Use when approved requirements need to become a concise, independently reviewed specification with explicit approval and preservation. If requirements are not approved yet, gather them first.
---

# Specifications

Turn approved requirements into a concise, implementation-ready living Markdown
spec. Keep requirements approval, spec review, spec approval, and commit as
distinct gates.

## Require approved requirements

Interactive human approval is strictly the default at every gate; ordinary multi-stage prompts (*"implement this ticket end-to-end"*, *"take this spec to code"*, *"preserve"*, *"save"*, *"commit"*) never waive it. Use an approved requirements summary from the conversation; if none exists, invoke sibling `requirements` with all supplied context and resume only after the user approves its summary. Do not treat a rough request, issue, or unapproved draft as approval.

When the user explicitly authorizes unattended execution, load [the autonomous mode reference](../../references/autonomous-mode.md) first: vetted approved requirements skip `requirements` elicitation, while contradictory or incomplete requirements halt before drafting.

## Resolve the living spec

Resolve the spec folder in this order:

1. A path the user names for this spec.
2. A folder that `AGENTS.md` or `CLAUDE.md` at the repository root names for
   specs, in a sentence such as `Specs live in design/specs/.`
3. `docs/specs/`. Kind folders are flat.

A spec is `current` when its `status` is absent or `stable` (`draft` and
`deprecated` specs do not own capabilities). Before creating any file, inspect
`current` specs in the resolved folder using sibling `library` (or check
existing spec frontmatter directly when running standalone) to see whether a
`current` spec's `description` already owns the capability:

- **Revise in place:** When a change alters behavior already owned by a `current`
  spec, revise that spec in place (`status: draft`, remove `verified`, review,
  obtain explicit approval — or complete a clean independent review round in
  explicitly authorized autonomous mode — and commit as `stable`); create no new
  file.
- **Create a new spec:** Create a new domain-named file (a noun, not a verb —
  `<slug>.md` matching `^[a-z0-9]+(-[a-z0-9]+)*$`, neither `index` nor `log`)
  only when no `current` spec's `description` owns the capability, and state in
  the review and approval summary (or autonomous stage report and handoff note)
  why no existing spec covers it.
- **Split along the domain seam:** When adding a change would stretch a spec's
  one-sentence `description` to an unrelated concern or make it unwieldy to
  verify in one sitting, propose splitting along the domain seam using scalar
  `supersedes: <old-path>` on each replacement spec (deprecating the split spec
  only once the replacement set is complete and approved, or cleanly reviewed in
  explicitly authorized autonomous mode, per
  [the OKF commit reference](../../references/okf-commit.md)).
- **Historical specs:** Do not perform upfront bulk compression of historical
  specs. When a change touches a domain with historical spec(s), consolidate
  into the slim living-spec shape in place, or merge overlapping specs using
  inline-list `supersedes: [path-a, path-b]`.

## Draft the spec

Before writing, inspect the relevant code, documentation, configuration, and
repository conventions. Never silently alter an approved requirement, and never
treat a choice that changes observable behavior, skipped or performed work, or
caller-visible trade-offs as a silent internal choice; in interactive mode
require explicit user intent (in explicitly authorized autonomous mode, resolve
conservatively under `Decisions for review` per the autonomous mode section
below). Whenever you resolve a genuinely internal choice without asking, list
it explicitly with what it traded away in the review and approval summary (or
under `Tactical decisions` in the autonomous stage report) — never bury it
silently in spec prose.

Start the file with this frontmatter, followed by one blank line and the body:

```markdown
---
type: spec
title: "<one-line title>"
description: "<one sentence>"
status: draft
tags: [<subject-slug>]
---
```

Write one field per line in this order, with no block lists or nesting.
Double-quote only `title` and `description`, escaping `\` and `"` inside them as
`\\` and `\"`; quote no other field. `tags` lists one or more slugs naming the
subject. Add `supersedes` after `tags` when replacing, splitting, or merging
specs: a single repository path (`supersedes: <path>`) for a replacement or
split, or an inline list (`supersedes: [path-a, path-b]`) for a merge or
consolidation. Repository paths are repo-root relative, without a leading slash,
and include `.md`, such as `docs/specs/<other-slug>.md`.

Choose the document structure in this order:

1. A structure or template explicitly supplied by the user.
2. An established repository convention.
3. Read [the default spec structure](references/spec-template.md) and follow it.

A higher-precedence structure may rename or combine sections, but it still
covers the required information unless the user explicitly overrides it. With
the default structure, require:

- `Summary`.
- `Goals and non-goals`.
- `Requirements and expected behavior`: flat, individually verifiable `R1`,
  `R2`, ..., leading with compact `Scenario | Expected outcome` tables for
  branching behavior, Given / When / Then where clear with externally
  observable `Then`, and approved observable `Definition of done` criteria
  inline.

Omit a separate `Verification` section, mandatory `Context and motivation` or
`Deployment and data effects` sections, internal implementation file paths, line
numbers, test names, and change-scoped delta narrative deferred to plans
(externally observable contract paths and OKF frontmatter paths are allowed).
Include `Technical design and constraints` only when technical choices
materially constrain valid implementations, and `Alternatives and consequential
decisions` only when rationale has lasting value. Set no target length and
retain no empty boilerplate.

`Open questions` is draft-only. In interactive mode, ask each question that
requires user intent, integrate its answer into the canonical section, and remove
the question before approval. In explicitly authorized autonomous mode, resolve
intent choices conservatively under `Decisions for review` (never marked
human-approved), integrate them, and remove `Open questions` before promotion.
Never approve or promote a spec with a blocking open question.

## Review the draft

When the user explicitly approves a spec they describe as already reviewed,
skip this section and go to the commit section; the earlier review need not
have happened in this conversation.

Before approval or autonomous promotion, read [the spec review contract](references/spec-review.md)
and [the shared review loop](../../references/review-loop.md). Review the draft
file itself.

Launch **Reviewer A** and **Reviewer B** in parallel as fresh, read-only reviewers with no parent conversation history (when subagent creation is unavailable: in interactive mode, use the disclosed self-review fallback in [the shared review loop](../../references/review-loop.md); in autonomous mode, halt immediately — never self-review). Explicitly disable parent history (such as `fork_turns: "none"`) on hosts exposing that control; a reviewer that has seen the drafting discussion is not independent. Set each reviewer's model and reasoning effort explicitly when the host exposes those controls; omitting them inherits yours, which is usually the costliest option:

- For ordinary work, step one tier down from the strongest model at moderate reasoning effort; if you already run below that tier, keep your own. Do not go lower: everything built from the spec inherits what this review misses, and nothing else checks the reviewer.
- Keep the strongest available tier and higher reasoning effort only where a missed finding is costly to reverse: authentication, secrets, or cryptography; data migration; public contracts; or broad architecture. A routine role or permission check is ordinary work.
- This skill names no models; choose from those the host lists. Use host defaults only when selection controls are unavailable.

Give each reviewer only its permitted inputs, and neither reviewer edits the spec, mutates the repository, approves the spec, or assigns dispositions:

- **Reviewer A (Requirements and spec):** Approved requirements, any explicit higher-precedence user or repository template constraints governing the draft, the exact spec draft, and the spec review contract — no repository code and no other repository documents.
- **Reviewer B (Spec and code):** The exact spec draft, read-only repository access, and the spec review contract.

Follow [the shared review loop](../../references/review-loop.md) for waiting on running reviewers, requiring `usable` output from launched reviewers before claiming an `independent` review, reviewer-failure fallbacks (in interactive mode: disclosed self-review across rounds when subagent creation is unavailable, and once-per-gate disclosed self-review per missing role without retrying a failed dispatch when subagent creation is available, halting and escalating if fallback fails or a later round fails after the one-time fallback is spent; in autonomous mode, halt immediately if an independent reviewer is unavailable, fails, or returns unusable output — never fall back to self-review), round scoping (Rounds 1–2 full draft; Round 3 onward diff-only within each role's read boundary), re-running both reviewers after any blocking edit from either reviewer, the round-3 step-back and final round, and halting and escalating if any `Blocking` finding remains unresolved after the final round.

Surface a compact disposition list in the conversation (never inside the spec) assigning every finding exactly one disposition (`Addressed`, `Elevated`, `Dismissed` with checkable evidence, or `Declined` for `Non-blocking` only). Resolve every instance of each addressed defect class across the spec, and never add prose solely to satisfy a reviewer when a human reader does not need it.

## Obtain approval

In interactive mode, after the review loop finishes clean with all findings adjudicated, present the review and approval summary — including any author-resolved internal choices with what they traded away, and why no existing spec covers a new spec — and ask the user to approve or correct the exact spec. Incorporate post-review user corrections; run another review only when they materially change scope or design. In explicitly authorized autonomous mode, skip asking for human approval and proceed directly per the commit and autonomous mode rules below after a clean independent review round.

Except in explicitly authorized autonomous mode, do not commit the spec, set `status: stable`, write `verified`, or deprecate any spec it supersedes before explicit approval. A request to preserve, save, record, or commit the spec is not approval, and calling it reviewed is not approval; only an explicit statement that the user approves it is. When such a request arrives without approval, say that the spec stays an uncommitted draft and ask the user to approve or correct it, rather than reporting it preserved.

## Commit the approved spec

Explicit approval (or a clean independent review round under explicitly authorized autonomous mode) authorizes the commit; do not ask again or offer another preservation choice. When the user explicitly approves a spec they describe as already reviewed, proceed to the commit: do not run another review, change the document's content, or ask for approval again. Any change made after approval, other than the promotion and deprecation edits in [the OKF commit reference](../../references/okf-commit.md), needs the user's approval (or clean autonomous independent review) of the changed document before it is committed.

Read and execute steps 1–5 of [the OKF commit reference](../../references/okf-commit.md) to set `status: stable` and `verified`, deprecate scalar or inline-list `supersedes` targets (for a split, only once the replacement set is complete and approved, or cleanly reviewed in explicitly authorized autonomous mode), commit strictly the modified files and verify the Jujutsu or Git recording checks, preserve changed files and report them uncommitted and not plan-ready on failure, and compute and report `<path>, blob <12-char hash>` using the resolved path.

## Autonomous mode and machine-confirmed specs

Load [the autonomous mode reference](../../references/autonomous-mode.md) whenever either condition applies:

- **Explicitly authorized autonomous mode:** Resolve `Elevated` findings and other intent choices (including unstated caller-visible behavior not following directly from a requirement) conservatively under `Decisions for review` (never marked human-approved), and record author-resolved internal choices with trade-offs under `Tactical decisions` and new-spec rationale (why no existing spec covers a new spec) in the stage report (and handoff note). If an independent reviewer is unavailable, fails, or returns unusable output — or if review does not converge — halt before promotion, leaving an uncommitted `draft` (never falling back to self-review) and emitting accumulated `Decisions for review`. A clean independent review round sets `status: stable` and `verified: { by: process:delivery-autonomous, at: <UTC> }`, commits via steps 1–5 of [the OKF commit reference](../../references/okf-commit.md) (preserving changed files and emitting `Decisions for review` on commit failure), and emits `Decisions for review` and `Tactical decisions` in the stage report.
- **Interactive confirmation of a `machine-confirmed` `stable` spec:** When an interactive gate encounters a `status: stable` spec whose `verified` line names only a non-`human:` actor, obtain explicit user approval, update `verified` (or remove it with an omission note if VCS `user.name` is empty or invalid) via step 1 and commit via steps 3–5 of [the OKF commit reference](../../references/okf-commit.md) without re-running review when content is unchanged (a `status: stable` spec with no `verified` line is **not** machine-confirmed). Any dependent `stable` plan refreshes its cited spec blob hash per [the OKF commit reference](../../references/okf-commit.md).

## Revise an approved spec

Revise in place per the in-place revision rule in [the OKF commit reference](../../references/okf-commit.md): never create a new file for a new revision. Set `status: draft` and remove `verified`, make the change, run spec review again when the change is material, obtain explicit approval (or complete a clean independent review round in explicitly authorized autonomous mode) of the revised spec, and re-commit through steps 1–5 — or propose splitting along the domain seam with `supersedes` when the change stretches the one-sentence `description` or makes the spec unwieldy in one sitting.

## Review a preserved spec later

When later work needs review against a preserved spec, the managing agent reads the spec by its committed blob hash — with Jujutsu, `git --git-dir="$(jj git root)" cat-file -p <blob>`; with Git, `git cat-file -p <blob>` (see `library`'s `pin-and-compare.md`) — or through version control when pinned by revision, and passes that content directly to the reviewer. Do not make the reviewer browse the repository's documents.
