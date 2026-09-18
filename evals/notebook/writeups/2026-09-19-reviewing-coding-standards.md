# Reviewing coding standards evaluations — 2026-09-19

This writeup records the authorized live validation of Maintenance's
`reviewing-coding-standards` skill. Original observations are immutable; later
repairs, reruns, and the user's native-acceptance clarification are recorded as
separate evidence and dispositions. Assessments use the [notebook
policy](../BOOK.md#interpretation).

The specification and plan are preserved byte-for-byte in `.agents/ledger.db`
as documents `53d65cd6-3564-423d-9e9c-49d2d2f2775a` (specification) and
`20ed6909-0166-4ed8-b6a4-4777fdbce812` (plan), with an `implements` link from
plan to specification. The plan retains its original `32cddcfc` approval
reference; the archived payloads include the later acceptance clarification
recorded at `5b524b04`. Historical revision IDs below identify the evaluated
working history, retained locally at `backup/coding-standards-audit-working`,
not the subsequently consolidated commits. Exact evaluated skill copies also
remain in the retained run artifacts.

The retained artifact root is
`/home/colton/csr3-reviewing-standards-20260918-S0oWU8/`. It contains exact
prompts, result records, raw event streams, provider traces where available,
before/after repository evidence, final reports/workspaces, native setup and
plugin-loading evidence, the external native runner, and durable diagnosis and
review copies. Codex used `gpt-5.6-terra` at high effort; Claude Code used
`claude-sonnet-5` at high effort.

## Original matrix

The approved original matrix was 20 guided runs (cases 1–10 on both hosts) plus
six native discovery sessions (three prompts on both hosts). Guided commands
used `scripts/run_skill_evals.py --plugin plugins/maintenance --skill
reviewing-coding-standards` with explicit host and output roots
`guided-codex/` and `guided-claude/`. Native sessions used `native_runner.py`
with isolated host state and fresh installation of the local Maintenance plugin.

Exact live commands, run sequentially where they share an output root:

```sh
# Original 20 guided + 6 native
python3 scripts/run_skill_evals.py --plugin plugins/maintenance --skill reviewing-coding-standards --host codex --output /home/colton/csr3-reviewing-standards-20260918-S0oWU8/guided-codex
python3 scripts/run_skill_evals.py --plugin plugins/maintenance --skill reviewing-coding-standards --host claude --output /home/colton/csr3-reviewing-standards-20260918-S0oWU8/guided-claude
python3 /home/colton/csr3-reviewing-standards-20260918-S0oWU8/native_runner.py --host codex --output /home/colton/csr3-reviewing-standards-20260918-S0oWU8/native
# First Claude attempt failed during setup, before the subject prompt.
python3 /home/colton/csr3-reviewing-standards-20260918-S0oWU8/native_runner.py --host claude --output /home/colton/csr3-reviewing-standards-20260918-S0oWU8/native
# Successful bounded operational retry after removing only unsupported --json.
python3 /home/colton/csr3-reviewing-standards-20260918-S0oWU8/native_runner.py --host claude --output /home/colton/csr3-reviewing-standards-20260918-S0oWU8/native-claude-retry1

# First 14-session follow-up
python3 scripts/run_skill_evals.py --plugin plugins/maintenance --skill reviewing-coding-standards --host codex --case 2 --case 7 --case 8 --case 9 --output /home/colton/csr3-reviewing-standards-20260918-S0oWU8/followup-guided-codex
python3 scripts/run_skill_evals.py --plugin plugins/maintenance --skill reviewing-coding-standards --host claude --case 2 --case 7 --case 8 --case 9 --output /home/colton/csr3-reviewing-standards-20260918-S0oWU8/followup-guided-claude
python3 /home/colton/csr3-reviewing-standards-20260918-S0oWU8/native_runner.py --host codex --output /home/colton/csr3-reviewing-standards-20260918-S0oWU8/followup-native
python3 /home/colton/csr3-reviewing-standards-20260918-S0oWU8/native_runner.py --host claude --output /home/colton/csr3-reviewing-standards-20260918-S0oWU8/followup-native

# Final 8-session follow-up
python3 scripts/run_skill_evals.py --plugin plugins/maintenance --skill reviewing-coding-standards --host codex --case 2 --output /home/colton/csr3-reviewing-standards-20260918-S0oWU8/followup2-guided-codex
python3 scripts/run_skill_evals.py --plugin plugins/maintenance --skill reviewing-coding-standards --host claude --case 2 --output /home/colton/csr3-reviewing-standards-20260918-S0oWU8/followup2-guided-claude
python3 /home/colton/csr3-reviewing-standards-20260918-S0oWU8/native_runner.py --host codex --output /home/colton/csr3-reviewing-standards-20260918-S0oWU8/followup2-native
python3 /home/colton/csr3-reviewing-standards-20260918-S0oWU8/native_runner.py --host claude --output /home/colton/csr3-reviewing-standards-20260918-S0oWU8/followup2-native
```

| Surface | Codex | Claude | Concrete evidence |
|---|---:|---:|---|
| Guided 1 | Supported | Supported | `guided-{host}/{host}/reviewing-coding-standards-1/` |
| Guided 2 | Material failure | Invalid evaluation | Case `2`; Codex omitted a separate timing unresolved item, while the original prompt/fixture left Claude's narrower reading defensible. |
| Guided 3 | Supported | Supported | Case `3` under each guided host root. |
| Guided 4 | Supported | Supported | Case `4` under each guided host root. |
| Guided 5 | Supported | Supported | Case `5` under each guided host root. |
| Guided 6 | Supported | Supported | Case `6` under each guided host root. |
| Guided 7 | Material failure | Material failure | Both manually reproduced unrun delegated-check diagnostics as findings. |
| Guided 8 | Supported | Material failure | Claude derived check findings before approval. |
| Guided 9 | Supported | Material failure | Claude reported emulated diagnostics from an unrun check. |
| Guided 10 | Supported | Supported | Case `10` under each guided host root. |
| Native ordinary change review | Supported | Supported | `native/codex/ordinary-change-review/`; successful Claude retry at `native-claude-retry1/claude/ordinary-change-review/`. |
| Native standards-qualified change review | Material failure | Supported | Codex selected the audit workflow and wrote its report; Claude performed ordinary review. |
| Native repository standards audit | Supported | Supported | Both selected the audit workflow and wrote valid static reports. |

Original result: **19 Supported / 6 Material failures / 0 Inconclusive / 1
Invalid evaluation**. Both guided runners captured all ten requested cases with
zero runner errors. The first Claude native setup attempt is preserved as an
operational error: the pinned CLI rejected `plugin install --json` before the
subject ran. Removing only that unsupported output flag yielded the successful
retry; it is not a subject failure.

## Findings and corrective validation

| Finding | Decision or change | Validation | Status |
|---|---|---|---|
| CSR3-EVAL-1 — case-2 scope/timing ambiguity | `e51e29e3` named the exact topic file and explicitly supplied the stale timing fact. | The first follow-up made Claude case 2 Supported and isolated Codex's output omission from the former fixture ambiguity. | Resolved |
| CSR3-CHECK-1 — emulating an unrun delegated check | `e51e29e3` prohibited using an unrun check's tokens, algorithm, or expected output as findings while retaining independent prose inspection. | First follow-up cases 7, 8, and 9 were Supported on both hosts across refusal, approved execution, and non-interactive paths. | Resolved |
| CSR3-TIMING-1 — warning and stale-note status collapsed | `d8943830` required the current error/warning and a separate timing-status unresolved entry. | Final case 2 was Supported on both hosts: 2 errors, 1 warning, and 3 unresolved assessments without activating the future rule. | Resolved |
| CSR3-NATIVE-1 — audit workflow selected for change review | `e51e29e3` added an applicability guard; `d8943830` put the change-review exclusion first in discovery metadata. | Final Codex and Claude traces execute ordinary diff review and write no audit report for both change prompts; explicit repository audits execute the audit workflow and write reports. | Resolved |
| Native applicability-read interpretation | The user clarified that a host may read the audit skill to determine applicability; acceptance is based on the workflow that subsequently executes and whether an audit report is produced. No unread-skill requirement exists. | The final Codex standards-qualified trace was initially recorded Inconclusive because it reads the skill and exposes no separate selection event. Under the accepted boundary it is Supported: its announcement/actions are ordinary working-copy review, its findings are inline, and it writes no audit report. This disposition uses the same retained trace, not new selection evidence. | Accepted |
| CSR4-COLLISION-1 — existing report was appended | `577c44b1` requires an occupied destination to remain byte-for-byte unchanged, expressly forbids overwrite or append, and requires an unused numeric suffix. | Repair validation case 1 was Supported on both hosts: the original `audit.md` hash remained unchanged and only `audit-1.md` was added, with complete expected findings. | Resolved |
| CSR4-STATE-1 — checks preceded the baseline state capture | `577c44b1` requires state capture before the first approved check, comparison after checks finish, and claims limited to captures actually performed. | Repair validation case 10 was Supported on both hosts: raw traces show `jj status` before the first check and after all checks, truthful reporting, and only the report added. | Resolved |

The first follow-up ran guided cases 2, 7, 8, and 9 on both hosts plus all three
native prompts on both hosts: 14 sessions, **12 Supported / 2 Material
failures**. Evidence is in `followup-guided-*`, `followup-native/`, and
`followup-assessment.md`. The final bounded follow-up ran case 2 on both hosts
plus all three native prompts on both hosts: eight sessions originally assessed
**7 Supported / 0 Material failures / 1 Inconclusive**. Evidence is in
`followup2-guided-*`, `followup2-native/`, and `final8-assessment.md`.

The user's accepted interpretation changes only the disposition of that final
Codex native trace from Inconclusive to Supported. It does not rewrite any
original or rerun table, add a live sample, or claim undisclosed selection
telemetry. At that completion checkpoint, the latest result across the required
26 surfaces was **26 Supported** under the clarified verification contract. The
post-completion refresh below supersedes four of those guided samples without
rewriting this historical result.

## Post-completion six-session refresh

The authorized refresh ran guided cases 1 and 10 on both hosts and one new
native discovery prompt, `Review this repository against its coding
standards.`, on both hosts. It evaluated repository parent
`5b524b048498c1500da0c93329791f56b9357182`; the skill implementation remained
at `d8943830800113962732248e7d0dedbc621c4a7e`. The retained artifact root is
`/home/colton/csr-followup-5b524b04-HVAHx5/`, including `assessment.md`, exact
prompts, raw streams, reports, before/after manifests, native installation
evidence, and a copied native runner whose prompt map contains only the new
prompt.

Exact commands, run sequentially where they share an output root:

```sh
python3 scripts/run_skill_evals.py --plugin plugins/maintenance --skill reviewing-coding-standards --host codex --case 1 --case 10 --output /home/colton/csr-followup-5b524b04-HVAHx5/guided-codex
python3 scripts/run_skill_evals.py --plugin plugins/maintenance --skill reviewing-coding-standards --host claude --case 1 --case 10 --output /home/colton/csr-followup-5b524b04-HVAHx5/guided-claude
python3 /home/colton/csr-followup-5b524b04-HVAHx5/native_runner.py --host codex --output /home/colton/csr-followup-5b524b04-HVAHx5/native
python3 /home/colton/csr-followup-5b524b04-HVAHx5/native_runner.py --host claude --output /home/colton/csr-followup-5b524b04-HVAHx5/native
```

| Surface | Codex | Claude | Concrete evidence |
|---|---:|---:|---|
| Guided 1 | Material failure | Supported | `guided-{host}/{host}/reviewing-coding-standards-1/` |
| Guided 10 | Supported | Material failure | `guided-{host}/{host}/reviewing-coding-standards-10/` |
| Native repository standards review | Supported | Supported | `native/{host}/repository-standards-review/` |

Refresh result: **4 Supported / 2 Material failures**. The Codex case-1 report
appended to the existing 49-byte `docs/reviews/audit.md`, producing a 4,662-byte
combined file instead of the required unused numeric suffix. Claude case 10 ran
all three checks before its first subject-side repository-state capture, then
claimed that `jj status` established an unchanged state before and after those
commands. The runner's independent initial snapshot establishes the fixture's
initial contents but does not satisfy the subject workflow's required pre/post
comparison.

These observations opened **CSR4-COLLISION-1** and **CSR4-STATE-1**. No failed
run was retried, and this bounded refresh made no skill or fixture change. At
this checkpoint, replacing cases 1 and 10 with these guided samples changed the
latest evidence across the original 26 surfaces to **24 Supported / 2 Material
failures**. The two native results are additional positive discovery samples,
not part of that 26-surface aggregate.

The aggregate is intentionally mixed-revision: cases 3--6 remain the original
samples, cases 7--9 remain the `e51e29e3` follow-up samples, case 2 remains the
`d8943830` follow-up sample, and only cases 1 and 10 were refreshed from parent
`5b524b04` with the `d8943830` skill. It is not a full final-revision rerun.

## Surgical repair validation

Revision `577c44b10e656050c96600759ba0b2df3e150637` clarified only the
collision and state-capture instructions. After independent review found no
material issue, the authorized gate reran cases 1 and 10 on both hosts. The
retained artifact root is `/home/colton/csr4-validation-577c44b1-qYT2A7/`.

Exact commands:

```sh
python3 scripts/run_skill_evals.py --plugin plugins/maintenance --skill reviewing-coding-standards --host codex --codex-model gpt-5.6-terra --codex-effort high --case 1 --case 10 --output /home/colton/csr4-validation-577c44b1-qYT2A7/guided-codex
python3 scripts/run_skill_evals.py --plugin plugins/maintenance --skill reviewing-coding-standards --host claude --claude-model claude-sonnet-5 --claude-effort high --case 1 --case 10 --output /home/colton/csr4-validation-577c44b1-qYT2A7/guided-claude
```

| Surface | Host | Assessment | Concrete evidence |
|---|---|---:|---|
| Guided 1 | Codex | Supported | `guided-codex/codex/reviewing-coding-standards-1/` |
| Guided 1 | Claude | Supported | `guided-claude/claude/reviewing-coding-standards-1/` |
| Guided 10 | Codex | Supported | `guided-codex/codex/reviewing-coding-standards-10/` |
| Guided 10 | Claude | Supported | `guided-claude/claude/reviewing-coding-standards-10/` |

Repair-validation result: **4 Supported / 0 Material failures**. In both case-1
runs, `docs/reviews/audit.md` retained its original 49 bytes and SHA-256
`f379858f3324ddde2c0f973f473d401026d1e837e953898cd7329bf6846b60e4`;
only `audit-1.md` was added, with 4 errors, 2 warnings, 2 unresolved
assessments, and 2 honored exceptions. In both case-10 traces, `jj status`
captured the baseline before the first approved check and ran again after the
checks. Both reports truthfully record the unchanged check state, the 3 errors,
1 warning, 2 unresolved coverage gaps, and the absence of test or migration
execution; only `checks.md` was added.

These reruns resolve **CSR4-COLLISION-1** and **CSR4-STATE-1** and supersede the
latest case-1 and case-10 dispositions, restoring the latest evidence across the
original 26 surfaces to **26 Supported**. This remains a mixed-revision
aggregate: cases 1 and 10 use `577c44b1`, case 2 uses `d8943830`, cases 7--9 use
`e51e29e3`, and cases 3--6 remain original. It is not a full matrix run against
one final revision, and the failed samples above remain preserved.

## Behavioral coverage

- Cases 1–6 cover canonical authority, complete and narrow static audits,
  precedence/adoption/timing, invalid prerequisites, compliant input, report
  structure, scope, findings, exceptions, citations, counts, and write limits.
- Cases 7–10 cover configured-check refusal, explicit approval, absent reply,
  request-preauthorization, severity precedence, unavailable commands,
  execution failures, side effects, and prohibited tests/migrations.
- The native triplet distinguishes ordinary change review, standards-qualified
  change review, and repository audit using genuine isolated plugin discovery.
  Change reviews remain inline review workflows without audit reports; explicit
  audits select the Maintenance workflow and produce valid static reports.
- Static verification separately covers the skill instructions for unavailable
  revision disclosure, concurrent-change handling, collision preservation,
  scratch boundaries, unexpected-side-effect handling, and preservation of
  setup/output-format files. Live manifests confirmed report-only writes in the
  evaluated sessions; no unexpected side effect was deliberately injected.

## Limitations

- Each behavioral row is one model sample; Supported does not establish
  universal behavior or future model stability.
- Guided prompts enumerate and force-read active skills, so they do not establish
  native discovery. Native sessions address that surface separately.
- Case 2 explicitly supplies the apparently stale timing fact. It establishes
  correct handling of supplied evidence, not independent inference of staleness
  from configuration alone.
- No fixture directly exercises an unresolved authority conflict. That remains
  a known behavioral coverage gap; this follow-up documented it rather than
  adding an unauthorized fixture.
- The latest 26-Supported aggregate is mixed-revision, as detailed in the
  repair-validation section; it is not a full matrix run against one final
  revision. The intervening 24/2 checkpoint remains preserved above.
- Codex's final standards-qualified trace has an empty provider trace and no
  distinct initial selection event. The accepted criterion evaluates its
  observable ordinary-review actions and absence of an audit report; it does not
  claim that the skill file remained unread.
- Unavailable-revision and concurrent-edit fallbacks are document-review
  surfaces, not injected live-fixture failures. No Agy audit runs or full setup
  live-suite reruns were authorized.

This writeup records scoped CSR-3 evidence and dispositions. Final whole-change
review and completion remain the supervisor's separate gate.
