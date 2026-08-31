# Library

Archive finished Markdown documentation into a verified SQLite ledger and restore it byte-for-byte whenever an agent needs it.

Library contains two Agent Skills. One moves completed Markdown out of your working tree into a searchable ledger; the other finds and restores it. Every archived document keeps a short summary, topics, and links alongside a losslessly compressed copy of the original. Nothing is deleted until the write is committed and verified.

Library uses only the Python 3 standard library. It never guesses what to archive—you always name the file or directory.

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

No build step is required. Python 3 must be available on your `PATH`.

## Use

Work through your agent rather than running the scripts directly. Ask for the operation and name the file or directory:

- **Archive** — *"Archive `docs/design.md` into the ledger."*
- **Recall** — *"Find the archived auth spec and restore it."*

The appropriate skill loads automatically. The ledger is created at `.agents/ledger.db` on the first archive.

## Skills

| Skill | What it's for |
| --- | --- |
| [`archiving-documentation`](skills/archiving-documentation/SKILL.md) | Archive Markdown after a work session, correct archive metadata, retry cleanup, or resolve a ledger merge conflict. Writes the ledger. |
| [`read-archive`](skills/read-archive/SKILL.md) | Find, inspect, restore, or compare documents already in the ledger. Read-only. |

The reader never writes SQLite; the writer handles corrections and replay. Restoring puts recovered Markdown back in your working tree, not the database.

## How the ledger works

Everything lives in `<workspace-root>/.agents/ledger.db`:

- **Lossless** — Content is zlib-compressed from the exact source bytes. A restore must reproduce the original SHA-256 and byte length.
- **Immutable** — SQLite triggers prevent archived payloads from being edited or deleted. Discovery metadata can be corrected later.
- **Discoverable** — Summaries, topics, and directed links let agents browse metadata without decompressing documents.

Source files are deleted only after the archive commits and its bytes verify. The writer rechecks each file's hash immediately before removing it. If cleanup cannot finish, the database remains authoritative and the command reports which files remain.

Full schema, JSON shapes, and value rules live in [schema.md](skills/archiving-documentation/references/schema.md).

## Committing the ledger

The ledger is a binary SQLite file, so Git and Jujutsu cannot merge it by row. Track it as binary and ignore its scratch files:

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

If two changes archive in parallel and collide, use the writer's [`replay` workflow](skills/archiving-documentation/references/replay.md) to combine the insert-only runs.

## Tests

From the Superstore checkout root:

```sh
python3 -m unittest discover -s plugins/library/tests
```
