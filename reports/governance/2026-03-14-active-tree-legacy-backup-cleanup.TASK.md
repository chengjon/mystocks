# TASK

> **历史任务说明**:
> 本文件是历史任务单、历史任务汇报或归档任务工件，不是当前任务系统、当前实施状态或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前主线任务系统及验证结果一并核对。
>
> 文内范围、完成状态、负责人、验证命令和下一步如未重新复核，应视为当时任务快照，不得直接当作当前事实。


> Exported from Mongo control plane. Do not treat this file as the primary editable task source.

- Issue Identifier: `2026-03-14-active-tree-legacy-cleanup-mystocks-spec2`
- Issue Title: `Classify and clean active-tree legacy backup files`
- Objective: `Audit and safely remove redundant active-tree .backup/.broken/.old/.new files using code-path and function-tree judgments.`
- Branch: `mystocks_spec2`
- Assigned Worker CLI: `mystocks_spec2`
- Tracker State: `merged`

## Allowed Paths
- `web/frontend/src/views/RiskMonitor.vue.broken`
- `web/frontend/src/views/BacktestAnalysis.vue.broken`
- `web/frontend/src/router/index.ts.broken`
- `web/frontend/src/router/index.ts.bak.20260214`
- `web/frontend/src/main.js.old`
- `web/frontend/src/App.vue.old`
- `web/backend/app/api/risk_management.py.backup.20260130`
- `web/backend/app/api/data.py.backup.20260130`
- `web/backend/app/api/technical_analysis.py.new`
- `src/database/database_service.py.backup.20260130`
- `src/advanced_analysis/decision_models_analyzer.py.backup.20260130`
- `src/monitoring/alert_manager.py.backup_complex_20251108`
- `reports/governance/2026-04-03-root-TASK-REPORT.pre-mongo-cutover.md`
- `reports/governance/2026-03-14-active-tree-legacy-backup-cleanup.TASK.md`
- `reports/governance/2026-03-14-active-tree-legacy-backup-cleanup.TASK-REPORT.md`

## Forbidden Paths
- (none)

## Acceptance Checks
- `git diff --check`

## OpenSpec
- (none)

## Owner Decision
- Suggested Owner: `mystocks_spec2`
- Final Owner: `mystocks_spec2`
- Worker CLI: `mystocks_spec2`
- Decision Basis:
  - Imported from archived root TASK-REPORT legacy blocks on 2026-04-03.
  - Classify and clean active-tree legacy backup files is preserved in Mongo as history, while markdown stays a projection/export layer.

## Scope Paths
- reports/governance/2026-04-03-root-TASK-REPORT.pre-mongo-cutover.md

## Structural Debt Disclosure

- canonical_source: `active tree 中仅保留无 legacy 后缀的现行运行时模块与入口：web/frontend/src/main.js、web/frontend/src/App.vue、web/frontend/src/router/index.ts、web/backend/app/api/risk_management.py、web/backend/app/api/data/__init__.py、web/backend/app/api/technical_analysis.py、src/database/database_service.py、src/advanced_analysis/decision_models_analyzer.py、src/monitoring/alert_manager.py。`
- compatibility_surface: `active tree 不再保留 legacy backup / broken / old / .new 文件；剩余同名痕迹仅允许存在于历史文档或非运行时元数据。`
- callers_or_consumers: `frontend 入口 main.js -> App.vue / router/index.ts；backend 路由注册链路 -> risk_management.py / api.data / technical_analysis.py；src 侧调用方继续依赖无 legacy 后缀的现行模块。`
- verification_command: `rg -n --hidden --glob '!*.git' "RiskMonitor\\.vue\\.broken|BacktestAnalysis\\.vue\\.broken|index\\.ts\\.broken|index\\.ts\\.bak\\.20260214|main\\.js\\.old|App\\.vue\\.old|risk_management\\.py\\.backup\\.20260130|data\\.py\\.backup\\.20260130|technical_analysis\\.py\\.new|database_service\\.py\\.backup\\.20260130|decision_models_analyzer\\.py\\.backup\\.20260130|alert_manager\\.py\\.backup_complex_20251108" web/frontend/src web/backend/app src`；`git diff --check`；`python -m py_compile web/backend/app/api/risk_management.py web/backend/app/api/data/__init__.py web/backend/app/api/technical_analysis.py src/database/database_service.py src/advanced_analysis/decision_models_analyzer.py src/monitoring/alert_manager.py`
- exit_condition: `N/A；本批次目标就是完成终态删除，不保留 active-tree 兼容层。`

## Cleanup / Removal Decision

- code_path_verdict: `safe-to-remove`
- function_tree_verdict: `重复冗余`
- removal_basis: `12 个对象均通过后缀精确扫描证明不再参与 active code path，功能树也已被无 legacy 后缀的现行实现覆盖。`
- keep_reason: `N/A；剩余历史提及仅属于归档文档或非运行时元数据，不构成保留 active-tree legacy 文件的依据。`

## Temporary / Compatibility Asset Ledger

