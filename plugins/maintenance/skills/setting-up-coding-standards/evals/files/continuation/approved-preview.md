# Previously approved proposal, supplied by the user

The user approved migrating the following exact meanings:
SHARED-004: Label normalization must not write files or send network requests.
PY-007: Public Python functions must use snake_case.
PY-011: Input parsing must catch only the specific exceptions it can handle.
PY-013: Every assignment must have an explanatory comment.
Retired PY-003 remains retired.

The complete proposed files were a flat docs/standards/README.md index with
shared.md containing SHARED-004 and python.md containing the three PY rules.
The index defines must/must not as requirements, should/should not as
recommendations with reasoned exceptions, applicability to Python in src/ and
tests/, and precedence: local rules, mechanical configuration, adopted baseline.
No baseline is adopted. Python guidance links pyproject.toml and the README Ruff
commands. Existing code and tools remain unchanged.

The approved migration replaces only coding sections of AGENTS.md and
CONTRIBUTING.md with canonical-index pointers, instructs agents to read applicable
standards before code work, preserves release/access text and CLAUDE.md's import,
updates docs/onboarding.md's incoming rule link, and leaves a short redirect at
docs/python-style.md because printed links need that path. Before preview,
CONTRIBUTING.md's PY-007 had no compatibility exception and Development access
had no emergency contact. No writes from this proposal have occurred yet.
