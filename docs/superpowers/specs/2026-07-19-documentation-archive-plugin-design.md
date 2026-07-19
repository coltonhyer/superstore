# Superstore Documentation Archive Plugin Design

Date: 2026-07-19  
Status: Approved

## Summary

Superstore is a Codex plugin containing two Agent Skills:

- `archiving-documentation` writes Markdown documentation into `.agents/ledger.db`.
- `read-archive` finds archived documents and restores their exact content.

Each archived document keeps a short searchable summary and topics alongside a
losslessly compressed copy of the original UTF-8 Markdown. Source files are
deleted only after the database write and verification succeed. The database
may be committed to version control; a logical replay operation safely combines
insert-only archive runs from parallel branches.

The plugin is inspired by cleanup of `docs/superpowers/` and `.superpowers/`,
but it never assumes those paths. Every archive operation requires an explicit
file or directory path.

## Goals

- Remove completed Markdown documentation from the working tree without losing
  its exact contents.
- Make archived documents cheap for agents to discover through summaries,
  topics, metadata, and directed links.
- Preserve exact source bytes for detailed retrieval and recovery.
- Keep document payloads immutable while allowing discovery metadata to be
  corrected.
- Support committed SQLite databases and safe replay of parallel, insert-only
  archive runs.
- Follow the Agent Skills specification and use only the Python standard
  library.

## Non-goals

- Non-Markdown inputs, including PDF and Word documents.
- Default directory scanning.
- Embeddings, vector search, or full-text indexing of compressed source.
- A remote archive service or live multi-writer database.
- Automatic version-control commits.
- A custom Git or Jujutsu merge driver.
- Automatic merging of concurrent edits to existing metadata.
- Compatibility with the user's previous private ledger schema.

## Plugin and skill structure

The repository will use a standard Codex plugin manifest and two self-contained
Agent Skills. The manifest registers the plugin as `superstore`:

```text
.codex-plugin/
└── plugin.json
skills/
├── archiving-documentation/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── archive.py
│   ├── references/
│   │   ├── schema.md
│   │   └── replay.md
│   └── evals/
│       ├── evals.json
│       └── files/
└── read-archive/
    ├── SKILL.md
    ├── scripts/
    │   └── read.py
    ├── references/
    │   └── query-model.md
    └── evals/
        ├── evals.json
        └── files/
tests/
└── test_ledger.py
```

Both `SKILL.md` files will:

- Use a directory-matching, lowercase, hyphenated `name`.
- Include a focused `description` explaining when the skill should activate.
- Stay below the specification's recommended 500-line and 5,000-token limits.
- Refer only to resources inside their own skill root.
- Avoid the experimental `allowed-tools` field for cross-client portability.

There is no third shared-knowledge skill. Agent Skills do not define skill
dependencies, and an implementation-only skill would add a misleading catalog
entry. The SQLite schema version is the shared contract between the two
self-contained scripts.

## Database location and compatibility

The ledger lives at `.agents/ledger.db` beneath the active workspace root. The
skills pass this path explicitly to their scripts rather than making the scripts
guess a Git or Jujutsu root. If the client does not expose a workspace root, the
skill asks the user rather than guessing.

The database uses:

```sql
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = DELETE;
PRAGMA user_version = 1;
```

`user_version` is the application schema version stored in the SQLite header.
New SQLite databases begin at `0`; the writer sets it to `1` only after creating
the complete v1 schema. Both scripts refuse unsupported nonzero versions.

The scripts require Python 3 with the standard `sqlite3`, `uuid`, `zlib`,
`hashlib`, `json`, and filesystem modules. IDs use UUIDv4 for compatibility
with Python runtimes older than 3.14. IDs are opaque text, so a future writer
may generate UUIDv7 values without migrating existing rows.

## Schema

### `archive_runs`

One immutable row describes each successfully inserted batch:

```sql
CREATE TABLE archive_runs (
    id          TEXT PRIMARY KEY,
    archived_at TEXT NOT NULL,
    source_root TEXT NOT NULL
);

CREATE TRIGGER archive_runs_immutable_update
BEFORE UPDATE ON archive_runs
BEGIN
    SELECT RAISE(ABORT, 'archive runs are immutable');
END;

CREATE TRIGGER archive_runs_no_delete
BEFORE DELETE ON archive_runs
BEGIN
    SELECT RAISE(ABORT, 'archive runs cannot be deleted');
END;
```

