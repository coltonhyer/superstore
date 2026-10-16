---
title: API protection specification
status: approved
topics: [api-protection]
---

# API protection specification

Every public API endpoint must reject unauthenticated callers and enforce the
documented per-user rate limit. Reuse only repository services whose presence
is established by inspection. Verify authentication rejection and rate-limit
behavior.
