---
type: spec
title: "Login lockout"
description: "Lock an account for 15 minutes after five failed sign-in attempts."
status: stable
verified: { by: human:Sam Kim, at: 2026-11-01T18:30:00Z }
tags: [auth, rate-limiting]
---

# Login lockout

## Requirements

- An account locks for 15 minutes after five consecutive failed sign-ins.
- A successful sign-in resets the failure count.

## Example

Lockout records are exported with this header:

```markdown
---
type: record
status: draft
tags: [audit]
---
```
