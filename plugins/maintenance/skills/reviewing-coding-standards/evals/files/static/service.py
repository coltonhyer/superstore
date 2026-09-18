def BadName(value):  # standards-exception: legacy caller
    return value


def alsoBad(value):
    return value


def name_too_long_for_rule(value):  # standards-exception: public API compatibility
    return value


def unrelated_reason_name(value):  # standards-exception: it is Tuesday
    return value


def arguable_reason_name(value):  # standards-exception: migration concern
    return value


def missing_reason_name(value):
    return value

