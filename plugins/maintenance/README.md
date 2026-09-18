# Maintenance

Establish lean coding standards for production code, tests, and supporting
scripts through repository inspection, research, and user decisions. Review
repositories against those standards and report violations with evidence.

## Install

### Codex

```sh
codex plugin add maintenance@superstore
```

### Claude Code

```sh
claude plugin install maintenance@superstore --scope user
```

### Antigravity

```sh
agy plugin install https://github.com/coltonhyer/superstore/tree/main/plugins/maintenance
```

No build step or runtime dependency is required. The host supplies repository
read/write and research capabilities; no other plugin is required.

## Use

Ask your agent to *"Set up coding standards for this repository"* or
*"Refine our existing coding standards."*

For a standards audit, ask *"Audit this repository against its coding standards
and save a violations report without remediation advice."* A named directory is
also valid scope. Diff, PR, and ordinary change reviews use other workflows.

## Skills

| Skill | What it is for |
| --- | --- |
| [`setting-up-coding-standards`](skills/setting-up-coding-standards/SKILL.md) | Inspect practices, research suitable guidance, agree on rules, and write approved standards with discovery references. |
| [`reviewing-coding-standards`](skills/reviewing-coding-standards/SKILL.md) | Audit established rules across a repository or named directory and save evidence-backed violations without proposing fixes. |

## Workflow and output

The skill reports explicit rules, mechanically enforced rules, and inferred
conventions separately. When standards exist, choose refinement or a fresh
start; without them, it starts fresh. Refinement preserves settled choices.
A fresh start carries existing rules forward only by agreement and discusses
one topic at a time.

Research must fit the repository's product, language versions, and tooling.
Missing or stale evidence is disclosed for a source or user decision; inferred
conventions and external guides do not become binding without agreement.

Before any target-file edits, the skill prepares drafts and previews all rules,
files, migrations, and discovery references. One explicit approval of that
complete proposal authorizes the writes; topic decisions alone do not.

The generated layout is a short `docs/standards/README.md` index with focused
topic files directly beside it. The index defines applicability, obligation
words, and precedence. Rules have stable IDs, descriptive headings, and explicit
anchors for findings such as `tests.md#test-001`. Topic filenames depend on the
agreed standards. See the private [output format](skills/setting-up-coding-standards/references/output-format.md)
and [research guidance](skills/setting-up-coding-standards/references/research.md).

After approval, the skill migrates superseded guidance while preserving
unrelated content, connects root `AGENTS.md` and relevant host entry points,
and links the index from `CONTRIBUTING.md` or root `README.md`. It verifies
replacement content and links before reporting completion.

Setup changes documentation only. It does not make code compliant, configure
tools, produce a cleanup audit, or commit, archive, push, or publish standards.

## Review output

The audit requires the canonical `docs/standards/README.md` index with obligation
words and precedence; an invalid prerequisite blocks without writing a report.
It inspects statically by default. Only exact, relevant configured checks may run
after explicit approval, never tests or migrations.

The skill writes a Markdown report to the requested or established location,
defaulting to `docs/reviews/coding-standards-YYYY-MM-DD.md` with a collision
suffix rather than overwriting. It separates mandatory-rule errors,
recommendation warnings, and unresolved assessments; records every confirmed
occurrence, scoped exception reasoning, commands, unassessed delegated rules,
side effects, and coverage limits. Findings cite rule IDs, source links, exact
locations, and evidence. Only canonically applicable rules and explicitly
adopted external baselines apply. The report contains no remediation advice and
can be used as input to a fresh requirements workflow; the audit does not start
that workflow.

## Validation

Structural checks run without invoking an agent:

```sh
python3 -m unittest discover -s tests
python3 scripts/run_skill_evals.py --plugin plugins/maintenance --list
```

The unittest suite prepares all 16 cases, checks copied fixtures and private
links, and validates prompt construction. Case IDs are stable; turns include
the initial request and every fixed reply.

| ID | Purpose | Turns |
| --- | --- | --- |
| 1 | Fresh Python setup; no explicit standards or redundant mode question | 3 |
| 2 | Refine scattered/mixed guidance; preserve IDs, content, old links and Claude import | 3 |
| 3 | Existing guidance; report before choosing fresh | 4 |
| 4 | Fresh mode already chosen; no repeated mode question | 3 |
| 5 | Python/JavaScript production, tests, scripts; deferred tooling change | 5 |
| 6 | Explicit scoped baseline; local/config/baseline precedence | 3 |
| 7 | Full draft on request, correction, approval of latest proposal | 4 |
| 8 | Withheld approval; no target writes | 2 |
| 9 | Repeated setup; title/file moves, retired IDs, pointer deduplication | 3 |
| 10 | Unavailable research; disclose and defer | 2 |
| 11 | Resume supplied partial migration under unchanged prior approval | 1 |
| 12 | Current content differs from approved preview; revised approval withheld | 2 |
| 13 | Implementation using split topic documents | 1 |
| 14 | Same implementation and rules in one document | 1 |
| 15 | Review using split topic documents | 1 |
| 16 | Same review and rules in one document | 1 |

The implementation comparison is **13 vs 14**; the review comparison is
**15 vs 16**. Each pair has identical code tasks, agreed rule bodies, source
notes, and discovery entry points. Only standards layout/navigation differs.
The single-document comparison deliberately combines the same topic bodies in
its index; it is a usability control, not a setup-output format recommendation.
Guided usage cases preload the setup skill and enumerate fixture paths; they
establish standards usability, not native host discovery. Separate native
sessions exercise ordinary host loading against actual generated standards.
See the [evaluation writeup](../../evals/notebook/writeups/2026-09-18-maintenance-coding-standards.md)
for observed coverage and limitations.

Short attributed research summaries are supplied in `evidence/sources.md` in
relevant workspaces, with original URLs and retrieval context. They cover only
the named sections, require no live provider, and do not constitute adoption of
a guide. Case 10 deliberately has no research evidence. Case 11 starts from
explicit prior-operation facts and partially written files; it does **not**
inject a real filesystem failure. Case 12 supplies prior-preview facts plus a
current working edit; it does **not** mutate files between turns.

Live evaluations are manual release checks. Use the
[shared runner](../../scripts/run_skill_evals.py) and
[shared evaluation guidance](../planning/README.md#validation) for authorized
case/host selection, model settings, execution, and evidence handling. The
[evaluation notebook](../../evals/notebook/BOOK.md) records reviewed outcomes;
listing and offline preparation alone establish no behavioral result.
