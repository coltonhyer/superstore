---
title: Planning Plugin Implementation Plan
status: approved
topics: [agent-skills, marketplace, planning-plugin, requirements, specifications]
implements: specs/planning-plugin.md
---

# Planning Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an installable Planning marketplace plugin that gathers approved requirements and writes independently reviewed specifications.

**Architecture:** Planning is a documentation-only plugin. Its two public Agent Skills contain the workflows, private reference files contain the spec template and reviewer contract, and declarative JSON evals describe observable behavior without adding a custom runner. Existing Python marketplace tests validate packaging and JSON structure.

**Tech Stack:** Agent Skills in Markdown, JSON plugin manifests and eval cases, Python standard-library unittest, Jujutsu.

**Spec:** docs/specs/planning-plugin.md

## Global Constraints

- Expose exactly two public skills: requirements and specs.
- Add no scripts, commands, persistent state, dedicated agents, runtime dependencies, or custom eval runner.
- Treat Library as optional and detect its skills from the active skill inventory.
- Inspect repository facts before questioning; load archived content only when history is plausibly relevant.
- Keep model selection capability-based. Do not name a vendor model or assume host-specific controls.
- Require explicit user approval of both the requirements summary and final spec.
- Preserve the existing user-owned changes in README.md and plugins/library/README.md. Never include the Library README in an implementation commit.
- Use Jujutsu, not Git, for every history operation.

## File Map

| File | Responsibility |
| --- | --- |
| plugins/planning/skills/requirements/SKILL.md | Requirements-gathering conversation and approval gate. |
| plugins/planning/skills/requirements/evals/evals.json | Portable behavioral cases for requirements gathering. |
| plugins/planning/skills/requirements/evals/files/project.toml | Sentinel repository fact used to verify inspection. |
| plugins/planning/skills/specs/SKILL.md | Spec drafting, review, approval, and preservation workflow. |
| plugins/planning/skills/specs/references/spec-template.md | Default required and conditional spec sections. |
| plugins/planning/skills/specs/references/spec-review.md | Read-only reviewer input, scope, and output contract. |
| plugins/planning/skills/specs/evals/evals.json | Portable behavioral cases for spec creation and review. |
| plugins/planning/skills/specs/evals/files/repository-template.md | Fixture for repository-template precedence. |
| plugins/planning/skills/specs/evals/files/flawed-spec.md | Fixture containing material review defects and dense prose. |
| plugins/planning/.codex-plugin/plugin.json | Codex plugin manifest. |
| plugins/planning/.claude-plugin/plugin.json | Claude Code plugin manifest. |
| plugins/planning/plugin.json | Antigravity plugin manifest. |
| plugins/planning/README.md | Installation, usage, skills, workflow, and Library integration. |
| .agents/plugins/marketplace.json | Codex marketplace listing. |
| .claude-plugin/marketplace.json | Claude Code marketplace listing. |
| README.md | Root marketplace table entry linking to Planning documentation. |
| tests/test_marketplace.py | Generic marketplace parity, packaging, and JSON checks. |

## Execution Setup

The current working-copy change contains user-owned README edits. Before Task 1,
create an empty child so implementation does not amend them:

~~~sh
jj status
jj new
jj status
jj diff -r @- --summary
~~~

Expected: the new working copy is empty; its parent contains only README.md and
plugins/library/README.md changes. Read docs/specs/planning-plugin.md before
editing.

---

### Task 1: Requirements Workflow

**Files:**

- Create: plugins/planning/skills/requirements/SKILL.md
- Create: plugins/planning/skills/requirements/evals/evals.json
- Create: plugins/planning/skills/requirements/evals/files/project.toml

**Interfaces:**

- Consumes: user-supplied context, relevant repository state, and optionally the read-archive skill.
- Produces: an approved chat summary containing goal/problem, relevant users/use cases, scope, functional and relevant quality requirements, constraints/decisions/assumptions, and a verifiable definition of done.

