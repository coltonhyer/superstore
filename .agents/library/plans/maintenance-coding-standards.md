---
title: Maintenance coding-standards setup implementation plan
status: approved
topics: [maintenance-plugin, coding-standards, implementation-planning, agent-skills, verification]
implements: specs/maintenance-coding-standards.md
---

# Maintenance coding-standards setup implementation plan

## Approved specification

- **Locator:** `.agents/ledger.db`, document
  `de76e319-28cf-48f8-828e-e54f93d99575`.
- **Title and original path:** Maintenance: coding-standards setup;
  `docs/specs/maintenance-coding-standards.md`.
- **Approved version:** approved in this conversation on 2026-09-18, archived
  in run `56444519-c839-4cad-8981-35735addbe8e`; exact-content SHA-256
  `13d4287049f4703c685fa5a3f8140c0d1c3554157d741115a663b1f98072e0d8`.

Section names below refer to that exact archived specification. The managing
agent loads it through `library:read-archive` and supplies the verified content
to any isolated implementer or reviewer; workers need not browse the archive.

## Approach

Deliver one self-contained `maintenance` plugin exposing only
`setting-up-coding-standards`. Implement the workflow as skill instructions with
two private references: the output format and focused research guidance. Reuse
the three existing host manifests, marketplace structure, unittest suite, and
behavioral eval runner. No runtime code, new dependencies, migration engine,
document parser, or future public skills are needed.

The skill establishes standards for another repository; implementing it does
not set up standards in Superstore itself. Keep cleanup review, lint setup,
and target-repository code changes outside this delivery. The existing
uncommitted spec archive in `.agents/ledger.db` is input, not implementation work
to modify or include incidentally in a commit.

Complete MCS-1 first. MCS-2 and MCS-3 can then proceed independently against its
public skill and references. MCS-4 consumes both and supplies the release
evidence. This plan authorizes no execution or live model spending by itself.
When execution is authorized, follow the existing `skill-evals` run-matrix
approval process before live checks.

## Tasks

### MCS-1: Write the standards-setup skill and private references

- **Spec references:** “Goals and non-goals”; all five subsections under
  “Requirements and expected behavior”; “Technical design and constraints.”
- **Deliverable:**
  `plugins/maintenance/skills/setting-up-coding-standards/SKILL.md`,
  `references/output-format.md`, and `references/research.md` beneath that skill.
  Keep the public skill responsible for workflow and approval boundaries; link
  the references at the points where their details are needed.
- **Prerequisites and order:** none; use the exact approved specification above.
- **Relevant paths and patterns:** follow the concise front matter, imperative
  workflow, and relative private-reference links in
  `plugins/planning/skills/requirements/SKILL.md` and
  `plugins/planning/skills/specs/SKILL.md`. Consult the available skill-authoring
  instructions during execution. These are authoring precedents, not runtime
  dependencies on Planning or any other plugin.
- **Constraints and required behavior:**
  - Inspect product, languages, relevant code, tests, scripts, explicit guidance,
    and tooling. Always summarize evidence as explicit, inferred, or enforced;
    report coverage limits and missing categories. Ask refine/fresh only when
    explicit standards exist and the user has not already chosen.
  - Propose relevant topics before researching. Fresh starts present concrete
    proposals one topic at a time; refinement focuses on requested changes.
    Inferences support proposals without becoming binding by default. Research
    guidance uses applicable primary sources, distinguishes available cached
    evidence from live research, and handles missing evidence honestly. Use the
    spec's cited guides as starting points, not a fixed rule catalog or required
    provider. Include product/language fit and actual lint capabilities.
  - The format reference defines `docs/standards/README.md`, flat relevant topic
    files, concrete applicability, ID-and-title headings, explicit ID anchors,
    must/should meanings, optional rationale and bad/good examples, stable IDs,
    and retired-ID notes. Include a small index example and the spec's rule
    example; do not prescribe their sample topics or rules universally.
  - Record approved baseline scope/reference and local exceptions without copying
    an entire external guide. State agreed local rules, then existing mechanical
    tool configuration, then baseline precedence. Link tools and commands rather
    than duplicating settings. Persist notes for deliberate local changes that
    conflict with tools, including whether they apply now or after follow-up.
  - Prepare complete drafts outside the target repository. One summarized final
    approval covers rules, precedence, migrations, file changes, and discovery
    references; supply full content on request. Recheck before overwrites, retain
    unrelated content, and report partial failures accurately.
  - Write standards before migrating old locations and incoming references.
    Add the shared AGENTS pointer, compatible entry points only for targeted
    hosts, and a human pointer in CONTRIBUTING or README. Reuse imports/symlinks,
    account for overriding instructions, and read back the result. Do not change
    code, tool configuration, global settings, or target-repository history.
