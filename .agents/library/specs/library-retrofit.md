---
title: Library retrofit
status: approved
topics: [library, documentation-archive, agent-skills, planning-plugin, implementation-planning]
supersedes: specs/documentation-archive-plugin-design.md
---

# Library retrofit

## Summary

Replace the SQLite ledger with a plaintext library at `.agents/library/`.
Specs, plans, and execution notes become Markdown files with a small
frontmatter block, committed beside the code they describe. The Library plugin
shrinks to one skill, `library`, that states the folder and frontmatter
convention and teaches agents how to find, read, pin, and compare documents.
Planning writes specs into the library, and Implementation writes plans and
execution handoff notes there, unconditionally, so the Library plugin is needed
only for discovery. This repository migrates its ten ledger documents, deletes
the ledger, and keeps this spec and its plan under the new convention.

## Context and motivation

Today the Library plugin stores documents as zlib payloads in
`.agents/ledger.db`, guarded by SQLite triggers, with a replay command for
combining binary conflicts. The ledger duplicates what version control already
provides: exact bytes, immutability, and history. Being binary, it cannot be
merged, diffed, reviewed in a pull request, grepped, or read without the
plugin's scripts. Its archive-and-delete step existed only to keep historical
documents out of `docs/`, and it left empty `docs/specs` and `docs/plans`
folders behind.

Planning and Implementation treat Library as optional and ask the user to
choose between Archive and Keep after every approval. That choice existed
because archiving required Python and SQLite. Writing a Markdown file to a
conventional path requires nothing, so the choice can go.

The repository already keeps agent process records as plain Markdown under
`.agents/execution/`. Specs and plans belong beside them under `.agents/`
rather than in `docs/`: `docs/` is the present-tense description of the
system and the default context source for humans, cold agents, and indexers,
while the library is a record of how the system got there and is true only as
of a revision.

## Goals and non-goals

Goals:

- Store specs, plans, and execution notes as committed Markdown under
  `.agents/library/`, versioned with the code.
- Keep the convention small enough to read and write without a parser or
  script.
- Let an agent find the current document on a subject, pin the version current
  at a revision, and compare revisions using only the file system and the
  active VCS.
- Remove the Archive/Keep decision and every ledger dependency from Planning
  and Implementation.
- Capture each whole-plan handoff as a committed library note before execution
  scratch is deleted.
- Migrate this repository's ledger losslessly and delete it.

Non-goals:

- Any reader, link checker, index, or sidecar script. One may be added later
  when evals show the need.
- Migration tooling for other repositories' ledgers. They migrate by hand, by
  an agent, following the README note.
- Changes to `.agents/execution/` semantics. It stays per-workspace, locally
  excluded, and deleted after handoff.
- Writing requirements summaries to the library.
- Automated promotion of durable content from the library into `docs/`.
- Byte-exact restore guarantees, immutability triggers, and replay. Version
  control covers them.
- Changes to the Maintenance plugin.

## Requirements and expected behavior

### Library convention

- Root: `.agents/library/`. It is committed and never ignored.
- Kinds: one folder per kind, named with a plural lowercase slug: `specs/`,
  `plans/`, `notes/`, or another plural slug when a new kind is needed. The
  folder is the kind. There is no `kind` field.
- Documents: `<kind>/<slug>.md`, with the slug matching
  `^[a-z0-9]+(-[a-z0-9]+)*$`. The filename is the document's identity. There
  is no `id` field.
- Frontmatter: a block delimited by `---` lines at the top of the file, one
  field per line, in this order when present:

  | Field | Required | Value |
  | --- | --- | --- |
  | `title` | always | one line of text |
  | `status` | specs and plans | `draft` or `approved`; omitted on other kinds, which are final when written |
  | `topics` | always | inline list of one or more slugs, such as `[auth, session-management]` |
  | `implements` | optional | one library-relative path, such as `specs/auth-sessions.md` |
  | `supersedes` | optional | one library-relative path |
  | `references` | optional | inline list of library-relative paths |

  No other fields, block lists, nesting, or quoting. Every field is one
  grep-able line. Paths are relative to `.agents/library/` and include `.md`.
- Body: free Markdown after the frontmatter block and one blank line. The spec
  template and the plan template's section structure are unchanged.
- Current: a document is current when its `status` is not `draft` and no
  non-draft document in the library names it in `supersedes`. A draft's
  `supersedes` takes effect when the draft is approved. Revisions of the same
  document are in-place edits. `supersedes` is used only when a differently
  named document replaces another. A `supersedes` target that does not exist
  yet affects nothing.