- [ ] **Step 1: Add the observable repository fixture**

Create project.toml with:

~~~toml
[ingestion]
max_batch_size = 7319
~~~

- [ ] **Step 2: Write the behavioral eval specification first**

Create evals.json using the repository's existing eval schema:

~~~json
{
  "skill_name": "requirements",
  "evals": [
    {
      "id": 1,
      "prompt": "Gather requirements for CSV export on the reports page. It is admin-only, exports the currently filtered rows as UTF-8, excludes scheduled exports, and is done when UI and API behavior are covered. Start from those decisions.",
      "expected_output": "Preserve every supplied decision, resolve only genuine remaining gaps, present the normalized requirements summary, and ask for approval.",
      "files": [],
      "expectations": [
        "Does not ask the user to repeat admin scope, filters, encoding, scheduling scope, or verification",
        "Uses engineering judgment for reversible implementation choices",
        "Includes in-scope and out-of-scope work",
        "Includes a verifiable definition of done",
        "Requests explicit approval",
        "Does not search an archive without a historical reason"
      ]
    },
    {
      "id": 2,
      "prompt": "Gather requirements for changing batch ingestion. Inspect the attached repository context before asking me about existing limits.",
      "expected_output": "Read project.toml, incorporate the configured maximum batch size, and do not ask the user for that discoverable fact.",
      "files": [
        "files/project.toml"
      ],
      "expectations": [
        "Reads repository context before questioning",
        "States that max_batch_size is 7319",
        "Does not ask for the existing maximum batch size",
        "Asks only about unresolved product intent"
      ]
    },
    {
      "id": 3,
      "prompt": "Keep the public response schema unchanged, but replace its status string with an object. Finish the requirements now.",
      "expected_output": "Identify the contradiction and ask one focused reconciliation question instead of claiming the requirements are complete.",
      "files": [],
      "expectations": [
        "Names the incompatible requirements",
        "Asks one focused question",
        "Does not invent a compatibility decision",
        "Does not present the requirements as approved or complete"
      ]
    },
    {
      "id": 4,
      "prompt": "Gather requirements for extending the rate limiter. This supersedes an earlier archived design.",
      "expected_output": "If read-archive is available, search compact archive metadata and load only a selected relevant document; otherwise continue without treating Library as required.",
      "files": [],
      "expectations": [
        "Checks the available skill inventory rather than plugin directories",
        "Uses metadata-first archive discovery when read-archive is available",
        "Does not broadly load archived documents",
        "Treats an unavailable Library skill or ledger as non-fatal"
      ]
    }
  ]
}
~~~

- [ ] **Step 3: Verify the eval file parses**

Run:

~~~sh
python3 -m json.tool plugins/planning/skills/requirements/evals/evals.json >/dev/null
~~~

Expected: exit 0.

- [ ] **Step 4: Write the requirements skill**

Start SKILL.md with:

~~~yaml
---
name: requirements
description: Use when a change needs its requirements gathered, clarified, normalized, and explicitly approved before specification or implementation.
---
~~~

Use direct imperative instructions and implement this exact sequence:

1. Extract known facts and decisions from all supplied context before asking anything.
2. Inspect relevant code, documentation, configuration, and repository history through the active version-control workflow. Do not ask for discoverable facts.
3. Check the active skill inventory. Use read-archive only when it is available and an earlier design or established historical decision is plausibly relevant; search metadata first and load only selected content. Treat an unavailable Library skill or ledger as non-fatal.
4. Ask one focused question at a time about genuine gaps, contradictions, scope boundaries, or success criteria.
5. Evaluate runtime, architecture, dependencies, feasibility, and technical consequences. Recommend an answer with concise trade-offs when the user must choose. Resolve established or reversible engineering choices yourself; elevate choices affecting scope, compatibility, security, operations, cost, or user priorities.
6. Propose decomposition when the request is too broad for one coherent spec. Never invent an unavailable blocking answer.
7. Stop only when scope is explicit, requirements do not conflict, behavior and constraints are unambiguous, completion is verifiable, and no blocking scope question remains.
8. Present the six-part normalized summary defined in the interface above and request explicit approval. Resume questioning after corrections. Write no file.

