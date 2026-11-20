---
name: plans
description: Turn an approved specification into a reviewed, explicitly approved, and preserved implementation plan before any execution begins.
---

# Plans

Use this skill when an approved specification needs task definitions for later
implementation. Plan creation is not authorization to execute.

## Require an approved specification

Identify the approved specification by its locator: a repository-relative
path, written `path@revision` when pinned; read a pinned locator through the
active version control. A spec document (`type: spec`) must carry a
`status: stable` line. One whose `status` is `draft` or `deprecated` is not
approved, and an approval statement does not stand in for it: route it back
through Planning. A spec supplied in another form, including a file without
that frontmatter or a `type: spec` file with no status line, needs the user's
explicit approval statement.
Its requirements, rationale, and acceptance criteria remain authoritative. Do
not treat a file, draft, issue, or request as approval. If the specification is
missing or unapproved, use Planning when available or request the missing input.
An execution request with only an approved specification routes here first; do
not begin implementation.

Preserve approval and execution choices already supplied by the user. A plan
instruction that conflicts with the specification does not override it.

## Draft the plan

Inspect relevant repository behavior and conventions before drafting.

Resolve the folder for the draft in this order:

1. A path the user names for this plan.
2. A folder that `AGENTS.md` or `CLAUDE.md` at the repository root names for
   plans, in a sentence such as `Plans live in design/plans/.`
3. `docs/plans/`. Kind folders are flat.

Write the draft to `<folder>/<slug>.md`. The slug defaults to the spec's slug,
matches `^[a-z0-9]+(-[a-z0-9]+)*$`, and is neither `index` nor `log`. Start the
file with this frontmatter, followed by one blank line and the body:

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
Write `title` and `description` in double quotes, with `\` and `"` inside them
escaped as `\\` and `\"`; quote no other field. `tags` defaults to the spec's
tags. Omit `implements` when the spec is not a repository file. Add
`supersedes: <path>` after `implements` only when this plan replaces a
differently named plan. A repository path is relative to the repository root,
without a leading slash, and includes `.md`, such as `docs/specs/<spec-slug>.md`.
The template's Locator line holds the spec's path and the revision of its
approved content, or the identity the user supplied when the spec is not a
repository file.

Use [the plan template](references/plan-template.md) unless a higher-precedence
repository or user structure covers the same information. Keep one plan to one
independently integrable change. A small change can have one short task. When a
specification cannot fit a coherent, reasonably sized plan, recommend separate
plans with independently deliverable scopes and their dependencies; do not
manufacture tasks merely to fill a template.

Give tasks stable identifiers. Each task must state its deliverable and exact
spec references, prerequisites and order, relevant files and established
patterns, constraints, and a concrete completion check. A task brief may quote
the exact spec excerpt needed by an isolated worker, but does not replace the
specification. Do not include complete implementation code or mutable progress
in the plan.

Do not use a discovery task to hide an unresolved material repository or scope
decision. A discovery task is valid when it has an observable deliverable and
a check that establishes it; a command is required only when known, and a
specific manual or behavioral observation can be the check. Escalate only when
the missing owner, location, or verification approach is a material scope,
ownership, or authority boundary that bounded inspection and ordinary
engineering judgment consistent with the approved spec cannot resolve.
Otherwise, select a new within-scope file or check, or define the bounded
discovery task, instead of leaving an empty task placeholder for implementation.

## Review before approval

When the user explicitly approves a plan they describe as already reviewed,
skip this section and go to the commit section; the earlier review need not
have happened in this conversation.

Read [the plan-review contract](references/plan-review.md) before asking for
approval. Run one fresh, read-only independent review when an independent
reviewer is available. Give it the approved spec, exact plan, relevant
repository context, and this contract. Do not fork or share your conversation
with it, even when the host offers to; a reviewer that has seen the drafting
discussion is not independent. It returns findings; it does not edit, approve,
preserve, or execute the plan.

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

Read usable reviewer output before adjudicating it. A usable result contains
the contract's findings or an explicit no-material-findings result. If an
independent reviewer is unavailable, or an attempted reviewer returns no
usable output after it finishes or fails, perform one self-review under the
same contract and disclose that fallback. Do not claim independence without
the usable reviewer text.

