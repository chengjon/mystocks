# TASK-REPORT

> Exported from Mongo control plane. Human notes may be appended, but active state lives in Mongo.

- Issue Identifier: `2026-03-14-active-tree-legacy-cleanup-mystocks-spec2`
- Issue Title: `Classify and clean active-tree legacy backup files`
- Assigned Worker CLI: `mystocks_spec2`
- Current Status: `merged`
- Latest Progress: Active-Tree Legacy Backup Cleanup
- Pending Request: `False`

## Updates
- `2026-03-14T00:00:45` [merged] mystocks_spec2: Active-Tree Legacy Backup Cleanup

## Requests
- (none)

## Graphiti

- server_status: `ok`
- ingest_status: `completed`
- search_summary: `nodes hit=9, facts hit=12`

## Detailed Updates

### `2026-03-14T00:00:45` [merged] mystocks_spec2
- Summary: Active-Tree Legacy Backup Cleanup

#### Scope
- 按 `TASK.md` 仅处理 12 个 active-tree legacy / backup / broken 文件。
- 目标是完成“代码路径判定 + 功能树判定”，只删除已证明 `重复冗余` 的对象。

#### Completed
- 1. 删除了以下 12 个已证明 `重复冗余` 的文件：
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
- 2. 保留结论：
- 本批次没有任何文件需要按 `有效` / `兼容保留` / `待判定` 留在 active tree。
- 当前可见的剩余引用仅存在于历史文档与非运行时元数据，不构成代码路径阻塞。

#### Structural Debt Disclosure
- canonical_source: `active tree 中仅保留无 legacy 后缀的现行运行时模块与入口：web/frontend/src/main.js、web/frontend/src/App.vue、web/frontend/src/router/index.ts、web/backend/app/api/risk_management.py、web/backend/app/api/data/__init__.py、web/backend/app/api/technical_analysis.py、src/database/database_service.py、src/advanced_analysis/decision_models_analyzer.py、src/monitoring/alert_manager.py。`
- compatibility_surface: `active tree 不再保留 legacy backup / broken / old / .new 文件；剩余同名痕迹仅允许存在于历史文档或非运行时元数据。`
- callers_or_consumers: `frontend 入口 main.js -> App.vue / router/index.ts；backend 路由注册链路 -> risk_management.py / api.data / technical_analysis.py；src 侧调用方继续依赖无 legacy 后缀的现行模块。`
- verification_command: `rg -n --hidden --glob '!*.git' "RiskMonitor\\.vue\\.broken|BacktestAnalysis\\.vue\\.broken|index\\.ts\\.broken|index\\.ts\\.bak\\.20260214|main\\.js\\.old|App\\.vue\\.old|risk_management\\.py\\.backup\\.20260130|data\\.py\\.backup\\.20260130|technical_analysis\\.py\\.new|database_service\\.py\\.backup\\.20260130|decision_models_analyzer\\.py\\.backup\\.20260130|alert_manager\\.py\\.backup_complex_20251108" web/frontend/src web/backend/app src`；`git -c safe.directory=/opt/claude/mystocks_spec2 diff --check`；`python -m py_compile web/backend/app/api/risk_management.py web/backend/app/api/data/__init__.py web/backend/app/api/technical_analysis.py src/database/database_service.py src/advanced_analysis/decision_models_analyzer.py src/monitoring/alert_manager.py`
- exit_condition: `N/A；本批次目标就是完成终态删除，不保留 active-tree 兼容层。`

#### Cleanup / Removal Decision
- code_path_verdict: `safe-to-remove`
- function_tree_verdict: `重复冗余`
- removal_basis: `12 个对象均通过后缀精确扫描证明不再参与 active code path，功能树也已被无 legacy 后缀的现行实现覆盖。`
- keep_reason: `N/A；剩余历史提及仅属于归档文档或非运行时元数据，不构成保留 active-tree legacy 文件的依据。`

#### Temporary / Compatibility Asset Ledger Delta

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

#### Metrics Lens

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| `scoped active-tree legacy files remaining after cleanup` | `0` | `12 targeted files before cleanup` | `N/A` | `0` | `TASK allowed paths + rg exact-name residual scan` |
| `legacy files removed in this batch` | `12` | `N/A` | `N/A` | `12` | `Completed list + git diff --name-status main...HEAD` |