- [ ] **Step 5: Check the workflow against its eval contract**

Run:

~~~sh
python3 -m json.tool plugins/planning/skills/requirements/evals/evals.json >/dev/null
rg -n 'GPT|Claude|Gemini|Sonnet|Opus' plugins/planning/skills/requirements
~~~

Expected: JSON exits 0 and the model-name search prints nothing.

If trajectory evaluation is available, run all four cases. Otherwise manually
run case 2 and verify the trace reads project.toml, the summary states 7319,
and no question asks for that value.

- [ ] **Step 6: Commit the requirements workflow**

Run:

~~~sh
jj commit 'plugins/planning/skills/requirements' -m 'feat: add requirements workflow'
~~~

Expected: the completed parent contains only the requirements skill, its evals,
and its fixture.

---

### Task 2: Specification and Review Workflow

**Files:**

- Create: plugins/planning/skills/specs/SKILL.md
- Create: plugins/planning/skills/specs/references/spec-template.md
- Create: plugins/planning/skills/specs/references/spec-review.md
- Create: plugins/planning/skills/specs/evals/evals.json
- Create: plugins/planning/skills/specs/evals/files/repository-template.md
- Create: plugins/planning/skills/specs/evals/files/flawed-spec.md

**Interfaces:**

- Consumes: the approved requirements summary produced by Task 1, repository context, and optionally Library's archiving-documentation and read-archive skills.
- Produces: an approved Markdown spec under docs/specs, followed by either Library archival or a spec-only version-control commit.
- Reviewer input: approved requirements, exact draft Markdown, and only relevant repository context.
- Reviewer output: material findings with evidence, impact, a suggested resolution, and whether user intent is required.

- [ ] **Step 1: Add the two review fixtures**

Create repository-template.md:

~~~markdown
# Repository Specification Template

## Problem

## Desired outcomes

## Boundaries

## Validation
~~~

Create flawed-spec.md:

~~~markdown
# Session Rotation

## Summary

Move session handling into an omnidirectional synchronization plane so all
identity vectors converge through a unified temporal control surface.

## Requirements

- Revoke every existing session immediately after deployment.
- Existing sessions must remain valid for 24 hours after deployment.

## Verification

Write appropriate tests.
~~~

- [ ] **Step 2: Write the default template**

Create spec-template.md as concise template guidance:

~~~markdown
# [Specification title]

## Summary

State the proposed change and intended outcome.

## Context and motivation

Explain the current problem and why it matters.

## Goals and non-goals

Separate intended outcomes from explicit exclusions.

## Requirements and expected behavior

Describe observable behavior, constraints, and relevant quality requirements.

## Technical design and constraints

Include only when implementation choices materially constrain the solution.

## Alternatives and consequential decisions

Include only when the rationale has lasting value.

## Verification

Organize by test surface. Under each surface, list the behaviors it verifies.

## Open questions

Draft-only. Ask questions requiring user intent, incorporate each answer into
its canonical section, and remove this section before approval.
~~~

- [ ] **Step 3: Write the reviewer contract**

Create spec-review.md:

~~~markdown
# Specification Review

Act as a fresh, read-only reviewer. Review only the approved requirements,
exact draft Markdown, and relevant repository context supplied by the managing
agent.

Report material omissions, contradictions, ambiguous behavior or scope,
unsupported assumptions, feasibility problems, unrequested scope expansion,
and missing verification surfaces or behaviors.

Avoid pedantic style criticism. You may request simpler prose when jargon or
density makes the spec meaningfully harder for humans or agents to understand,
but only when the revision preserves meaning, context, and facts.

For each finding return:

