# Execution state

Only the inline primary or later supervisor reads and updates this record. A
delegated worker receives its task brief and writes an implementation report;
it does not load or modify execution state.

Create the execution directory only after adding it to the active VCS's local
exclusion mechanism. Keep the record with that one workspace and exact approved
plan version. On resumption, reconcile every claimed task revision, report,
evidence location, and disposition against the repository before acting.

```markdown
# Execution <id>

- **Approved plan:** exact locator, approved revision, and supplied content
  identity.
- **Approved spec:** exact locator, version, and supplied content identity.
- **Authorization and choices:** execution authorization and preserved user
  choices.
- **Workspace and start:** workspace identity, starting revision, VCS, scratch
  path, and local exclusion location.

## Tasks

| Task | Status | Agent | Report/evidence | Recorded revisions | Review findings and dispositions |
| --- | --- | --- | --- | --- | --- |
| <id> | pending / implementing / reported for review / awaiting review / blocked / complete | <owner> | <paths> | <ids or none> | <IDs and dispositions> |

## Decisions, blockers, and recovery

- **Tactical decisions:** <decision and evidence>
- **Blockers or scope escalation:** <what is missing and required approval>
- **Next action:** <one concrete action>
```

`complete` requires a recorded result, current verification, resolved material
findings, supporting locations, and no unresolved conflicts. Before final
readiness, account for every intended implementation change in this execution;
unrelated pre-existing work remains separate. Keep reports, review results,
diagnostic reports, and evidence paths while the execution is incomplete.

## Handoff note

At successful whole-plan handoff, after whole-change checks pass, the primary
writes the note to `<handoffs folder>/<execution-id>.md`, using this
execution's id. The execution id must match `^[a-z0-9]+(-[a-z0-9]+)*$` and be
neither `index` nor `log`, which OKF reserves. Resolve the handoffs folder in
this order:

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

- **Plan:** `<plan path>@<revision>`
- **Spec:** `<spec path>@<revision>`
- **Start:** `<starting revision>` **Result:** `<start>..<end>`

## Whole-change checks

## Review outcomes and dispositions

## Limitations

## Tactical decisions
```

Fill each section from this record, writing `none` for an empty one; the
note's Result range excludes the note's own revision. Record the note as its
own revision through the active VCS workflow. Remove only this execution's
scratch after the note is recorded. If recording the note fails, leave the
note in place, report the failure, and retain scratch. Also retain scratch for
a blocker, interruption, failed record, unresolved decision, or cleanup
failure.

A note counts as recorded only when the recording check in implementing-plans
holds for its path: the working copy no longer changes the note, and the newest
revision touching it is new. A described working-copy commit is not recorded.
