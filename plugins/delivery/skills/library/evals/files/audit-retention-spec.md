---
type: spec
title: "Audit log retention"
description: "Keep audit log entries for 365 days, then delete them."
status: stable
verified: { by: human:Sam Kim, at: 2026-11-01T18:30:00Z }
tags: [audit, retention]
supersedes: design/specs/audit-retention-old.md
---

# Audit log retention

## Requirements

- Audit log entries are kept for 365 days.
- Entries older than 365 days are deleted by the nightly job.
