---
type: plan
title: "Finish plan"
description: "Tasks that implement the finish specification."
status: stable
verified: { by: human:Eval Reviewer, at: 2026-10-01T12:00:00Z }
tags: [finish]
implements: docs/specs/finish.md
---

# Finish plan

## Approved specification

- **Locator:** `docs/specs/finish.md`

## Tasks

### FINISH-1: `finish.value()` returns `done`

- **Spec references:** Finish spec
- **Deliverable:** `finish.value()` returns `done`
- **Prerequisites and order:** none
- **Relevant paths and patterns:** `finish.py` only; `test_finish.py` is the check
- **Completion check:** `python3 test_finish.py` exits 0
