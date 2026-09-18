# Research guidance

Research the topics proposed after inspection and the mode decision. Use
available host capabilities; do not require a provider, plugin, language, linter,
or catalog of rules.

## Evidence and fit

Prefer applicable primary sources: language and framework documentation,
maintainers' style guides, actual linter documentation, and respected open-source
projects with comparable product and runtime needs. Check the repository's
language versions, frameworks, product constraints, and actual configuration
before recommending a rule. Reputation alone does not establish applicability.

Reuse relevant verified material already available in context or a cache. Keep
links to sources actually read and identify the relevant edition, version, or
date when it matters. Distinguish available cached evidence from live research;
do not present old evidence as freshly checked. When freshness affects a
recommendation, verify it with available live capabilities or disclose the limit.

If research is unavailable or evidence insufficient, identify the affected
recommendation and obtain the missing source or a user decision on proceeding
without it. Continue unaffected work, but do not invent support or claim the
research is complete. Repository inference can motivate a proposal, not establish
either external endorsement or user adoption.

Read actual tool configuration and commands, then consult documentation matching
the relevant tool/version to determine which proposals are checked, configurable
but not currently checked, or require judgment. Verify both current enforcement
and claims about proposed tooling follow-up against the exact rule and applicable
exceptions. A formatter target or formatting check does not establish strict
validation of every instance; disclose unsupported coverage as an evidence gap.
Do not assume an installed linter enforces every supported rule or change its
configuration during this workflow.
Bring deliberate local/tool conflicts and effective timing into the discussion.

## Starting points, not an adopted rulebook

These guides informed the output design and can start relevant research. Read
only sources useful to the repository and proposed topics; this list is neither
a required research checklist nor a source of automatically binding rules.

- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/about.html):
  compact navigation, topic documents, and individually linkable guidelines.
- [Airbnb JavaScript guide](https://github.com/airbnb/javascript): concise rules,
  explanations, and examples for relevant JavaScript projects.
- [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html):
  explanations of consequential tradeoffs in its C++ context.
- [C++ Core Guidelines structure](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#ss-struct):
  rule identifiers and titles with reasons, examples, and enforcement guidance.
- [PEP 8](https://peps.python.org/pep-0008/): Python style guidance.
- [Django coding style](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/):
  a project baseline with local conventions; select a relevant version if used.

Use other primary sources when they better fit the repository. Research informs
concrete user choices; it does not replace the agreed output format or create an
additional competing rulebook. An external baseline becomes binding only through
explicit adoption with scope, reference, local ID, exceptions, and precedence as
defined in [the output format](output-format.md).
