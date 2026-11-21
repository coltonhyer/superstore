---
type: spec
title: "Token policy"
description: "Issue extended API access tokens with a 120-minute lifetime and explicit refresh."
status: deprecated
verified: { by: human:Sam Kim, at: 2026-10-15T12:00:00Z }
tags: [auth, tokens]
---

# Token policy

## Requirements

- API access tokens expire 120 minutes after issuance.
- Clients request a fresh token before the 120-minute window ends.
- Expired tokens are rejected with HTTP 401.
