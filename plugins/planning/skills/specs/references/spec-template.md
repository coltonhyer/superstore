# Default Specification Structure

Adapt the headings to the repository, but preserve the required information.
Do not copy empty sections into a draft.

## Required information

### Summary

State the proposed change and intended outcome.

### Context and motivation

Explain the current problem and why it matters.

### Goals and non-goals

Separate intended outcomes from explicit exclusions.

### Requirements and expected behavior

Describe observable behavior, constraints, and relevant quality requirements.

### Verification

Organize verification by test surface. Under each surface, list the behaviors
that surface verifies.

## Conditional information

Include `Technical design and constraints` only when implementation choices
materially constrain the solution.

Include `Alternatives and consequential decisions` only when their rationale
has lasting value.

## Draft-only questions

Use `Open questions` only while an answer requiring user intent is unresolved.
After an answer, incorporate it into the canonical section and remove the
question. An approved spec has no blocking open questions.
