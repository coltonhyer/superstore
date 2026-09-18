# Shared standards

<a id="shared-001"></a>
## SHARED-001: Invalid limits are explicit

Limit parsing must raise ValueError for an invalid value, with a message that
identifies the limit and includes the rejected value. It must not return a
success-shaped sentinel such as zero. Callers show this message to operators.
