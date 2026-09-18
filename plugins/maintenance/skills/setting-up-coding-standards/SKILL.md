---
name: setting-up-coding-standards
description: Use when establishing or refining repository coding standards through inspection, research, and user decisions, then writing approved guidance and discovery references.
---

# Setting Up Coding Standards

Establish lean standards for the repository's production code, tests, and
supporting scripts, including their organization. Use the host's available
repository and research capabilities; no other plugin is required.

This workflow writes documentation only. Do not change code, configure or
install tools, produce a cleanup audit, alter global settings, or commit,
archive, push, or publish the target repository's standards.

## Inspect and report

Read repository guidance, manifests, tooling configuration and commands, layout,
and representative code, tests, and scripts. Identify the product, languages and
relevant versions, frameworks, and current standards, including any existing
`docs/standards/`. Use discoverable facts without asking the user to repeat them.
Keep inspection read-only: inspect code, configuration, and commands without
executing repository code, tests, linters, or formatters. Report configured
checks without implying they were run or passed.

Always show a concise findings report before discussing the mode. Include the
repository profile, inspected evidence, coverage limits, and these distinctions:

- **Explicit:** existing rules and their source paths.
- **Enforced:** mechanical rules supported by actual tool configuration and
  commands; distinguish configured checks from evidence that they run.
- **Inferred:** recurring conventions with representative locations, uncertainty,
  and inconsistencies. Inference is proposal evidence, not a binding standard.

Report missing categories and absent explicit standards; do not imply exhaustive
inspection. When explicit standards exist, ask whether to refine them or start
fresh, unless the user already chose; acknowledge that choice after the report.
Without explicit standards, proceed fresh without a mode question.

Refinement starts from existing standards and focuses on requested changes.
A fresh start carries no existing coding rule forward without agreement. Both
modes preserve unrelated instructions and content. If an existing rule is agreed
again with unchanged meaning in fresh mode, retain its valid ID even when its
topic, title, or location changes; fresh mode does not reset rule identity.

## Research and decide

Propose a short list of relevant topics before researching; let the user adjust
it as discussion proceeds. Organization, readability, interfaces, errors, tests,
scripts, documentation, and formatting are considerations, not required topics.
Cover production code, tests, and scripts where applicable; record absences
instead of creating speculative rules or empty files.

Read [research guidance](references/research.md) when gathering evidence. Check
product, language/version, and tooling fit. Explain which proposals existing
linters actually check and which require judgment. Disclose missing evidence
and obtain a source or user decision for affected recommendations.

For a fresh start, work one topic at a time: present concrete proposals and
concise reasons, then ask a focused question to accept or adjust them. For
refinement, use the findings and requested changes to propose improvements
without re-eliciting settled preferences. Research and inferred conventions
inform decisions; they do not silently adopt rules.

Resolve contradictory proposals. Read [the output format](references/output-format.md)
when shaping the agreed rules, baseline adoption, precedence, stable IDs, and
tool references. If a deliberate local rule conflicts with current tooling,
agree whether it applies now or after follow-up and retain that decision beside
the rule. Leave configuration unchanged.

## Prepare the approval proposal

Prepare complete drafts outside the target repository before requesting final
approval; do not create, modify, or remove target files yet. Inspect incoming
references to old guidance, mixed-purpose files, human entry points, and agent
instructions for hosts in use (including the current host) or explicitly
targeted. Plan their migration alongside the canonical `docs/standards/README.md`
and flat topic files.

Before showing the preview, review draft standards against the output boundary:
retain future repository obligations and persistent context; remove setup-only
constraints and history. Show one concise preview covering:

- Selected rules by topic, consequential decisions, any adopted baseline's
  scope/reference and local exceptions, and the agreed precedence.
- Changes from existing rules, including deliberately discarded rules and
  remaining tooling gaps with their effective timing.
- Every file to create, update, relocate, or remove; treatment of old paths and
  incoming references; preservation of unrelated content.
- Agent and human discovery-reference changes described below.

Make exact full content available on request without printing it all by default.
Topic decisions do not authorize writes. One explicit approval of this complete
proposal authorizes the described documentation and migration. Incorporate
corrections; a materially changed proposal needs renewed approval.

## Write, migrate, and connect discovery

After approval, recheck affected content before any canonical, migration, or
discovery writes. Material changes since the preview require reconciliation and
renewed approval before any of those writes.

1. Write the canonical standards first and verify the agreed replacement.
2. Update incoming references and migrate superseded guidance. In mixed-purpose
   files, replace only superseded standards sections with a reference. Remove a
   standards-only copy only after verifying its replacement; keep a short
   redirect when the old path must remain discoverable. Migrate existing
   standards to the same flat canonical layout in either mode.
3. Add or update one root `AGENTS.md` pointer to `docs/standards/README.md`,
   creating the file if absent. Instruct agents to read the index and applicable
   standards before writing or reviewing code; preserve other instructions.
4. Make that pointer reachable for hosts in use or explicitly targeted. Reuse
   existing imports or symlinks. For targeted Claude Code, use its existing
   `CLAUDE.md` entry point to import shared `AGENTS.md`, resolving the import
   relative to that file; create the entry point if absent. Check overriding
   instructions or host files that bypass the shared guidance. Do not populate
   unused hosts or change personal/global settings.
5. Add one human reference in existing `CONTRIBUTING.md`, otherwise root
   `README.md`; create a minimal root README if neither exists. Resolve links
   relative to the containing file. Entry points link to standards, not copies.

If writing or migration fails, preserve recoverable content, report exact files
written and steps still pending, and do not claim completion. On resumption,
inspect the actual partial result against the approved proposal before continuing;
recheck replacements before removing old content and seek renewed approval only
when the proposal materially changes. Use ordinary edits, not a migration system.

## Verify and report

Read back the resulting files against the same output boundary. Check agreed
rules, unique stable IDs and anchors, retained IDs for unchanged rules in either
mode, brief retired-ID notes in the canonical index, index links and
applicability, baseline/precedence,
tool-conflict timing, discovery references, incoming links, and migration
outcomes. Confirm unrelated content survived and host overrides do not bypass
the pointer.

Report the canonical index path, written/migrated files, and unresolved issues
concisely. Completion requires the approved documentation and references in
place, not existing code's compliance with the new standards.
