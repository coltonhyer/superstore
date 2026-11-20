from rate import valid_rate


assert valid_rate(1)
assert not valid_rate(0)
assert not valid_rate(-1)
