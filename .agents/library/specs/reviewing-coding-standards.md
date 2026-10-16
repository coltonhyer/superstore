---
title: Repository coding standards review specification
status: approved
topics: [coding-standards, maintenance-plugin, specifications, verification]
---

# Repository coding standards review

## Summary

Add `reviewing-coding-standards` to Maintenance alongside standards setup. The
skill inspects a repository against its documented standards and writes a
Markdown report with errors, warnings, and unresolved assessments. Findings are
actionable through evidence and rule traceability; they contain no remediation
advice. A maintainer can use the report in a separate requirements workflow.

## Context and motivation

Standards setup establishes scoped rules with obligation words, precedence,
stable IDs, and effective timing. Maintainers need a corresponding audit that
applies those decisions consistently without inventing rules or proposing fixes.

Local change `plprpupk` contains a preliminary implementation made before
requirements approval. This specification derives from the approved requirements,
not that draft. Implementation must reconcile the draft against this contract,
particularly its execution permission, exception handling, classifications,
trigger boundary, and missing behavioral evaluations.

## Goals and non-goals

Review all applicable production code, tests, supporting scripts, and repository
organization by default. Honor an explicitly narrower path, component, rule,
or topic scope, retaining shared guidance needed to interpret selected rules.
Assume standards setup has established the canonical `docs/standards/` layout.

This skill does not handle diff, PR, or ordinary change reviews. Those requests
may consult the same standards through other workflows but must not execute this
audit workflow. A host may read the skill instructions solely to determine
applicability; that read-only inspection is not workflow activation when the
request then proceeds as an ordinary change review without an audit report. A
request for a standards audit of a named directory remains in scope.

Default to static inspection. Only specific, relevant configured checks may run
with explicit user approval as described below. Running tests, database migrations,
or unrelated scripts is outside this audit. Do not install dependencies, modify code or standards,
recommend fixes, rank implementation work, or start another workflow. Only the
report is written; do not commit, archive, push, or publish it.

## Requirements and expected behavior

### Establish authority and scope

Read repository instructions and require `docs/standards/README.md` with
obligation words and precedence, then read applicable topic documents. Judge the
precondition by those artifacts, not by proof that the setup skill ran. Guidance
outside the canonical layout is not an independent rule source; references
explicitly adopted by canonical rules and their tool configuration still apply.
Read relevant tool configuration as evidence.

Apply the documented scope, obligation words, precedence, exceptions, and
effective timing. Canonical precedence is local rules, then existing mechanical
tool configuration, then explicitly adopted external baselines. If a
conflict cannot be resolved from the documented authority, record it as unresolved.

Only explicit adoption makes an external guide binding. Read the adopted edition
and sections within their declared scope; cite the adoption rule and upstream
section. Ordinary attribution to Google C++, Airbnb JavaScript, Rust API
Guidelines, PEP 8, or another source does not adopt its rules. Use available
source evidence or retrieve the selected reference with host capabilities;
unavailable evidence leaves the affected assessment unresolved. No research
provider or other plugin is required.

Do not enforce retired or not-yet-effective rules. For a deferred rule, apply
the documented current expectation. The effective-timing note governs; apparent
completion of tooling follow-up does not override a note that still defers the
rule. Record an apparently stale note as unresolved without activating the rule.
Do not infer policy from recurring code patterns or personal preferences.
Check the canonical precondition before auditing code, requesting check execution,
or creating a report. If the index is absent, unreadable, or lacks obligation
words or precedence, stop with an explicit blocking failure that names the
missing or invalid prerequisite and identifies `setting-up-coding-standards`
as the required setup workflow. Write no report or other file, do not fall back
to noncanonical guidance, and do not start setup automatically. This is a
failed prerequisite, not a clean audit or an unresolved finding in a report.
Once the index meets the precondition, unavailable individual rule sources and
ambiguous rules remain scoped unresolved assessments as described below.

### Static inspection and completeness

Use host file-reading, searching, and repository-state capabilities. Read-only
utilities for inspecting files and history are allowed. Execution of configured
checks is optional and subject to the following approval boundary.

### Explicitly approved checks

Only check commands named by the canonical standards or tool configuration and
relevant to the current audit qualify. Inspect the exact commands, scripts, and
relevant hooks first, and show the commands to the user. Approval covers only
those specific commands and their disclosed scope, not arbitrary repository
execution. Existing explicit approval in the request suffices when it identifies
those commands; otherwise ask once. With no answer, including a non-interactive
run, continue statically without executing them. Do not run tests, migrations,
or unrelated scripts under this permission.

