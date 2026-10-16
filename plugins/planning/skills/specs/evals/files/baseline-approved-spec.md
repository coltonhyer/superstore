---
title: Team CSV export
status: approved
topics: [team-export]
---

# Team CSV Export

## Summary

Allow administrators to export the currently filtered team rows as UTF-8 CSV.

## Context and motivation

Administrators need to move filtered team data into external analysis tools.

## Goals and non-goals

- Export the current filtered result set.
- Do not add scheduled exports.

## Requirements and expected behavior

- Only administrators can export.
- The export uses the active team-list filters.
- The response is UTF-8 CSV.

## Verification

### API

- An administrator receives UTF-8 CSV containing only filtered rows.
- A non-administrator is rejected.

### UI

- Export uses the filters currently shown on the team list.
