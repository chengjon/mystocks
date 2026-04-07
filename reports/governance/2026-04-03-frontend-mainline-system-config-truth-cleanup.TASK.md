# TASK

> **历史任务说明**:
> 本文件是历史任务单、历史任务汇报或归档任务工件，不是当前任务系统、当前实施状态或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前主线任务系统及验证结果一并核对。
>
> 文内范围、完成状态、负责人、验证命令和下一步如未重新复核，应视为当时任务快照，不得直接当作当前事实。


> Exported from Mongo control plane. Do not treat this file as the primary editable task source.

- Issue Identifier: `2026-04-03-frontend-mainline-system-config-truth-cleanup-main`
- Issue Title: `Frontend Mainline System-Config Truth Cleanup`
- Objective: `Remove stale active-tree System-Config contract hints so scripts and active reference docs match the confirmed truth: no unified backend system-settings contract exists, the page save path is local-only, and datasource writeback belongs to System-Data.`
- Branch: `wip/root-dirty-20260403`
- Assigned Worker CLI: `main`
- Tracker State: `verified`

## Allowed Paths
- `scripts/dev/tools/generate-page-config.js`
- `docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md`
- `docs/api/ARTDECO_TRADING_CENTER_API_MAPPING.md`
- `reports/governance/2026-04-03-frontend-mainline-system-config-truth-cleanup.TASK.md`
- `reports/governance/2026-04-03-frontend-mainline-system-config-truth-cleanup.TASK-REPORT.md`

## Forbidden Paths
- (none)

## Acceptance Checks
- `git diff --check -- scripts/dev/tools/generate-page-config.js docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md docs/api/ARTDECO_TRADING_CENTER_API_MAPPING.md`
- `node --check scripts/dev/tools/generate-page-config.js`

## OpenSpec
- (none)

## Related Plans
- docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md

## Owner Decision
- Suggested Owner: `main`
- Final Owner: `main`
- Worker CLI: `main`
- Decision Basis:
  - System-Config truth is already confirmed in Mongo: no unified backend system-settings contract exists.
  - Active generators and active reference docs should not continue to advertise /api/system/settings or pending-contract wording.

## Scope Paths
- scripts/dev/tools/generate-page-config.js
- docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md
- docs/api/ARTDECO_TRADING_CENTER_API_MAPPING.md

## Structural Debt Disclosure

- canonical_source: `当前 System-Config 真值为页面本地设置语义；数据源真实写回归属 System-Data；active generator/docs 不再宣称存在统一 /api/system/settings 后端契约。`
- compatibility_surface: `保留页面级 local-only save 语义；未保留统一 system-settings 后端 shim 或兼容接口。`
- callers_or_consumers: `scripts/dev/tools/generate-page-config.js`、`docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md`、`docs/api/ARTDECO_TRADING_CENTER_API_MAPPING.md` 以及由 page-config 生成的 active build artifacts。
- verification_command: `git diff --check -- scripts/dev/tools/generate-page-config.js docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md docs/api/ARTDECO_TRADING_CENTER_API_MAPPING.md`；`node --check scripts/dev/tools/generate-page-config.js`；`rg -n "/api/system/settings|系统配置接口真值待确认|保存配置|统一系统配置后端契约仍未建立|保存本地设置" scripts/dev/tools/generate-page-config.js docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md docs/api/ARTDECO_TRADING_CENTER_API_MAPPING.md`
- exit_condition: `仅当后端引入真实统一 system-settings 契约并同步 OpenAPI / active docs 后，才允许重新改写当前 System-Config 真值。`

## Cleanup / Removal Decision

- code_path_verdict: `safe-to-remove`
- function_tree_verdict: `重复冗余`
- removal_basis: `active-tree 中关于 /api/system/settings、待确认统一后端契约、保存配置 的旧提示与当前真实功能树冲突；删除这些提示后，生成器、执行矩阵与 API mapping 才与当前实现一致。`
- keep_reason: `历史设计稿与阶段汇报中的旧表述仍可作为归档材料保留，但不得继续充当 active guidance。`

## Temporary / Compatibility Asset Ledger

| path | type | owner | introduced_by | reason | exit_condition | planned_removal_milestone | target_removal_date | current_status |
|---|---|---|---|---|---|---|---|---|
| `N/A` | `other` | `main` | `N/A` | `本批次未新增或保留 shim / backup / temporary-entry；只治理 active guidance 的错误真值。` | `N/A` | `N/A` | `N/A` | `N/A` |

## Metrics Lens

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| `scoped active guidance files still advertising stale unified system-settings contract` | `0` | `N/A` | `历史归档文档中仍可能存在旧表述，但不属于 active guidance` | `0` | `rg -n "/api/system/settings|系统配置接口真值待确认|保存配置|统一系统配置后端契约仍未建立|保存本地设置" ...` |
| `scoped active guidance files aligned to current truth` | `3 files aligned` | `N/A` | `N/A` | `3 files aligned` | `scripts/dev/tools/generate-page-config.js + docs/plans/...phase-4... + docs/api/ARTDECO_TRADING_CENTER_API_MAPPING.md` |

## Next Steps
- Only revisit this area if backend introduces a real unified system-settings contract and OpenAPI changes land.

## Compatibility Notes
- Mongo is the source of truth; exported markdown is a projection for review and comparison.
- This cleanup removes stale active-tree contract hints without introducing a new backend system-settings contract.

## Artifact Links
- reports/governance/2026-04-03-frontend-mainline-system-config-truth-cleanup.TASK.md
- reports/governance/2026-04-03-frontend-mainline-system-config-truth-cleanup.TASK-REPORT.md
- docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md
- docs/api/ARTDECO_TRADING_CENTER_API_MAPPING.md
