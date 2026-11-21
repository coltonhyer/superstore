# Execution state

Only the inline primary or later supervisor reads and updates this record. A
delegated worker receives its task brief and writes an implementation report;
it does not load or modify execution state.

Create the execution directory (normally `.agents/execution/<run-id>/`) only
after adding it to the active VCS's local exclusion mechanism. Keep the record
with that one workspace and exact approved plan version. On resumption,
reconcile every claimed task revision, report, evidence location, and
disposition against the repository before acting.

```markdown
# Execution <run-id>

- **Approved plan:** <plan path>, blob <12-char hash> (or non-repository identity)
- **Approved specs:** <spec path>, blob <12-char hash> for each implemented repository spec (or non-repository identity)
- **Authorization and choices:** <interactive vs. explicitly authorized autonomous opt-in, and preserved choices>
- **Workspace and start:** <workspace identity, starting revision for local recovery and whole-change diff verification, VCS, scratch path, and local exclusion location>

## Tasks

| Task | Status | Agent | Report/evidence | Recorded revisions | Review findings and dispositions |
| --- | --- | --- | --- | --- | --- |
| <id> | pending / implementing / reported for review / awaiting review / blocked / complete | <owner> | <paths> | <ids or none> | <IDs and dispositions> |

## Decisions, blockers, and recovery

- **Decisions for review:** <prior-stage (specs/plans) and execution entries using five fields: Question, Options considered, Chosen option, Reason, Evidence — or none>
- **Tactical decisions:** <one concise line each, including prior-stage tactical decisions, with checkable evidence — or none>
- **Incidental fixes:** <separate-commit pre-existing fixes with recorded revision and verification — or none>
- **Blockers or scope escalation:** <what is missing and required approval>
- **Next action:** <one concrete action>
```

`complete` requires a recorded result, current verification, resolved material
findings, supporting locations, and no unresolved conflicts. Before final
readiness, account for every intended implementation change in this execution;
unrelated pre-existing work and separate-commit incidental pre-existing fixes
remain distinct. Keep reports, review results, diagnostic reports, and evidence
paths while the execution is incomplete. On any halt, verification failure,
recording failure, or unconverged gate, retain execution scratch and — in an
explicitly authorized autonomous run — emit each accumulated `Decisions for
review` entry in full with all five fields (`Question`, `Options considered`,
`Chosen option`, `Reason`, `Evidence`), plus any `Tactical decisions`, in the
halt report.

## Handoff note

At successful whole-plan handoff, after whole-change checks pass, the primary
writes the note to `<handoffs folder>/<plan-slug>.md` with no revision suffix,
appending `-2`, `-3`, and so on if a prior handoff for that slug already exists.
The slug must match `^[a-z0-9]+(-[a-z0-9]+)*$` and be neither `index` nor
`log`, which OKF reserves. Resolve the handoffs folder in this order:

1. A path the user names for this note.
2. A folder that `AGENTS.md` or `CLAUDE.md` at the repository root names for
   handoffs, in a sentence such as `Handoffs live in design/handoffs/.`
3. `docs/handoffs/`. Kind folders are flat.

The note's frontmatter holds these fields, one per line, in this order:

- `type: handoff`.
- `title`: the plan's title without its trailing word `plan`, matched in any
  letter case (`plan`, `Plan`), followed by ` execution`, such as
  `Authentication sessions execution` for the plan titled
  `Authentication sessions plan`.
- `description`: one sentence saying what the execution delivered.
- `tags`: copied from the plan.
- `implements`: the plan's repository path, only when the plan is a repository
  file.

Write `title` and `description` in double quotes, with `\` and `"` inside them
escaped as `\\` and `\"`; quote no other field. A repository path is relative
to the repository root, without a leading slash, and includes `.md`. The
headings are fixed so notes stay uniform:

```markdown
---
type: handoff
title: "<plan title without trailing plan> execution"
description: "<one sentence on what the execution delivered>"
tags: [<plan tags>]
implements: <plan path>
---

# <plan title without trailing plan> execution

- **Plan:** <plan path>, blob <12-char hash>
- **Specs:** <spec path>, blob <12-char hash> (list each implemented repository spec; omit `, blob <12-char hash>` if non-repository)
- **Change:** <issue, pull/merge request, or short description>

## Whole-change checks

## Review outcomes and dispositions

## Incidental fixes

## Limitations

## Decisions for review

## Tactical decisions
```

Fill each section from this record, writing `none` for an empty one. Omit
`, blob <12-char hash>` for non-repository plans or specs, and list every
implemented repository spec on `Specs`. Committed handoff notes never cite
branch or pre-merge commit hashes, Jujutsu change IDs, revision ranges, or
scratch paths: identify the change on `Change`, reference review findings by
finding ID and disposition, call out separate-commit incidental pre-existing
fixes under `## Incidental fixes` without commit hashes, format each entry
under `## Decisions for review` with the five fields (`Question`,
`Options considered`, `Chosen option`, `Reason`, `Evidence`), and list each
entry under `## Tactical decisions` on one concise line with checkable evidence.

Record the handoff note as its own separate revision through the active VCS
workflow (never bundled with other files). Remove only this execution's scratch
after the note is recorded. If recording the note fails, leave the note in
place, report the failure (emitting each accumulated `Decisions for review`
entry in full with all five fields in an autonomous run), and retain scratch.
Also retain scratch (and emit each accumulated `Decisions for review` entry in
full with all five fields in an autonomous run) for a blocker,
interruption, verification failure, failed record, unconverged gate, unresolved
decision, or cleanup failure.

A note counts as recorded only when the recording check in implementing-plans
holds for its path: with Jujutsu, `jj diff -r @ <path>` prints nothing and
`jj log -r @- <path>` shows a new revision; with Git,
`git status --porcelain <path>` prints nothing and `git log -1 -- <path>`
shows the new commit. A described working-copy commit is not recorded.
