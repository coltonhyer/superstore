---
type: spec
title: "Release notes"
description: "Publish release notes within one day of every tagged release."
status: stable
verified: { by: human:Sam Kim, at: 2026-11-01T18:30:00Z }
tags: [releases, communication]
---

# Release notes

## Requirements

- Release notes are published within one day of every tagged release.
- Each entry names the pull request that made the change.

## Example

A note about login changes starts like this:

```markdown
---
type: note
status: approved
tags: [auth]
---
```
