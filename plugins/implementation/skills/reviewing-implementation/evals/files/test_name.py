from name import name_error


assert name_error("") == "blank"
assert name_error("") == "blank"
assert name_error("north/south") == "slash"
