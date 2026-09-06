def parse_account(value):
    return value


def request_account(value, send):
    return send(parse_account(value))
