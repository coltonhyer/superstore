---
type: spec
title: "API tokens"
description: "Scope third-party API tokens by workspace role and read/write permissions."
status: stable
verified: { by: human:Sam Kim, at: 2026-11-02T09:15:00Z }
tags: [auth, tokens, permissions]
supersedes: docs/specs/token-policy-v2.md
---

# API tokens

## Requirements

- Third-party API tokens carry explicit workspace role scopes.
- Read-only tokens cannot invoke mutating endpoints.
