---
type: plan
title: "Team export split plan"
description: "Two tasks that split the filtered CSV export into an API route and a dependent UI action."
status: draft
tags: [team-export]
implements: docs/specs/team-export.md
supersedes: docs/plans/team-export.md
---

# Team export split plan

## Approved specification

- **Locator:** `docs/specs/team-export.md`

## Approach

Add the existing team-list filters to one CSV export route, then expose its UI
action once the route exists.

## Tasks

### EXPORT-1: Export route

- **Spec references:** current-filter CSV export and API verification
- **Deliverable:** the export route returns the specified UTF-8 CSV
- **Prerequisites and order:** none
- **Relevant paths and patterns:** existing team list route
- **Completion check:** focused API check establishes filtered UTF-8 CSV

### EXPORT-2: Export action

- **Spec references:** UI verification
- **Deliverable:** administrators can trigger the download from the team list
- **Prerequisites and order:** after EXPORT-1; consumes the export route as
  supplied
- **Relevant paths and patterns:** existing team list action
- **Completion check:** focused UI check establishes the unchanged query is sent
