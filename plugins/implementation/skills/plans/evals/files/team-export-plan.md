# Team export implementation plan

## Approved specification

- **Locator:** `docs/specs/team-export.md`

## Approach

Add the existing team-list filters to one CSV export route and expose its UI
action.

## Tasks

### EXPORT-1: Export filtered teams

- **Spec references:** current-filter CSV export and UI/API verification
- **Deliverable:** administrators can download the specified CSV
- **Prerequisites and order:** none
- **Relevant paths and patterns:** existing team list route and action
- **Completion check:** focused UI and API checks establish filtered UTF-8 CSV
