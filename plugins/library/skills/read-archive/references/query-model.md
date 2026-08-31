# Ledger Query Model

## Commands

| Need | Command | Payload access |
|---|---|---|
| Browse vocabulary | `read.py topics --db <db>` | None |
| Find candidates | `read.py search --db <db> [filters]` | None |
| Read one selected document | `read.py show --db <db> <id>` | Selected row only |

`search` supports `--title`, `--kind`, `--path`, repeated `--topic`,
`--summary`, `--archived-after`, `--archived-before`,
`--include-superseded`, and `--limit`. Repeated topics use AND semantics.
The default limit is 20.

By default, search removes every document targeted by a `supersedes` link.
Use `--include-superseded` only when the user requests history or a revision
comparison.

Topics are a broad shared-subject index. Directed links are evidence of a
specific relationship:

- `plan --implements--> spec`
- `new --supersedes--> old`
- `document --references--> dependency`

Search results include one-hop incoming and outgoing link metadata. Follow an
ID with `show` only when exact source text is needed. Repeat `show` explicitly
for deeper traversal.

The reader opens SQLite in read-only URI mode with `query_only`. Stop on a
missing database, invalid SQLite image, unsupported schema, corrupt zlib,
byte-length mismatch, or SHA-256 mismatch. Never guess missing content.
