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

- When history is plausibly relevant, resolve the document folders in this
  order: a path the user names, a folder that `AGENTS.md` or `CLAUDE.md` at the
  repository root names for that type (such as `Specs live in design/specs/.`),
  then `docs/<kind>/` (`docs/specs/`, `docs/plans/`, `docs/handoffs/`). When
  any of those folders exists, load the `library` skill if it is in the active
  skill inventory and read the current documents on the subject by type and
  tags. Without the skill, filter the documents' frontmatter lines in those
  folders directly. The frontmatter is the block between the first two `---`
  lines at the top of a file; filter on those lines only, with any tool whose
  output is only that block's lines (a YAML parser is fine when the
  environment has one), and never decide from a line below the closing `---`,
  where bodies hold example frontmatter in fenced blocks. For example, this
  prints only frontmatter, one `FILE: line` per line, on any POSIX `awk`
  (`find` reports a missing folder and carries on, `-H` follows a folder that
  is a symbolic link, and `awk` alone stops at the first path it cannot
  open):

  ```sh
  find -H docs/specs docs/plans -maxdepth 1 -name '*.md' ! -name index.md ! -name log.md \
    -exec awk '{ sub(/\r$/, "") }
         FNR == 1 { fm = ($0 == "---"); next }
         fm && /^---$/ { fm = 0 }
         fm { print FILENAME ": " $0 }' {} + | grep -E ': (status|tags): '
  ```

  Change the `grep` to `': tags: .*[[, ]<slug>[],]'` to match a whole tag
  slug.

  `head`, `cat`, and a version-control `show` or `diff` of a document count as
  reading its body, so do not use them to inspect frontmatter or to discover
  documents, and do not use version-control history to discover documents.
  A document is current when its `status` is absent or `stable`. Read only the
  current documents' bodies; a `draft` or `deprecated` document is ruled out
  from its frontmatter and must not shape the questions you ask. Read its body
  only when the user asks for an earlier design or a comparison with it; a
  request that changes established behavior is not that request.
- Do not search the document folders for every task. A missing folder is not
  an error: `find` reports it and carries on, and that folder simply has no
  hits.

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
