# G2.388 OpenSpec active-change residual inventory / no-source

## Boundary

Mode: `no-source`.

This node inventories only the 5 dirty active OpenSpec change groups named by the operator:

- `implement-dirty-worktree-cleanup-governance`
- `implement-html5-migration-experience-optimization`
- `restructure-frontend-directory`
- `sequence-backend-architecture-unblocks`
- `split-backend-core-modules-with-compatibility-wrappers`

This node does not edit, restore, delete, stage, or commit any file.

## Evidence Summary

- Current HEAD: `99cfce98a chore(openspec): retire archived drift changes`.
- Staged files during inventory: 0.
- Target groups: 5.
- Target dirty files: 16.
- Each target change passes `openspec validate <change-id> --strict` with exit code 0.
- PostHog flush noise appears in validation stderr, but OpenSpec validation status is 0 for every target change.

## Decision Table

| Classification | Change | Active status | Dirty shape | Validation | Evidence | Disposition |
|---|---|---|---|---|---|---|
| 有效 | `implement-dirty-worktree-cleanup-governance` | `0/67 tasks` | `??=4`, `M=0` | Pass | New proposal, design, tasks, and `directory-governance` delta spec. Tasks are fully unchecked, indicating a draft governance proposal rather than stale completion residue. | Dedicated governance OpenSpec package. Do not mix with spec residuals or active implementation. |
| 有效 | `implement-html5-migration-experience-optimization` | `63/111 tasks` | `M=4`, `??=1` | Pass | Modified proposal/design/spec/tasks plus `tasks-review.md`; large tracked diff (`+550/-88`); current tasks summarize `71/119` done in working copy. | Dedicated high-risk frontend experience package. Needs review before any commit because scope is broad and overlaps frontend architecture. |
| 有效 | `restructure-frontend-directory` | `76/92 tasks` | `M=2`, `??=0` | Pass | Modified design/tasks only; small tracked diff (`+3/-3`); existing proposal/spec remain present. | Narrow frontend directory package candidate. Can be reviewed separately from HTML5 migration. |
| 陈旧 / 重复风险 | `sequence-backend-architecture-unblocks` | `Complete` | `??=3`, `M=0` | Pass | Change is already marked complete with `33/33` tasks, but proposal, proposal review, and `architecture-governance` delta spec are untracked. | Do not commit as ordinary active-change residual. Requires a closeout/archive/backfill decision first. |
| 有效 | `split-backend-core-modules-with-compatibility-wrappers` | `12/24 tasks` | `??=4`, `M=0` | Pass | New proposal, design, and architecture/directory governance delta specs; tasks are half complete. | Dedicated backend-core OpenSpec package. Do not mix with `sequence-backend-architecture-unblocks`. |

## Three-Class Result

| Class | Changes | Count | Notes |
|---|---|---:|---|
| 有效 | `implement-dirty-worktree-cleanup-governance`, `implement-html5-migration-experience-optimization`, `restructure-frontend-directory`, `split-backend-core-modules-with-compatibility-wrappers` | 4 | Valid active changes, but each needs its own package or domain-scoped package. |
| 陈旧 | `sequence-backend-architecture-unblocks` | 1 | Completed status with untracked backfill artifacts; needs a closeout/archive decision before mutation. |
| 重复 | None confirmed | 0 | No exact duplicate was confirmed. There are domain overlaps between frontend changes, but the evidence supports separate scopes. |

## Package Recommendations

Recommended follow-up order:

1. `G2.389 openspec dirty-worktree-governance change package preflight / no-source`
   - Scope: `implement-dirty-worktree-cleanup-governance`.
   - Reason: directly governs the current cleanup line and has no tracked modifications.

2. `G2.390 openspec backend-core split change package preflight / no-source`
   - Scope: `split-backend-core-modules-with-compatibility-wrappers`.
   - Reason: active backend-core change with architecture/directory governance deltas.

3. `G2.391 openspec frontend active-change package split / no-source`
   - Scope: `implement-html5-migration-experience-optimization` and `restructure-frontend-directory`.
   - Goal: decide whether these stay separate packages or require sequencing due frontend architecture overlap.

4. `G2.392 openspec completed-change backfill disposition / no-source`
   - Scope: `sequence-backend-architecture-unblocks`.
   - Goal: decide whether the untracked proposal/spec/review files are valid closeout backfill, stale duplicate, or should be deferred.

Do not stage any active-change residual until its package receives explicit authorization.
