# Team CSV Export

## Summary

Allow workspace users to export the currently filtered team rows as UTF-8 CSV.

## Context and motivation

Users need filtered team data for offline analysis.

## Goals and non-goals

- Allow administrators and ordinary workspace members to export.
- Do not add scheduled exports.

## Requirements and expected behavior

- The export uses the active team-list filters.
- Administrators and ordinary workspace members can export.
- The response is UTF-8 CSV.

## Verification

### API

- Administrators and ordinary workspace members receive filtered UTF-8 CSV.

### UI

- The export action uses the filters currently shown on the team list.