- `id` is a UUIDv4.
- `archived_at` is an RFC 3339 UTC timestamp.
- `source_root` is the normalized explicit file or directory supplied for the
  operation.

An all-duplicate retry does not create an empty archive run.

### `documents`

Each Markdown file remains a separate document:

```sql
CREATE TABLE documents (
    id                 TEXT PRIMARY KEY,
    archive_run_id     TEXT NOT NULL REFERENCES archive_runs(id),
    source_path        TEXT NOT NULL,
    title              TEXT NOT NULL,
    kind               TEXT NOT NULL,
    summary            TEXT NOT NULL,
    content_zlib       BLOB NOT NULL,
    content_sha256     TEXT NOT NULL CHECK (length(content_sha256) = 64),
    source_bytes       INTEGER NOT NULL CHECK (source_bytes >= 0),
    UNIQUE (source_path, content_sha256)
);

CREATE INDEX documents_by_run ON documents(archive_run_id);
```

- `source_path` is relative to the workspace when the source is inside it and
  absolute otherwise.
- `kind` is a normalized lowercase slug. Common values include `spec`, `plan`,
  and `notes`, but bespoke kinds are allowed.
- `summary` is editable discovery metadata, normally 80–200 words covering the
  document's purpose, key decisions, outcome, and unresolved work without
  inventing information.
- `content_zlib` is `zlib.compress()` applied to the exact original UTF-8 bytes.
- `content_sha256` is the lowercase SHA-256 hex digest of those uncompressed
  bytes.
- `source_bytes` records the original byte length.
- `(source_path, content_sha256)` makes retries idempotent while allowing the
  same content to retain distinct provenance at different paths.

Payload columns are immutable and documents cannot be deleted:

```sql
CREATE TRIGGER documents_payload_immutable
BEFORE UPDATE OF
    id, archive_run_id, source_path, content_zlib, content_sha256, source_bytes
ON documents
BEGIN
    SELECT RAISE(ABORT, 'archived document payload is immutable');
END;

CREATE TRIGGER documents_no_delete
BEFORE DELETE ON documents
BEGIN
    SELECT RAISE(ABORT, 'archived documents cannot be deleted');
END;
```

The writer may update `title`, `kind`, and `summary`.

### `document_topics`

Topics are a many-to-many, indexed discovery surface:

```sql
CREATE TABLE document_topics (
    document_id TEXT NOT NULL REFERENCES documents(id),
    topic       TEXT NOT NULL CHECK (topic <> ''),
    PRIMARY KEY (document_id, topic)
);

CREATE INDEX document_topics_by_topic
    ON document_topics(topic, document_id);
```

Topics are normalized lowercase slugs such as `auth`, `api`, or `migration`.
The archiving agent honors explicit topics, reuses existing vocabulary when
possible, and otherwise infers a small useful set.

### `document_links`

One edge table represents directed document relationships:

```sql
CREATE TABLE document_links (
    from_document_id TEXT NOT NULL REFERENCES documents(id),
    relation         TEXT NOT NULL CHECK (relation <> ''),
    to_document_id   TEXT NOT NULL REFERENCES documents(id),
    PRIMARY KEY (from_document_id, relation, to_document_id),
    CHECK (from_document_id <> to_document_id)
);

CREATE INDEX document_links_by_target
    ON document_links(to_document_id, relation, from_document_id);
```

Relations are normalized lowercase verbs. Documented defaults are
`implements`, `supersedes`, and `references`, but bespoke verbs are allowed.
No one-to-one constraint is imposed: one spec may have several plans, and one
plan may implement several specs.

A shared topic means that documents concern the same surface. A directed link
states the exact relationship. Revisions are new records linked as:

```text
new document --supersedes--> old document
```

## Writer skill

### Candidate discovery

`archiving-documentation` requires an explicit Markdown file or directory. If
the user did not provide one, the skill asks for it and performs no scan.

For a file, the writer accepts only a regular `.md` file. For a directory,
`archive.py scan` recursively finds regular `.md` files beneath it. The scan:

