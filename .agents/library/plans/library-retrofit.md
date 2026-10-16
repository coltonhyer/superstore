---
title: Library retrofit plan
status: approved
topics: [library, documentation-archive, agent-skills, planning-plugin, implementation-planning]
implements: specs/library-retrofit.md
---

# Library retrofit plan

## Approved specification

- **Locator:** `.agents/library/specs/library-retrofit.md@xooqszys`

## Approach

Migrate this repository's ledger first, so the library has content, the
spec's `supersedes` target exists, and the old reader is no longer needed.
Replace the Library plugin next, then switch Planning and Implementation onto
the library in one recorded task each, keeping the unit tests green after
every task. Run the affected behavioral eval suites, then bump versions last,
as AGENTS.md requires.

The executing primary follows the approved spec for its own whole-plan
handoff: it writes and records `.agents/library/notes/<execution-id>.md`
before deleting scratch, even though the installed Implementation skills
predate that rule.

## Tasks

### T1: Migrate the ledger into the library and remove it

- **Spec references:** Migration of this repository; Library convention;
  Verification, Migration check.
- **Deliverable:** The ten files listed in the spec's migration table exist
  under `.agents/library/specs/` and `.agents/library/plans/`, each with
  `title` and `topics` from the ledger, `status: approved`, and on the five
  plans an `implements` line naming the spec from the ledger's
  `document_links`. Each body is the archived content byte for byte after the
  frontmatter block and one blank line. `.agents/ledger.db`, the three ledger
  lines in `.gitignore`, the `.gitattributes` file, and the empty `docs/specs`,
  `docs/plans`, and `docs/superpowers` folders are removed.
- **Prerequisites and order:** None. First task.
- **Relevant paths and patterns:** `.agents/ledger.db` tables `documents`
  (`source_path`, `title`, `content_zlib`, `content_sha256`),
  `document_topics`, and `document_links`. Read it with Python's `sqlite3`
  and `zlib` from the standard library, run with `python3 -I`, from a script
  kept outside the repository. Write topics in the ledger's row order. Do not
  normalize newlines or trailing whitespace in bodies. Verify before deleting
  anything. Do not commit or record on the user's behalf beyond the task's own
  recording.
- **Completion check:** Before deletion, a comparison over all ten documents
  prints one `OK` line per document establishing that the SHA-256 of the
  bytes after the frontmatter block and one blank line equals the ledger's
  `content_sha256`, `title` equals the ledger title, the `topics` set equals
  the ledger's topic set, and `implements` matches `document_links`; that
  output is attached to the task report. After deletion,
  `test ! -e .agents/ledger.db && test ! -e .gitattributes && ! grep -q ledger .gitignore && test ! -d docs/specs && test ! -d docs/plans && test ! -d docs/superpowers`
  succeeds. A reviewer can repeat the comparison against the ledger in the
  task's parent revision with `jj file show -r <task-revision>- .agents/ledger.db`.

### T2: Rewrite the Library plugin as one convention-and-reading skill

- **Spec references:** Library convention; Library skill; Manifests, READMEs,
  and marketplace; Evals, Library suite; Technical design and constraints;
  Quality requirements.
- **Deliverable:** `plugins/library/skills/library/SKILL.md` with `name:
  library`, a description that triggers on finding, reading, pinning, or
  comparing documents under `.agents/library/` or needing the convention, and
  the content the spec lists: layout and frontmatter contract with one
  complete example, the reading workflow, pinning and comparing in both jj and
  git forms, and the boundaries. `plugins/library/skills/library/evals/
  evals.json` with per-file fixtures under `evals/files/` targeting
  `.agents/library/<kind>/` paths and the four cases the spec names: current
  document on a topic excluding a draft and a superseded document; a pinned
  read through the VCS where the same target is a `baseline` fixture and a
  changed `working` fixture; a convention question answered without writing a
  script or index; scoped reading when the subject is known. The
  `archiving-documentation` and `read-archive` skills, their scripts,
  references, eval fixtures, and `plugins/library/tests/` are removed.
  `plugins/library/README.md` is rewritten for the convention, installation,
  and the legacy-ledger migration section. The three Library manifests, the
  root `README.md` plugin row and Tests section, and
  `.claude-plugin/marketplace.json` describe the plaintext library.
  `tests/test_marketplace.py` gains a Library check: exactly the `library`
  skill under `skills/`, its README links it, and the Codex manifest keeps
  `skills` at `./skills/` with at most three `defaultPrompt` entries. The
  `skills` arrays of Implementation `plans` case 7 and Planning `specs` case 6
  drop `archiving-documentation` and `read-archive`, and nothing else in
  those cases changes here, so `test_implementation_case_skill_links_resolve_in_copied_layout`
  keeps resolving every case until T3 and T4 rewrite them.
