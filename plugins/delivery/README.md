# Delivery

Take requests from rough intent through approved requirements, independently
reviewed specifications and implementation plans, verified and reviewed local
execution, and Open Knowledge Format (OKF) documents committed in `docs/`.

Delivery bundles eight Agent Skills covering the full local delivery lifecycle
and its repository document conventions. The approved specification remains
authoritative throughout; a plan is not authorization to execute, and the
workflow ends locally without pushing or publishing.

## Install

### Codex

```sh
codex plugin add delivery@superstore
```

### Claude Code

```sh
claude plugin install delivery@superstore --scope user
```

### Antigravity

```sh
agy plugin install https://github.com/coltonhyer/superstore/tree/main/plugins/delivery
```

No build step or runtime dependency is required beyond Markdown and your
version control (Jujutsu or Git).

## Use

Ask your agent to start any part of the workflow; the relevant skill loads
automatically:

- **Requirements** — *"Gather the requirements for this change."*
- **Specification** — *"Write a spec for this feature."*
- **Plan** — *"Turn this approved specification into an implementation plan."*
- **Execute** — *"Execute this approved plan."*
- **Review** — *"Review this implementation range against the approved intent."*
- **Verify** — *"Verify this change before it is recorded."*
- **Library** — *"Which spec is current on auth?"*, *"Show me the team export
  plan as it was at the last release."*, or *"Write a note on the CI runner
  capacity decision."*

You may provide partial or complete requirements up front. The workflow starts
from that context instead of asking you to repeat it.

## Skills

| Skill | What it is for |
| --- | --- |
| [`requirements`](skills/requirements/SKILL.md) | Inspect context, resolve gaps one question at a time, and obtain approval of a verifiable requirements summary. |
| [`specs`](skills/specs/SKILL.md) | Write, independently review, approve, and commit a specification, by default under `docs/specs/`. |
| [`plans`](skills/plans/SKILL.md) | Turn an approved specification into a reviewed, explicitly approved, and committed implementation plan. |
| [`implementing-plans`](skills/implementing-plans/SKILL.md) | Execute one authorized task brief or coordinate an authorized whole plan inline. |
| [`subagent-execution`](skills/subagent-execution/SKILL.md) | Coordinate one-task-at-a-time delegated execution and evidence-based recovery. |
| [`reviewing-implementation`](skills/reviewing-implementation/SKILL.md) | Review an implementation task, fix, or whole change against approved intent and evidence. |
| [`verifying-changes`](skills/verifying-changes/SKILL.md) | Return scoped, current verification evidence before a change is recorded. |
| [`library`](skills/library/SKILL.md) | Find, read, pin, and compare Open Knowledge Format documents in `docs/`, and write notes and other types no workflow owns. |

## Workflow

Interactive human approval and separate execution authorization are strictly
the default at every gate (`requirements`, `specs`, `plans`, and execution);
ordinary multi-stage prompts (*"take this spec to code"*, *"preserve"*,
*"save"*, *"commit"*) never waive them. Explicitly authorized autonomous
execution (`process:delivery-autonomous`) skips human approval only where
explicitly opted in, never waives independent agent review, halts immediately
with zero self-review fallback when a gate does not converge or an independent
reviewer is unavailable, fails, or returns unusable output, surfaces intent
and out-of-scope choices under `Decisions for review` (and internal trade-offs
under `Tactical decisions`), and still ends locally without pushing or
publishing.

`requirements` inspects repository context, resolves gaps one question at a
time (recording any internal choice with its trade-off), and produces an
approved summary in the conversation. `specs` consumes that summary (or runs
`requirements` first when missing; vetted approved requirements supplied with
an autonomous opt-in skip elicitation, while contradictory or incomplete
requirements halt), resolves the living domain spec in place (creating a new
spec only when no `current` spec covers the capability, or splitting with
`supersedes`), runs parallel two-reviewer independent review (**Reviewer A**
against requirements and spec; **Reviewer B** against spec and code) in a
bounded 3-round loop plus a step-back final round, and assigns each finding one
of four checkable dispositions (`Addressed`, `Elevated`, `Dismissed` with
checkable evidence, or `Declined` for `Non-blocking` only) before requesting
approval (or promoting after a clean independent round in autonomous mode).

