---
type: spec
title: "Team export"
description: "Export the filtered team rows as UTF-8 CSV across all pages."
status: stable
verified: { by: human:Sam Kim, at: 2026-11-01T18:30:00Z }
tags: [export, teams]
---

# Team export

## Requirements

- Administrators export the currently filtered team rows as UTF-8 CSV.
- The export includes every matching row across all pages, not only the
  visible page.
- Columns are team_id, team_name, owner_email, and member_count, in that order.
