---
name: skill-evals
description: Use when listing, running, monitoring, or reviewing behavioral skill evaluations in this repository.
---

# Skill Evals

Own the evaluation from case selection through evidence-backed review. Observe
subject behavior without coaching it or treating the case author's preferred
answer as ground truth.

## Select the run

1. Discover plugins that contain `skills/*/evals/evals.json` rather than using
   a hardcoded plugin menu.
2. Honor any plugin, skill, case, host, model, and effort requested by the user.
   When required scope is unspecified, list the available cases for each
   relevant plugin:

   ```sh
   python3 scripts/run_skill_evals.py --plugin plugins/<plugin> --list
   ```

3. Before spending live model quota, confirm the run matrix with the user unless
   their request already authorizes that exact scope.
4. Give every run an explicit `--output` directory so its artifacts remain
   available for review.

## Run and observe

Run each selected plugin from the repository root:

```sh
python3 scripts/run_skill_evals.py \
  --plugin plugins/<plugin> \
  --host <host> [--host <host> ...] \
  [--<host>-model <model>] [--<host>-effort <effort>] \
  [--skill <skill>] [--case <id>] \
  --output <artifact-directory>
```

While it runs:

- Confirm that the announced plugin, cases, hosts, models, and effort match the
  approved matrix and that the process and artifact capture continue to make
  progress.
- Observe only. Do not alter a subject workspace, send improvised replies, or
  expose eval definitions or author guidance to the subject.
- A live process or reviewer that is still running has not failed. Use the
  runner's timeout and captured status rather than guessing from silence.
- Treat runner, authentication, timeout, parsing, or artifact failures as
  operational errors, not subject failures. Diagnose them from the retained
  evidence and rerun only the affected scope after correcting the cause.
- Treat completed but undesirable subject behavior as evidence. Do not rerun it
  merely to obtain a passing sample.

After execution, verify that each requested case and host has a `result.json`
and the expected turn artifacts before reviewing behavior.

## Review a run

1. Read the exact active skills under `workspace/.eval/skills`, including only
   the references needed to understand the behavior under review.
2. Read `result.json`, `prompt.txt`, `initial.evidence.json`, every turn's
   response, raw event stream, provider trace, and repository evidence. Inspect
   the final workspace when file contents or version-control state matter.
3. Independently reconstruct the supplied facts, remaining decisions, required
   workflow gates, permitted judgment, and observed actions.
4. Read `review-context.json` last. Its author guidance supplies useful review
   questions, not ground truth. Identify guidance that assumes one valid branch,
   contradicts the skill or request, or depends on evidence the harness did not
   capture.
5. Report only material findings with concrete artifact paths or event evidence.

Distinguish:

- **Contract failure:** an observable hard requirement was violated, such as an
  approval boundary, required sequencing, unsupported completion claim, or
  repository side effect.
- **Judgment concern:** the decision is materially ungrounded or internally
  inconsistent. Do not fail a different but defensible decision.
- **Inconclusive evidence:** the artifacts cannot establish what happened.
  Missing provider events are not proof that an action did not occur.
- **Evaluation defect:** the fixture, replies, author guidance, or capture
  mechanism makes the requested conclusion invalid.

## Report

State the executed matrix and artifact directory. When reviewing a batch, lead
with one row per case and host containing the `Assessment` and a one-line cited
reason; include per-run details only for rows not assessed `Supported`.

For each run, return:

- `Assessment`: `Supported`, `Material failure`, `Inconclusive`, or
  `Invalid evaluation`.
- `Findings`: material issues in priority order, each tied to evidence.
- `Reasoning`: why the behavior was or was not grounded and consistent with the
  skill contract.
- `Evaluation issues`: defects or missing evidence separate from subject
  behavior.

If more than one assessment applies, name the primary one and report the others
as findings. `Supported` means this run provides affirmative evidence for the
workflow; it does not claim universal correctness. Do not reward verbosity,
exact wording, or agreement with the author's preferred implementation.

When recording a batch under `evals/notebook`, keep the original results
immutable. Track later decisions and reruns in a finding-keyed ledger with
`Decision or change`, `Validation`, and `Status` (`Open`, `Resolved`, or
`Accepted`). Use a separate rerun table only when the follow-up is itself a
substantial matrix.
