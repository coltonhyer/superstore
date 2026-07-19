# Replay parallel archive runs

Binary SQLite images cannot be row-merged by Git or Jujutsu. Preserve the
unresolved ledger and identify its common ancestor before resolving the
conflict.

Materialize four distinct paths:

1. Materialize the common ancestor as `base.db`.
2. Materialize the already-integrated side as `destination.db`.
3. Materialize the feature side as `source.db`.
4. Verify that each snapshot opens as SQLite.
5. Replay to a fourth, new path:

   ```bash
   python3 skills/archiving-documentation/scripts/archive.py replay \
     --base base.db \
     --destination destination.db \
     --source source.db \
     --output resolved.db
   ```

6. Replace the version-control conflict with `resolved.db` using ordinary Git
   or Jujutsu conflict-resolution commands.
7. Commit the resolved database through the user's ordinary workflow.

## Jujutsu

Inspect the conflict with `jj resolve --list`. Materialize each conflict side
using the installed Jujutsu version's file-conflict commands; conflict-term
syntax is version-dependent, so consult that version's help instead of
assuming a fixed syntax. Verify every materialized snapshot:

```bash
file <snapshot>
sqlite3 <snapshot> 'PRAGMA integrity_check;'
```

## Git

Materialize the common ancestor and both branch blobs:

```bash
git show <merge-base>:.agents/ledger.db >base.db
git show <integrated-commit>:.agents/ledger.db >destination.db
git show <feature-commit>:.agents/ledger.db >source.db
```

Verify each file with `file` and `sqlite3` as shown above before replay.

## Safety contract

- Replay supports only source-side insert-only archive runs.
- Existing metadata edits, deletions, divergent UUIDs, duplicate path/hash rows, missing link targets, and schema mismatches abort.
- Inputs are never modified; only the distinct output path is atomically replaced.
- Metadata-only commits must be serialized or manually reapplied.
- The skill never installs a custom merge driver or changes VCS configuration.
