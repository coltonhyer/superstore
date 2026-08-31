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

Write the draft under `docs/specs`. Follow an established repository naming
convention; otherwise use `docs/specs/<descriptive-slug>.md`.

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

Before requesting approval, read
[the review contract](references/spec-review.md) and produce one review result
unless the user opts out. Initial review always uses the live Markdown before
any archival.

### Produce the review

When subagent creation is available, launch one fresh, read-only reviewer:

- For ordinary work, use a capable general-purpose reviewer at the host's
  normal intelligence and effort.
- Prefer a stronger available tier and higher reasoning effort for security,
  data migration, public contracts, or broad architecture.
- Use host defaults when selection controls are unavailable. Never hard-code a
  model or agent name.

Give the reviewer only the approved requirements, exact draft, relevant
repository context, and review contract. The reviewer reports findings; it
does not edit the spec or approve it.

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

Do not archive or commit the spec before explicit approval.

## Preserve the approved spec

After approval, inspect the active skill inventory for
`archiving-documentation`. Do not infer availability from a plugin directory
or `.agents/ledger.db`. Honor an Archive or Keep choice the user already made.

When `archiving-documentation` is available and no choice exists, ask whether
to:

- **Archive:** Invoke Library with the exact approved path. Follow its scan,
  confirmation, cleanup, and failure boundaries. Stop without making a
  version-control commit, and report that the ledger change remains uncommitted.
  If archival fails, preserve recoverable state and do not silently fall back to
  Keep.
- **Keep:** Commit only the approved spec through the repository's active
  version-control workflow. Verify that the spec entered repository history and
  no longer remains only in the mutable working copy before claiming it was
  committed. Approval authorizes that commit; do not ask again or include
  unrelated working-copy changes.

When Library is unavailable, use Keep without treating the missing integration
as an error. If no supported version control exists, leave the spec under
`docs/specs` and report that it was not committed. On any failure, report the
exact outcome without claiming completion.

## Review an archived spec later

When later work needs review against an archived spec, the managing agent uses
`read-archive` to select and load the exact verified Markdown, then passes
that content directly to the reviewer. Do not make the reviewer browse or load
the archive broadly.
