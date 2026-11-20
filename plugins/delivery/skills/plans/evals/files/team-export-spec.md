---
type: spec
title: "Team export specification"
description: "Workspace administrators can export the currently filtered team rows as UTF-8 CSV."
status: stable
verified: { by: human:Eval Reviewer, at: 2026-10-01T12:00:00Z }
tags: [team-export]
---

# Team export specification

Workspace administrators can export the currently filtered team rows as UTF-8
CSV. The UI sends its existing team-list query unchanged to
`GET /api/workspaces/{workspace_id}/teams/export.csv`. Columns are `team_id`,
`team_name`, `owner_email`, and `member_count`. Scheduled exports are out of
scope. Verify the UI action and API response.
