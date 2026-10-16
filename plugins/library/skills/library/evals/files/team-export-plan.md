---
title: Team export plan
status: approved
topics: [export, teams]
implements: specs/team-export.md
---

# Team export plan

## T1: Stream all pages

Iterate the team query with keyset pagination on team_id, 500 rows per page,
and write each page to the response stream until a page returns fewer than
500 rows. The UI query string is passed through unchanged.

## T2: Export button

Add an Export CSV action to the team list that calls the export endpoint.
