---
type: spec
title: "OKF documents in docs"
description: "Makes Superstore's documents Open Knowledge Format concepts stored under docs/, with the library skill as the OKF encoder and approval recorded as stable with a verified field."
status: stable
verified: { by: human:Colton Hyer, at: 2026-11-22T01:42:41Z }
tags: [delivery-plugin, library, open-knowledge-format, agent-skills]
supersedes: docs/specs/library-retrofit.md
references: [docs/specs/specifications.md, docs/specs/review-loop.md, docs/specs/plan-execution.md, docs/specs/autonomous-execution.md, docs/specs/skill-checks.md]
---

# OKF documents in docs

## Summary

Superstore's documents become Open Knowledge Format (OKF) v0.2 concepts,
stored by default in flat folders under `docs/` (`docs/specs/`, `docs/plans/`,
and `docs/notes/` for both ordinary notes and `type: handoff` execution
receipts; or `docs/<plural>/` for other types). The library skill
becomes superstore's OKF encoder: it ships an unmodified copy of the OKF spec
and states only what OKF leaves open, namely document types, locations, extra
fields, when each status is set, and how to find, write, pin, and compare
documents. The `delivery` plugin ships eight public skills in one plugin
(`library`, `requirements`, `specs`, `plans`, `implementing-plans`,
`subagent-execution`, `reviewing-implementation`, and `verifying-changes`),
independent of `maintenance`, sharing OKF approval and commit checks through
plugin-level shared references rather than duplicating them across skills.
Approval sets OKF's `stable` and records the verifier in OKF's `verified` field
(`human:<approver>` on explicit human approval, or `process:delivery-autonomous`
on autonomous clean review per `docs/specs/autonomous-execution.md`); approving a
replacement also sets each replaced document to `deprecated` in the same commit.
This repository moves its documents from `.agents/library/` to `docs/`.

## Context and motivation

Library 0.2.0 fixes the location at `.agents/library/`, makes the folder the
document's kind, and uses fields no other tool understands: `topics`,
`status: approved`, and currency computed by following `supersedes` chains.
Only an explicit user-supplied path overrides the location.

Repositories keep their essential documents under `docs/`, and tools that read
Markdown knowledge commonly skip hidden folders. OKF v0.2, published by Google
under Apache 2.0, standardizes what those tools read: a required `type`; a
recommended `title`, one-sentence `description`, and `tags`; a lifecycle
`status` of `draft`, `stable`, or `deprecated`, where an absent status means
`stable`; reserved `index.md` and `log.md` files; and the rule that consumers
preserve unknown keys and never reject a document for them. A document that
follows OKF can be read by any OKF consumer without superstore-specific code.

This reverses 0.2.0's choice of `.agents/` over `docs/`. That choice kept
historical documents from crowding present-tense documentation. A `deprecated`
status, which any OKF consumer reads, now does that job, so location no longer
has to.

## Goals and non-goals

Goals:

- Every document a superstore skill writes is a valid OKF v0.2 concept.
- Documents live under `docs/` (`docs/specs/`, `docs/plans/`, and `docs/notes/`
  for `note` and `handoff` by default; `docs/<plural>/` for other types), and a
  repository can name other locations once in its agent instructions.
- An unmodified, pinned copy of OKF's `SPEC.md` inside the library skill is the
  single source for the format.
- One field, `status`, decides whether a document is current.
- `delivery` ships all eight local workflow and document skills in one plugin
  (with no dependency on `maintenance`, and `maintenance` with no dependency on
  `delivery`), keeping shared workflow and OKF commit rules in plugin-level
  shared references without missing-sibling-plugin hedging.
- This repository's documents migrate losslessly.

Non-goals:

- Requirements and decision documents; a later spec covers them.
- Changes to Rosetta or any other OKF consumer. No skill names one.
- The Maintenance plugin and its `docs/standards/` and `docs/reviews/` files.
  Nothing claims that `docs/` as a whole is an OKF bundle.
- Writing `index.md`, `log.md`, or OKF's provenance, trust, and computation
  families (`sources`, `generated`, `stale_after`, and the Attested
  Computation fields). The one exception is the `verified` line approval
  writes.
