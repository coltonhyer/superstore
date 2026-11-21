---
type: spec
title: "Team export UI"
description: "Provide a team-list UI export action that downloads currently filtered team rows as CSV."
status: stable
verified: { by: human:Sam Kim, at: 2026-11-01T18:30:00Z }
tags: [team-export, ui]
---

# Team Export UI

## Summary

Provide an Export CSV button on the team-list view for workspace administrators.

## Goals and non-goals

- Goals:
  - Trigger CSV downloads using the active team-list filters in the UI.
- Non-goals:
  - Custom column selection in the export dialog.

## Requirements and expected behavior

- `R1`: Only administrators see and trigger the Export CSV button on the team list.
  - *Acceptance criterion:* Ordinary workspace members do not see the Export CSV action.
- `R2`: Triggering Export CSV passes the active team-list UI filters and downloads the CSV file.
  - *Acceptance criterion:* Clicking Export CSV downloads UTF-8 CSV matching the active UI filters.
