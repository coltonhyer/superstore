# Implementer brief

The supervisor gives a fresh implementer one bounded brief:

```markdown
# <task ID> implementer brief

- **Authorization and approved context:** pinned plan and spec identities
  (`<path>, blob <12-char hash>` when repository files), exact task excerpt
  plus only the applicable committed plan/spec excerpts and earlier approved
  or conservatively resolved decisions.
- **Scope and interfaces:** allowed paths, relevant repository conventions,
  starting state, unrelated work that must remain separate, and any explicitly
  authorized pre-existing fix.
- **Workspace:** assigned workspace and active-VCS instructions.
- **Required process:** read `implementing-plans`; verify before recording;
  record only the verified task change (keeping any incidental fix in its own
  separate commit); write the implementation report.
- **Report destination:** <execution-relative report path>.
- **Return boundary:** return the report and evidence to the supervisor; do not
  dispatch, review, adjudicate, update execution state, publish, or expand scope.
```

The brief is the worker's context boundary, not a request to open the full
plan, browse the repository's documents, or load the complete execution
record. Fix a pre-existing defect only when it blocks the task or is explicitly
authorized in the brief; if a blocking pre-existing fix would change observable
behavior without explicit authorization, stop and report `blocked` so the
supervisor can obtain user intent or resolve it under `Decisions for review`.
Land any incidental fix in its own separate commit (never bundled with task
commits) and call it out separately in the implementation report. A repair brief
names the finding, its evidence, the affected range, and the required
correction/check.
