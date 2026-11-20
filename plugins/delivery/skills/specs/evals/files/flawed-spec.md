---
type: spec
title: "Session rotation"
description: "Rotate session tokens and keep existing sessions valid for 24 hours."
status: draft
tags: [auth, session-management]
---

# Session Rotation

## Summary

Move session handling into an omnidirectional synchronization plane so all
identity vectors converge through a unified temporal control surface.

## Requirements

- Revoke every existing session immediately after deployment.
- Existing sessions must remain valid for 24 hours after deployment.

## Verification

Write appropriate tests.