- Migration tooling, third-party OKF skills, validators, or MCP servers, and
  network access while a skill runs.
- Changes to `.agents/execution/` scratch semantics.

## Requirements and expected behavior

### Document format

Every document starts with a frontmatter block delimited by `---` lines, one
field per line, in this order when present:

| Field | Presence | Value |
| --- | --- | --- |
| `type` | always | `spec`, `plan`, or `handoff`; another lowercase slug, such as `note`, for a type no workflow owns |
| `title` | always | one line of text, in double quotes |
| `description` | always | one sentence, in double quotes |
| `status` | specs and plans | `draft`, `stable`, or `deprecated` |
| `verified` | approved specs and plans, when approval names a human or autonomous verifier | one line: `{ by: human:<approver>, at: <approval time> }` on explicit human approval, or `{ by: process:delivery-autonomous, at: <approval time> }` on autonomous clean review (`docs/specs/autonomous-execution.md`) |
| `tags` | always | inline list of one or more slugs, such as `[auth, session-management]` |
| `implements` | optional | one repository path (such as `docs/specs/auth-sessions.md`) or an inline list of repository paths (`[path-a, path-b]`) when a plan implements multiple specs |
| `supersedes` | optional | one repository path or an inline list of repository paths (`[path-a, path-b]`) for merges and splits |
| `references` | optional | inline list of repository paths |

- Superstore writes no block lists or nesting, so every field stays one
  grep-able line. `title` and `description` are always written in double
  quotes, with `\` and `"` inside them escaped as `\\` and `\"`, so any
  wording stays valid YAML; unquoted, a `: ` breaks the line and a ` #` cuts
  it short. No other field is quoted. OKF allows more; this is the subset
  superstore writes.
- A repository path is written the way locators are: relative to the
  repository root, without a leading slash, including `.md`.
- In `verified`, explicit human approval sets `by: human:<approver>`, where the
  approver is the user name version control is configured with, read by
  `jj config get user.name` or `git config user.name`, and the approval time is
  an ISO 8601 UTC instant such as `2026-11-01T18:30:00Z`. This is OKF's
  single-verifier form (§5.2), and a `human:` actor marks the document
  human-reviewed (§5.3, §7). When that name is empty or contains any of `,` `[`
  `]` `{` `}` `#` `:`, human approval writes no `verified` line and the report
  says so. Those characters would break the one-line form, and the rule also
  catches bot accounts such as `dependabot[bot]`. Explicitly authorized
  autonomous approval (`docs/specs/autonomous-execution.md`) writes
  `{ by: process:delivery-autonomous, at: <approval time> }`, marking the
  document OKF `machine-confirmed` (§5.2–§5.3) and never `human:`.
- The body is free Markdown after the frontmatter block and one blank line.
- A file is named `<slug>.md`. The slug matches `^[a-z0-9]+(-[a-z0-9]+)*$` and
  is neither `index` nor `log`, which OKF reserves (§3.1). Living specs
  (`docs/specs/`) keep undated domain slugs (`docs/specs/specifications.md`).
  New plans (`docs/plans/`), handoff notes (`<plan-slug>-handoff.md`, prefixed
  with `YYYY-MM-DD-` if `<plan-slug>` is undated), and point-in-time standalone
  notes (`docs/notes/`) default to `YYYY-MM-DD-<slug>.md` using the current
  date (unless the user names another filename for a standalone note);
  existing undated files remain valid and edit in place without renaming.
- A document without `status` is final when written. OKF reads an absent
  status as `stable` (§5.4).
- The `references` field is superstore's own and is unrelated to OKF's
  `references/` folder convention (§6.3).

### Locations

The folder for a document type resolves in this order:

1. A path the user names for this document.
2. A folder that `AGENTS.md` or `CLAUDE.md` at the repository root names for
   that type, in a sentence such as `Specs live in design/specs/.` For
   `handoff`, check for `handoffs` first and fall back to `notes`.
3. `docs/specs/` for `spec`, `docs/plans/` for `plan`, `docs/notes/` for
   `handoff` and `note`, and `docs/<plural>/` for any other lowercase type. Kind
   folders are flat.

