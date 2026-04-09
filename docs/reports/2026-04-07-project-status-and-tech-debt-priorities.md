# Project Status And Tech Debt Priorities

> **历史文档说明**:
> 本文件用于保存一次针对当前项目状态、未完成项目和技术负债的整理结论，供后续执行阶段参考。
> 当前共享规则与审批门禁仍以 `architecture/STANDARDS.md` 为准；本文件不是代码实现或治理口径的唯一事实来源。

**Generated:** 2026-04-07  
**Branch observed:** `wip/root-dirty-20260403`

---

## 1. Current Status

当前主线项目是一次代码库收敛治理工作，而不是新功能项目。

按 `.planning/PROJECT.md` 与 `.planning/ROADMAP.md`：

- 总阶段数: 4
- 已完成阶段: 1
- 当前阶段: Phase 2 `Dead Code Inventory & Removal`
- 当前状态: `batch-1-executing`

### Completed

- Phase 1 已完成：Python lint baseline
- `ruff` 总错误数从 `1456` 降到 `877`
- `W293` / `F841` / `W291` 已清零

参考：

- `.planning/phases/01-python-lint-baseline/01-SUMMARY.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`

### Important Caveat

Phase 2 目录中已经存在 4 份计划文件，但自动进度工具仍把该阶段统计为 `plan_count: 0`。这说明 `.planning` 工件命名与自动统计规则之间存在口径偏差，本身也是一项流程治理债务。

### Batch 1 Execution Update

截至 2026-04-07，本次会话已实际完成 Phase 2 第一批“只重定向/合并、不删除”的工作：

- `src/database/services/database_service.py` 已去掉对 `src.routes.wencai_routes` 的依赖，改为桥接到 canonical service 层，并保留 `USE_MOCK_DATA=true` 的 mock 路径
- `src/data_access.py` 已从 `data_access_pkg` shim 改为转发到 canonical `src.data_access`
- `src/database_optimization/` 下 4 个优化器类已并入 `src/data_access/optimizers/`
- 相关测试和脚本导入已切换到 canonical 位置
- `tests/api_contract_tests.py` 中对不存在的 `src.api.types.*` 导入已移除

本批次验证结果：

- `ruff check` 通过
- `pytest tests/unit/database_optimization/test_performance_monitor.py -q --no-cov -o addopts=''`: `22 passed`
- `pytest scripts/tests/test_database_optimization.py -q --no-cov -o addopts=''`: `45 passed`
- `pytest tests/api_contract_tests.py -q --no-cov -o addopts=''`: `no tests ran`
- GitNexus `impact` 检查中，本批涉及的优化器类与导入修复函数均为 `LOW` 风险
- GitNexus `detect_changes(scope="staged")`: `changed_files: 14`, `risk_level: low`

### Workspace Truth Update

补充检查发现，当前工作区中以下历史目录已经不存在：

- `src/routes/`
- `src/api/`
- `src/data_access_pkg/`
- `src/db_manager/`
- `src/database_optimization/`

这意味着 `.planning` 和历史盘点文档中的 Phase 2 “待删除对象”在当前仓库真相下应重新解释为：

- 已发生过的历史收敛动作
- 或旧计划口径滞后于当前工作区

### 2026-04-09 Status Sync

补充执行记录表明，两条此前容易被反复重开的治理线已经基本收口：

- 文档治理 / state 控制面：
  - `9ced0498b docs(governance): reclose recurring worklogs root`
  - `2549953ab docs(state): refresh root task control snapshots`
  - 这意味着 `docs/worklogs/` 复发、root `TASK.md` / `TASK-REPORT.md` 快照漂移，当前都应视为已关闭输入，而不是下一轮待办
- 技术债治理脚本真值：
  - `bd7579111 governance(tech-debt): standardize default drift report artifact`
  - `baseline-drift-report` 的默认产物名已统一为 `reports/analysis/tech-debt-baseline-drift-report.json`
  - `tests/unit/test_tech_debt_governance_gate.py` 已锁定该默认值
  - 定点验证：`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=. pytest -o addopts='' tests/unit/test_tech_debt_governance_gate.py` = `14 passed`

