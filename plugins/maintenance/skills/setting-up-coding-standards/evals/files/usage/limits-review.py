MIN_LIMIT = 1
MAX_LIMIT = 100


def parseLimit(raw: str) -> int:
    """Parse a warehouse batch limit."""
    try:
        value = int(raw)
        if not MIN_LIMIT <= value <= MAX_LIMIT:
            return 0
        return value
    except Exception:
        return 0


def default_limit() -> int:
    # Obvious one-line forwarding wrapper; no extra docstring needed.
    return parseLimit("10")