Skills that read documents resolve folders in the same order. A document at a
one-off user path is still valid; readers find it when a task names it.

### Status and currency

- Specs and plans are written with `status: draft`.
- Explicit human approval sets `status: stable` and writes the `human:` `verified`
  line (omitting `verified` when the configured VCS user name is empty or invalid);
  explicitly authorized autonomous clean review sets `status: stable` and writes
  `process:delivery-autonomous` (`docs/specs/autonomous-execution.md`).
- When the approved document has `supersedes` (either a single path or an inline
  list `[path-a, path-b]`), approval iterates over every listed target: it sets
  each migrated target's `status` to `deprecated` unless it already is, reports
  unmigrated targets unchanged, and ignores missing targets. For a spec split,
  deprecate the split spec only once the replacement set is complete and approved.
  The commit holds the approved document and every file this step changed, and
  nothing else.
- When that commit is refused or fails, every file the step changed stays in
  the working copy with its new status and is reported uncommitted and not
  downstream-ready.
- Revising a stable document in place sets `status: draft` and removes its
  `verified` line, since the approved content is changing; approval sets `stable`
  and writes a new `verified` line. A mechanical blob-citation-only refresh on a
  `stable` plan whose tasks and content are unchanged commits without flipping to
  `draft` or re-requesting approval (`docs/specs/plan-execution.md`).
- A document is current when its `status` is absent or `stable`. The body of a
  `draft` or `deprecated` document is read only when a task asks for history
  or a comparison. `verified` records who approved a document and when; it
  does not decide whether the document is current (interactive downstream gates
  still route non-`human:` verified docs for confirmation per
  `docs/specs/autonomous-execution.md`).
- Superstore always writes `status` on specs and plans. A spec or plan without
  one is current to readers, as OKF says, but is not approved for planning or
  execution.

### Library skill

`plugins/delivery/skills/library/` holds `SKILL.md` and three references. Two
are byte-for-byte copies from `GoogleCloudPlatform/open-knowledge-format` at
commit `ad30107c31c06aec8a7d5636e0d1058118604e6f`:

- `references/okf-spec.md`: that commit's `SPEC.md` (OKF v0.2).
- `references/okf-LICENSE.md`: that commit's `LICENSE.md` (Apache 2.0). The
  repository has no NOTICE file.

The third, `references/pin-and-compare.md`, holds the Pin and compare
commands described below.

`SKILL.md`:

- Triggers on tasks that find, read, write, pin, or compare the repository's
  specs, plans, handoff notes, or other documents.
- States that every document is an OKF concept governed by
  `references/okf-spec.md`, and names its version, source URL, commit, and
  license file. The URL is plain text, not a link, so the skill links nothing
  outside its plugin.
- Covers, in sections: the document types, locations, and file names; the
  frontmatter table; the status rules; Find; Pin and compare; Write; and when
  to open the spec.
- **Document folders** are the resolved folders of `spec`, `plan`, `handoff`,
  and `note` (by default `docs/specs/`, `docs/plans/`, and `docs/notes/`), plus
  any folder `AGENTS.md` or `CLAUDE.md` at the repository root names for a type.
  A document of another type is found when a task names that type.
- **Find:** filter on frontmatter lines inside the document folders only,
  never the whole repository, whose eval fixtures and other Markdown can
  carry similar lines; a folder that does not exist yields no hits.
  Frontmatter is the block between the first two `---` lines at the top of a
  file: filter on those lines only, with any tool whose output is only that
  block's lines, never on a line of a body, where fenced examples can look
  like frontmatter.
  Rule documents out from their frontmatter lines before opening any body,
  even when the task or the user hands over a list of files: `head`, `cat`,
  and a version-control `show` or `diff` of a document count as reading its
  body, so they are not used to inspect frontmatter or to discover documents,
  and neither is version-control history. Keep only hits whose `status` is
  `stable` or absent; read only the bodies the answer depends on; follow link
  fields only when the task needs their content; cite each document by its
  path, by `<path>`, blob `<12-char hash>` for committed plans and handoffs
  (`docs/specs/plan-execution.md`), or by `path@revision` for ad-hoc pinned reads. Tags
  match as whole slugs, as today. A search for documents naming a path in
  `supersedes` covers every document folder and matches whole paths across both
  scalar (`supersedes: <path>`) and inline-list (`supersedes: [path-a, path-b]`)
  forms without prefix or suffix false matches. A Markdown file in a document
  folder, other than `index.md` and `log.md`, that has no `type` line or has a
  `status` outside OKF's three values is reported to the user as not yet
  migrated, never skipped silently. `.agents/execution/` is execution scratch, not
  a document folder.
