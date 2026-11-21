---
type: spec
title: "Team export API"
description: "Provide an administrator-only API endpoint to export filtered team rows as UTF-8 CSV."
status: stable
verified: { by: human:Sam Kim, at: 2026-11-01T18:30:00Z }
tags: [team-export, api]
---

# Team Export API

## Summary

Provide an administrator-only API endpoint to export filtered team rows as UTF-8 CSV.

## Goals and non-goals

- Goals:
  - Return filtered team rows as UTF-8 CSV for workspace administrators.
- Non-goals:
  - Scheduled API exports.

## Requirements and expected behavior

- `R1`: Only workspace administrators may request the export endpoint; non-administrators receive HTTP 403.
  - *Acceptance criterion:* Requesting the endpoint as a non-administrator returns HTTP 403.
- `R2`: Requests return HTTP 200 with UTF-8 CSV rows matching the query filters.
  - *Acceptance criterion:* An administrator receives HTTP 200 with filtered UTF-8 CSV.
