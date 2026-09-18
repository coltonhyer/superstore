# Coding standards

These agreed rules cover Python under src/, tests/, and scripts/. Read shared
and every applicable topic. Applicability helps navigation; inspect other
standards or repository context whenever useful.

Must and must not are requirements. Should and should not are recommendations
allowing a reasoned exception; reviewers distinguish the two and consider reasons.
Precedence: agreed local rules, existing configuration for mechanical matters,
then explicitly adopted external baselines. Ordinary source citations import
no rules. The supplied source notes are research evidence, not additional policy.

| Topic | Description | Applies to |
| --- | --- | --- |
| [Shared](#shared-standards) | Invalid-limit contract | src/, tests/, scripts/ |
| [Python](#python-standards) | Errors, docs, naming | Python in src/, tests/, scripts/ |
| [Tests](#testing-standards) | Coverage and naming | tests/ |
| [Scripts](#script-standards) | Import behavior | scripts/ |

# Shared standards

<a id="shared-001"></a>
## SHARED-001: Invalid limits are explicit

Limit parsing must raise ValueError for an invalid value, with a message that
identifies the limit and includes the rejected value. It must not return a
success-shaped sentinel such as zero. Callers show this message to operators.

# Python standards

<a id="py-001"></a>
## PY-001: Narrow exception handling

Parsing code must catch only exceptions it can handle; numeric conversion may
catch ValueError. Catching Exception conceals programming errors.

<a id="py-002"></a>
## PY-002: Explain non-obvious behavior

Public functions should have a short docstring. An obvious one-line forwarding
wrapper may omit it with a reasoned explanation in its review.

<a id="py-009"></a>
## PY-009: Python naming baseline

Python function names must follow PEP 8's Function and Variable Names section,
reference read 2026-09-18: https://peps.python.org/pep-0008/#function-and-variable-names.
This adoption covers only function naming (lowercase words separated by
underscores, with compatibility exceptions); it does not import the whole guide.

Mechanical checks live in [pyproject.toml](../../pyproject.toml): `ruff check .`
and `ruff format --check .`. Ruff's selected rules do not establish error-message
quality or this function-naming baseline.

# Testing standards

<a id="test-001"></a>
## TEST-001: Demonstrate boundary behavior

Limit-parser tests must cover both allowed endpoints, out-of-range values, and
malformed text. Use the repository's unittest convention.

<a id="test-002"></a>
## TEST-002: Descriptive test names

Test names should state the behavior and outcome rather than numbered examples.

# Script standards

<a id="script-001"></a>
## SCRIPT-001: Imports have no side effects

Scripts under scripts/ must defer execution to a main function guarded by
`if __name__ == "__main__"`. This requirement does not govern library modules.
