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
active version control. A spec under `.agents/library/specs/` must carry
`status: approved`; a `draft` spec is not approved. For a spec supplied at a
path outside the library, the user's explicit approval statement suffices.
Its requirements, rationale, and acceptance criteria remain authoritative. Do
not treat a file, draft, issue, or request as approval. If the specification is
missing or unapproved, use Planning when available or request the missing input.
An execution request with only an approved specification routes here first; do
not begin implementation.

Preserve approval and execution choices already supplied by the user. A plan
instruction that conflicts with the specification does not override it.

## Draft the plan

Inspect relevant repository behavior and conventions before drafting. Write
the draft to `.agents/library/plans/<slug>.md`; only an explicit user-supplied
location overrides that path. The slug defaults to the spec's slug and matches
`^[a-z0-9]+(-[a-z0-9]+)*$`. Start the file with this frontmatter, followed by
one blank line and the body:

```markdown
---
title: <one-line title>
status: draft
topics: [<subject-slug>]
implements: specs/<spec-slug>.md
---
```

`topics` defaults to the spec's topics. Omit `implements` when the spec is
outside the library or the plan is written to a user-supplied path outside the
library. The template's Locator line holds the spec's path and the revision of
its approved content; for a spec outside the library, that is the supplied path
and revision.

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

Ask the user to approve or correct the exact reviewed plan. Do not set
`status: approved`, commit, or execute it before explicit approval. A request
to preserve, save, record, or commit the plan is not approval, and calling it
reviewed is not approval; only an explicit statement that the user approves it
is. When such a request arrives without approval, say that the plan stays an
uncommitted draft and ask the user to approve or correct it, rather than
reporting it preserved.

## Commit the approved plan

Explicit approval authorizes the commit; do not ask again or offer another
preservation choice. When the user explicitly approves a plan they describe
as reviewed, proceed to the commit: do not run another review, change the
document's content, or ask for approval again. Any change made after approval
needs the user's approval of the changed document before it is committed.

1. Set `status: approved` in the plan's frontmatter.
2. Commit only that file through the repository's active version-control
   workflow. Leave unrelated working-copy changes out of the commit and
   untouched.
3. Verify that the plan entered repository history and is no longer only in
   the mutable working copy. Describing the working-copy change is not a
   commit. With Jujutsu, `jj commit -m '<message>' <path>` moves it into a finished revision; confirm
   that `jj diff -r @ <path>` prints nothing and that `jj log -r @- <path>`
   shows a revision newer than the one you started from. With Git,
   `git add <path> && git commit -m '<message>' <path>`; confirm that
   `git status --porcelain <path>` prints nothing and that
   `git log -1 -- <path>` shows the new commit. Claim a commit only when both
   checks hold.
4. Report the plan's locator with its revision, such as
   `.agents/library/plans/<slug>.md@<revision>`.

When no supported version control exists or the commit is refused, leave the
file in place with `status: approved` and report it uncommitted. On any
recording failure, report the exact outcome without claiming it was committed
or working around it. An uncommitted plan is not execution-ready.

After a successful commit, return the locator to the user or continue only an
execution request the user already authorized. Later workflows read the plan
at that locator, through version control when it names a revision.

## Revise an approved plan

Material changes to approved scope or approach revise the plan in place; do
not create a new file for a new revision. Set `status: draft`, make the change,
and review it again. Obtain explicit approval of the revised plan, then commit
it as above before work on the affected scope proceeds. A revision the approved
specification does not support needs an approved spec revision first.
