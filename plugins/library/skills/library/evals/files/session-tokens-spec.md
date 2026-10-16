---
title: Session tokens
status: approved
topics: [auth, session-management]
supersedes: specs/auth-sessions.md
---

# Session tokens

Replaces the authentication sessions spec with rotating tokens.

## Requirements

- Sessions expire after 30 minutes of inactivity.
- Tokens rotate on every privilege change.
- Signing out invalidates every session for the account.
