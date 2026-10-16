---
title: Authentication sessions
status: approved
topics: [auth, session-management]
---

# Authentication sessions

## Requirements

- Sessions expire after 8 hours of inactivity.
- Session tokens are opaque random strings stored server side.
- Signing out invalidates only the current device's session.
