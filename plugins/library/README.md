# Library

Keep specs, plans, notes, and other agent-facing documents as plain Markdown
under `.agents/library/`, committed with the code they describe.

Library contains one Agent Skill, [`library`](skills/library/SKILL.md). It
teaches agents the convention and how to find, read, pin, and compare
documents with ordinary file tools and the repository's version control
(Jujutsu or Git). It never writes documents, builds an index, or ignores the
folder; the workflows that produce specs and plans write them.

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
- *"Where should a new decision record go?"*

## The convention

```text
.agents/library/
  specs/<slug>.md
  plans/<slug>.md
  notes/<slug>.md
  <another-plural-kind>/<slug>.md
```

- The folder is the document's kind, named with a plural lowercase slug. The
  filename slug (`^[a-z0-9]+(-[a-z0-9]+)*$`) is its identity.
- The folder is committed and never ignored.
- Each document starts with a frontmatter block, one field per line, in this
  order:

  ```markdown
  ---
  title: Authentication sessions plan
  status: approved
  topics: [auth, session-management]
  implements: specs/auth-sessions.md
  ---
  ```

  `title` and `topics` are always present. `status` (`draft` or `approved`)
  appears on specs and plans only; other kinds are final when written.
  `implements` and `supersedes` take one path, and `references` takes an inline
  list of paths, all relative to `.agents/library/`. No other fields, block
  lists, nesting, or quoting, so every field is one grep-able line.
- A document is current when it is not a draft and no non-draft document names
  it in `supersedes`. Revisions are in-place edits; `supersedes` is only for a
  differently named replacement.
- A locator is a repository-relative path, written `path@revision` when pinned
  to a Jujutsu change id or Git commit.

The [skill](skills/library/SKILL.md) has the full contract and reading
workflow.

## Why plain files

- Files rather than SQLite: version control already gives exact bytes,
  immutability, and history for text.
- In the repository rather than a sidecar: the commit graph relates each
  document state to the commits made while it was current.
- Under `.agents/` rather than `docs/`: historical specs would pollute
  present-tense documentation and any index built on it.

## Migrating a 0.1.0 ledger

Library 0.1.0 archived documents into a SQLite ledger at `.agents/ledger.db`.
There is no migration script; migrate by hand or ask an agent to:

1. Open the database with any SQLite client and read its schema.
2. For each document, decompress its zlib-compressed content payload to
   recover the exact Markdown.
3. Read the topics and links tables for each document. A document is current
   when no `document_links` row with relation `supersedes` targets it; migrate
   only current documents.
4. Write one library file per current document to
   `.agents/library/<folder>/<slug>.md`, where `kind` maps to the plural
   folder (`spec` to `specs/`, `plan` to `plans/`, `notes` to `notes/`).
   Build frontmatter from its title, topics, and links. The ledger has no
   status, so give specs and plans `status: approved` because every archived
   document was final. `implements` and `references` links become
   library-relative paths; do not copy `supersedes` links, since superseded
   revisions are not migrated.
5. Delete `.agents/ledger.db` and its `.gitignore` and `.gitattributes`
   entries, then commit.
