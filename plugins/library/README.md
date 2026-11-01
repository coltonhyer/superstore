# Library

Keep specs, plans, handoff notes, and other agent-facing documents as
Open Knowledge Format (OKF) Markdown in `docs/`, committed with the code they
describe.

Library contains one Agent Skill, [`library`](skills/library/SKILL.md). It is
superstore's OKF encoder: it ships an unmodified copy of the OKF spec and
states only what OKF leaves open, which is the document types, locations,
extra fields, when each status is set, and how to find, write, pin, and
compare documents with ordinary file tools and the repository's version
control (Jujutsu or Git). It writes only documents of types no workflow owns,
such as notes, and leaves them uncommitted. It never builds an index or
ignores the folder; the Planning and Implementation workflows write specs,
plans, and handoff notes themselves.

## Install

### Codex

```sh
codex plugin add library@superstore
```

### Claude Code

```sh
claude plugin install library@superstore --scope user
```

### Antigravity

```sh
agy plugin install https://github.com/coltonhyer/superstore/tree/main/plugins/library
```

No build step or runtime dependency is required beyond Markdown and your
version control.

## Use

Ask your agent about the documents; the skill loads automatically:

- *"Which spec is current on auth?"*
- *"Show me the team export plan as it was at the last release."*
- *"Write a note on the CI runner capacity decision."*

## The convention

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
  folder per kind under `docs/`, named with the type's plural.
- A repository names its own folder for a type in `AGENTS.md` or `CLAUDE.md`
  at the repository root, in a sentence such as `Specs live in design/specs/.`
  A path the user names for one document wins over both.
- The filename slug matches `^[a-z0-9]+(-[a-z0-9]+)*$` and is neither `index`
  nor `log`.
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
  `deprecated`) appears on specs and plans; approval sets `stable` and writes
  `verified`. `implements` and `supersedes` take one repository path, and
  `references` takes an inline list of paths, all relative to the repository
  root. No block lists or nesting, so every field is one line.
- A document is current when its `status` is absent or `stable`. Revising a
  stable document in place sets it back to `draft`; approving a replacement
  sets the replaced document to `deprecated` unless it already is; a
  document not yet migrated (no `type` line) stays unchanged.
- A locator is a repository-relative path, written `path@revision` when pinned
  to a Jujutsu change id or Git commit.

The [skill](skills/library/SKILL.md) has the full contract and reading
workflow.

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
commands for pinned reads, diffs, and history.

To upgrade the copy:

1. Replace `okf-spec.md` and `okf-LICENSE.md` with `SPEC.md` and `LICENSE.md`
   from the newer upstream commit.
2. Update the version and commit line in `skills/library/SKILL.md` and the
   checksums in `tests/test_marketplace.py`.
3. Bump Library's version in its manifests.

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
