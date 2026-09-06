---
name: verifying-changes
description: Verify an explicit implementation change against its intended behavior and return current, scoped evidence without changing the implementation or recording completion.
---

# Verifying Changes

Use this procedure for standalone verification, before an implementer records a
change, and for the assembled result after review fixes. It returns evidence to
the caller; it does not fix code, commit, or mark a task complete.

## Establish the subject

Start with the approved intent and an explicit change scope. Inspect the actual
diff and repository state, including uncommitted work. State when either input
is incomplete and limit the conclusion accordingly.

Compare the intended behavior to the actual change, not merely to the
implementer's summary. Select checks that fit the surface: behavioral or
regression tests for code, validation for configuration, and structural or
behavioral evaluation for documentation and skills. A passing happy-path test
does not establish omitted boundary, failure, or integration behavior.

Run existing, focused checks where they answer an open question. Do not rerun
every prior check by default. Results apply only to the code state they tested:
after a relevant edit, rerun or report the earlier result as stale. If a
required tool or check is unavailable, record the gap; it is not success.

## Return evidence

Report:

- **Intent and scope:** checked behavior, revision or working-copy state, and
  relevant paths.
- **Established:** each behavior supported by current evidence.
- **Checks:** exact commands or observations, results, and the state each
  applies to.
- **Failures and gaps:** failed, untested, stale, or unavailable checks and
  the resulting uncertainty.
- **Conclusion:** only what the evidence supports; say when correctness remains
  unestablished.

Leave the implementation and repository history unchanged. Return control to
the caller to address failures, decide dispositions, record changes, or declare
completion. For final verification, retain task evidence that still applies and
rerun checks invalidated by later changes, unresolved concerns, or review fixes.
