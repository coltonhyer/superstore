from src.auth.tokens import issue_token


def create_session(user_id):
    return issue_token(user_id)