Use check-only modes: no autofix, formatting writes, or dependency installation.
Disable caches or direct them outside the repository when supported. A missing
tool or a command that cannot satisfy these constraints is a coverage gap.
Tool output supplies candidates to verify against current files and governing
rules, not automatic findings. List rules delegated to an unrun check as not
assessed; do not imply static reading provided equivalent mechanical coverage.

Record every executed command and result, or state that none ran. Compare the
working copy before and after execution; verify that the audit changed only the
report and disclose any unexpected side effects. Do not erase user changes or
silently clean up unexpected artifacts, or claim report-only writes when other
changes occurred.

### Inspection coverage

Inventory in-scope files and applicable rules, then inspect every in-scope area.
Read surrounding code, callers, and configuration where needed to establish a
finding. Search matches are candidates rather than proof. Existing diagnostics
may inform inspection only when their provenance and relevance can be assessed;
they do not replace verification against the current files and governing rules.

Report every confirmed occurrence, without a top-N limit. Group occurrences of
the same rule violation when helpful, retaining every location and materially
different evidence. Do not count the same occurrence under the same rule twice.
Sampling cannot establish completed coverage. If inspection is incomplete,
write a partial report identifying the remaining paths and rule assessments.

### Classification and exceptions

Use these separate report sections, with no ranking within either section:

- **Errors (requirement violations):** confirmed departures from mandatory rules.
- **Warnings (recommendation departures):** confirmed departures from recommendations.

For verified findings from configured checks, use the obligation word in the
applicable topic rule that names the check. If none is specified, use the tool's
effective configured severity: error maps to error, and warn maps to warning.
A check without severities yields errors for verified violations because it
defines a pass/fail obligation. This fallback resolves absent obligation words
for configured checks; it does not resolve contradictory standards or ambiguous
prose rules. Cite the topic rule or link naming the check, the configuration
path, and the tool's rule code where available. Execution failures remain
coverage gaps, not violations; a nonzero exit alone is not a finding.

A mandatory-rule exception must be authorized by the standards; a site comment
alone cannot waive a requirement. A recommendation exception requires a reason
documented through the standards' specified exception mechanism, or in the
standards or at the affected site when no mechanism is specified. If a required
record cannot be read, mark the assessment unresolved. For a recommendation,
check that the recorded reason exists and addresses the rule; do not judge
whether it is good enough. A reason that plainly does not address the rule is
a warning that quotes it. An arguable reason is unresolved. An applicable reason
that clearly addresses the rule is honored, not counted as a finding. List
honored site-recorded exceptions under coverage with location, rule, and quoted
reason; do the same for records in another standards-authorized location.
An undocumented recommendation departure is a warning. An unclear exception
belongs in unresolved assessments, not in confirmed findings. Never
invent an unstated justification. Clearly unauthorized mandatory-rule departures
remain errors even when a comment claims an exception.

Ambiguous obligation strength, conflicting authority, unavailable evidence, and
uncertain applicability also belong in unresolved assessments. Continue reviewing
independently assessable rules. Unresolved assessments are excluded from error
and warning counts.

### Report contract

Write to the user-specified destination, otherwise the repository's established
report location, otherwise `docs/reviews/coding-standards-YYYY-MM-DD.md`. Choose
an unused numeric suffix if the destination already exists; never overwrite an
existing file. The necessary report directory may be created. The current audit
may build its new report incrementally to retain coverage and findings across
interruptions. Do not create scratch files, auxiliary inventories, or other
artifacts inside the repository. Host scratch space outside it is permitted.

The report includes:

- Review date, repository revision, relevant working-copy changes, and standards
  source paths. Findings refer to the inspected working-copy state, not just its
  parent revision. If revision identification is unavailable, disclose that limit.
- Included and excluded paths, assessed rules, coverage limits, and whether the
  audit is complete or partial, including honored recorded exceptions. List
  executed commands and results, unassessed delegated rules, and any side effects.
- Separate error and warning sections. Each finding has a report-local ID,
  governing rule ID and source link/anchor where available, exact file and line
  locations, observed evidence, and why it conflicts with the rule. Structural
  findings identify the directory or missing artifact instead of inventing a line.
- Separate unresolved assessments with the affected scope and missing or
  ambiguous evidence. Relevant exception reasoning accompanies the assessment.
- Error and warning totals; distinguish grouped findings from occurrence counts.
  Zero findings means none confirmed within assessed scope, not proof of universal
  compliance. Relative links resolve from the report location.