#### Verification Evidence
- 1. 精确残留扫描：
- 命令：
- `rg -n --hidden --glob '!*.git' "RiskMonitor\\.vue\\.broken|BacktestAnalysis\\.vue\\.broken|index\\.ts\\.broken|index\\.ts\\.bak\\.20260214|main\\.js\\.old|App\\.vue\\.old|risk_management\\.py\\.backup\\.20260130|data\\.py\\.backup\\.20260130|technical_analysis\\.py\\.new|database_service\\.py\\.backup\\.20260130|decision_models_analyzer\\.py\\.backup\\.20260130|alert_manager\\.py\\.backup_complex_20251108" web/frontend/src web/backend/app src`
- 结果：
- 返回码 `1`
- 标准输出为空
- 说明：active code trees 中已无上述 legacy 文件名残留
- 2. Git diff 格式检查：
- 命令：
- `git -c safe.directory=/opt/claude/mystocks_spec2 diff --check`
- 结果：
- 通过，无 whitespace / conflict marker 问题
- 3. 当前工作树实际变更面：
- 命令：
- `git -c safe.directory=/opt/claude/mystocks_spec2 status --short`
- 结果：
- 本轮相关变更为 `TASK-REPORT.md` + 12 个目标文件删除
- 另有 `TASK.md` 为派单前置脏改，未在本轮修改
- 4. 相对 `main` 的真实交付范围：
- 命令：
- `git -c safe.directory=/opt/claude/mystocks_spec2 diff --name-status main...HEAD`
- `git -c safe.directory=/opt/claude/mystocks_spec2 diff --check main...HEAD`
- 结果：
- 仅包含 `TASK-REPORT.md` 和 12 个目标文件删除
- `diff --check main...HEAD` 通过
- 5. 现行替代模块语法检查：
- 命令：
- `python -m py_compile web/backend/app/api/risk_management.py web/backend/app/api/data/__init__.py web/backend/app/api/technical_analysis.py src/database/database_service.py src/advanced_analysis/decision_models_analyzer.py src/monitoring/alert_manager.py`
- 结果：
- 通过
- 6. GitNexus 变更探测（按规范执行，但结果受 worktree / index freshness 限制污染）：
- 命令：
- `gitnexus_detect_changes(scope="all")`
- `gitnexus_detect_changes(scope="staged")`
- `gitnexus_detect_changes(scope="compare", base_ref="main")`
- 结果：
- `scope="all"` 与 `scope="compare"` 返回高噪声 `critical`
- `scope="staged"` 返回 `No changes detected`
- 该工具对本轮“删除 legacy 备份文件 + worktree 既有历史状态”的组合不够稳定
- 解释：
- 本轮实际交付范围以 `git diff --name-status main...HEAD` 和 `git status --short` 为准
- 7. 探索性回归（非本次门禁，但已记录）：
- 命令：
- `pytest web/backend/tests/test_large_file_split_regressions.py tests/unit/monitoring/test_alert_manager_simplified.py -q`
- 结果：
- `13 failed, 44 passed`
- 失败归因（均不指向已删除文件）：
- `tests/unit/monitoring/test_alert_manager_simplified.py`
- 失败原因：测试文件未导入 `AlertManager`，直接实例化触发 `NameError`
- `web/backend/tests/test_large_file_split_regressions.py::test_strategy_management_module_stays_below_850_lines`
- 失败原因：`web/backend/app/api/strategy_management/get_monitoring_db.py` 当前为 `930` 行，超出门禁
- `web/backend/tests/test_large_file_split_regressions.py::test_cache_api_split_helpers_remain_importable`
- `web/backend/tests/test_large_file_split_regressions.py::test_notification_module_remains_importable`
- 失败原因：`app.core.config` 因缺失必需环境变量触发 `SystemExit: 1`
- 结论：
- 该命令暴露的是仓库既有测试/环境债务，不是本次 legacy 删除回归

#### Current Status
- 12 个 active-tree legacy / backup / broken 文件已完成双层判定并删除，active runtime code path 只保留现行无后缀实现。
- 当前剩余同名痕迹仅位于历史文档与非运行时元数据，不构成 active tree 保留依据。

#### Next
- 如需继续治理，只应处理历史文档或 `.omc` 等非运行时元数据中的名称残留，不需要恢复这些 active-tree legacy 文件。

