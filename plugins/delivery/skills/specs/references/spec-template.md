# Default Specification Structure

Adapt headings to higher-precedence user or repository templates without copying
empty sections into a draft. Preserve the required information below unless the
user explicitly overrides it.

Write each living spec in the present tense to describe target behavior,
non-goals, and constraints for one enduring capability or domain (named after the
domain noun, not a verb or change). Do not write change-scoped delta narrative;
explain why a change happens now, migration steps, exact files, and concrete
test commands in the implementation plan instead. If adding a change would
stretch a spec's one-sentence `description` to an unrelated concern or make it
unwieldy to verify in one sitting, split along the domain seam using
`supersedes`.

## Required sections

### Summary

State the enduring capability, its boundaries, and the intended target state.

### Goals and non-goals

Separate target outcomes from explicit exclusions so downstream work does not
drift into excluded behavior.

### Requirements and expected behavior

List flat, individually verifiable requirements (`R1`, `R2`, ...) describing
externally observable behavior, constraints, and relevant quality requirements:

- Place approved observable acceptance criteria from requirements (`Definition of
  done`) inline under the requirement or expected behavior they govern.
- When behavior varies across runtime triggers, inputs, or states, lead with a
  compact `Scenario | Expected outcome` table instead of burying branches in
  prose.
- Express standalone triggered behaviors using Given / When / Then where clear,
  keeping `Then` focused on an externally observable outcome.
- Keep triggerless rules and invariants in a short list.

Citation rule: plans, handoffs, and review findings cite requirements as
`<spec-slug>:R#` against a pinned spec blob. Sibling living specs reference one
another by path and capability rather than by requirement number.

## Conditional sections

- `Technical design and constraints`: Include only when technical choices or
  system boundaries materially constrain valid implementations.
- `Alternatives and consequential decisions`: Include only when the rationale
  has lasting value for future readers and maintainers.

## Draft-only sections

- `Open questions`: Include only while an answer requiring user intent is
  unresolved. Once answered, integrate the decision into the canonical section
  and remove the question. An approved spec has no blocking open questions.

## What to omit

Omit the following from living specs unless explicitly required by a
higher-precedence user or repository template:

- A separate `Verification` section.
- Mandatory `Context and motivation` or `Deployment and data effects` sections.
- Internal implementation file paths, line numbers, and test names (externally
  observable contract paths and OKF frontmatter paths are allowed).
- Change-scoped narrative such as why this delta happens now, migration steps,
  exact implementation files, and concrete test commands.
