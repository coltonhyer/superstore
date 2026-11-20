---
type: spec
title: "Legacy login"
description: "Lock an account for one hour after three failed sign-in attempts."
status: deprecated
tags: [auth]
---

# Legacy login

Replaced by the login lockout spec.

## Requirements

- An account locks for one hour after three consecutive failed sign-ins.

## Example

The old export header looked like this:

```markdown
---
type: record
status: stable
tags: [auth]
---
```