这对后续优先级的直接影响是：

- 不再把 `docs/worklogs/` 复发收口列为当前主线待办
- 不再把 drift report 默认产物命名列为待统一事项
- 文档治理剩余工作转向仍然过度暴露的 guide family，继续按 family wave 收薄导航面
- 当前主代码线优先级仍保持为 Phase 2 历史收口真相对齐，其后才进入 `docs/reports/2026-04-07-phase3-4-execution-matrix.md` 对应的前端结构批次

---

## 2. Recommended Priority Order

### Priority 1: Reconcile Historical Phase 2 Docs With Workspace Truth

先把 Phase 2 历史计划、盘点稿与当前工作区真相对齐。

这是当前最重要的动作，因为：

- 当前工作区里相关目录已经不存在，若继续沿用“待删除”口径，会误导后续执行
- 仍然有少量旧字符串引用和历史文档描述没有收口
- 需要把“删除审批稿”转为“历史收敛审计稿”

目标范围：

- `src/routes/`
- `src/api/`
- `src/data_access_pkg/`
- `src/db_manager/`
- `src/database_optimization/`

核心输出：

- 当前工作区真相说明
- 历史目录与 canonical 目标的对应关系
- 残余引用与旧文档待修项
- 后续验证命令

主要参考：

- `.planning/phases/02-dead-code-inventory-removal/02-CONTEXT.md`
- `.planning/phases/02-dead-code-inventory-removal/02-RESEARCH.md`
- `.planning/phases/02-dead-code-inventory-removal/02-01-PLAN.md`

### Priority 2: Finish Residual Caller And Comment Cleanup

继续处理残余调用方、脚本字符串映射和旧注释。

重点包括：

- 清理对历史目录的残余字符串引用
- 修正仍然提到 `src.database_optimization` 的测试注释和文档
- 持续验证 `src.data_access` / `src.data_access.optimizers` 是当前唯一真相源

主要参考：

- `.planning/phases/02-dead-code-inventory-removal/02-02-PLAN.md`
- `.planning/phases/02-dead-code-inventory-removal/02-03-PLAN.md`

当前执行状态：

- 该优先级已开始执行
- 第一批已经完成：Wencai 调用方重定向、`database_optimization` 向 `src/data_access/optimizers/` 的合并、脚本/测试导入修复
- `scripts/cicd_pipeline.sh` 当前已直接检查 `web/backend/app.main`
- 下一步重点转为残余文档/注释/字符串引用收口

### Priority 3: Verify Canonical Layer Coverage

继续验证 canonical 层是否完全承接历史职责，特别是：

- `src.data_access`
- `src.data_access.optimizers`
- `web/backend/app/*`

### Priority 4: Phase 3 Frontend Structural Consolidation

Phase 2 收口后，下一梯队是前端结构收敛。

重点包括：

- 先按已确认事实固化 frontend entry truth source：`index.html -> /src/main-standard.ts -> /src/router/index.ts`
- 合并大小写冲突目录
- 清理多余 `main-*` 入口
- 收敛 `views/composables/`
- 清理 `views/demo/` 与 `views/converted.archive/`

这是部署与模块解析风险，优先级高于命名美化类问题。

补充审计结论：

