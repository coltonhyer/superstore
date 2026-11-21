---
type: plan
title: "Pin plan"
description: "Tasks that implement the pin specification."
status: stable
verified: { by: human:Eval Reviewer, at: 2026-10-01T12:00:00Z }
tags: [pin]
implements: docs/specs/pin.md
---

# Pin plan

## Approved specifications

- docs/specs/pin.md, blob 82c3887dbaea

## Approach

Uncommitted working-copy edit: switch labels to upper case and rewrite the
focused test accordingly.

## Tasks

### PIN-1: Labels use upper case

- **Spec references:** Pin specification, the label formatting requirement
- **Deliverable:** `label("ada lovelace")` returns `ADA LOVELACE`
- **Prerequisites and order:** none
- **Relevant paths and patterns:** `pin.py` and `test_pin.py`
- **Completion check:** `python3 test_pin.py` exits 0 after switching the
  assertion to upper case
