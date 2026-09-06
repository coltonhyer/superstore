# Implementation

Execute an approved, preserved implementation plan through scoped verification,
review, and local recording. The approved specification remains authoritative;
a plan is not authorization to execute.

## Install

### Codex

```sh
codex plugin add implementation@superstore
```

### Claude Code

```sh
claude plugin install implementation@superstore --scope user
```

### Antigravity

```sh
agy plugin install https://github.com/coltonhyer/superstore/tree/main/plugins/implementation
```

No build step or runtime dependency is required.

## Use

Ask your agent to execute an approved implementation plan, or to perform one
part of the workflow:

- **Plan** — *"Turn this approved specification into an implementation plan."*
- **Execute** — *"Execute this approved, preserved plan."*
- **Review** — *"Review this implementation range against the approved intent."*
- **Verify** — *"Verify this change before it is recorded."*

## Skills

| Skill | What it is for |
| --- | --- |
| [`plans`](skills/plans/SKILL.md) | Turn an approved specification into a reviewed, explicitly approved, and preserved implementation plan. |
| [`implementing-plans`](skills/implementing-plans/SKILL.md) | Execute one authorized task brief or coordinate an authorized whole plan inline. |
| [`subagent-execution`](skills/subagent-execution/SKILL.md) | Coordinate one-task-at-a-time delegated execution and evidence-based recovery. |
| [`reviewing-implementation`](skills/reviewing-implementation/SKILL.md) | Review an implementation task, fix, or whole change against approved intent and evidence. |
| [`verifying-changes`](skills/verifying-changes/SKILL.md) | Return scoped, current verification evidence before a change is recorded. |

## Workflow

The default for an authorized plan is sequential delegation: one
scoped worker task, verification, local recording, independent review and
disposition, then the next task. When delegation is unavailable or inline work
is explicitly requested, `implementing-plans` follows the same gates inline.

Planning, preservation, and execution each need explicit approval. `plans`
reviews and obtains approval before it preserves a plan; `implementing-plans`
requires an approved, preserved plan, its authoritative specification, and
execution authorization. Existing unrelated changes, including pending Library
preservation, stay outside implementation recordings.

Library is optional: when available, it archives or retrieves exact approved
context; otherwise preservation remains in repository history. Debugging is
optional during evidence-based recovery. Detailed procedures and contracts stay
with their owning skills and private references.

The endpoint is local: the workflow records verified changes and reports the
result. It does not push, create a pull or merge request, merge, deploy, or
publish.

## Validation

Behavioral cases live beside each skill in `evals/evals.json`. Structural
checks do not invoke an agent:

```sh
python3 -m unittest discover -s tests
python3 scripts/run_skill_evals.py --plugin plugins/implementation --list
```

Run behavioral evaluations only with an explicitly approved host and retained
output path. Inspect the resulting evidence rather than treating a runner
invocation as an automatic pass.
