---
name: reviewing-coding-standards
description: Do not select for review of a change, diff, commit, or PR, including review against coding standards. Select only for a standards audit of repository state or an explicit path, component, rule, or topic scope, producing an evidence-backed report.
---

# Reviewing Coding Standards

First check applicability from the requested subject. Use this workflow only
for a standards audit of a repository or explicit path, component, rule, or
topic scope. A request to review a diff, PR, commit, or ordinary change remains
an ordinary change review even when it says "against our coding standards";
return to the normal change-review workflow and do not create this audit's
report. If the request is an applicable standards audit, continue below.

Audit documented standards across the requested scope and write one Markdown
report with confirmed errors, warnings, and unresolved assessments. Do not
recommend fixes, rank implementation work, modify code or standards, install
dependencies, or start another workflow. Only the report may be written; do not
commit, archive, push, or publish it.

## Establish authority and scope

Read repository instructions, then require `docs/standards/README.md` to define
obligation words and precedence. Check this before auditing code, requesting a
check, or creating a report. If the index is absent, unreadable, or lacks either
item, stop with a blocking failure that names the invalid prerequisite and
identifies `setting-up-coding-standards` as the required setup workflow. Write
nothing, do not use noncanonical guidance, and do not start setup automatically.
The companion setup skill's [output format](../setting-up-coding-standards/references/output-format.md)
explains the canonical layout and rule identity; it is not a rule source.

Read applicable topic documents and relevant tool configuration. Default to all
applicable production code, tests, supporting scripts, and repository
organization. Honor an explicitly narrower path, component, rule, or topic
scope while retaining shared guidance needed to interpret selected rules.
Guidance outside `docs/standards/` is not independently binding unless a
canonical rule explicitly adopts it or its tool configuration applies.

Apply documented scope, obligation words, exceptions, and effective timing.
Precedence is local rules, then existing mechanical tool configuration, then
explicitly adopted external baselines. Ordinary attribution does not adopt an
external guide. For an adoption, inspect the selected edition and sections in
scope and cite both the local adoption rule and upstream section, retrieving the
source with available host capabilities when needed. Unavailable evidence or an
unresolved authority conflict makes only the affected assessment unresolved;
no research provider or other plugin is required.

Do not infer policy from recurring code, personal preference, retired rules, or
rules not yet effective. A deferred rule's timing note controls even when its
tooling follow-up appears complete. For an apparently stale timing note, do
both: apply the documented current expectation, including any resulting error
or warning, and add a separate **Unresolved assessments** entry for the rule's
status and timing. Do not activate the deferred rule.

## Inspect statically

Inventory in-scope files and applicable rules, then inspect every in-scope area.
Use host file reading, search, and repository/history inspection. Search results
and existing diagnostics are candidates, not proof; verify current files,
surrounding code, callers, configuration, and governing rules. Report every
confirmed occurrence with no top-N limit. Group same-rule occurrences when
useful while retaining every location and materially different evidence, and
do not count one occurrence under the same rule twice. Sampling is partial
coverage; preserve completed work and list remaining paths and assessments.

Default to static inspection. A command may run only when it is a specific,
relevant check named by canonical standards or applicable tool configuration.
First inspect and show the user the exact command, script or hook, and scope.
Run it only with explicit approval naming those commands, whether already in the
request or obtained by asking once. With no answer, continue statically. Never
run tests, migrations, unrelated scripts, autofix or formatting-write modes, or
dependency installation. Disable caches or direct them outside the repository
when supported; otherwise record the constraint as a coverage gap.

Check output supplies candidates that still require verification. A missing
tool, unsafe command, or execution failure is a coverage gap, not a violation;
a nonzero exit alone is not a finding. List rules delegated to an unrun check as
not assessed without claiming equivalent static coverage. Do not reproduce or
emulate an unrun check's diagnostic logic to assert findings from its tokens,
algorithm, or expected output. Inspection needed to understand the command and
its safety does not authorize substitute diagnostics. Independently assessable
prose rules remain in scope when their evidence does not depend on reproducing
the delegated check. Capture repository state before the first approved check
runs, then compare it with repository state after the approved checks finish.
Record only commands, results, and state checks actually performed, or that no
check ran; never claim a pre/post comparison without both captures. Disclose
unexpected side effects and do not erase user changes, silently clean artifacts,
or claim report-only writes when anything else changed.

## Classify findings and exceptions

Use separate, unranked sections:

- **Errors (requirement violations):** confirmed departures from mandatory rules.
- **Warnings (recommendation departures):** confirmed departures from recommendations.

For a verified configured-check finding, first use the obligation word in the
topic rule naming the check. If absent, use effective configured severity:
`error` is an error and `warn` is a warning. A severity-free pass/fail check
produces errors. This fallback does not resolve contradictory or ambiguous prose.
Cite the topic rule or link naming the check, configuration path, and tool rule
code when available.

A mandatory-rule exception must be authorized by the standards; an unauthorized
site comment does not waive the requirement. A recommendation exception needs
a recorded reason through the standards' mechanism, or in the standards or at
the affected site when no mechanism is specified. If the record is unreadable,
or the reason's relevance is arguable, make the assessment unresolved. Honor a
reason that clearly addresses the rule without judging its quality or counting
a finding. List each honored exception under coverage with its location, rule,
and quoted reason, including records in another authorized location. An absent
reason is a warning; a plainly unrelated reason is a warning that quotes it.
Never invent a justification. An unclear exception, ambiguous obligation,
conflicting authority, unavailable evidence, or uncertain applicability is an
unresolved assessment. Continue independently assessable rules and exclude all
unresolved assessments from error and warning counts.

## Write the report

Use the user-specified destination, otherwise the repository's established
location, otherwise `docs/reviews/coding-standards-YYYY-MM-DD.md`. If the chosen
destination exists, leave it byte-for-byte unchanged: do not overwrite or append;
choose an unused numeric suffix. The necessary report directory may be created,
and only this audit's newly created report may be built incrementally to retain
work across interruptions. Create no repository scratch files, inventories, or
other artifacts. Outside-repository host scratch is allowed.

Include:

- Review date, repository revision or its unavailable limit, relevant
  working-copy changes, standards source paths, and that findings address the
  inspected working-copy state.
- Included and excluded paths, assessed rules, completeness or partial limits,
  honored recorded exceptions, executed commands and results, unassessed
  delegated rules, and any side effects.
- Separate **Errors**, **Warnings**, and **Unresolved assessments** sections.
  Each finding needs a report-local ID, governing rule ID and source
  link/anchor when available, exact file and line locations, observed evidence,
  and why it conflicts. Identify a directory or missing artifact for a
  structural finding rather than inventing a line. Each unresolved assessment
  names its scope and missing or ambiguous evidence, including relevant
  exception reasoning.
- Error and warning totals that distinguish grouped findings from occurrence
  counts. Zero means no confirmed findings within assessed scope, not universal
  compliance. Make relative links resolve from the report location.

Before finishing, recheck references, locations, counts, exception treatment,
and coverage claims against inspected evidence. Recheck findings affected by a
detectable repository change or record the coverage limitation. Exclude
replacements, patches, remediation, acceptance criteria, priorities, and fix
plans. Finish with the report path, counts, and material coverage limits; do not
start the later requirements workflow.
