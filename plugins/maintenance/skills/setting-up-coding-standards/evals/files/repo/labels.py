def normalize_label(value: str) -> str:
    return value.strip().upper()


def join_labels(values: list[str]) -> str:
    return ",".join(normalize_label(value) for value in values)
