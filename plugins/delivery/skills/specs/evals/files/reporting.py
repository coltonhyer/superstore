"""Delinquency reporting helpers for subscription accounts."""


def is_delinquent(account: dict[str, str]) -> bool:
    """Return True when the account has a past_due subscription status."""
    return account["status"] == "past_due"


def list_delinquent_accounts(
    accounts: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Return all accounts currently in a delinquent subscription state."""
    return [account for account in accounts if is_delinquent(account)]
