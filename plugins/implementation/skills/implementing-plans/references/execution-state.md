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
writes `.agents/library/notes/<execution-id>.md`, using this execution's id.
Its frontmatter holds `title` (the plan's subject followed by ` execution`,
such as `Authentication sessions execution` for a plan titled
`Authentication sessions plan`), `topics` copied from the plan, and
`implements: plans/<slug>.md` only when the plan is a library document; a note
for a plan at a user-supplied path outside the library omits `implements`. The
headings are fixed so notes stay uniform:

```markdown
---
title: <plan subject> execution
topics: [<plan topics>]
implements: plans/<slug>.md
---

# <plan subject> execution

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
