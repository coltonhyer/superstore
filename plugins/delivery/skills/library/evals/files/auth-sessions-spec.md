---
type: spec
title: "Authentication sessions"
description: "Expire idle sessions after 8 hours and store opaque tokens server side."
status: deprecated
verified: { by: human:Sam Kim, at: 2026-11-01T18:30:00Z }
tags: [auth, session-management]
---

# Authentication sessions

## Requirements

- Sessions expire after 8 hours of inactivity.
- Session tokens are opaque random strings stored server side.
- Signing out invalidates only the current device's session.
