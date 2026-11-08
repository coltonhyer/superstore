# Review instructions

This repository is prose that agents execute: skill text, the eval cases that
measure it, the library documents it produces, and the runner that drives the
evals. Failure here is a host reading a sentence, doing the wrong thing, and
believing it complied. Read the whole changed file, not only the diff; the
sentence that breaks a rule is usually not the one that changed.

A review contract supplied with the task keeps its own scope and result
format. This file adds the severity, skip, and check rules below. Under a
supplied contract, report everything it calls material as Important, along
with the classes below; a Nit is anything else and blocks nothing.

## What Important means here

Reserve Important for:

- Skill text that admits a wrong reading: a term that gates an action with no
  definition (`approved`, `reviewed`, `recorded`, `current`, `independent`);
  one situation that two sentences send to different outcomes; a step that
  claims a repository effect without naming the check that proves it, or
  without saying what its failure path leaves behind; a request word that is
  not approval (`preserve`, `save`, `commit`) left unnamed where approval is
  defined; a gate the text makes the agent re-run after the user has
  explicitly passed it, such as a second review or a second approval ask.
- Twin passages that disagree on a shared rule, and a rule removed in a
  rewrite with no new home.
- A removed or renamed name still mentioned outside a legacy section.
- An eval case that cannot measure what it claims.
- A library document, handoff note, or notebook entry that misstates history.
- A runner flag that is accepted and changes nothing.
- Runner or test code that breaks the behavior it implements, or exposes
  credentials or the host user's identity beyond the selected login.
- The plugin version rule in `AGENTS.md` broken.

Wording, tone, ordering, and Markdown style are Nit at most, unless the change
alters which sentence a reader obeys.

## Cap the nits

Report at most five Nits per review.

## Do not report

- Anything a test under `tests/` asserts. Name the test when you skip a
  finding on that ground; do not assume coverage from a test's name.
- A request to rewrite an original observation under `evals/notebook/`
  because a later repair or rerun changed the outcome; corrections belong in
  follow-ups and later rows. A count, id, or label that disagrees with the
  writeup's own tables is still a finding.
- An eval case only because its expectations allow more than one defensible
  answer. Expectations are review questions, not ground truth.
- A contract gap recorded Open in a writeup under `evals/notebook/writeups/`
  or a handoff note under `docs/handoffs/`, unless the change touches
  that passage.

## Evidence

Cite a file and line for every finding. For a claim about what an agent would
do, quote the sentence that causes it; a guess from a file name, a heading, or
a skill description is not evidence. For a claim about history, paste the
`jj log` or `jj diff` output, or the Git equivalent, that shows it.

## Always check

### Skill text (`plugins/*/skills/*/SKILL.md`, `references/`)

- For each changed sentence that decides what the agent does to the
  repository or tells the user, name the most plausible wrong reading that
  changes that outcome. Report it when no sentence in the skill rules it out,
  an ordinary request or eval prompt could produce it, and it would cross a
  gate the skill defines or is one of the kinds the first bullet of "What
  Important means here" lists. One situation that two sentences send
  to different outcomes is a finding; a sequence of steps under one trigger
  is not.
- Every step that records, commits, or deletes names its proof: a command or
  observable condition in both the Jujutsu and Git forms. "Verify that it
  entered history" is not one. A commit is claimed only when the working copy
  no longer changes the file and a new revision contains it. The step's
  failure path says what it leaves behind for everything the success path
  changes.
- Every passage with a twin still agrees with it on every shared rule: the
  approval, commit, and revise sections of `planning/specs` and
  `implementation/plans`; the recording check in `implementing-plans`, its
  `execution-state.md`, and the Finish section of `subagent-execution`; the
  execution gate in `implementing-plans` and `subagent-execution`; the plan
  template's locator and the plans skill; the Library skill's frontmatter
  table and the frontmatter that `specs`, `plans`, and `execution-state.md`
  write; the README tier lists and defaults and the skills and runner they
  describe. Name both passages.
- For each removed sentence that told the agent to do or not do something,
  name where that rule now lives or what retired it.
- When a change removes or renames a skill, field, path, or term, search
  `plugins/`, `tests/`, `README.md`, both marketplace indexes, and every
  `plugin.json` for the old name.
- A rule that restricts reading names what counts as a read (`head`, `cat`,
  `show`, `diff`) and gives the filter command that replaces it.
- Run every changed shell snippet in a scratch repository with
  `JJ_CONFIG=/dev/null JJ_EDITOR=false GIT_EDITOR=false` and stdin from
  `/dev/null`. A snippet that opens an editor, matches hyphenated slugs with
  `\b`, or needs GNU-only syntax without saying so is a finding.

### Eval cases (`plugins/*/skills/*/evals/`)

- The runner tells every subject that Jujutsu is in use and lists every
  fixture under "Attached repository files". A prompt that denies version
  control, expects discovery of a listed file, or denies a capability the
  hosts have measures nothing.
