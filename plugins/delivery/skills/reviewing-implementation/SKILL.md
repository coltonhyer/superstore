---
name: reviewing-implementation
description: Review a scoped implementation task, whole change set, or fix range against approved intent and evidence without changing code or deciding dispositions.
---

# Reviewing Implementation

Review a scoped task change, whole change set, or fix range using the approved
intent and available verification evidence. Read the
[review contract](references/review-contract.md) and
[the shared review loop](../../references/review-loop.md) before returning a
result. Every reviewer starts with fresh context and no parent conversation
history (for example, `fork_turns: "none"` where supported).

Inspect implementation and tests for correctness, missing or extra behavior,
unsupported assumptions, fragile design, and material maintenance problems.
Classify any addition beyond approved requirements or intent as *serves the
ask*, *unnecessary*, or *conflicts*, and flag additions that change observable
behavior or delivered scope as requiring explicit user intent (or `Decisions for
review` in autonomous mode). Test review considers assertion quality, meaningful
branch and boundary coverage, failure behavior, mocks that hide the behavior
under test, brittleness, and genuine redundancy. A missing-coverage finding must
name the behavior and defect that could escape; similar tests protecting
distinct contracts are not automatically redundant.

Inspect beyond a single file diff when a concrete question requires it,
including:

- **Moved symbols:** search for and flag any leftover re-export shim or
  importer still referencing a moved symbol's old path, except shims explicitly
  required by an approved compatibility requirement.
- **User-facing documentation claims:** inspect backing code to verify factual
  claims made by changed user-facing documentation.
- **Incidental pre-existing fix separation:** inspect commit boundaries to
  verify that any incidental pre-existing fix landed in its own separate commit
  (not tangled with feature or task commits) and is called out separately for
  the handoff.

Run focused additional checks when existing evidence leaves a meaningful doubt;
do not blindly repeat every implementer test. Rounds 1 and 2 review the full task
or whole change; Round 3 onward (except a full-change final round after a
step-back redesign) reviews the diff since the prior round, prior findings and
dispositions, and fixed defect classes, allowing targeted reads to verify
class-wide fixes, moved symbols, user-facing doc claims, or commit separation. A
caller-supplied fix review checks prior findings, the correction range, and
correction evidence for those findings and newly introduced breakage without
turning into an unrelated fresh review. Whole-change review additionally examines
cross-task interactions and approved-spec coverage.

Leave the implementation and repository history unchanged, and never request
appeasement prose that a human reader does not need. Return structured findings
(`Blocking` or `Non-blocking`, each naming a one-line defect class and the
specific instance, evidence, impact, smallest adequate correction, `Needs user
intent`, and scope-fit label for out-of-scope additions), verification gaps, or
an explicit `No material findings` result. Do not fix code, declare a task
complete, or assign a finding disposition; the managing agent owns `Addressed`,
`Elevated`, `Dismissed` (with exact checkable evidence), and `Declined`
(`Non-blocking` only).
