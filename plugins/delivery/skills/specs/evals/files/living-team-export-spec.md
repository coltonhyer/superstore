---
type: spec
title: "Team CSV export"
description: "Allow administrators to export currently filtered team rows as UTF-8 CSV."
status: stable
verified: { by: human:Sam Kim, at: 2026-11-01T18:30:00Z }
tags: [team-export]
---

# Team CSV Export

## Summary

Administrators can export the currently filtered team rows from the team list as UTF-8 CSV.

## Goals and non-goals

- Goals:
  - Export the active filtered team rows for workspace administrators as UTF-8 CSV.
- Non-goals:
  - Scheduled or background exports.

## Requirements and expected behavior

- `R1`: Only workspace administrators may export team rows; non-administrators are rejected.
  - *Acceptance criterion (API):* Requesting the export as a non-administrator returns HTTP 403.
- `R2`: The export returns UTF-8 CSV containing only the rows matching the active team-list filters.
  - *Acceptance criterion (API):* An administrator receives HTTP 200 with a UTF-8 CSV response matching the active filters.
- `R3`: The team-list UI export action submits the filters currently shown on the team list.
  - *Acceptance criterion (UI):* Triggering export in the team-list UI downloads the filtered UTF-8 CSV for the active filters.
