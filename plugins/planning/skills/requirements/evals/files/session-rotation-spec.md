---
title: Session rotation
status: approved
topics: [auth, session-management]
supersedes: specs/session-lifetimes.md
---

# Session rotation

## Summary

Rotate session tokens on privilege change and expire idle sessions.

## Requirements and expected behavior

- A new session token is issued whenever the user's role changes, and the
  previous token stops working immediately.
- A session expires after 30 minutes without activity.
- A session expires 12 hours after sign-in regardless of activity.