- **Prerequisites and order:** T1.
- **Relevant paths and patterns:** Eval JSON shape
  `{"skill_name": ..., "evals": [{id, prompt, expected_output, skills?, files, replies?, expectations}]}`
  with fixture entries `{source, target, state}` where `state` is `baseline`
  or `working`; `scripts/skill_eval_core.py` resolves `skills` names against
  `plugins/*/skills/<name>` and copies only regular files. Follow the
  `test_maintenance_has_two_public_skills_and_valid_links` pattern in
  `tests/test_marketplace.py`. Codex manifest fields to update: `description`,
  `keywords`, `interface.shortDescription`, `interface.longDescription`,
  `interface.defaultPrompt`. Keep the SKILL.md under 500 lines and
  VCS-neutral except where both VCS forms are shown. Use the topic grep that
  delimits on the inline list syntax, not `\b`. The runner commits `baseline`
  fixtures as one commit described `eval fixture`, so the pinned-read prompt
  names its revision by that description, which the subject resolves with
  the VCS, as `subagent-execution` case 2 already does.
- **Completion check:** `python3 -m unittest discover -s tests` passes;
  `find plugins/library -name '*.py' -o -name '*.db' -o -name __pycache__`
  prints nothing; `wc -l plugins/library/skills/library/SKILL.md` is under
  500; `python3 -c "import json;json.load(open('plugins/library/skills/library/evals/evals.json'))"`
  succeeds; `grep -rniE 'ledger|archiv|read-archive' plugins/library README.md .claude-plugin`
  matches only the README's legacy section.

### T3: Move Planning onto the library

- **Spec references:** Planning: specs; Planning: requirements; Manifests,
  READMEs, and marketplace; Evals, Planning suites; Quality requirements.
- **Deliverable:** `plugins/planning/skills/specs/SKILL.md` writes drafts to
  `.agents/library/specs/<slug>.md` with `status: draft`, `title`, and
  `topics`, overridden only by an explicit user path; on approval sets
  `status: approved`, commits only that file through the active VCS workflow,
  verifies, and reports `path@revision`; handles in-place revision; reads a
  preserved spec by locator for later review; and no longer contains the
  Archive/Keep section, the skill-inventory check, or `read-archive`.
  `references/spec-review.md` says "browse the library".
  `plugins/planning/skills/requirements/SKILL.md` replaces its `read-archive`
  bullets with the library guidance in the spec. `plugins/planning/README.md`
  replaces the Optional Library integration section and the `read-archive`
  example, and its fixture example uses a library path. The specs eval suite
  keeps case 1 declaring `requirements` and case 2 declaring no extra skill,
  replaces cases 6 and 9's Archive/Keep expectations with
  approval-then-commit behavior, makes case 8 the recording-failure case
  where the prompt states that no supported version control is available and
  the expected outcome is the approved file left in place and reported as
  uncommitted, makes case 7 the unrelated-working-copy case
  with `approved-spec.md` at `.agents/library/specs/approved-spec.md` in
  `working` state beside `README.md`, adds an in-place revision case, and
  moves every spec fixture to a library path with frontmatter. The
  requirements suite replaces case 4's `reader-ledger.db` fixture with
  library file fixtures covering a current spec, a superseded spec with its
  superseder, and a draft, declaring the `library` skill, and removes
  `files/reader-ledger.db`. `tests/test_eval_runner.py` asserts the specs
  case 7 path at `.agents/library/specs/approved-spec.md` and uses `library`
  in place of `read-archive`.
- **Prerequisites and order:** T2, so the `library` skill resolves for eval
  `skills` entries. Independent of T4.
- **Relevant paths and patterns:** `planning_case("specs", 1)`,
  `planning_case("specs", 2)`, `planning_case("specs", 7)`, and
  `planning_case("requirements", 1)` are loaded by `tests/test_eval_runner.py`;
  keep those ids meaningful. Fixture spec files start with the frontmatter
  block from the spec's convention. Keep both SKILL.md files under 500 lines.
- **Completion check:** `python3 -m unittest discover -s tests` passes;
  `grep -rniE 'ledger|archiv|read-archive' plugins/planning tests` prints
  nothing; `grep -rn 'Archive' plugins/planning` prints nothing; both
  `wc -l plugins/planning/skills/*/SKILL.md` counts are under 500; both eval
  files load as JSON.

### T4: Move Implementation onto the library

- **Spec references:** Implementation: plans; Implementation:
  implementing-plans and subagent-execution; Manifests, READMEs, and
  marketplace; Evals, Implementation suites; Technical design and
  constraints; Quality requirements.
