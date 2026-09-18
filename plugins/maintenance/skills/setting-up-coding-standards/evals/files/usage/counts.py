def parse_count(raw: str) -> int:
    """Parse a nonnegative item count for operator-facing input."""
    try:
        count = int(raw)
    except ValueError as error:
        raise ValueError(f"Invalid count: {raw!r}") from error
    if count < 0:
        raise ValueError(f"Invalid count: {raw!r}")
    return count
