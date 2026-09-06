# Implementation review contract

## Inputs and scope

Accept one of these review scopes with applicable approved intent and available
verification evidence:

- **Task:** the assigned change and its task boundaries.
- **Whole change:** the complete assembled change set and interactions that a
  task review cannot establish.
- **Fix range:** prior findings, the correction range, and evidence for the
  correction. Check those findings and newly introduced breakage; do not turn
  it into an unrelated fresh review.

Identify the reviewed revision or working-copy state, paths, intent, and any
scope or evidence limitation before evaluating it. Treat an implementer claim
as a lead, not evidence.

## Review procedure

Compare the actual change and relevant tests with approved intent. Check for
missing or extra behavior, unsupported assumptions, fragile design, and
material maintenance risk. Test review examines assertions, meaningful branch,
boundary, and failure coverage, deceptive mocks, brittleness, and redundancy.

Name the behavior and escaping defect for each missing-coverage concern. Flag
only genuinely redundant checks; retain similar tests when they protect
different contracts. Inspect code outside the supplied diff or run an
additional focused check only to answer a concrete doubt. Do not demand an
arbitrary coverage target or repeat all implementer checks by default.

Do not edit implementation, alter repository history, mark progress complete,
or adjudicate findings.

## Result

Return either **No material findings** with reviewed scope/state and remaining
verification gaps, or a result containing:

- **Reviewed:** scope, code state, approved intent, and evidence considered.
- **Findings:** stable identifier, material issue, supporting evidence, impact,
  and a concrete focused check when one would resolve a doubt.
- **Verification gaps:** unavailable, stale, incomplete, or otherwise
  insufficient evidence, distinct from code findings.

The managing agent assigns every material finding exactly one disposition:
`Addressed`, `Elevated`, or `Dismissed`, with evidence. A known material defect
is never dismissed merely because earlier attempts were exhausted.