- **Pin and compare:** `SKILL.md` states the locator and blob-pin rules and says
  to read `references/pin-and-compare.md` before computing or reading a
  12-character Git blob hash, resolving a revision, reading a document at a
  revision, comparing revisions, or listing a document's history. The reference
  documents computing and reading 12-character committed Git blob hashes in both
  Git and Git-backed Jujutsu repositories (including non-colocated Jujutsu via
  its Git store, `jj git root`), computed only from post-approval committed
  blobs rather than dirty working copies, alongside ad-hoc `path@revision` reads,
  revision comparisons, and history listing in both Jujutsu and Git forms.
  History from before a document moved stays at its old path: `jj log` on the
  new path stops at the move, so query the old path too; `git log --follow`
  follows the move.
- **Write:** writes documents of types no workflow owns, with the frontmatter
  above and the location order. It leaves the new document in the working
  copy and commits nothing; recording it belongs to the user or the workflow
  that asked for it. It never writes or changes a `spec`, `plan`, or
  `handoff`, whose skills own approval and recording. Before writing the
  first document of a type to a default folder that already exists, it checks
  that the folder holds no Markdown without OKF frontmatter, other than
  `index.md` and `log.md`, such as another tool's reports; if it does, it asks
  the user where the documents should go. It never creates `index.md`,
  `log.md`, an index, a cache, or a script, and never adds a document folder
  to an ignore file.
- **When to open the spec:** a type or case these rules do not cover, or an
  OKF folder another tool wrote. It points to sections by number: §3.1
  reserved filenames, §4.1 frontmatter, §5.4 status, §6 links and paths, §8
  index files, §9 log files, §11 conformance.

### Delivery: specs

- The draft carries `type: spec`, `title`, `description`, `status: draft`, and
  `tags`; it adds `supersedes` (scalar or inline list) only when it replaces or
  splits differently named specs.
- The draft's location follows the location order, replacing "only an
  explicit user-supplied path overrides it".
- Approval follows the status rules, shared through plugin-level shared
  references (`plugins/delivery/references/`). The recording check runs on every
  committed path: with Jujutsu, `jj diff -r @ <path>` prints nothing and
  `jj log -r @- <path>` shows a new revision for each; with Git,
  `git status --porcelain <path>` prints nothing and `git log -1 -- <path>`
  shows the new commit for each.
- Link fields are repository paths and valid at any location, so the special
  cases for documents outside the library are removed.
- Downstream committed plans and handoffs cite the approved spec by repository
  path and 12-character committed Git blob hash (`<path>`, blob `<12-char hash>`,
  per `docs/specs/plan-execution.md`); ad-hoc revision reports may still use
  `path@revision` when quoting history.
- Spec Reviewer A (`docs/specs/review-loop.md`) is forbidden from browsing
  repository code or documents beyond the supplied requirements and draft;
  Reviewer B reads repository code read-only.

### Delivery: requirements

When history is plausibly relevant, the requirements skill reads the current
documents on the subject, by type and tags, in the resolved locations (by
default `docs/specs/`, `docs/plans/`, `docs/notes/`). It applies the currency
rule above. A missing document folder is not an error, and it does not search
on every task. Its completion gate requires the summary to state what happens
today and what the change makes different (answered from the repository when
possible, asking the user only when it cannot, or stating that nothing handles
this today for something new).

### Delivery: plans

- Every repository spec document (`type: spec`) the plan implements must be
  committed, clean, and carry a `status: stable` line
  (`docs/specs/plan-execution.md`); interactive confirmation of non-`human:`
  verified specs follows `docs/specs/autonomous-execution.md`. A spec supplied
  in another form, including a file without that frontmatter or a `type: spec`
  file without a status line, needs the user's explicit approval statement.
