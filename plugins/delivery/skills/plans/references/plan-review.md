# Plan review contract

Act as a fresh, read-only reviewer. Every reviewer starts with fresh context
and no parent conversation history; on hosts exposing a history-forking
control, parent history is disabled (for example, `fork_turns: "none"`). Review
only the approved specification(s), exact plan, and relevant repository context
supplied by the managing agent.

Identify the reviewed plan path and state, each pinned approved spec (`<path>,
blob <12-char hash>`, or non-repository identity), and any context limitation.

## Checks

Return every material finding involving:

- **Spec coverage and multi-spec `implements`:** Material gaps in spec
  coverage across every spec listed in `implements`, or unsupported repository
  assumptions. Flag a plan that leaves required spec behavior undelivered, or
  assigns it to code outside the repository without evidence, even when the plan
  states that exclusion openly; plan approval cannot stand in for a scope
  decision. Behavior the plan assigns to a named separate plan of the same
  specification is a scope boundary to check, not a gap.
- **Change-scoped slug and blob pins:** Verify a change-scoped slug based on
  supplied context when the plan targets multiple specs or an existing living
  spec that already has an earlier plan. Verify committed 12-char blob pins (`<path>, blob <12-char
  hash>`) for every cited repository spec, and flag any branch or pre-merge
  commit hash, Jujutsu change ID, or revision range anywhere in the plan.
- **Task boundaries, discovery, and checks:** Check task boundaries or
  ordering, delegation context, relevant paths and patterns, and concrete
  completion checks. Flag unnecessary scope or implementation prescriptions when
  they would make the plan misleading or infeasible. Do not require arbitrary
  task counts or style changes. Flag a task that merely defers required spec
  behavior or an unresolved material scope, ownership, or authority boundary to
  discovery; discovery is sufficient only when its observable result and
  completion observation are defined. When bounded inspection and ordinary
  engineering judgment consistent with the approved spec can resolve a missing
  owner, location, or verification approach, the plan may choose a new
  within-scope file or check; otherwise identify the approval-blocking user
  decision rather than treating a placeholder as a resolution.
- **Scope fit:** Classify any addition beyond the approved spec(s) or
  requirements as *serves the ask* (non-behavior-changing support work directly
  serving the ask), *unnecessary*, or *conflicts*. Flag additions that change
  observable behavior or delivered scope as requiring explicit user intent (or
  `Decisions for review` in autonomous mode).

## Round scoping

- **Rounds 1 and 2:** Review the full plan.
- **Round 3 onward (except a full-plan final round after a step-back
  redesign):** Review the diff since the prior round, prior findings and their
  dispositions, and fixed defect classes — checking that diff, newly introduced
  regressions, and whether each fix resolved its defect class. Targeted reads
  are strictly limited to the supplied plan, spec(s), and relevant repository
  code; do not browse repository documents beyond the supplied plan and spec(s).

## Output shape

Return `usable` output: either an explicit **No material findings** statement
with reviewed scope/state and remaining uncertainty, or structured findings
where each item includes:

- **ID:** Stable identifier (for example, `P1`, `P2`).
- **Severity:** `Blocking` (a correctness defect, requirement or scope gap,
  false code claim, consumer breakage, hollow guarantee, or contract/gate defect)
  or `Non-blocking` (minor polish or an optional improvement that does not break
  correctness, requirements, scope, consumers, or contracts).
- **Defect class and instance:** One-line defect class plus the specific
  instance (addressing fixes every instance of the class).
- **Evidence:** The relevant spec requirement, plan text, or repository
  code/symbol.
- **Impact:** Why implementation, verification, or review would be harmed.
- **Smallest adequate correction:** Minimal fix for the instance and class.
- **Needs user intent:** `yes` or `no`.
- **Scope-fit label:** `serves the ask`, `unnecessary`, or `conflicts` when
  flagging an out-of-scope addition.

## Strict reviewer boundaries

- Never mutate the repository.
- Never approve, commit, or execute the plan.
- Never assign finding dispositions (`Addressed`, `Elevated`, `Dismissed`, and
  `Declined` belong solely to the managing agent; `Declined` is for
  `Non-blocking` only).
- Never browse repository documents beyond the supplied plan and spec(s).
- Never make implementation choices beyond the evidence supplied for review.
- Never request appeasement prose that a human reader does not need.
