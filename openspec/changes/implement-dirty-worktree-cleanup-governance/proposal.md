# Change: Implement dirty worktree cleanup governance

## Why

The repository currently has a long-lived dirty worktree with more than one thousand mixed changes across frontend, backend, tests, scripts, OpenSpec, and documentation. The cleanup must be implemented through recoverable, reviewable slices instead of a root-level reset, blanket stash, or mixed commit.

## What Changes

- Add an OpenSpec-governed execution plan for dirty worktree cleanup.
- Require a recovery snapshot, inventory, classification, clean review worktree, slice validation, and final cleanup flow before mutating high-risk paths.
- Split cleanup implementation into bounded slices for documentation, OpenSpec, frontend, backend/API, Python source/scripts/tests, root config/tooling, and stale worktrees/stash.
- Normalize the cleanup procedure around a single authoritative 0-9 step map and one classification source of truth.
- Define concrete recovery artifacts, including `phase0-manifest.json`, `restore-instructions.md`, and documented `git apply --check` limitations.
- Preserve generated/runtime artifacts before removal and keep PM2 service availability explicit in cleanup gates.
- Add explicit guards for the latest common failure modes: root-clean false completion, versioned ignore overreach, squash-merge branch misclassification, WIP worktree deletion, and premature rescue branch deletion.
- Require staged-scope GitNexus detection and code-slice impact checks before code cleanup commits.
- Require final cleanup of temporary review worktrees and related cleanup branches.

## Impact

- Affected specs: `directory-governance`
- Affected docs:
  - `docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE.md`
  - `docs/superpowers/plans/2026-05-27-dirty-worktree-cleanup-plan.md`
  - future cleanup reports under `docs/reports/cleanup/`
- Affected code: none during proposal creation; later implementation slices may touch `web/frontend/`, `web/backend/`, `src/`, `scripts/`, `tests/`, `openspec/`, and root governance/config files after slice-specific approval and validation.
