---
title: Session lifetimes
status: approved
topics: [auth, session-management]
---

# Session lifetimes

## Summary

Issue one session token at sign-in and keep it for an absolute lifetime of
8 hours without rotation.

## Requirements and expected behavior

- A session token never rotates during its lifetime.
- A session expires 8 hours after sign-in.
