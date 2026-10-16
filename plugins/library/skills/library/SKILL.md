---
name: library
description: Use when a task needs to find, read, pin, or compare specs, plans, notes, or other documents under .agents/library/, or needs the library's layout and frontmatter convention.
---

# Library

The library is plain Markdown committed under `.agents/library/`. Version
control supplies history, exact bytes, and pinning. This skill reads the
library; it never writes documents, never creates an index or script, and
never ignores the folder.

## Layout

- Root: `.agents/library/`, committed and never ignored.
- Kinds: one folder per kind, named with a plural lowercase slug: `specs/`,
  `plans/`, `notes/`, or another plural slug when a new kind is needed. The
  folder is the kind; there is no `kind` field.
- Documents: `<kind>/<slug>.md`, where the slug matches
  `^[a-z0-9]+(-[a-z0-9]+)*$`. The filename is the document's identity; there
  is no `id` field.

## Frontmatter

Every document starts with a block delimited by `---` lines, one field per
line, in this order when present:

| Field | Presence | Value |
| --- | --- | --- |
| `title` | always | one line of text |
| `status` | specs and plans only | `draft` or `approved` |
| `topics` | always | inline list of one or more slugs, such as `[auth, session-management]` |
| `implements` | optional | one library-relative path, such as `specs/auth-sessions.md` |
| `supersedes` | optional | one library-relative path |
| `references` | optional | inline list of library-relative paths |

No other fields, block lists, nesting, or quoting. Every field is one
grep-able line. Paths are relative to `.agents/library/` and include `.md`.
Kinds other than specs and plans omit `status`; they are final when written.

The body is free Markdown after the frontmatter block and one blank line.

A complete example, `.agents/library/plans/auth-sessions.md`:

```markdown
---
title: Authentication sessions plan
status: approved
topics: [auth, session-management]
implements: specs/auth-sessions.md
---

# Authentication sessions plan

Rotate session tokens on privilege change and expire idle sessions after
30 minutes.
```

## Current documents

A document is current when its `status` is not `draft` and no non-draft
document in the library names it in `supersedes`.

- A draft's `supersedes` takes effect only when the draft is approved.
- Revisions of the same document are in-place edits; read history through
  version control, not through new files.
- `supersedes` is used only when a differently named document replaces
  another. A `supersedes` target that does not exist affects nothing.

## Locators

A locator is a repository-relative path, written `path@revision` when pinned to
a version-control revision such as a Jujutsu change id or a Git commit. An
unpinned locator means the working copy.

## Read

1. **Scope.** When the task names a document or locator, read that file
   directly and skip discovery. Otherwise pick the kind folder the task needs
   and list it:

   ```sh
   ls .agents/library/specs/
   ```

2. **Filter on frontmatter lines.** Rule documents out from their frontmatter
   lines before opening any body, even when the task or the user hands you a
   list of files. Never read the body of a `draft` or superseded document
   unless the task asks for history or a comparison. Filter with grep on the
   frontmatter field lines; `head`, `cat`, or a version-control `show` or
   `diff` of a document counts as reading its body, so do not use them to
   inspect frontmatter or to discover documents, and do not use version-control
   history to discover documents. Match whole topic slugs
   by delimiting on the inline list syntax, not with `\b`, which treats `-` as
   a boundary:

   ```sh
   grep -l '^topics: .*[[, ]auth[],]' .agents/library/*/*.md   # whole slug only
   grep -l '^status: approved' .agents/library/specs/*.md
   grep -H '^title: ' .agents/library/specs/*.md
   ```

3. **Exclude drafts and superseded documents.** Drop any hit whose `status`
   is `draft`. For each remaining candidate, find who supersedes it:

   ```sh
   grep -rl '^supersedes: specs/auth-sessions.md' .agents/library
   ```

   Check each hit's `status` line; a draft hit does not count. A candidate
   with a non-draft superseder is not current; follow to the superseder and
   apply the same check to it.

4. **Read the selected file in full.** Read only the documents the answer
   depends on, not every filtered hit. Frontmatter lines are enough to rule
   documents out.
5. **Follow links only when needed.** Read an `implements` or `references`
   target when the task needs its content, such as the spec behind a plan.
   Topics establish relevance, not a need to read.
6. **Cite.** Name each document by its locator: the path for a working-copy
   read, or `path@revision` for a pinned read.

## Pin and compare

Read a pinned locator through the active version control, never from the
working copy. Use whichever system the repository uses; neither is preferred.

Resolve a revision first when the task names it indirectly, such as by its
description:

```sh
jj log -r 'description(substring:"auth sessions")' --no-graph -T 'change_id.short() ++ " " ++ commit_id.short() ++ "\n"'
git log --format='%h %s' --grep='auth sessions'
```

Read a document at a revision:

```sh
jj file show -r <rev> .agents/library/specs/auth-sessions.md
git show <rev>:.agents/library/specs/auth-sessions.md
```

Compare a document between revisions, or between a revision and the working
copy:

```sh
jj diff --from <old> --to <new> .agents/library/specs/auth-sessions.md
jj diff --from <old> .agents/library/specs/auth-sessions.md
git diff <old> <new> -- .agents/library/specs/auth-sessions.md
git diff <old> -- .agents/library/specs/auth-sessions.md
```

List a document's history:

```sh
jj log .agents/library/specs/auth-sessions.md
git log --oneline -- .agents/library/specs/auth-sessions.md
```

Cite the result as `path@revision` with the revision you actually read.

## Boundaries

- Name `.agents/library` explicitly in every search. Ripgrep and similar
  tools skip dot-folders by default, so an unscoped search silently misses
  the library.
- Do not scan or read the whole library when the subject is known; filter on
  frontmatter and read only what matches.
- `.agents/execution/` is execution scratch, not library content.
- Never write or edit documents, create an index, cache, or helper script, or
  add the library to an ignore file. Writing documents belongs to the
  workflow that owns them.