- **Completion check:** read the three files against the cited spec sections;
  follow each private link and walk through fresh, refinement, and interrupted
  migration flows. Every step must have a defined next action and preserve the
  single final approval boundary. Confirm the examples agree with the workflow
  and introduce no additional mandatory fields, topics, or services.

### MCS-2: Package and register Maintenance with structural checks

- **Spec references:** “Summary”; “Technical design and constraints”;
  “Verification / Package and static structure.”
- **Deliverable:** the plugin's three manifests and README, both marketplace
  entries, root README entry, and focused additions to `tests/test_marketplace.py`.
- **Prerequisites and order:** MCS-1 supplies the public skill name, relative
  reference paths, and documented behavior.
- **Relevant paths and patterns:** create
  `plugins/maintenance/.codex-plugin/plugin.json`,
  `plugins/maintenance/.claude-plugin/plugin.json`,
  `plugins/maintenance/plugin.json`, and `plugins/maintenance/README.md` using
  `plugins/planning/` as the packaging precedent. Update
  `.agents/plugins/marketplace.json`, `.claude-plugin/marketplace.json`, and
  `README.md`. Reuse existing manifest fields, version conventions, installation
  instructions, and plugin-local skill discovery; no marketplace schema changes.
- **Constraints:** describe the delivered setup skill accurately and expose only
  that skill. Document the generated layout, refine/fresh workflow, research
  requirement, approval boundary, and evaluation commands without duplicating
  the skill's full instructions. Do not copy pinned host/model versions into a
  second maintenance-specific configuration.
- **Completion check:** extend the existing tests to require Maintenance in both
  indexes, matching manifest names, exactly one public skill, valid README and
  private-reference paths, and the output-format example's heading, anchor, and
  obligation vocabulary. Check observable structure, not exact prose. Run
  `python3 -m unittest discover -s tests`; inspect README installation and skill
  links. Generated-document behavior belongs to MCS-3/MCS-4, not static tests.

### MCS-3: Add setup and standards-use behavioral cases

- **Spec references:** “Verification / Setup workflow behavior”;
  “Verification / Usefulness to implementers and reviewers”; the corresponding
  behavior in “Requirements and expected behavior.”
- **Deliverable:**
  `plugins/maintenance/skills/setting-up-coding-standards/evals/evals.json`,
  small reusable fixtures under its `evals/files/`, and case-selection/evidence
  instructions in the Maintenance README's validation section.
- **Prerequisites and order:** MCS-1 supplies the actual subject instructions and
  format. MCS-2 is not a prerequisite; keep its README edits coordinated.
- **Relevant paths and patterns:** use the `prompt`, `expected_output`,
  `expectations`, `files`, and fixed `replies` format demonstrated in
  `plugins/planning/skills/requirements/evals/evals.json` and
  `plugins/implementation/skills/plans/evals/evals.json`. The existing
  `scripts/skill_eval_core.py` supports baseline/working file fixtures and native
  multi-turn replies; it does not provide arbitrary between-turn mutation hooks.
- **Case coverage:**
  - Fresh single-language setup without explicit standards: report first, no
    redundant mode question, relevant research, concrete topic proposals, no
    repository writes before final approval.
  - Refinement of scattered and mixed-purpose guidance: evidence categories,
    preservation of unrelated content, moved references, meanings, and IDs.
  - Fresh start despite existing guidance: informed mode choice, no silently
    inherited rules, and only approved removals.
  - Multiple languages with production code, tests, and scripts: applicable
    shared/topic guidance, no empty topics, unchanged tool configuration, and
    persistent notes for explicitly selected tooling changes.
  - Explicit baseline adoption: local/config/baseline precedence, citation-only
    sources importing no rules, and no redundant mismatch question for mechanical
    settings already resolved by that precedence.
  - Correction and withheld approval branches: concise preview, full draft on
    request, no writes on withheld approval, and approval of the latest proposal.
  - Repeated setup and revised rules: retain IDs through title edits and moves,
    do not reuse retired IDs, and do not duplicate pointers.
  - Unavailable research and interrupted migration: disclose gaps and partial
    results, preserve recoverable content, and do not invent success. Seed a
    resumed partial state with explicit prior-operation facts for recovery
    coverage; do not claim this simulates a real filesystem failure.
  - Changed content since a preview: supply a prior approved proposal and current
    differing files as a continuation fixture; preserve the new content and seek
    revised approval when reconciliation materially changes the proposal.