| path | type | owner | introduced_by | reason | exit_condition | planned_removal_milestone | target_removal_date | current_status |
|---|---|---|---|---|---|---|---|---|
| `web/frontend/src/views/RiskMonitor.vue.broken` | `backup` | `mystocks_spec2` | `issue_or_task=historical-emergency-fix-snapshot; created_at=unknown` | `损坏页面临时重命名残留` | `代码路径判定为 0 命中且功能树判定为 重复冗余` | `2026-03-14-active-tree-legacy-backup-cleanup` | `2026-03-14` | `removed` |
| `web/frontend/src/views/BacktestAnalysis.vue.broken` | `backup` | `mystocks_spec2` | `issue_or_task=historical-emergency-fix-snapshot; created_at=unknown` | `损坏页面临时重命名残留` | `代码路径判定为 0 命中且功能树判定为 重复冗余` | `2026-03-14-active-tree-legacy-backup-cleanup` | `2026-03-14` | `removed` |
| `web/frontend/src/router/index.ts.broken` | `backup` | `mystocks_spec2` | `issue_or_task=historical-route-recovery-snapshot; created_at=unknown` | `旧路由损坏快照` | `代码路径判定为 0 命中且功能树判定为 重复冗余` | `2026-03-14-active-tree-legacy-backup-cleanup` | `2026-03-14` | `removed` |
| `web/frontend/src/router/index.ts.bak.20260214` | `backup` | `mystocks_spec2` | `issue_or_task=historical-route-backup; created_at=2026-02-14` | `日期化备份快照` | `代码路径判定为 0 命中且功能树判定为 重复冗余` | `2026-03-14-active-tree-legacy-backup-cleanup` | `2026-03-14` | `removed` |
| `web/frontend/src/main.js.old` | `backup` | `mystocks_spec2` | `issue_or_task=historical-app-shell-replacement; created_at=unknown` | `旧入口文件快照` | `代码路径判定为 0 命中且功能树判定为 重复冗余` | `2026-03-14-active-tree-legacy-backup-cleanup` | `2026-03-14` | `removed` |
| `web/frontend/src/App.vue.old` | `backup` | `mystocks_spec2` | `issue_or_task=historical-app-shell-replacement; created_at=unknown` | `旧应用壳层快照` | `代码路径判定为 0 命中且功能树判定为 重复冗余` | `2026-03-14-active-tree-legacy-backup-cleanup` | `2026-03-14` | `removed` |
| `web/backend/app/api/risk_management.py.backup.20260130` | `backup` | `mystocks_spec2` | `issue_or_task=historical-api-split-backup; created_at=2026-01-30` | `风险管理旧文件备份` | `代码路径判定为 0 命中且功能树判定为 重复冗余` | `2026-03-14-active-tree-legacy-backup-cleanup` | `2026-03-14` | `removed` |
| `web/backend/app/api/data.py.backup.20260130` | `backup` | `mystocks_spec2` | `issue_or_task=historical-api-split-backup; created_at=2026-01-30` | `数据 API 旧文件备份` | `代码路径判定为 0 命中且功能树判定为 重复冗余` | `2026-03-14-active-tree-legacy-backup-cleanup` | `2026-03-14` | `removed` |
| `web/backend/app/api/technical_analysis.py.new` | `temporary-entry` | `mystocks_spec2` | `issue_or_task=historical-temporary-migration-module; created_at=unknown` | `迁移期 .new 过渡文件` | `代码路径判定为 0 命中且功能树判定为 重复冗余` | `2026-03-14-active-tree-legacy-backup-cleanup` | `2026-03-14` | `removed` |
| `src/database/database_service.py.backup.20260130` | `backup` | `mystocks_spec2` | `issue_or_task=historical-module-split-backup; created_at=2026-01-30` | `数据库服务拆分备份` | `代码路径判定为 0 命中且功能树判定为 重复冗余` | `2026-03-14-active-tree-legacy-backup-cleanup` | `2026-03-14` | `removed` |
| `src/advanced_analysis/decision_models_analyzer.py.backup.20260130` | `backup` | `mystocks_spec2` | `issue_or_task=historical-module-split-backup; created_at=2026-01-30` | `决策模型分析器拆分备份` | `代码路径判定为 0 命中且功能树判定为 重复冗余` | `2026-03-14-active-tree-legacy-backup-cleanup` | `2026-03-14` | `removed` |
| `src/monitoring/alert_manager.py.backup_complex_20251108` | `backup` | `mystocks_spec2` | `issue_or_task=historical-simplification-snapshot; created_at=2025-11-08` | `复杂告警管理器旧快照` | `代码路径判定为 0 命中且功能树判定为 重复冗余` | `2026-03-14-active-tree-legacy-backup-cleanup` | `2026-03-14` | `removed` |

## Metrics Lens

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| `scoped active-tree legacy files remaining after cleanup` | `0` | `12 targeted files before cleanup` | `N/A` | `0` | `TASK allowed paths + rg exact-name residual scan` |
| `legacy files removed in this batch` | `12` | `N/A` | `N/A` | `12` | `TASK-REPORT completed list + git diff main...HEAD` |

## Next Steps
- Historical document mentions and non-runtime metadata can be audited separately; active tree no longer needs these legacy files.

## Compatibility Notes
- Imported from archived root TASK-REPORT legacy blocks on 2026-04-03.
- Mongo is the source of truth; exported markdown is a projection for review and comparison.

## Artifact Links
- reports/governance/2026-04-03-root-TASK-REPORT.pre-mongo-cutover.md
- reports/governance/2026-03-14-active-tree-legacy-backup-cleanup.TASK.md
- reports/governance/2026-03-14-active-tree-legacy-backup-cleanup.TASK-REPORT.md
