---
type: handoff
title: "OKF documents execution"
description: "Moved Superstore's documents into docs/ as OKF documents, made the library skill the OKF encoder, and put Planning and Implementation on stable approval with a verified field, in the range xknlouww..qwsxtkrk."
tags: [library, open-knowledge-format, agent-skills, planning-plugin, implementation-planning]
implements: docs/plans/okf-documents.md
---

# OKF documents execution

- **Plan:** `.agents/library/plans/okf-documents.md@xknlouww`
- **Spec:** `.agents/library/specs/okf-documents.md@xknlouww`, the final approved text, which `lptmrtkx` moves to `docs/specs/okf-documents.md`
- **Start:** `xknlouww` **Result:** `xknlouww..qwsxtkrk`

## Whole-change checks

- `python3 -m unittest discover -s tests`: 42 tests OK at `qwsxtkrk`, including `test_skill_files_fit_one_codex_read`, which holds every plugin `SKILL.md` within 240 lines (largest: library, 239).
- Whole-change review 1, at the strongest tier, before the repairs: 1 Important (W-R1, frontmatter filters matched lines in document bodies), 2 Minor (W-R2, W-R3), 1 Nit. Verification 1 found the same defect (W-V1) and passed every other check.
- Whole-change review 2, at the strongest tier, on the repaired text and the revised spec: 0 Important, 3 Nits.
- Whole-change verification 2: every unit test and static check passed. Its gaps are under Limitations.
- Static checks: the only `.agents/library` hits are migration notes. Every link resolves inside its plugin. Versions are Library 0.3.0, Planning 0.4.0, and Implementation 0.4.0, equal in both manifests.
- Migration: 15 documents moved into `docs/` with bodies byte-identical to their originals. The OKF documents spec's body has since changed through its own revisions.
- Evals: 183 original runs (165 Supported, 16 material failures, 2 Inconclusive), plus 127 follow-up runs of the library suite and requirements/4.
  - On the final library text: codex 16 of 16 Supported, agy 10 of 10 Supported, and claude 9 of 10 Supported, two of those with judgment concerns. Claude's library/5 was a Material failure, which is F12, still Open.
  - Details are in `evals/notebook/writeups/2026-11-02-okf-documents.md`.

## Review outcomes and dispositions

### Task reviews

| Task | Outcome |
| --- | --- |
| T1 | No material findings. Supervisor finding S1 (the attribution line was dictated by the brief) Addressed. |
| T2 | T2-R1 to T2-R6, S2 to S6, and T2-F1 Addressed; the fix review found all resolved. |
| T3 | T3-R1 to T3-R7, S7, S8, and T3-F1 to T3-F3 Addressed. |
| T4 | T4-R1 and T4-R2 Addressed. T4-R3 Dismissed for this change because it predates it; see Limitations. |
| T5 | T5-R1 to T5-R3 and T5-F1 Addressed by the identity rework under Tactical decisions. |
| T6 | No material findings. |
| T7 | No material findings. |
| T8 | T8-R1 to T8-R6 Addressed; three style notes Dismissed. |
| T9 | No material findings. |

### Whole-change review 1 (W-R1 to W-R3)

- W-R1 was Addressed with a frontmatter-only extractor, the user's decision on 2026-11-06.
- W-R2 was Addressed. The user kept the exception for a `supersedes` target without a `type` line and aligned the wording.
- W-R3 was Addressed with the reworded handoff title rule, the user's "Fix now".

### Fix-range reviews of repairs 1 to 3

- F2-1 (empty files), F2-2 (symlinked folders), and F2-3 (stale descriptions) were Addressed.
- Nits 1, 2, 3, and 5 were applied. Nit 4 (frontmatter with no closing `---`) was accepted as malformed input.

### Spec revision reviews

- **First revision:** SR1 to SR5 were Addressed. R1 asked to confirm the handoff title wording, and the user approved it with the spec.
- **Second revision:** findings 1, 3, and 4 were Addressed. On finding 2, the user decided on the 240-line limit, now enforced by a test.

### Follow-up evals

- **F11:** codex skipped the Write rules. It was Addressed by a self-contained Write folder check and by fitting `SKILL.md` in 240 lines.
- **Fix review of that repair:**
  - I1, a Find step 1 sentence that would also stop an agent reading a file a user attached on purpose, was Addressed by removing the sentence.
  - I2, a wrong run count in a description, was Addressed.
  - Two wording nits were applied.
