---
title: Pin plan
status: draft
topics: [pin]
implements: specs/pin.md
---

# Pin plan

## Approved specification

- **Locator:** `.agents/library/specs/pin.md`

## Approach

Unreviewed draft edit: switch labels to upper case and rewrite the test.

## Tasks

### PIN-1: Labels use upper case

- **Spec references:** none yet
- **Deliverable:** `label("ada lovelace")` returns `ADA LOVELACE`
- **Prerequisites and order:** none
- **Relevant paths and patterns:** `pin.py` and `test_pin.py`
- **Completion check:** `python3 test_pin.py` exits 0 after the test is
  rewritten for upper case
