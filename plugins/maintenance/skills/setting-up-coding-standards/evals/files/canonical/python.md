# Python conventions

<a id="py-007"></a>
## PY-007: Public names

Public Python functions must use snake_case.

<a id="py-011"></a>
## PY-011: Error handling

Input parsing must catch only the specific exceptions it can handle.

<a id="py-013"></a>
## PY-013: Comment every assignment

Every assignment must have an explanatory comment.

Mechanical checks: [Ruff configuration](../../pyproject.toml), `ruff check .`
and `ruff format --check .`. Naming and meaningful comments need human judgment.
