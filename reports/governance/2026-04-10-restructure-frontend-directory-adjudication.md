# Adjudication: restructure-frontend-directory

> **治理裁定说明**:
> 本文件用于记录 2026-04-10 对 `restructure-frontend-directory` 的当前治理判断。
> 共享规则仍以 `architecture/STANDARDS.md` 为准；本文件只回答该 active change 是否应继续保留，以及当前应如何理解其执行边界。

## Decision

Keep `restructure-frontend-directory` active as the canonical frontend-structure convergence line, but treat it as a late-stage repo-truth closeout line rather than a literal 92-task migration checklist.

## Why It Must Stay Active

- The change is structurally valid: `openspec validate restructure-frontend-directory --strict` passes.
- Current frontend repo-truth guides explicitly anchor active directory truth back to this change ledger.
- Historical execution has already landed substantial convergence work into the real router/domain-entry layout, and that work still needs a coherent active ownership line.
- The current technical-debt register also still points to frontend structural mess under this mainline rather than under any replacement change.

## Why The Original Checklist Cannot Be Read Literally Anymore

Current repo truth has drifted well beyond the original March assumptions:

- `docs/guides/frontend-structure.md` and `docs/reports/FRONTEND_STRUCTURE_REPO_TRUTH_STATUS_2026-04-06.md` already record phases 0 through 5 as materially closed through verified micro-batches.
- `docs/reports/tasks/2026-03-27-frontend-directory-restructure-replacement-task.md` explicitly states the old `7/92` task package could not be continued mechanically and needed replacement-task logic.
- The current `src/views/` tree still contains many historical root-level `.vue` files and legacy directories, so the spec text that expects a clean exact end-state is ahead of current repository reality.
- The task ledger itself already contains many repo-truth remap notes showing the original `git mv` instructions were superseded by compatibility-wrapper and canonical-entrypoint inversion batches.

## Practical Interpretation

- This change remains the canonical active line for frontend directory convergence.
- It is not a blank stale roadmap and should not be retired today.
- It is also not an exact representation of current repository shape; some spec/task wording now functions as target-state intent, not literal current status.

## Execution Rule For Future Sessions

- Do not retire this change as stale.
- Do not archive it as completed yet.
- Do not continue the original checklist from the top.
- Continue only from repo-truth closeout slices such as:
  - remaining compatibility-wrapper retirement decisions
  - shared-asset normalization where current code proves it is safe
  - external workflow gates: review, merge, deploy, archive
  - selective restructuring of the remaining root-level / legacy directories based on current route truth, not on old folder-count assumptions
