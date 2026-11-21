# Review loop, fallbacks, and finding dispositions

This reference defines the shared review loop, independent-review gate rules,
reviewer-failure fallbacks, and checkable finding dispositions across all
`delivery` review gates: spec, plan, task, and whole-change reviews.

## Core definitions

- **`usable` output:** Structured findings matching the gate's contract or an
  explicit no-material-findings result returned by a reviewer. Tool or agent
  status metadata without contract text is not usable output.
- **`independent` review:** Usable contract output received and read from a
  distinct launched reviewer — never a self-review fallback. A launched
  reviewer that is still running has not failed; wait for it to finish or fail
  before deciding it returned no usable output.
- **`Blocking` finding:** A correctness defect, requirement or scope gap, false
  code claim, consumer breakage, hollow guarantee, or contract/gate defect.
- **`Non-blocking` finding:** Minor polish or an optional improvement that does
  not break correctness, requirements, scope, consumers, or contracts.
- **`clean` round:** A round in which every reviewer at the gate produces no
  blocking edits and no `Elevated` finding remains unresolved. A `Blocking`
  finding `Dismissed` with checkable evidence produces no edit and does not
  force another round, and `Non-blocking` findings do not prevent a round
  from being clean.

## Reviewer-failure fallbacks

| Mode and host capability | Trigger | Fallback action | Cap and escalation |
| --- | --- | --- | --- |
| Interactive, without subagent creation | Gate requires review | Use disclosed self-review across rounds of the gate | Bounded by the 3-round cap, step-back final round, and escalation rules |
| Interactive, with subagent creation | Any reviewer at a single- or multi-reviewer gate fails or returns unusable output | Do not retry the failed dispatch; fall back once per gate to a disclosed self-review for each missing role | If the fallback cannot complete, or any later round fails after the one-time fallback is spent, halt and escalate to the user |
| Autonomous mode | Independent reviewer is unavailable, fails, or returns unusable output | Halt immediately; never fall back to author self-review and never promote a spec or plan to `stable` | Escalate to the user and report the halt |

A self-review fallback must always be disclosed to the user as self-review and
never reported as an independent review.

## Shared review loop

1. **Fresh reviewer context:** Every reviewer starts with fresh context and no
   parent conversation history. On hosts exposing a history-forking control,
   the caller explicitly disables parent history (for example,
   `fork_turns: "none"`).
2. **Severity and defect class:** Every reviewer tags each finding `Blocking`
   or `Non-blocking`, and names both a one-line defect class and the specific
   instance. Addressing a finding must fix every instance of that class across
   the artifact or change under review.
3. **Out-of-scope additions:** Reviewers that receive approved requirements or
   intent classify any addition beyond those requirements as:
   - *serves the ask*: non-behavior-changing support work (such as tests,
     documentation, or internal structure directly serving the ask) — the
     managing agent may keep it.
   - *unnecessary* or *conflicts*: additions that do not serve the ask or
     conflict with requirements — the managing agent removes them without
     escalating.
   Any addition that changes observable behavior or delivered scope still
   requires explicit user intent (or `Decisions for review` in autonomous mode).
4. **Round scoping:**
   - **Rounds 1 and 2:** Review the full artifact or change.
   - **Round 3 onward (except a full-artifact or full-change final round after
     a step-back redesign in step 6):** Provide the diff since the prior round,
     prior findings and their dispositions, and defect classes already fixed.
     Scope the review to checking that diff, newly introduced regressions, and
     whether each fix resolved its defect class. Allow targeted reads only within
     each reviewer's permitted scope to verify class-wide fixes or code claims
     (for example, a reviewer restricted to spec or reference documents must not
     read repository implementation code).
5. **Clean-round advancement:** A round is clean only when every reviewer at
   the gate produces no blocking edits and no `Elevated` finding remains
   unresolved. At a multi-reviewer gate, any blocking edit from any reviewer
   re-runs all reviewers for that gate. A `Blocking` finding `Dismissed`
   with checkable evidence produces no edit and does not force another
   round. An `Elevated` finding blocks gate progression until answered by
   the user (or conservatively resolved in autonomous mode), and any
   resulting edit re-runs the gate's reviewers. `Non-blocking` findings are
   recorded without forcing another round.
6. **Round 3 cap and step-back final round:** If round 3 still does not finish
   clean, stop ordinary rounds. Step back to reconsider the approach (whether
   scope grew beyond requirements or a recurring defect class signals a design
   flaw), apply any redesign, and run one final round — diff-only for targeted
   edits, or full artifact or change when a redesign was applied.
7. **Post-final-round gate:** After the final round, record remaining
   `Non-blocking` findings. If the final round does not finish clean — that
   is, any `Blocking` finding is not `Dismissed` with checkable evidence
   (including any finding that would require a blocking edit or remains
   `Elevated`) — do not apply an unreviewed fix or run another round; halt
   progression at that gate and escalate to the user, including halting
   autonomous mode rather than promoting to `stable`.

## Checkable finding dispositions

The managing agent — never the reviewer — assigns every finding one disposition
in the conversation or execution/review report, never inside the spec or plan
itself:

- **`Addressed`:** The finding holds and is fixed. Mandatory for valid
  `Blocking` findings; optional for `Non-blocking` findings (optional code
  edits still require fresh verification and recording). Required record: where
  the artifact or code changed and how the defect class was resolved.
- **`Elevated`:** Resolution requires user intent or depends on facts outside
  every file the reviewer could read. Required record: the open question for
  the user. Blocks interactive approval (or resolves conservatively in
  autonomous mode).
- **`Dismissed`:** The finding is wrong based on checkable evidence the
  reviewer could have read (a specific file and symbol, or a decision recorded
  in the artifact). Required record: the exact checkable evidence. *"This was
  intentional"* is never valid, and a fresh reader's inability to follow a spec
  or plan is never dismissed.
- **`Declined`:** Allowed for `Non-blocking` findings only — true but minor
  (never allowed for blocking correctness, requirement, or contract defects).
  Required record: a short rationale, recorded without editing and without
  triggering another review round.

Never add prose to a spec or plan solely to satisfy a reviewer when a human
reader does not need it.
