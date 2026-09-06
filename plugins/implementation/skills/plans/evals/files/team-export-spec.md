# Team export specification

**Status:** Approved

Workspace administrators can export the currently filtered team rows as UTF-8
CSV. The UI sends its existing team-list query unchanged to
`GET /api/workspaces/{workspace_id}/teams/export.csv`. Columns are `team_id`,
`team_name`, `owner_email`, and `member_count`. Scheduled exports are out of
scope. Verify the UI action and API response.