- `views/announcement/AnnouncementMonitor.vue` 当前仍是 `router/index.ts` 的现役路由页面
- `views/stocks/` 当前仍被 `watchlist/Screener.vue` 与 `src/composables/market/useDataAnalysis.ts` 直接复用
- `views/monitoring/` 在本次审计范围内未发现现役 `router/index.ts` / `views/*` / `src/composables/*` import，但仍有历史 `router/index.js*` 与测试 spec 痕迹，现阶段应标为“待判定”而不是“可删”
- `views/monitoring/` 功能树状态已经单独补完，当前目录级口径应为 `historical router targets + test-guarded monitoring assets`
- `views/composables/` 当前主要服务 root-level legacy views（如 `Analysis.vue`、`TradingDashboard.vue`、`TechnicalAnalysis.vue` 等）的相对路径引用，不应直接迁移
- `main-standard.ts` 是当前 HTML 真入口，但 `main.js` 仍被 `web/frontend/verify-mount.js` 直接读取，入口变体治理仍需先做 caller 分类
- `views/composables/usePhase4Dashboard.ts` 与 `views/demo/composables/usePhase4Dashboard.ts` 是分叉实现，不是薄包装
- `views/composables/useTechnicalAnalysis.ts` 与 `views/technical/composables/useTechnicalAnalysis.ts` 也是分叉实现，应作为 Phase 3/4 的重复实现候选单独治理
- `views/composables/` 文件级状态已经单独补完，当前目录级判断应为 `root-level legacy view support + partial test guards + duplicate-candidates`
- `views/demo/`、`views/converted.archive/`、`views/examples/` 当前更接近“测试守护资产/历史示例资产”，不是当前主路由真相，也不能直接按死代码目录处理
- `Phase4Dashboard` 这组重复实现目前更像“历史路由资产 + demo资产”的并存，而不是同一真相源的简单重命名
- `TechnicalAnalysis` 这组重复实现目前更像“离开主路由后的双分叉存量”，治理重点应放在功能树判定，而不是先机械合并
- `Phase4Dashboard` / `TechnicalAnalysis` 双分叉功能树判定已经单独补完，当前可直接区分 `canonical`、`历史保留`、`示例资产`、`独立分叉待判定`
- `phase4.routes.js` 在当前审计范围内未发现被现役路由聚合链引用，因此 `Phase4Dashboard` root 版本更像脱离主链的旧路由资产
- `phase4.routes.js` 还引用了缺失文件 `StrategyMgmtPhase4.vue`，说明该路由文件本身也已具备“过期残留”特征
- `market/Technical.vue` 已被 `market-route-canonical-paths.spec.ts` 与 `domain-body-migration-ownership.spec.ts` 明确约束为 canonical technical page
- 历史路由资产状态已经单独补完：
  - `src/router/index.js` = `historical legacy router asset`
  - `src/router/index.js.clean` = `historical broken backup / stale working copy`
  - `src/router/index.js.backup-phase2.3` = `historical backup`
  - `src/router/phase4.routes.js` = `stale route asset`
- `index.js.clean` 不是可靠“干净备份”，因为文件内部已出现重复嵌套路由对象，不能再作为可运行历史样本使用
- 下一步执行前置清单已整理到 `docs/reports/2026-04-07-phase3-execution-preconditions.md`
- 历史路由资产专门报告已整理到 `docs/reports/2026-04-07-legacy-router-asset-status.md`
- `views/monitoring` 专门报告已整理到 `docs/reports/2026-04-07-monitoring-functional-status.md`
- `views/composables` 专门报告已整理到 `docs/reports/2026-04-07-views-composables-status.md`
- 双分叉页面功能树专门报告已整理到 `docs/reports/2026-04-07-duplicate-page-functional-status.md`
- 可执行批次矩阵已整理到 `docs/reports/2026-04-07-phase3-4-execution-matrix.md`

### Priority 5: Phase 4 Naming And Shim Polish

最后处理：

- root shim 处置：`core.py`、`data_access.py`、`monitoring.py`
- `calcu/`
- `part1.py` / `part2.py` / `part3.py`
- `*_new.py`
- `*.bak` / `*.backup`
- Pinia store 职责边界重叠

---

## 3. Main Unfinished Work

按 `.planning/PROJECT.md` 当前 Active 项，未完成主项包括：

- 修复 frontend case-conflict directories
- 继续降低剩余 ruff errors
- 合并重叠 data access layers
- 路由层收敛，移除 `src/routes/` 与 `src/api/`
- 清理 frontend entry points
- 整理 frontend structural mess
- 解决 root-level shim chains
- 修复 naming conventions
- 收敛重叠 Pinia stores

---

## 4. Key Technical Debt

### 4.1 Structural Debt

来自 `.planning/codebase/CONCERNS.md` 的关键结构债务：

- P0: adapter 重复层
- P0: frontend 大小写冲突目录
- P1: 多套 data access 层并存
- P1: routes 分散在三套位置
- P1: 测试数量高但质量与信噪比不足
- P2: frontend 结构混乱
- P2: backend API 目录膨胀
- P2: root shim chain
- P2: naming / mechanical split 问题

