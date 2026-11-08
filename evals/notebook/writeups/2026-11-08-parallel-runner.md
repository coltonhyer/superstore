# Parallel runner library run — 2026-11-08

This writeup records one run of the existing library suite with the parallel
eval runner (`scripts/run_skill_evals.py`, from the skill checks change). It
measures the runner, not the skills. The run is not graded: no case was
reviewed, and it has no Supported, Material failure, or Inconclusive counts.
The specification is `docs/specs/skill-checks.md` and the plan is
`docs/plans/skill-checks.md`. The run used the runner as built at revision
`qwtwnozo` and ran at revision `wrwrklmp`, on 2026-11-08.

The retained artifact root is
`.agents/eval-results/2026-11-08-parallel-runner/`, excluded from version
control. It holds `summary.json`, `run.log` (the runner's stdout and stderr),
`started.txt`, `ended.txt`, and one folder per host with a `result.json` per
case.

## Run

```sh
python3 scripts/run_skill_evals.py --plugin plugins/library --host claude --host codex --host agy --output .agents/eval-results/2026-11-08-parallel-runner
```

Subjects (the runner defaults): `claude-sonnet-5`, `gpt-5.6-terra`, and
`gemini-3.8-flash-high`, each at high effort.

| Host | Cases | Captured | Errors | Login refreshed |
| --- | --- | --- | --- | --- |
| claude | 10 | 10 | 0 | none |
| codex | 10 | 10 | 0 | none |
| agy | 10 | 10 | 0 | library/1 |
| Total | 30 | 30 | 0 | 1 |

Wall time: 162.4 s (`summary.json` `wall_seconds`; `started.txt` to
`ended.txt` is 04:42:11Z to 04:44:55Z, 164 s). The runner exited 0 and
printed `Captured 30, errors 0, wall 162s`.

## Concurrency

Hosts ran side by side, all three starting at 04:42:12Z. Within each host the
first case (`library/1`) ran alone, then the rest ran up to four at a time.
Peak cases running at once, from the
order of `Running` and `CAPTURED` lines in `run.log`:

| Host | Ran at once | Peak at once | Drop to one case at a time |
| --- | --- | --- | --- |
| claude | yes | 4 | none |
| codex | yes | 4 | none |
| agy | yes | 4 | none |

`run.log` has no line or warning about a host dropping to one case at a time.
Only agy's `library/1` refreshed its login.

## Comparison

The latest one-at-a-time library runs, on 2026-11-07, kept no timing, so no
measured time exists to compare against. The comparison is what one at a time
would take: the sum of this run's own case durations (`duration_seconds` of
each turn in each `result.json`).

| Host | Sum of case durations | Longest case |
| --- | --- | --- |
| claude | 165.6 s | 25.5 s |
| codex | 218.9 s | 37.0 s |
| agy | 496.1 s | 102.1 s |
| All hosts | 880.6 s (14 min 41 s) | 102.1 s |

One at a time across hosts would have taken about 880.6 s against 162.4 s
observed, roughly 5.4 times as long. This is an estimate: the durations were
measured under concurrent load, and one at a time would also add a login
refresh per host.
