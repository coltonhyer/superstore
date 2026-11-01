---
title: OKF documents plan
status: approved
topics: [library, open-knowledge-format, agent-skills, planning-plugin, implementation-planning]
implements: specs/okf-documents.md
---

# OKF documents plan

## Approved specification

- **Locator:** `.agents/library/specs/okf-documents.md@xknlouww`

## Approach

Copy the OKF spec into the library skill first, so every later link to it
resolves and the checksum test guards it from the start. Rewrite the Library
plugin next, then move Planning and Implementation onto the new convention in
one recorded task each, with their eval suites changing in the same task as
the skill text they test. Implementation follows Planning, so T4 can check
its twin passages against T3's. Give the eval runner its commit identity, then update
`REVIEW.md`. Migrate this repository's own documents once all skill text is in
place, so the repository and the skills switch over together. Run the affected
eval suites, then bump versions last, as `AGENTS.md` requires. Keep
`python3 -m unittest discover -s tests` passing after every task.

This plan and its spec are read through their pinned locators for the whole
execution, so moving both files in T7 does not disturb it. The executing
primary follows the approved spec for its own whole-plan handoff: it writes
and records `docs/handoffs/<execution-id>.md` with `type: handoff`, even
though the installed Implementation skills predate that rule.

Every document this plan writes or migrates follows the spec's document
format: one field per line in the spec's order, `title` and `description` in
double quotes with `\` and `"` escaped, no other quoting, and repository paths
without a leading slash.

## Tasks

### T1: Copy the OKF spec and license into the library skill

- **Spec references:** Library skill (the two references); Verification,
  Repository unit tests.
- **Deliverable:** `plugins/library/skills/library/references/okf-spec.md` and
  `plugins/library/skills/library/references/okf-LICENSE.md` are byte-for-byte
  copies of `SPEC.md` and `LICENSE.md` from
  `GoogleCloudPlatform/open-knowledge-format` at commit
  `ad30107c31c06aec8a7d5636e0d1058118604e6f`. `tests/test_marketplace.py`
  gains a test asserting their SHA-256 values.
- **Prerequisites and order:** None. First task.
- **Relevant paths and patterns:** Fetch the files pinned to the commit, for
  example
  `https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/ad30107c31c06aec8a7d5636e0d1058118604e6f/SPEC.md`
  and the same path for `LICENSE.md`, into a scratch directory outside the
  repository, then copy them in without any change, not even a header or a
  newline normalization. Expected SHA-256:
  `26aa5da029278939f914e578107242d9607d4f2dc5fe153272b82f9ed1030101` for
  `SPEC.md` and
  `8c6db340475136df3c1201d458fa5755698eace76e510471ecc9d857d6083dac` for
  `LICENSE.md`. Use `hashlib` from the standard library in the test, beside
  `test_library_has_one_public_skill_and_valid_links`.
- **Completion check:** `sha256sum plugins/library/skills/library/references/okf-spec.md plugins/library/skills/library/references/okf-LICENSE.md`
  prints the two expected values, and `python3 -m unittest discover -s tests`
  passes, including the new test.

### T2: Rewrite the Library plugin as the OKF encoder

- **Spec references:** Document format; Locations; Status and currency;
  Library skill; READMEs, manifests, and REVIEW.md (the Library README,
  manifest, and marketplace bullets); Technical design and constraints;
  Quality requirements; Verification, Behavioral evals (`library`).
