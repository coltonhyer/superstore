# Text plan

## Approved specification

- **Locator:** `docs/specs/text-spec.md`
- **Approved version:** the committed baseline copy

## Approach

Two independent one-function corrections. Each module has a focused
module-level assertion test that already states the required behavior, run as
`python3 <test file>`.

## Tasks

### TEXT-1: Slugs normalize whitespace and case

- **Spec references:** Text specification, the slug requirement
- **Deliverable:** `slug(" Ada ")` returns `ada`
- **Prerequisites and order:** none
- **Relevant paths and patterns:** `slug.py` only; `test_slug.py` is the check
- **Completion check:** `python3 test_slug.py` exits 0

### TEXT-2: Summaries use the `count=<number>` format

- **Spec references:** Text specification, the summary requirement
- **Deliverable:** `summary(3)` returns `count=3`
- **Prerequisites and order:** none; independent of TEXT-1
- **Relevant paths and patterns:** `summary.py` only; `test_summary.py` is the
  check
- **Completion check:** `python3 test_summary.py` exits 0
