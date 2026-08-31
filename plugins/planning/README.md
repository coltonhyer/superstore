# Planning

Turn rough requests into approved requirements and concise, independently
reviewed specifications.

Planning contains two Agent Skills. `requirements` discovers and confirms
what done means. `specs` writes the approved result under `docs/specs`,
reviews it, and preserves it after approval. Library integration is optional.

## Install

### Codex

```sh
codex plugin add planning@superstore
```

### Claude Code

```sh
claude plugin install planning@superstore --scope user
```

### Antigravity

```sh
agy plugin install https://github.com/coltonhyer/superstore/tree/main/plugins/planning
```

No build step or runtime dependency is required.

## Use

Ask your agent to start either workflow:

- **Requirements** — *"Gather the requirements for this change."*
- **Specification** — *"Write a spec for this feature."*

You may provide partial or complete requirements up front. The workflow starts
from that context instead of asking you to repeat it.

## Skills

| Skill | What it is for |
| --- | --- |
| [`requirements`](skills/requirements/SKILL.md) | Inspect context, resolve gaps one question at a time, and obtain approval of a verifiable requirements summary. |
| [`specs`](skills/specs/SKILL.md) | Write, independently review, approve, and preserve a specification under `docs/specs`. |

## Workflow

`requirements` produces an approved summary in the conversation. `specs`
consumes that summary, writes a draft, runs one material-issues review, and
shows each finding as `Addressed`, `Elevated`, or `Dismissed` before
requesting approval. Without an approved summary, `specs` runs
`requirements` first.

## Optional Library integration

When Library is installed, `requirements` may consult relevant archived
history through `read-archive`. After spec approval, `specs` offers to
archive the document through `archiving-documentation` or keep it in
repository history. Planning continues to work when Library is absent.

## Validation

Behavioral cases live beside each skill in `evals/evals.json`. Run marketplace
checks from the Superstore checkout root:

```sh
python3 -m unittest discover -s tests
```
