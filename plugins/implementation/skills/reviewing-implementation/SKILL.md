---
name: reviewing-implementation
description: Review a scoped implementation task, whole change set, or fix range against approved intent and evidence without changing code or deciding dispositions.
---

# Reviewing Implementation

Review a scoped task change, whole change set, or fix range using the approved
intent and available verification evidence. Read the applicable
[review contract](references/review-contract.md) before returning a result.

Inspect implementation and tests for correctness, missing or extra behavior,
unsupported assumptions, fragile design, and material maintenance problems.
Test review considers assertion quality, meaningful branch and boundary
coverage, failure behavior, mocks that hide the behavior under test,
brittleness, and genuine redundancy. A missing-coverage finding must name the
behavior and defect that could escape; similar tests protecting distinct
contracts are not automatically redundant.

Inspect beyond a supplied diff only when a concrete question requires it. Run
focused additional checks when existing evidence leaves a meaningful doubt; do
not blindly repeat every implementer test. A fix review checks reported defects
and breakage introduced by the correction. Whole-change review additionally
examines cross-task interactions and approved-spec coverage.

Leave the implementation and repository history unchanged. Return findings
with evidence and impact, verification gaps, or an explicit no-material-
findings result. Do not fix code, declare a task complete, or assign a finding
disposition; the managing agent owns `Addressed`, `Elevated`, and `Dismissed`.
