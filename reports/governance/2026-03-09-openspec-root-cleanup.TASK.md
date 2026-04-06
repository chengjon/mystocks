# TASK

> Exported from Mongo control plane. Do not treat this file as the primary editable task source.

- Issue Identifier: `2026-03-09-openspec-root-cleanup-main`
- Issue Title: `OpenSpec And Root Cleanup Decisions`
- Objective: `Preserve the March 9 OpenSpec cleanup and related root-governance retention decisions as dedicated Mongo-backed history.`
- Branch: `main`
- Assigned Worker CLI: `main`
- Tracker State: `verified`

## Allowed Paths
- `openspec`
- `reports/governance/2026-04-03-root-TASK-REPORT.pre-mongo-cutover.md`
- `reports/governance/2026-03-09-openspec-root-cleanup.TASK.md`
- `reports/governance/2026-03-09-openspec-root-cleanup.TASK-REPORT.md`

## Forbidden Paths
- (none)

## Acceptance Checks
- (none)

## OpenSpec
- (none)

## Owner Decision
- Suggested Owner: `main`
- Final Owner: `main`
- Worker CLI: `main`
- Decision Basis:
  - Imported from archived root TASK-REPORT legacy blocks on 2026-04-03.
  - OpenSpec And Root Cleanup Decisions is preserved in Mongo as history, while markdown stays a projection/export layer.

## Scope Paths
- openspec
- reports/governance/2026-04-03-root-TASK-REPORT.pre-mongo-cutover.md

## Structural Debt Disclosure

- canonical_source: `当前 OpenSpec 真值以现行 active/archived change 结构和对应 spec tree 为准；本任务在 Mongo/export markdown 中保留的是清理决策记录，而不是再维护一套并行变更体系。`
- compatibility_surface: `保留 archived root TASK-REPORT legacy blocks 作为历史投影；未保留另一套 active OpenSpec 清单或旧式 root-level 手工判定流程。`
- callers_or_consumers: `openspec list/validate/archive` 使用者、仓库治理维护者、后续查阅 March 9 清理决策的治理任务。
- verification_command: `openspec list`；`openspec validate add-policy-driven-directory-governance --strict`；`openspec validate refactor-technical-debt-remediation-wave1 --strict`；`openspec archive reorganize-project-directory-structure --skip-specs --yes`
- exit_condition: `历史清理决策仅作为归档记录保留；后续任何 OpenSpec 变更治理都必须落在当前 OpenSpec 结构和 Mongo-backed work item 中，不再回到 root legacy blocks。`

## Cleanup / Removal Decision

- code_path_verdict: `safe-to-remove (superseded / non-standard active changes)`
- function_tree_verdict: `重复冗余（已退场旧 change）/ 有效（保留治理主线）`
- removal_basis: `已完成、非标准或被新主线接管的 OpenSpec change 继续保留在 active 列表只会制造平行主线和陈旧治理噪声。`
- keep_reason: `仍具独立治理能力边界的 change（如保留的技术债治理主线）需要继续作为 active/mainline 能力存在，不能一并清空。`

## Temporary / Compatibility Asset Ledger

| path | type | owner | introduced_by | reason | exit_condition | planned_removal_milestone | target_removal_date | current_status |
|---|---|---|---|---|---|---|---|---|
| `reports/governance/2026-04-03-root-TASK-REPORT.pre-mongo-cutover.md` | `other` | `main` | `issue_or_task=2026-04-03-root-task-artifact-mongo-cutover; created_at=2026-04-03` | `保留 March 9 清理决策的 root legacy 投影证据` | `无消费者依赖 root legacy block 时仅继续归档保留，不再作为 active truth` | `future-root-legacy-retirement` | `N/A` | `retained` |
| `openspec/changes/archive/2026-03-09-*` | `other` | `main` | `issue_or_task=2026-03-09-openspec-root-cleanup; created_at=2026-03-09` | `保留已退场 / superseded change 的归档痕迹` | `仅作为 archive 留存，不再回流 active 列表` | `archive-only` | `N/A` | `retained` |

## Metrics Lens

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| `active completed/non-standard OpenSpec changes left in cleaned scope` | `0` | `N/A` | `N/A` | `0` | `openspec list + cleanup notes in TASK-REPORT` |
| `retained governance mainline candidates after March 9 review` | `1` | `N/A` | `other retained candidates may exist outside this task scope` | `1 clearly retained governance mainline` | `TASK-REPORT note: tech-debt-governance-2026q1 keep decision` |

## Next Steps
- 后续 OpenSpec 治理只应继续清理仍被证明为 superseded 的 change，避免重新引入平行主线。

## Compatibility Notes
- Imported from archived root TASK-REPORT legacy blocks on 2026-04-03.
- Mongo is the source of truth; exported markdown is a projection for review and comparison.

## Artifact Links
- reports/governance/2026-04-03-root-TASK-REPORT.pre-mongo-cutover.md
- reports/governance/2026-03-09-openspec-root-cleanup.TASK.md
- reports/governance/2026-03-09-openspec-root-cleanup.TASK-REPORT.md
