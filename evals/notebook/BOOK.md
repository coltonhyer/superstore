# Skill Evaluation Notebook

This notebook records reviewed behavioral evaluation runs.

## Interpretation

- **Supported** means the captured run provides affirmative evidence for the
  workflow. It does not claim universal model correctness.
- **Material failure** means an observable workflow contract or consequential
  behavior was violated.
- **Inconclusive** means the retained artifacts cannot establish what happened.
- **Invalid evaluation** means the fixture, guidance, or capture mechanism
  prevents a sound behavioral conclusion.
- Case-author expectations are review questions, not exact-answer ground
  truth. Defensible implementation judgment is not penalized.

Counts describe each run as originally observed. Later fixes and reruns belong
in its writeup rather than rewriting history or altering the index count.

Finding ledgers use three lifecycle states:

- **Open:** further action is expected.
- **Resolved:** a correction or evaluation decision closed the finding.
- **Accepted:** no further action is planned; the decision records why.

Follow-up runs are validation evidence attached to a finding. Give them a
separate results table only when the follow-up is itself a substantial matrix.

## Runs

`S/MF/I` means Supported / Material failure / Inconclusive. Invalid evaluations
are called out in the writeup when present.

| Date | Scope | Hosts | S/MF/I | Writeup |
|---|---|---|---|---|
| 2026-08-31 | full matrix (22×3) | codex, claude, agy | 54/10/2 | [2026-08-31-full-matrix.md](writeups/2026-08-31-full-matrix.md) |
| 2026-09-06 | implementation (34×3 staged, +24 follow-ups) | codex, claude, agy | 98/1/3 | [2026-09-06-implementation.md](writeups/2026-09-06-implementation.md) |
