---
type: spec
title: "Export limits"
description: "Cap a CSV export at 100,000 rows and five exports per workspace per hour."
status: stable
verified: { by: human:Sam Kim, at: 2026-11-01T18:30:00Z }
tags: [export, rate-limits]
---

# Export limits

## Requirements

- A single CSV export contains at most 100,000 rows.
- Exports above 50,000 rows are delivered as a download link.
- A workspace may start at most 5 exports per hour.
