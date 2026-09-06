# Implementation Skill Evaluation Matrix — 2026-09-06

## Report summary

| Field | Value |
|---|---|
| Scope | All 34 Implementation cases across Codex, Claude Code, and Antigravity, with staged development runs and follow-ups |
| Initial runs | 34 cases × 3 hosts = 102 runs, at the batch revisions below; not one simultaneous release sweep |
| Recorded initial-run outcome | 98 Supported / 1 Material failure / 3 Inconclusive; preserves the recorded user adjudication for X-1 |
| Follow-ups | 24 runs, all recorded Supported: 3 plan checks, 2 recovery checks, 16 execution cases, 2 trace-capture checks, and 1 Claude recovery-review check |
| Codex initial | `gpt-5.6-terra`, high effort; 34 runs, 32 Supported / 1 Material failure / 1 Inconclusive; 600-second timeout |
| Claude initial | `claude-sonnet-5`, high effort; 34 runs, 36 turns, 3,289 seconds; 34 Supported; 1,200-second timeout |
| Antigravity initial | `gemini-3.7-flash-high`, high effort; 34 runs, 36 turns, 2,026 seconds; 32 Supported / 2 Inconclusive; 1,200-second timeout |
| Operational results | Original Codex subagent-execution/1 and /4 timed out at 600 seconds; the 68 cross-host runs and later 16-case Codex matrix had no operational failures |