- Finding: a concise statement of the problem.
- Evidence: the relevant requirement or spec text.
- Impact: why implementation or review would be harmed.
- Suggested resolution: the smallest adequate correction.
- Needs user intent: yes or no.

Return no finding when the draft has no material problem. Do not edit files,
approve the spec, browse an archive, or make implementation choices beyond the
review evidence.
~~~

- [ ] **Step 4: Write the behavioral eval specification**

Create evals.json:

~~~json
{
  "skill_name": "specs",
  "evals": [
    {
      "id": 1,
      "prompt": "Write a spec for adding team exports. I have not approved a requirements summary.",
      "expected_output": "Run requirements from the supplied context and wait for summary approval before drafting a spec.",
      "files": [],
      "expectations": [
        "Invokes or follows the requirements workflow",
        "Does not draft a spec before requirements approval",
        "Does not archive or commit anything"
      ]
    },
    {
      "id": 2,
      "prompt": "Use this approved summary to write the spec: admins export currently filtered team rows as UTF-8 CSV; scheduled export is out of scope; UI and API behavior must be verified.",
      "expected_output": "Write a concise default-format spec whose verification section names test surfaces before their behaviors, then review it before requesting approval.",
      "files": [],
      "expectations": [
        "Uses every required default section",
        "Omits empty conditional sections",
        "Organizes verification by UI and API surfaces followed by behaviors",
        "Runs one review before requesting approval",
        "Does not archive or commit before approval"
      ]
    },
    {
      "id": 3,
      "prompt": "Write the spec from an approved requirements summary and follow the attached repository template.",
      "expected_output": "Prefer repository-template.md over Planning's default headings while retaining all required information.",
      "files": [
        "files/repository-template.md"
      ],
      "expectations": [
        "Uses Problem, Desired outcomes, Boundaries, and Validation",
        "Does not append duplicate default sections",
        "Removes resolved open questions before approval"
      ]
    },
    {
      "id": 4,
      "prompt": "Review the attached draft against its own stated requirements, resolve what you safely can, and show the disposition ledger.",
      "expected_output": "Find the deployment contradiction, replace or request simplification of the dense summary without losing facts, reject the vague verification section, and classify every material finding.",
      "files": [
        "files/flawed-spec.md"
      ],
      "expectations": [
        "Finds the mutually exclusive session-lifetime requirements",
        "Flags verification that names no test surface or behavior",
        "Allows a concise human-readability correction without unrelated style nits",
        "Uses only Addressed, Elevated, or Dismissed dispositions",
        "Elevates the contradictory product decision"
      ]
    },
    {
      "id": 5,
      "prompt": "After I approve the reviewed spec, preserve it. Library may or may not be installed.",
      "expected_output": "Before approval perform no preservation; afterward detect archiving-documentation from the skill inventory, offer archive or keep when available, and otherwise make a spec-only version-control commit.",
      "files": [],
      "expectations": [
        "Does not infer Library installation from a directory or ledger",
        "Does not archive or commit before explicit approval",
        "Does not silently commit after an archival failure",
        "Never includes unrelated working-copy changes",
        "Reports a preserved file without claiming a commit when no supported VCS exists"
      ]
    }
  ]
}
~~~

- [ ] **Step 5: Verify the eval file parses**

Run:

~~~sh
python3 -m json.tool plugins/planning/skills/specs/evals/evals.json >/dev/null
~~~

Expected: exit 0.

- [ ] **Step 6: Write the specs skill**

Start SKILL.md with:

~~~yaml
---
name: specs
description: Use when approved requirements need to become a concise, independently reviewed specification with an explicit approval and preservation decision.
---
~~~

Use direct imperative instructions and implement this exact sequence:

