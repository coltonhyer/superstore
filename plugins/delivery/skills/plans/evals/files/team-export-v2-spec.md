---
type: spec
title: "Team export specification"
description: "Workspace administrators can export the currently filtered team rows as UTF-8 CSV including an audit export timestamp."
status: stable
verified: { by: human:Eval Reviewer, at: 2026-10-01T12:00:00Z }
tags: [team-export]
---

# Team export specification

Workspace administrators can export the currently filtered team rows as UTF-8
CSV. The UI sends its existing team-list query unchanged to
`GET /api/workspaces/{workspace_id}/teams/export.csv`.

- **EXPORT-1:** Columns are `team_id`, `team_name`, `owner_email`, and
  `member_count`. Verify the UI action and API response.
- **EXPORT-2:** Append an `audit_exported_at` UTC ISO 8601 column (for example,
  `2026-10-01T12:00:00Z`) to every exported CSV row using the export request
  time. Scheduled exports remain out of scope.
