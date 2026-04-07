# TASK

> **历史任务说明**:
> 本文件是历史任务单、历史任务汇报或归档任务工件，不是当前任务系统、当前实施状态或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前主线任务系统及验证结果一并核对。
>
> 文内范围、完成状态、负责人、验证命令和下一步如未重新复核，应视为当时任务快照，不得直接当作当前事实。


> Exported from Mongo control plane. Do not treat this file as the primary editable task source.

- Issue Identifier: `2026-04-03-frontend-mainline-phase-4-main`
- Issue Title: `Frontend Mainline Phase 4`
- Objective: `Close Mock/Real validation for the ten Phase 4 risk and system pages, preserve the matrix evidence in Mongo-backed history, and keep the System-Config contract gap explicit.`
- Branch: `wip/root-dirty-20260403`
- Assigned Worker CLI: `main`
- Tracker State: `verified`

## Allowed Paths
- `docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md`
- `reports/analysis/frontend-mainline-phase-4-matrix.md`
- `reports/analysis/frontend-mainline-phase-4-status.json`
- `reports/governance/2026-04-03-root-TASK-REPORT.pre-mongo-cutover.md`
- `reports/governance/2026-04-03-frontend-mainline-phase-4.TASK.md`
- `reports/governance/2026-04-03-frontend-mainline-phase-4.TASK-REPORT.md`

## Forbidden Paths
- (none)

## Acceptance Checks
- (none)

## OpenSpec
- (none)

## Related Plans
- docs/plans/2026-04-02-frontend-mainline-testing-overall-plan.md
- docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md

## Owner Decision
- Suggested Owner: `main`
- Final Owner: `main`
- Worker CLI: `main`
- Decision Basis:
  - Frontend mainline Phases 1-3 already live as focused Mongo work items; Phase 4 follows the same per-phase control-plane pattern.
  - Risk/System phase evidence is preserved as control-plane data, with markdown exported only as a snapshot view.

## Scope Paths
- docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md
- reports/analysis/frontend-mainline-phase-4-matrix.md
- reports/analysis/frontend-mainline-phase-4-status.json

## Next Steps
- 使用 `reports/analysis/frontend-mainline-phase-4-matrix.md`
- 使用 `reports/analysis/frontend-mainline-phase-4-status.json`
- 确认 `System-Config` 的后端配置契约真值，并补非破坏式 real-write smoke

## Compatibility Notes
- Mongo is the source of truth; exported markdown is a projection for review and comparison.
- Phase 4 closeout keeps the System-Config real-write gap explicit instead of implying backend closure.

## Artifact Links
- reports/analysis/frontend-mainline-phase-4-matrix.md
- reports/analysis/frontend-mainline-phase-4-status.json
- reports/governance/2026-04-03-root-TASK-REPORT.pre-mongo-cutover.md
- reports/governance/2026-04-03-frontend-mainline-phase-4.TASK.md
- reports/governance/2026-04-03-frontend-mainline-phase-4.TASK-REPORT.md
