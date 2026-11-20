---
type: spec
title: "Session lifetimes"
description: "Issue one session token at sign-in and keep it for an absolute lifetime of 8 hours."
status: deprecated
verified: { by: human:Sam Kim, at: 2026-11-01T18:30:00Z }
tags: [auth, session-management]
---

# Session lifetimes

## Summary

Issue one session token at sign-in and keep it for an absolute lifetime of
8 hours without rotation.

## Requirements and expected behavior

- A session token never rotates during its lifetime.
- A session expires 8 hours after sign-in.