- **Constraints:** split materially different branches into cases with stable
  numeric IDs; reuse fixture files rather than manufacturing unrelated projects.
  Include short attributed source excerpts or summaries with original URLs and
  retrieval context. Clearly label them as supplied evidence; never require a
  live research provider or infer research completion from a citation alone.
  Fixed replies must express real user choices and approval, not coach the
  subject through the workflow. Use bounded relevant topics to keep reply
  sequences meaningful. Judge defensible variations rather than exact wording.
- **Standards-use cases:** include small implementation and review tasks against
  representative output of MCS-1's format, each in split-document and equivalent
  single-document variants. Keep agreed rules and code tasks identical across
  variants. Ask for ordinary implementation/review, without invoking setup;
  verify applicable shared/language/topic rules, allowance for further context,
  and evidence tied to valid rule IDs. MCS-4 also checks actual generated output,
  so hand-authored fixtures alone cannot establish the output's usefulness.
- **Completion check:** run
  `python3 scripts/run_skill_evals.py --plugin plugins/maintenance --list`.
  Prepare each case with the existing `prepare_workspace` helper in temporary
  directories without invoking a host; verify fixture sources/targets and the
  resulting prompts. Read fixed conversations and expectations against the skill.
  Keep expected answers outside subject-visible files. Record which observations
  require runtime traces rather than pretending fixture validation proves them.

### MCS-4: Verify setup behavior and generated standards in use

- **Spec references:** all three “Verification” subsections;
  “Discovery and completion.”
- **Deliverable:** retained run artifacts and a dated evidence report at
  `evals/notebook/writeups/<run-date>-maintenance-coding-standards.md`, indexed in
  `evals/notebook/BOOK.md`, identifying the tested revision, exact cases/hosts,
  artifact locations, findings, and unresolved limitations. Follow the existing
  notebook convention; do not put mutable progress into this plan or the skill.
- **Prerequisites and order:** MCS-2 and MCS-3 complete; execution and the live
  matrix authorized. Use `.agents/skills/skill-evals/SKILL.md` for run selection,
  observation, evidence review, and permitted reruns.
- **Relevant paths and patterns:** reuse `scripts/run_skill_evals.py` and its host
  defaults. Propose all Maintenance cases on Codex and the split-document
  implementation/review cases on Claude Code and Antigravity, with explicit
  retained output directories. Confirm exact case IDs, hosts, models, effort, and
  artifact paths before spending quota. This is a proposed matrix, not approval.
- **Execution and evidence:**
  - Run the existing structural suite and case listing. Run the authorized live
    cases using `--plugin plugins/maintenance`, appropriate `--skill`/`--case`
    filters, explicit `--host` flags, and `--output` paths.
  - Read complete captured conversations and file evidence before author review
    guidance. Verify sequencing, research provenance, approval boundaries,
    generated content, ID stability, migrations, pointer reuse, and truthful
    completion. Separate operational errors, invalid fixtures, judgment concerns,
    and observed contract failures; correct and rerun only affected cases.
  - Select a completed setup run's actual standards and repository as the usage
    sample. In disposable copies, run fresh implementation and review sessions
    with ordinary task prompts through each supported host. Retain the generated
    instruction files; do not name the index in prompts or preload the standards.
    Capture prompts, responses, provider traces where available, and resulting
    diffs. This is a bounded manual check using the existing hosts, not a new
    evaluation runner. Include these sessions in the authorized matrix.
  - The automated runner enumerates fixture paths and preloads the available
    skill. Its usage cases therefore establish guided usability, not unprompted
    host discovery. Use the fresh sessions to observe native entry-point
    discovery. Where traces cannot establish reads, report that limitation
    instead of inferring discovery from the final answer alone.
  - Compare the same generated rules and tasks in split and single-document
    forms on one authorized host. Check missed applicable rules, unnecessary
    loading, navigation effort, correct implementation, and focused review
    findings with valid IDs. Preserve both forms in artifacts and avoid universal
    performance claims. Do not change agreed rules to improve a comparison.
- **Completion check:** the report maps every required verification behavior to
  concrete artifact evidence and a disposition. Required observations must be
  supported; do not report completion from static tests alone, skipped live runs,
  unavailable hosts, or inconclusive traces. Record remaining verification work
  explicitly if authorization or tooling prevents completion. Review the final
  implementation against the approved spec after any evidence-driven fixes.
