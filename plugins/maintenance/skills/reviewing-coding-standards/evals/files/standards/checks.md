# Configured checks

<a id="check-001"></a>
## CHECK-001: Explicit obligation

The `explicit-obligation` diagnostic from the configured standards check MUST
pass for Python source files.

<a id="check-002"></a>
## CHECK-002: Configured severities

Other diagnostics from commands in `standards-check.json` use their configured
severity. Diagnostics without a severity are pass/fail obligations.

Configured unit tests and migration scripts are not standards-audit checks.

