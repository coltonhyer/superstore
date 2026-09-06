# Sequence plan

## Approved specification

- **Locator:** `docs/specs/sequence-spec.md`
- **Approved version:** the committed baseline copy

## Approach

Two layered corrections. `two.py` already imports `one.value()`, so the second
task depends on the first task's reviewed result and must not reimplement it.
Each module has a focused module-level assertion test run as
`python3 <test file>`.

## Tasks

### ONE-1: `one.value()` returns `one`

- **Spec references:** Sequence spec, the `one.py` requirement
- **Deliverable:** `one.value()` returns `one`
- **Prerequisites and order:** none
- **Relevant paths and patterns:** `one.py` only; `test_one.py` is the check
- **Completion check:** `python3 test_one.py` exits 0

### TWO-1: `two.value()` composes the reviewed `one.value()`

- **Spec references:** Sequence spec, the `two.py` requirement
- **Deliverable:** `two.value()` returns `one-two` by appending `-two` to
  `one.value()`
- **Prerequisites and order:** after ONE-1 has review evidence; consumes the
  `one.value()` interface as supplied, without changing `one.py`
- **Relevant paths and patterns:** `two.py` only; `test_two.py` is the check
- **Completion check:** `python3 test_two.py` exits 0, and `python3 test_one.py`
  still exits 0