- Each expectation is observable in the retained artifacts and reachable by
  at least one defensible path. An expectation that presupposes one branch
  where the prompt leaves two is a finding.
- A fixture pair that must read as two versions differs in byte length; the
  runner keeps file times and `jj` keys its snapshot on size and time.
- Fixtures satisfy the shapes the skills demand: library documents carry the
  Library skill's frontmatter, a sample handoff note has a non-empty Result
  range, a file the case expects to be changed exists at baseline, and no
  shared fixture already performs the behavior under test.

### Documents and records (`docs/specs/`, `docs/plans/`, `docs/handoffs/`, `docs/notes/`, `evals/notebook/`)

- Frontmatter follows the Library skill, and every link path resolves except
  a `supersedes` target.
- Every `path@revision` and change id the change adds resolves:
  `jj file show -r <revision> <path>` and `jj log -r <id>`. Ids a writeup
  records as observed during a run are original observations.
- A handoff note is its own revision with no other files. Its Result range is
  `<start>..<end>` from the execution's starting revision and excludes the
  note itself.
- Every sentence the change adds or edits that states commit order, counts,
  or ids agrees with `jj log`; ids a writeup records as observed during a
  run are exempt. A `BOOK.md` row matches its writeup's results table.

### Runner, manifests, and history

- Every flag the runner accepts changes the command it builds. A change to a
  CLI pin or default model cites a live run on that pin and model, in the
  change or its writeup.
- The plugin version rule in `AGENTS.md` holds for a whole change set,
  including equal versions in both manifests. A task review before a plan's
  final task does not flag the missing bump.
- Each commit is one logical change. A fix to text introduced earlier in the
  same change set belongs in the commit that introduced it, not after the
  version bump.

## Skill text quality

For a change to skill text, read each changed skill against this checklist and
report its findings as Nits, within the cap of five. This section sits outside
the two sections that `AGENTS.md` ties to recorded failures, because its items
come from agentskills.io.

The scope is the skill's `SKILL.md` and each file that `SKILL.md` links, except
`okf-spec.md` and `okf-LICENSE.md`, which are vendored and never edited. Ask
each item of every passage in scope. Each item cites the agentskills.io page
and section it comes from.

- **Earns its place.** Would the agent get this wrong without it? If not, cut
  it; if unsure, mark it "test it". Source: Best practices, "Add what the
  agent lacks, omit what it knows".
- **Moderate detail.** Leave edge cases the agent's judgment handles to it.
  Source: Best practices, "Aim for moderate detail".
- **Coherent unit.** The skill does one job, needs no other skill for its
  core task, and covers no second job. Source: Best practices, "Design
  coherent units".
- **When to load.** Each reference link says when to read it, and references
  are one level deep. Source: Best practices, "Structure large skills with
  progressive disclosure"; Specification, "File references".
- **Specificity matches fragility.** Give exact commands where an operation is
  fragile; elsewhere give the reason, not rigid steps. Source: Best
  practices, "Match specificity to fragility".
- **Defaults, not menus.** One default, with alternatives named briefly.
  Source: Best practices, "Provide defaults, not menus".
- **Procedure, not answer.** Teach a method for the class of task, not one
  instance's answer. Source: Best practices, "Favor procedures over
  declarations".
- **Gotchas up front.** Corrections to mistakes the agent would otherwise make
  sit in `SKILL.md`, before the step they affect. Source: Best practices,
  "Gotchas sections".
- **Template for output.** Output with a required shape has a template, not a
  prose description. Source: Best practices, "Templates for output format".
- **Checkable gates.** Multi-step work with gates has a checklist or a
  validation step. Source: Best practices, "Checklists for multi-step
  workflows"; "Validation loops"; "Plan-validate-execute".
- **Script candidate.** Flag a command the agent must rebuild or adapt on
  every run. Source: Best practices, "Bundling reusable scripts".
- **Specific, not generic.** No advice every agent already follows, such as
  "handle errors appropriately". Source: Best practices, "Start from real
  expertise".
- **Description.** It says what the skill does and when to use it, in terms of
  what the user wants, in a few sentences. Source: Specification,
  "`description` field"; Optimizing skill descriptions, "Writing effective
  descriptions".

Pages: `https://agentskills.io/skill-creation/best-practices`,
`https://agentskills.io/specification`,
`https://agentskills.io/skill-creation/optimizing-descriptions`.

- Leave out what a test or rumdl enforces, such as the 240-line limit
  (`test_skill_files_fit_one_codex_read`) and links that resolve.
- Report each finding as one line:
  `<file>:<line> | <item> | "<quoted text>" | <change>`. Name the change in a
  few words, such as cut, move to a reference with a when-to-load line, pick a
  default, or test it.
- Findings are advisory and block nothing. When the same text is also one of
  the Important classes above, those rules apply to it.
- Asked on demand to review a skill against this checklist, list every
  finding.

## Summary

Start with the count of Important findings, then the count of Nits. When
there is nothing to fix, say so in one line.
