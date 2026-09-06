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

- **Approved plan:** exact locator, preserved version, and supplied content
  identity.
- **Approved spec:** exact locator, version, and supplied content identity.
- **Authorization and choices:** execution authorization and preserved user
  choices.
- **Workspace and start:** workspace identity, starting revision, VCS, scratch
  path, and local exclusion location.
- **Pending preservation:** `none` or separate Library database path and
  affected archive document locators; it is outside implementation recordings.

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
unrelated pre-existing work and pending Library preservation remain separate.
Keep reports, review results, diagnostic reports, and evidence paths while the
execution is incomplete. Final handoff also records the resulting change set,
whole-change checks, review outcomes, limitations, and any separately pending
preservation change. Remove only this execution's scratch after that successful
handoff; retain it for a blocker, interruption, failed record, unresolved
decision, or cleanup failure.
