# G2.389 OpenSpec dirty-worktree-governance change package preflight / no-source

## Boundary

Mode: `no-source`.

Scope is limited to:

`openspec/changes/implement-dirty-worktree-cleanup-governance/`

This node does not edit, restore, delete, stage, or commit any file.

## Evidence Summary

- Active change: `implement-dirty-worktree-cleanup-governance`
- Active status: `0/67 tasks`, `8d ago`
- Dirty shape: `??=4`, `M=0`
- Files:
  - `design.md`
  - `proposal.md`
  - `specs/directory-governance/spec.md`
  - `tasks.md`
- `openspec validate implement-dirty-worktree-cleanup-governance --strict`: exit code 0.
- Staged files during preflight: 0.
- PostHog flush network noise appears in stderr, but OpenSpec validation exits 0.

## Package Structure

| File | Role | Status |
|---|---|---|
| `proposal.md` | Change proposal | Present, untracked |
| `design.md` | Design notes | Present, untracked |
| `tasks.md` | Task plan | Present, untracked, `0/67` checked |
| `specs/directory-governance/spec.md` | Delta spec | Present, untracked |

The delta spec defines one new requirement:

`Dirty Worktree Cleanup Governance`

It contains 15 scenarios covering cleanup preparation, classification, recovery artifacts, safe slicing, graph-backed impact gates, generated/runtime artifacts, multi-branch dirty work, root clean-status claims, ignore-rule limits, squash-merged branches, WIP worktrees, rescue branches, root realignment, and temporary cleanup infrastructure retirement.

## Duplicate / Stale / Validity Check

| Question | Result | Evidence |
|---|---|---|
| Is this change active? | Yes | `openspec list` shows `0/67 tasks`. |
| Does it validate? | Yes | `openspec validate <change-id> --strict` exits 0. |
| Is it a tracked modification? | No | All 4 files are untracked. |
| Is it already archived? | No | No archive match found. |
| Does current `directory-governance` spec already contain this requirement? | No | Active spec exists, but all 16 Requirement/Scenario headings from this change are missing from the active spec. |
| Is it stale? | No hard evidence | Tasks are all unchecked, which is consistent with an active proposal draft rather than a completed stale artifact. |
| Is it duplicate? | No confirmed duplicate | Existing `directory-governance` spec has different requirements; this change adds dirty-worktree cleanup governance. |

## Existing Implementation Evidence

The repository already contains related governance artifacts:

- `docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE.md`
- `architecture/STANDARDS.md`
- `AGENTS.md`
- `CLAUDE.md`
- prior dirty-cleanup worklogs such as `g2-376`, `g2-379`, `g2-381`, `g2-387`, and `g2-388`

This means the change is partially backed by current repository practice, but its `tasks.md` still records `0/67` completed tasks. Therefore it should be accepted as an active proposal package, not as an implementation closeout or archive-ready change.

## Decision

Classification: `有效`.

Disposition: eligible for a formal OpenSpec package acceptance node, with a strict scope of the 4 untracked files under `openspec/changes/implement-dirty-worktree-cleanup-governance/`.

It should not be bundled with:

- modified active specs
- untracked spec directories
- other active changes
- deletion-retirement residue
- source/test/frontend/backend changes

## Recommended Next Node

`G2.390 openspec dirty-worktree-governance change package acceptance / spec-authorized`

Suggested scope:

- `openspec/changes/implement-dirty-worktree-cleanup-governance/design.md`
- `openspec/changes/implement-dirty-worktree-cleanup-governance/proposal.md`
- `openspec/changes/implement-dirty-worktree-cleanup-governance/specs/directory-governance/spec.md`
- `openspec/changes/implement-dirty-worktree-cleanup-governance/tasks.md`

Required gates:

- Stage only the 4 files above.
- Do not stage `openspec/specs/**`.
- Do not stage other active change groups.
- Run `openspec validate implement-dirty-worktree-cleanup-governance --strict`.
- Run `openspec validate --changes --strict`.
- Run `git diff --cached --check`.
- Run staged path allowlist before commit.
