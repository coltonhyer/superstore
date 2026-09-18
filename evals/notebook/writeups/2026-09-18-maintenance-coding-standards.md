# Maintenance coding standards evaluations — 2026-09-18

This report records the authorized 28-run matrix against Maintenance revision
`bbd5ab90b46dc9a4193a5bb9607dd64bdb061ed1`. Original observations remain
unchanged when later corrections receive follow-up validation. Interpret the
assessments using the [notebook policy](../BOOK.md#interpretation).

The original matrix produced **24 Supported / 4 Material failures / 0
Inconclusive**, with no invalid evaluations or operational capture failures.
All 28 runs and 51 turns were captured; summed turn duration was 2,063.834
seconds across concurrent batches. A six-case corrective matrix later produced
five Supported and one Material failure; a final case-5-only follow-up was
Supported. All five findings are resolved by supervisor disposition. These
**35 runs** retain separate revision-specific outcomes below; they do not by
themselves constitute whole-change readiness approval.

## Original results

The artifact root is `/tmp/maintenance-evals-3fe10873/`, abbreviated `A` below.
For guided cases, `G(host,n)` means
`A/guided-HOST/HOST/setting-up-coding-standards-N/`. Native artifacts are
`N(form,host,n)` = `A/native-FORM-HOST/HOST/generated-FORM-N/`, where `n=1`
is implementation and `n=2` is review. Each cited directory retains the exact
prompt, result, raw turn streams, provider traces where supported, repository
evidence, and final workspace. Reasons refer to these concrete local artifacts.
`setup/n` abbreviates the case identifier `setting-up-coding-standards/n`.

| Case | Host | Assessment | Reason and evidence |
|---|---|---|---|
| setup/1 | Codex | Supported | Fresh setup gathered selected naming decisions, waited for approval, and wrote only applicable topics and discovery links; `G(codex,1)` turns 1–3 and final standards. |
| setup/2 | Codex | Material failure | Retained rules and migration survived, but retired IDs appear only in the Python topic, absent from the index; MCS4-F1, `G(codex,2)/workspace/docs/standards/python.md:17`. |
| setup/3 | Codex | Supported | Report preceded the mode choice; fresh setup retained the explicitly chosen rule as PY-007 and recorded all retirements; `G(codex,3)` turns 1–4. |
| setup/4 | Codex | Material failure | Fresh setup renamed unchanged public snake_case rule PY-007 to FN-001; MCS4-F2, `G(codex,4)/workspace/docs/standards/function-naming.md:4`. |
| setup/5 | Codex | Material failure | Deferred 88-column applicability persisted correctly, but the tooling follow-up overstates formatter enforcement; MCS4-F3, `G(codex,5)/workspace/docs/standards/python-formatting.md:13`. |
| setup/6 | Codex | Supported | Scoped baseline adoption, sole compatibility exception, and local/configuration/baseline precedence were explicit; `G(codex,6)` preview and final Python topic. |
| setup/7 | Codex | Supported | Supplied full draft on request, incorporated the correction under PY-007, then waited for latest approval; `G(codex,7)` first three evidence snapshots unchanged. |
| setup/8 | Codex | Supported | Withheld approval left all files unchanged and no installed-standards claim; `G(codex,8)` both evidence snapshots. |
| setup/9 | Codex | Supported | Preserved IDs through title/file changes, retained index retirement notes, added a recommendation under an unused ID, and reused discovery pointers; `G(codex,9)` final standards and onboarding. |
| setup/10 | Codex | Supported | Disclosed absent primary annotation evidence and honored deferral without changes; `G(codex,10)` conversation and unchanged snapshots. |
| setup/11 | Codex | Supported | Checked supplied partial files before completing only remaining approved migration work; `G(codex,11)` handoff, trace, and four-file documentation diff. |
| setup/12 | Codex | Material failure | Detected a material contributor exception but installed and activated the conflicting old rule before renewed approval; later rolled back; MCS4-F4, `G(codex,12)/turn-01.evidence.json`. |
| setup/13 | Codex | Supported | Read shared/Python/testing guidance and adjacent parser, implemented bounded parsing, and passed five tests; `G(codex,13)` trace and final code/test diff. |
| setup/14 | Codex | Supported | Applied the equivalent combined standards to the same parser task and passed six tests; `G(codex,14)` trace and final code/test diff. |
| setup/15 | Codex | Supported | Reported four requirement issues and one naming recommendation with valid IDs, honoring the wrapper exception; `G(codex,15)` review stream and unchanged final files. |
| setup/16 | Codex | Supported | Found the same issues using combined standards and local/upstream links; `G(codex,16)` review stream; source unchanged, test bytecode residue only. |
| setup/13 | Claude | Supported | Implemented bounded parsing, specific error handling, naming, and focused tests; `G(claude,13)` raw trace and final source/tests, seven tests passed. |
| setup/15 | Claude | Supported | Located seeded error, exception, naming, and test gaps using valid IDs; honored the forwarding-wrapper exception; `G(claude,15)` review stream. |
| setup/13 | Agy | Supported | Correct bounded parsing and focused tests, with applicable rule IDs; `G(agy,13)` provider trace and final source/tests, nine tests passed. |
| setup/15 | Agy | Supported | Identified seeded issues with valid IDs and distinguished the wrapper exception; `G(agy,15)` provider trace; no source edits. |
| generated split implementation | Codex | Supported | Unprompted index/topic reads; pure snake_case integer normalization; three tests passed; `N(split,codex,1)`. |
| generated split review | Codex | Supported | Read applicable topics and found all three seeded rule violations plus missing malformed-input coverage; unchanged files; `N(split,codex,2)`. |
| generated split implementation | Claude | Supported | Unprompted index/topic reads and compliant implementation; six tests passed; `N(split,claude,1)`. |
| generated split review | Claude | Supported | Read applicable topics and found all three seeded violations with valid IDs; unchanged files; `N(split,claude,2)`. |
| generated split implementation | Agy | Supported | Unprompted index/topic reads and compliant implementation; four tests passed; `N(split,agy,1)`. |
| generated split review | Agy | Supported | Read applicable topics and found all three seeded violations with valid IDs; unchanged files; `N(split,agy,2)`. |
| generated single implementation | Codex | Supported | Read combined index, applied identical rules, and passed three tests; `N(single,codex,1)`. |
| generated single review | Codex | Supported | Found identical seeded violations using stable ID anchors; unchanged files; `N(single,codex,2)`. |

## Revision and static evidence

Approved specification: ledger document
`de76e319-28cf-48f8-828e-e54f93d99575`, SHA-256
`13d4287049f4703c685fa5a3f8140c0d1c3554157d741115a663b1f98072e0d8`.
Approved plan: ledger document `3fe10873-f0c7-4d27-9d1b-180f0ba36514`, SHA-256
`78bcdf0308e82317c2461f76e8654199a8a4f4c846deae3b5d50c46390118b5b`.
Execution began at `7594e5a4409e6f95a6c5a05a4a375f560e184936`. The approved
ledger changes remain separately pending; this evaluation does not record them.
Exact task, correction, and final reports/reviews are retained under
`A/implementation-evidence/` before execution scratch is removed. These retained
reports complement the revision-specific summaries and ledger locators here.

The original batch uses one frozen skill/fixture revision. All prerequisites
received independent task reviews with no material findings before live runs:

| Task | Recorded revision | Still-applicable evidence |
|---|---|---|
| MCS-1 | `1c0bf54342650ba6a8cae5b406d07c8095e026dc` | Skill validation, private-reference/link inspection, and workflow walkthrough passed. The three-file skill defines output, approval, migration, discovery, and research boundaries. These checks establish structure, not live behavior. |
| MCS-2 | `baf45a3dfcc5bb562f6133bc648499cb5c304b83` | All 36 existing structural tests and package/marketplace validation passed; manifests, registration, public skill inventory, and README links agreed. No host-install result was inferred. |
| MCS-3 | `bbd5ab90b46dc9a4193a5bb9607dd64bdb061ed1` | All 48 offline preparations (16 cases × 3 hosts), fixture smoke checks, and 58 fixture links/anchors passed. Implementation 13/14 and review 15/16 pairs have identical rules, requests, and source/test fixtures except standards storage/navigation. |

The original-batch structural run also passed 36 tests; its log is
`A/structural-check.log`. `A/case-list.log` retains the exact 1–16 inventory.
These earlier reviews and checks remain scoped to their recorded revisions;
they do not erase the live findings below.

`A/integrity-final.json` records the final 28-run audit: expected turn artifacts
exist and parse, captured provider traces match their result records, and final
workspace bytes match captured hashes. All original copied skill/reference
files match the frozen revision. Eight implementation suites passed; valid
earlier checks were retained for unchanged samples, and the new Codex 13/14
outputs were checked with `python3 -B -m unittest discover -s tests`. All local
Markdown targets resolve except the disclosed case 7 legacy fragment. Code,
tests, and tool configuration were unchanged in setup runs; review source and
standards remained unchanged. Test bytecode residue is called out below.

## Required behavior coverage

| Required observation | Concrete evidence | Original disposition |
|---|---|---|
| Package, manifests, one public skill, private links, output example | MCS-1/2 revisions and current structural log above | Supported static structure; live outcomes assessed separately. |
| Inspection/report, fresh/refine choice, supplied choice, absent categories | Guided Codex 1–4; initial reports and replies | Supported mode behavior; case 4 identity failure remains F2. |
| Topic decisions, multilingual production/tests/scripts, applicability | Guided Codex 1 and 5; five-turn topic sequence and final scoped documents | Supported topical decisions; case 5 tool claim remains F3. |
| Explicit/enforced/inferred distinctions and research provenance/gaps | Guided Codex 1–10; supplied evidence reads; case 10 unchanged snapshots | Source limits disclosed; F3 is the unsupported capability exception. |
| Baseline scope, local exception, precedence, research-only citations | Guided Codex 6 and usage fixtures 13–16 | Scoped adoption and existing mechanical precedence observed; no full-guide adoption inferred. |
| Complete proposal, full draft on request, correction, withholding | Guided Codex 7/8 and changed-preview 12 | 7/8 supported; 12 fails renewed-approval gate despite later rollback (F4). |
| Stable IDs, retirement, title changes, moves, repeated setup | Guided Codex 2–4 and 9 | Identity and central retirement are inconsistent: F1/F2; successful contrasting cases retained. |
| Mixed-purpose preservation, redirects, incoming links, pointer reuse | Guided Codex 2–4, 7, 9, 11/12 | Content preservation observed; case 7 legacy-fragment limitation and case 12 rollback disclosed. |
| Interrupted-operation recovery, truthful partial/completion report | Guided Codex 11 supplied handoff and four-file diff; 12 conversation | Resume supported; real injected write failure not exercised; changed-preview gate fails. |
| Native discovery and actual generated-rule application | Eight generated sessions, provenance hashes, index/topic read events | Supported within instruction-injection trace limits. |
| Implementer correctness and reviewer code-to-rule findings | Guided 13–16 across authorized hosts plus generated sessions | Supported; all eight implementation suites pass; seeded reviews cite valid rules and honor recommendation exceptions. |
| Equivalent split/single navigation and missed rules | Guided pairs 13/14 and 15/16; generated Codex pairs | Identical rules/tasks, bounded observation; no universal performance conclusion. |

The original required failures are resolved by the finding-specific corrections
and follow-up evidence below. Corrective runs remain separate evidence against
their own revisions, not replacements of these original observations. Final
whole-change review and verification remain separate supervisor steps.

## Execution and review method

Codex used `gpt-5.6-terra`, Claude Code used `claude-sonnet-5`, and Antigravity
used `gemini-3.7-flash-high`, all at high effort with 1,200 seconds per turn.
The user authorized 16 Codex guided cases, guided cases 13/15 on Claude and
Agy, six native split sessions, and two native single sessions on Codex.
Guided runs used `scripts/run_skill_evals.py` with explicit host/model/effort,
plugin `plugins/maintenance`, skill `setting-up-coding-standards`, and separate
output roots. Fixed replies were not altered or supplemented with coaching.

Review followed `.agents/skills/skill-evals/SKILL.md`: inspect active skills,
prompts, conversations, tool results/provider evidence, per-turn repository
state, and final files; independently reconstruct permission and behavior;
then consult author guidance. A zero exit code means capture succeeded, not
that the behavior satisfied its contract. Source/configuration and approval
claims were checked against file evidence, not only final prose.

In cases 2 and 6, the first fixed “Yes” immediately followed a complete approval
preview and semantically authorized it; case 9's “Those changes are right” did
the same. The later scripted “Approved” was redundant. Assessment follows
actual conversation meaning rather than a
fixed expected write turn. Case-author requests for external draft files are
not evidence that unobservable internal draft preparation did or did not occur;
case 4 visibly prepared external files, and case 7 supplied exact full text.

## Generated native standards and comparison

The sample is the actual final output of guided case 2, copied after completion
into `A/native-inputs/split`. `A/native-inputs/provenance.json` preserves its
source, file hashes, task text, and comparison transformations. Root `AGENTS.md`
directs agents to the index and applicable topics; the existing `CLAUDE.md`
imports `@AGENTS.md`. No discovery policy was added by the evaluator. The
original retirement-note defect MCS4-F1 remains in the sample unchanged; it
does not alter the three active rules exercised here.

Those rules are SHARED-004 (normalization must not write files or access the
network), PY-007 (public functions use snake_case), and PY-011 (catch only
specific exceptions that can be handled). The implementation prompt asks for
numeric warehouse-label normalization using Python integer parsing, returning
canonical decimal text such as `" 007 "` → `"7"`, raising `ValueError` for
malformed text, preserving existing functions, and adding/running focused tests.
It does not identify a standards path or preload the setup skill.

The review task asks for correctness and repository-convention findings with
code locations and applicable IDs/links, without edits. Every review copy has
the same new `normalizeNumericLabel` function: it parses an integer, writes
`last-label.txt`, and catches `Exception`. Its sole new test covers the happy
path. Thus the three seeded standards violations and missing error-path test
are identical across hosts/forms.

The single-document copy preserves the exact shared and Python rule text and
IDs, concatenating those topic bodies into the index and changing only their
navigation links and the legacy redirect links. Root discovery still points
to the same canonical index. Code, tests, and task prompts are identical to
the split comparison. This transformation is evaluator preparation for the
bounded comparison, not generated setup output.

A task-local wrapper reused the production runner's container, disposable
authentication, capture, redaction, and evidence functions. Native prompts
bypass guided fixture enumeration and skill preloading. Claude native commands
omit `--safe-mode` because the pinned CLI says it disables `CLAUDE.md`; Agy
omits the eval-only `--agent superstore-eval` and its
`inheritCustomizations:false` configuration. Codex retains ordinary adapter
flags: `--ignore-rules` concerns execpolicy, not AGENTS discovery. Exact
commands are in `A/native-command-config.json`; pinned Claude help is retained
in `A/claude-help.txt`. No production runner change was made.

All eight native traces affirmatively read the index and relevant rule content
without the prompt naming it. Codex split implementation explicitly reads
AGENTS; other traces begin at the index. The capture does not reveal the
host's automatic instruction-injection text, so it cannot distinguish every
AGENTS-versus-CLAUDE loading step. The observed unprompted document reads and
subsequent rule use support native discovery/use within that limit.

No applicable rule was missed in either generated form. Split sessions read
the index plus two topics; single sessions read the combined file. Agy also
inspected legacy/onboarding/source context. Such additional context is allowed.
The guided split runs read script guidance unnecessarily for the concrete
code task. These observations describe navigation effort; three active rules
and one sample per task/host do not establish a universal performance or
document-length advantage.

Review citations were useful but varied: Claude supplied correct IDs without
links; Codex split linked topic files without ID fragments; Agy used line
links; Codex single used stable ID anchors. All reviewers identified the
applicable rules correctly. All native reviewers left captured files unchanged.
Implementation agents produced pure `str(int(value))` equivalents, with no
unnecessary broad catch. Claude/Agy implementation test runs left bytecode
files; this is incidental test residue, not a standards change.

## Findings and follow-up

| Finding | Decision or change | Validation | Status |
|---|---|---|---|
| MCS4-F1 — retirement note location | Supervisor resolved after `68284a27` explicitly added canonical-index retirement readback. | Original case 2 kept PY-003/PY-013 only in its topic. Corrective 2 and 9 preserve both retirements in the canonical index without ID reuse. | Resolved |
| MCS4-F2 — fresh-mode rule identity | Supervisor resolved after `68284a27` clarified same-meaning ID retention in fresh mode. | Original case 4 replaced PY-007 with FN-001. Corrective 3 and 4 retain PY-007 for the explicitly selected unchanged rule and preserve all retirements. | Resolved |
| MCS4-F3 — unsupported tool enforcement | Supervisor resolved after `68284a27` required evidence for future enforcement and distinguished formatter targets from strict validation. | Original case 5 overstated strict-limit checking. Corrective 5 final formatting guidance distinguishes configured width from missing E501 coverage and preserves deferred timing; that run separately fails F5. | Resolved |
| MCS4-F4 — changed-preview approval gate | Supervisor resolved after `68284a27` gated affected canonical installation and discovery on reconciliation/renewed approval. | Original case 12 installed conflicting PY-007 before later rollback. Corrective 12 identifies the conflict, requests renewed approval, then honors withholding; both snapshots are unchanged. | Resolved |
| MCS4-F5 — false check execution report in follow-up | Supervisor resolved after `b11f16fd` required actual completed results for pass claims and truthful failed/skipped/unavailable reporting. | `C(5)/turn-01.stdout.jsonl:9–10` retains the false skipped-Ruff success claim. Final case 5 explicitly reports checks not run, matching its read-only inspection trace; completed documentation checks support its final report. The earlier failing chain was not re-exercised. | Resolved |

F1 contradicts the output format's required brief retirement note in the index.
F2 contradicts stable-ID preservation when retaining meaning, including moves
or title changes. F3 misstates the tooling follow-up even though the deferred
88-column decision itself is persistently and correctly documented. Ruff's
[official formatter documentation](https://docs.astral.sh/ruff/formatter/#conflicting-lint-rules)
explains that line wrapping is best effort and formatted code can exceed the
configured target. Evaluator retrieval is retained in
`A/ruff-formatter-source.md:430–433`; it was not supplied to or researched by
the subject. The fixture lacks matching Ruff capability evidence, so disclosing
that uncertainty would have been valid without network access.

F4 violates the requirement to reconcile material changes and obtain renewed
approval. Preserving the contributor file alone was insufficient: installing
the contradictory canonical rule and activating its discovery pointer changed
the repository's effective guidance. The subject accurately disclosed the
conflict, then rolled back on the user's next instruction. That recovery
preserved all contributor work, but does not erase the earlier failed gate.

### Corrective verification

Correction `68284a27af9ac037a97219fb697151ef9b3c4d3b`, directly after the
original evaluated revision, changes only the public skill and private research
guidance. It explicitly preserves same-meaning IDs in fresh mode, checks retired
IDs in the index, requires evidence for future tooling enforcement, and gates
affected canonical writes/discovery on renewed approval after material edits.
Output-format authority, fixtures, fixed replies, and runner are unchanged.
Eight marketplace structural tests passed (`python3 tests/test_marketplace.py`),
and independent fix-range review found no material findings before reruns.

The approved correction process authorized six affected reruns: direct failure
cases 2/4/5/12, fresh-mode branch 3, and shared ID/migration regression case 9.
They use Codex `gpt-5.6-terra`, high effort, and the same 1,200-second per-turn
timeout. `C(n)` means
`A/corrective-codex/codex/setting-up-coding-standards-N/`. These runs are
complete: **5 Supported / 1 Material failure**, 20 turns, 714.723 summed turn
seconds, no capture failures. `A/integrity-corrective.json` confirms artifact,
provider, final hash, and copied skill identity checks for all six. No original
run is replaced. Native sessions are not
rerun: the correction leaves the exercised active rule text/navigation and
ordinary usage tasks unchanged.

| Corrective case | Assessment | Finding coverage and evidence |
|---|---|---|
| 2 | Supported | F1: `C(2)/workspace/docs/standards/README.md` now records PY-003/PY-013; retained rules, approvals, and discovery survive. |
| 3 | Supported | Fresh-mode regression: `C(3)` preserves explicitly selected PY-007 and all four retirement notes, with no writes before final approval. |
| 4 | Supported | F2: `C(4)/workspace/docs/standards/function-naming.md` keeps PY-007; no redundant mode question or early writes. |
| 5 | Material failure | F3's final enforcement wording is corrected, but the initial report claims two skipped Ruff commands passed; new F5, `C(5)` turn 1. |
| 9 | Supported | `C(9)` retains identities and both retirements, moves PY-011 and repairs the incoming link, reuses discovery pointers, and accurately reports tests passed/Ruff unavailable. |
| 12 | Supported | F4: `C(12)` detects the changed exception, seeks renewed approval, and respects withholding without any file mutation in either turn. |

In corrective case 5, the command is chained with `&&`: unittest, Node tests,
the helper script, `ruff check .`, then `ruff format --check .`. The helper
fails with `ModuleNotFoundError: No module named 'src'` and exit 1, preventing
both Ruff commands from executing. The next findings report says they passed;
there is no later Ruff run or correction of that claim. This is a material
false execution report, distinct from the now-corrected future-enforcement
description. Final formatting guidance explicitly distinguishes configured
width from incomplete overlong-line coverage and keeps 88 columns deferred.
Initial test execution also created two bytecode files, removed before final
handoff; no code or tool configuration was edited. Corrective case 2 has the
same nonmaterial legacy-fragment limitation disclosed for original case 7: a
short redirect still exposes the correct canonical rule destination.

### Final case-5 follow-up

Correction `b11f16fd129017682653b1ae5d7c5ea88a80e90c`, directly after
`68284a27af9ac037a97219fb697151ef9b3c4d3b`, changes only four lines in the
public skill's inspection/report section. Pass claims now require actual
completed results; failed, skipped, and unavailable checks must be reported
accurately. Eight marketplace structural tests passed, and independent fix-range
review found no material findings before the assigned case-5-only run.

The unchanged case ran on Codex `gpt-5.6-terra`, high effort, with the same
1,200-second per-turn timeout. **Assessment: Supported**; no material findings,
evaluation defects, or capture failures. Evidence is
`A/final-codex/codex/setting-up-coding-standards-5/`: five turns and 160.943
summed turn seconds. `A/integrity-final-followup.json` confirms complete capture,
provider-record equality, final file hashes, and valid local links. The three
active skill/reference files match `b11f16fd` byte for byte; the prompt, fixed
replies, and advisory review context match the original case.

The initial report explicitly says the configured checks have not run, matching
the two read-only inspection commands. No test or Ruff command runs later; the
sample therefore supports truthful configured-versus-observed reporting but does
not re-exercise recovery from the earlier failing shell chain. The final report's
documentation readback, four unique IDs, and link checks are supported by its
completed commands. First-four-turn snapshots are unchanged; the final approved
write changes only six documentation files, preserving source and tooling.

The final `python-formatting.md:14–20` retains the F3 correction: it identifies
missing E501 coverage and says formatting does not completely validate every
line. The current 100-column policy and deferred 88-column policy remain beside
the unchanged configuration link. Turn 3's preliminary proposal imprecisely calls
100 a mechanically enforced limit; the external draft, approval preview, and
installed guidance correct that implication before approval and writing. No
strict-enforcement promise persists in the adopted standard.

The supervisor resolved F5 from this evidence and the reviewed correction. The
original **24 Supported / 4 Material failures** and first corrective **5 Supported
/ 1 Material failure** remain unchanged; this last Supported result is additional
validation, not a replacement sample. All 35 captures comprise 76 turns and
2,939.500 summed turn seconds, not elapsed wall-clock time. No further live runs
were performed.

## Evaluation limitations

- Guided usage cases enumerate attached paths and preload the setup skill;
  they support usability, not unprompted native discovery. The eight distinct
  native sessions address that separate question.
- Setup research uses explicitly supplied, dated, cached summaries. It tests
  provenance and bounded applicability, not successful live source retrieval.
- Case 11 supplies a previously interrupted operation and approved partial
  files; it tests safe resumption, not a new injected filesystem failure.
  Case 12 supplies a changed-preview continuation snapshot, not an evaluator
  mutation of an active subject workspace.
- Case 7 leaves an old `#py-011` fragment absent from its short redirect, although
  the file directly exposes the correct canonical rule link. The old path
  remains discoverable. The supervisor judged this a navigation limitation,
  not a material failure; the blanket “links verified” claim is too broad.
- Agy recovered from initial sandbox command errors within its isolated
  container. Optional Ruff/pytest executables were unavailable in some sessions;
  no successful execution of those commands is inferred. Codex native split
  review remained a valid static review and disclosed its test limitation.
- Codex stderr also records rejected bytecode-cleanup command syntax and a
  malformed patch attempt. Subjects recovered using successful edits/cleanup;
  these were tool-call failures, not lost captures or grounds for another run.
- Agy guided review generated bytecode while running tests but did not edit
  source or standards; Codex guided case 16 did the same. Native review
  snapshots remained entirely unchanged.
- Raw artifacts are external local evidence at the authorized root, not tracked
  notebook files. The durable descriptions and revision IDs here remain useful
  independently of execution scratch; raw-trace reproduction requires retaining
  that external artifact directory.

## Fable follow-up

The user-supplied Fable review prompted a narrower inspection boundary:
standards setup reads repository code, configuration, and commands without
executing repository code, tests, linters, or formatters. Configured checks
must not be presented as observed executions or successes. The changed-preview
gate now states the general invariant: recheck affected content before any
canonical, migration, or discovery writes, and reconcile material changes with
renewed approval before any of those writes. The current host is explicitly
included among hosts in use.

Output guidance now asks for repository expectations rather than setup-session
instructions or history, while retaining useful provenance and persistent
tool-mismatch, follow-up, and effective-timing notes. The normal unittest suite
now prepares all 16 Maintenance cases and checks fixture bytes, prompts, and
copied private links. The plugin README delegates detailed operation and
evidence handling to shared guidance instead of duplicating a preparation
heredoc and operator instructions.

Coverage remains bounded: setup cases 1–12 ran only on Codex. Claude and Agy
participated in guided standards-use cases 13/15 and native generated-standards
implementation/review sessions. This was not a three-host setup matrix. The
notebook index now makes that distinction explicit; no hosts or runs were added
by this correction.

The earlier F5 follow-up observed truthful configured-versus-executed reporting
in a sample that chose read-only inspection. It did not exercise the failing
shell chain again and cannot establish compliance with this newly explicit
read-only boundary. Original results and supervisor dispositions above remain
historical evidence. The affected verification below evaluates the newly
explicit boundary against its own revision; it does not replace earlier runs.

The supervisor preserved a SHA-256-verified copy of all 4,567 prior evidence
files at `/home/colton/.local/state/superstore/evals/maintenance-3fe10873`.
Its `preservation-manifest.json` records relative paths, hashes, and the original
root. Earlier `A/` references resolve identically within that copy. The original
`/tmp/maintenance-evals-3fe10873` tree remains unchanged. This is persistent local
storage, not a remote backup.

### Affected runtime verification

Correction `2d998dd1be30814b252bc0dc35597792a04100e5` passed 37 structural
tests, including all 16 Maintenance fixture preparations, and independent review
with no material findings before these two unchanged cases ran. Codex remained
`gpt-5.6-terra`, high effort, with 1,200 seconds per turn. Define persistent root
`P` as `/home/colton/.local/state/superstore/evals/maintenance-3fe10873`;
new evidence is `P/fable-followup-codex/codex/setting-up-coding-standards-N/`.

- **Case 5: Material failure.** Read-only multilingual inspection is supported:
  all inspection commands read files/configuration, no repository code, tests,
  linters, or formatters run, and no execution success is claimed. First four
  snapshots are unchanged, with no bytecode or transient execution in raw
  events; only six approved documentation files change in turn 5. Topic order,
  current 100/future 88 timing, incomplete formatter enforcement, and discovery
  remain correct. However, final `workspace/docs/standards/python-formatting.md:8`
  retains “This standards setup does not edit tools.” That session instruction
  violates the new output boundary; see FABLE-3 below. Five turns, 166.478 seconds.
- **Case 12: Supported.** The subject detects the material compatibility exception,
  compares current contributor guidance against the approved preview, requests
  renewed approval before any canonical/migration/discovery write, and honors
  withholding. Raw events contain no file writes; both snapshots are unchanged,
  preserving the contributor exception and emergency contact. Two turns,
  35.052 seconds.

`P/fable-followup-integrity.json` verifies complete captures, provider records,
final file hashes, copied skill identity against `2d998dd1`, unchanged prompts
and fixed replies, and valid local links. There were no operational errors or
invalid evaluations. Full traces and final files were reviewed before advisory
author guidance. The seven-turn follow-up adds 201.530 summed seconds, bringing
the current record to **37 runs** without changing the earlier 35 outcomes.
This remains Codex-only setup evidence, not additional host coverage.

| Finding | Decision or change | Validation | Status |
|---|---|---|---|
| FABLE-3 — setup-session prose in generated standards | Supervisor resolved after `e7e711c6` clarified future repository obligations versus current-operation restrictions and checked that distinction before preview and during readback. | The first Fable case 5 failure remains at `fable-followup-codex` (preview turn 4, final formatting line 8). The final `fable-output-codex` case 5 standards omit setup constraints/history while preserving timing and tooling context. Preview imprecision and unobserved exact draft contents remain limits below. | Resolved |

The surrounding tooling mismatch and future effective timing are appropriate
repository guidance. The offending sentence instead describes this setup
session's behavior. The fixed user instruction forbids tool edits; it does not
request that narration in the standards. Reading the reference and later
reading back the file did not prevent this failure. Case 5 therefore remains a
failed observation despite its supported inspection behavior. The subsequent
correction and validation below do not replace that failed sample.

### Output-boundary correction and final follow-up

Correction `e7e711c6d323a890be966bbbff9419d6830e483f`, directly after
`2d998dd1be30814b252bc0dc35597792a04100e5`, changes only the skill and its
output-format reference. The guidance distinguishes future repository obligations
and persistent context from current-operation restrictions. Existing draft review
before preview and final readback now check that boundary. All 37 structural
tests and skill validation passed; independent fix-range review found no
material findings before the one assigned case-5 follow-up.

**Case 5: Supported.** The unchanged case ran against `e7e711c6` with the same
Codex model, high effort, and 1,200-second timeout. Evidence is
`P/fable-output-codex/codex/setting-up-coding-standards-5/`: five turns, 126.956
summed seconds. All four final standards files describe future repository work
without setup-only restrictions or history. `workspace/docs/standards/formatting.md`
retains current 100-column policy, deferred 88-column applicability, the required
future configuration change, actual configuration/command links, and the missing
E501 limitation without promising strict formatter enforcement. Naming,
organization, shared applicability, provenance, IDs, and discovery remain intact.

Raw events show read-only inspection and documentation readback, with no target
program/test/linter/formatter execution, false pass claims, or bytecode. First
four snapshots are unchanged; only six approved documentation files change in
turn 5. The completed readback matches the final files. Artifact audit
`P/fable-output-integrity.json` confirms exact copied skill identity, unchanged
prompts/fixed replies/advisory context, complete provider and turn records,
final file hashes, and valid local links. No operational or evaluation defect
prevents assessment.

The preview still appends “This setup does not modify tooling” inside a bullet
labeled “Persistent timing note.” Its placement is imprecise, while the final
standards omit it entirely. This is retained as a conversational-preview
limitation rather than treating every occurrence of a scope assurance as a
persistent rule. No external draft tool events appear in this sample, so exact
preapproval draft contents are not directly observable; absence of such events
does not establish that internal preparation was skipped. The supervisor
resolved FABLE-3 on the reviewed correction and final durable-output evidence,
without claiming ideal preview wording or visibility into unrecorded drafting.

The six Fable review points now have scoped evidence and supervisor dispositions:

| Review point | Addressed evidence and limits |
|---|---|
| Inspection side effects and execution reporting | `2d998dd1` makes inspection read-only; both new case-5 traces perform no target execution and report only configured checks. Earlier F5 failed-chain scope limits remain unchanged. |
| Setup-session prose in durable output | `e7e711c6` plus final case 5 supports the output boundary; first Fable case 5 remains Material failure, with preview/draft limits above. |
| Host coverage labeling | BOOK and this section explicitly identify Codex-only setup and cross-host standards usage; no Claude/Agy setup outcome is inferred. |
| Missing routine Maintenance fixture tests | Both corrections passed the 37-test suite, including all 16 Maintenance preparations, fixture bytes, prompt checks, and copied private links. |
| Duplicated operating instructions | `2d998dd1` delegates README operating detail to shared guidance; independent static review found no material findings. The generalized approval gate also remains supported by new case 12. |
| Evidence lifetime | Supervisor SHA-256 verification preserved all 4,567 prior files at P, with a manifest; new runs are stored there directly. This is persistent local storage, not remote backup. |

All **38 runs** remain separately attributable: original 24 Supported/4 Material
failures, first corrective 5 Supported/1 Material failure, earlier final case 5
Supported, first Fable follow-up 1 Supported/1 Material failure, and last case 5
Supported. These comprise 88 turns and 3,267.986 summed turn seconds. BOOK counts
10 corrective follow-ups while retaining the original 24/4/0 assessment column.
No finding remains Open after the supplied supervisor dispositions. Final
whole-change review and verification remain separate supervisor steps; no more
live calls were made. Before scratch cleanup, the supervisor will retain exact
follow-up implementation, evaluation, and review reports under
`P/fable-review-evidence/`.