The managing agent assigns every material finding one disposition in the
conversation: `Addressed`, `Elevated`, or `Dismissed`, with evidence or a
reason. Show each finding and its disposition before requesting approval. An
`Addressed` disposition identifies the plan change and evidence; an
`Elevated` disposition identifies the user decision that blocks approval; and
a `Dismissed` disposition gives its reason. A later reviewer conclusion does
not adjudicate earlier findings. Resolve all material findings before approval.
Re-review only when a correction materially changes scope or task structure.

## Obtain approval

Ask the user to approve or correct the exact reviewed plan. Incorporate
corrections. Run another review only when they materially change scope or task
structure.

Do not commit the plan, set `status: stable`, write `verified`, deprecate the
plan it supersedes, or execute it before explicit approval.
A request to preserve, save, record, or commit the plan is not approval, and
calling it reviewed is not approval; only an explicit statement that the user
approves it is. When such a request arrives without approval, say that the
plan stays an uncommitted draft and ask the user to approve or correct it,
rather than reporting it preserved.

## Commit the approved plan

Explicit approval authorizes the commit; do not ask again or offer another
preservation choice. When the user explicitly approves a plan they describe
as reviewed, proceed to the commit: do not run another review, change the
document's content, or ask for approval again. Any change made after approval,
other than the edits steps 1 and 2 make, needs the user's approval of the
changed document before it is committed.

1. Set `status: stable` in the plan's frontmatter and write its `verified`
   line, `verified: { by: human:<approver>, at: <approval time> }`, after
   `status`. The approver is the user name version control is configured with:
   with Jujutsu, `jj config get user.name`; with Git, `git config user.name`.
   The approval time is the UTC instant printed by
   `date -u +%Y-%m-%dT%H:%M:%SZ`. When the name is empty or contains any of
   `,` `[` `]` `{` `}` `#` `:`, write no `verified` line and say so in the
   report.
2. When the plan has `supersedes`, check the named plan first. A target
   without a `type` line is not yet migrated: leave it unchanged and say so in
   the report. Otherwise set its `status` to `deprecated` unless it already
   is, replacing its `status` line or, when it has none, adding one after
   `description`. A `supersedes` target that does not exist affects nothing.
3. Commit, through the repository's active version-control workflow, exactly
   the files steps 1 and 2 changed: the plan and, when step 2 changed it, the
   replaced plan. Leave unrelated working-copy changes out of the commit and
   untouched. Describing the working-copy change is not a commit. List each
   path once per command. With Jujutsu,
   `jj commit -m '<message>' <path> <path>` moves the files into a finished
   revision. With Git,
   `git add <path> <path> && git commit -m '<message>' <path> <path>`.
4. Verify that every committed path entered repository history and is no
   longer only in the mutable working copy. With Jujutsu, confirm that
   `jj diff -r @ <path>` prints nothing and that `jj log -r @- <path>` shows a
   revision newer than the one you started from, for each path. With Git,
   confirm that `git status --porcelain <path>` prints nothing and that
   `git log -1 -- <path>` shows the new commit, for each path. Claim a commit
   only when both checks hold for every committed path.
5. Report the plan's locator with its revision, such as
   `docs/plans/<slug>.md@<revision>`, using the resolved path.

When no supported version control exists or the commit is refused or fails,
leave every file step 3 would have committed in place with its new status and
report those files uncommitted. On any failure, report the exact outcome
without claiming completion or working around it. An uncommitted plan is not
execution-ready.

After a successful commit, return the locator to the user or continue only an
execution request the user already authorized. Later workflows read the plan
at that locator, through version control when it names a revision.

## Revise an approved plan

Revise in place; do not create a new file for a new revision. Set
`status: draft` and remove the `verified` line, make the change, and review it
again when the change is material. Obtain explicit approval of the revised
plan, then commit it as above, which sets `status: stable` and writes a new
`verified` line.

Material changes to approved scope or approach revise the plan this way, and
work on the affected scope waits for the re-approved commit. A revision the
approved specification does not support needs an approved spec revision first.
