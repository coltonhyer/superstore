# Greeting plan

## Approved specification

- **Locator:** `docs/specs/greeting-spec.md`
- **Approved version:** the committed baseline copy

## Approach

Correct the one greeting function in place. The existing focused test already
states the required output, so no test changes are needed.

## Tasks

### GREET-1: Greeting returns the specified string

- **Spec references:** Greeting specification, the `Hello, <name>!` requirement
- **Deliverable:** `greeting("Ada")` returns `Hello, Ada!`
- **Prerequisites and order:** none
- **Relevant paths and patterns:** `greeting.py` only; `test_greeting.py` is a
  plain module-level assertion run with `python3 test_greeting.py`
- **Completion check:** `python3 test_greeting.py` exits 0 against the changed
  `greeting.py`