- Rejects symlinks rather than following them outside the requested scope.
- Rejects invalid UTF-8 and an empty candidate set.
- Computes each file's SHA-256 and byte length.
- Assigns an archive-run UUID and document UUIDs for the pending manifest.
- Reports exact candidate paths and any matching prior record at the same path.
- Reports existing topic vocabulary to encourage reuse.

The agent shows the exact candidate list and obtains confirmation before
summarizing or writing anything.

### Agent-generated metadata

After confirmation, the agent reads each candidate and fills a temporary JSON
manifest containing:

- The scan-issued run and document IDs.
- The expected source path and SHA-256.
- Title, kind, and grounded summary.
- Normalized topics.
- Outgoing directed links to new document IDs from the same manifest or
  existing archive document IDs.

The agent may delegate summary drafts for a large batch. The parent agent
remains responsible for checking the summaries, selecting topics, and ensuring
links use the intended direction.

When a changed document has the same source path as an existing record, the
writer links the new record to the latest active prior record with
`supersedes`. Renamed-document revisions require agent judgment rather than a
filename heuristic.

### Transaction and cleanup

`archive.py archive`:

1. Re-reads every source and rejects the batch if a path, hash, or encoding
   changed after scanning.
2. Creates the v1 database when absent or validates `user_version` when present.
3. Enables foreign keys and uses `journal_mode=DELETE`.
4. Begins one transaction for the archive run, documents, topics, and links.
5. Compresses each source, inserts it, decompresses it again, and verifies its
   length and SHA-256.
6. Runs `foreign_key_check` and `integrity_check` inside the transaction,
   requiring no foreign-key rows and the single integrity result `ok`.
7. Commits only if the complete batch is valid, then closes SQLite.
8. Deletes the confirmed source files.
9. For a directory input, removes newly empty directories bottom-up, including
   the supplied root if it became empty.

The script reports the run ID, inserted and duplicate document counts,
uncompressed and compressed byte totals, and cleanup result. It never commits
version-control changes.

If a database operation or verification fails, the transaction rolls back and
all source files remain. If deletion fails after a successful commit, the
database stays authoritative and undeleted files remain in place. A retry
verifies matching path/hash records and finishes cleanup without inserting
duplicates.

### Metadata maintenance

The writer skill also owns metadata corrections. It previews the exact change
and obtains confirmation before invoking `archive.py metadata` to change a
document's title, kind, summary, topics, or links. The command cannot change or
delete the archived payload.

Metadata-edit commits are not eligible for automatic branch replay. They must
be serialized or reapplied manually when branches conflict.

## Reader skill

`read-archive` opens the database using SQLite read-only mode and
`PRAGMA query_only = ON`. It never mutates the ledger.

`read.py` supports three focused operations:

- `topics`: list normalized topics and document counts.
- `search`: filter title, kind, source path, topics, summary, and archive date.
- `show`: return one selected document's metadata, incoming and outgoing links,
  revision context, and exact Markdown.

Search returns compact JSON results with IDs, titles, kinds, paths, timestamps,
topics, links, and summaries. Results default to 20 matches and exclude any
document targeted by a `supersedes` link. The caller can explicitly include
superseded history.

`show` decompresses only the selected payload and verifies its byte length and
SHA-256 before returning it. Link traversal is one hop; the agent can repeat the
operation for deeper exploration.

The reader refuses:

- Missing or unsupported schemas.
- Invalid compressed data.
- Byte-length or SHA-256 mismatches.
- A materialized version-control conflict that is not a valid SQLite database.

V1 searches short summaries with ordinary SQLite predicates and uses the topic
index for fast filtering. At the expected scale of roughly 10,000 documents,
this avoids a duplicate FTS index and optional SQLite features. Add FTS only
after measured summary-search latency warrants it.

## Parallel-branch replay

Git and Jujutsu cannot semantically merge two SQLite database images. Even
branches that only insert different rows produce a binary conflict. The writer
therefore includes a VCS-agnostic logical replay operation rather than a custom
merge driver.

Replay receives three valid snapshots:

- `base`: the common-ancestor ledger.
- `destination`: the integrated ledger that should be preserved.
- `source`: the feature ledger containing archive runs to replay.

The skill's `references/replay.md` explains how to materialize valid Git and
Jujutsu conflict sides before invoking the helper.

`archive.py replay`:

1. Opens all three inputs read-only and verifies matching `user_version`,
   `integrity_check`, and `foreign_key_check` results.
2. Compares `base` and `source` and requires the feature change to be
   insert-only archive runs. Any edit or deletion of pre-existing metadata
   aborts with the affected document IDs.
3. Creates a temporary database beside the requested output using SQLite's
   backup API from `destination`.
4. Imports source archive runs absent from `base`, followed by their documents,
   topics, and outgoing links.
5. Treats an already-present, byte-identical run as an idempotent replay.
6. Aborts on divergent UUID collisions, duplicate path/hash conflicts, missing
   link targets, or unsupported row changes.
7. Verifies every imported payload, foreign keys, and complete database
   integrity.
8. Closes all connections and atomically replaces the requested output only
   after every check succeeds.

Neither input database is modified. A failure removes the temporary output and
leaves the known-good destination untouched.

## Version-control guidance

The skills do not require or modify version-control configuration. When the
ledger is tracked, the writer recommends:

```gitattributes
.agents/ledger.db binary
```

and excluding transient sidecars:

```gitignore
.agents/ledger.db-journal
.agents/ledger.db-wal
.agents/ledger.db-shm
```

Ignoring sidecars is safe here because the writer deliberately uses
`journal_mode=DELETE`, completes recovery when necessary, validates the main
database before source deletion, and performs no version-control operation
while a connection is open.

The expected compressed ledger size for 10,000 average 500–1,500-line Markdown
documents is approximately 200–400 MB including summaries, topics, metadata,
and indexes. Git may delta-compress historical versions, but no storage ratio is
assumed.

## Error handling

The writer fails without deleting sources when:

- No explicit path was supplied.
- A candidate is missing, symlinked, non-Markdown, or invalid UTF-8.
- A file changes between scan and archive.
- The manifest contains invalid IDs, empty metadata, malformed topics or
  relations, duplicate candidates, or missing link targets.
- The database schema is unsupported.
- Compression round-trip, SHA-256, foreign-key, or integrity verification
  fails.

The reader and replay helper return nonzero exit codes and structured errors.
They do not return partial source content or partially replace a database.

## Tests and skill evals

### Deterministic integration tests

`tests/test_ledger.py` uses `unittest`, temporary directories, and subprocesses
to exercise the scripts through their real command-line interfaces. It covers:

- Exact compression/decompression and SHA-256 round trips.
- Recursive Markdown discovery, non-Markdown exclusion, symlink rejection, and
  empty-directory cleanup.
- Multi-document topics and directed links.
- Changed-file and malformed-manifest failures preserving every source.
- Retry idempotency and automatic `supersedes` links.
- Reader filtering and default exclusion of superseded documents.
- Corrupt payload and unsupported-schema errors.
- Three-snapshot replay preserving independent archive runs.
- Replay rejection of metadata edits, collisions, and schema mismatches.

No pytest, mocks package, fixtures framework, or external database is required.

### Agent Skill evals

Each skill contains `evals/evals.json` following the Agent Skills evaluation
guidance, starting with two or three realistic prompts and expected outcomes.

Writer evals verify that the agent:

- Asks for a path rather than assuming a default.
- Shows and confirms exact candidates before mutation.
- Produces grounded summaries, normalized topics, and meaningful directed links.
- Leaves source files intact on a safety failure.

Reader evals verify that the agent:

- Searches topics and summaries before loading exact content.
- Selects current documents unless history was requested.
- Follows directed links when answering cross-document questions.
- Reports archive corruption or schema incompatibility rather than guessing.

`skills-ref validate` checks both skill directories. A final smoke run invokes
each script exactly as documented by its `SKILL.md`. Eval result workspaces are
generated outside the skill directories and are not committed.

## Acceptance criteria

The v1 design is complete when:

- Both skill directories pass Agent Skills validation.
- An explicit Markdown directory can be archived only after confirmation.
- Every archived file can be restored byte-for-byte.
- Failed validation never deletes source material.
- Topics, summaries, kinds, dates, paths, and links support compact discovery.
- Revisions preserve history through `supersedes`.
- Parallel insert-only archive runs can be replayed into one valid database.
- Concurrent existing-metadata edits are detected and rejected.
- The complete standard-library integration suite passes.