- **Deliverable:** `plugins/library/skills/library/SKILL.md` keeps `name:
  library`, has a description that triggers on finding, reading, writing,
  pinning, or comparing specs, plans, handoff notes, or other documents, and
  covers what the spec's Library skill section lists: OKF as the governing
  contract (version, source URL as plain text, commit, and license file);
  document types, locations, and file names; the frontmatter table; the status
  rules; document folders; Find, including the read restriction and the
  not-yet-migrated report; Pin and compare in both Jujutsu and Git forms,
  including history from before a move; Write, including leaving documents
  uncommitted and the folder check; and when to open the spec, by section
  number. `plugins/library/README.md` describes the OKF convention, the
  default location and how a repository names its own, the copied spec and
  its license, the three migration notes the spec lists, and the upgrade
  steps, and drops the argument for `.agents/` over `docs/`. The three Library
  manifests, the Library entry in `.claude-plugin/marketplace.json`, and the
  Library row in the root `README.md` describe OKF documents in `docs/`. The
  library eval suite moves cases 1 to 4 to `docs/` fixtures with OKF
  frontmatter: case 1's superseded spec carries `status: deprecated` and its
  draft `status: draft`; case 3's expectations describe the OKF fields and a
  `docs/<kind>/` folder; case 4's two ordinary notes are `type: note` in
  `docs/notes/`. It adds cases for: a spec folder named in a fixture
  `AGENTS.md`; writing a document of an unowned type with valid frontmatter
  and leaving it uncommitted; a case the rules do not cover that sends the
  agent to `references/okf-spec.md`; a frontmatter-less file in `docs/specs/`
  reported as not yet migrated; and a new type whose default folder already
  holds another tool's files without OKF frontmatter, where the agent asks
  where the documents should go.
- **Prerequisites and order:** T1.
- **Relevant paths and patterns:** The current `SKILL.md` for structure and
  for rules that keep a home: the read restriction, whole-slug tag matching,
  and pinned reads. Eval JSON shape
  `{"skill_name": ..., "evals": [{id, prompt, expected_output, skills?, files, replies?, expectations}]}`
  with fixture entries `{source, target, state}`; a fixture pair that must
  read as two versions differs in byte length. Codex manifest fields:
  `description`, `keywords`, `interface.shortDescription`,
  `interface.longDescription`, `interface.defaultPrompt` (at most three).
  Run every changed shell snippet in a scratch repository with
  `JJ_CONFIG=/dev/null JJ_EDITOR=false GIT_EDITOR=false` and stdin from
  `/dev/null`.
- **Completion check:** `python3 -m unittest discover -s tests` passes;
  `wc -l plugins/library/skills/library/SKILL.md` is under 500;
  `grep -n '\.agents/library' plugins/library -r` matches only the README's
  migration notes; the eval file loads as JSON; and a scratch-repository run
  of each shell snippet in `SKILL.md` returns what the skill says it returns.

### T3: Move Planning onto OKF documents

- **Spec references:** Document format; Locations; Status and currency;
  Planning: specs; Planning: requirements; READMEs, manifests, and REVIEW.md
  (Planning README); Verification, Behavioral evals (`specs`,
  `requirements`); Quality requirements.
- **Deliverable:** `plugins/planning/skills/specs/SKILL.md` writes drafts with
  the spec's frontmatter (`type: spec`, quoted `title` and `description`,
  `status: draft`, `tags`, and `supersedes` only when replacing a differently
  named spec) to the location the location order gives; on explicit approval
  sets `status: stable`, writes `verified` under the `user.name` rule, sets a
  superseded spec to `deprecated` unless it already is, commits exactly the
  files that step changed, runs the recording check on each committed path in
  both Jujutsu and Git forms, and on a refused or failed commit leaves those
  files in place and reports them uncommitted; on revision sets
  `status: draft` and removes `verified`; reports the resolved locator; and no
  longer has special cases for documents outside the library.
  `references/spec-review.md` forbids browsing the repository's documents
  beyond those supplied. `plugins/planning/skills/requirements/SKILL.md` reads
  history from the resolved locations with the new currency rule.
  `plugins/planning/README.md` describes the new paths and fields. The specs
  suite updates every case whose prompt, expectations, or fixtures name
  `.agents/library` or `status: approved`, moving fixtures to `docs/specs/`
  with OKF frontmatter, so approval expects `stable` and a `verified` line
  naming `human:Eval Reviewer`; it
  adds cases for a spec folder named in a fixture `AGENTS.md`, for approving
  a replacement that sets the replaced spec to `deprecated` in the same
  commit, and for re-approving a revised replacement whose target is already
  `deprecated`, which commits only the spec. The requirements suite moves
  case 4's fixtures to `docs/specs/` with a `stable` current spec, a
  `deprecated` replaced spec, and a `draft`, and case 5's prompt names no
  document folders under `docs/` in place of `.agents/library/`.
  `tests/test_eval_runner.py` asserts the specs case 7 fixture at
  `docs/specs/approved-spec.md`.
