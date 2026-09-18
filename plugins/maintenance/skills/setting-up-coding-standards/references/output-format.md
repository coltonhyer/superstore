# Standards output format

Use `docs/standards/README.md` as the canonical index. Put relevant topic files
directly beside it with short lowercase kebab-case names. Only `README.md` is
required by name; choose topics from agreed standards, not this example. Do not
create one file per rule, unused sections, required front matter, a registry,
parser, or generated documentation.

Standards describe obligations for future repository work and the persistent
context needed to apply them, including useful source attribution. Current setup
restrictions govern execution and conversational reporting; they and setup
history do not belong in the standards.

## Index

State scope briefly. Include relative topic links, short descriptions, and
concrete applicability by paths, languages, or kinds of work. Make shared
guidance explicit: all applicable documents can govern one change. Applicability
helps navigation and does not prohibit inspecting other standards or files.
Do not repeat the rules as a second checklist.

Define obligation words once: **must** and **must not** are requirements within
the stated scope; **should** and **should not** are recommendations permitting a
reasoned exception. Reviewers distinguish requirement violations from
recommendations and consider the reason for an exception.

State precedence once: agreed local rules first, then existing tool configuration
for mechanical matters, then an explicitly adopted external baseline. Include
this precedence in the approval preview. Where configuration differs mechanically
from the baseline, that precedence resolves the exception without a separate
question or a note for every mismatch.

Small illustrative index; its topics and paths are not mandatory:

```markdown
# Coding standards

These standards cover production Python, its tests, and repository scripts.
Read shared guidance and every topic applicable to the change.

| Topic | Description | Applies to |
| --- | --- | --- |
| [Shared](shared.md) | Cross-cutting expectations | Code under `src/`, `tests/`, and `scripts/` |
| [Python](python.md) | Python conventions | All `*.py` files in that scope |
| [Tests](tests.md) | Test expectations | Tests under `tests/` |

“Must” and “must not” are requirements within their stated scope. “Should” and
“should not” are recommendations allowing a reasoned exception. Reviewers must
distinguish these and consider the reason for an exception.

Precedence: agreed local rules, existing tool configuration for mechanical
matters, then any explicitly adopted external baseline.
```

## Topic files and rule identity

Give each topic a descriptive title. Each short rule has a repository-unique
ID and descriptive level-two heading, preceded by an explicit lowercase ID
anchor. Use obligation words consistently and keep applicability qualifications
beside the rule. Add rationale, bad/good examples, or source links only when they
help interpretation; these are optional, not required fields.

````markdown
# Testing standards

<a id="test-001"></a>
## TEST-001: Test names describe behavior

Test names should describe the behavior and expected outcome they demonstrate.

This helps readers understand a failure without reading the entire test.

```python
# Bad: does not explain what the test demonstrates.
def test_login_2(): ...

# Good: identifies the input condition and expected outcome.
def test_login_rejects_expired_password(): ...
```
````

This illustrates format, not an automatically adopted testing rule. The index
links to `tests.md`; a finding can cite `TEST-001` and `tests.md#test-001`.

Preserve valid IDs for retained rules when moving, reordering, or renaming them.
IDs identify rules even when files move. Assign distinct IDs to new rules; do not
renumber to close gaps or reuse retired IDs. When retiring IDs, keep a brief
index note to prevent reuse, for example `Retired IDs: TEST-003 (removed).`

## Baselines and tools

Write agreed local expectations in topic files. To adopt an external baseline,
give the adoption rule a local ID and identify the selected guide, applicable
scope, edition or dated reference, and local exceptions. Summarize its coverage
for approval instead of copying the entire guide. Findings can cite the local
adoption ID plus the upstream section. Ordinary source citations establish
provenance; they do not adopt unselected upstream rules.

For existing mechanical enforcement, link actual configuration and commands from
the applicable topic instead of transcribing settings into prose rules. State
what the tools actually check; do not claim they enforce judgment-based guidance.
Written guidance supplies judgment, useful rationale, and agreed exceptions.

A deliberate local change conflicting with configuration needs a persistent note
beside the affected rule: describe the mismatch, required tooling follow-up, and
the agreed effective timing (now or after that follow-up). If deferred, make the
current expectation clear. Do not leave contradictory instructions active. This
is distinct from a baseline's mechanical mismatch already resolved by index
precedence.
