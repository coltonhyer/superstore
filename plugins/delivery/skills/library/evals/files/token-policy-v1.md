---
type: spec
title: "Token policy"
description: "Issue short-lived API access tokens with a 15-minute lifetime."
status: deprecated
verified: { by: human:Sam Kim, at: 2026-10-15T12:00:00Z }
tags: [auth, tokens]
---

# Token policy

## Requirements

- API access tokens expire 15 minutes after issuance.
- Expired tokens are rejected with HTTP 401.
