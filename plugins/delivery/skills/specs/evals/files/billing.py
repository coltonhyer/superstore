"""Billing account guards and API invoice generation."""


class SubscriptionError(ValueError):
    """Raised when a billing action is blocked by subscription state."""


def is_past_due(account: dict[str, str]) -> bool:
    """Return whether the account is currently marked past_due."""
    return account.get("status") == "past_due"


def require_active_subscription(account: dict[str, str]) -> None:
    """Reject delinquent accounts before API invoice creation."""
    if is_past_due(account):
        raise SubscriptionError("account_past_due")


def _generate_invoice(account: dict[str, str]) -> dict[str, str]:
    """Create and return an invoice record for the account."""
    return {"account_id": account["id"], "status": "issued"}


def create_invoice_via_api(account: dict[str, str]) -> dict[str, str]:
    """API entry point for creating an invoice."""
    require_active_subscription(account)
    return _generate_invoice(account)
