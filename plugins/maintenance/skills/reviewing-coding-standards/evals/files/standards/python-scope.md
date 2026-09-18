# Scoped Python naming rules

<a id="py-101"></a>
## PY-101: Local spelling

Functions in `src/api.py` MUST use snake_case. This local rule overrides the
configured naming style and external baseline.

<a id="py-102"></a>
## PY-102: Adopted temporary-name rule

Functions in `src/api.py` MUST NOT be named `tmp`. This rule adopts
`evidence/external.md`, edition 2025, section `NAMING-1`.

The same guide's `PARAMETERS-2` discussion is attribution only and is not
adopted.

<a id="py-103"></a>
## PY-103: Parameter count

Functions in `src/api.py` SHOULD accept at most three parameters. This
recommendation is the documented current expectation while this deferred timing
note remains. The note defers promotion to a requirement until
`max_parameters_follow_up_enabled` is enabled in `standards-check.json`. That
setting is already enabled, so the still-deferred note is apparently stale; the
note remains authoritative while present.

<a id="py-104"></a>
## PY-104: Retired abbreviation rule

Retired on 2025-01-01; do not enforce.

<a id="py-105"></a>
## PY-105: Ambiguous-name draft

Functions should or must avoid names containing `ambiguous`; obligation strength
has not been decided.

<a id="py-106"></a>
## PY-106: Missing adopted source

Functions containing `missing_source` MUST comply with
`evidence/missing.md`, edition 2025, section `MISSING-1`.
