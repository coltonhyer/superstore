# Release publishing specification

**Status:** Approved

Parse a release manifest into a validated release record, persist that record,
and provide a command that publishes the persisted record. The persistence
layer consumes the parser's validated record; the command must not parse a
second copy. Verify malformed manifests are rejected, persisted records can be
loaded, and publishing receives the persisted release data.
