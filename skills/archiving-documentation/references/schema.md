# Ledger schema v1

The ledger is SQLite with `PRAGMA foreign_keys = ON`,
`PRAGMA journal_mode = DELETE`, and application schema version 1.

## SQL objects

```sql
CREATE TABLE archive_runs (
    id TEXT PRIMARY KEY,
    archived_at TEXT NOT NULL,
    source_root TEXT NOT NULL
)
```

```sql
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    archive_run_id TEXT NOT NULL REFERENCES archive_runs(id),
    source_path TEXT NOT NULL,
    title TEXT NOT NULL,
    kind TEXT NOT NULL,
    summary TEXT NOT NULL,
    content_zlib BLOB NOT NULL,
    content_sha256 TEXT NOT NULL CHECK (length(content_sha256) = 64),
    source_bytes INTEGER NOT NULL CHECK (source_bytes >= 0),
    UNIQUE (source_path, content_sha256)
)
```

```sql
CREATE INDEX documents_by_run ON documents(archive_run_id)
```

```sql
CREATE TABLE document_topics (
    document_id TEXT NOT NULL REFERENCES documents(id),
    topic TEXT NOT NULL CHECK (topic <> ''),
    PRIMARY KEY (document_id, topic)
)
```

```sql
CREATE INDEX document_topics_by_topic
ON document_topics(topic, document_id)
```

```sql
CREATE TABLE document_links (
    from_document_id TEXT NOT NULL REFERENCES documents(id),
    relation TEXT NOT NULL CHECK (relation <> ''),
    to_document_id TEXT NOT NULL REFERENCES documents(id),
    PRIMARY KEY (from_document_id, relation, to_document_id),
    CHECK (from_document_id <> to_document_id)
)
```

```sql
CREATE INDEX document_links_by_target
ON document_links(to_document_id, relation, from_document_id)
```

```sql
CREATE TRIGGER archive_runs_immutable_update
BEFORE UPDATE ON archive_runs
BEGIN
    SELECT RAISE(ABORT, 'archive runs are immutable');
END
```

```sql
CREATE TRIGGER archive_runs_no_delete
BEFORE DELETE ON archive_runs
BEGIN
    SELECT RAISE(ABORT, 'archive runs cannot be deleted');
END
```

```sql
CREATE TRIGGER documents_payload_immutable
BEFORE UPDATE OF
    id, archive_run_id, source_path, content_zlib, content_sha256, source_bytes
ON documents
BEGIN
    SELECT RAISE(ABORT, 'archived document payload is immutable');
END
```

```sql
CREATE TRIGGER documents_no_delete
BEFORE DELETE ON documents
BEGIN
    SELECT RAISE(ABORT, 'archived documents cannot be deleted');
END
```

Archive-run rows are immutable and cannot be deleted. Document payload columns
(`id`, `archive_run_id`, `source_path`, `content_zlib`, `content_sha256`, and
`source_bytes`) can never be updated, and archived documents cannot be deleted.
Later metadata operations may replace only discovery metadata.

## JSON shapes

`scan` emits:

```json
{
  "schema_version": 1,
  "run_id": "UUIDv4",
  "source_root": "/absolute/normalized/requested/path",
  "source_type": "file",
  "workspace_root": "/absolute/normalized/workspace",
  "existing_topics": ["auth"],
  "documents": [
    {
      "id": "UUIDv4",
      "absolute_path": "/absolute/normalized/requested/path/spec.md",
      "source_path": "docs/spec.md",
      "content_sha256": "64-lowercase-hex-characters",
      "source_bytes": 1234,
      "prior_document_id": null
    }
  ]
}
```

The enriched archive manifest preserves every scan field and adds these fields
to each document:

```json
{
  "id": "scan-issued-UUIDv4",
  "absolute_path": "/path/from/scan",
  "source_path": "path/from/scan",
  "content_sha256": "hash-from-scan",
  "source_bytes": 1234,
  "prior_document_id": "existing-document-id-or-null",
  "title": "Human-readable title",
  "kind": "plan",
  "summary": "Grounded 80–200 word discovery summary.",
  "topics": ["auth", "session-management"],
  "links": [
    {
      "relation": "implements",
      "to_document_id": "another-new-or-existing-document-id"
    }
  ]
}
```

A complete-state metadata replacement has this shape:

```json
{
  "document_id": "existing-document-id",
  "title": "Corrected title",
  "kind": "spec",
  "summary": "Corrected grounded summary.",
  "topics": ["auth"],
  "links": [
    {
      "relation": "references",
      "to_document_id": "existing-target-id"
    }
  ]
}
```

## Value rules

Run and document IDs are canonical UUIDv4 text. `archived_at` is RFC 3339 UTC
with a trailing `Z`. Kinds, topics, and relations are normalized lowercase
slugs matching `^[a-z0-9]+(?:-[a-z0-9]+)*$`. Common kinds are `spec`, `plan`,
and `notes`; any other normalized lowercase slug is allowed.

`implements` means the source document implements the target, `supersedes`
means the source is a newer revision of the target, and `references` is a
general directed citation. Bespoke normalized verbs are allowed. Links are
many-to-many; there is no one-to-one constraint.

`source_path` uses POSIX separators and is relative when the source is beneath
the explicit workspace root; otherwise it is absolute. Every selected Markdown
file must be valid UTF-8. `content_zlib` is zlib-compressed from the exact source
bytes without newline normalization. Decompression must reproduce the recorded
SHA-256 digest and byte length before the transaction commits.

`PRAGMA user_version` is the application schema version stored in the SQLite
header. New databases begin at 0. The writer sets it to 1 only after all v1
objects exist in one successful schema transaction. Writer and reader scripts
reject unsupported nonzero versions.

## Transactions, cleanup, and exit codes

The writer validates and re-reads every manifest source before opening SQLite.
It creates or validates the schema, begins one archive transaction, inserts the
run, documents, topics, and links, verifies compressed payloads, runs
`foreign_key_check` and `integrity_check`, and then commits. Source cleanup
starts only after that commit. A database failure rolls back the archive
transaction and leaves every source untouched.

Cleanup re-reads each exact manifest path without following symlinks and checks
its byte length and SHA-256 immediately before deletion. A changed or replaced
path remains in place. A cleanup failure does not roll back the committed
archive: the database is authoritative, the command reports the retained paths,
and the same confirmed manifest is the record for a cleanup-only retry.

Exit code 0 means the operation and cleanup completed. Exit code 2 means
validation, database, compression, or filesystem setup failed before a
successful archive result. Exit code 3 means the archive committed but at least
one cleanup action failed.

As an estimate, not a guaranteed compression ratio, a ledger containing 10,000
average 500–1,500-line Markdown documents is expected to be on the order of
200–400 MB including payloads and discovery metadata.

## VCS guidance

Recommended `.gitattributes` entry (first line); recommended `.gitignore`
entries (remaining three):

```text
.agents/ledger.db binary
.agents/ledger.db-journal
.agents/ledger.db-wal
.agents/ledger.db-shm
```
