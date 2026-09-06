---
name: plans
description: Turn an approved specification into a reviewed, explicitly approved, and preserved implementation plan before any execution begins.
---

# Plans

Use this skill when an approved specification needs task definitions for later
implementation. Plan creation is not authorization to execute.

## Require an approved specification

Identify the approved specification by its exact repository or archive locator.
Its requirements, rationale, and acceptance criteria remain authoritative. Do
not treat a file, draft, issue, or request as approval. If the specification is
missing or unapproved, use Planning when available or request the missing input.
An execution request with only an approved specification routes here first; do
not begin implementation.

Preserve approval and execution choices already supplied by the user. A plan
instruction that conflicts with the specification does not override it.

## Draft the plan

Inspect relevant repository behavior and conventions before drafting. Write
under `docs/plans` unless repository convention or the user selects another
location. Follow an established naming convention or use a descriptive slug.

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

Read [the plan-review contract](references/plan-review.md) before asking for
approval. Run one fresh, read-only independent review when an independent
reviewer is available. Give it the approved spec, exact plan, relevant
repository context, and this contract. It returns findings; it does not edit,
approve, preserve, or execute the plan.

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

## Obtain approval and preserve the approved plan

Ask the user to approve or correct the exact reviewed plan. Do not preserve,
commit, or execute it before explicit approval. Material changes to approved
scope or approach create a revision related to the earlier approved plan; it
needs the appropriate review, explicit approval, and preservation before work
on the affected scope.

After approval, inspect the active skill inventory for
`archiving-documentation`; do not infer availability from plugin directories or
the ledger. Honor an existing Archive or Keep choice. When Library is
available and no choice exists, ask the user to choose:

- **Archive:** Invoke `archiving-documentation` with the exact approved path.
  Follow its scan, confirmation, integrity, cleanup, and failure boundaries.
  Return its exact document locator and report that the ledger change remains
  uncommitted. Do not make a version-control commit or fall back to Keep if
  archival fails.
- **Keep:** Record only the approved plan through the active repository
  workflow. Verify it entered history; approval does not authorize unrelated
  working-copy changes.

When Library is unavailable, use Keep without presenting unavailable archival
as an option. If recording is unavailable or fails, preserve the recoverable
document and report the incomplete outcome; it is not execution-ready.

After successful preservation, report the exact plan locator and either return
it to the user or continue only an execution request the user already
authorized. For an archived plan needed later, the managing agent uses
`read-archive` to load the exact verified document before supplying it to the
next workflow.
