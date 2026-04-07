# TASK

> **历史任务说明**:
> 本文件是历史任务单、历史任务汇报或归档任务工件，不是当前任务系统、当前实施状态或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前主线任务系统及验证结果一并核对。
>
> 文内范围、完成状态、负责人、验证命令和下一步如未重新复核，应视为当时任务快照，不得直接当作当前事实。


> Exported from Mongo control plane. Do not treat this file as the primary editable task source.

- Issue Identifier: `2026-03-09-repository-hygiene-dev-repo-hygiene-b1`
- Issue Title: `Repository Hygiene Root Convergence`
- Objective: `Preserve the root repository hygiene convergence workstream as dedicated Mongo history, covering root docs, backups, reports, and task-artifact workflow exceptions.`
- Branch: `dev-repo-hygiene-b1`
- Assigned Worker CLI: `dev-repo-hygiene-b1`
- Tracker State: `verified`

## Allowed Paths
- `reports/governance/2026-03-09-batch-2-root-error-remediation.md`
- `reports/governance/2026-03-09-batch-3-root-doc-inventory.md`
- `docs/reports/cleanup/index-artifacts/INDEX_root.md`
- `reports/governance/2026-03-09-repository-hygiene-root-convergence.TASK.md`
- `reports/governance/2026-03-09-repository-hygiene-root-convergence.TASK-REPORT.md`
- `reports/governance/2026-04-03-root-TASK-REPORT.pre-mongo-cutover.md`

## Forbidden Paths
- (none)

## Acceptance Checks
- (none)

## OpenSpec
- (none)

## Related Plans
- reports/governance/2026-03-09-batch-2-root-error-remediation.md
- reports/governance/2026-03-09-batch-3-root-doc-inventory.md

## Owner Decision
- Suggested Owner: `dev-repo-hygiene-b1`
- Final Owner: `dev-repo-hygiene-b1`
- Worker CLI: `dev-repo-hygiene-b1`
- Decision Basis:
  - Imported from archived root TASK-REPORT legacy blocks on 2026-04-03.
  - Repository Hygiene Root Convergence is preserved in Mongo as history, while markdown stays a projection/export layer.

## Scope Paths
- reports/governance/2026-03-09-batch-2-root-error-remediation.md
- reports/governance/2026-03-09-batch-3-root-doc-inventory.md
- docs/reports/cleanup/index-artifacts/INDEX_root.md

## Structural Debt Disclosure

- canonical_source: `root repository hygiene 的当前证据以分批 remediation/doc inventory 文档和 INDEX_root 汇总为准；Mongo/export markdown 只保留 convergence 决策历史，不再让 root loose files 充当并行真相源。`
- compatibility_surface: `保留 archived root TASK-REPORT legacy 投影作为历史参考；未保留新的 root-level 手工治理总盘。`
- callers_or_consumers: `root cleanup 后续任务、目录整理审阅者、task-artifact workflow exception 追溯者。`
- verification_command: `N/A（历史导入 work item；证据来源为 reports/governance/2026-03-09-batch-2-root-error-remediation.md、reports/governance/2026-03-09-batch-3-root-doc-inventory.md、docs/reports/cleanup/index-artifacts/INDEX_root.md）`
- exit_condition: `后续 root repository hygiene 决策都必须继续落在受控治理路径中，不再通过 root loose artifacts 扩散新的平行记录。`

## Cleanup / Removal Decision

- code_path_verdict: `safe-to-remove (redundant root artifacts already converged)`
- function_tree_verdict: `重复冗余 / 失效但兼容保留`
- removal_basis: `已经被 remediation/doc inventory/index 收敛覆盖的 root loose artifacts 不应继续作为活动治理入口存在。`
- keep_reason: `少量 archived root projections 仍保留为历史证据，用于对照 pre-mongo-cutover 状态。`

## Temporary / Compatibility Asset Ledger

| path | type | owner | introduced_by | reason | exit_condition | planned_removal_milestone | target_removal_date | current_status |
|---|---|---|---|---|---|---|---|---|
| `reports/governance/2026-04-03-root-TASK-REPORT.pre-mongo-cutover.md` | `other` | `dev-repo-hygiene-b1` | `issue_or_task=2026-04-03-root-task-artifact-mongo-cutover; created_at=2026-04-03` | `保留 root repository hygiene convergence 的历史投影证据` | `仅作 archive/reference，不再作为 active governance truth` | `future-root-legacy-retirement` | `N/A` | `retained` |

## Metrics Lens

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| `repository hygiene evidence artifacts in scope` | `3 files` | `N/A` | `N/A` | `3 files retained as evidence` | `Scope Paths` |
| `new root-level parallel governance truth introduced by this historical item` | `0` | `N/A` | `N/A` | `0` | `Objective + compatibility notes` |

## Next Steps
- 后续若继续做 root hygiene，只应沿用受控 inventory/remediation 路径，不再新增 root loose governance artifacts。

## Compatibility Notes
- Imported from archived root TASK-REPORT legacy blocks on 2026-04-03.
- Mongo is the source of truth; exported markdown is a projection for review and comparison.

## Artifact Links
- reports/governance/2026-03-09-batch-2-root-error-remediation.md
- reports/governance/2026-03-09-batch-3-root-doc-inventory.md
- reports/governance/2026-04-03-root-TASK-REPORT.pre-mongo-cutover.md
- reports/governance/2026-03-09-repository-hygiene-root-convergence.TASK.md
- reports/governance/2026-03-09-repository-hygiene-root-convergence.TASK-REPORT.md
