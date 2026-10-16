---
title: Repository coding standards review implementation plan
status: approved
topics: [coding-standards, maintenance-plugin, implementation-planning, verification]
implements: specs/reviewing-coding-standards.md
---

# Implement repository coding standards review

## Approved specification

- **Locator:** [docs/specs/reviewing-coding-standards.md](../specs/reviewing-coding-standards.md)
- **Approved version:** commit `32cddcfc`, approved in conversation and preserved
  as Markdown. The specification, including its approval and classification
  policies, is authoritative over preliminary implementation `plprpupk`.

## Approach

Reconcile the existing audit skill with the approved specification, add a small
shared-fixture evaluation suite, and validate on Codex and Claude Code. Reuse
the existing runner and file evidence; do not build an analyzer, a new harness,
or a language matrix. This is one Maintenance change with three ordered tasks.
The setup skill and its output format remain unchanged.

This plan defines work for later execution. Approval and preservation of the
plan are required before execution; drafting it runs no live evaluations.

## Tasks

### CSR-1: Reconcile the skill and public documentation

- **Spec references:** `Goals and non-goals`; all subsections of `Requirements
  and expected behavior`; `Technical design and constraints`.
- **Deliverable:** revised `reviewing-coding-standards` instructions and accurate
  Maintenance documentation implementing the full approved contract.
- **Prerequisites and order:** first; start from the existing draft, not a new
  plugin. Read the approved spec and setup output format before editing.
- **Relevant paths and patterns:**
  `plugins/maintenance/skills/reviewing-coding-standards/SKILL.md`,
  `plugins/maintenance/README.md`, the three Maintenance manifests,
  root `README.md`, and `.claude-plugin/marketplace.json`. Existing metadata
  already exposes two skills; change it only where the revised behavior requires
  clarification. Retain the relative link to setup's `references/output-format.md`.
- **Constraints:** keep instructions concise and self-contained within Maintenance.
  Explicitly exclude diff/PR/change review in frontmatter. Replace legacy-layout
  support with the canonical-index prerequisite and report-free blocking failure.
  Preserve static inspection by default; only exact relevant configured commands
  receive explicit execution approval, never tests or migrations. Implement
  obligation/configured-severity/pass-fail classification, evidence verification,
  scoped exceptions and their recorded reasons, deferred-note authority, and
  unresolved assessments outside finding counts. Preserve every occurrence,
  narrower scope, revision evidence, report-only writes, collision suffixes,
  incremental reporting, and no remediation or automatic next workflow. Include
  command results, unassessed delegated rules, and unexpected side-effect handling.
- **Completion check:** compare the instructions directly against each referenced
  spec subsection; every observable obligation has an instruction and no old
  draft policy contradicts it. Run the available skill-creator frontmatter
  validator on this skill and `python3 -m unittest discover -s tests`.
  Structural success is not behavioral validation.

### CSR-2: Add compact fixtures and offline validation

- **Spec references:** `Verification / Structural checks`;
  `Verification / Small fixture evaluations on both hosts`; report and
  classification contracts supplying the expected results.
- **Deliverable:** `plugins/maintenance/skills/reviewing-coding-standards/evals/`
  containing `evals.json` and small reusable fixtures, plus focused updates to
  existing structural/preparation tests. Keep expected findings in evaluator
  guidance, not subject-visible files.
- **Prerequisites and order:** after CSR-1; cases exercise the reconciled skill.
- **Relevant paths and patterns:** reuse `files`, `state: baseline/working`,
  `replies`, and `expectations` from setup's `evals/evals.json` and the existing
  `scripts/skill_eval_core.py` schema. Modify `tests/test_eval_runner.py` to
  assert setup's IDs 1–16 separately from the new audit cases, then prepare and
  inspect both suites. Extend `tests/test_marketplace.py` only for discovery,
  manifests, and links not already covered. Each audit case lists
  `setting-up-coding-standards` in `skills` so the sibling output-format link
  resolves in `.eval/skills`; loading that reference must not start setup.
- **Fixture design and case IDs:** reuse a tiny Python repository with production,
  test, and script files, canonical rules, a configuration file, and supplied
  external-source excerpts. Use these ten short cases rather than duplicating
  a language matrix:

  | ID | Behavior and observable outcome |
  | --- | --- |
  | 1 | Full static audit: repeated errors/warnings across production/tests/scripts; all locations retained without duplicates; relevant, unrelated, arguable, missing, and unauthorized exception reasons; standards-defined record location and unreadable record; unresolved excluded from counts; source citations, report-local IDs, working changes, honored-exception coverage, and existing-report collision preservation |
  | 2 | Narrow path and topic audit: only selected scope produces findings; shared guidance still applies; local/config/baseline precedence, adopted versus citation-only guide, deferred note despite apparently completed tooling, retired rule, ambiguous rule, and missing individual source |
  | 3 | Canonical index absent but legacy guidance present: explicit failure, setup prerequisite named, no code audit, check request, file writes, or automatic setup |
  | 4 | Index lacks obligation words or precedence: same blocking outcome; preserve the malformed index |
  | 5 | Index cannot be read as a file: same blocking outcome; use a directory at the index path populated by a harmless fixture marker, avoiding permission tests dependent on container UID |
  | 6 | Compliant small repository: zero confirmed findings with scoped coverage, no invented rules or universal compliance claim |
  | 7 | Relevant configured check proposed, scripted reply declines: no execution; report identifies delegated rules as unassessed |
  | 8 | Relevant configured check proposed, scripted reply approves the literal command: only that command executes; verified hits use explicit obligation over severity, error/warn defaults, then severity-free error; citations include topic/config/rule code; no tests, migrations, autofix, or installs |
  | 9 | Same configured check, no reply/non-interactive: no execution and static report with unassessed delegated rules rather than stopping indefinitely at the question |
  | 10 | Literal relevant commands authorized in initial request: no repeated approval request; missing executable and a configured check that fails operationally are coverage gaps, not findings; inspect commands first and record actual results |