- The draft carries `type: plan`, `title`, `description`, `status: draft`,
  `tags` defaulting to the implemented spec(s)' tags, and `implements` naming
  the spec's repository path (or an inline list `[path-a, path-b]` when one plan
  implements multiple repository specs; omitted when none are repository files).
  It adds `supersedes` (scalar or inline list) only when it replaces differently
  named plans. Its location follows the location order (default `docs/plans/`).
  New plans default to `YYYY-MM-DD-<name>.md` using the current date when
  first drafted, where `<name>` defaults to the spec's slug when targeting one
  living spec with no earlier plan, or a change-scoped slug when targeting
  multiple specs or a living spec that already has an earlier plan
  (`docs/specs/plan-execution.md`); existing undated plans remain valid and edit
  in place without renaming.
- Approval, revision, recording, and committed blob pinning follow the shared
  plugin-level reference rules (`plugins/delivery/references/`).
- The plan-review contract forbids browsing the repository's documents beyond
  the supplied plan and spec(s).

### Delivery: execution gate

`implementing-plans` and `subagent-execution` require a committed, clean plan
with a `status: stable` line (and every repository spec named in `implements`
committed and clean, per `docs/specs/plan-execution.md`). A plan whose status is
`draft` or `deprecated`, that has no status line, or that is uncommitted or dirty
is not execution-ready and routes back through `plans`. Interactive runs
encountering a non-`human:` verified plan follow
`docs/specs/autonomous-execution.md`. The two passages must agree, and the
Delivery README states the same gate.

### Delivery: handoff notes

`implementing-plans`, its `execution-state.md`, and `subagent-execution` write
the handoff note to `<notes/handoffs folder>/<handoff-slug>.md` (appending
`-2`, `-3` on collision, per `docs/specs/plan-execution.md`), resolving the
folder in order: user-named path, a folder root `AGENTS.md` or `CLAUDE.md`
names for handoffs or else for notes, then `docs/notes/` by default. The
filename is `<plan-slug>-handoff.md` when `<plan-slug>` starts with
`YYYY-MM-DD-`, or `YYYY-MM-DD-<plan-slug>-handoff.md` (current execution date)
when `<plan-slug>` is undated or from a non-repository plan. The note carries
`type: handoff`, `title` (the plan's title without its trailing word `plan`, in
any letter case, followed by ` execution`), a one-sentence `description` of what
the execution delivered, `tags` copied from the plan, and `implements` naming
the plan's repository path when the plan is a repository file. The slug must
satisfy the file-name rule above. Its body carries blob citations for the plan
and every implemented repository spec, a `Change` line, and fixed
`## Decisions for review` and `## Tactical decisions` headings
(`docs/specs/plan-execution.md`). Recording rules and scratch handling stay
unchanged. `type: note` stays free for ordinary notes, which the library skill
writes.

### READMEs, manifests, and REVIEW.md

- `plugins/delivery/README.md` describes the OKF convention, the default
  location and how a repository names its own, and the copied spec and its
  license. It drops the argument for `.agents/` over `docs/`. It carries
  migration notes, each targeting `docs/` (`docs/specs/`, `docs/plans/`,
  `docs/notes/`, or `docs/<plural>/`) with OKF frontmatter, for a
  0.2.0 library, a 0.1.0 ledger, and documents that Planning or
  Implementation 0.2.0 wrote under `docs/` without frontmatter; those gain
  frontmatter in place, since their file names already fit the slug rule. It
  lists the steps to upgrade the copied spec: replace the two copied files
  from a newer commit, update SKILL.md's version and commit line and the unit
  test's checksums, and bump Delivery's version.
- The Delivery and root READMEs describe the consolidated `delivery` plugin,
  document paths, and fields.
- Delivery's manifests and marketplace entries describe the eight local workflow
  and OKF document skills under `docs/`. The Codex manifest's interface
  strings follow, with at most three default prompts.
- `REVIEW.md` references the `delivery` document locations, twin-passage rules
  (reduced where shared plugin-level references replace duplicated passages),
  and committed blob-pinned handoff format.

### Eval runner