- **Prerequisites and order:** T2, so the `library` skill an eval declares has
  the new rules.
- **Relevant paths and patterns:** `planning_case("specs", 1)`,
  `planning_case("specs", 2)`, `planning_case("specs", 7)`, and
  `planning_case("requirements", 1)` are loaded by `tests/test_eval_runner.py`;
  keep those ids meaningful. The approval, commit, and revise sections are
  twins of `implementation/plans`; write them to agree word for word on every
  shared rule. Keep both SKILL.md files under 500 lines.
- **Completion check:** `python3 -m unittest discover -s tests` passes;
  `grep -rn '\.agents/library\|status: approved' plugins/planning` prints
  nothing; both `wc -l plugins/planning/skills/*/SKILL.md` counts are under
  500; both eval files load as JSON; each changed shell snippet, run in a
  scratch repository with `JJ_CONFIG=/dev/null JJ_EDITOR=false
  GIT_EDITOR=false` and stdin from `/dev/null`, prints what the skill says it
  prints; and no Markdown link in a changed SKILL.md or reference file
  resolves outside `plugins/planning/`.

### T4: Move Implementation onto OKF documents

- **Spec references:** Document format; Locations; Status and currency;
  Implementation: plans; Implementation: execution gate; Implementation:
  handoff notes; READMEs, manifests, and REVIEW.md (Implementation README);
  Verification, Behavioral evals (`plans`, `implementing-plans`,
  `subagent-execution`); Quality requirements.
- **Deliverable:** `plugins/implementation/skills/plans/SKILL.md` requires a
  `type: spec` document to carry a `status: stable` line and accepts any
  other spec form only on the user's explicit approval; writes drafts with
  `type: plan`, quoted `title` and `description`, `status: draft`, `tags`, and
  `implements` naming the spec's repository path when the spec is a
  repository file, adding `supersedes` only when replacing a differently named
  plan; and carries the same approval, commit, recording, failure, and
  revision rules as `planning/specs`. `references/plan-review.md` and
  `subagent-execution/references/implementer-brief.md` forbid browsing the
  repository's documents in place of "browse the library".
  `implementing-plans/SKILL.md` and `subagent-execution/SKILL.md` require the
  plan at its locator with a `status: stable` line and route `draft`,
  `deprecated`, or status-less plans back through `plans`, in matching words,
  and write the handoff note at `<handoffs folder>/<execution-id>.md`.
  `implementing-plans/references/execution-state.md` gives the note's
  frontmatter (`type: handoff`, quoted `title` and `description`, `tags`, and
  `implements` when the plan is a repository file), requires the execution id
  to satisfy the file-name rule, and keeps the body headings.
  `plugins/implementation/README.md` states the `stable` gate and the new
  paths. Evals: every case in the three suites whose prompt, expectations,
  or fixtures name `.agents/library` or `status: approved` is updated, with
  fixtures moved to `docs/` and given OKF frontmatter. In the plans suite,
  case 3 keeps its frontmatter-less spec at
  `docs/specs/release-publishing.md` with the user's explicit approval and
  now expects a plan at `docs/plans/release-publishing.md` whose `implements`
  names that path; cases 7 to 9 expect `stable` and `verified`; case 11 still
  refuses the `draft` spec; a new case approves a plan that replaces another
  and expects the replaced plan `deprecated` in the same commit. The
  implementing-plans and subagent-execution suites move fixtures to `docs/`
  with plans at `status: stable`, keep implementing-plans case 10's refusal of
  a `draft` plan, expect the handoff note at `docs/handoffs/<execution-id>.md`
  with `type: handoff` wherever a case reaches whole-plan handoff, and move
  subagent-execution case 9's note fixture to `docs/handoffs/finish-run.md`.
- **Prerequisites and order:** T3, so its twin passages can be checked
  against `planning/specs`.
