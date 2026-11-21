# Specification Review

Before spec approval, launch Reviewer A and Reviewer B in parallel as fresh,
read-only reviewers, except on interactive mode's fast-path when the user
explicitly approves a spec they describe as already reviewed.

Every reviewer starts with fresh context and no parent conversation history. On
hosts exposing a history-forking control, the caller explicitly disables parent
history (for example, `fork_turns: "none"`).

## Reviewer A: Requirements and spec

### Reviewer A inputs and read boundary

Receive only the approved requirements, any explicit higher-precedence user or
repository template constraints governing the draft, and the spec draft. Read no
repository code and browse no other repository documents — including in Round 3
onward targeted reads, which are limited strictly to the spec draft.

### Reviewer A checks

Return every material finding involving:

- **Requirement coverage and contradictions:** Missing, altered, or
  contradicted requirements, including inline `Definition of done` criteria.
- **Ambiguity:** Undefined behavior or boundaries where two readers would not
  build the same thing.
- **Scope fit:** Classify any addition beyond the approved requirements as
  *serves the ask* (non-behavior-changing support work directly serving the ask),
  *unnecessary*, or *conflicts*. Flag additions that change observable behavior
  or delivered scope as requiring explicit user intent (or `Decisions for
  review` in autonomous mode).
- **Ask for less:** Flag internal implementation file paths, line numbers, test
  names, separate `Verification` sections, or change-story bloat. Exempt OKF
  frontmatter paths, externally observable contract paths, and headings
  required by a supplied higher-precedence template.
- **Readability without style nits:** Avoid pedantic style criticism. Request
  simpler prose only when jargon or density makes the spec meaningfully harder
  for humans or agents to understand while preserving meaning, context, and
  facts.

## Reviewer B: Spec and code

### Reviewer B inputs and read boundary

Receive the spec draft and read-only repository access. In Round 3 onward
targeted reads, read the spec draft and repository files only to verify
class-wide fixes or code claims.

### Reviewer B checks

Return every material finding involving:

- **Code accuracy:** Verify every claim about current repository code (whether
  cited or not) and flag contradictions with actual files, symbols, or behavior
  present in the repository.
- **Consumer impact:** Trace changed symbols or values to all consumers,
  including stored data or operational effects when relevant.
- **Hollow guarantees and footguns:** Verify that normal production triggers
  reach and satisfy the practical goal rather than being blocked, bypassed, or
  satisfied only in degenerate cases.
- **Optional testability check:** When useful, verify testability of specified
  behaviors on a temporary copy of the source outside the repository without
  mutating the repository.

### Greenfield and docs-only repositories

When no relevant implementation code exists yet, do not raise `Blocking`
false-code-claim findings merely because target application code is absent.
Still check internal consistency and hollow guarantees in the draft, state that
no relevant implementation code was present to verify against, and return
`No material findings` when none exist.

## Round scoping

- **Rounds 1 and 2:** Review the full spec draft.
- **Round 3 onward (except a full-draft final round after a step-back
  redesign):** Review the diff since the prior round, prior findings and their
  dispositions, and fixed defect classes — checking that diff, newly introduced
  regressions, and whether each fix resolved its defect class — strictly
  respecting each role's read boundary above during targeted reads.

## Shared finding output shape

Each reviewer returns `usable` output: either an explicit `No material
findings` statement when none exist, or structured findings where each item
includes:

- **ID:** Stable reviewer-prefixed identifier (for example, `A1`, `A2` for
  Reviewer A; `B1`, `B2` for Reviewer B).
- **Severity:** `Blocking` (a correctness defect, requirement or scope gap,
  false code claim, consumer breakage, hollow guarantee, or contract/gate defect)
  or `Non-blocking` (minor polish or an optional improvement that does not break
  correctness, requirements, scope, consumers, or contracts).
- **Defect class and instance:** One-line defect class plus the specific
  instance.
- **Evidence:** The relevant requirement, spec text, or repository code/symbol.
- **Impact:** Why implementation, verification, or review would be harmed.
- **Smallest adequate correction:** Minimal fix for the instance and class.
- **Needs user intent:** `yes` or `no`.
- **Scope-fit label:** `serves the ask`, `unnecessary`, or `conflicts` when
  flagging an out-of-scope addition.

## Strict reviewer boundaries

- Never mutate the repository, including during optional temporary-copy
  testability checks.
- Never approve the spec.
- Never assign finding dispositions (`Addressed`, `Elevated`, `Dismissed`, and
  `Declined` belong solely to the managing agent).
- Never make implementation choices beyond the review evidence.
- Never request appeasement prose that a human reader does not need.
