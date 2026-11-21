from auto import status_label

assert status_label(True) == "enabled"
assert status_label(False) == "disabled"
