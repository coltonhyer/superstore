# Superstore

Archive finished Markdown docs into a verified SQLite ledger — and get them back, byte-for-byte, whenever an agent needs them.

Superstore is a plugin — for Codex, Claude Code, or Antigravity — with two Agent Skills. One moves completed Markdown out of your working tree into a searchable ledger; the other finds and restores it. Every archived doc keeps a short summary, topics, and links for easy discovery alongside a losslessly compressed copy of the original. Nothing is deleted until the write is committed and verified.

It's built to complement [superpowers](https://github.com/obra/superpowers): superpowers helps agents *produce* plans, specs, and notes; Superstore gives them a safe place to *retire and recall* that documentation instead of leaving it to clutter the repo.

Pure Python 3 standard library, no dependencies. It never guesses what to archive — you always name the file or directory.

## Install

For Codex:

```sh
codex plugin marketplace add coltonhyer/superstore
codex plugin add superstore@superstore
```

For Claude Code:

```sh
claude plugin marketplace add coltonhyer/superstore --scope user
claude plugin install superstore@superstore --scope user
```

For Antigravity:

```sh
agy plugin install https://github.com/coltonhyer/superstore
```

No build step. Requires Python 3 on your `PATH`.

## Use it

You work through your agent, not by running scripts. Just ask, naming the file or directory:

- **Archive** — *"Archive `docs/design.md` into the ledger."*
- **Recall** — *"Find the archived auth spec and restore it."*

The right skill loads automatically; the ledger is created at `.agents/ledger.db` on the first archive.

## The two skills

| Skill | What it's for |
|---|---|
| [`archiving-documentation`](skills/archiving-documentation/SKILL.md) | Archive Markdown after a work session, correct archive metadata, retry a cleanup, or resolve a merge conflict on the ledger. Writes the ledger. |
| [`read-archive`](skills/read-archive/SKILL.md) | Find, inspect, restore, or compare docs already in the ledger. Read-only. |

The reader never writes SQLite; the writer handles corrections and replay. Restoring puts recovered Markdown back in your working tree, not the database.

## How the ledger works

Everything lives in one SQLite file at `<workspace-root>/.agents/ledger.db`. Three things make it trustworthy:

- **Lossless** — content is zlib-compressed from the exact source bytes. A restore has to reproduce the original SHA-256 and byte length or it fails loudly.
- **Immutable** — archived payloads can't be edited or deleted (SQLite triggers enforce it). You can fix discovery metadata (title, summary, topics, links) later, but never the content itself.
- **Discoverable** — summaries, topics, and directed links (`implements`, `supersedes`, `references`, …) let agents browse metadata without decompressing anything.

Source files are deleted only after the archive commits and its bytes verify, and the writer re-checks each file's hash right before removing it. If cleanup can't finish, the database is still authoritative and the command tells you which files remain.

Full schema, JSON shapes, and value rules live in [schema.md](skills/archiving-documentation/references/schema.md).

## Committing the ledger

The ledger is a binary SQLite file, so Git and Jujutsu can't merge it by row. Track it as binary and ignore its scratch files:

```gitattributes
# .gitattributes
.agents/ledger.db binary
```

```gitignore
# .gitignore
.agents/ledger.db-journal
.agents/ledger.db-wal
.agents/ledger.db-shm
```

If two branches archive in parallel and collide, don't reach for a merge driver — use the writer's `replay` workflow ([replay.md](skills/archiving-documentation/references/replay.md)) to combine the insert-only runs.

## Layout

```
skills/
  archiving-documentation/   # writer: SKILL.md, scripts/archive.py, references, evals
  read-archive/              # reader: SKILL.md, scripts/read.py, references, evals
tests/test_ledger.py         # ledger test suite (unittest)
.codex-plugin/plugin.json    # Codex manifest
.claude-plugin/              # Claude Code manifest + marketplace.json
plugin.json                  # Antigravity manifest
```

## Tests

The suite is pure `unittest` — no dependencies:

```sh
python3 -m unittest discover -s tests
```