- Locator: a repository-relative path, written `path@revision` when pinned to
  a VCS revision such as a jj change id or a git commit. An unpinned locator
  means the working copy.

### Library skill

`plugins/library/skills/library/SKILL.md` is the plugin's only skill. Its
description triggers when a task needs to find, read, pin, or compare documents
under `.agents/library/`, or needs the library's convention. It covers:

- The layout and frontmatter contract above, with one complete example.
- Reading: list the kind folder, filter on frontmatter lines with grep, exclude
  drafts and superseded documents, read the selected file in full, follow
  `implements` and `references` only when the task needs them, and cite the
  path and revision.
- Pinning and comparing: read a pinned locator through the active VCS and
  compare revisions with the VCS diff. The skill shows both the jj and the git
  form and prefers neither.
- Boundaries: name the path explicitly because ripgrep and similar tools skip
  dot-folders by default; do not scan the whole library when the subject is
  known; `.agents/execution/` is scratch, not library content; the skill never
  writes documents, never creates an index, and never ignores the folder.

The plugin keeps no scripts, references, or tests. `plugins/library/README.md`
describes the convention for humans, installation, and a short legacy section
on migrating a 0.1.0 ledger by hand: open the database, read its schema,
decompress each document's zlib payload, read the topics and links tables,
write one library file per current document, then delete the ledger and its
`.gitignore` and `.gitattributes` entries.

### Planning: specs

- The draft is written to `.agents/library/specs/<slug>.md` with
  `status: draft`, a `title`, and `topics`, unless the user names another
  location. The repository-convention clause is removed; only an explicit
  user-supplied path overrides the library default.
- Review happens on that file. On explicit approval the skill sets
  `status: approved`, commits only that file through the active VCS workflow,
  verifies it entered history, and reports the locator with its revision.
  Without supported version control it leaves the file and reports it
  uncommitted.
- Revising an approved spec happens in place: set `status: draft`, review when
  the change is material, obtain explicit approval, set `approved`, commit.
- The Archive/Keep section, the skill-inventory check, and the `read-archive`
  guidance are removed. Later review against a preserved spec reads the file
  at its locator, through the VCS when a revision is given, and passes the
  content to the reviewer.
- The spec-review contract's "browse an archive" becomes "browse the
  library".

### Planning: requirements

- When history is plausibly relevant and `.agents/library/` exists, load the
  `library` skill if it is in the active inventory and read the current
  documents on the subject by kind and topic; without the skill, read the
  files directly. Do not search the library on every task. A missing library
  is not an error.

### Implementation: plans

- The approved specification is identified by its locator. A library spec
  must carry `status: approved`. For a spec supplied at a path outside the
  library, the user's explicit approval statement suffices, the plan omits
  `implements`, and the template's locator field holds the supplied path and
  revision.
- The draft is written to `.agents/library/plans/<slug>.md`, with the slug
  defaulting to the spec's slug, `status: draft`, a `title`, `topics`
  defaulting to the spec's, and `implements: specs/<slug>.md`. Only an
  explicit user-supplied location overrides that path; the
  repository-convention clause is removed.
- On explicit approval: `status: approved`, commit only the plan, verify,
  report the locator with its revision. A recording failure leaves the plan,
  reports it, and the plan is not execution-ready.
- In-place revision follows the same draft, review, approve, commit path as
  specs.
- The plan template's Approved specification section becomes one Locator
  line holding `path@revision`; its separate Approved version line and its
  archive wording are removed. The plan-review contract refers to plan and
  spec locators and forbids browsing the library beyond the supplied
  documents.

### Implementation: implementing-plans and subagent-execution

- Execution requires the plan at its locator with `status: approved`. When a
  locator pins a revision, the content is read through the VCS at that
  revision.
- The note takes the execution id the run already uses for its scratch
  directory. Scratch stays at `.agents/execution/<execution-id>/`, locally
  excluded, and its semantics are unchanged.
- All wording about pending Library preservation or database changes is
  removed from the skills, the execution-state reference, and the READMEs.
  The implementer brief tells workers not to browse the library, in place of
  "explore archives".
- Handoff note: at successful whole-plan handoff, in both the inline primary
  and the delegated supervisor flow, the primary writes
  `.agents/library/notes/<execution-id>.md` with a `title`, `topics` copied
  from the plan, and `implements: plans/<slug>.md` when the plan is a library
  document. A note for a plan at a user-supplied path outside the library
  omits `implements`; the body's Plan line records the locator. Its body
  records the plan
  and spec locators with revisions, the starting revision and resulting change
  set, whole-change checks, review outcomes and dispositions, limitations, and
  tactical decisions. The primary records the note as its own revision through
  the active VCS workflow after whole-change checks pass. Scratch is deleted
  only after the note is recorded. A recording failure leaves the note,
  reports it, and retains scratch under the existing rules.

