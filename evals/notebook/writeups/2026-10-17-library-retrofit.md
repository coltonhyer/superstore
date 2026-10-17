# Library retrofit evaluations — 2026-10-17

This writeup records the live validation run for the library retrofit: the
change that replaced the SQLite ledger with the plaintext library under
`.agents/library/` and moved Planning and Implementation onto it. The
specification is `.agents/library/specs/library-retrofit.md@xooqszys` and the
plan is `.agents/library/plans/library-retrofit.md@xooqszys`. Original
observations are immutable; repairs, reruns, and dispositions are recorded as
separate evidence. Assessments use the [notebook policy](../BOOK.md#interpretation).

The retained artifact root is
`.agents/eval-results/2026-10-16-library-retrofit/`, excluded from version
control. It holds, per run, the prompt, result record, raw event stream,
provider trace where the host supplies one, before and after repository
evidence, and the final workspace. Runner logs and the launch scripts are in
the session scratchpad and are not retained.

Subjects: Codex `gpt-5.6-terra` at high effort; Claude Code `claude-sonnet-5`
at high effort; Antigravity `gemini-3.8-flash-high` on CLI 1.4.0. The
Antigravity defaults changed during the run: the image pinned CLI 1.1.22 and
the runner's default model `gemini-3.7-flash-high` no longer existed in the
account catalog, which also rejects a separate `--effort` flag for every model
it lists. The pin, the default model, and the agy command builder were
corrected before the agy matrix ran (now one commit, `ykwyzmrs`).

## Matrix

The approved matrix was every case of the six affected suites on all three
hosts, one run per case, staged: claude first, then codex and agy. After the
first host the suites were run concurrently; each run has its own container and
state directory, so concurrency is safe.

| Suite | Cases |
| --- | --- |
| library | 4 |
| specs | 11 |
| requirements | 6 |
| plans | 11 |
| implementing-plans | 10 |
| subagent-execution | 9 |

Commands, one per suite and host, run from the repository root:

```sh
python3 scripts/run_skill_evals.py --plugin plugins/<plugin> --skill <suite> --host <host> --output .agents/eval-results/2026-10-16-library-retrofit/<stage>-<host>/<suite>
```

Follow-ups used the same command with `--case <n>` into `followup<k>-<host>/`
and `rerun2-<host>/` roots.

## Results by suite and host

`S/MF/I` means Supported / Material failure / Inconclusive, as originally
observed, before repairs. Reruns of operational errors (timeouts, and three
containers the operator removed by mistake) replace the errored artifacts and
are counted here.

| Suite | claude (stage 1) | codex (stage 2) | agy (stage 2) |
| --- | --- | --- | --- |
| library | 3/1/0 | 3/1/0 | 3/1/0 |
| specs | 5/6/0 | 9/2/0 | 11/0/0 |
| requirements | 5/1/0 | 5/1/0 | 5/1/0 |
| plans | 8/3/0 | 10/1/0 | 11/0/0 |
| implementing-plans | 8/2/0 | 10/0/0 | 10/0/0 |
| subagent-execution | 5/3/0 | 9/0/0 | 6/3/0 |

Totals as originally observed: claude 34/16/0, codex 46/5/0, agy 46/5/0, or
126/26/0 across the 153 matrix runs. A further 22 corrective follow-up runs
and 5 operational reruns (two 600 s timeouts, three containers the operator
removed) are counted in the ledger below, not here.

The codex and agy columns for specs, plans, implementing-plans, and
subagent-execution ran after one or more of the repairs below, so they also
serve as evidence for those repairs; the skill copy each run saw is recorded
in its workspace.

## Findings ledger

Revision ids below name the commits as they were recorded during the run. After the run the working history was squashed into nine commits: repairs 1 to 7 and the recording-check port are folded into the feature commits of the skills they corrected (`mwymnxyv` library, `vzqkltll` planning, `posrrtnm` implementation), the runner changes into `ykwyzmrs`, and the version bump `rsuwympq` is the final task commit.

Each material failure is listed once, keyed to the behavior, with the repair
that addressed it and the follow-up evidence. States: Resolved, Accepted, Open.

| Id | Behavior | Where seen | Decision or change | Validation | Status |
| --- | --- | --- | --- | --- | --- |
| F1 | Read every library body, including off-topic and draft documents, when the files were listed | claude library/1, requirements/4; codex library/4; agy library/4, requirements/4 | Repair 1 (`tvynztwm`): rule documents out from frontmatter before any body. Repair 7 (`sxssqsnw`): `head`, `cat`, and history dumps count as body reads; history is not discovery | follow-up 1 claude: library/1 and requirements/4 Supported; follow-up 5: five of six held (agy both, claude both, codex requirements/4); codex library/4 still read its two correct bodies by filename before filtering, in the same shell call that loaded the skill | Resolved on claude and agy; codex library/4 Accepted: correct read set, wrong order, driven by the prompt's attached-file list |
| F2 | After explicit approval of a document the user called reviewed, re-reviewed, edited, and asked again | claude specs/6, plans/7, plans/8 | Repair 1: proceed to commit, no re-review or re-ask; post-approval edits need re-approval. Repair 5 (`nvompwry`): review section defers to the commit section; the prior review need not be in this conversation | follow-up 1: specs/6, plans/8 Supported, plans/7 failed; follow-up 3: plans/7 Supported on claude and codex | Resolved |
| F3 | Claimed a commit after `jj describe` on the working-copy commit | claude specs/11, plans/7 | Repairs 1 to 3 (`tvynztwm`, `ypzxylzz`, `uzxqyqmw`): concrete check in both VCS forms, working copy clean and a new revision | follow-up 1: specs/11 Supported; follow-up 3: plans/7 Supported | Resolved |
| F4 | Recording-failure case left `status: draft` | claude plans/9 | Repair 1: the failure paragraph keeps `status: approved` | follow-up 1: plans/9 Supported; codex plans/9 Supported | Resolved |
| F5 | Treated "preserve it now" as approval and committed an unapproved spec | codex specs/5 | Repair 5: a request to preserve, save, record, or commit is not approval. Repair 6 (`kzkomtmu`): say it stays an uncommitted draft and ask for approval | follow-up 3: no commit on both hosts, codex reported "preserved"; follow-up 4: Supported on both hosts | Resolved |
| F6 | Handoff note "recorded" by describing the working-copy commit; scratch deleted | claude implementing-plans/8, subagent-execution/2 | Repair 4 (`woztskty`): recording check ported to implementing-plans, execution-state, and subagent-execution Finish | codex implementing-plans and subagent-execution all Supported under the new text; claude reruns of subagent-execution 1, 2, 4 and implementing-plans 8 all recorded the note correctly | Resolved |
| F7 | Independent reviewer launched below the skill's tier floor | claude specs/2, 3, 9; codex specs/4 (authentication at medium effort) | None in this changeset; the tier wording predates the retrofit | — | Open |
| F8 | Reviewer prompt told the reviewer findings exist | claude specs/10 | None; reviewer-independence wording predates the retrofit | — | Open |
| F9 | Approved requirement narrowed without saying so; weak reviewer missed it | claude specs/9 | None; subject judgment, and the case's scripted reply assumes a draft in turn one | — | Open |
| F10 | Tracked `.gitignore` used instead of the local exclusion and committed with pre-existing work; whole-change review skipped; worker scope widened | claude implementing-plans/8, subagent-execution/4 | None in this changeset; exclusion and Finish contract wording predate the retrofit | claude reruns: the tracked `.gitignore` did not recur and implementing-plans/8 used the exact local exclusion; subagent-execution/4 still skipped the whole-change review at Finish | Open |
| F11 | Skipped an available independent review under a false "no reviewer available" claim and invented an implementation for a file the fixture lacks | claude implementing-plans/7 | None; fixture gap plus pre-existing review rule | — | Open |
| F12 | Diagnosis dispatched without a model setting | claude subagent-execution/6 | None; tier rule predates the retrofit | — | Open |
| F13 | One plan written for two independently integrable tracks instead of recommending separate plans | codex plans/4 | None; fixture gives no code to plan against | — | Open |
| F14 | Did not name the public-schema contradiction | codex requirements/3 | None; subject judgment | — | Open |
| F15 | Diagnosis done inline while subagents were available, with a false or missing "no investigator available" disclosure | agy subagent-execution/5, 6, 8 | None; the Recovery contract predates the retrofit, and the cases do not test dispatch | — | Open |
| F16 | Preservation request without approval reported as "preserved" | codex specs/5 under repair 5 | Repair 6 (`kzkomtmu`): say it stays an uncommitted draft and ask for approval | follow-up 4: Supported on codex and claude | Resolved |

## Evaluation defects

Case and harness problems the reviewers found, separate from subject behavior.

- The prompt's "Attached repository files" list names every fixture, so the
  discovery step is never exercised and filename selection is easy.
- Cases that state "no subagent capability is available" run on hosts that
  expose subagent tools; the subjects followed the prompt.
- Several fixtures leave the target file uncommitted at baseline (greeting.py),
  so a task recording necessarily adds the whole file.
- The shared `local-exclude` fixture already lists some cases' scratch
  directories, so "exclude before creating" is not tested there.
- Plans fixtures contain no application code, so any re-review produces
  blocking findings; case 4's spec is one sentence.
- Supervisor cases run close to the 600 s per-turn timeout; two timed out and
  were rerun.
- `provider_trace` is empty on every host; reviewer prompts and worker briefs
  are not captured; the Codex provider file is not merged into `result.json`.
- Eval commits inside containers carry the real user identity despite the
  "Name and email not configured" warning.
- Antigravity: the runner's `--sandbox` makes the first command fail and the
  model self-escalates; the agent tool restriction is not visible in the init
  event; resumed turns omit the eval agent; finish-tool arguments leak into the
  captured response; harness files are committed into the eval fixture
  revision and visible to subjects.
- The fixture pair for a pinned-read case must differ in byte length, because
  the runner copies fixtures with `copy2` and jj's snapshot keys on size and
  mtime; one such pair was fixed during T2.
- Author guidance for several single-turn cases expects the summary branch
  that a defensible clarifying question makes unobservable.
- The README's Codex tier list and the Antigravity default were stale.

## Whole-change review

An independent whole-change review of the assembled change set found no
material findings and verified spec coverage with no gaps. It recorded five
low items: the runner's `--agy-effort` flag is now a silent no-op; the Library
skill needs a precedence sentence for an explicitly named draft versus a
handed list; the specs skill's first gate has no explicit entry for approving
an existing spec; the plans case 3 and 4 fixture choice differs from the plan's
letter; and the version bump preceded three later skill fixes, which the
squash resolved by making the bump the final task commit.

## Operational notes

- The first host ran serially for about 90 minutes; the rest ran concurrently.
- Three live containers were removed by an operator cleanup that matched by
  command text; the affected cases were rerun under `rerun2-<host>/`.
- Antigravity could not run until the image pin, default model, and command
  builder were corrected; the earlier agy error artifacts were discarded.