`plans` requires committed, clean, `status: stable` repository spec(s) (an
explicit user approval exception applies to committed and clean `type: spec`
files without a `status` line, frontmatterless files, or non-repository specs;
`draft`, `deprecated`, and dirty or uncommitted specs are rejected and routed
back through `specs`). It uses the spec's slug for one living spec with no
earlier plan and a change-scoped slug for multi-spec plans or living specs
with earlier plans, writes scalar or inline-list `implements` and optional
`supersedes`, pins committed specs in `## Approved specifications` as
`<path>, blob <12-char hash>` (with a two-step mechanical refresh on `stable`
plans when only cited spec blob hashes change), runs the bounded review loop
and four dispositions, and obtains explicit approval before setting
`status: stable`, writing `verified`, deprecating `supersedes` targets, and
committing strictly the changed files. Plan creation is not authorization to
execute.

`implementing-plans` and `subagent-execution` require a committed, clean,
`status: stable` repository plan (or explicitly approved non-repository plan),
every implemented repository spec committed and clean (`status: stable`, or
explicitly approved if without `status` or `type: spec` frontmatter), and
separate execution authorization. When an interactive gate encounters a
`status: stable` spec or plan verified only by a non-`human:` actor
(`machine-confirmed`, such as `process:delivery-autonomous`), it routes
confirmation through `specs` or `plans` without re-review when content is
unchanged (a `status: stable` document with no `verified` line is **not**
machine-confirmed).

The default for an authorized plan is sequential delegation: one scoped worker
task, verification via `verifying-changes` before recording, local recording,
independent task review via `reviewing-implementation` (with optional
`Non-blocking` review code edits also freshly verified and recorded) and
verified fixes before advancing, then whole-change review and verification. When
delegation is unavailable or inline work is explicitly requested,
`implementing-plans` follows the same gates inline; debugging is optional
during evidence-based recovery. `reviewing-implementation` also checks moved
symbols for leftover shims or stale importers, user-facing documentation claims
against backing code, and commit separation for incidental pre-existing fixes
(allowed only when blocking or explicitly authorized, and always landed in
their own separate commit); unrelated working-copy changes stay outside
implementation recordings. At successful whole-plan handoff, execution writes
`docs/handoffs/<plan-slug>.md` (or `-2`, `-3`, ... on collision) with `Plan`
and `Specs` blob citations, a `Change` line (without commit hashes, Jujutsu
change IDs, revision ranges, or scratch paths), and the six fixed headings
(`Whole-change checks`, `Review outcomes and dispositions`,
`Incidental fixes`, `Limitations`, `Decisions for review`,
`Tactical decisions`), committing it as its own separate revision before
cleaning up only that execution's scratch.

The endpoint is local: the workflow records verified changes and reports the
result. It does not push, create a pull or merge request, merge, deploy, or
publish.

## Documents

[`library`](skills/library/SKILL.md) is Superstore's OKF encoder: it ships an
unmodified copy of the OKF spec and states only what OKF leaves open, which is
the document types, locations, extra fields, when each status is set, and how
to find, write, pin, and compare documents with ordinary file tools and the
repository's version control (Jujutsu or Git). It writes only documents of
types no workflow owns, such as notes, and leaves them uncommitted. It never
builds an index or ignores the folder; `specs`, `plans`, and whole-plan
execution write specs, plans, and handoff notes themselves.

```text
docs/
  specs/<slug>.md
  plans/<slug>.md
  handoffs/<slug>.md
  notes/<slug>.md
  <another-plural-kind>/<slug>.md
```

- Each document is an OKF concept. Its `type` is `spec`, `plan`, `handoff`, or
  another lowercase slug such as `note`. By default it lives in one flat
  folder per kind under `docs/`, named with the type's plural. At successful
  whole-plan handoff, execution writes a `type: handoff` note to
  `docs/handoffs/<plan-slug>.md` (appending `-2`, `-3`, and so on if a prior
  handoff for that slug already exists).
- A repository names its own folder for a type in `AGENTS.md` or `CLAUDE.md`
  at the repository root, in a sentence such as `Specs live in design/specs/.`
  A path the user names for one document wins over both.
- The filename slug matches `^[a-z0-9]+(-[a-z0-9]+)*$` and is neither `index`
  nor `log`. Point-in-time standalone notes in the notes folder (default
  `docs/notes/`) may prefix filenames with `YYYY-MM-DD-` (which fits the slug
  rule); living specs keep undated domain slugs.
