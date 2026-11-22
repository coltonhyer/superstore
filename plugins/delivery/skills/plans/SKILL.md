---
name: plans
description: Turn an approved specification into a reviewed, explicitly approved, and preserved implementation plan before any execution begins.
---

# Plans

Use this skill when approved specification(s) need task definitions for later
implementation. Plan creation is not authorization to execute.

## Require approved specifications

Interactive human approval is strictly the default at every gate; ordinary
multi-stage prompts (*"implement this ticket end-to-end"*, *"take this spec to
code"*, *"preserve"*, *"save"*, *"commit"*) never waive it. Preserve approval
and execution choices already supplied by the user. When the user explicitly
authorizes unattended end-to-end execution, load
[the autonomous mode reference](../../references/autonomous-mode.md) first.

A repository spec is **committed and clean** only when: with Jujutsu,
`jj diff -r @ <path>` prints nothing and `jj file list -r @- <path>` prints
`<path>`; with Git, `git status --porcelain <path>` prints nothing and
`git ls-tree --name-only HEAD -- <path>` prints `<path>` (never use
`jj log -r @- <path>` for readiness checks). An uncommitted or dirty repository
spec is not plan-ready.

Every repository spec (`type: spec`) the plan implements must be committed and
clean and carry `status: stable`. An approval statement cannot override `draft`
or `deprecated`: route missing, unapproved, dirty, or uncommitted specs back
through sibling `specs`. In interactive mode, if any implemented `status:
stable` spec carries `verified` only from a non-`human:` actor (e.g.,
`process:delivery-autonomous`), flag it and route confirmation through sibling
`specs` per [the autonomous mode reference](../../references/autonomous-mode.md)
before planning; a `status: stable` spec with no `verified` line (such as a
migrated historical spec or one approved without a valid VCS `user.name`) is
**not** machine-confirmed.

A spec supplied in another form — including a committed and clean `type: spec`
file without a `status` line, a frontmatterless repository file, or a
non-repository spec — requires the user's explicit approval statement (and if
it is a repository file, it must still be committed and clean and pin its
committed blob hash). Do not treat a rough file, issue, or request as approval.
Spec requirements, rationale, and acceptance criteria remain authoritative; a
plan instruction that conflicts with a spec does not override it. In
interactive mode, an execution request with only an approved spec routes here
first — do not begin implementation.

## Draft the plan

Inspect relevant repository behavior and conventions before drafting. Resolve
the draft folder in order: (1) a user-named path, (2) a folder `AGENTS.md` or
`CLAUDE.md` at repository root names for plans (`Plans live in design/plans/.`),
or (3) `docs/plans/` (kind folders are flat).

Unless the user names a file path, default new plans to
`<folder>/YYYY-MM-DD-<name>.md` using today's date when first drafted
(existing undated plans remain valid and edit in place). `<name>` defaults to
the spec's slug when targeting one living spec with no earlier plan; when
targeting multiple specs or an existing living spec that already has an earlier
plan, use a change-scoped slug so each change preserves its own plan and
handoff history without overwriting earlier plans. The filename stem matches
`^[a-z0-9]+(-[a-z0-9]+)*$` and is neither `index` nor `log`.

Start the file with this frontmatter, followed by one blank line and the body:

```markdown
---
type: plan
title: "<one-line title>"
description: "<one sentence>"
status: draft
tags: [<subject-slug>]
implements: <spec path>
---
```

Write one field per line in this order, with no block lists or nesting.
Double-quote only `title` and `description`, escaping `\` and `"` inside them as
`\\` and `\"`; quote no other field. `tags` defaults to implemented spec(s)'
tags. `implements` holds a single repo path or inline list `[path-a, path-b]`,
omitted when all specs are non-repository. Add `supersedes` after `implements`
(scalar `<path>` or inline list `[path-a, path-b]`) only when replacing earlier
plan(s). Repository paths are repo-root relative, without a leading slash, and
include `.md`, such as `docs/specs/<spec-slug>.md`.