The runner configures the commit identity
`Eval Reviewer <eval-reviewer@example.invalid>` in each eval workspace, in
both its Jujutsu repository config and its Git config, so approval cases
record a `verified` line under the rule above.

### Migration of this repository

- Every document under `.agents/library/` moves to `docs/<kind>/<slug>.md`
  with its slug unchanged: six specs, six plans, and one handoff note, plus
  this spec and its plan. The handoff note moved initially to `docs/handoffs/`
  (and subsequently into `docs/notes/` alongside the other repository handoffs).
- Frontmatter: `type` from the old folder, with `notes/` becoming `handoff`;
  `title` unchanged in wording and written in double quotes; a new
  one-sentence `description`; `status: approved` becomes `stable`, except that
  each document named in a non-draft document's `supersedes` becomes
  `deprecated` (`documentation-archive-plugin-design.md` and
  `library-retrofit.md`); `topics` becomes `tags` with the same values in the
  same order; link fields become repository paths under `docs/`.
- No migrated document gains `verified`: who approved it and when was never
  recorded reliably, and the migration does not invent it.
- Each body stays byte-identical. Locators inside bodies keep their old paths,
  which still resolve at the revisions they name.
- `.agents/library/` is removed.
- The handoff note for this change's own execution was initially written under
  `docs/handoffs/` (and subsequently moved into `docs/notes/`).

### Versions

For any changeset that alters a skill or its references under `plugins/delivery/`,
bump `delivery`'s version once for the whole changeset in both
`.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`, keeping the two
equal.

### Quality requirements

- No runtime dependency beyond Markdown and the active version control, and
  no network access while a skill runs.
- `delivery` has no dependency on `maintenance`, and `maintenance` has no
  dependency on `delivery`.
- Identical behavior on Claude Code, Codex, and Antigravity.
- Every plugin `SKILL.md` stays within 240 lines, the most codex reads in one
  pass, and links nothing outside its own plugin.
- Prose stays neutral between Jujutsu and Git except where both forms are
  shown.

## Technical design and constraints

A spec, a plan, and a handoff note:

```markdown
---
type: spec
title: "Authentication sessions"
description: "Rotate session tokens on privilege change and expire idle sessions."
status: stable
verified: { by: human:Sam Kim, at: 2026-11-01T18:30:00Z }
tags: [auth, session-management]
---
```

```markdown
---
type: plan
title: "Authentication sessions plan"
description: "Three tasks that add token rotation and the idle-session timeout."
status: draft
tags: [auth, session-management]
implements: docs/specs/auth-sessions.md
---
```

```markdown
---
type: handoff
title: "Authentication sessions execution"
description: "Token rotation and the idle timeout landed and passed whole-change checks."
tags: [auth, session-management]
implements: docs/plans/2026-11-01-auth-sessions.md
---
```

Frontmatter is the block between the first two `---` lines at the top of a
file. The skill filters on those lines only, with any tool whose output is
only that block's lines (the example's `awk` scans the whole file but prints
only those lines); a YAML parser is fine when the environment has one. Its
portable example prints each file's frontmatter lines as `FILE: line` with POSIX
`awk` and pipes them into `grep`; `find` reports a missing folder and carries
on, where `awk` alone stops at the first path it cannot open, and `-H`
follows a document folder that is a symbolic link:

```sh
find -H docs/specs -maxdepth 1 -name '*.md' ! -name index.md ! -name log.md \
  -exec awk '{ sub(/\r$/, "") }
       FNR == 1 { fm = ($0 == "---"); next }
       fm && /^---$/ { fm = 0 }
       fm { print FILENAME ": " $0 }' {} + | grep ': status: stable$'
```

Specs and plans always carry `status`, so this lists the current specs; a
document of another type is current when it has no `status` line or
`status: stable`. Other filters change the `grep` or the folders:
`': tags: .*[[, ]auth[],]'` over `docs/specs docs/plans` matches a whole tag
slug, and a delimiter-safe whole-path match over `: supersedes:` across every
document folder (matching both scalar `supersedes: <path>` and inline-list
`supersedes: [path-a, path-b]` without prefix or suffix false matches) finds a
replaced document. The not-yet-migrated report prints files whose frontmatter
has no `type` line, including an empty file, or whose `status` is outside the
three values, except `index.md` and `log.md`:

```sh
find -H docs/specs docs/plans docs/notes -maxdepth 1 -name '*.md' ! -name index.md ! -name log.md \
  \( -size 0 -print -o -exec awk '{ sub(/\r$/, "") }
       FNR == 1 { if (f != "" && !t) print f; f = FILENAME; t = 0; fm = ($0 == "---"); next }
       fm && /^---$/ { fm = 0 }
       fm && /^type: / { t = 1 }
       fm && /^status: / && !/^status: (draft|stable|deprecated)$/ { print FILENAME }
       END { if (f != "" && !t) print f }' {} + \) | sort -u
```

## Alternatives and consequential decisions

- **OKF over a private convention.** OKF owns the fields superstore shares
  with other tools. Each tool follows it independently, so none encodes
  another's vocabulary.
- **An unmodified, pinned copy over a link or a curated summary.** The copy
  works offline and identically on every host, cannot change underneath its
  readers, and is reviewed when upgraded. A link needs network access and
  follows a moving branch; a curated summary drifts from upstream. The
  maintained repository is `open-knowledge-format`; the copy under
  `knowledge-catalog/okf/` is a frozen snapshot.
- **Pin and compare in a reference file, with `SKILL.md` within 240 lines.**
  Codex reads a skill in 240-line chunks and often stops after the first, so
  rules past line 240 go unread: in the follow-up evals, every codex
  `library/9` failure read only lines 1 to 240, when the Write rules began at
  line 248. Moving the Pin and compare commands to a reference, loaded when a
  task pins, compares, or lists history, together with dropping the complete
  spec example and moving Find's construction notes to the README, keeps
  every rule in the first chunk.
- **A POSIX `awk` extractor over a YAML parser.** It needs no runtime beyond
  the shell tools the skills already use; Python and Node ship no YAML parser
  in their standard libraries. A parser the environment already has is still
  allowed.
- **OKF's status values over `approved`.** Currency becomes one field any OKF
  reader understands. The cost is a second file in a replacement's approval
  commit.
- **Approval recorded in `verified` over a custom `approved` value.** Every
  value stays standard OKF: human approval shows as OKF's human-reviewed tier
  (`human:`), autonomous approval shows as OKF's machine-confirmed tier
  (`process:delivery-autonomous`), and the file names who verified it and when.
  `status` alone still decides currency.
- **`docs/` over `.agents/`.** Hidden folders are skipped by indexers and many
  tools. A `deprecated` status, not location, now keeps old documents out of
  current answers.
- **`handoff` in frontmatter, stored in `docs/notes/`.** Keeping `type: handoff`
  in frontmatter leaves `type: note` free for ordinary notes written by `library`
  and lets tools filter execution receipts cleanly, while storing them in
  `docs/notes/` avoids a fourth top-level folder for another point-in-time
  supplementary artifact.
- **Shared plugin-level references within `delivery`.** `library`, `requirements`,
  `specs`, `plans`, `implementing-plans`, `subagent-execution`,
  `reviewing-implementation`, and `verifying-changes` ship together in
  `delivery`, sharing OKF approval/commit checks and workflow rules via
  `plugins/delivery/references/` rather than duplicating twin passages across
  skills. Single-skill eval cases load one skill alongside plugin-level shared
  references (`docs/specs/skill-checks.md`).
- **Repository paths without a leading slash.** Link fields use the same form
  as locators. OKF's `/`-prefixed form means a bundle root, which superstore
  does not declare, and reads as the filesystem root outside OKF.
- **The library skill writes only unowned types.** Approval stays with the
  workflows that run it.

## Verification

### Repository unit tests

`python3 -m unittest discover -s tests` verifies:

- Both marketplace indexes agree, and every plugin has a README, a skills
  folder, and parsable manifests with matching names.
- `delivery` exposes its eight public skills, its README links them, and every
  relative link across its README, skills, and plugin-level shared references
  resolves.
