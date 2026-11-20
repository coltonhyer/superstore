---
type: spec
title: "Team data export"
description: "Replace the team CSV export with an export that also includes the member count."
status: draft
tags: [team-export]
supersedes: docs/specs/team-export.md
---

# Team Data Export

## Summary

Allow administrators to export the currently filtered team rows as UTF-8 CSV,
including a member_count column, in place of the existing team CSV export.

## Context and motivation

Administrators need member counts in the data they move into external
analysis tools.

## Goals and non-goals

- Export the current filtered result set with a member_count column.
- Do not add scheduled exports.

## Requirements and expected behavior

- Only administrators can export.
- The export uses the active team-list filters.
- The response is UTF-8 CSV whose last column is member_count, with the same
  value as the team-list rows.

## Verification

### API

- An administrator receives UTF-8 CSV containing only filtered rows and the
  member_count column.
- A non-administrator is rejected.

### UI

- Export uses the filters currently shown on the team list.
