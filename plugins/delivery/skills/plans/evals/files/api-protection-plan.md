---
type: plan
title: "API protection plan"
description: "Tasks that implement the api-protection specification."
status: draft
tags: [api-protection]
implements: docs/specs/api-protection.md
---

# API protection

## Approved specifications

- docs/specs/api-protection.md, blob 987102b8f7f0

## Approach

Use the Redis cluster for authorization state and add authentication middleware.

## Tasks

### API-1: Require authentication

- **Spec references:** authentication requirement
- **Deliverable:** middleware rejects unauthenticated callers
- **Prerequisites and order:** none
- **Relevant paths and patterns:** route middleware
- **Completion check:** API test proves anonymous callers are rejected
