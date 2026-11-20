from context import normalize


assert normalize("label") == "label"
assert normalize("") is None
