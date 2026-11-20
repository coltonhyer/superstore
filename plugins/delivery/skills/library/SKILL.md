---
name: library
description: Use when a task needs to find, read, write, pin, or compare specs, plans, handoff notes, or other documents in the repository, or needs the document convention (Open Knowledge Format frontmatter, types, locations, status).
---

# Library

Every document is an Open Knowledge Format (OKF) concept: Markdown with a
frontmatter block, committed in the repository. Version control supplies
history, exact bytes, and pinning. This skill is superstore's OKF encoder: it
states only what OKF leaves open, namely document types, locations, extra
fields, when each status is set, and how to find, write, pin, and compare
documents. It never creates an index, a cache, or a helper script, and never
adds a document folder to an ignore file.

OKF governs. [`references/okf-spec.md`](references/okf-spec.md) is a
byte-for-byte copy of OKF v0.2 (`SPEC.md`) from
`https://github.com/GoogleCloudPlatform/open-knowledge-format` at commit
`ad30107c31c06aec8a7d5636e0d1058118604e6f`, licensed Apache 2.0 under
[`references/okf-LICENSE.md`](references/okf-LICENSE.md). Never edit either
file. Nothing here claims that `docs/` as a whole is an OKF bundle.

## Types, locations, file names

| Type | Written by | Default folder |
| --- | --- | --- |
| `spec` | the specs workflow | `docs/specs/` |
| `plan` | the plans workflow | `docs/plans/` |
| `handoff` | the whole-plan execution workflow | `docs/handoffs/` |
| `note` and any other lowercase slug | this skill | `docs/<kind>/`, the type's plural, such as `docs/notes/` |

A document's folder resolves in this order:

1. A path the user names for this document.
2. A folder that `AGENTS.md` or `CLAUDE.md` at the repository root names for
   that type, in a sentence such as `Specs live in design/specs/.`
3. `docs/<kind>/`. Kind folders are flat.

Reading follows the same order. A document at a one-off user path is still
valid; it is found when a task names it.

The **document folders** are the resolved folders of `spec`, `plan`,
`handoff`, and `note`, plus any folder `AGENTS.md` or `CLAUDE.md` names for a
type. A document of another type is found when a task names that type.
`.agents/execution/` is execution scratch, not a document folder.

A file is named `<slug>.md`. The slug matches `^[a-z0-9]+(-[a-z0-9]+)*$` and
is neither `index` nor `log`, which OKF reserves (§3.1).

## Frontmatter

A block delimited by `---` lines, one field per line, in this order when
present:

| Field | Presence | Value |
| --- | --- | --- |
| `type` | always | `spec`, `plan`, or `handoff`; another lowercase slug, such as `note`, for a type no workflow owns |
| `title` | always | one line of text, in double quotes |
| `description` | always | one sentence, in double quotes |
| `status` | specs and plans | `draft`, `stable`, or `deprecated` |
| `verified` | approved specs and plans, when approval can name a person | one line: `{ by: human:<approver>, at: <approval time> }` |
| `tags` | always | inline list of one or more slugs, such as `[auth, session-management]` |
| `implements` | optional | one repository path, such as `docs/specs/auth-sessions.md` |
| `supersedes` | optional | one repository path |
| `references` | optional | inline list of repository paths |

- Every field is one line: no block lists or nesting. `title` and
  `description` are always in double quotes, with `\` and `"` inside them
  escaped as `\\` and `\"`; unquoted, a `: ` breaks the line and a ` #` cuts
  it short. No other field is quoted. OKF allows more; this is the subset
  written here (§4.1).
- A repository path is relative to the repository root, without a leading
  slash, and includes `.md`. `references` is unrelated to OKF's `references/`
  folder convention (§6.3).
- `verified` is written by approval, never by this skill. The approver is the
  user name version control is configured with, and the time is an ISO 8601
  UTC instant such as `2026-11-01T18:30:00Z`.
- The body is free Markdown after the frontmatter block and one blank line.
- A document without `status` is final when written. OKF reads an absent
  status as `stable` (§5.4).

## Status

- Specs and plans are written with `status: draft`. Explicit approval sets
  `stable` and writes `verified`. Approving a document that has `supersedes`
  also sets the named document to `deprecated` unless it already is; a target
  without a `type` line is not yet migrated, so it stays unchanged and the
  report says so.
- Revising a stable document in place sets `draft` and removes `verified`;
  approval sets `stable` and writes a new `verified`.
- A document is **current** when its `status` is absent or `stable`. The body
  of a `draft` or `deprecated` document is read only when a task asks for
  history or a comparison. `verified` records who approved a document and
  when; it does not decide whether the document is current.
- A spec or plan without `status` is current to readers, as OKF says, but is
  not approved for planning or execution.
- Revisions of the same document are in-place edits; read history through
  version control, not through new files. `supersedes` is used only when a
  differently named document replaces another; a `supersedes` target that does
  not exist affects nothing.

## Find

1. **Scope.** When the task names a document or locator, read that file
   directly and skip discovery. Otherwise resolve the folder the task needs
   and list it. A folder that does not exist yields no hits; `find`
   (step 2) reports it and carries on.

   ```sh
   ls docs/specs/
   ```