- **Relevant paths and patterns:** `tests/test_marketplace.py` requires the
  five Implementation skill folders and README links to stay as they are.
  The plans approval, commit, and revise sections are twins of
  `planning/specs`, and the execution gate in `implementing-plans` and
  `subagent-execution` is a twin pair; write each pair to agree on every
  shared rule. Keep every SKILL.md under 500 lines and the existing links
  between Implementation skills unchanged.
- **Completion check:** `python3 -m unittest discover -s tests` passes;
  `grep -rn '\.agents/library\|status: approved\|browse the library' plugins/implementation`
  prints nothing; all five `wc -l plugins/implementation/skills/*/SKILL.md`
  counts are under 500; all eval files load as JSON; a side-by-side read of
  the approval, commit, and revise sections of `planning/specs` and
  `implementation/plans`, and of the execution gate in `implementing-plans`
  and `subagent-execution`, finds every shared rule worded the same, and the
  task report lists each shared rule with its line in both files; each
  changed shell snippet run as in T3 prints what the skill says it prints; and
  no Markdown link in a changed SKILL.md or reference file resolves outside
  `plugins/implementation/`.

### T5: Give the eval runner a commit identity

- **Spec references:** Eval runner; Verification, Repository unit tests.
- **Deliverable:** `prepare_workspace` in `scripts/skill_eval_core.py`
  configures `Eval Reviewer <eval-reviewer@example.invalid>` in each new
  workspace's Jujutsu repository config and Git config before the `eval
  fixture` commit. `tests/test_eval_runner.py` asserts that a prepared
  workspace reports `Eval Reviewer` from both `jj config get user.name` and
  `git config user.name`.
- **Prerequisites and order:** None. Must land before T8.
- **Relevant paths and patterns:** `prepare_workspace` runs
  `jj git init --colocate .` at `scripts/skill_eval_core.py:222`; set the
  identity with `jj config set --repo user.name ...` and `user.email`, and
  `git config user.name ...` and `user.email` in the workspace. Follow the
  existing `skipUnless(shutil.which("jj"))` pattern in
  `tests/test_eval_runner.py` for the new test.
- **Completion check:** `python3 -m unittest discover -s tests` passes,
  including the new identity test.

### T6: Update REVIEW.md

- **Spec references:** READMEs, manifests, and REVIEW.md (`REVIEW.md`
  bullet).
- **Deliverable:** `REVIEW.md` replaces its two `.agents/library/`
  references with the document locations under `docs/`, and its list of twin
  passages adds the execution gate in `implementing-plans` and
  `subagent-execution`. The task's commit message names the precedent: the
  first independent review of the approved spec found the gate unswitched, a
  review finding on this repository as `AGENTS.md` requires.
- **Prerequisites and order:** T4, so the twin pair exists.
- **Relevant paths and patterns:** `REVIEW.md` lines 54 and 118 hold the two
  references; the twin list is the third bullet under "Skill text".
- **Completion check:** `grep -n '\.agents/library' REVIEW.md` prints
  nothing, and the twin list names both `implementing-plans` and
  `subagent-execution` for the execution gate.

### T7: Migrate this repository's documents

- **Spec references:** Migration of this repository; Document format;
  Verification, Migration check.
- **Deliverable:** The fifteen documents under `.agents/library/` (seven
  specs, seven plans including this one, and one note) exist at
  `docs/specs/`, `docs/plans/`, and `docs/handoffs/` with unchanged slugs.
  Each has `type` from its old folder (`notes/` becomes `handoff`), its
  `title` unchanged in wording and double-quoted, a new one-sentence
  double-quoted `description`, `tags` equal to its former `topics` in order,
  and its link fields as repository paths under `docs/`. Specs and plans have
  `status: stable`, except `documentation-archive-plugin-design.md` and
  `library-retrofit.md` among the specs, which are `deprecated`. No document
  carries `verified`. Each body is byte-identical to the old file's body.
  `.agents/library/` is removed.
- **Prerequisites and order:** T1 through T6.
- **Relevant paths and patterns:** Read each old file's frontmatter and body
  with a script kept outside the repository and run with `python3 -I`; write
  frontmatter in the spec's field order and split the body after the
  frontmatter block and one blank line without normalizing newlines or
  trailing whitespace. Write each description from the document's own summary.
  Pinned locators inside bodies keep their old paths.
- **Completion check:** A comparison over all fifteen documents prints one
  `OK` line each, establishing that the SHA-256 of the bytes after the
  frontmatter block and one blank line equals that of the old file's body at
  T7's starting revision, whose change id is recorded before any edit
  (`jj file show -r <start> <old path>`), the title
  wording matches, `tags` equal the old `topics`, `type` matches the folder,
  the status is as specified, every link path exists, the `title` and
  `description` lines are double-quoted, and no `verified` line is present;
  that output is attached to the task report.
  `test ! -e .agents/library` succeeds, and
  `jj file show -r xooqszys .agents/library/plans/library-retrofit.md` still
  prints the plan.

### T8: Run the affected eval suites and record the writeup

- **Spec references:** Verification, Behavioral evals.
- **Deliverable:** The `library`, `specs`, `requirements`, `plans`,
  `implementing-plans`, and `subagent-execution` suites run through
  `scripts/run_skill_evals.py` with the matrix the user approves with this
  plan: hosts `claude`, `codex`, and `agy` at the defaults in
  `scripts/skill_eval_hosts.py`, one run per case, each plugin run with
  `--output .agents/eval-results/<date>-okf-documents/<plugin>`, in two
  stages. Stage 1 runs all six suites on `claude`; material failures are
  corrected in skill text and only the affected cases rerun on `claude` as
  follow-ups. Stage 2 runs all six suites on `codex` and `agy` and handles
  host-specific failures the same way. A host unavailable in the executing
  environment leaves this task incomplete for that host and is reported as a
  limitation; it does not narrow the matrix. The primary then stops before T9
  and asks the user whether to bump versions without that host's results.
  One writeup at
  `evals/notebook/writeups/<date>-okf-documents.md` covers both stages and
  follows the existing writeup structure, and `evals/notebook/BOOK.md` gains
  one Runs row. Each material failure is either corrected in skill text, with
  the follow-up run attached, or recorded as a finding with a lifecycle
  state.
- **Prerequisites and order:** T1 through T7.
- **Relevant paths and patterns:** `evals/notebook/writeups/2026-10-17-library-retrofit.md`
  for structure; the `skill-evals` skill; the runner's own host flags. Hosts
  that are unavailable are named in the writeup, not simulated. Before the
  first run, add `/.agents/eval-results/<date>-okf-documents/` to
  `.git/info/exclude`, as earlier runs did, so the run workspaces never enter
  the working-copy change. Follow-up reruns go to their own roots, such as
  `.agents/eval-results/<date>-okf-documents/followup<k>-<host>/<plugin>`,
  because the runner refuses an existing result directory. A correction to
  skill text from an earlier task belongs in that task's commit, not after
  the version bump.
- **Completion check:** Every case in the six suites has a `result.json` under
  the output directory for every host in the matrix, the writeup exists, the
  BOOK row lists the scope, hosts, and counts, the writeup's findings table
  has a state for every material failure, and `jj status` lists no path
  under `.agents/eval-results/`.

### T9: Bump plugin versions

- **Spec references:** Versions.
- **Deliverable:** `version` is `0.3.0` in
  `plugins/library/.claude-plugin/plugin.json` and
  `plugins/library/.codex-plugin/plugin.json`, and `0.4.0` in the same two
  files for `plugins/planning` and `plugins/implementation`. The Antigravity
  `plugin.json` files are untouched.
- **Prerequisites and order:** T1 through T8, or the user's decision in T8 to
  proceed without an unavailable host's results. Final task.
- **Relevant paths and patterns:** `AGENTS.md`, Plugin versions.
- **Completion check:**
  `python3 -c "import json;print([json.load(open(f'plugins/{p}/{m}/plugin.json'))['version'] for p in ('library','planning','implementation') for m in ('.claude-plugin','.codex-plugin')])"`
  prints `['0.3.0', '0.3.0', '0.4.0', '0.4.0', '0.4.0', '0.4.0']`, and
  `python3 -m unittest discover -s tests` passes.
