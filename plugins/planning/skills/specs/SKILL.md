---
name: specs
description: Use when approved requirements need to become a concise, independently reviewed specification with explicit approval and preservation. If requirements are not approved yet, gather them first.
---

# Specifications

Turn approved requirements into an implementation-ready Markdown spec. Keep
requirements approval, spec approval, review, and preservation as distinct
gates.

## Require approved requirements

Use an approved requirements summary from the conversation. If none exists,
invoke the `requirements` skill with all context the user already supplied,
then resume here only after the user approves its summary.

Do not treat a rough request, issue, or unapproved draft as approval.

## Draft the spec

Before writing, inspect the relevant code, documentation, configuration, and
repository conventions. Use engineering judgment to make the design concrete,
but do not silently alter an approved requirement. Ask the user when a
consequential ambiguity requires their intent; resolve reversible internal
choices yourself.

Write the draft to `.agents/library/specs/<slug>.md` unless the user names
another location; only an explicit user-supplied path overrides it. Use a
descriptive slug matching `^[a-z0-9]+(-[a-z0-9]+)*$`. Start the file with this
frontmatter, followed by one blank line and the body:

```markdown
---
title: <one-line title>
status: draft
topics: [<subject-slug>]
---
```

`topics` lists at least one slug naming the subject. Add `supersedes:
specs/<other-slug>.md` only when this spec replaces a differently named one.
A spec written to a user-supplied path outside the library carries the same
frontmatter without `supersedes`.

Choose the document structure in this order:

1. A structure or template explicitly supplied by the user.
2. An established repository convention.
3. [Planning's default structure](references/spec-template.md).

A higher-precedence structure may rename or combine sections, but it still
covers the required information unless the user explicitly overrides it.

With the default structure, require:

- Summary.
- Context and motivation.
- Goals and non-goals.
- Requirements and expected behavior.
- Verification organized by test surface, with the behaviors verified under
  each surface.

Include technical design and constraints only when they materially constrain
the solution. Include alternatives and consequential decisions only when their
rationale has lasting value. Set no target length and retain no empty
boilerplate.

`Open questions` is draft-only. Ask each question that requires user intent,
integrate its answer into the canonical section, and remove the resolved
question. Do not approve a spec with a blocking open question.

## Review the draft

When the user explicitly approves a spec they describe as already reviewed,
skip this section and go to the commit section; the earlier review need not
have happened in this conversation.

Before requesting approval, read
[the review contract](references/spec-review.md) and produce one review result
unless the user opts out. Review the draft file itself.

### Produce the review

When subagent creation is available, launch one fresh, read-only reviewer. Set
its model and reasoning effort explicitly when the host exposes those controls;
omitting them inherits yours, which is usually the costliest option:

- For ordinary work, step one tier down from the strongest model at moderate
  reasoning effort; if you already run below that tier, keep your own. Do not
  go lower: everything built from the spec inherits what this review misses,
  and nothing else checks the reviewer.
- Keep the strongest available tier and higher reasoning effort only where a
  missed finding is costly to reverse: authentication, secrets, or
  cryptography; data migration; public contracts; or broad architecture. A
  routine role or permission check is ordinary work.
- This skill names no models; choose from those the host lists. Use host
  defaults only when selection controls are unavailable.

Give the reviewer only the approved requirements, exact draft, relevant
repository context, and review contract. Do not fork or share your conversation
with it, even when the host offers to; a reviewer that has seen the drafting
discussion is not independent. The reviewer reports findings; it does not edit
the spec or approve it.

When subagent creation is unavailable, perform the same review yourself and
disclose that it was not independent.

### Read the review

Receive and read a usable review result before adjudicating findings or asking
for approval. A usable result follows the review contract: it either contains
material findings or explicitly reports that there are none. Tool or agent
status without review text is not a review result.

Wait for the launched reviewer to finish or fail before deciding that it
returned no usable result. A reviewer that is still running has not failed.

Treat the review as independent only when usable output came from the launched
reviewer. If an independent attempt returns no usable result, do not retry it;
perform one self-review using the same contract and disclose the fallback.

### Adjudicate the review

Exercise independent judgment over every material finding. Surface a compact
disposition list in the conversation, not in the spec:

- `Addressed`: change the spec and identify where.
- `Elevated`: ask the user to adjudicate; approval remains blocked.
- `Dismissed`: make no change and give a short reason.

Leave no material finding unresolved or deferred; assign each one exactly one
of the three dispositions. Resolve lower-risk findings when the evidence
supports one answer; elevate findings that require user intent or a
consequential trade-off. Review again only when a resolution materially changes
scope or design.

## Obtain approval

After review findings are resolved or adjudicated, ask the user to approve or
correct the exact spec. Incorporate corrections. Run another review only when
they materially change scope or design.

Do not commit the spec or set `status: approved` before explicit approval.
A request to preserve, save, record, or commit the spec is not approval, and
calling it reviewed is not approval; only an explicit statement that the user
approves it is. When such a request arrives without approval, say that the
spec stays an uncommitted draft and ask the user to approve or correct it,
rather than reporting it preserved.

## Commit the approved spec

Explicit approval authorizes the commit; do not ask again or offer another
preservation choice. When the user explicitly approves a spec they describe
as reviewed, proceed to the commit: do not run another review, change the
document's content, or ask for approval again. Any change made after approval
needs the user's approval of the changed document before it is committed.

1. Set `status: approved` in the spec's frontmatter.
2. Commit only that file through the repository's active version-control
   workflow. Leave unrelated working-copy changes out of the commit and
   untouched.
3. Verify that the spec entered repository history and is no longer only in
   the mutable working copy. Describing the working-copy change is not a
   commit. With Jujutsu, `jj commit -m '<message>' <path>` moves it into a finished revision; confirm
   that `jj diff -r @ <path>` prints nothing and that `jj log -r @- <path>`
   shows a revision newer than the one you started from. With Git,
   `git add <path> && git commit -m '<message>' <path>`; confirm that
   `git status --porcelain <path>` prints nothing and that
   `git log -1 -- <path>` shows the new commit. Claim a commit only when both
   checks hold.
4. Report the spec's locator with its revision, such as
   `.agents/library/specs/<slug>.md@<revision>`.

When no supported version control exists or the commit is refused, leave the
file in place with `status: approved` and report it uncommitted. On any
failure, report the exact outcome without claiming completion or working
around it.

## Revise an approved spec

Revise in place; do not create a new file for a new revision. Set
`status: draft`, make the change, and review it again when the change is
material. Obtain explicit approval of the revised spec, then commit it as
above.

## Review a preserved spec later

When later work needs review against a preserved spec, the managing agent reads
the file at its locator, through version control when the locator names a
revision, and passes that content directly to the reviewer. Do not make the
reviewer browse the library.
