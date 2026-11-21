"""Production webhook entry point for scheduled billing events."""

from app.billing import _generate_invoice


def handle_billing_webhook(
    event_type: str,
    account: dict[str, str],
) -> dict[str, str] | None:
    """Process a billing webhook event and issue invoices for renewal triggers."""
    if event_type == "subscription.renewal_due":
        return _generate_invoice(account)
    return None
