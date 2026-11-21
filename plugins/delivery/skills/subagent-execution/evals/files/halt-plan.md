---
type: plan
title: "Halt badge plan"
description: "One task implementing `badge` per the halt badge specification."
status: stable
verified: { by: process:delivery-autonomous, at: 2026-10-01T12:00:00Z }
tags: [halt]
implements: docs/specs/halt.md
---

# Halt badge plan

## Approved specifications

- docs/specs/halt.md, blob 26c79dbe6d93

## Tasks

### HALT-1: Implement `badge`

- **Spec references:** Halt badge spec
- **Deliverable:** `badge("ok")` returns `"[ok]"`
- **Prerequisites and order:** none
- **Relevant paths and patterns:** `halt.py` only; `test_halt.py` is the check
- **Completion check:** `python3 test_halt.py` exits 0