- **Constraints:** configure one small standard-library Python check with real
  source-dependent diagnostics and severity settings; the eval image already
  includes Python. Include configured tests/migration scripts as out-of-scope
  alternatives, never as approved commands. Keep any fixture-script validation
  runnable by the implementer outside subject sessions. No new linter dependency.
  Make rule IDs, locations, expected classifications, and occurrence counts
  explicit in evaluator expectations. Do not require exact report prose.
  Inspect commands and tool traces as well as file manifests; unchanged final
  files alone cannot prove that no forbidden execution occurred. Unexpected
  side-effect disclosure is reviewed if observed; compliant check fixtures must
  not intentionally violate report-only writes. Revision-unavailable and
  concurrent-edit fallback behavior stay document-review checks per the spec.
- **Completion check:** run `python3 -m unittest discover -s tests` and
  `python3 scripts/run_skill_evals.py --plugin plugins/maintenance --skill reviewing-coding-standards --list`.
  All ten cases load and prepare with byte-correct fixtures, working-state
  evidence, complete prompts, and resolvable private references; setup's original
  16 cases remain intact. Confirm each spec verification-table behavior maps to
  the cases above or an explicitly identified manual/document-review surface.

### CSR-3: Validate both hosts and record evidence

- **Spec references:** all of `Verification`, especially native discovery and
  the final completion gate.
- **Deliverable:** retained live artifacts and a concise evaluation writeup under
  `evals/notebook/writeups/`, indexed in `evals/notebook/BOOK.md`, with exact case,
  host, model/effort, command, and evidence locators. Update Maintenance's validation
  documentation to distinguish the setup suite, audit suite, and native checks.
- **Prerequisites and order:** after CSR-1 and CSR-2 pass. Use the repository's
  `skill-evals` instructions when running/reviewing evaluations. Execute all ten
  audit cases on Codex and Claude Code, using the runner's existing host model
  and effort defaults and recording their actual values. This is 20 guided runs
  plus six native discovery runs; do not run setup's full live suite or Agy.
  Confirm this concrete matrix before live execution unless already authorized
  by the user's execution request.
- **Relevant paths and patterns:** `scripts/run_skill_evals.py`,
  `scripts/skill_eval_hosts.py`, `evals/Dockerfile`,
  `.agents/skills/skill-evals/SKILL.md`, and the existing Maintenance evaluation
  writeup's disposable container/capture pattern. Store raw evidence outside
  the repository in a unique retained output directory. The guided invocation is
  `python3 scripts/run_skill_evals.py --plugin plugins/maintenance --skill reviewing-coding-standards --host codex --host claude --output <retained-output-directory>`.
- **Native setup and check:** in disposable host state, install the local
  Maintenance plugin through each host's supported plugin-loading mechanism.
  Inspect installed CLI help and capture exact commands/configuration; do not
  reuse flags that disable native plugin or instruction discovery. The current
  guided prompt forces skill reads, so it cannot establish this surface. Reuse
  its isolated authentication, event capture, and before/after evidence where
  practical through a task-local wrapper outside the repository; no permanent
  runner extension is needed. Confirm plugin availability from host loading
  evidence before each independent session. Keep personal configurations unchanged.
- **Native prompts:** reuse a small canonical fixture and run each prompt on both
  hosts without forced skill reads: ordinary change review; “review this change
  against our coding standards”; explicit repository standards audit. The first
  two must execute ordinary change review and write no audit report; the third
  must execute the audit workflow and produce a valid static report. Read-only
  inspection of the audit skill while deciding applicability is allowed and is
  not itself audit-workflow execution; acceptance does not require the skill to
  remain unread. Judge the boundary from the subsequent workflow actions and
  report behavior, retaining plugin-loading and tool evidence rather than only
  the final response. Classify a run as inconclusive only when those retained
  actions and report artifacts cannot establish which workflow executed.
- **Completion check:** read each run's actual skill, prompts, responses, tool
  events, report, and file evidence before evaluator guidance. Demonstrate every
  seeded finding and approval boundary against its evidence. Record failures,
  operational errors, and inconclusive capture separately; no pass from runner
  completion alone. Fix supported implementation defects within the spec and
  rerun only affected cases/hosts, preserving original evidence and the disposition
  of each finding. If a repair changes discovery wording, rerun the three native
  prompts on both hosts. Completion requires affirmative results for both hosts,
  successful structural checks after edits, and a final implementation review
  against the approved spec. Do not mark missing native evidence complete or
  silently broaden the run matrix to obtain a passing sample.