2. **Filter on frontmatter lines, inside the document folders only.** The
   frontmatter is the block between the first two `---` lines at the top of a
   file. Filter on those lines only, with any tool whose output is only that
   block's lines; a YAML parser is fine when the environment has one. Never
   decide from a line below the closing `---`: bodies hold example
   frontmatter in fenced blocks. Never search the whole repository: eval
   fixtures and other Markdown can carry similar lines. Rule documents out
   from their frontmatter lines before opening any body, even when the task
   or the user hands you a list of files. `head`, `cat`, and a version-control `show` or
   `diff` of a document count as reading its body, so do not use them to
   inspect frontmatter or to discover documents, and do not use
   version-control history to discover documents. The extractor below prints
   only frontmatter, one `FILE: line` per line, so it is allowed even though
   `awk` scans the whole file; pipe it into `grep`.

   ```sh
   find -H docs/specs -maxdepth 1 -name '*.md' ! -name index.md ! -name log.md \
     -exec awk '{ sub(/\r$/, "") }
          FNR == 1 { fm = ($0 == "---"); next }
          fm && /^---$/ { fm = 0 }
          fm { print FILENAME ": " $0 }' {} + | grep ': status: stable$'
   ```

   Specs and plans always carry `status`, so this lists the current specs. A
   document of another type is current when it has no `status` line or
   `status: stable`. List other folders after `docs/specs` to search them
   too, and change the last `grep` to filter on another field.
   Match whole tag slugs by delimiting on the inline-list syntax, not with
   `\b`, which treats `-` as a boundary: `grep ': tags: .*[[, ]auth[],]'` for
   a tag (over `docs/specs docs/plans`), `grep ': title: '` for titles. To
   find documents naming a path in `supersedes`, search every document folder
   (`docs/specs docs/plans docs/handoffs docs/notes`) and use
   `grep ': supersedes: docs/specs/auth-sessions.md'`.

3. **Keep current documents.** Keep hits whose `status` is `stable` or
   absent; drop `draft` and `deprecated`. A `supersedes` line on a draft
   retires nothing.
4. **Read only what the answer depends on.** Read selected files in full, not
   every filtered hit. Frontmatter lines are enough to rule documents out.
5. **Follow links only when needed.** Read an `implements` or `references`
   target when the task needs its content, such as the spec behind a plan.
   Tags establish relevance, not a need to read.
6. **Report what is not yet migrated.** A Markdown file in a document folder,
   other than `index.md` and `log.md`, that has no `type` line (an empty file
   has none), or has a `status` outside `draft`, `stable`, and `deprecated`,
   is reported to the user as not yet migrated, never skipped silently. Such
   a file is never selected as a current document, even when a filter above
   matches it; name it in the answer as not yet migrated.

   ```sh
   find -H docs/specs docs/plans docs/handoffs docs/notes -maxdepth 1 -name '*.md' ! -name index.md ! -name log.md \
     \( -size 0 -print -o -exec awk '{ sub(/\r$/, "") }
          FNR == 1 { if (f != "" && !t) print f; f = FILENAME; t = 0; fm = ($0 == "---"); next }
          fm && /^---$/ { fm = 0 }
          fm && /^type: / { t = 1 }
          fm && /^status: / && !/^status: (draft|stable|deprecated)$/ { print FILENAME }
          END { if (f != "" && !t) print f }' {} + \) | sort -u
   ```

7. **Cite** each document by its path, or by `path@revision` for a pinned
   read.

## Pin and compare

A locator is a repository-relative path, written `path@revision` when pinned
to a version-control revision such as a Jujutsu change id or a Git commit. An
unpinned locator means the working copy.
Read a pinned locator through the active version control, never from the
working copy. Use whichever system the repository uses; neither is preferred.

Before resolving a revision, reading a document at a revision, comparing
revisions, or listing a document's history, read
[`references/pin-and-compare.md`](references/pin-and-compare.md); it gives each
command in its Jujutsu and Git forms and how to follow history across a move.

Cite the result as `path@revision` with the revision you actually read.

## Write

Write documents of types no workflow owns, such as `note`, with the
frontmatter above at the folder the location order resolves. Never write or
change a `spec`, `plan`, or `handoff`: their skills own approval and
recording. Do not edit an existing file unless the task asks to change it.

- Leave the new document in the working copy and commit nothing. Recording it
  belongs to the user or the workflow that asked for it.
- Before writing the first document of a type to a default folder that
  already exists, check that the folder holds no Markdown without OKF
  frontmatter, other than `index.md` and `log.md`, such as another tool's
  reports. Run this check, with the type's folder in place of
  `docs/reviews`:

  ```sh
  find -H docs/reviews -maxdepth 1 -name '*.md' ! -name index.md ! -name log.md \
    \( -size 0 -print -o -exec awk '{ sub(/\r$/, "") }
         FNR == 1 { if (f != "" && !t) print f; f = FILENAME; t = 0; fm = ($0 == "---"); next }
         fm && /^---$/ { fm = 0 }
         fm && /^type: / { t = 1 }
         END { if (f != "" && !t) print f }' {} + \) | sort -u
  ```

  If it lists any file, stop and ask the user where the documents should go.
  Write nothing in that folder until they answer.
- Never create `index.md` or `log.md`; the general rule against an index,
  cache, script, or ignore-file entry applies here too.

A complete note, `docs/notes/ci-runners.md`:

```markdown
---
type: note
title: "CI runner capacity"
description: "Shared runners queue jobs during the morning peak."
tags: [ci, infrastructure]
---

# CI runner capacity

Paginate long test matrices across two runner pools.
```

## When to open the spec

Open [`references/okf-spec.md`](references/okf-spec.md) for a type or case these
rules do not cover, or for an OKF folder another tool wrote. Sections: §3.1
reserved filenames, §4.1 frontmatter, §5.4 status, §6 links and paths, §8 index
files, §9 log files, §11 conformance.
