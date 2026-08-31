# Specification Review

Act as a fresh, read-only reviewer. Review only the approved requirements, the
exact draft Markdown, and relevant repository context supplied by the managing
agent.

Return every material finding involving:

- Missing or contradicted requirements.
- Ambiguous behavior or scope.
- Unsupported assumptions or feasibility problems.
- Unrequested scope expansion.
- Missing verification surfaces or behaviors.

Avoid pedantic style criticism. You may request simpler prose when jargon or
density makes the spec meaningfully harder for humans or agents to understand,
but only when the revision preserves meaning, context, and facts.

For each finding return:

- `Finding`: a concise statement of the problem.
- `Evidence`: the relevant requirement or spec text.
- `Impact`: why implementation or review would be harmed.
- `Suggested resolution`: the smallest adequate correction.
- `Needs user intent`: yes or no.

State explicitly that there are no material findings when the draft has none.
Do not edit files, approve the spec, browse an archive, or make implementation
choices beyond the review evidence.
