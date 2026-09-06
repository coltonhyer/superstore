# API protection

## Approved specification

- **Locator:** `docs/specs/api-protection.md`

## Approach

Use the Redis cluster for authorization state and add authentication middleware.

## Tasks

### API-1: Require authentication

- **Spec references:** authentication requirement
- **Deliverable:** middleware rejects unauthenticated callers
- **Prerequisites and order:** none
- **Relevant paths and patterns:** route middleware
- **Completion check:** API test proves anonymous callers are rejected
