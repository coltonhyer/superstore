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