1. Require an approved requirements summary. If absent, run requirements from all supplied context and resume only after approval.
2. Inspect relevant repository context, apply engineering judgment, and never silently change approved requirements.
3. Write under docs/specs, following repository naming when present and otherwise using a descriptive slug.
4. Apply template precedence: explicit user structure, repository convention, then references/spec-template.md. A higher-precedence structure may rename or combine sections but still covers the required information unless the user explicitly overrides it.
5. Keep the five default information areas required by the spec. Include technical design/constraints and alternatives/decisions only when material. Set no target length and retain no empty boilerplate. Ask open questions only while drafting, integrate each answer into its canonical section, and remove the resolved question. Never approve a spec with a blocking open question.
6. Run one automatic review unless the user opts out. Supply references/spec-review.md, the approved requirements, exact live spec, and only relevant context to one fresh read-only reviewer.
7. Use a normal capable reviewer for ordinary work and a stronger available tier with higher effort for security, migrations, public contracts, or broad architecture. Use host defaults when selection controls are unavailable. Fall back to self-review and disclose it when subagents are unavailable.
8. Judge every material finding and show a compact Addressed, Elevated, or Dismissed ledger in chat, not in the spec. Give locations for addressed items and reasons for dismissals; block approval on elevated items. Re-review only after a material scope or design change.
9. Request explicit user approval. Incorporate corrections and repeat review only when they materially change scope or design.
10. After approval, detect archiving-documentation from the active skill inventory. Honor a prior choice or ask Archive versus Keep. When archiving, give Library the exact path and follow its scan, confirmation, cleanup, and failure boundaries without making a VCS commit. Otherwise commit only the approved spec through the active repository workflow when Keep is chosen or Library is unavailable; approval authorizes that commit, so do not ask again.
11. Preserve recoverable state and report exact outcomes on archive, cleanup, VCS, or no-VCS failures. Never silently fall back from failed archival to a commit.
12. For later archived-spec review, use read-archive to retrieve the exact verified Markdown and pass that content to the reviewer; never make the reviewer browse the archive.

- [ ] **Step 7: Check the workflow against its eval contract**

Run:

~~~sh
python3 -m json.tool plugins/planning/skills/specs/evals/evals.json >/dev/null
rg -n 'GPT|Claude|Gemini|Sonnet|Opus' plugins/planning/skills/specs
~~~

Expected: JSON exits 0 and the model-name search prints nothing.

If trajectory evaluation is available, run all five cases. Otherwise manually
run case 4 and verify the reviewer identifies both material defects, permits
only a meaning-preserving readability correction, and elevates the
contradiction.

- [ ] **Step 8: Commit the specs workflow**

Run:

~~~sh
jj commit 'plugins/planning/skills/specs' -m 'feat: add specification workflow'
~~~

Expected: the completed parent contains only the specs skill, references,
evals, and fixtures.

---

### Task 3: Marketplace Packaging, Documentation, and Validation

**Files:**

- Modify: tests/test_marketplace.py:1
- Create: plugins/planning/.codex-plugin/plugin.json
- Create: plugins/planning/.claude-plugin/plugin.json
- Create: plugins/planning/plugin.json
- Create: plugins/planning/README.md
- Modify: .agents/plugins/marketplace.json
- Modify: .claude-plugin/marketplace.json
- Modify: README.md:25

**Interfaces:**

- Consumes: the complete skills from Tasks 1 and 2.
- Produces: Planning as installable plugin planning@superstore for Codex and Claude Code, plus direct repository URL installation for Antigravity.

- [ ] **Step 1: Replace the Library-specific marketplace test**

Replace tests/test_marketplace.py with:

~~~python
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CODEX_INDEX = ROOT / ".agents/plugins/marketplace.json"
CLAUDE_INDEX = ROOT / ".claude-plugin/marketplace.json"
MANIFESTS = (
    ".codex-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    "plugin.json",
)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class MarketplaceLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.codex = {
            plugin["name"]: plugin for plugin in load_json(CODEX_INDEX)["plugins"]
        }
        cls.claude = {
            plugin["name"]: plugin for plugin in load_json(CLAUDE_INDEX)["plugins"]
        }

    def test_marketplaces_agree(self):
        self.assertEqual(set(self.codex), set(self.claude))
        self.assertIn("planning", self.codex)

        for name in self.codex:
            with self.subTest(plugin=name):
                source = f"./plugins/{name}"
                self.assertEqual(self.codex[name]["source"]["path"], source)
                self.assertEqual(self.claude[name]["source"], source)

    def test_listed_plugins_are_self_contained(self):
        root_readme = (ROOT / "README.md").read_text(encoding="utf-8")

        for name in self.codex:
            plugin_root = ROOT / "plugins" / name
            with self.subTest(plugin=name):
                self.assertTrue((plugin_root / "README.md").is_file())
                self.assertTrue((plugin_root / "skills").is_dir())
                self.assertIn(f"(plugins/{name}/README.md)", root_readme)

                for relative in MANIFESTS:
                    manifest = plugin_root / relative
                    self.assertTrue(manifest.is_file(), str(manifest))
                    self.assertEqual(load_json(manifest)["name"], name)

    def test_plugin_json_files_parse(self):
        roots = (
            ROOT / ".agents/plugins",
            ROOT / ".claude-plugin",
            ROOT / "plugins",
        )
        for root in roots:
            for path in root.rglob("*.json"):
                with self.subTest(path=path.relative_to(ROOT)):
                    load_json(path)

    def test_root_is_not_a_plugin(self):
        for relative in (*MANIFESTS, "skills"):
            self.assertFalse((ROOT / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()
~~~

- [ ] **Step 2: Run the marketplace test and observe the missing listing**

Run:

~~~sh
python3 -m unittest discover -s tests -p 'test_marketplace.py' -v
~~~

Expected: FAIL because planning is not yet present in both marketplace
indexes.

- [ ] **Step 3: Add the three Planning manifests**

Create plugins/planning/.codex-plugin/plugin.json:

~~~json
{
  "name": "planning",
  "version": "0.1.0",
  "description": "Gather requirements and produce concise, reviewed specifications.",
  "author": {
    "name": "Superstore contributors"
  },
  "keywords": [
    "planning",
    "requirements",
    "specifications",
    "agent-skills"
  ],
  "skills": "./skills/",
  "interface": {
    "displayName": "Planning",
    "shortDescription": "Gather requirements and write reviewed specs",
    "longDescription": "Turn partial requests into approved requirements and concise specifications with independent review and explicit preservation.",
    "developerName": "Superstore contributors",
    "category": "Productivity",
    "capabilities": [
      "Read",
      "Write"
    ],
    "defaultPrompt": [
      "Gather the requirements for this change.",
      "Write a reviewed specification for this feature."
    ]
  }
}
~~~

Create plugins/planning/.claude-plugin/plugin.json:

~~~json
{
  "name": "planning",
  "description": "Gather requirements and produce concise, reviewed specifications.",
  "version": "0.1.0",
  "author": {
    "name": "Superstore contributors"
  }
}
~~~

Create plugins/planning/plugin.json:

~~~json
{
  "$schema": "https://antigravity.google/schemas/v1/plugin.json",
  "name": "planning",
  "description": "Gather requirements and produce concise, reviewed specifications."
}
~~~

- [ ] **Step 4: Add Planning to both marketplace indexes**

Append this object to the plugins array in .agents/plugins/marketplace.json:

~~~json
{
  "name": "planning",
  "source": {
    "source": "local",
    "path": "./plugins/planning"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Productivity"
}
~~~

Append this object to the plugins array in .claude-plugin/marketplace.json:

~~~json
{
  "name": "planning",
  "source": "./plugins/planning",
  "description": "Gather requirements and produce concise, reviewed specifications.",
  "category": "productivity"
}
~~~

- [ ] **Step 5: Write the plugin README**

Create plugins/planning/README.md with these sections and commands:

~~~~markdown
# Planning

Turn rough requests into approved requirements and concise, independently
reviewed specifications.

Planning contains two Agent Skills. requirements discovers and confirms what
done means; specs writes the approved result under docs/specs, reviews it, and
preserves it after approval. Library integration is optional.

## Install

### Codex

~~~sh
codex plugin add planning@superstore
~~~

### Claude Code

~~~sh
claude plugin install planning@superstore --scope user
~~~

### Antigravity

~~~sh
agy plugin install https://github.com/coltonhyer/superstore/tree/main/plugins/planning
~~~

No build step or runtime dependency is required.

## Use

- Requirements — “Gather the requirements for this change.”
- Specification — “Write a spec for this feature.”

You may provide partial or complete requirements up front. The workflow starts
from that context instead of asking you to repeat it.

## Skills

| Skill | What it is for |
| --- | --- |
| [requirements](skills/requirements/SKILL.md) | Inspect context, resolve gaps one question at a time, and obtain approval of a verifiable requirements summary. |
| [specs](skills/specs/SKILL.md) | Write, independently review, approve, and preserve a specification under docs/specs. |

## Workflow

Requirements produces an approved chat summary. Specs consumes that summary,
writes a draft, runs one material-issues review, surfaces Addressed, Elevated,
and Dismissed findings, and asks for approval. Without an approved summary,
specs runs requirements first.

## Optional Library integration

When Library is installed, requirements may consult relevant archived history
through read-archive. After spec approval, specs offers to archive the document
through archiving-documentation or keep it in repository history. Planning
continues to work when Library is absent.

## Validation

Behavioral cases live beside each skill in evals/evals.json. Run marketplace
checks from the Superstore checkout root:

~~~sh
python3 -m unittest discover -s tests
~~~
~~~~

- [ ] **Step 6: Link Planning from the root README**

Add this row immediately after Library in the plugin table without altering the
user's existing note or layout edits:

~~~markdown
| `planning` | Turn rough requests into approved requirements and concise, reviewed specifications. | [README](plugins/planning/README.md) |
~~~

- [ ] **Step 7: Run deterministic validation**

Run:

~~~sh
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s plugins/library/tests -v
find .agents/plugins .claude-plugin plugins -name '*.json' -print |
  while read -r path; do python3 -m json.tool "$path" >/dev/null || exit 1; done
~~~

Expected: both unittest suites pass and every JSON file parses.

- [ ] **Step 8: Review the final marketplace boundary**

Run:

~~~sh
jj status
jj diff --summary
~~~

Expected implementation paths:

- .agents/plugins/marketplace.json
- .claude-plugin/marketplace.json
- README.md
- plugins/planning/.codex-plugin/plugin.json
- plugins/planning/.claude-plugin/plugin.json
- plugins/planning/plugin.json
- plugins/planning/README.md
- tests/test_marketplace.py

The current diff must not contain plugins/library/README.md because that
user-owned edit remains in the parent change.

- [ ] **Step 9: Commit marketplace integration**

Run:

~~~sh
jj commit \
  .agents/plugins/marketplace.json \
  .claude-plugin/marketplace.json \
  README.md \
  plugins/planning/.codex-plugin/plugin.json \
  plugins/planning/.claude-plugin/plugin.json \
  plugins/planning/plugin.json \
  plugins/planning/README.md \
  tests/test_marketplace.py \
  -m 'feat: add planning marketplace plugin'
~~~

- [ ] **Step 10: Verify the completed stack**

Run:

~~~sh
jj status
jj log -r '@---::@' --no-graph -T 'change_id.short() ++ " " ++ commit_id.short() ++ " " ++ description.first_line() ++ "\n"'
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s plugins/library/tests -v
~~~

Expected: the current working copy is empty, the three implementation changes
are visible with their intended descriptions, and both test suites pass. If the
current workspace still carries user-owned changes rather than using the setup
child, stop and separate them before claiming completion.