Before finishing, verify references, locations, counts, exception treatment, and
coverage claims against inspected evidence. Detectable changes during the audit
require rechecking affected findings or recording a coverage limitation.

Exclude suggested replacements, patches, remediation steps, acceptance criteria,
implementation priorities, and fix plans. Finish with the report path, counts,
and material coverage limits. Do not initiate the later requirements workflow.

## Technical design and constraints

Keep the skill as concise instructions under
`plugins/maintenance/skills/reviewing-coding-standards/SKILL.md`, reusing the
setup output-format reference where helpful. No custom analyzer, rule registry,
report generator, or runtime dependency is needed. State the exclusion of diff,
PR, and ordinary change reviews in the skill's frontmatter description so it is
visible during skill selection. Keep Maintenance documentation
and host metadata consistent with its two public skills. The setup workflow and
its output format remain unchanged.

## Verification

### Structural checks

Extend `tests/test_marketplace.py` as needed to verify public skill discovery,
manifest consistency, README links, and private reference resolution. Validate
skill frontmatter and prepare the new cases through the existing evaluation
harness. These checks do not establish behavioral correctness.

### Small fixture evaluations on both hosts

Define a compact suite in
`plugins/maintenance/skills/reviewing-coding-standards/evals/evals.json` using
small fixtures and the existing runner. Reuse fixtures across focused cases;
avoid a language matrix or a large evaluation library. The intended surfaces are:

| Fixture surface | Behaviors verified |
| --- | --- |
| Canonical standards with production, test, and script violations | Errors versus warnings; rule citations; every occurrence; grouping without duplicates; recorded and unauthorized exceptions; relevant reasons honored and listed, plainly unrelated reasons quoted in warnings, arguable reasons unresolved; standards-defined exception locations and unavailable records; counts exclude unresolved items; report IDs, revision, locations, and coverage |
| Authority and scope variants | Local/configuration/baseline precedence; adopted versus attribution-only guides; deferred rules with apparently completed tooling follow-up; narrower path and topic scope; missing sources or conflicting rules remain unresolved |
| Missing canonical standards and compliant input | Explicit blocking failure for an absent, unreadable, or incomplete index, including when noncanonical guidance exists; names setup prerequisite, writes no report, runs no checks, and does not start setup; distinguish this from a completed audit with no confirmed findings; no invented rules or unqualified compliance claim |
| Configured check with scripted approval replies | Declining or absent approval prevents execution and exposes unassessed delegated rules; approval runs only the displayed relevant command; tests and migrations remain unrun; command results and side effects are recorded; verified output becomes cited findings using explicit obligation before configured severity, then error for severity-free checks; execution failures remain coverage gaps |

Across these cases, inspect the actual report and tool traces for no remediation
advice, unapproved or out-of-scope execution, or writes other than the report. Retain
before/after file evidence and confirm an existing report is preserved. External
reference excerpts can be supplied as fixture evidence; no live web dependency
is needed. Use a small standard-library Python script for the configured check,
with Python available in the eval environment; do not install a linter. The
harness may arrange fixtures; the subject may run only explicitly approved checks.

Run the same compact cases live on Codex and Claude Code. Retain prompts,
responses, tool events, final reports, and repository evidence. Evaluate known
rule/location/classification outcomes, not exact prose. Missing traces or
operational failures are inconclusive rather than passing behavior.

Unavailable revision identification and concurrent edits during an audit remain
document-review checks, not claims of live fixture coverage. Do not add concurrency
machinery solely to exercise these fallback instructions.

### Native discovery checks on both hosts

Install the local Maintenance plugin into isolated host configurations, without
altering personal installations or explicitly invoking or preloading the audit
skill. Budget this small setup separately from the existing guided runner; prior
standards-discovery sessions do not prove plugin selection. Check three prompts:
an ordinary change review and "review this change against our coding standards"
must remain ordinary change-review workflows and must not produce an audit
report; an explicit repository standards-audit request must execute the audit
workflow and produce its report. Read-only inspection of the audit skill to
decide applicability is allowed and does not by itself fail the first two
checks; there is no requirement that the skill remain unread. Evaluate the
selected workflow from the subsequent actions and report behavior. Retain
plugin-loading, discovery, and action evidence.
Guided fixture runs alone do not demonstrate native trigger behavior; use a small
manual native session per prompt and host rather than expanding the shared runner
solely for these checks.

Completion requires successful structural checks and affirmative behavioral and
discovery evidence on both hosts. Report actual coverage and any failed or
inconclusive cases; do not claim completion from case preparation alone.
