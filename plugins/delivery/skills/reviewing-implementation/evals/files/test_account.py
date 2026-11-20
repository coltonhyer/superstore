from unittest.mock import patch

from account import request_account


with patch("account.parse_account", return_value="acct-123"):
    assert request_account("not an account", lambda value: value) == "acct-123"
