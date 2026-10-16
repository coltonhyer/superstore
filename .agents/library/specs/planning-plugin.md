---
title: Planning Plugin Design
status: approved
topics: [agent-skills, marketplace, planning-plugin, requirements, specifications]
---

# Planning Plugin Design

## Summary

Add a `planning` marketplace plugin with two public skills:

- `requirements` gathers and confirms the complete requirements for a change.
- `specs` turns approved requirements into a reviewed specification under
  `docs/specs` and then preserves it according to the user's choice.

The plugin remains useful on its own. When Library is installed, it can consult
relevant archived context and offer to archive an approved spec, but Library is
never a required dependency.

## Goals

- Start from requirements the user has already supplied instead of making them
  repeat information.
- Investigate relevant repository context before asking the user for facts.
- Continue requirements gathering until scope, behavior, constraints, and the
  definition of done are clear enough for explicit approval.
- Produce concise, implementation-ready specs without fixed lengths or empty
  boilerplate sections.
- Independently review each draft for material problems before user approval.
- Preserve approved specs without coupling Planning to Library.
- Work across supported agent hosts without hard-coded model names, agent roles,
  or host-specific effort controls.

## Non-goals

- Implementation plans, code implementation, or handoff-plan workflows.
- A separately invocable spec-review skill. It can be split out later if direct
  independent review proves useful.
- Persistent requirements files. The approved requirements summary remains in
  the conversation and is incorporated into the spec.
- A custom model-evaluation framework.
- Replacing repository-specific templates or version-control instructions.

## Plugin layout

```text
plugins/planning/
  README.md
  .codex-plugin/plugin.json
  .claude-plugin/plugin.json
  plugin.json
  skills/
    requirements/
      SKILL.md
      evals/
        evals.json
    specs/
      SKILL.md
      references/
        spec-template.md
        spec-review.md
      evals/
        evals.json
```

No scripts, commands, persistent state, or dedicated agent definitions are
needed. `spec-template.md` and `spec-review.md` are private references owned by
`specs`, not additional public workflows.

The normal flow is:

```text
supplied context
  -> requirements questions
  -> approved requirements summary
  -> spec draft
  -> independent review and dispositions
  -> user approval
  -> archive with Library or commit the Markdown
```

## `requirements` skill

### Inputs and context

The workflow accepts a rough request, detailed requirements, issue text, or an
existing document. It first extracts what is already known, then inspects the
relevant code, documentation, configuration, and repository history. It must
not ask the user for facts that the repository can answer.

When `read-archive` is available and historical specs or decisions are
plausibly relevant, archived documentation is part of the surrounding context.
The agent searches compact metadata first and loads only selected documents.
It does not search the archive for every task, and a missing Library skill or
ledger is not an error. Explicit references to an earlier design or a change to
established behavior strongly favor an archive lookup.

### Question loop

The agent asks one focused question at a time about genuine gaps,
contradictions, boundaries, and success criteria. It should offer a recommendation
and concise trade-offs when that helps the user decide.

The agent evaluates runtime, architecture, dependencies, feasibility, and
technical consequences using repository context and engineering judgment. It
adopts established or easily reversible defaults without burdening the user.
It raises consequential choices when they affect scope, compatibility,
security, operations, cost, or another user priority.

If the requested work is too broad for one coherent spec, the agent proposes a
decomposition before continuing. If a blocking answer genuinely cannot be
obtained, it reports that requirements remain incomplete instead of inventing
an answer.

### Completion gate

Questioning stops only when:

- Scope boundaries are explicit.
- No known requirements contradict one another.
- Expected behavior and constraints are unambiguous.
- Completion can be verified.
- No blocking scope questions remain.

The skill then presents a normalized summary containing:

- Goal and problem.
- Relevant users and use cases.
- In-scope and out-of-scope work.
- Functional and relevant quality requirements.
- Constraints, decisions, and assumptions.
- A verifiable definition of done.

The user must approve or correct the summary. Corrections resume the workflow.
Approval completes it and allows an immediate handoff to `specs`. The skill
writes no files.

## `specs` skill

### Entry and drafting

The workflow consumes an approved requirements summary. If none is present, it
runs the `requirements` workflow using all context already supplied, then
resumes only after approval.

Before drafting, the agent inspects the relevant repository and uses technical
judgment to make the design concrete. It may not silently change approved
requirements. A consequential ambiguity becomes a workflow question; a
reversible internal choice may be resolved by the agent.

Specs are written under `docs/specs`. An established repository naming
convention takes precedence; otherwise use `docs/specs/<descriptive-slug>.md`.

### Template precedence

Choose structure in this order:

1. An explicit user-provided template or structure.
2. An established repository convention.
3. Planning's default template.

Alternative structures may rename or combine sections. They still cover the
required information unless the user explicitly overrides it.

Planning's default template requires:

- Summary.
- Context and motivation.
- Goals and non-goals.
- Requirements and expected behavior.
- Verification organized as test surfaces followed by the behaviors verified
  at each surface.

It conditionally includes:

- Technical design and constraints when they materially constrain the
  solution.
- Alternatives and consequential decisions when their rationale has lasting
  value.

