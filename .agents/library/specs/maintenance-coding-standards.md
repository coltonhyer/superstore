---
title: Maintenance: coding-standards setup
status: approved
topics: [maintenance-plugin, coding-standards, agent-skills, specifications]
---

# Maintenance: coding-standards setup

## Summary

Add the `maintenance` plugin with one public skill,
`setting-up-coding-standards`. It inspects a repository, reports existing
standards and practices, researches appropriate guidance, and works with the
user to establish coding standards. After approval, it writes those standards
under `docs/standards/`, migrates existing guidance where necessary, and adds
references for people and coding agents.

The output is a short index and focused Markdown files with identifiable rules.
It supports implementation and future cleanup reports without a custom document
processor or a fixed list of rules for every repository.

## Context and motivation

Superstore currently provides Planning, Implementation, and Library. None owns
establishing repository coding standards. Library preserves documentation;
standards setup decides its content through repository evidence, research, and
user preferences. Maintenance is the home for this skill and later cleanup
review. This change delivers standards setup only.

The documentation format is a synthesis of established patterns, not a universal
standard. It draws on the
[Rust API Guidelines](https://rust-lang.github.io/api-guidelines/about.html): a
compact entry point, focused topic documents, and individually linkable rules.
[Airbnb](https://github.com/airbnb/javascript) demonstrates concise rules with
explanations and examples; [Google C++](https://google.github.io/styleguide/cppguide.html)
demonstrates explanations of consequential tradeoffs. The
[C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#ss-struct)
pair rule identifiers with descriptive titles, reasons, examples, and enforcement
guidance.
[PEP 8](https://peps.python.org/pep-0008/) and
[Django](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/)
show language guidance and a project baseline with local exceptions. Linter rule
documentation can help explain what existing tools actually check. These are
research starting points, not standards automatically imposed on every repository.

## Goals and non-goals

The skill establishes lean, coherent standards for production code, tests, and
supporting scripts, including their organization. Both people and agents must
be able to find applicable guidance, and a reviewer must be able to cite the
specific rule behind a finding.

It does not change code to comply, install or configure linters or formatters,
produce a cleanup audit, or implement the later cleanup-review skill. It does
not introduce a documentation website, required front matter, a rule registry,
or a new evaluation runner. It does not commit, archive, push, or publish the
target repository's generated standards as part of setup.

## Requirements and expected behavior

### Inspect and report before asking about the mode

Inspect repository guidance, manifests, configuration, layout, representative
code, tests, and scripts. Identify product type, languages and relevant versions,
frameworks, explicit coding standards, recurring practices inferred from code,
and existing linting/formatting configuration and commands. Existing context may
answer these questions; do not ask the user to repeat discoverable facts.

Inspection should cover the relevant areas without claiming every file was
reviewed. Always show a concise findings report before the mode discussion. It
includes the repository profile, the evidence inspected, any coverage limits,
and three distinct kinds of observations:

- Explicit standards, with their source paths and a summary of existing rules.
- Tool-enforced rules, supported by the actual configuration.
- Inferred conventions, with representative locations and uncertainty or
  inconsistencies clearly identified.

Report when an area or explicit standards are absent. Inference alone does not
establish a binding standard. Existing setup under `docs/standards/` is inspected
in the same way as guidance elsewhere.

When explicit standards exist, ask whether to **refine existing standards** or
**start fresh**. If the user already supplied that choice, acknowledge it after
the report instead of asking again. When no explicit standards are found, report
that finding and proceed with a fresh start without asking the mode question.
Refinement takes existing standards as the starting point and works through
changes. A fresh start uses observations as context but carries no existing
coding rule into the adopted standards without the user's agreement. Either
mode preserves unrelated repository instructions and content.

### Research and decide with the user

After the report and mode decision, propose a short list of relevant topics to
bound the research and discussion; let the user adjust it as work proceeds.

Use available research capabilities to inspect relevant primary sources:
established language guides, framework guidance, and respected open-source
projects with comparable product and runtime needs. Check applicability rather
than treating reputation as sufficient. Account for language versions, product
type, and current tooling. Determine which proposed rules existing linters can
check and which require judgment, without configuring those tools.

Reuse relevant verified source material; keep links to the sources actually
read. If research cannot be performed or evidence is insufficient, disclose the
gap and obtain the missing source or a user decision about the affected
recommendation. Do not invent source support or claim the research was completed.

For fresh starts, proceed one topic at a time: present concrete proposed
standards with concise reasoning, then ask a focused question so the user can
accept or adjust them. Use repository evidence and ecosystem guidance to form
recommendations, without treating inferred conventions as adopted standards.
For refinement, use the initial summary to focus on the areas the user wants to
change and propose improvements grounded in evidence. Avoid re-eliciting settled
preferences. In both modes, cover production code, tests, and scripts where
applicable, including their organization; record when a category is absent rather
than creating speculative rules or empty files.

The repository determines relevant topics. Organization, naming/readability,
interfaces, error handling, tests, scripts, documentation, and formatting are
considerations, not mandatory headings or a questionnaire to repeat unchanged.
Resolve contradictory proposed rules before final approval. Explain any chosen
standard that will require a later lint-configuration change; leave the actual
configuration unchanged. Research informs the user's choices, not the output
layout or an additional competing rulebook.

### Output location and document format

Use a single canonical standards directory at the repository root:

```text
docs/standards/
  README.md
  shared.md
  python.md
  tests.md
  scripts.md
```

Only `README.md` is required by name. The other filenames illustrate applicable
topics; choose short, descriptive, lowercase kebab-case names and create only
files needed by the agreed standards. Topic files sit directly in this directory.
An existing standards layout is migrated into this same flat structure in either
mode. Do not create a separate file for every rule.

The index contains a short statement of scope and a table of relative links,
brief descriptions, and concrete applicability, such as file paths, languages,
or kinds of work. It makes shared guidance explicit and helps readers select all
relevant documents: for example, shared, Python, API, and testing guidance can
all apply to one change. Applicability is navigation guidance, not a restriction
on inspecting other standards or repository files.
Do not duplicate the full rule set as a second checklist in the index.

Topic files have a descriptive title followed by short rules. Each rule has a
repository-unique identifier such as `SHARED-001`, `PY-001`, or `TEST-001`.
Use a level-two heading containing the ID and descriptive title, with an explicit
lowercase ID anchor so a title edit does not change the citation target:

````markdown
# Testing standards

<a id="test-001"></a>
## TEST-001: Test names describe behavior

Test names should describe the behavior and expected outcome they demonstrate.

This helps readers understand a failure without reading the entire test.

```python
# Bad: does not explain what the test demonstrates.
def test_login_2(): ...

# Good: identifies the input condition and expected outcome.
def test_login_rejects_expired_password(): ...
```
````

This is a format example, not a prescribed testing rule. The index links to
topic files; a report can cite `TEST-001` and link to `tests.md#test-001`. The ID
identifies the rule even if its file moves. Preserve existing valid IDs when
retaining the same rule, including when moving or reordering rules; do not
renumber to close gaps or reuse retired IDs. Retain a brief note of retired IDs
in the index when needed to prevent reuse. Assign distinct IDs to new rules.
No registry file or parser is needed.

Define the obligation vocabulary once in the index: "must" and "must not" are
requirements within the stated scope; "should" and "should not" are recommendations
that permit a reasoned exception. Use these words consistently in rule bodies.
A reviewer must distinguish a requirement violation from a recommendation and
consider the reason for any exception. Keep applicability qualifications beside
the rule. Include short rationale, optional bad/good examples, or source links
when they help interpretation.

Write agreed expectations in the topic files. An explicitly selected external
baseline is also allowed: identify the guide, its applicable scope and edition
or dated reference, and any local exceptions. Give the adoption rule a local ID;
a finding can cite that ID plus the relevant upstream section. Summarize what
adoption covers for approval instead of copying the guide. Ordinary source
citations explain provenance and do not import unselected rules. State precedence
once in the index and include it in the approval preview: agreed local rules
first, then existing tool configuration for mechanical matters, then the adopted
baseline. A mechanical difference between existing configuration and the baseline
is therefore a resolved exception, not a conflict requiring a separate question
or per-rule mismatch note.

For rules already enforced by tools, link the actual configuration and commands
from the applicable topic rather than transcribing mechanical settings into
individual prose rules. The configuration defines current mechanical checks;
written guidance covers judgment, relevant rationale, and agreed exceptions.
Do not claim tooling enforces judgment-based guidance. If a chosen change
conflicts with current configuration, keep a note beside the affected rule
describing the mismatch and required tooling follow-up. Agree and record whether
that rule applies now or after the tooling change; do not leave contradictory
instructions active or imply this skill changed the configuration.

Keep the files lean without a word or rule quota. No required front matter,
generated documentation, duplicate metadata, or mandatory unused sections.

### Approval, writing, and migration

Prepare the complete proposed content before requesting approval, but do not
create, modify, or remove target repository files yet. If a draft file is needed,
keep it outside that repository. Show a concise preview containing:

- Selected standards grouped by topic, including consequential decisions.
- Changes from existing rules, including any deliberately discarded rules.
- Files to create, update, relocate, or remove, and the treatment of old paths.
- Agent and human discovery-reference changes and any remaining tooling gaps.

Do not print all proposed files by default. Make exact full content available on
request. One explicit approval of this proposal authorizes the described writes
and migration. Corrections update the proposal; do not treat a materially
changed proposal as already approved.

After approval, write the standards, then update references and migrate the old
locations. For mixed-purpose files, replace only the superseded standards
sections with an appropriate reference, preserving unrelated text. For a
standards-only file, remove the superseded copy only after verifying the agreed
replacement; retain a short redirect when an old path must remain discoverable.
Account for incoming repository references to moved guidance. A fresh start is
not permission to discard unrelated content or delete files outside the approved
changes.

Recheck affected content before overwriting it. If it changed after the preview,
reconcile the change rather than overwrite another edit; return for approval if
the proposal must materially change. If a write or migration fails, preserve
recoverable content, report the exact partial result, and do not claim setup is
complete. Use ordinary file edits and verification, not a migration framework.

### Discovery and completion

Add or update one pointer to `docs/standards/README.md` in root `AGENTS.md`,
creating that file when absent. Instruct agents to read the index and applicable
standards before writing or reviewing code. Preserve other instructions.

Make the pointer reachable through host-specific instructions for the hosts in
use or explicitly targeted. Reuse existing imports or symlinks. For Claude Code,
use its existing `CLAUDE.md` entry point to import the shared `AGENTS.md`, resolving
the path relative to that file; create the entry point if Claude is targeted and
none exists. Check for overrides or existing host files that would bypass the
shared instructions. Do not populate configuration for unused hosts or alter
personal/global agent settings.

For humans, add one reference in the existing `CONTRIBUTING.md` guide, or root
`README.md` when no contributing guide exists. If neither exists, create a
minimal root README with the reference. Adjust relative paths for the containing
file. Do not copy the standards into these entry points.

Before reporting completion, read back the resulting files and check that the
agreed rules, IDs, index links, discovery references, and migration outcome are
correct, with unrelated content preserved. Report the canonical index path,
written/migrated files, and any unresolved issue concisely. Successful completion
requires the approved documentation and references to be in place; it does not
require existing code to satisfy the newly agreed standards.

## Technical design and constraints

Follow the existing self-contained plugin layout under `plugins/maintenance/`:
the three host manifests, a plugin README, and
`skills/setting-up-coding-standards/SKILL.md`. Use private references for the
output format and research guidance when needed to keep the public skill clear.
Register Maintenance in both marketplace indexes and the root README. Expose
only this one public skill in this change.

Use the existing host packaging and evaluation conventions. The skill requires
repository read/write and research capabilities supplied by the host; it adds no
runtime dependency and does not require Library, Planning, Firecrawl, or another
plugin to be installed. Do not hard-code a research provider, coding language,
linter, model, or catalog of rules. Do not create empty future skills.

## Verification

### Package and static structure

Extend the existing marketplace checks to cover Maintenance's registration,
matching manifests, README links, single public skill, and valid private
references. Confirm the skill and examples agree on the output path, layout,
rule-link format, and approval boundary. Run the repository's existing structural
test suite; no new test framework is required.

Check the skill's format example for a heading containing the rule ID and title,
a matching explicit anchor, and consistent obligation vocabulary.

### Setup workflow behavior

Use the existing skill-evaluation format and runner with fixtures covering:

- A fresh single-language repository with no explicit standards: inspection and
  report precede topic proposals; the redundant mode question is skipped;
  researched recommendations are relevant; preferences are gathered topic by
  topic; nothing in the target repository changes before final approval.
- Refinement with scattered and mixed-purpose standards: the summary distinguishes
  explicit, inferred, and tool-enforced rules; retained meanings and IDs survive;
  approval covers migration; unrelated documentation survives and old references
  resolve to the agreed standards. IDs survive title edits and moves, and retired
  IDs are not reused.
- A fresh start in a repository with existing standards: the report precedes the
  mode question, which is omitted if the user already supplied the choice. Prior
  rules are not silently inherited; deliberately superseded guidance is handled
  only within the approved file changes.
- A multilingual repository with tests and scripts: relevant topics are created,
  shared applicability is explicit, and absent categories do not produce empty
  files. Existing lint configuration informs recommendations but is not edited.
  Any intentional mismatch remains documented with its applicability and tooling
  follow-up, rather than disappearing after the approval preview.
- Explicit adoption of an external baseline: its scope and reference are clear,
  agreed local rules take precedence over existing tool configuration, which in
  turn takes precedence over the baseline for mechanical matters. A configured
  formatting choice differing from the baseline does not cause a redundant
  question or mismatch note. Review findings can cite the adoption rule and
  upstream section. A source cited only as research imports no rules.
- Approval correction or withheld approval: a concise preview is shown, full
  text is supplied on request, and writes wait for approval of the current
  proposal. Repeated setup does not duplicate pointers or renumber retained rules.
- A research gap or interrupted migration: missing evidence is disclosed and
  partial file operations are reported without fabricated research, silent data
  loss, or a false completion claim.

Keep research evidence inspectable in the evaluation trace, distinguishing
provided/cached source material from live retrieval. Use the existing live-eval
authorization and host-selection process; no live runs are authorized by this
spec alone. Validate discovery behavior on the supported hosts when executing
the approved verification work.

### Usefulness to implementers and reviewers

With representative generated standards, give an implementation agent a small
scoped task and a reviewer a fixture containing an identifiable standards issue.
Verify that each finds the index, reads the applicable shared/language/topic
guidance, and can inspect additional context when needed. The implementer should
apply the relevant agreed decisions; the reviewer should connect code evidence
to a valid rule ID and explain a focused improvement. These are evaluations of
the produced documentation, not implementation of the future cleanup skill.

Inspect the actual traces for missed applicable rules, unnecessary document
loading, and navigation overhead. Compare with the same agreed rules presented
in a single document in representative cases. Treat agent behavior as evidence
for usability, not a universal performance claim or a word-count benchmark.
