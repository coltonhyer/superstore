---
name: read-archive
description: Use when a task needs to find, inspect, restore, compare, or reason from Markdown documentation previously stored in a Superstore SQLite ledger.
---

# Read Archive

Use compact discovery metadata first. Decompress exact Markdown only after
selecting the document needed for the task.

## Locate the ledger

Use `<workspace-root>/.agents/ledger.db`. If the active workspace root is not
available, ask the user rather than guessing. Pass the database explicitly to
every command.

## Discovery workflow

1. Browse known topics when the relevant vocabulary is unclear:

   ```bash
   python3 <skill-root>/scripts/read.py topics \
     --db <workspace-root>/.agents/ledger.db
   ```

2. Search titles, kinds, paths, topics, summaries, or archive dates:

   ```bash
   python3 <skill-root>/scripts/read.py search \
     --db <workspace-root>/.agents/ledger.db \
     <filters>
   ```

3. Keep the default current-document view unless the user asks for history.
4. Use topics to find a shared subject. Use directed links to establish
   `implements`, `supersedes`, `references`, or a bespoke relationship.
5. When exact wording or full detail is needed, select an ID and run:

   ```bash
   python3 <skill-root>/scripts/read.py show \
     --db <workspace-root>/.agents/ledger.db \
     <document-id>
   ```

6. Answer from the verified `content` and cite the archived title, source path,
   and document ID. Repeat `show` for another ID only when one-hop link metadata
   establishes that it is relevant.

Read [references/query-model.md](references/query-model.md) for filter and link
semantics.

## Restore a document

Restoring writes archived Markdown back to the working tree. It never touches
SQLite.

1. Identify the exact document with the discovery workflow and confirm the ID
   with the user.
2. Run `show` for that ID. The command verifies byte length and SHA-256 before
   returning, so the JSON `content` field is the exact archived bytes.
3. Decide the destination. Default to the archived `source_path` (relative paths
   are under the workspace root); use a different path only when the user asks.
4. If a file already exists at the destination, show that it differs and get
   confirmation before overwriting. Never clobber silently.
5. Write the `content` string verbatim to the destination without newline
   normalization or reformatting, then report the path and document ID.

## Compare revisions

1. Find both revisions. A `supersedes` edge links a newer document to the older
   one; run `search --include-superseded` or read the `supersedes` and
   `superseded_by` links from `show` to get both IDs.
2. Run `show` for each ID and diff their verified `content` fields.
3. Report the differences and cite both titles, source paths, and document IDs.

## Failure boundary

The script is read-only. If it reports a missing or unsupported schema,
materialized VCS conflict, invalid compressed payload, byte-length mismatch, or
SHA-256 mismatch, stop and report that condition. Do not mutate the ledger,
query around the damaged row for partial source, or infer its contents.

Use the writer skill for metadata corrections or replay; this skill never
writes SQLite.