`Open questions` is draft-only. The agent asks the user questions that require
user intent, incorporates each answer into its canonical section, and removes
the resolved question. An approved spec contains no blocking open questions.
The template has no target length and does not retain empty sections.

### Independent review

After writing the draft, run one automatic independent review unless the user
opts out. Use one fresh, read-only reviewer. Give it the approved requirements,
the exact spec, and only relevant repository context.

Reviewer selection is capability-based:

- Use a capable general-purpose reviewer at the host's normal intelligence and
  effort for ordinary work.
- Prefer a stronger available tier and higher reasoning effort for security,
  data migration, public contracts, or broad architectural changes.
- Never hard-code model or agent names, and fall back to host defaults when
  selection controls are unavailable.

If subagents are unavailable, the managing agent performs the same review and
states that it was not independent.

The reviewer reports only material findings:

- Missing or contradicted requirements.
- Ambiguous behavior or scope.
- Unsupported technical assumptions or feasibility problems.
- Unrequested scope expansion.
- Missing verification surfaces or behaviors.

It avoids pedantic style criticism. It may request simpler prose when jargon
or density makes the spec meaningfully harder for humans or agents to
understand, but only when the revision preserves its meaning, context, and
facts.

The managing agent exercises its own judgment over every finding and surfaces
a compact disposition list in the conversation:

- `Addressed`: the spec was changed; identify where.
- `Elevated`: user adjudication is required; approval is blocked.
- `Dismissed`: no change is warranted; give a short reason.

The disposition list is not stored in the spec. Addressed findings are resolved
automatically, elevated findings are presented to the user, and dismissed
findings create no future obligation. Review runs again only when the
resolutions materially change scope or design.

For a later review against an archived spec, the managing agent uses
`read-archive` to select and load the exact verified Markdown, then supplies
that content directly to the reviewer. The reviewer does not browse or load
the archive broadly. During initial spec creation, review always precedes
archival and therefore reads the live Markdown.

### Approval

After review findings are resolved or adjudicated, the user explicitly
approves or corrects the spec. Corrections are incorporated, and material
changes trigger another review. No archive or version-control commit occurs
before approval.

## Preservation after approval

After approval, inspect the available skill inventory for
`archiving-documentation`. Do not infer installation from directories or an
existing ledger.

If the skill is available, ask whether to archive the approved spec with
Library or keep the Markdown in repository history. Honor a choice the user
already supplied without asking again.

When the user chooses archive:

- Give `archiving-documentation` the exact approved path.
- Follow Library's scan and deletion confirmation requirements.
- Respect Library's result and stop without creating a version-control commit.
- Do not silently fall back to committing the Markdown if archival fails.

When the user chooses keep, or Library is unavailable, commit only the approved
spec using the repository's configured version-control workflow. Spec approval
authorizes this commit; no redundant confirmation is needed. Existing unrelated
working-copy changes must not be included.

If no supported version control exists, leave the approved spec under
`docs/specs` and report that it was not committed. On any archive or commit
failure, preserve recoverable state, report the exact outcome, and do not claim
completion.

## Documentation and marketplace integration

- Add Planning to both marketplace indexes.
- Add Planning to the root README's plugin table with a link to its README.
- Document installation for Codex, Claude Code, and Antigravity in
  `plugins/planning/README.md`.
- Document both skills, example requests, the approval flow, independent review,
  and optional Library integration in the plugin README.
- Keep detailed templates and reviewer instructions in their reference files,
  not duplicated in README prose.

## Validation

### Deterministic checks

Generalize `tests/test_marketplace.py` so both marketplace indexes must agree
and every listed plugin must have its directory, manifests, README, and root
README link. Parse all added JSON. Do not add tests that merely grep skill prose
and claim to prove agent behavior.

### Behavioral checks

Store focused behavioral cases in each skill's `evals/evals.json`. The JSON is
a portable test specification, not automated proof by itself; this repository
currently has no eval runner.

When the host exposes agent trajectories, grade both tool use and output.
Otherwise run the same cases as manual smoke tests and inspect the transcript.
Do not build a custom runner until repeated manual validation becomes costly.

Use fixture-only sentinel facts to make inspection observable. For example, a
fixture repository may contain an unusual `max_batch_size = 7319` that the
prompt omits. The `requirements` case passes only when the trace shows a
repository read, the summary contains `7319`, and the agent does not ask the
user for that value.

Behavioral cases cover:

- Preserving supplied requirements without asking them again.
- Investigating repository facts before questioning.
- Refusing premature completion when scope is missing or contradictory.
- Producing the agreed summary and requiring approval.
- Searching archived metadata only when historical context is plausibly
  relevant.
- Routing `specs` through `requirements` when no approved summary exists.
- Applying required and conditional template content without boilerplate.
- Finding seeded material spec defects without style nitpicks.
- Dispositioning findings as `Addressed`, `Elevated`, or `Dismissed`.
- Preventing archive and commit operations before approval.
- Offering archival only when Library is available.

Multi-turn cases inspect repository or version-control state as well as the
transcript. For example, the approval-gate case must show no commit before the
approval message and a spec-only commit afterward.