- Each document starts with a frontmatter block, one field per line, in this
  order:

  ```markdown
  ---
  type: plan
  title: "Authentication sessions plan"
  description: "Three tasks that add token rotation and the idle-session timeout."
  status: stable
  verified: { by: human:Sam Kim, at: 2026-11-01T18:30:00Z }
  tags: [auth, session-management]
  implements: docs/specs/auth-sessions.md
  ---
  ```

  `type`, `title`, `description`, and `tags` are always present, and `title`
  and `description` are in double quotes. `status` (`draft`, `stable`, or
  `deprecated`) appears on specs and plans; drafts are written with
  `status: draft`. Approval (explicit human or explicitly authorized autonomous
  clean review) sets `status: stable` and writes `verified`: explicit human
  approval writes `verified: { by: human:<approver>, at: <approval time> }`
  from the user name version control is configured with (omitting `verified`
  with a note in the report when unset, empty, or containing `,` `[` `]` `{` `}`
  `#` `:`), and explicitly authorized autonomous clean review writes
  `verified: { by: process:delivery-autonomous, at: <approval time> }` (OKF
  `machine-confirmed`, never `human:`). Approving a document with `supersedes`
  iterates over every listed target across scalar and inline-list forms:
  setting each migrated target to `deprecated` unless it already is, leaving
  unmigrated targets (no frontmatter or no `type` line) unchanged and reporting
  them, ignoring missing targets, and deprecating a split spec only once the
  replacement set is complete and approved, then committing strictly the files
  that step changed. `implements` takes one repository path or an inline list
  (`[path-a, path-b]`) for multi-spec plans, `supersedes` takes one repository
  path or an inline list (`[path-a, path-b]`) for merges and splits, and
  `references` takes an inline list of paths — all relative to the repository
  root without a leading slash. No block lists or nesting, so every field is
  one line.
- A document is current when its `status` is absent or `stable`. Revising a
  stable document in place flips it back to `draft` and removes `verified`
  until it is approved again, except for a mechanical blob-citation-only
  refresh on a `stable` plan whose tasks and content are unchanged, which
  commits without flipping `status` to `draft` or re-requesting approval.
- A locator is a repository-relative path, pinned as `<path>`, blob
  `<12-char hash>` (computed only from committed revisions) for committed plans
  and handoffs, or `path@revision` for ad-hoc pinned reads via a Jujutsu change
  or commit id or Git commit.
- `library` is optional for discovery in the planning and execution skills:
  `requirements` may load `library` to find current documents on a subject, or
  filter frontmatter directly without it.

The [`library` skill](skills/library/SKILL.md) has the full contract and
reading workflow.

Maintainer note: the skill's frontmatter extractor runs on any POSIX `awk` and
strips Windows line endings. `find` is there so a missing folder is reported
and skipped (`awk` alone stops at the first path it cannot open), and `-H`
makes it follow a document folder that is a symbolic link.

## The copied spec

`skills/library/references/okf-spec.md` is a byte-for-byte copy of OKF v0.2
(`SPEC.md`) from `https://github.com/GoogleCloudPlatform/open-knowledge-format` at commit
`ad30107c31c06aec8a7d5636e0d1058118604e6f`, and
`skills/library/references/okf-LICENSE.md` is that commit's Apache 2.0
`LICENSE.md`. The copy works offline and identically on every host, and it
cannot change underneath readers. Nothing here claims that `docs/` as a whole
is an OKF bundle.

`skills/library/references/pin-and-compare.md` holds the Jujutsu and Git
commands for computing and reading 12-character committed Git blob hashes,
pinned reads, diffs, and history.

To upgrade the copy:

1. Replace `okf-spec.md` and `okf-LICENSE.md` with `SPEC.md` and `LICENSE.md`
   from the newer upstream commit.
2. Update the version and commit line in `skills/library/SKILL.md` and the
   checksums in `tests/test_marketplace.py`.
3. Bump Delivery's version in its manifests.

## Why plain files

- Files rather than SQLite: version control already gives exact bytes,
  immutability, and history for text.
- In the repository rather than a sidecar: the commit graph relates each
  document state to the commits made while it was current.

## Migrating

Every migration targets `docs/<kind>/<slug>.md` with the OKF frontmatter
above. There is no migration script; migrate by hand or ask an agent to.

### From Library 0.2.0

Library 0.2.0 kept documents at `.agents/library/<kind>/<slug>.md` (`specs/`,
`plans/`, `notes/`) with the fields `title`, `status` (`draft` or `approved`),
`topics`, and library-relative `implements`, `supersedes`, and `references`
paths. Move each file, then rewrite its frontmatter. History from before the
move stays at the old path. The rewrite is:

- Add `type`: `spec` for `specs/`, `plan` for `plans/`. A file in `notes/`
  written by Implementation 0.3.0's whole-plan execution is a handoff note:
  `type: handoff` in `docs/handoffs/`. Any other note is `type: note` in
  `docs/notes/`.
