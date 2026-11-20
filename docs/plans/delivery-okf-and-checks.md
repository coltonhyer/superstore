---
type: plan
title: "Delivery OKF foundation and skill checks plan"
description: "Five tasks that wire plugin-level shared references into the eval runner and tests, add the shared OKF commit reference, generalize command-test scanning, update the library skill and blob-pinning commands with lockstep tests, and align REVIEW.md, Delivery README document rules, and library eval coverage."
status: stable
verified: { by: human:Colton Hyer, at: 2026-11-21T05:54:24Z }
tags: [delivery-plugin, library, open-knowledge-format, agent-skills, skill-evals, verification]
implements: [docs/specs/okf-documents.md, docs/specs/skill-checks.md]
references: [docs/specs/plan-execution.md, docs/specs/autonomous-execution.md]
---

# Delivery OKF foundation and skill checks plan

## Approved specifications

- `docs/specs/okf-documents.md`, blob `16d55212e3f9`
- `docs/specs/skill-checks.md`, blob `75d871c7fbe6`

## Approach

This plan is the first of three independently integrable plans delivering the consolidated `delivery` plugin changeset. It establishes the shared-reference infrastructure, OKF encoder and blob-citation mechanics, and test/review checks that Plans 2 and 3 build on:

- **This plan (`delivery-okf-and-checks`):** Eval-workspace copying and link validation for `plugins/<plugin>/references/`, manifest version-parity testing (and removing the tested parity clause from `REVIEW.md`), the shared `plugins/delivery/references/okf-commit.md` reference, generalized `tests/test_skill_commands.py` discovery across `plugins/*/references/*.md`, lockstep `library` skill + `pin-and-compare.md` + command-test updates (inline-list `implements`/`supersedes`, `process:delivery-autonomous`, `YYYY-MM-DD-` notes, 12-char committed Git blob computation/lookup in Git and colocated/non-colocated Jujutsu), scoped `REVIEW.md` updates for `plugins/*/references/*.md` and blob citations, `plugins/delivery/README.md` `Documents` and `pin-and-compare.md` summary alignment (keeping `## Validation` untouched since it is already current for `plugins/delivery`), and a new `library/11` eval case.
- **Plan 2 (separate plan — `specifications.md` + `review-loop.md`):** Shared `review-loop.md` and `dispositions.md` plugin references, `requirements` and `specs` skill updates (including linking `../../references/okf-commit.md`), two-reviewer `spec-review.md` split, `plan-review.md` loop alignment, reducing `REVIEW.md:82-90` twin-passage entries migrated by `specs`, and updated `specs`/`requirements` evals.
- **Plan 3 (separate plan — `plan-execution.md` + `autonomous-execution.md`):** Shared `autonomous-mode.md` plugin reference, `plans`, `implementing-plans`, `subagent-execution`, `reviewing-implementation`, and `verifying-changes` skill updates (including linking `../../references/okf-commit.md`), `<plan-slug>.md` handoffs (including any handoff-refresh wording on mechanical plan blob refresh), completing `REVIEW.md:82-90` twin-passage reduction, updating `REVIEW.md:118,129-131` and `plugins/delivery/README.md:118-119` (`<plan-slug>.md` handoffs and `Change` line) plus `plugins/delivery/README.md` `## Workflow`, updated evals, and the single changeset manifest version check/bump per `AGENTS.md`.

Every task in this plan leaves both repository checks passing (`python3 -m unittest discover -s tests` and `uvx rumdl@0.3.2 check --no-cache .`). No vendored file (`okf-spec.md`, `okf-LICENSE.md`) is edited, and `plugins/delivery/skills/library/SKILL.md` stays within the 240-line Codex single-read cap. Because `plugins/delivery` (`0.1.0`) is newly introduced in this unmerged changeset and Plans 2–3 continue modifying `plugins/delivery/`, no manifest version bump is made in this plan; Plan 3 owns the single changeset version check/bump.

## Tasks

### T1: Support plugin-level shared references in eval workspaces, tighten link checks, and test manifest version parity

