---
type: spec
title: "Team CSV export"
description: "Allow workspace users to export the currently filtered team rows as UTF-8 CSV."
status: draft
tags: [team-export]
---

# Team CSV Export

## Summary

Allow workspace users to export the currently filtered team rows as UTF-8 CSV.

## Goals and non-goals

- Goals:
  - Allow administrators and ordinary workspace members to export the currently filtered team rows as UTF-8 CSV.
- Non-goals:
  - Scheduled exports.

## Requirements and expected behavior

- `R1`: Administrators and ordinary workspace members can export the currently filtered team rows.
  - *Acceptance criterion:* Requesting an export as an administrator or ordinary workspace member succeeds with the filtered team rows.
- `R2`: The export returns UTF-8 CSV containing only the currently filtered team rows.
  - *Acceptance criterion:* The export output uses UTF-8 CSV encoding and includes only the currently filtered team rows.
