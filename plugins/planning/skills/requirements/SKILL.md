---
name: requirements
description: Use when a proposed change needs its requirements clarified, normalized, and explicitly approved before a spec, plan, or implementation. Start from supplied requirements and repository context instead of re-eliciting known facts.
---

# Requirements

Produce an approved, verifiable requirements summary in the conversation. Do
not write a requirements file or begin specification or implementation work.

## Start from available context

1. Extract the facts, decisions, constraints, and unresolved points from
   everything the user already supplied. Detailed requirements, issue text,
   and existing documents are starting context, not material to ask for again.
2. Inspect the relevant repository context before questioning. Read the code,
   documentation, configuration, and version-control history that can answer
   scope or current-behavior questions. Keep the inspection proportional to the
   request; do not read the entire repository by default.
3. Do not ask the user for a fact the repository can answer.

Historical documentation is relevant when the request cites an earlier design
or changes established behavior:

- Check the active skill inventory for `read-archive`; do not infer its
  availability from plugin directories or a ledger file.
- When it is available and history is plausibly relevant, search compact
  metadata first and load only the selected document needed for the decision.
- Do not search the archive for every task. A missing Library skill or ledger
  is not an error.

## Resolve gaps

Ask one focused question at a time about a genuine gap, contradiction, scope
boundary, or success criterion. Begin with the question whose answer removes
the most uncertainty.

Use engineering judgment for runtime, architecture, dependencies, feasibility,
and other technical consequences:

- Adopt an established repository choice or an easily reversible default
  without burdening the user.
- Raise a choice when it changes scope, compatibility, security, operations,
  cost, or another user priority.
- When the user must choose, give a recommendation and concise trade-offs.

A workflow question requires user intent or a consequential decision. An
implementation detail the agent can safely derive is not a requirements
question.

If the requested work is too broad for one coherent specification, propose a
decomposition before continuing. If a blocking answer cannot be obtained,
state that the requirements remain incomplete rather than inventing it.

## Completion gate

Continue gathering requirements until all of these are true:

- Scope boundaries are explicit.
- No known requirements contradict one another.
- Expected behavior and constraints are unambiguous.
- Completion can be verified.
- No blocking scope question remains.

Then present this complete summary:

~~~markdown
## Requirements summary

### Goal and problem

### Relevant users and use cases

### In scope

### Out of scope

### Functional requirements

### Relevant quality requirements

### Constraints, decisions, and assumptions

### Definition of done
~~~

Keep the content concise but preserve every approved fact and decision.
`Definition of done` must be observable or testable. Ask the user to approve
or correct the summary. Corrections resume the workflow; only explicit approval
completes it.
