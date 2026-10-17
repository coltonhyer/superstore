# Superstore

## Plugin versions

Before publishing a changeset that alters a skill or its references under
`plugins/<name>/`, bump that plugin's version once for the whole changeset, not
per task or commit, in both `.claude-plugin/plugin.json` and
`.codex-plugin/plugin.json`, and keep the two equal. When the work follows an
implementation plan, make the bump the plan's final task. Some hosts deliver a
plugin update only when its version changes, so a changeset published without
a bump may never reach installed copies. While the plugins are in v0, use a
minor bump for changed behavior and a patch bump for fixes. Changes limited to
a README or eval cases need no bump.

## Reviews

When reviewing a change to this repository, read `REVIEW.md` first and follow
it. Every rule under its "What Important means here" and "Always check"
sections came from a failure recorded under `evals/notebook/writeups/` or a
review finding on this repository. Add a rule only with such a precedent and
name it in the commit message. Remove a rule once a test under `tests/`
enforces it.
