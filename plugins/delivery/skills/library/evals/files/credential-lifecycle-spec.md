---
type: spec
title: "Credential lifecycle"
description: "Unify session and API token rotation, revocation, and expiry rules."
status: stable
verified: { by: human:Sam Kim, at: 2026-11-01T18:30:00Z }
tags: [auth, tokens, credentials]
supersedes: [docs/specs/session-policy.md, docs/specs/token-policy.md]
---

# Credential lifecycle

## Requirements

- Unifies session and API token issuance under one rotation schedule.
- Revoking an account credential invalidates all active tokens immediately.
