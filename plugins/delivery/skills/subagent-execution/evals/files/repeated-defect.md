# RETRY-1 evidence

Approved behavior rejects blank labels. Two implementer reports each changed
formatting only. `python3 test_label.py` fails because `label.normalize("")`
returns an empty string instead of rejecting blank input. The attached source,
check, and `docs/recovery/retry-attempts.md` are the available evidence.
Determine supported causes and a correction/check without modifying
implementation.
