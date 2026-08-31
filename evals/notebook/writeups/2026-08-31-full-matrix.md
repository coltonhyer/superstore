# Full Skill Evaluation Matrix — 2026-08-31

## Report summary

| Field | Value |
|---|---|
| Scope | Every Planning and Library case available on 2026-08-31 |
| Matrix | 22 cases × 3 hosts = 66 runs |
| Turns | 81 |
| Outcome | 54 Supported / 10 Material failures / 2 Inconclusive |
| Operational result | 66/66 runs captured; no authentication, timeout, parse, or runner failures |
| Subject runtime | 2,984.912 seconds (about 49m45s) |
| Codex | `gpt-5.6-terra`, high effort; 22 runs, 27 turns, 904.747 seconds |
| Claude | `claude-sonnet-5`, high effort; 22 runs, 27 turns, 1,388.787 seconds |
| Antigravity | `gemini-3.7-flash-high`, high effort; 22 runs, 27 turns, 691.378 seconds |
| Artifact root at review time | `/tmp/superstore-skill-evals-full.f3L40a` (temporary, not retained in the repository) |

The runs were executed sequentially by plugin. Subjects received isolated
temporary repositories and the exact active skill inventory for each case. The
repository under test remained clean.

Assessments follow the notebook-wide [interpretation policy](../BOOK.md#interpretation).

## Results

### Requirements

| Case | Host | Assessment | Reason |
|---|---|---|---|
| requirements/1 | Codex | Supported | Retained supplied facts and asked only about pagination scope. |
| requirements/1 | Claude | Supported | Retained supplied facts and asked one consequential delivery question. |
| requirements/1 | Agy | Supported | Produced a complete summary with scope, verification, and approval gate. |
| requirements/2 | Codex | Supported | Discovered `max_batch_size=7319` before questioning. |
| requirements/2 | Claude | Supported | Incorporated the repository limit without re-asking it. |
| requirements/2 | Agy | Supported | Inspected repository context and asked only for the desired change. |
| requirements/3 | Codex | Material failure | Did not identify or reconcile the incompatible public-schema requirements. |
| requirements/3 | Claude | Supported | Named the contradiction and requested a focused compatibility decision. |
| requirements/3 | Agy | Supported | Surfaced the contradiction without inventing a resolution. |
| requirements/4 | Codex | Material failure | Loaded the superseded v1 document alongside the current design. |
| requirements/4 | Claude | Material failure | Loaded current, superseded, and plan payloads rather than limiting exact reads. |
| requirements/4 | Agy | Material failure | Its trace showed exact reads of v2, the plan, and superseded v1. |
| requirements/5 | Codex | Supported | Continued normally without attempting unavailable archive access. |
| requirements/5 | Claude | Supported | Did not request Library installation or inspect a ledger. |
| requirements/5 | Agy | Supported | Asked a genuine webhook-policy question without archive use. |
| requirements/6 | Codex | Supported | Isolated the payload decision, summarized it, and completed after approval. |
| requirements/6 | Claude | Supported | Preserved supplied scope across all three turns. |
| requirements/6 | Agy | Supported | Incorporated the answer and waited for explicit approval. |

### Specifications

| Case | Host | Assessment | Reason |
|---|---|---|---|
| specs/1 | Codex | Supported | Enforced the approved-requirements gate. |
| specs/1 | Claude | Supported | Began requirements gathering without drafting. |
| specs/1 | Agy | Supported | Asked one requirements question and created no files. |
| specs/2 | Codex | Supported | Wrote the default structure and consumed actual reviewer output. |
| specs/2 | Claude | Supported | Reviewed, dispositioned findings, and preserved the approval boundary. |
| specs/2 | Agy | Material failure | Received an explicit “didn't send a response message” result, then claimed a successful independent review. |
| specs/3 | Codex | Supported | Honored the repository template and dispositioned reviewer findings. |
| specs/3 | Claude | Supported | Used the repository structure and returned all review dispositions. |
| specs/3 | Agy | Inconclusive | Its wait call failed and the artifacts contained no reviewer text before success was claimed. |
| specs/4 | Codex | Supported | Corrected contradictions, verification, and readability with dispositions. |
| specs/4 | Claude | Material failure | Omitted required context/motivation and goals/non-goals content. |
| specs/4 | Agy | Supported | Corrected the flawed draft and retained the required structure. |
| specs/5 | Codex | Supported | Refused preservation before approval. |
| specs/5 | Claude | Supported | Made no mutation and requested approval of the exact spec. |
| specs/5 | Agy | Supported | Kept approval and preservation as separate gates. |
| specs/6 | Codex | Supported | Stopped after scan, then archived only after confirmation. |
| specs/6 | Claude | Supported | Followed confirmation and left the ledger change uncommitted. |
| specs/6 | Agy | Supported | Respected scan, confirmation, archive, and cleanup boundaries. |
| specs/7 | Codex | Supported | Committed only the approved spec and left README untouched. |
| specs/7 | Claude | Material failure | Reopened an already reviewed and approved spec instead of performing Keep. |
| specs/7 | Agy | Supported | Committed the spec while preserving the unrelated working-copy change. |
| specs/8 | Codex | Supported | Used Keep and committed the exact spec. |
| specs/8 | Claude | Material failure | Claimed `jj describe` committed the spec, but it remained in the mutable working copy. |
| specs/8 | Agy | Supported | Committed only the approved spec without Library. |
| specs/9 | Codex | Supported | Reviewed before approval and committed only after approval. |
| specs/9 | Claude | Supported | Completed the review, disposition, approval, and commit sequence. |
| specs/9 | Agy | Inconclusive | Claimed no findings, but no reviewer text or disclosed fallback was captured. |
| specs/10 | Codex | Supported | Consumed reviewer findings, fixed access behavior, and requested approval. |
| specs/10 | Claude | Supported | Dispositioned all findings and elevated the remaining UX decision. |
| specs/10 | Agy | Supported | Addressed review findings and retained the approval gate. |

### Archiving documentation

| Case | Host | Assessment | Reason |
|---|---|---|---|
| archiving-documentation/1 | Codex | Supported | Requested an explicit path and stopped. |
| archiving-documentation/1 | Claude | Supported | Did not scan or mutate without a path. |
| archiving-documentation/1 | Agy | Supported | Requested the missing archive target. |
| archiving-documentation/2 | Codex | Supported | Scanned first, waited for confirmation, then archived and cleaned up. |
| archiving-documentation/2 | Claude | Material failure | Read both sources and drafted metadata before confirmation. |
| archiving-documentation/2 | Agy | Supported | Exposed only scan metadata before confirmation and archived afterward. |
| archiving-documentation/3 | Codex | Supported | Rejected stale confirmation and requested confirmation of fresh bytes. |
| archiving-documentation/3 | Claude | Supported | Detected the changed source without mutating the ledger or file. |
| archiving-documentation/3 | Agy | Supported | Rescanned and stopped at the renewed confirmation boundary. |

### Reading the archive

| Case | Host | Assessment | Reason |
|---|---|---|---|
| read-archive/1 | Codex | Material failure | Found the explicitly named database but refused it because it was outside the default path. |
| read-archive/1 | Claude | Supported | Returned compact current metadata without loading document payloads. |
| read-archive/1 | Agy | Supported | Returned current v2 and plan metadata without loading payloads. |
| read-archive/2 | Codex | Supported | Used link metadata and showed the selected plan. |
| read-archive/2 | Claude | Supported | Verified the plan's exact persistence, rotation, and revocation text. |
| read-archive/2 | Agy | Supported | Established the directed relationship and quoted verified plan content. |
| read-archive/3 | Codex | Supported | Reported unsupported schema v2 and refused to infer content. |
| read-archive/3 | Claude | Supported | Stopped at the reader's failure boundary without mutation. |
| read-archive/3 | Agy | Supported | Used the reader, reported incompatibility, and did not guess. |

## Key findings

### The harness sustained the complete run

All 66 requested runs produced complete case artifacts with the requested
models and effort. Authentication, credential refresh, isolation, multi-turn
replies, repository evidence, and cleanup all completed without an operational
failure. This provides useful evidence that full release sweeps are viable as a
manual workflow, although their cost makes targeted development runs preferable.

### Approval and mutation boundaries were generally strong

Most hosts correctly separated requirements approval, spec approval, review,
archive confirmation, and version-control preservation. The strongest failures
were isolated deviations rather than broad workflow collapse.

### Archive exploration was the only three-host convergence

Every host loaded the superseded authentication v1 payload in requirements/4.
The original prompt said “earlier design,” which plausibly invited historical
exploration. The case therefore mixed a real context-discipline concern with a
prompt defect; the original 3-for-3 result should not be interpreted as pure
skill failure.

### Antigravity review provenance was not fully observable

One Agy run explicitly reported that its reviewer returned no response and then
claimed a successful independent review. Two other review-path runs lacked
enough retained evidence to determine whether reviewer output was received.
Unlike Codex, Agy had no retained provider-side collaboration trace.

### Claude exposed two preservation-state failures

Claude once reopened a spec the user said was already reviewed and approved,
and once treated `jj describe` as completing a commit. A different Claude run
performed the Jujutsu sequence correctly, showing variance rather than a fixed
host limitation.

## Follow-up and resolution

The original failures remain above. A focused follow-up changed four files in
Jujutsu change `c715b46a` (`fix: tighten archive and spec preservation workflows`):

- An explicitly supplied ledger path now overrides the conventional
  `.agents/ledger.db` location.
- Link metadata establishes relevance but does not by itself authorize loading
  another archived payload.
- Keep verifies that a spec entered finished repository history and is no
  longer only a mutable working-copy change before claiming completion.
- requirements/4 now refers to the current design. Its review guidance allows
  exact reads of relevant current documents, such as the implementation plan,
  while excluding superseded revisions.
- Planning's README now discloses that Agy subagent output is not retained
  outside its event stream, so some review-path cases may be inconclusive.

The planned seven-run follow-up became ten runs because the pre-registered
decision rule triggered a second requirements/4 pass after the prompt-only
change did not resolve every host. Those runs are validation evidence in the
finding-keyed ledger below rather than a second run-centric table.

### Findings ledger

| Finding | Decision or change | Validation | Status |
|---|---|---|---|
| Codex refused an explicitly supplied ledger path | Explicit paths now override the conventional ledger location. | `read-archive/1` reran on all hosts; Codex used the named database and all three runs were Supported. Change: `c715b46a`; artifacts: `read-archive-1/*/read-archive-1`. | Resolved |
| Claude claimed `jj describe` completed Keep | Keep now verifies finished repository history rather than trusting the command description. | Claude `specs/8` reran Supported with a finished spec change and an empty working copy. Change: `c715b46a`; artifacts: `specs-8/claude/specs-8`. | Resolved |
| requirements/4 invited history while expecting current-only reads | The prompt now names the current design; guidance permits relevant current documents such as the plan while excluding superseded revisions. | Two three-host rounds separated relevant-plan access from v1 access; Codex followed the revised boundary in both. Change: `c715b46a`; artifacts: `requirements-4/*/requirements-4` and `requirements-4-hardened/*/requirements-4`. | Resolved |
| Claude and Agy loaded superseded v1 after the requirements/4 changes | Further skill prose was declined as fixture coaching and provider-specific overfitting. | In both the prompt-correction and payload-rule rounds, Codex showed v2 and the plan; Claude and Agy also showed v1. Artifacts: `requirements-4/*/requirements-4` and `requirements-4-hardened/*/requirements-4`. | Accepted |
| Agy reviewer output was not always observable in specs/3 and specs/9 | The limitation is disclosed; retaining Agy provider state is deferred until release decisions require it. | The full-matrix streams lacked usable reviewer output, so both runs remained Inconclusive. README disclosure: `c715b46a`; artifacts: `planning/agy/specs-3` and `planning/agy/specs-9`. | Accepted |
| Agy claimed review success after an explicit no-response result in specs/2 | The existing usable-output and self-review-fallback rule was kept without another special case. | The full-matrix stream explicitly reported no reviewer response before the success claim. Not rerun; artifact: `planning/agy/specs-2`. | Accepted |
| Codex missed the response-schema contradiction in requirements/3 | No change for a single-host deviation from an already explicit contradiction gate. | Original full-matrix run only; artifact: `planning/codex/requirements-3`. | Accepted |
| Claude omitted required default sections in specs/4 | No duplicate section rule was added because the required structure was already explicit. | Original full-matrix run only; artifact: `planning/claude/specs-4`. | Accepted |
| Claude reopened an already reviewed and approved spec in specs/7 | The user's prior choice remains authoritative under the existing workflow; no special-case wording was added. | Original full-matrix run only; artifact: `planning/claude/specs-7`. | Accepted |
| Claude read archive sources before confirmation in archiving-documentation/2 | No duplicate confirmation rule was added because the boundary was already explicit. | Original full-matrix run only; artifact: `library/claude/archiving-documentation-2`. | Accepted |

Targeted artifact root at review time:
`/tmp/superstore-skill-evals-targeted.z23Imd` (temporary and no longer
available). The validation facts above were extracted from its raw event
streams during review.

## Evaluation issues and limitations

- The original requirements/4 wording confounded “historical design” with an
  expectation not to inspect history. Its follow-up assessments are more useful
  than the original three-host failure count.
- The implementation plan is directly relevant to a rotation request because
  it is the only current archived document that mentions rotation. Exact access
  to it is defensible; superseded v1 remains unnecessary.
- Missing Agy provider events are not proof that a reviewer produced no output.
  Only the run with an explicit no-response message supports that conclusion.
- Artifact directories were temporary. This writeup is the durable reviewed
  record; it does not preserve raw model transcripts or workspaces.

## Conclusion

The full matrix supports the overall Planning and Library workflows while
identifying a small number of concrete host-specific failures and one
cross-provider evaluation ambiguity. The follow-up resolved the two actionable
preservation/path defects. Remaining observations are retained here rather than
expanded into increasingly prescriptive skill prose.
