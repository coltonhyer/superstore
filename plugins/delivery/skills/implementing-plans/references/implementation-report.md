# Implementation report contract

The assigned implementer writes this report for the supervisor. It describes
implementation and evidence; it does not approve work or update execution
state.

```markdown
# <task ID> implementation report

- **Approved context:** pinned plan and spec identities (`<path>, blob <12-char hash>` when repository files), task brief/excerpts, and execution authorization.
- **Scope:** assigned paths and any preserved unrelated working-copy changes.
- **Changes:** implemented behavior and relevant paths.
- **Incidental fixes:** separate-commit blocking or explicitly authorized pre-existing fixes (with their own recorded revision and verification), or `none`.
- **Recorded result:** exact revision identifier or range; `not recorded` with the recording failure when applicable.
- **Verification:** exact commands or observations, actual results, and the state/revision they apply to.
- **Concerns and gaps:** failed, stale, unavailable, or unrun checks; scope or context uncertainty.
- **Status:** `reported for review`, `blocked`, or `incomplete` — never `complete` solely from this report.
- **Next action:** the concrete supervisor decision, review, correction, or recovery needed.
```

Fix a pre-existing defect only when it blocks the task or is explicitly
authorized in the brief. Because a delegated worker cannot obtain user intent
or record autonomous `Decisions for review` itself, stop and report `blocked`
whenever a blocking pre-existing fix would change observable behavior without
explicit authorization. Land any incidental fix in its own separate commit
(never bundled with task commits) and call it out under `Incidental fixes`.

Use `reported for review` only after verification and successful recording.
When verification or recording fails, preserve the recoverable state and say
why completion cannot be claimed.
