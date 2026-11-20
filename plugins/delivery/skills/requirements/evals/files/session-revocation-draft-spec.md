---
type: spec
title: "Session revocation"
description: "Revoke every session for a user when that user changes their password."
status: draft
tags: [auth, session-management]
supersedes: docs/specs/session-rotation.md
---

# Session revocation

## Summary

Revoke every session for a user when that user changes their password, and
drop idle expiry.

## Requirements and expected behavior

- Changing a password revokes all of the user's sessions.
- Sessions no longer expire for inactivity.