### 4.2 Static Quality Debt

按 `reports/analysis/tech-debt-baseline.json`（2026-04-05）：

- `frontend_type_errors`: `0`
- `frontend_suppressions_count`: `0`
- `skip_xfail_count`: `0`
- `backend_todo_count`: `0`
- `backend_placeholder_count`: `0`

但后端静态分析仍有：

- `total_issues`: `1253`
- `security_issues`: `49`
- `docstring_issues`: `619`
- `type_annotation_issues`: `400`
- `pydantic_issues`: `119`
- `endpoint_function_issues`: `174`

说明前端类型债当前基线较干净，但后端静态质量债仍较重。

### 4.3 Historical Debt Signals

按历史快照 `reports/analysis/tech-debt-current-real-week2-day5.json`（2026-03-01）：

- `frontend_type_errors`: `131`
- `frontend_suppressions_count`: `67`
- `skip_xfail_count`: `234`
- `backend_todo_count`: `54`
- `backend_placeholder_count`: `548`
- `test_placeholder_assert_count`: `298`

这些数字不应直接视为当前值，但说明测试层、占位代码和抑制项曾经积累较重。

### 4.4 Process Debt

按 2026-04-07 生成本报告时的工作树快照，仍能明确看到两项流程债：

- Phase 2 计划工件已存在，但自动进度统计未正确识别
- 当次工作树极度脏：`git status --short | wc -l` 观测值为 `2887`

这会直接影响：

- 变更 blast radius 判断
- 回归定位
- 阶段验证可信度

---

## 5. Suggested Execution Sequence

建议按下面顺序推进：

1. 把 Phase 2 文档解释为历史收敛审计稿，而不是当前待删除清单
2. 完成残余 caller / 注释 / 文档字符串收口
3. 继续验证 canonical 层覆盖完整性
4. 进入 Phase 3 前端结构收敛
5. 最后做 Phase 4 命名与 shim 收尾

---

## 6. Reference Files

- `/opt/claude/mystocks_spec/.planning/PROJECT.md`
- `/opt/claude/mystocks_spec/.planning/ROADMAP.md`
- `/opt/claude/mystocks_spec/.planning/codebase/CONCERNS.md`
- `/opt/claude/mystocks_spec/.planning/phases/01-python-lint-baseline/01-SUMMARY.md`
- `/opt/claude/mystocks_spec/.planning/phases/02-dead-code-inventory-removal/02-CONTEXT.md`
- `/opt/claude/mystocks_spec/.planning/phases/02-dead-code-inventory-removal/02-RESEARCH.md`
- `/opt/claude/mystocks_spec/.planning/phases/02-dead-code-inventory-removal/02-01-PLAN.md`
- `/opt/claude/mystocks_spec/.planning/phases/02-dead-code-inventory-removal/02-02-PLAN.md`
- `/opt/claude/mystocks_spec/.planning/phases/02-dead-code-inventory-removal/02-03-PLAN.md`
- `/opt/claude/mystocks_spec/.planning/phases/02-dead-code-inventory-removal/02-04-PLAN.md`
- `/opt/claude/mystocks_spec/docs/reports/2026-04-07-legacy-router-asset-status.md`
- `/opt/claude/mystocks_spec/docs/reports/2026-04-07-monitoring-functional-status.md`
- `/opt/claude/mystocks_spec/docs/reports/2026-04-07-views-composables-status.md`
- `/opt/claude/mystocks_spec/docs/reports/2026-04-07-duplicate-page-functional-status.md`
- `/opt/claude/mystocks_spec/docs/reports/2026-04-07-phase3-4-execution-matrix.md`
- `/opt/claude/mystocks_spec/docs/reports/2026-04-07-frontend-structure-repo-truth-audit.md`
- `/opt/claude/mystocks_spec/docs/reports/2026-04-07-phase3-execution-preconditions.md`
- `/opt/claude/mystocks_spec/reports/analysis/tech-debt-baseline.json`
- `/opt/claude/mystocks_spec/reports/analysis/tech-debt-current-real-week2-day5.json`
