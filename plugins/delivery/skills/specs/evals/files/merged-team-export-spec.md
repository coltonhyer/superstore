---
type: spec
title: "Team CSV export"
description: "Allow administrators to export currently filtered team rows as UTF-8 CSV across UI and API."
status: draft
tags: [team-export]
supersedes: [docs/specs/export-api.md, docs/specs/export-ui.md]
---

# Team CSV Export

## Summary

Consolidate the team export API and UI capabilities into one administrator-only UTF-8 CSV export specification.

## Goals and non-goals

- Goals:
  - Allow workspace administrators to export filtered team rows from the UI and API as UTF-8 CSV.
- Non-goals:
  - Scheduled exports and custom column selection dialogs.

## Requirements and expected behavior

- `R1`: Only workspace administrators may view the Export CSV UI control or request the export API; non-administrators receive HTTP 403.
  - *Acceptance criterion:* Non-administrators do not see the UI export control and receive HTTP 403 from the export API.
- `R2`: Triggering Export CSV in the UI or calling the export API returns HTTP 200 with UTF-8 CSV matching the active team-list filters.
  - *Acceptance criterion:* Administrators receive UTF-8 CSV containing only the filtered team rows from both the UI action and the API endpoint.