- Every plugin `SKILL.md` (`plugins/*/skills/*/SKILL.md`) is within 240 lines.
- The eval-runner fixture assertions use `docs/specs/approved-spec.md`, and a
  prepared eval workspace reports `Eval Reviewer` from both
  `jj config get user.name` and `git config user.name`.
- The SHA-256 of `references/okf-spec.md` is
  `26aa5da029278939f914e578107242d9607d4f2dc5fe153272b82f9ed1030101`, and
  that of `references/okf-LICENSE.md` is
  `8c6db340475136df3c1201d458fa5755698eace76e510471ecc9d857d6083dac`, matching
  the files at the pinned commit, so any edit to the copies fails the tests.

### Static checks

- A search for `.agents/library` across `plugins/`, `tests/`, the READMEs,
  `REVIEW.md`, both marketplace indexes, and every `plugin.json` matches only
  migration notes.
- Every plugin `SKILL.md` is within 240 lines and links nothing outside its
  plugin.
- Every changed shell snippet runs in a scratch repository with
  `JJ_CONFIG=/dev/null JJ_EDITOR=false GIT_EDITOR=false` and stdin from
  `/dev/null`.
- The version fields in each changed plugin's two manifests are equal.

### Migration check

- Fifteen documents exist under `docs/specs/`, `docs/plans/`, and (as
  migrated initially) `docs/handoffs/` (subsequently moved into `docs/notes/`)
  with the required fields, a `type` matching their kind, the
  specified statuses, and `tags` equal to their former `topics`. Every
  `title` and `description` line is double-quoted, and none carries
  `verified`.
- For each document, the SHA-256 of the bytes after the frontmatter block and
  one blank line equals that of its pre-migration body.
- `.agents/library/` is gone, and
  `jj file show -r xooqszys .agents/library/plans/library-retrofit.md` still
  prints the plan.

### Behavioral evals

Run through the repository's eval runner, with fixtures moved to `docs/`
paths and OKF frontmatter:

- `library`: selects the current document by status, excluding `draft` and
  `deprecated` ones; reads a pinned version through version control; answers a
  convention question with the OKF fields and default `docs/` folders
  (`docs/specs/`, `docs/plans/`, `docs/notes/`, and `docs/<plural>/`) without writing a
  script or index; reads only matching documents when the subject is known;
  honors a location named in `AGENTS.md`; writes a document of an unowned type
  with valid frontmatter and leaves it uncommitted; opens
  `references/okf-spec.md` for a case its rules do not cover; reports a file
  with no `type` line in a document folder as not yet migrated, while a
  migrated document whose body holds fenced example frontmatter is neither
  reported as not yet migrated nor taken as current from a body line; asks
  where to put a new type whose default folder holds another tool's files
  without OKF frontmatter. Fixtures keep ordinary notes as `type: note` in `docs/notes/`.
- `specs`: writes the draft to `docs/specs/` with `type: spec` and
  `status: draft`; honors a location named in `AGENTS.md`; makes no commit
  before approval; approval sets `stable`, writes `verified` with the approver
  and a UTC time, and commits only the spec; approving
  a replacement also sets the replaced spec to `deprecated` in the same
  commit; in-place revision returns to `draft`, removes `verified`, and needs
  approval again, and
  re-approving a revised replacement commits only the spec when its target is
  already `deprecated`.
- `plans`: requires a `stable` spec; accepts a spec without frontmatter on
  explicit approval; drafts new plans at `docs/plans/YYYY-MM-DD-<slug>.md`
  with `implements` as a repository path (leaving existing undated plans valid);
  approval and replacement commits behave as for specs; a recording failure is
  reported as not execution-ready.
- `implementing-plans` and `subagent-execution`: refuse a plan that is not
  committed, clean, and `stable`; write and record the handoff note in
  `docs/notes/` named `<plan-slug>-handoff.md` (prefixing `YYYY-MM-DD-` if
  `<plan-slug>` is undated, and appending `-2`, `-3` on collision) with
  `type: handoff`, `implements`, blob citations, and fixed decision headings
  before deleting scratch.
- `requirements`: reads current documents under `docs/` when history is
  relevant, skips `draft` and `deprecated` ones, states what happens today
  and what changes in the summary, and does not search on an unrelated task.