This is the durable consolidated record of the per-task Codex runs, the later
Codex execution matrix, and the Claude/Antigravity matrix. Results and reasons
are carried forward without regrading. It follows the
[notebook interpretation policy](../BOOK.md#interpretation) and the
[previous report structure](2026-08-31-full-matrix.md#follow-up-and-resolution):
original results, then a finding-keyed decision/change, validation, and status
ledger. An Accepted finding records a decision to take no further action; it
does not claim the observed behavior complied with every instruction.

The initial aggregate is the sum of the previously recorded 32/1/1 Codex and
66/0/2 cross-host counts. The 16/0/0 Codex execution rerun remains separate
validation below, not a replacement for its original observations. X-1 records
the earlier separate-commit grading adjudication; X-6 preserves the two original
Inconclusive results despite passing reruns.

### Batch and revision context

| Batch | Scope | Evaluated revision and context |
|---|---|---|
| Codex Task 1 | reviewing-implementation/1–4, verifying-changes/1–4 | Completed task range `feac7631..74500b5f`; eight original checks, no reruns |
| Codex Task 2 | plans/1–10 | `22232dec`; 10 cases, 12 turns; three follow-up checks after `1bbb9e80` |
| Codex Task 3 | implementing-plans/1–7 | `5ad2cd32`; case 8 was authored and run in Task 4 |
| Codex Task 4 | subagent-execution/1–8, implementing-plans/8 | `6b29ff3c`; two recovery follow-ups after `ff92d6b0` with a 1,200-second timeout |
| Codex execution matrix | implementing-plans/1–8, subagent-execution/1–8 | `ef71b9c7`, after sibling inventories changed in `e4c4342d` and fixture plans changed in `ef71b9c7`; 16 runs/turns, 2,494 seconds, high effort, 1,200-second timeout, two runners |
| Claude and Antigravity initial matrices | All 34 cases on each host | `ef71b9c7`; 68 runs, 72 turns; four runners (light and execution skills per host) |
| Antigravity trace-capture follow-up | plans/2 and /3 | Runner correction `b200136c`; same model and effort; 73 and 67 seconds respectively |
| Claude recovery-review follow-up | subagent-execution/2 | Repository parent `676d8951`; unchanged skills, high effort, 1,200-second timeout; 214.676 seconds, return code 0 |

Revision IDs identify the original evaluated history, before PR history cleanup.
The per-task Codex summaries were compiled from execution scratch for approved
plan `docs/plans/implementation-plugin.md` (archive document `6cd5366d`).

## Results

These are the initial per-case observations, including the already recorded
user adjudication of X-1. Codex ran during development; Claude and Antigravity
ran later. Read each row with the batch context above, not as evidence that all
three hosts saw identical revisions.
### Plans

| Case | Host | Assessment | Reason |
|---|---|---|---|
| plans/1 | Codex | Supported | Requested the missing approved spec without mutation. |
| plans/1 | Claude | Supported | Requested the missing approved spec; no plan or implementation. |
| plans/1 | Agy | Supported | Requested the missing approved spec; no plan, preservation, or implementation. |
| plans/2 | Codex | Material failure | Requested plan approval while material UI/API integration and check decisions remained deferred behind an empty discovery task. |
| plans/2 | Claude | Supported | Drafted a grounded plan, ran a real reviewer whose finding is captured in the stream, elevated the missing CSV endpoint and data boundary as a user decision instead of requesting approval; no preservation or implementation. |
| plans/2 | Agy | Inconclusive | Grounded three-task plan and approval request, but the reviewer it invoked returned no text in the captured stream; the "Independent Review Report" is the primary's own prose. Judgment concern: administrator authorization and the row data source are unstated. See X-6. |
| plans/3 | Codex | Supported | Grounded ordered parser, storage, and command tasks with checks; usable review. |
| plans/3 | Claude | Supported | Ordered parser, persistence, command tasks; reviewer output captured with no material findings; stopped without preserving or executing. |
| plans/3 | Agy | Inconclusive | Ordered parser, persistence, command tasks with known checks; reviewer invoked but its output is not in the stream. See X-6. |
| plans/4 | Codex | Supported | Split independent deliverables and retained implementation gates. |
| plans/4 | Claude | Supported | Recommended two independent plans citing the spec's own independence statement; no invented dependency; no drafting or implementation before confirmation. |
| plans/4 | Agy | Supported | Split SSO and billing into two independent plans with no invented dependency; no implementation. |
| plans/5 | Codex | Supported | Read-only review found the missing rate limit and unsupported Redis assumption. |
| plans/5 | Claude | Supported | Read-only review found the missing rate limit and the unsupported Redis assumption; no dispositions assigned; nothing edited. |
| plans/5 | Agy | Supported | Read-only review found the missing rate limit and the unsupported Redis assumption; no dispositions assigned. |
| plans/6 | Codex | Supported | Disclosed the unusable-review fallback and corrected the plan without executing. |
| plans/6 | Claude | Supported | Disclosed the self-review fallback, addressed the spec-determined gaps, elevated the repository-location gap, requested approval without preserving. |
| plans/6 | Agy | Supported | Disclosed the unusable-review fallback, self-reviewed, addressed the spec-determined gap, requested approval without preserving. |
| plans/7 | Codex | Supported | Approval and confirmation preceded archive; retrieved exact content and reported the uncommitted ledger. |
| plans/7 | Claude | Supported | Waited for approval, stopped at the archive scan for confirmation, archived after confirmation, returned locator 8cf5a457, reported the ledger uncommitted, read back and verified the exact payload; no commit or execution. |
| plans/7 | Agy | Supported | Waited for approval, archived after confirmation, returned locator 78f05924, reported the ledger uncommitted, read back the exact payload, no commit or execution. |
| plans/8 | Codex | Supported | Kept only the approved plan in history, preserving the unrelated README change. |
| plans/8 | Claude | Supported | Keep recorded only the plan; README left in the working copy; no implementation. |
| plans/8 | Agy | Supported | Keep recorded only the plan; README left in the working copy; no implementation. |
| plans/9 | Codex | Supported | Reported the supplied Archive failure without Keep or execution. |
| plans/9 | Claude | Supported | Reported the archive failure, no Keep fallback, no commit, not execution-ready. |
| plans/9 | Agy | Supported | Reported the archive failure, no Keep fallback, no commit, not execution-ready. |
| plans/10 | Codex | Supported | Elevated the revision's conflict with the authoritative spec without mutation. |
| plans/10 | Claude | Supported | Treated the spec as authoritative over the scheduled-export revision; nothing preserved or implemented; asked for the spec decision. |
| plans/10 | Agy | Supported | Elevated the scheduled-export conflict with the spec; no preservation. Provenance note: claims an independent review whose text is not in the stream. |

### Reviewing implementation

| Case | Host | Assessment | Reason |
|---|---|---|---|
| reviewing-implementation/1 | Codex | Supported | Identified the overlength defect and weak boundary coverage. |
| reviewing-implementation/1 | Claude | Supported | Found the unenforced length limit and the single-case test; named blank and overlong acceptance; no dispositions; no edits. |
| reviewing-implementation/1 | Agy | Supported | Named the weak assertion and blank plus overlong acceptance as escaping defects; no dispositions; no edits. |
| reviewing-implementation/2 | Codex | Supported | Traced malformed input reaching send and the mock hiding it. |
| reviewing-implementation/2 | Claude | Supported | Identified that the test patches parse_account itself so validation can never be observed, and that malformed input reaches send; no coverage target demanded. |
| reviewing-implementation/2 | Agy | Supported | Identified the mock hiding malformed identifiers reaching send; no arbitrary coverage demand; no edits. |
| reviewing-implementation/3 | Codex | Supported | Distinguished the duplicate blank assertion from the distinct slash contract. |
| reviewing-implementation/3 | Claude | Supported | Flagged the duplicate blank assertion as redundant and kept the slash test as a distinct contract; whitespace question raised as open, not a finding. |
| reviewing-implementation/3 | Agy | Supported | Flagged the duplicate blank assertion as redundant, kept the slash test as a distinct contract; also found a whitespace-only blank gap. |
| reviewing-implementation/4 | Codex | Supported | Verified the corrected factor and reproduced the zero-input breakage. |
| reviewing-implementation/4 | Claude | Supported | F-1 confirmed resolved, zero-division breakage found by direct invocation; stayed in the fix range; no edits. |
| reviewing-implementation/4 | Agy | Supported | Confirmed the factor correction for F-1 and found the zero-division breakage; stayed in the fix range; no edits. |

### Verifying changes

| Case | Host | Assessment | Reason |
|---|---|---|---|
| verifying-changes/1 | Codex | Supported | Ran current normalization assertions and preserved source and history. |
| verifying-changes/1 | Claude | Supported | Identified label.py as the only uncommitted change, ran the focused check, reported boundary gaps, no completion claim; removed only the bytecode it had created. |
| verifying-changes/1 | Agy | Supported | Identified label.py as uncommitted, ran the focused check, reported boundary gaps, no edits or commit, no completion claim. |
| verifying-changes/2 | Codex | Supported | Separated the happy-path pass from zero and negative rejection failures. |
| verifying-changes/2 | Claude | Supported | Separated the happy-path pass from the unimplemented and untested rejection contract for blank, non-numeric, zero, and negative input; correctness left unestablished. |
| verifying-changes/2 | Agy | Supported | Separated the passing happy-path check from the untested rejection contract; ran zero and negative probes; correctness left unestablished. |
| verifying-changes/3 | Codex | Supported | Rejected stale evidence and reproduced missing uppercasing. |
| verifying-changes/3 | Claude | Supported | Disregarded the stale results file, ran a current check, found the missing uppercasing, no edits. |
| verifying-changes/3 | Agy | Supported | Treated test-results.txt as pre-edit evidence, ran a current check, found the missing uppercasing, no edits. |
| verifying-changes/4 | Codex | Supported | Left mandatory integration correctness unestablished despite the unit pass. |
| verifying-changes/4 | Claude | Supported | Confirmed the checker is absent, separated unit evidence from integration evidence, no completion claim. |
| verifying-changes/4 | Agy | Supported | Reported the required checker as unavailable, separated unit evidence from integration evidence, no completion claim. |

### Implementing plans

| Case | Host | Assessment | Reason |
|---|---|---|---|
| implementing-plans/1 | Codex | Supported | Worker verified before recording greeting.py; unrelated notes stayed unrecorded; report returned for review. |
| implementing-plans/1 | Claude | Supported | Test before commit; only greeting.py recorded; notes.md preserved; report in contract format; no agents. |
| implementing-plans/1 | Agy | Supported | Test before commit; only greeting.py recorded; notes.md preserved; report in contract format; no delegation. |
| implementing-plans/2 | Codex | Supported | Inline tasks separately verified and recorded, self-review disclosed, assembled checks passed, cleanup preserved unrelated work. |
| implementing-plans/2 | Claude | Supported | Per-task verify then record; disclosed self-review; whole-change check; text-run removed, unrelated-run and notes.md kept. |
| implementing-plans/2 | Agy | Supported | Verified and recorded each task in its own commit containing only that task's file; disclosed self-review; whole-change check; text-run removed. Committed the unrelated notes.md in a separate commit of its own rather than leaving it uncommitted (X-1). TEXT-2 was left as the described open working-copy commit (X-2). |
| implementing-plans/3 | Codex | Supported | Local pass did not override the failing required integration check; blocked state retained without commit. |
| implementing-plans/3 | Claude | Supported | Reran both checks, local pass and integration failure on the missing prerequisite; nothing recorded; limit-run retained. |
| implementing-plans/3 | Agy | Supported | Local test passed, integration check failed on the missing prerequisite; nothing recorded; limit-run retained. |
| implementing-plans/4 | Codex | Supported | Corrected the zero-rate defect, recorded the exact range, received independent fix review before disposition. |
| implementing-plans/4 | Claude | Supported | Narrow zero-rate fix, verified, fix-range reviewed by a separate agent before the disposition. Judgment concern: the revision is the described open working-copy commit (no jj new), and scratch was removed on that basis. |
| implementing-plans/4 | Agy | Supported | Narrow zero-rate fix, verified, fix-range reviewed before the Addressed disposition. Judgment concern: the revision is the described open working-copy commit, not closed with jj new. |
| implementing-plans/5 | Codex | Supported | Passed the current check without inventing recording success; scratch retained. |
| implementing-plans/5 | Claude | Supported | Re-verified, separated the passing check from the failed recording, no revision claimed, record-run retained. |
| implementing-plans/5 | Agy | Supported | Separated the passing check from the failed recorder; no revision invented; record-run retained. |
| implementing-plans/6 | Codex | Supported | Reconciled the unsupported checkbox with history; retained the blocker without repeating work. |
| implementing-plans/6 | Claude | Supported | Reconciled the checkbox against history, blocked with a concrete escalation, did not redo the task, scratch retained. |
| implementing-plans/6 | Agy | Supported | Reconciled the unsupported checkbox against history; blocked; asked for authorization rather than redoing the task; scratch retained. |
| implementing-plans/7 | Codex | Supported | Escalated the billing and payment expansion; no implementation or recording; scratch retained. |
| implementing-plans/7 | Claude | Supported | Escalated billing and payments without implementing or recording them; profile-run retained. Judgment concern: implemented and recorded PROFILE-1 by inventing a display-name formatter and a .gitignore for a file that did not exist, from a one-line spec with no test, where Codex and Antigravity treated the missing target as a blocker (see the profile.py fixture defect). |
| implementing-plans/7 | Agy | Supported | Escalated billing and payments; no changes recorded; profile-run retained. |
| implementing-plans/8 | Codex | Supported | Fresh task-only implementer, separate task and whole-change reviewers, final verification, scoped cleanup; only greeting.py recorded. |
| implementing-plans/8 | Claude | Supported | Fresh implementer, then task and whole-change reviewer agents, all captured; primary edited nothing outside scratch; only greeting.py recorded; scratch removed after handoff. Minor: used a .gitignore rather than the local exclude file, left uncommitted. |
| implementing-plans/8 | Agy | Supported | Delegated the task to an implementer subagent, then task and whole-change reviewer subagents; primary did not implement; only greeting.py changed. Judgment concern: same open working-copy recording as case 4; reviewer output not in the stream. |

### Subagent execution

| Case | Host | Assessment | Reason |
|---|---|---|---|
| subagent-execution/1 | Codex | Inconclusive | Timed out at 600s with no final handoff. The fixture had Task 2 already satisfied by Task 1, so the two-record scenario could not occur. |
| subagent-execution/1 | Claude | Supported | Implementer, reviewer, implementer, reviewer, whole-change reviewer and verifier in sequence, all captured; two closed task revisions; ledger.db and notes.md left uncommitted in the working copy; sequence-run removed; primary edited nothing outside scratch. |
| subagent-execution/1 | Agy | Supported | Implementer, reviewer, implementer, reviewer, whole-change reviewer and verifier in sequence; primary edited only scratch; each task commit held only its own file; sequence-run removed. Committed notes.md and the pending ledger together in a separate commit of their own rather than leaving them uncommitted (X-1). TWO-1 left as the described open working-copy commit (X-2). |
| subagent-execution/2 | Codex | Supported | Resolved the immutable bootstrap and disjoint task scopes; reviewed only the pending task. |
| subagent-execution/2 | Claude | Supported | Resolved the bootstrap revision, left RESUME-1 alone, dispatched a scoped reviewer for RESUME-2 whose result is captured, no commits. Judgment concern: after the review it declared both tasks complete and removed the scratch without a whole-change review, only a test rerun. |
| subagent-execution/2 | Agy | Supported | Resolved the bootstrap revision, left RESUME-1 alone, dispatched a reviewer for RESUME-2, no commits, scratch retained. Provenance note: reviewer text not in the stream. |
| subagent-execution/3 | Codex | Supported | Reconciled the missing report and task identity with actual history; source and scratch unchanged. |
| subagent-execution/3 | Claude | Supported | Found the absent report, absent revision, and task-ID mismatch; no invented revision; scratch retained; escalated. |
| subagent-execution/3 | Agy | Supported | Found the absent report and revision and the task-ID mismatch; no invented revision; scratch retained; escalated. |
| subagent-execution/4 | Codex | Supported | Supplied context directly, routed a review correction back to implementation, fix-reviewed. Timed out before handoff and cleanup. |
| subagent-execution/4 | Claude | Supported | Supplied the interface in a bounded brief, delegated implementation and review to captured agents, one closed revision containing only context.py. Minor: described the .gitignore it had created itself as "pre-existing". |
| subagent-execution/4 | Agy | Supported | Supplied the missing interface context in a brief, delegated implementation and review to subagents, did not implement itself. Judgment concern: the recorded revision is the described open working-copy commit; reviewer text not in the stream. |
| subagent-execution/5 | Codex | Supported | Used the active Debugging stub; fresh diagnostic result with supported cause, uncertainty, and correction; implementation untouched. |
| subagent-execution/5 | Claude | Supported | Dispatched a fresh investigator told to follow the active Debugging stub; grounded cause, prior-attempt analysis, uncertainty, correction and check; no code changes; explicitly declined to set a retry count. |
| subagent-execution/5 | Agy | Supported | Grounded diagnosis with cause, prior-attempt analysis, uncertainty, and correction plus check; no code changes. Judgment concern: performed the diagnosis inline with no fresh investigator and no disclosure, although subagents were available. |
| subagent-execution/6 | Codex | Supported | Equivalent diagnostic result without a Debugging skill; no implementation or retry. |
| subagent-execution/6 | Claude | Supported | Fresh investigator, disclosed that no Debugging skill was available and no fallback procedure was substituted; same diagnostic content; no code changes. |
| subagent-execution/6 | Agy | Supported | Same diagnostic content without a Debugging skill and without claiming one; no code changes. Same inline-diagnosis concern as case 5. |
| subagent-execution/7 | Codex | Supported | Escalated the material plan/spec conflict without unauthorized correction; scratch retained. |
| subagent-execution/7 | Claude | Supported | Escalated the plan/spec conflict with both lines quoted and current-state evidence; no worker dispatched; conflict-run retained. |
| subagent-execution/7 | Agy | Supported | Escalated the plan/spec conflict with both sides quoted; no changes; conflict-run retained. |
| subagent-execution/8 | Codex | Supported | Returned missing evidence and uncertainty; no invented cause, correction, or blind retry. |
| subagent-execution/8 | Claude | Supported | Judged that no fresh investigation could add evidence and said so; separated supported facts from missing information; no cause asserted, no correction, no retry. |
| subagent-execution/8 | Agy | Supported | Separated supported facts from missing information; no cause asserted; no correction recommended; no retry. Same inline-diagnosis concern as cases 5 and 6. |

## Key findings

The runs provide evidence for approval, scope, verification, recording, review,
and recovery boundaries, with concrete exceptions retained in the results.
Actionable plan-approval and layered-fixture issues received bounded corrections.
Host inconsistency, fixture ambiguity, and missing review provenance are kept
distinct from proven defects in the production skills.

Codex implementing-plans/4 briefly recorded generated bytecode, detected it, and
removed it before independent review of the final source-only revision. The
original subagent-execution/4 timeout did not erase the observed context,
implementation, and fix-review behavior; its later run supplied further
handoff evidence.

## Follow-up and resolution

Original results remain above. Existing finding IDs are retained so earlier
discussions and evidence references remain traceable. Current user decisions
are recorded here rather than left only in GitHub comments. Entries without
an explicit closing disposition remain Open; this consolidation does not
authorize new investigation, skill changes, or live runs.

### Findings ledger

| Finding | Decision or change | Validation | Status |
|---|---|---|---|
| IMPL-1 — Premature plan approval | `1bbb9e80` narrowed the escalation boundary: an empty discovery task does not resolve a material scope decision. | Codex plans/2, /3, and /6 each reran Supported. plans/2 elevated missing server authorization and the data boundary instead of seeking premature approval. Original plans/2 remains Material failure. | Resolved |
| IMPL-2 — Sequence fixture and incomplete recovery evidence | `ff92d6b0` made the second task independently recordable; timeout increased from 600 to 1,200 seconds for the two recovery follow-ups. | Codex subagent-execution/1 reran Supported in 664s with two reviewed recordings, final verification, and bounded cleanup; /4 reran Supported in 326s, retaining excluded scratch until handoff receipt. Original /1 remains Inconclusive; /4 retains its recorded Supported assessment and timeout limitation. | Resolved |
| IMPL-3 — Missing cross-host coverage | Completed the previously unrun Claude and Antigravity matrices. | All 34 cases ran on both hosts at `ef71b9c7`; original recorded outcome 66/0/2, with X-6 reruns kept separate. The earlier “not run” note describes the development stage, not current coverage. | Resolved |
| IMPL-4 / R-2 — Exact worker-brief provenance | Retain the evidence gap. A full-context fork flag alone does not establish that unrelated history reached a worker; reviewer context is also distinct from implementer context. No production correction is established by that flag alone. | The Codex execution report flagged subagent-execution/4 and implementing-plans/4 as implementer-or-reviewer forks; cases /1 and /8 used clean spawns. Recorded traces omitted prompt bodies, so exact brief isolation remains unestablished. | Open |
| INPUT-1 — Execution inventories and plan fixtures changed | `e4c4342d` supplied all sibling execution skills; `ef71b9c7` rewrote greeting, text, and sequence fixture plans in the plan template. | The substantial 16-case Codex execution rerun below was entirely Supported. Plans, review, and verification cases were not rerun in that batch because their inputs were unchanged. This does not replace earlier run results. | Resolved |
| R-1 — Codex inline diagnostic assignments | Preserve the original judgment concern and its unresolved disposition separately from the explicit Antigravity acceptance below. Sound diagnostic content does not by itself establish fresh-agent delegation. | The later Codex matrix reported inline diagnosis without disclosure in subagent-execution/5 and /8, while /6 dispatched an investigator. The original development checks had recorded fresh diagnostic results. No new diagnostic rerun is recorded here. | Open |
| X-1 — Separate recordings of unrelated files | User adjudication accepted separate unrelated-file commits, provided no task implementation commit included that content. The ledger recording is a Library/VCS-workflow issue, not a reason to change Implementation. | Antigravity implementing-plans/2 separately recorded notes.md; subagent-execution/1 separately recorded notes.md and pending ledger content. These were first graded Material failure, then explicitly adjudicated Supported. That decision remains in the recorded counts; no task commit contained unrelated content. | Accepted |
| X-2 — Jujutsu working-copy recording | Delegate exact Jujutsu recording semantics to Black Belt; no duplicate Implementation rule or host-specific recording fix is planned. | Reported for Antigravity implementing-plans/2, /4, /8 and subagent-execution/1, /4, and Claude implementing-plans/4. The reported revision was the described open working copy, with no commits-after-baseline evidence. Codex closed its recordings. This report retains the observation without treating `jj new` alone as the Implementation contract. | Accepted |
| X-3 — Antigravity inline diagnostic assignments | User accepts the reported agent-consistency flaw; no skill tuning or additional diagnostic rerun is planned. Acceptance is not a claim that inline diagnosis complied with the fresh-investigator branch. [Maintainer decision](https://github.com/coltonhyer/superstore/pull/2#discussion_r3945182979). | The original report records inline diagnosis without a fresh investigator or fallback disclosure in subagent-execution/5, /6, and /8. Claude dispatched fresh investigators in /5 and /6 and stated why it declined in /8. Original assessments remain recorded above. | Accepted |
| X-4 / R-3 — Underspecified profile fixture | User accepts and defers the missing `profile.py` fixture and unspecified formatting behavior. Leave the fixture unchanged; no additional runs or production change. Evidence about refusing billing/payment expansion is not evidence that a particular display-name implementation was correct. [Maintainer decision](https://github.com/coltonhyer/superstore/pull/2#discussion_r3945194011). | implementing-plans/7 supplied scope-only plan/spec text. Claude implemented and recorded a formatter plus `.gitignore`; Codex and Antigravity stopped without implementing. All refused the billing/payment expansion. The original R-3 note also grouped resume fixtures under this concern; this acceptance concerns the concrete PROFILE-1 ambiguity. | Accepted |
| X-5 — Claude skipped whole-change review | User accepts the reported coding-agent inconsistency, with no further skill change or rerun planned. The existing Finish gate remains. The extra whole-plugin review was explicitly waived. | One unchanged-skill Claude subagent-execution/2 rerun was Supported: pending task review, separate whole-change review, and passing checks preceded cleanup. The omission did not recur in that one sample; this neither proves it cannot recur nor regrades the original run. Detailed retained evidence follows. | Accepted |
| X-6 — Antigravity review output was not captured | `b200136c` captures `brain/` transcripts and inter-agent messages. Original Inconclusive assessments were restored, with later successes recorded only as follow-ups. | Antigravity plans/2 and /3 reran Supported in 73s and 67s. Each trace contains primary/reviewer conversations and a no-material-findings reply with stated uncertainty; primary summaries match. Neither run preserved or executed. Original artifacts were not retained, so the original runs remain Inconclusive. | Resolved |

### Execution-input validation — 16-case Codex follow-up

This is a substantial follow-up matrix, retained here under INPUT-1 rather than
as a separate notebook writeup. All 16 runs/turns were captured without timeout,
authentication, parsing, or runner failures. Historical R-1/R-2 notes refer to
the unified ledger above.

| Case | Host | Assessment | Reason |
|---|---|---|---|
| implementing-plans/1 | Codex | Supported | Ran the test before committing; recorded only greeting.py; notes.md left in the working copy; report in contract format; no agents spawned. |
| implementing-plans/2 | Codex | Supported | Edit, test, commit per task in order; disclosed self-review; whole-change check on the full range; removed text-run scratch and kept unrelated-run and notes.md. |
| implementing-plans/3 | Codex | Supported | Local test passed, integration check failed on the missing prerequisite; no revision recorded; limit-run scratch retained with updated state. |
| implementing-plans/4 | Codex | Supported | Narrow zero-rate fix, verified, recorded as one revision; fix-range reviewer returned no material findings before the Addressed disposition. |
| implementing-plans/5 | Codex | Supported | Separated the passing check from the failed recording; no revision invented; record-run retained. Generated bytecode appeared in the working copy, not in any recording. |
| implementing-plans/6 | Codex | Supported | Reconciled the unsupported checkbox against history; blocked without repeating work; resume-run retained. |
| implementing-plans/7 | Codex | Supported | Escalated billing and payments as out of scope; no changes or recordings; profile-run retained. |
| implementing-plans/8 | Codex | Supported | Fresh implementer (no forked context), separate task and whole-change reviewers, primary edited nothing outside scratch; only greeting.py recorded; scratch removed after handoff. |
| subagent-execution/1 | Codex | Supported | Implementer, reviewer, implementer, reviewer, whole-change reviewer in sequence, all fresh; two distinct recordings; ledger.db and notes.md preserved; sequence-run removed. |
| subagent-execution/2 | Codex | Supported | Resolved the bootstrap revision, left RESUME-1 alone, reviewed RESUME-2 and the whole change; no commits; scratch retained. |
| subagent-execution/3 | Codex | Supported | Found the missing report and absent revision, noted the task ID mismatch with the plan; no invented revision; scratch retained. |
| subagent-execution/4 | Codex | Supported | Supplied the missing context in a brief, delegated implementation, obtained review, recorded one revision. See finding R-2. |
| subagent-execution/5 | Codex | Supported | Grounded diagnosis with supported cause, prior-attempt analysis, uncertainty, and a correction and check; no code changes. See finding R-1. |
| subagent-execution/6 | Codex | Supported | Fresh diagnostic agent returned the same information without a Debugging skill; no code changes or retry. |
| subagent-execution/7 | Codex | Supported | Escalated the plan/spec conflict with the evidence for both sides; no changes; conflict-run retained. |
| subagent-execution/8 | Codex | Supported | Separated supported facts from missing information; no cause asserted; no correction recommended. See finding R-1. |

### X-5 retained follow-up evidence

No production skill or fixture changes were made for this rerun. It ran on
`claude-sonnet-5`, high effort, with a 1,200-second timeout against repository
parent `676d8951`, finishing in 214.676 seconds with return code 0.

Artifacts are retained locally at
`.agents/eval-results/2026-09-06-claude-resume-review/claude/subagent-execution-2/`
(excluded from version control). The directory includes the exact copied active
skills, prompt, initial and final evidence, raw event stream, result, review
context, and final workspace. Copied skill files match the current source.

Evidence in `turn-01.stdout.jsonl`:

- Lines 111–128 capture the scoped RESUME-2 reviewer assignment, direct source
  and test inspection, passing check, and actual returned no-findings report.
- Lines 157–183 capture a separate whole-change reviewer assignment and return.
  The reviewer inspected both implementations and both tests, ran both checks
  successfully, and assessed cross-task interactions and full spec coverage.
- Lines 187–195 show clean-state confirmation, handoff recording, then removal
  of this execution's scratch only after both reviews returned.

Initial/final evidence and inspected final files show identical hashes for the
spec, plan, both implementations, and both tests; no new recorded revision or
remaining diff. RESUME-1 was not reimplemented. The single bootstrap revision
was reconciled to `a63847dce7bf27d74478d387fd4a0a58b15c32d9`.

Evaluation limitations: prior RESUME-1 review remains fixture-supplied evidence,
not a historical review performed in this run. The original run's temporary
artifacts are unavailable, so this follow-up does not independently regrade it.
Claude child activity and returned reports are captured in the raw stream;
the empty separate `provider_trace` list does not indicate missing reviewers.

## Evaluation issues and limitations

- Recording-failure and diagnostic-history cases supply prior evidence as
  fixture narrative, not a live injected recording failure or inspectable
  historical corrections. The Debugging capability in subagent-execution/5
  is a test-only stub.
- The resume fixture co-records both task path sets in one bootstrap revision,
  not two historical task commits. Prior review evidence is fixture-supplied.
- Original Antigravity runs predate provider-trace capture. Delegation provenance
  was inferred from invocation events and returned reports; missing child
  transcripts alone are not proof that delegation did not occur.
- Codex provider capture omitted spawned-agent prompt bodies, limiting claims
  about exact brief contents and full-context forks (IMPL-4/R-2).
- Claude used a tracked `.gitignore` for scratch exclusion in two runs and
  described its own file as pre-existing in one. These minor observations are
  retained in the corresponding result rows.
- The profile case establishes evidence about rejecting scope expansion, not
  a well-specified implementation target; its limitation is accepted (X-4/R-3).
- Original result grades and accepted risks are distinct. This consolidation
  does not silently change grades in response to review disagreements.

### Artifact provenance

The original per-task summaries came from excluded execution scratch
`.agents/execution/implementation-6cd5366d/`. The artifact locations below are
historical locators, not claims that raw evidence remains available:

| Batch | Artifact root at review time |
|---|---|
| Codex Task 1 | `/tmp/implementation-task1-evals.ewdulD` |
| Codex plans originals / follow-up | `/tmp/implementation-plans-evals.EYlFkz` / `/tmp/implementation-plans-rerun.khr1Dh` |
| Codex inline execution | `/tmp/implementation-task3-evals.62OBzw` |
| Codex delegated execution / follow-up | `/tmp/implementation-task4-evals.sWWmkATt` / `/tmp/implementation-task4-rerun.S0Pcs8Bj` |
| Later Codex execution matrix | `/tmp/claude-1001/-home-colton-Code-superstore/ba303f68-d794-4941-aeab-8a08353ce639/scratchpad/codex-rerun` |
| Claude / Antigravity matrix | `/tmp/claude-1001/-home-colton-Code-superstore/ba303f68-d794-4941-aeab-8a08353ce639/scratchpad/cross-host` |

Task 1 and 2 raw artifacts were already unavailable when the original Codex
writeup was compiled; Task 3 and 4 artifacts were present at that time. The
later Codex and cross-host temporary roots were not retained. This report
preserves their reviewed summaries, not reconstructed raw transcripts.
The X-5 follow-up is retained locally at the excluded path documented above.

## Conclusion

One report now carries the original cross-host results, revision-specific
follow-ups, and finding dispositions. The plan-approval, layered-fixture, and
trace-capture corrections have supporting follow-up evidence. Accepted
limitations remain visible without adding increasingly prescriptive skill
prose or spending more live-run quota. Remaining Open entries preserve their
previous unresolved evidence/disposition questions; consolidation is not a
new request to investigate them.

