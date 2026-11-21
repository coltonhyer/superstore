# Pin and compare

The commands for computing and reading 12-character committed Git blob hashes,
reading a document at a revision, comparing revisions, and following history,
in their Jujutsu and Git forms.

Resolve a revision first when the task names it indirectly, such as by its
description:

```sh
jj log -r 'description(substring:"auth sessions")' --no-graph -T 'change_id.short() ++ " " ++ commit_id.short() ++ "\n"'
git log --format='%h %s' --grep='auth sessions'
```

Read a document at a revision:

```sh
jj file show -r <rev> docs/specs/auth-sessions.md
git show <rev>:docs/specs/auth-sessions.md
```

Compute a 12-character committed Git blob hash (always from a committed
revision, never from a dirty working copy; `jj git root` works in both
colocated and non-colocated Git-backed Jujutsu repositories):

```sh
git --git-dir="$(jj git root)" rev-parse --short=12 "$(jj log -r <rev> --no-graph -T commit_id):docs/specs/auth-sessions.md"
git rev-parse --short=12 <rev>:docs/specs/auth-sessions.md
```

Read a document by its committed Git blob hash:

```sh
git --git-dir="$(jj git root)" cat-file -p <blob>
git cat-file -p <blob>
```

Compare a document between revisions, or between a revision and the working
copy:

```sh
jj diff --from <old> --to <new> docs/specs/auth-sessions.md
jj diff --from <old> docs/specs/auth-sessions.md
git diff <old> <new> -- docs/specs/auth-sessions.md
git diff <old> -- docs/specs/auth-sessions.md
```

List a document's history:

```sh
jj log docs/specs/auth-sessions.md
git log --oneline --follow -- docs/specs/auth-sessions.md
```

History from before a document moved stays at its old path. `jj log` on the
new path stops at the move, so query the old path too; `git log --follow`
follows the move.

```sh
jj log <old path>
git log --follow --oneline -- <new path>
```