- **Fix review of the 240-line cut:**
  - F1, the spec's description of the skill's layout, was Addressed by the second spec revision.
  - N1, the README upgrade wording, was Addressed.
  - N2, naming working-copy comparisons in the when-to-load sentence, was Dismissed as low risk.
  - N3, fixes landing after the version bump, was Addressed by folding them into `wmupovrm`, the user's decision.

### Whole-change review 2 (W2-R1 to W2-R3)

- W2-R2 was Addressed in the Write check.
- W2-R1 is under Limitations.
- W2-R3 is a cosmetic follow-up: the root README's Library row omits handoff notes, and the Codex `defaultPrompt` says "library document".

## Limitations

### Open findings

- **F12 is Open.** Claude sometimes opens files the eval prompt lists as attached, instead of filtering first. In library/5 it opened the deprecated spec in 1 of 4 runs at the first repaired text and 1 of 1 at the final text, and in 0 of 3 runs at an intermediate text that had a sentence saying attached files still go through the filter. It also happened once in library/8, and every answer was correct. That sentence was withdrawn because it would also stop an agent from reading a file a user attaches on purpose. A net-zero-line rewording of Find step 1 is proposed for a later change.
- **F8, the handoff title rule, has no eval validation.** The user dropped the seven planned reruns.

### Gaps carried to later specs

- **T4-R3:** the execution gate accepts an uncommitted `stable` plan. This predates the change.
- **W2-R1:** a `type: spec` file whose status is outside OKF's three values is named by neither clause of the plans gate. The spec words it the same way.

### Tool coverage

- Only mawk was available to test the `awk` commands. BSD and macOS `awk` were not run.
- `find -maxdepth` is not POSIX, though GNU, BSD, macOS, busybox, and bfs support it.

### Revision citations

- This note and the plan cite revisions, as the current rules require. GitHub issue #8 tracks how history curation orphans such citations.
- The folds of 2026-11-07 already orphaned the commit ids the follow-up eval records observed. The writeup therefore identifies tested text by SHA-256.

### Verification gaps

- The upstream OKF files were not refetched; only the pinned checksums were checked.
- The migration check "no document carries `verified`" no longer holds for the OKF documents spec, which now carries its own approval.

## Tactical decisions

### Execution

- The execution id is `okf-documents-pkqymxxw`, named for the plan's approval revision at the start. That revision was later squashed into `xknlouww`, and the id keeps its original name. Workers end commit messages with their own session's attribution line, adopted after S1 on T1.

### Document rules

- **S7:** a `supersedes` target without a `type` line is left unchanged and reported, not deprecated.
- **T2-R4:** a file that is not yet migrated is reported and never selected as current.
- **W-R1 (2026-11-06):** a POSIX `awk` frontmatter extractor piped into `grep`, given as a rule plus one portable example. Python and Node ship no YAML parser in their standard libraries; a parser the environment already has is allowed.

### Eval runner and runs

- **T5:** the eval container gets the Jujutsu identity from `JJ_USER` and `JJ_EMAIL`, and host-side calls use `--config`. The spec's "Jujutsu repository config" cannot work because jj 0.44 stores per-repository config under the user's config folder, which the container, with `HOME=/state`, does not see. The purpose is the same. The 164 stray `~/.config/jj/repos/<id>` folders the tests created were deleted.
- **T8:** each suite gets its own output root, because every runner process writes `summary.json` at its root.
- **Follow-up runs (2026-11-07):** the seven handoff-title reruns were dropped. The runs fix only what breaks and record the rest.

### Skill size and history (2026-11-07)

- The library `SKILL.md` was cut to 239 lines: the Pin and compare commands moved to `references/pin-and-compare.md`, the spec example was removed, and the construction notes moved to the README. Codex reads a skill 240 lines at a time.
- Every plugin `SKILL.md` stays within 240 lines, enforced by a unit test. The user's decision was "whatever codex allows".
- History was folded at the user's request:
  - three review-fix commits went into their task commits;
  - the two follow-up library fixes went into `wmupovrm`, under REVIEW.md;
  - the 240-line test went into `wmupovrm`;
  - the plan approval `pkqymxxw`, both spec revisions, and their approvals went into `xknlouww`, which now holds the final spec and the plan.

### Follow-ups

The GitHub project Superstore tracks the follow-ups:

- **Spec B:** requirements documents, decision documents, and dated file names.
- **Skill checks:** a review file, rumdl, Vale, command tests, parallel eval runs, baseline runs, and the 240-line rule.
- **The rest:** small-model runs, the execution gate, Rosetta, and issue #8.