- **Spec references:** `docs/specs/skill-checks.md` (`Parallel eval runs` -> `Plugin-level shared references`); `docs/specs/okf-documents.md` (`Goals and non-goals`, `Versions`, `Quality requirements`, `Alternatives` -> `Shared plugin-level references within delivery`, `Verification` -> `Repository unit tests`, `Static checks`).
- **Deliverable:** `prepare_workspace()` copies `plugins/<plugin>/references/` into `.eval/references/` without expanding the active skill inventory; eval-runner and marketplace link tests strip fenced code blocks, handle `#fragment` anchors, and enforce containment; `tests/test_marketplace.py` enforces equal `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` `version` values and `REVIEW.md:141-142` drops that now-tested clause per `AGENTS.md`.
- **Prerequisites and order:** None. Runs first so subsequent tasks adding `plugins/delivery/references/` files are immediately verified by workspace and link tests.
- **Relevant paths and patterns:**
  - `scripts/skill_eval_core.py`: in `prepare_workspace()` (around lines 241–252), if `(plugin_root / "references").is_dir()`, copy it with `shutil.copytree` to `destination / ".eval/references"`. Do not add entries to `case.skills` or `build_prompt()`. `file_manifest()` already ignores `.eval`.
  - `tests/test_eval_runner.py`: update `test_delivery_case_skill_links_resolve_in_copied_layout` (lines 295–309) to scan all Markdown files under `prepared.workspace / ".eval"` (covering `.eval/skills` and `.eval/references`, skipping `okf-spec.md` and `okf-LICENSE.md`), strip fenced code blocks first (supporting both backtick and `~~~` tilde fences with optional leading indentation, e.g. `r"(?ms)^[ \t]*(`{3,}|~{3,})[^\n]*\n.*?^[ \t]*\1[ \t]*$"`), match general Markdown links `\[[^\]]+\]\(([^)]+)\)`, ignore URLs (`://`) and same-file anchors (`#`), strip `#fragment` suffixes, verify `(markdown.parent / path_part).is_file()`, and assert `(markdown.parent / path_part).resolve().is_relative_to((prepared.workspace / ".eval").resolve())`. Add a test with a temporary plugin containing `references/shared.md` and a single-skill eval case linking `../../references/shared.md` from `SKILL.md`, asserting `.eval/references/shared.md` is copied, the relative link resolves inside `.eval`, `build_prompt()` lists no extra skills, and `collect_evidence()` omits `.eval/references/` from `status` and `files`.
  - `tests/test_marketplace.py`: update `test_delivery_has_eight_public_skills_and_valid_links` (lines 89–123) to strip fenced code blocks (both backtick and `~~~` tilde fences with optional leading indentation) before scanning links, cover `README.md`, every `SKILL.md`, every `skills/*/references/*.md` (excluding `okf-spec.md` and `okf-LICENSE.md`), and every `references/*.md` under `plugins/delivery/` when present, and assert that every resolved relative link from any skill or reference file stays inside `plugin_root.resolve()` (`README.md` may continue linking repo-root paths like `../../evals/Dockerfile` and `../../.agents/skills/skill-evals/SKILL.md`). Add a test asserting `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` `version` strings are equal for every listed plugin.
  - `REVIEW.md` (lines 141–142): remove *"including equal versions in both manifests"* now that `tests/test_marketplace.py` enforces it, keeping the whole-changeset bump rule intact (per `AGENTS.md`'s rule to remove a check once `tests/` enforces it).
- **Completion check:** `python3 -m unittest discover -s tests` and `uvx rumdl@0.3.2 check --no-cache .` both pass, including the new `.eval/references/` copy/containment tests and manifest version-parity test.

### T2: Add shared OKF approval, deprecation, and commit reference

- **Spec references:** `docs/specs/okf-documents.md` (`Document format`, `Status and currency`, `Delivery: specs`, `Delivery: plans`).
- **Deliverable:** A plugin-level shared reference `plugins/delivery/references/okf-commit.md` serving as the single source of truth for spec/plan approval promotion, scalar and inline-list `supersedes` deprecation, VCS commit and recording verification (Jujutsu and Git), commit-failure file preservation, committed 12-character Git blob computation, in-place revision, and mechanical blob-citation-only refresh on a `stable` plan.
- **Prerequisites and order:** Depends on T1 so marketplace and eval-workspace link checks immediately cover `plugins/delivery/references/okf-commit.md`.
- **Relevant paths and patterns:**
  - Create `plugins/delivery/references/okf-commit.md` (bundled at plugin root, linked by `specs` in Plan 2 and `plans` in Plan 3 as `../../references/okf-commit.md`).
  - **Single-skill eval isolation constraint:** Include NO Markdown link into `../skills/...` from `plugins/delivery/references/okf-commit.md`, because single-skill eval workspaces copy only the target skill plus `.eval/references/`. Mention `library`'s `pin-and-compare.md` only in plain backticks/prose, and include the two committed blob computation commands inline.
  - **Command formatting:** Use inline backticks for template commands with placeholders (`<message>`, `<path>`, `<paths>`), matching existing `specs/SKILL.md` and `plans/SKILL.md` commit prose and leaving concrete runnable fenced `sh` blob commands in `pin-and-compare.md` (tested in T4).
  - **Approval-guard boundary:** Approval-trigger definitions (including non-approval request words `preserve`, `save`, `record`, `commit`) remain in `specs/SKILL.md` and `plans/SKILL.md`; `okf-commit.md` defines the mechanics executed after explicit human approval or an authorized autonomous clean review.
  - Cover every required rule from `docs/specs/okf-documents.md`:
    1. Promotion to `status: stable` and `verified`: interactive explicit human approval writes `verified: { by: human:<approver>, at: <approval time> }` from `jj config get user.name` / `git config user.name` and `date -u +%Y-%m-%dT%H:%M:%SZ` (omitting `verified` with a note in the report when the name is empty or contains any of `,` `[` `]` `{` `}` `#` `:`); explicitly authorized autonomous clean review writes `verified: { by: process:delivery-autonomous, at: <approval time> }` (OKF `machine-confirmed`, never `human:`).
    2. `supersedes` target iteration across both scalar (`supersedes: <path>`) and inline-list (`supersedes: [path-a, path-b]`) forms: inspect each target; leave unmigrated targets (no `type` line) unchanged and report them; set migrated targets to `status: deprecated` unless already `deprecated` (replacing `status` or adding after `description`); ignore missing targets; for a spec split, deprecate the split spec only once the replacement set is complete and approved.
    3. Scoped commit of strictly the files steps 1 and 2 actually modified (explicitly excluding already-`deprecated` targets, unmigrated targets, and unrelated working-copy changes) and recording verification in both Jujutsu (`jj commit -m '<message>' <paths>`, verifying `jj diff -r @ <path>` prints nothing and `jj log -r @- <path>` shows a newer revision for every committed path) and Git (`git add <paths> && git commit -m '<message>' <paths>`, verifying `git status --porcelain <path>` prints nothing and `git log -1 -- <path>` shows the new commit for every committed path).
    4. Commit/recording failure path: when no supported VCS exists or the commit is refused or fails, leave every file the step changed in place with its new status, report them uncommitted and not downstream-ready, and do not claim completion.
    5. Post-approval committed 12-char Git blob citation (`<path>`, blob `<12-char hash>`), computed only from the committed revision (never a dirty working copy) via `git --git-dir="$(jj git root)" rev-parse --short=12 "$(jj log -r @- --no-graph -T commit_id):<path>"` (Jujutsu, colocated and non-colocated) or `git rev-parse --short=12 HEAD:<path>` (Git).
    6. In-place revision (`status: draft`, remove `verified`, review, re-approve, re-commit) vs. mechanical blob-citation-only refresh on a `stable` plan whose tasks and content are unchanged (commits the refreshed plan without flipping to `draft` or re-requesting approval; handoff-refresh semantics stay scoped to Plan 3).
  - Must pass `rumdl` (`plugins/**/*.md` is linted by `.rumdl.toml`).
- **Completion check:** `plugins/delivery/references/okf-commit.md` exists with zero links outside `plugins/delivery/references/` and zero fenced shell blocks; all inline Jujutsu and Git commit/verify/identity/blob snippets in `okf-commit.md` succeed in a scratch repository with `JJ_CONFIG=/dev/null JJ_EDITOR=false GIT_EDITOR=false` and stdin from `/dev/null` (using repo-local test identity for the commit steps); and both `python3 -m unittest discover -s tests` and `uvx rumdl@0.3.2 check --no-cache .` pass.

### T3: Generalize command-test block discovery to include plugin-level shared references

- **Spec references:** `docs/specs/skill-checks.md` (`Command tests` -> `Coverage`).
- **Deliverable:** `tests/test_skill_commands.py` scans `plugins/*/references/*.md` alongside `plugins/*/skills/*/SKILL.md` and `plugins/*/skills/*/references/*.md`, drops the brittle hardcoded `BLOCK_COUNT` constant in favor of exact bidirectional set coverage, and includes a unit test verifying discovery of fenced shell blocks under `plugins/*/references/*.md`.
- **Prerequisites and order:** Depends on T2 only so `plugins/delivery/references/okf-commit.md` already exists when scanning `plugins/*/references/*.md`; runs before T4 so T4 can add new fenced `sh` blocks to `pin-and-compare.md` without fighting a hardcoded `BLOCK_COUNT`.
- **Relevant paths and patterns:**
  - `tests/test_skill_commands.py`:
    - Update `shell_blocks(root=ROOT)` (lines 54–82) to accept an optional `root: Path = ROOT` parameter and collect `plugins/*/skills/*/SKILL.md`, `plugins/*/skills/*/references/*.md`, and `plugins/*/references/*.md`.
    - Remove `BLOCK_COUNT = 10` (line 15) and its assertion on line 354 while keeping `self.assertTrue(keys)`, `keys - set(COVERED) == []`, `set(COVERED) - keys == []`, and `len(COVERED) == len(set(COVERED))`.
    - Add a unit test constructing a temporary root with `plugins/demo/references/shared.md` containing a fenced `sh` block and asserting `shell_blocks(root=temp_root)` discovers `("plugins/demo/references/shared.md", <first line>)`.
- **Completion check:** `python3 -m unittest discover -s tests` and `uvx rumdl@0.3.2 check --no-cache .` both pass cleanly.

### T4: Update library skill, pin-and-compare reference, and lockstep command tests

- **Spec references:** `docs/specs/okf-documents.md` (`Document format`, `Status and currency`, `Library skill` -> `Find`, `Pin and compare`, `Technical design and constraints`, `Quality requirements`); `docs/specs/skill-checks.md` (`Command tests` -> `Coverage`, `Fixtures`, `Pin and compare`).
- **Deliverable:** Lockstep update to `plugins/delivery/skills/library/SKILL.md` (strictly `<= 240` lines), `plugins/delivery/skills/library/references/pin-and-compare.md`, and `tests/test_skill_commands.py` adding inline-list `implements`/`supersedes`, `process:delivery-autonomous` in `verified`, optional `YYYY-MM-DD-` standalone note filenames, delimiter-safe whole-path `supersedes` grep with scalar/list/near-match fixtures across all available `awk` implementations, and 12-character committed Git blob computation/lookup commands tested in both colocated and non-colocated (`jj git init --no-colocate`) Jujutsu repositories.
- **Prerequisites and order:** Depends on T2 (wording alignment with `okf-commit.md`) and T3 (`shell_blocks()` generalization and `BLOCK_COUNT` removal).
- **Relevant paths and patterns:**
  - `plugins/delivery/skills/library/SKILL.md` (currently **239/240 lines** — tighten existing phrasing cleanly so every rule fits within `<= 240` lines without dropping any rule checked by `REVIEW.md` or `library` evals 1–10):
    - **Types, locations, file names:** Note that point-in-time standalone notes in `docs/notes/` may prefix filenames with `YYYY-MM-DD-` (which fits the slug rule), while living specs keep undated domain slugs.
    - **Frontmatter table and rules:** Update `verified` to cover explicit human approval (`human:<approver>`) and autonomous clean review (`process:delivery-autonomous`, OKF `machine-confirmed`); update `implements` to accept one repository path or an inline list (`[path-a, path-b]`) for multi-spec plans; update `supersedes` to accept one repository path or an inline list (`[path-a, path-b]`) for merges and splits.
    - **Status:** Note that `supersedes` approval iterates over every listed target (deprecating a split spec only once its replacement set is complete and approved), and that a mechanical blob-citation-only refresh on a `stable` plan commits without flipping to `draft` or re-requesting approval.
    - **Find (step 2):** Replace `grep ': supersedes: docs/specs/auth-sessions.md'` with `grep -E ': supersedes: (.*[, [])?docs/specs/auth-sessions\.md([],]|$)'` matching both scalar and inline-list forms without prefix or suffix false matches. Keep `TAGS_PATTERN`, `TITLE_PATTERN`, and all `awk` extractors verbatim.
    - **Find (step 7) and Pin and compare:** Document `<path>`, blob `<12-char hash>` for committed plan/handoff citations alongside `path@revision` for ad-hoc pinned reads, and direct readers to `references/pin-and-compare.md` before computing or reading a 12-character committed Git blob hash, resolving a revision, reading/comparing revisions, or listing history.
  - `plugins/delivery/skills/library/references/pin-and-compare.md`:
    - Update lines 3–4 summary to include computing and reading 12-character committed Git blob hashes alongside revision reads, diffs, and history.
    - Add two fenced `sh` blocks explaining that blob hashes are computed only from committed revisions (never dirty working copies) and that `jj git root` works in both colocated and non-colocated Git-backed Jujutsu repositories:
      1. Compute 12-character committed Git blob hash:
         - `git --git-dir="$(jj git root)" rev-parse --short=12 "$(jj log -r <rev> --no-graph -T commit_id):docs/specs/auth-sessions.md"`
         - `git rev-parse --short=12 <rev>:docs/specs/auth-sessions.md`
      2. Read a document by committed Git blob hash:
         - `git --git-dir="$(jj git root)" cat-file -p <blob>`
         - `git cat-file -p <blob>`
  - `tests/test_skill_commands.py`:
    - Update `SUPERSEDES_PATTERN` (line 41) to `"grep -E ': supersedes: (.*[, [])?docs/specs/auth-sessions\\.md([],]|$)'"`, asserting verbatim presence in `library/SKILL.md`.
    - Expand `SPECS` and `PLANS` fixtures (lines 179–292) with scalar `supersedes`, single-item inline list `supersedes: [docs/specs/auth-sessions.md]`, multi-item inline lists (first and last positions), and negative near-matches (`docs/specs/auth-sessions-v2.md`, `old/docs/specs/auth-sessions.md`, `[docs/specs/auth-sessions.md.bak]`); update expected output constants (`SUPERSEDING`, `STABLE_SPECS`, `STABLE_PLAN`, `TITLES`, `STATUS_AND_TAGS`) accordingly so every `awk` subtest passes with exact stdout.
    - In `PinAndCompareTests` (lines 485–607): compute `cls.blob1` (12-char Git blob hash of `V1` at `cls.first`), add `<blob>` replacement in `run_lines()`, and add `@covers(PIN, ...)` tests for both new blob blocks asserting exact 12-char hash output and `V1.decode()` content for both Jujutsu and Git.
    - Add a dedicated test in `PinAndCompareTests` creating a **non-colocated** Jujutsu scratch repo (`jj git init --no-colocate .`, asserting `not (noncoloc / ".git").exists()`) and running the Jujutsu lines of both blob blocks against it, asserting exact 12-char blob hash and exact file content via `jj git root`.
  - Never modify `plugins/delivery/skills/library/references/okf-spec.md` or `okf-LICENSE.md`.
- **Completion check:** `wc -l plugins/delivery/skills/library/SKILL.md` reports `<= 240`, `python3 -m unittest discover -s tests` passes across all available `awk` implementations and colocated/non-colocated Jujutsu + Git repos (including OKF SHA-256 checksums), and `uvx rumdl@0.3.2 check --no-cache .` passes.

### T5: Align REVIEW.md, Delivery README document rules, and library eval coverage

- **Spec references:** `docs/specs/okf-documents.md` (`READMEs, manifests, and REVIEW.md`, `Verification` -> `Behavioral evals`); `docs/specs/skill-checks.md` (`Command tests` -> `REVIEW.md`).
- **Deliverable:** `REVIEW.md` updated for `plugins/*/references/*.md` command-test scope and committed blob-citation verification (leaving active twin-passage and handoff-format checks intact until Plans 2–3); `plugins/delivery/README.md` `## Documents` and `pin-and-compare.md` summary aligned with `library/SKILL.md` (leaving `docs/handoffs/<execution-id>.md` and `## Workflow` for Plan 3); and a new behavioral eval case (`library/11`) exercising inline-list `supersedes` discovery and committed-blob-vs-working-copy lookup.
- **Prerequisites and order:** Depends on T1–T4 so all referenced files, commands, and test behaviors exist and pass before documenting and evaluating them.
- **Relevant paths and patterns:**
  - `REVIEW.md`:
    - Update `### Skill text` (lines 66 and 98–100) to include `plugins/*/references/*.md` alongside `plugins/*/skills/*/SKILL.md` and `references/`.
    - Update `### Documents and records` (lines 126–128) to add verification of committed blob citations (`git cat-file -p <blob>` or `git --git-dir="$(jj git root)" cat-file -p <blob>`) alongside existing `path@revision` verification.
    - Leave `REVIEW.md:82-90` (twin passages) and `REVIEW.md:118,129-131` (handoff `Result` range) unchanged in Plan 1 (Plans 2–3 update them as live skills migrate). These edits only adapt existing `Always check` rules for Plan 1's new paths and citation mechanics (no new ungrounded review rules are added under `AGENTS.md`).
  - `plugins/delivery/README.md`:
    - Update `## Documents` (lines 123–160) so filename rules (optional `YYYY-MM-DD-` prefix on standalone notes), frontmatter (`verified` with `human:` and `process:delivery-autonomous`, scalar or inline-list `implements` and `supersedes`), multi-target `supersedes` deprecation (including spec-split timing), the mechanical blob-citation-only refresh exception on a `stable` plan, and committed 12-char blob citations alongside `path@revision` match `library/SKILL.md`. Leave line 118–119 (`docs/handoffs/<execution-id>.md`) and `## Workflow` untouched until Plan 3.
    - Update lines 180–181 (`## The copied spec`) so the one-line summary of `pin-and-compare.md` mentions committed Git blob hashes alongside pinned reads, diffs, and history.
  - `plugins/delivery/skills/library/evals/evals.json` and `plugins/delivery/skills/library/evals/files/`:
    - Add case `11` with baseline fixtures including a spec carrying an inline list `supersedes: [docs/specs/session-policy.md, docs/specs/token-policy.md]` and a distractor spec with a neutral filename whose `supersedes` holds a near-match path (`docs/specs/token-policy-v2.md`, so attached filenames do not telegraph exclusion per `REVIEW.md:108-111`), plus a `baseline` + different-byte-length `working` fixture pair for `docs/specs/token-policy.md` (per `REVIEW.md:115-116`, e.g., baseline `15-minute` limit vs. working-copy `120-minute` limit so file sizes differ).
    - Prompt asks which current spec supersedes `docs/specs/token-policy.md` and asks for the committed 12-character Git blob hash and content of `docs/specs/token-policy.md` at the committed revision described `eval fixture` (matching `library/2`, without modifying any file), so expectations verify whole-path inline-list `supersedes` discovery and committed-blob computation/reading distinct from the dirty working copy.
- **Completion check:** `python3 -m unittest discover -s tests` (including `test_delivery_case_skill_links_resolve_in_copied_layout` preparing `library/11`) and `uvx rumdl@0.3.2 check --no-cache .` both pass cleanly.