- **Deliverable:** `plugins/implementation/skills/plans/SKILL.md` identifies
  the spec by locator, requires `status: approved` on a library spec and
  accepts an explicitly approved spec outside the library without
  `implements`, writes drafts to `.agents/library/plans/<slug>.md` with the
  frontmatter the spec lists, overridden only by an explicit user path,
  commits only the plan on approval and reports `path@revision`, reports a
  recording failure as not execution-ready, handles in-place revision, and
  drops Archive/Keep and `read-archive`. `references/plan-template.md` has one
  Locator line holding `path@revision` and no Approved version line.
  `references/plan-review.md` names plan and spec locators and forbids
  browsing the library beyond the supplied documents.
  `skills/implementing-plans/SKILL.md` requires `status: approved`, reads
  pinned locators through the VCS, drops the Library database sentence, and
  writes and records the handoff note before cleanup in the inline flow.
  `skills/subagent-execution/SKILL.md` drops the pending-preservation wording
  in Dispatch and requires the note in Finish. `references/execution-state.md`
  drops the Pending preservation bullet and describes the note at final
  handoff with the body headings from the spec. `references/implementer-brief.md`
  says "browse the library". `plugins/implementation/README.md` drops the
  Library paragraph and pending-preservation sentence. Evals: the plans suite
  replaces cases 7, 8, and 9 with approval-then-commit, unrelated working
  copy, and recording failure, makes case 10 an in-place revision, keeps
  case 3's spec fixture at `docs/specs/portfolio.md` with the prompt stating
  explicit approval and expects a plan without `implements`, adds case 11
  where a library spec with `status: draft` is refused, and moves every other
  spec and plan fixture to library paths with frontmatter; the
  subagent-execution suite removes case 1's `pending-preservation.txt`
  fixture and its ledger expectation, expects the handoff note wherever a
  case reaches Finish, and adds one case where the prompt states that
  recording the note fails, expecting the note left in place, the failure
  reported, and scratch retained; the implementing-plans suite moves fixtures
  to library paths with `status: approved`, expects the note where a case
  completes the whole plan, adds one case whose plan and spec locators are
  pinned `path@revision` with the revision named by the `eval fixture`
  description, and adds one case that refuses a plan whose `status` is
  `draft`.
- **Prerequisites and order:** T2. Independent of T3.
- **Relevant paths and patterns:** `tests/test_marketplace.py` requires the
  five Implementation skill folders and README links to stay as they are.
  Note frontmatter: `title`, `topics` copied from the plan, and `implements:
  plans/<slug>.md` only for a library plan; body headings Whole-change
  checks, Review outcomes and dispositions, Limitations, Tactical decisions,
  preceded by the Plan, Spec, Start, and Result lines. The note takes the
  run's existing execution id. Keep every SKILL.md under 500 lines and the
  existing links between Implementation skills unchanged.
- **Completion check:** `python3 -m unittest discover -s tests` passes;
  `grep -rniE 'ledger|archiv|read-archive' plugins/implementation` prints
  nothing; `grep -rn 'Archive' plugins/implementation` prints nothing; all
  five `wc -l plugins/implementation/skills/*/SKILL.md` counts are under 500;
  all eval files load as JSON.

### T5: Run the affected eval suites and record the writeup

- **Spec references:** Verification, Behavioral evals.
- **Deliverable:** The `library`, `specs`, `requirements`, `plans`,
  `implementing-plans`, and `subagent-execution` suites run through
  `scripts/run_skill_evals.py` with the matrix the user approved: hosts
  `codex`, `claude`, and `agy` at the defaults in
  `scripts/skill_eval_hosts.py`, one run per case, each plugin run with
  `--output .agents/eval-results/<date>-library-retrofit/<plugin>`, in two
  stages. Stage 1 runs all six suites on `claude`; material failures are
  corrected in skill text and only the affected cases rerun on `claude` as
  follow-ups. Stage 2 runs all six suites on `codex` and `agy` and handles
  host-specific failures the same way. A host that is unavailable in the
  executing environment leaves this task incomplete for that host and is
  reported as a limitation; it does not narrow the matrix. One writeup at
  `evals/notebook/writeups/<date>-library-retrofit.md` covers both stages and
  follows the existing writeup structure, and `evals/notebook/BOOK.md` gains
  one Runs row; both follow repository convention rather than the spec. Each
  material failure is either corrected in skill text, with the follow-up run
  attached, or recorded as a finding with a lifecycle state.
- **Prerequisites and order:** T1 through T4.
- **Relevant paths and patterns:** `evals/notebook/writeups/2026-09-19-reviewing-coding-standards.md`
  for structure; the `skill-evals` skill when present in the active inventory;
  the runner's own host flags. Hosts that are unavailable are named in the
  writeup, not simulated.
- **Completion check:** Every case in the six suites has a `result.json`
  under the output directory for every host in the matrix, the writeup
  exists, the BOOK row lists the scope, hosts, and S/MF/I counts, and the
  writeup's findings table has a state for every material failure.

### T6: Bump plugin versions

- **Spec references:** Versions.
- **Deliverable:** `version` is `0.2.0` in `plugins/library/.claude-plugin/plugin.json`
  and `plugins/library/.codex-plugin/plugin.json`, and `0.3.0` in the same
  two files for `plugins/planning` and `plugins/implementation`. The
  Antigravity `plugin.json` files are untouched by this task.
- **Prerequisites and order:** T1 through T5. Final task.
- **Relevant paths and patterns:** AGENTS.md, Plugin versions.
- **Completion check:**
  `python3 -c "import json;print([json.load(open(f'plugins/{p}/{m}/plugin.json'))['version'] for p in ('library','planning','implementation') for m in ('.claude-plugin','.codex-plugin')])"`
  prints `['0.2.0', '0.2.0', '0.3.0', '0.3.0', '0.3.0', '0.3.0']`, and
  `python3 -m unittest discover -s tests` passes.
