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

Behavioral cases live beside each skill in `evals/evals.json`. Structural and
runner tests do not call an agent:

```sh
python3 -m unittest discover -s tests
```

List the live cases, or run one case across the supported hosts:

```sh
python3 scripts/run_skill_evals.py --list
python3 scripts/run_skill_evals.py \
  --skill requirements --case 2 \
  --host codex --host claude --host agy \
  --output /tmp/planning-evals
```

Live evals are manual release checks, not CI tests. They require Docker and an
active subscription login for each selected provider. Runs use your existing
CLI logins; a refreshed token is written back only if newer. The runner builds
[`evals/Dockerfile`](../../evals/Dockerfile) automatically; the image pins Codex
`0.150.1`, Claude Code `2.1.251`, Antigravity `1.1.22`, and Jujutsu `0.44.0`.

The default subject matrix is Codex `gpt-5.6-terra`, Claude Code
`claude-sonnet-5`, and Antigravity `gemini-3.7-flash-high`, all at high
effort. Per-host `--<host>-model` and `--<host>-effort` flags override it.
The runner captures evidence and reports operational errors; it does not turn
subjective behavior into an automatic pass/fail score.

Each subject runs as a non-root user in a read-only container with only its
temporary Jujutsu repository and disposable provider state mounted writable.
The adapters disable inherited customizations through Codex's ignore flags,
Claude's `--safe-mode`, and Antigravity's non-inheriting eval agent. The
container remains the filesystem boundary because subject permission checks
are bypassed. Eval definitions, author guidance, the Superstore checkout, and
normal host credentials are not mounted.

Before retaining artifacts, the runner redacts exact credential values; a
detected leak fails the case and discards the workspace. This is
accidental-retention hygiene, not protection from transformed or exfiltrated
credentials.

Every turn retains the event stream, stderr, assistant response, file hashes,
working-copy diff, status, and commits after the fixture baseline. Antigravity
subagent output is not in its event stream, so the runner copies each
subagent's transcript and inter-agent messages from the disposable state into
the turn's provider trace before that state is deleted. Results default to a
temporary directory; use `--output` to keep them at a chosen path.

Codex `gpt-5.6-terra` uses the v2 multi-agent interface, which pinned Codex
`0.150.1` disables by default. The adapter enables v2, keeps its disposable
session state for the case, and leaves reviewer timing to Codex. Codex's JSON
stream omits v2 reviewer provenance, so the runner adds a sanitized trace from
that disposable state before deleting it. This lets a reviewer distinguish
reviewer output received by the managing agent from a spawn or wait status
alone. The adapter also disables Codex's nested command sandbox because the
outer container already supplies the filesystem boundary.

Run, observe, and review behavioral evals from a normal Codex or Claude session
using [`skill-evals`](../../.agents/skills/skill-evals/SKILL.md):

```text
Use $skill-evals to run Planning's specs/9 case on Codex and review the result.
```

The evaluator reads the complete artifacts and exact skill copies supplied to
the subject after each run. It treats case-author guidance as advisory,
separates hard workflow violations from defensible judgment, and reports
missing evidence or faulty cases instead of forcing a grade.

### Authoring cases

An eval contains a user `prompt`, a concise `expected_output`, and observable
`expectations`. These fields record the author's intent and useful review
questions; they are not exact-answer ground truth. Prefer hard workflow
boundaries and observable artifacts. Leave implementation choices and other
fuzzy judgments to the reviewer.

Put all requirements the user already knows in `prompt`. Use `replies` only
for deliberately unresolved workflow questions and approval steps:

```json
{
  "prompt": "Gather requirements. The only open decision is retention.",
  "replies": ["Retain records for 30 days.", "Approved."]
}
```

Replies are sent in order in the same native agent session. They are fixed on
purpose: if the subject repeats a resolved question or asks an unexpected one,
the harness does not improvise around the error and the criteria can expose it.
Use separate cases for materially different answer branches.

Fixtures use paths relative to the eval directory and repository workspace:

```json
{
  "source": "files/approved-spec.md",
  "target": "docs/specs/approved-spec.md",
  "state": "working"
}
```

`baseline` fixtures are committed before the subject starts. `working`
fixtures are added afterward to represent existing uncommitted work. Add
optional skill names through `skills` only when that case is meant to expose
another plugin capability, such as `read-archive`.
