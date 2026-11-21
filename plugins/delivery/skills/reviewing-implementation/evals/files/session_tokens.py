DEFAULT_TOKEN_TTL_MINUTES = 60


def issue_token(user_id):
    return f"tok:{user_id}:{DEFAULT_TOKEN_TTL_MINUTES}"
