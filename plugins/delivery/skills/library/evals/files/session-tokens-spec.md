---
type: spec
title: "Session tokens"
description: "Rotate session tokens on privilege change and expire idle sessions after 30 minutes."
status: stable
verified: { by: human:Sam Kim, at: 2026-11-01T18:30:00Z }
tags: [auth, session-management]
supersedes: docs/specs/auth-sessions.md
---

# Session tokens

Replaces the authentication sessions spec with rotating tokens.

## Requirements

- Sessions expire after 30 minutes of inactivity.
- Tokens rotate on every privilege change.
- Signing out invalidates every session for the account.
