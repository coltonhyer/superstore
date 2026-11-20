---
type: spec
title: "API protection specification"
description: "Every public API endpoint must reject unauthenticated callers and enforce the documented per-user rate limit."
status: stable
verified: { by: human:Eval Reviewer, at: 2026-10-01T12:00:00Z }
tags: [api-protection]
---

# API protection specification

Every public API endpoint must reject unauthenticated callers and enforce the
documented per-user rate limit. Reuse only repository services whose presence
is established by inspection. Verify authentication rejection and rate-limit
behavior.
