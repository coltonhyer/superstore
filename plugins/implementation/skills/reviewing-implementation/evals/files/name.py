def name_error(value):
    if not value:
        return "blank"
    if "/" in value:
        return "slash"
    return None
