---
name: archiving-documentation
description: Use when Markdown documentation should be archived or cleaned up after a work session, archive metadata needs correction, archive cleanup needs retrying, or insert-only ledger work must be replayed across branches.
---

# Archiving Documentation

Archive only explicitly selected Markdown while preserving its exact bytes.
Treat the SQLite ledger as authoritative only after the writer reports a
committed, verified transaction.

## Archive workflow

1. Require one explicit `.md` file or directory. If none was supplied, ask for
   it and stop. Never scan a conventional directory by assumption.
2. Determine the active workspace root. If unavailable, ask for it. Use
   `<workspace-root>/.agents/ledger.db`.
3. Run:

   ```bash
   python3 <skill-root>/scripts/archive.py scan \
     --db <workspace-root>/.agents/ledger.db \
     --workspace-root <workspace-root> \
     <explicit-path>
   ```

4. Show every returned candidate path and any `prior_document_id`. Ask for
   confirmation before reading for summaries, writing the database, or deleting
   anything.
5. After confirmation, preserve all scan-issued fields in a temporary JSON
   manifest outside the source tree. Add a title, lowercase-slug kind, grounded
   80–200 word summary covering purpose, key decisions, outcome, and unresolved
   work present in the source, a small set of lowercase-slug topics, and
   outgoing links. Never invent a missing outcome or unresolved item.
6. Use `implements` from a plan to the spec it implements. Use `references` for
   a direct non-implementation dependency. The writer automatically adds
   `supersedes` for changed content at the same path; use agent judgment for a
   renamed revision.
7. Existing topic vocabulary from `scan` is a preference, not a closed list.
   Shared topics mean shared subject matter; directed links state a specific
   relationship. Use `auth` and `session-management` for authentication-session
   documents.
8. For a large confirmed batch, a low-cost subagent may draft summaries in the
   background. The parent must check every summary against source text, choose
   topics, and verify link direction and target IDs.
9. Run:

   ```bash
   python3 <skill-root>/scripts/archive.py archive \
     --db <workspace-root>/.agents/ledger.db \
     --manifest <temporary-manifest.json>
   ```

10. Report the run ID, inserted and duplicate counts, byte totals, and cleanup
    result. Never make a version-control commit for the user.

Read [references/schema.md](references/schema.md) when constructing or
diagnosing a manifest.

## Safety outcomes

- Exit `0`: database and cleanup completed.
- Exit `2`: validation or database work failed; source files remain.
- Exit `3`: the database committed and is authoritative, but listed paths
  remain. Re-run scan/archive on those exact unchanged files to finish cleanup
  idempotently.

Do not manually delete a source after exit `2`. Do not rewrite a payload,
remove an archived document, disable integrity checks, or guess through an
unsupported schema.

Before invoking `archive`, require a fresh confirmed scan. If a candidate
changed, stop before any transaction, leave the source, rescan, and reconfirm
the new bytes. A cleanup request is not confirmation of new bytes. Once
`archive` runs, use its exit result; exit `3` means the database committed and
the source remains for the existing cleanup-retry workflow.

## Metadata correction

The user must identify the archived document. Use the reader skill if discovery
is needed. Prepare a complete metadata manifest as documented in
[references/schema.md](references/schema.md), show the exact before/after
change, and get confirmation. Then run:

```bash
python3 <skill-root>/scripts/archive.py metadata \
  --db <workspace-root>/.agents/ledger.db \
  --manifest <temporary-metadata-manifest.json>
```

This replaces title, kind, summary, topics, and outgoing links only. Metadata
edits are not eligible for automatic replay.

## Parallel branch conflict

Read [references/replay.md](references/replay.md). Materialize valid base,
destination, and source SQLite snapshots, verify each snapshot, and run the
documented `replay` command to a distinct output. Stop on existing-metadata
edits, deletions, collisions, missing targets, corruption, or schema mismatch.
Never configure a merge driver.