### Manifests, READMEs, and marketplace

- Library's three manifests describe the plaintext library. The Codex
  manifest's keywords, interface strings, and default prompts follow.
- `plugins/library/README.md`, `plugins/planning/README.md`,
  `plugins/implementation/README.md`, the root `README.md`, and
  `.claude-plugin/marketplace.json` drop ledger and Archive/Keep language.
  Fixture examples in READMEs use library paths. The root README stops listing
  the library test command.
- `tests/test_marketplace.py` checks that Library exposes exactly the
  `library` skill, that its README links it, and that its Codex manifest keeps
  `skills` at `./skills/` with at most three default prompts.
- `tests/test_eval_runner.py` updates its specs fixture-path assertions to the
  library path and replaces its `read-archive` skill name with `library`.

### Evals

- The two Library suites and their fixtures are removed. A new
  `plugins/library/skills/library/evals/` suite uses file fixtures placed
  under `.agents/library/<kind>/` and covers: selecting the current document on a topic while excluding a
  draft and a superseded document; reading a pinned locator through the VCS
  when the working copy has moved on; answering a convention question with the
  layout and frontmatter instead of writing a script or index; and reading
  only the matching documents when the subject is known.
- Planning and Implementation suites replace Archive/Keep cases with
  approval-then-commit, unrelated-working-copy, and recording-failure cases;
  add an in-place revision case for specs and for plans; move spec and plan
  fixtures to library paths with frontmatter; replace the requirements
  suite's `reader-ledger.db` fixture with library file fixtures; remove the
  `subagent-execution` fixture copied to `.agents/ledger.db` together with
  its pending-preservation expectation; and expect the handoff note wherever
  a case reaches whole-plan handoff.

### Migration of this repository

Each ledger document becomes a library file at the path below with
`status: approved`, its `title` and `topics` from the ledger, and `implements`
from the ledger's links. Date prefixes are stripped and nothing else is
renamed. The body is the archived content, byte for byte, after the
frontmatter block and one blank line.

| Ledger `source_path` | Library path |
| --- | --- |
| `docs/superpowers/specs/2026-07-19-documentation-archive-plugin-design.md` | `specs/documentation-archive-plugin-design.md` |
| `docs/superpowers/plans/2026-07-19-documentation-archive-plugin.md` | `plans/documentation-archive-plugin.md` |
| `docs/specs/planning-plugin.md` | `specs/planning-plugin.md` |
| `docs/superpowers/plans/2026-08-29-planning-plugin.md` | `plans/planning-plugin.md` |
| `docs/specs/spec-to-integration-plugin.md` | `specs/spec-to-integration-plugin.md` |
| `docs/plans/implementation-plugin.md` | `plans/implementation-plugin.md` |
| `docs/specs/maintenance-coding-standards.md` | `specs/maintenance-coding-standards.md` |
| `docs/plans/maintenance-coding-standards.md` | `plans/maintenance-coding-standards.md` |
| `docs/specs/reviewing-coding-standards.md` | `specs/reviewing-coding-standards.md` |
| `docs/plans/reviewing-coding-standards.md` | `plans/reviewing-coding-standards.md` |

Each plan's `implements` names the spec on the row above it. After the files
are written and their bodies hash-match the ledger, `.agents/ledger.db` is
deleted together with its three `.gitignore` lines and the `.gitattributes`
file, whose only line is the ledger entry. This spec's `supersedes` link
resolves once the migration lands. The empty `docs/specs`, `docs/plans`, and
`docs/superpowers` folders are removed.

### Versions

Library moves to 0.2.0, and Planning and Implementation to 0.3.0, in each
plugin's `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`, as the
final task. Antigravity manifests carry no version.

### Quality requirements

- No runtime dependencies beyond Markdown and the active VCS. No skill commits
  a binary file.
- Each changed SKILL.md stays under 500 lines, references no removed Library
  resource, and links nothing outside its own plugin. Existing links between
  Implementation skills are unchanged.
- Prose stays VCS-neutral except where the jj and git forms are both shown.
- The convention is identical on Claude Code, Codex, and Antigravity.

## Technical design and constraints

A plan and the note written at its handoff:

```markdown
---
title: Authentication sessions plan
status: approved
topics: [auth, session-management]
implements: specs/auth-sessions.md
---
```

