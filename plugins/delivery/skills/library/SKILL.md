---
name: library
description: Use when a task needs to find, read, write, pin, or compare specs, plans, handoff notes, or other documents in the repository, or needs the document convention (Open Knowledge Format frontmatter, types, locations, status).
---

# Library

Every document is an Open Knowledge Format (OKF) concept: Markdown with
frontmatter, committed in the repository. Version control supplies history,
exact bytes, and pinning. This skill is superstore's OKF encoder: it states
only what OKF leaves open—types, locations, extra fields, status rules, and
how to find, write, pin, and compare documents. Never create an index, cache,
or helper script, and never add a document folder to an ignore file.

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

Reading follows the same order; a document at a one-off user path is valid
and found when a task names it.

The **document folders** are the resolved folders of `spec`, `plan`,
`handoff`, and `note`, plus any folder `AGENTS.md` or `CLAUDE.md` names for a
type; other types are found when named. `.agents/execution/` is execution
scratch, not a document folder.

A file is named `<slug>.md`, matching `^[a-z0-9]+(-[a-z0-9]+)*$` and neither
`index` nor `log`, which OKF reserves (§3.1). Point-in-time standalone notes in
the notes folder (default `docs/notes/`) may prefix filenames with `YYYY-MM-DD-`
(which fits the slug rule); living specs keep undated domain slugs.

## Frontmatter

A block delimited by `---` lines, one field per line, in this order when
present:

| Field | Presence | Value |
| --- | --- | --- |
| `type` | always | `spec`, `plan`, or `handoff`; another lowercase slug, such as `note`, for a type no workflow owns |
| `title` | always | one line of text, in double quotes |
| `description` | always | one sentence, in double quotes |
| `status` | specs and plans | `draft`, `stable`, or `deprecated` |
| `verified` | approved specs and plans, when approval names a human or autonomous verifier | `{ by: human:<approver>, at: <approval time> }` (explicit human approval) or `{ by: process:delivery-autonomous, at: <approval time> }` (autonomous clean review; OKF `machine-confirmed`, never `human:`) |
| `tags` | always | inline list of one or more slugs, such as `[auth, session-management]` |
| `implements` | optional | one repository path (such as `docs/specs/auth-sessions.md`) or inline list (`[path-a, path-b]`) for multi-spec plans |
| `supersedes` | optional | one repository path or inline list (`[path-a, path-b]`) for merges and splits |
| `references` | optional | inline list of repository paths |

- Every field is one line (no block lists or nesting). Quote only `title` and
  `description` in double quotes (no other field is quoted), escaping `\` and
  `"` as `\\` and `\"` (unquoted `: ` breaks lines; ` #` cuts them). OKF allows
  more; this is the subset written here (§4.1).
- Paths are repo-root relative, without a leading slash, and include `.md`.
  `references` is unrelated to OKF's `references/` folder convention (§6.3).
- `verified` is written by approval, never by this skill: `human:<approver>`
  uses the user name version control is configured with; autonomous clean
  review uses `process:delivery-autonomous` (never `human:`). The time is an
  ISO 8601 UTC instant such as `2026-11-01T18:30:00Z`.
- Body is free Markdown after the frontmatter block and one blank line. A
  document without `status` is final when written; OKF reads absent status as
  `stable` (§5.4).

## Status

- Specs and plans are written with `status: draft`. Approval (explicit human or
  authorized autonomous clean review) sets `stable` and writes `verified`.
  Approving a document with `supersedes` (scalar or inline list) iterates over
  every listed target: sets each migrated target to `deprecated` unless it
  already is, leaves unmigrated targets (no frontmatter or no `type` line)
  unchanged and reports them, and ignores missing targets. For a spec split,
  deprecate the split spec only once the replacement set is complete and
  approved.
- Revising a stable document in place sets `draft` and removes `verified`;
  approval sets `stable` and writes a new `verified`. A mechanical
  blob-citation-only refresh on a `stable` plan whose tasks and content are
  unchanged commits without flipping `status` to `draft` or re-requesting
  approval.
- A document is **current** when its `status` is absent or `stable`. The body
  of a `draft` or `deprecated` document is read only when a task asks for
  history or a comparison. `verified` records who approved a document and
  when; it does not decide whether the document is current.
- A spec or plan without `status` is current to readers, as OKF says, but is
  not approved for planning or execution.
- Revisions of the same document are in-place edits; read history through
  version control, not new files. `supersedes` is used only when a differently
  named document replaces another.

