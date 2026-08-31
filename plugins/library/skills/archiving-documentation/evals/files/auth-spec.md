# Authentication Session Design

Use opaque session identifiers stored in secure, HTTP-only cookies. Keep session
state on the server and rotate the identifier after privilege changes.

The design applies to browser authentication. API-token authentication is
outside this document.

## Decisions

- Revoke sessions server-side.
- Expire idle sessions after 30 minutes.
- Preserve an audit event when a session is revoked.
