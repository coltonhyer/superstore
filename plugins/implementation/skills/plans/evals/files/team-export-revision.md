# Team export implementation plan, revision 2

## Approved specification

- **Locator:** `docs/specs/team-export.md`, approved version 1

## Relationship

Revises the previously approved team-export plan by adding a scheduled export
worker.

## Tasks

### EXPORT-2: Schedule recurring exports

- **Spec references:** scheduled export requirement
- **Deliverable:** recurring team CSV export worker
- **Prerequisites and order:** EXPORT-1
- **Relevant paths and patterns:** background jobs
- **Completion check:** worker test proves a scheduled CSV is delivered
