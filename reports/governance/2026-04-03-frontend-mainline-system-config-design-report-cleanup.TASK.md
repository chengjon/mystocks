# TASK

> **历史任务说明**:
> 本文件是历史任务单、历史任务汇报或归档任务工件，不是当前任务系统、当前实施状态或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前主线任务系统及验证结果一并核对。
>
> 文内范围、完成状态、负责人、验证命令和下一步如未重新复核，应视为当时任务快照，不得直接当作当前事实。


> Exported from Mongo control plane. Do not treat this file as the primary editable task source.

- Issue Identifier: `2026-04-03-frontend-mainline-system-config-design-report-cleanup-main`
- Issue Title: `Frontend Mainline System-Config Design Report Cleanup`
- Objective: `Align the remaining stale System-Config backend contract wording in the historical phase-2 design report to the confirmed current truth without implying a unified backend system-settings API exists.`
- Branch: `wip/root-dirty-20260403`
- Assigned Worker CLI: `main`
- Tracker State: `verified`

## Allowed Paths
- `docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md`
- `reports/governance/2026-04-03-frontend-mainline-system-config-design-report-cleanup.TASK.md`
- `reports/governance/2026-04-03-frontend-mainline-system-config-design-report-cleanup.TASK-REPORT.md`

## Forbidden Paths
- (none)

## Acceptance Checks
- `git diff --check -- docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md`
- `rg -n 'localStorage|System-Data|/health/detailed|/health|/api/v1/data-sources/config/batch' docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md`

## OpenSpec
- (none)

## Related Plans
- docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md

## Owner Decision
- Suggested Owner: `main`
- Final Owner: `main`
- Worker CLI: `main`
- Decision Basis:
  - The current System-Config truth is already confirmed in active codepaths and governance snapshots.
  - The remaining stale backend config contract wording sits in a historical design completion report that is still easy to quote out of context.

## Scope Paths
- docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md

## Structural Debt Disclosure

- canonical_source: `当前 System-Config 真值为 localStorage-only 页面保存、health 只读接口与 System-Data 批量写回分工；历史 design report 不得继续宣称存在统一 backend system-config 契约。`
- compatibility_surface: `保留历史 design report 作为归档设计说明；未保留统一 system-config 后端 shim 或兼容接口。`
- callers_or_consumers: `docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md` 以及可能引用该历史设计报告的后续讨论、汇报和追溯工作。
- verification_command: `git diff --check -- docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md`；`rg -n 'localStorage|System-Data|/health/detailed|/health|/api/v1/data-sources/config/batch' docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md`
- exit_condition: `仅当后端引入真实统一 system-settings 契约并同步 OpenAPI / active docs 后，才允许重新改写该历史报告中的当前真值说明。`

## Cleanup / Removal Decision

- code_path_verdict: `safe-to-remove`
- function_tree_verdict: `重复冗余`
- removal_basis: `历史 design report 中旧的 backend config contract wording 与现行真实功能树冲突，继续保留会让历史报告被误读为当前 active contract。`
- keep_reason: `历史 design report 文档本身仍需保留用于追溯；被移除的是过时 contract wording，而不是整份报告。`

## Temporary / Compatibility Asset Ledger

| path | type | owner | introduced_by | reason | exit_condition | planned_removal_milestone | target_removal_date | current_status |
|---|---|---|---|---|---|---|---|---|
| `N/A` | `other` | `main` | `N/A` | `本批次未新增或保留 shim / backup / temporary-entry；只治理历史 design report 的过时 contract wording。` | `N/A` | `N/A` | `N/A` | `N/A` |

## Metrics Lens

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| `historical design report stale backend contract mentions in scope` | `0` | `N/A` | `N/A` | `0` | `rg -n --no-messages "/api/v1/system/config|system/datasource" docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md` |
| `historical design report aligned to current truth markers` | `present` | `N/A` | `N/A` | `present` | `rg -n 'localStorage|System-Data|/health/detailed|/health|/api/v1/data-sources/config/batch' docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md` |

## Next Steps
- Leave broader design-report modernization for separate work if needed.

## Compatibility Notes
- Mongo is the source of truth; this is a narrow design-report wording cleanup only.
- This cleanup does not claim the old phase-2 design was implemented verbatim; it only prevents the report from advertising a backend contract that the active codepath does not provide.

## Artifact Links
- reports/governance/2026-04-03-frontend-mainline-system-config-design-report-cleanup.TASK.md
- reports/governance/2026-04-03-frontend-mainline-system-config-design-report-cleanup.TASK-REPORT.md
- docs/reports/design/ARTDECO_PHASE2_COMPLETION_REPORT.md
