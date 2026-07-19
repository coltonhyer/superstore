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

## Failure boundary

The script is read-only. If it reports a missing or unsupported schema,
materialized VCS conflict, invalid compressed payload, byte-length mismatch, or
SHA-256 mismatch, stop and report that condition. Do not mutate the ledger,
query around the damaged row for partial source, or infer its contents.

Use the writer skill for metadata corrections or replay; this skill never
writes SQLite.
