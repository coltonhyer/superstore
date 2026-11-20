from label import normalize


assert normalize("") is None
assert normalize(" label ") == "label"