## Find

1. **Scope.** When the task names a document or locator, read that file
   directly and skip discovery. Otherwise resolve the folder the task needs
   and list it. A folder that does not exist yields no hits; `find`
   (step 2) reports it and carries on.

   ```sh
   ls docs/specs/
   ```

2. **Filter on frontmatter lines, inside the document folders only.**
   Frontmatter is the block between the first two `---` lines at the top of a
   file; filter only those lines (a YAML parser is fine if available). Never
   decide from a line below closing `---` (bodies hold example frontmatter in
   fenced blocks) or search the whole repo (eval fixtures match). Rule
   documents out from frontmatter before opening any body, even given a file
   list. `head`, `cat`, and version-control `show` or `diff` count as reading
   bodies—never use them or version-control history to inspect frontmatter or
   discover documents. The extractor below prints only `FILE: line` for
   frontmatter, so it is allowed even though `awk` scans the whole file; pipe
   it into `grep`.

   ```sh
   find -H docs/specs -maxdepth 1 -name '*.md' ! -name index.md ! -name log.md \
     -exec awk '{ sub(/\r$/, "") }
          FNR == 1 { fm = ($0 == "---"); next }
          fm && /^---$/ { fm = 0 }
          fm { print FILENAME ": " $0 }' {} + | grep ': status: stable$'
   ```

   Specs and plans always carry `status`, so this lists current specs. Other
   types are current when `status` is absent or `stable`. Add other folders
   after `docs/specs`, and change the `grep` to filter other fields. Match
   whole tag slugs on inline-list delimiters (not `\b`, which breaks on `-`):
   `grep ': tags: .*[[, ]auth[],]'` (over `docs/specs docs/plans`),
   `grep ': title: '` for titles. To find documents naming a path in
   `supersedes`, search every document folder (`docs/specs docs/plans
   docs/handoffs docs/notes`) with
   `grep -E ': supersedes: (.*[, [])?docs/specs/auth-sessions\.md([],]|$)'`
   (matches scalar and inline-list forms without prefix/suffix false matches).

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

7. **Cite** each document by its path, `<path>`, blob `<12-char hash>` for
   committed plans and handoffs, or `path@revision` for ad-hoc pinned reads.

## Pin and compare

A locator is a repository-relative path, pinned as `<path>`, blob
`<12-char hash>` (committed plans and handoffs) or `path@revision` (ad-hoc
pinned reads via Jujutsu change/commit id or Git commit). An unpinned locator
means the working copy. Compute blob hashes only from committed revisions,
never dirty working copies, and read pinned locators through version control,
never the working copy; neither Jujutsu nor Git is preferred.

Before computing or reading a 12-character committed Git blob hash, resolving a
revision, reading a document at a revision, comparing revisions, or listing a
document's history, read
[`references/pin-and-compare.md`](references/pin-and-compare.md) for Jujutsu
and Git commands and move history. Cite ad-hoc reads as `path@revision` with the
revision read.

## Write

Write documents of types no workflow owns, such as `note`, with the
frontmatter above at the folder the location order resolves. Never write or
change a `spec`, `plan`, or `handoff`: their skills own approval and
recording. Do not edit an existing file unless the task asks to change it.

- Leave the new document in the working copy and commit nothing. Recording it
  belongs to the user or the workflow that asked for it.
- Before writing the first document of a type to an existing default folder,
  check that it holds no Markdown without OKF frontmatter (besides `index.md`
  and `log.md`, e.g., another tool's reports), replacing `docs/reviews`:

  ```sh
  find -H docs/reviews -maxdepth 1 -name '*.md' ! -name index.md ! -name log.md \
    \( -size 0 -print -o -exec awk '{ sub(/\r$/, "") }
         FNR == 1 { if (f != "" && !t) print f; f = FILENAME; t = 0; fm = ($0 == "---"); next }
         fm && /^---$/ { fm = 0 }
         fm && /^type: / { t = 1 }
         END { if (f != "" && !t) print f }' {} + \) | sort -u
  ```

  If it lists any file, stop, ask the user where to put the documents, and
  write nothing there until they answer.
- Never create `index.md` or `log.md`, nor an index, cache, script, or ignore entry.

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

Open [`references/okf-spec.md`](references/okf-spec.md) for cases these
rules omit or another tool's OKF folder (§3.1 reserved filenames, §4.1
frontmatter, §5.4 status, §6 links/paths, §8 index, §9 log, §11 conformance).