Committed plans never cite branch or pre-merge commit hashes, Jujutsu change
IDs, or revision ranges. Pin every cited repository spec as
`<path>, blob <12-char hash>` computed strictly from its committed blob via
step 5 of [the OKF commit reference](../../references/okf-commit.md) or
`library`'s `pin-and-compare.md` — never from a dirty working copy.
Non-repository specs are excluded from `implements` (omit `implements` when
all specs are non-repository), omit blob hashes, and cite the user-supplied
identity.

Use [the plan template](references/plan-template.md) unless a higher-precedence
repository or user structure covers the same information. Carry per-change
context (brief motivation and approach), exact tasks, relevant file paths and
conventions, and concrete completion checks. Keep one plan to one independently
integrable change; a small change can have one short task. When specs cannot fit
a coherent, reasonably sized plan, recommend separate plans with independently
deliverable scopes and their dependencies; do not manufacture tasks merely to
fill a template.

Give tasks stable identifiers. Each task states its deliverable, exact spec
references (`<spec-slug>:R#` or section against pinned spec blob(s)),
prerequisites and order, relevant files and established patterns, constraints,
and a concrete completion check. A task brief may quote the exact spec excerpt
needed by an isolated worker, but does not replace the spec. Do not include
complete implementation code or mutable progress in the plan.

Do not use a discovery task to hide an unresolved material repository or scope
decision. A discovery task is valid when it has an observable deliverable and
a check that establishes it; a command is required only when known, and a
specific manual or behavioral observation can be the check. Escalate only when
the missing owner, location, or verification approach is a material scope,
ownership, or authority boundary that bounded inspection and ordinary
engineering judgment consistent with the approved spec cannot resolve; otherwise
select a new within-scope file or check, or define the bounded discovery task.

## Review before approval

In interactive mode, when the user explicitly approves a plan they describe as
already reviewed, skip this section and go to the commit section; the earlier
review need not have happened in this conversation.

Before approval or autonomous promotion, read
[the plan-review contract](references/plan-review.md) and
[the shared review loop](../../references/review-loop.md). Review the draft
file itself. Launch one fresh, read-only independent reviewer when subagent
creation is available, giving it the approved spec(s), exact plan, relevant
repository context, and plan-review contract. Explicitly disable parent history
(such as `fork_turns: "none"`) on hosts exposing that control; a reviewer that
has seen the drafting discussion is not independent. It returns findings; it
does not edit, approve, commit, assign dispositions, or execute the plan.

Set the reviewer's model and reasoning effort explicitly when the host exposes
those controls; omitting them inherits yours, which is usually the costliest
option. For an ordinary plan, step one tier down from the strongest model at
moderate reasoning effort; if you already run below that tier, keep your own.
Do not go lower: every task inherits what this review misses, and nothing else
checks the reviewer. Keep the strongest available tier and higher reasoning
effort only where a missed finding is costly to reverse: authentication,
secrets, or cryptography; data migration; public contracts; or broad
architecture. A routine role or permission check is ordinary work. This skill
names no models; choose from those the host lists.

Wait for a running reviewer and require `usable` output before claiming an `independent` review. Follow [the shared review loop](../../references/review-loop.md) for reviewer-failure fallbacks (in interactive mode: disclosed self-review across rounds when subagent creation is unavailable, and once-per-gate disclosed self-review without retrying a failed dispatch when subagent creation is available, halting if fallback fails or a later round fails after the one-time fallback is spent; in autonomous mode, halt immediately before promotion if an independent reviewer is unavailable, fails, or returns unusable output — never fall back to self-review), round scoping (Rounds 1–2 full plan; Round 3 onward diff-only within the supplied plan, spec(s), and relevant code), blocking-edit re-runs (any blocking edit triggers the next round up to round 3 plus the step-back final round; `Non-blocking` findings record without forcing another round), and halting and escalating — never promoting — if any `Blocking` finding remains unresolved after the final round.

Assign every finding one disposition in the conversation (never inside the
plan): `Addressed`, `Elevated`, `Dismissed` with checkable evidence, or
`Declined` for `Non-blocking` only. Resolve every instance of an addressed
defect class across the plan, and never add prose solely to satisfy a reviewer.

## Obtain approval

In interactive mode, after the review loop finishes clean with all findings
adjudicated, present the review summary and ask the user to approve or correct
the exact reviewed plan. Incorporate corrections; re-run review when corrections
materially change scope, approach, or task structure (or resolve any blocking
edit). In explicitly authorized autonomous mode, skip asking for human approval
and proceed directly to commit after a clean independent review round.