#### Risks / Notes
- Startup Blockers / Read-First Gaps:
- 1. `git fetch origin` / `git rebase main`
- 初始阻塞原因：早先沙箱无法写上游主仓库的 worktree git metadata。
- 初始报错：`cannot open '/opt/claude/mystocks_spec/.git/worktrees/mystocks_spec2/FETCH_HEAD': Read-only file system`
- 后续处理结果：
- 权限放开后已成功执行 `git fetch origin`
- 已成功执行 `git rebase main`
- 当前分支已同步到 `main` 最新提交 `e4ecf083 (feat(maestro): enable env-auth mongo coordination)`
- 同步前核对：
- `git -c safe.directory=/opt/claude/mystocks_spec2 rev-list --left-right --count main...HEAD` -> `1 0`
- `git -c safe.directory=/opt/claude/mystocks_spec2 diff --stat HEAD..main` 仅涉及：
- `scripts/runtime/maestro_collab.py`
- `tests/unit/runtime/test_maestro_coordination_cli.py`
- 上述差异均不在本任务允许范围内，因此先提交本轮清理，再 rebase 吃入该修复提交。
- 2. Mongo control plane `coordctl`
- 阻塞原因：Mongo 鉴权不可用。
- 实际报错：`pymongo.errors.OperationFailure: Command createIndexes requires authentication`
- 影响：
- 无法执行 `work show`
- 无法执行 `work mark/update add`
- 本轮进度仅能先落在 `TASK-REPORT.md`
- 3. `TASK.md` 指定的 3 份必读文档在仓库中不存在：
- `docs/reports/ARCHITECTURE_ASSESSMENT_REPORT.md`
- `docs/reports/API_VERSION_CONFLICT_INVESTIGATION.md`
- `docs/guides/multi-cli-tasks/MONGO_MULTICLI_OPERATION_CHECKLIST.md`
- 替代读取：
- `docs/plans/2026-03-14-architecture-api-remediation-worker-allocation.md`
- `docs/guides/multi-cli-tasks/MONGO_MULTICLI_COORDINATION_GUIDE.md`
- `docs/reports/plans/compatibility-inventory.md`
- `docs/reports/plans/code-simplification-notes.md`
- Classification and Action:
- | 文件 | 状态判定 | 动作 | 代码路径判定 | 功能树判定 |
- |---|---|---|---|---|
- | `web/frontend/src/views/RiskMonitor.vue.broken` | `重复冗余` | 已删除 | 对后缀文件名在 `web/frontend/src` 精确扫描为 `0`；当前 `main.js` 只加载 `router/index.ts`，现行 `router/index.ts` 风控路由指向 ArtDeco 页面 | `docs/reports/EMERGENCY_FIX_COMPLETION_REPORT.md` 说明它是临时重命名的损坏页面；当前风险功能树已转到 `ArtDecoRiskManagement.vue` / `risk-tabs/*` |
- | `web/frontend/src/views/BacktestAnalysis.vue.broken` | `重复冗余` | 已删除 | 对后缀文件名在 `web/frontend/src` 精确扫描为 `0`；现行 `router/index.ts` 的回测路由指向 `ArtDecoBacktestAnalysis.vue` | `EMERGENCY_FIX_COMPLETION_REPORT.md` 说明它是临时重命名的损坏页面；当前回测功能树已转到 ArtDeco 策略页 |
- | `web/frontend/src/router/index.ts.broken` | `重复冗余` | 已删除 | 对后缀文件名在 `web/frontend/src` 精确扫描为 `0`；当前入口 `web/frontend/src/main.js` 明确导入 `./router/index.ts` | 属于旧路由快照，功能树已被当前 `router/index.ts` 覆盖 |
- | `web/frontend/src/router/index.ts.bak.20260214` | `重复冗余` | 已删除 | 对后缀文件名在 `web/frontend/src` 精确扫描为 `0`；当前入口只使用 `router/index.ts` | 属于日期备份快照，功能树已被当前 `router/index.ts` 覆盖 |
- | `web/frontend/src/main.js.old` | `重复冗余` | 已删除 | 对后缀文件名在 `web/frontend/src` 精确扫描为 `0`；当前活动入口是 `web/frontend/src/main.js` | `web/frontend/FRONTEND_FIX_IMPLEMENTATION_GUIDE.md` 将其标记为替换入口文件时产生的临时旧文件 |
- | `web/frontend/src/App.vue.old` | `重复冗余` | 已删除 | 对后缀文件名在 `web/frontend/src` 精确扫描为 `0`；当前活动入口从 `main.js` 导入 `./App.vue` | `FRONTEND_FIX_IMPLEMENTATION_GUIDE.md` 将其标记为替换 App 壳层时产生的临时旧文件 |
- | `web/backend/app/api/risk_management.py.backup.20260130` | `重复冗余` | 已删除 | 对后缀文件名在 `web/backend/app` 精确扫描为 `0`；现行注册链路导入的是 `web/backend/app/api/risk_management.py` | `docs/reports/phase1.4_risk_management_split_progress.md` 标记其为“备份原文件”；现行 `risk_management.py` 是指向 `app.api.risk` 的弃用 shim |
- | `web/backend/app/api/data.py.backup.20260130` | `重复冗余` | 已删除 | 对后缀文件名在 `web/backend/app` 精确扫描为 `0`；现行注册链路导入的是包级 facade `web/backend/app/api/data/__init__.py` | `docs/reports/phase1_complete_execution_summary_report.md` 标记其为“备份原文件”；当前数据功能树由 `api/data/*` 子路由和 `data_api_new.py` 兼容层承接 |
- | `web/backend/app/api/technical_analysis.py.new` | `重复冗余` | 已删除 | 对后缀文件名在 `web/backend/app` 精确扫描为 `0`；`api.__init__`、`register_routers.py`、`router_registry.py` 均导入现行 `technical_analysis.py` | `docs/reports/plans/compatibility-inventory.md` 与 `code-simplification-notes.md` 都把它列为零引用删除候选；现行技术分析模块存在且可编译 |
- | `src/database/database_service.py.backup.20260130` | `重复冗余` | 已删除 | 对后缀文件名在 `src` 精确扫描为 `0`；现行代码树使用 `src/database/services/database_service.py` 与 `src/database/database_service.py` | `docs/reports/phase1.2_database_service_split_completion.md` 明确它是拆分时备份的原文件 |
- | `src/advanced_analysis/decision_models_analyzer.py.backup.20260130` | `重复冗余` | 已删除 | 对后缀文件名在 `src` 精确扫描为 `0`；GitNexus 图谱命中活跃 `DecisionModelsAnalyzer` 位于 `src/advanced_analysis/decision_models_analyzer.py` | `docs/reports/phase1.1_decision_models_split_completion.md` 明确它是拆分时备份的原文件；活跃类仍由 `src/advanced_analysis/__init__.py` 调用 |
- | `src/monitoring/alert_manager.py.backup_complex_20251108` | `重复冗余` | 已删除 | 对后缀文件名在 `src` 精确扫描为 `0`；GitNexus 图谱命中活跃 `AlertManager` 位于 `src/monitoring/alert_manager.py` | 活跃文件头部注释明确“复杂多渠道告警已迁移到 Grafana”；备份文件仅是简化前快照 |
- Residual Risks / Notes:
- 1. 历史文档仍提到已删除文件名，例如：
- `web/frontend/FRONTEND_FIX_IMPLEMENTATION_GUIDE.md`
- `docs/reports/EMERGENCY_FIX_COMPLETION_REPORT.md`
- `docs/reports/phase1_complete_execution_summary_report.md`
- 这些引用属于历史迁移记录，不构成运行时代码路径
- 2. `.omc` 元数据仍可能保留旧文件名：
- 按 `TASK.md` 明确要求，本轮未触碰 `.omc/**`
- 该类引用属于非运行时记忆数据，不作为保留 active-tree legacy 文件的依据
- 3. 由于 Mongo control plane 鉴权阻塞，本轮尚无法把状态回写为 `in_progress` / `ready_for_review`
- 即使在 rebase 到 `e4ecf083` 之后，`coordctl` 仍失败
- 进一步核对：
- worktree 根目录不存在 `.env`
- 当前 shell 中也不存在 `MONGODB_ROOT_USERNAME` / `MONGODB_ROOT_PASSWORD` / `MAESTRO_COLLAB_MONGO_URI` 等变量
- `coordctl` 现行逻辑会从 `.env` 或环境变量读取 Mongo 凭据；在缺失凭据时只能匿名连接，最终触发 `Command createIndexes requires authentication`
- 交付状态已完整记录在本文件，待具备凭据后可由 main CLI 或后续会话补写
- Git Delivery Snapshot:
- 1. 本轮清理提交：
- `4ef9ecb7`
- `chore(cleanup): remove active-tree legacy backups`
- 2. 当前分支基线：
- 已 rebase 到 `main` 的 `e4ecf083`
- 3. 当前工作树状态：
- 仅剩 `TASK.md` 为未提交派单文件改动
- 本轮实现文件已全部在提交中