```markdown
---
title: Authentication sessions execution
topics: [auth, session-management]
implements: plans/auth-sessions.md
---

# Authentication sessions execution

- **Plan:** `.agents/library/plans/auth-sessions.md@kxqzmvtr`
- **Spec:** `.agents/library/specs/auth-sessions.md@pwrsnlqo`
- **Start:** `zrkzwyku` **Result:** `zrkzwyku..xooqszys`

## Whole-change checks

## Review outcomes and dispositions

## Limitations

## Tactical decisions
```

The note's headings are fixed so notes stay uniform across executions.

Reference patterns the skill shows, all plain grep over one-line fields:

```sh
grep -l '^status: approved' .agents/library/specs/*.md
grep -l '^topics: .*[[, ]auth[],]' .agents/library/*/*.md   # whole slug only
grep -rl '^supersedes: specs/auth-sessions.md' .agents/library   # then check each hit's status line; a draft hit does not count
jj file show -r kxqzmvtr .agents/library/specs/auth-sessions.md
git show kxqzmvtr:.agents/library/specs/auth-sessions.md
```

Existing skill text that names `docs/specs` or `docs/plans` as the write
location changes to the library paths. A user-supplied path still wins, and a
document the skills write there carries the same frontmatter without the link
fields, which are library-relative by definition.

## Alternatives and consequential decisions

- **Files over SQLite.** The ledger's hashing, triggers, dedupe, and replay all
  served the binary blob. Version control gives the same guarantees for text,
  and text merges.
- **In-repo over a sidecar.** The useful relation, which commits landed while a
  document state was current, is the commit graph when the document lives in
  it. A sidecar must reconstruct it from timestamps, which breaks under
  rebases.
- **`.agents/` over `docs/`.** Historical specs are near-duplicates of current
  docs and would dominate any index that does not understand supersession.
  Location is the only filter every tool honors.
- **No `id` or `kind` fields.** Both are the path.
- **Scalar `implements`.** One plan implements one spec, matching the plans
  skill.
- **A `status` field rather than an approved-only library.** Jujutsu snapshots
  the working copy, so "uncommitted" cannot mark a draft.
- **No scripts.** Grep over one-line fields is enough at this scale. An index
  can be derived from the files later; the reverse is not true.

## Verification

### Repository unit tests

`python3 -m unittest discover -s tests` verifies:

- Both marketplace indexes agree and every plugin has a README, a skills
  folder, and three parsable manifests with matching names.
- Library exposes exactly the `library` skill, its README links it, and its
  Codex manifest keeps `skills` at `./skills/` with at most three default
  prompts.

### Static text checks

- A case-insensitive search for `ledger`, `archiv`, and `read-archive` across
  `plugins/library`, `plugins/planning`, `plugins/implementation`, `tests/`,
  `README.md`, and `.claude-plugin/` matches only the Library README's legacy
  section. The Maintenance plugin, which uses "archive" as an ordinary verb,
  is out of scope and excluded from the search.
- Every changed SKILL.md is under 500 lines, and `plugins/library` contains no
  `.py` or `.db` file.
- The version fields in each plugin's Claude and Codex manifests are equal and
  at the stated numbers.

### Behavioral evals

Run through the repository's eval runner per suite:

- `library`: current-document selection excluding drafts and superseded
  documents; pinned reads through the VCS; convention answers without scripts;
  scoped reading when the subject is known.
- `specs`: draft written to the library path with `status: draft`; no commit
  before approval; approval sets `approved` and commits only the spec, leaving
  unrelated working-copy changes; in-place revision flips to draft and
  requires re-approval; no Archive/Keep prompt.
- `requirements`: reads current library documents when history is relevant
  and skips the draft and superseded ones; does not search on an unrelated
  task.
- `plans`: approved library spec required by locator with `status: approved`;
  an explicitly approved spec outside the library accepted without
  `implements`; plan written under `plans/` with `implements`; approval
  commits only the plan; recording failure reported as not execution-ready;
  in-place revision.
- `implementing-plans` and `subagent-execution`: refuses a plan without
  `status: approved`; reads pinned locators through the VCS; writes and
  records the handoff note before deleting scratch; retains scratch and
  reports when the note cannot be recorded.

### Migration check

One-time, in this repository:

- The ten files exist at the table's paths with the required frontmatter.
- For each file, the SHA-256 of the bytes after the frontmatter block and one
  blank line equals the ledger's `content_sha256` for that document.
- For each file, `title` equals the ledger title, `topics` equals that
  document's ledger topic set, and `implements` matches `document_links`:
  present on the five plans and absent on the five specs.
- The ledger, its `.gitignore` lines, the `.gitattributes` file, and the empty
  `docs/` subfolders are gone, and `jj status` shows no ledger path.
