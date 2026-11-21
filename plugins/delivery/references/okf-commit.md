# OKF approval, deprecation, and commit

This reference defines the post-approval mechanics for OKF `spec` and `plan`
documents. Execute it only after explicit human approval or an explicitly
authorized autonomous clean independent review under the owning skill (`specs`
or `plans`). Approval triggers — including non-approval request words such as
`preserve`, `save`, `record`, and `commit` — and review requirements remain
defined by the owning skill.

Explicit approval or authorized autonomous clean review authorizes the commit:
do not run another review, change the document's content, or ask for approval
again. Any content edit made after approval, other than the edits steps 1 and
2 make (or a mechanical blob-citation-only refresh below), requires approval
of the changed document again before committing.

## Commit an approved document

1. **Promote to `status: stable` and `verified`:** Set `status: stable` in
   the document's frontmatter and write (or replace) its `verified` line right
   after `status`:
   - **Explicit human approval:** write
     `verified: { by: human:<approver>, at: <approval time> }`. Read
     `<approver>` from the user name version control is configured with — with
     Jujutsu, `jj config get user.name`; with Git, `git config user.name` — and
     `<approval time>` from the UTC instant printed by
     `date -u +%Y-%m-%dT%H:%M:%SZ`. When the configured name is unset, empty,
     or contains any of `,` `[` `]` `{` `}` `#` `:`, write no `verified` line
     (removing any existing `verified` line if present) and report that
     omission.
   - **Explicitly authorized autonomous clean independent review:** write
     `verified: { by: process:delivery-autonomous, at: <approval time> }` using
     `date -u +%Y-%m-%dT%H:%M:%SZ`. This marks the document OKF
     `machine-confirmed`, never `human:`.

2. **Deprecate `supersedes` targets:** When the document has `supersedes`,
   inspect every listed target across both scalar (`supersedes: <path>`) and
   inline-list (`supersedes: [path-a, path-b]`) forms:
   - Ignore missing targets; they affect nothing.
   - Leave unmigrated targets (no frontmatter, or frontmatter without a `type`
     line) unchanged and report them unchanged.
   - For migrated targets (frontmatter with a `type` line), set
     `status: deprecated` unless `status` is already `deprecated`, replacing
     the `status` line or, when none exists, adding `status: deprecated` after
     `description`.
   For a spec split, deprecate the split spec only once the replacement set is
   complete and approved.

3. **Commit strictly the changed files and verify recording:** Commit, through
   the repository's active version-control workflow, strictly the files steps 1
   and 2 actually modified: the approved document and each `supersedes` target
   whose status step 2 changed to `deprecated`. Explicitly exclude
   already-`deprecated` targets, unmigrated targets, missing targets, and
   unrelated working-copy changes; leave unrelated changes untouched.
   Describing the working-copy change is not a commit. List each path once per
   command.
   - With Jujutsu, `jj commit -m '<message>' <paths>` moves the files into a
     finished revision. Verify for every committed path that
     `jj diff -r @ <path>` prints nothing and `jj log -r @- <path>` shows a
     revision newer than the one you started from.
   - With Git, `git add <paths> && git commit -m '<message>' <paths>`. Verify
     for every committed path that `git status --porcelain <path>` prints
     nothing and `git log -1 -- <path>` shows the new commit.
   Claim a commit only when both checks hold for every committed path.

4. **Handle commit or recording failure:** When no supported version control
   exists, the commit is refused or fails, or either recording check fails for
   any path, leave every changed file in place in the working copy with its
   new status (and updated fields), and report those files uncommitted and not
   downstream-ready (not plan-ready for a spec; not execution-ready for a
   plan). Report the exact failure outcome without claiming completion or
   working around it.

5. **Compute and report the committed blob citation:** Compute the
   12-character committed Git blob hash only from the committed revision, never
   from a dirty working copy:
   - With Jujutsu (colocated and non-colocated):
     `git --git-dir="$(jj git root)" rev-parse --short=12 "$(jj log -r @- --no-graph -T commit_id):<path>"`
   - With Git: `git rev-parse --short=12 HEAD:<path>`
   Explicitly report `<path>, blob <12-char hash>` using the resolved path
   (downstream committed plans and handoffs cite approved, committed specs and
   plans this way; ad-hoc history queries and revision reports may still use
   `<path>@<revision>` — see `library`'s `pin-and-compare.md` for blob lookups
   and revision diffs).

## Revise vs. refresh a stable document

- **In-place revision:** Revise in place; do not create a new file for a new
  revision. Set `status: draft` and remove the `verified` line, make the
  change, and review it again when the change is material. Obtain approval of
  the revised document again, then re-commit through steps 1–5 (setting
  `status: stable` and writing a new `verified` line).
- **Mechanical blob-citation-only refresh on a `stable` plan:** When a
  `stable` plan's tasks and content are unchanged and only its cited spec blob
  hash(es) need updating, update only the cited spec blob hash(es), commit the
  refreshed plan through steps 3–4, and compute its new committed blob hash
  with step 5 — without flipping `status` to `draft`, changing `verified`, or
  re-requesting approval.