Except in explicitly authorized autonomous mode, do not commit the plan, set
`status: stable`, write `verified`, deprecate `supersedes` targets, or execute
it before explicit approval. A request to preserve, save, record, or commit
the plan is not approval, and calling it reviewed is not approval; only an
explicit statement that the user approves it is. When such a request arrives
without approval, say that the plan stays an uncommitted draft and ask the user
to approve or correct it, rather than reporting it preserved. Keep execution
authorization separate from plan approval in interactive mode.

## Commit the approved plan

Explicit approval (or a clean independent review round under explicitly
authorized autonomous mode) authorizes the commit; do not ask again or offer
another preservation choice. When the user explicitly approves a plan they
describe as already reviewed, proceed to commit: do not run another review,
change the document's content, or ask for approval again. Any edit after
approval, other than promotion/deprecation edits (or a mechanical
blob-citation-only refresh), requires approval (or clean autonomous independent
review) of the changed plan before committing.

Read and execute steps 1–5 of [the OKF commit reference](../../references/okf-commit.md) to set `status: stable` and `verified`, deprecate scalar or inline-list `supersedes` targets, commit strictly the modified files and verify the Jujutsu or Git recording checks, preserve changed files and report them uncommitted and not execution-ready on failure, and compute and report `<path>, blob <12-char hash>` using the resolved path. Continue only an execution request the user already authorized.

## Revise or refresh an approved plan

- **In-place revision:** Revise in place per
  [the OKF commit reference](../../references/okf-commit.md) — never create a
  new file for a new revision. Set `status: draft` and remove `verified`, make
  the change, review again when material (or always complete a clean
  independent review round in explicitly authorized autonomous mode), obtain
  explicit approval (skipping human approval in explicitly authorized autonomous
  mode after that clean round), and re-commit through steps 1–5. Work on
  affected scope waits for the re-approved commit; a revision unsupported by the
  spec(s) needs an approved spec revision first.
- **Mechanical blob-citation-only refresh:** When a `stable` plan's tasks and
  content are unchanged and only cited spec blob hash(es) need updating, run the
  two-step mechanical refresh in
  [the OKF commit reference](../../references/okf-commit.md) without flipping
  `status` to `draft`, changing `verified`, or re-requesting approval, and
  commit any refreshed pre-merge handoff as its own separate revision.

## Autonomous mode and machine-confirmed plans

Load [the autonomous mode reference](../../references/autonomous-mode.md)
whenever either condition applies:

- **Explicitly authorized autonomous mode:** Resolve `Elevated` findings and
  other intent choices (including unstated caller-visible behavior not
  following directly from a requirement) conservatively under
  `Decisions for review` (never marked human-approved), and record internal
  trade-offs under `Tactical decisions` in the stage report (and handoff note).
  On reviewer unavailability/failure or unconverged review, halt before
  promotion leaving an uncommitted `draft` (never self-review) and emit
  accumulated `Decisions for review`. A clean independent review round sets
  `status: stable` and `verified: { by: process:delivery-autonomous, at: <UTC> }`,
  commits via steps 1–5 of
  [the OKF commit reference](../../references/okf-commit.md) (preserving changed
  files and emitting `Decisions for review` on commit failure), and emits
  `Decisions for review` and `Tactical decisions` in the stage report.
- **Interactive confirmation of a `machine-confirmed` `stable` plan:** When an
  interactive gate encounters a `status: stable` plan verified only by a
  non-`human:` actor, obtain explicit user approval, update `verified` (or
  remove it with an omission note if VCS `user.name` is empty or invalid) via
  step 1 and commit via steps 3–5 of
  [the OKF commit reference](../../references/okf-commit.md) without re-running
  review when content is unchanged (a `status: stable` plan with no `verified`
  line is **not** machine-confirmed), and refresh any existing pre-merge
  handoff as its own separate revision via step 2 of the mechanical refresh in
  [the OKF commit reference](../../references/okf-commit.md) (verifying the steps
  3–4 recording check and leaving the refreshed handoff in place as uncommitted
  on failure).