- Quote `title` and add a one-sentence quoted `description`.
- Map `status: approved` to `stable`. Add no `verified` line: who approved
  the document and when was never recorded, and a migration does not invent
  them. `draft` stays `draft`.
- Rename `topics` to `tags`.
- Prefix `implements`, `supersedes`, and `references` paths with `docs/` so
  they are repository paths. A link to a note that became a handoff note
  points into `docs/handoffs/`, not `docs/notes/`.
- Currency was computed from `supersedes` chains. Set `status: deprecated` on
  each document that an approved document names in `supersedes`.

### From a Library 0.1.0 ledger

Library 0.1.0 archived documents into a SQLite ledger at `.agents/ledger.db`.

1. Open the database with any SQLite client and read its schema.
2. For each document, decompress its zlib-compressed content payload to
   recover the exact Markdown.
3. Read the topics and links tables for each document. A document is current
   when no `document_links` row with relation `supersedes` targets it; migrate
   only current documents.
4. Write one file per current document to `docs/<folder>/<slug>.md`, where
   `kind` maps to the plural folder (`spec` to `specs/`, `plan` to `plans/`,
   `notes` to `notes/`). Build the OKF frontmatter from its title, topics, and
   links: `type` from the kind (`note` for `notes`), a quoted `title`, a
   quoted one-sentence `description`, `tags` from the topics, and
   `implements` and `references` as repository paths. The ledger has no
   status, so give specs and plans `status: stable` because every archived
   document was final; do not copy `supersedes` links, since superseded
   revisions are not migrated.
5. Delete `.agents/ledger.db` and its `.gitignore` and `.gitattributes`
   entries, then commit.

### Documents written without frontmatter

Planning 0.2.0 wrote specs under `docs/specs/` and Implementation 0.2.0 wrote
plans under `docs/plans/`, both without frontmatter. Their file names already
fit the slug rule, so they gain frontmatter in place: add `type`, a quoted
`title` and `description`, `status` (`stable` for an approved document, `draft`
otherwise), and `tags`, plus `implements` for a plan. The library skill
reports any Markdown file in a document folder that still has no `type` line
as not yet migrated.

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
  --output /tmp/delivery-evals
```

`--plugin` selects the plugin whose cases run (default `plugins/delivery`) and
may repeat to run several plugins in one run, as long as no skill name is
shared between them. Hosts run side by side, and each host runs up to four of
its cases at once, starting them in case order. A host's first case runs
alone; a later case joins the others only while the host's login stays valid
until ten minutes past the case's worst end, so a token refresh never races
between sessions. A host whose login expiry cannot be read, whose refresh rule
is not confirmed, or that refreshes during a parallel case, falls back to one
case at a time and the run says so.

Live evals are manual release checks, not CI tests. They require Docker and an
active subscription login for each selected provider. Runs use your existing
CLI logins; a refreshed token is written back only if newer. The runner builds
[`evals/Dockerfile`](../../evals/Dockerfile) automatically; the image pins Codex
`0.155.0`, Claude Code `2.1.251`, Antigravity `1.4.0`, and Jujutsu `0.44.0`.

The default subject matrix is Codex `gpt-5.6-terra`, Claude Code
`claude-sonnet-5`, and Antigravity `gemini-3.8-flash-high`, all at high
effort. Per-host `--<host>-model` and `--<host>-effort` flags override it.
These defaults are already mid-tier, so cases that expect the managing agent
to choose a cheaper reviewer or worker only exercise that choice when the
subject runs on the host's strongest model. Judging those cases needs each
host's tier order, which the artifacts do not record. Strongest first, it is
currently `gpt-6-astra`, `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna` on
Codex and `fable`, `opus`, `sonnet`, `haiku` on Claude Code.
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
`0.155.0` disables by default. The adapter enables v2, keeps its disposable
session state for the case, and leaves reviewer timing to Codex. Codex's JSON
stream omits v2 reviewer provenance, so the runner adds a sanitized trace from
that disposable state before deleting it. This lets a reviewer distinguish
reviewer output received by the managing agent from a spawn or wait status
alone. The adapter also disables Codex's nested command sandbox because the
outer container already supplies the filesystem boundary.

Run, observe, and review behavioral evals from a normal Codex or Claude session
using [`skill-evals`](../../.agents/skills/skill-evals/SKILL.md):

```text
Use $skill-evals to run Delivery's specs/9 case on Codex and review the result.
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
another skill capability, such as `library`.
