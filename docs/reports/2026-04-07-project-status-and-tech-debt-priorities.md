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

---

## 2. Recommended Priority Order

### Priority 1: Finish Phase 2 Inventory First

先完成 Phase 2 的“只盘点、不删除”子阶段，产出 `DELETION-CANDIDATES.md`。

这是当前最重要的动作，因为：

- `architecture/STANDARDS.md` 明确要求删除前同时完成“代码路径判定”和“功能树判定”
- 当前 5 个目标层仍有残余调用和兼容职责，不能仅凭 grep 结果直接删除
- 这一产物是后续重定向、合并和删除的审批前提

目标范围：

- `src/routes/`
- `src/api/`
- `src/data_access_pkg/`
- `src/db_manager/`
- `src/database_optimization/`

核心输出：

- 每个目标目录的文件级清单
- 功能归属
- 调用方证据
- 保留/删除建议
- 重定向目标
- 验证命令

主要参考：

- `.planning/phases/02-dead-code-inventory-removal/02-CONTEXT.md`
- `.planning/phases/02-dead-code-inventory-removal/02-RESEARCH.md`
- `.planning/phases/02-dead-code-inventory-removal/02-PLAN-01-inventory.md`

### Priority 2: Redirect Callers And Merge Overlapping Layers

在盘点完成后，执行 Phase 2 的重定向和合并动作。

重点包括：

- 把 `src/routes` / `src/api` / `src/db_manager` 的残余调用迁移到 canonical 位置
- 把 `src/database_optimization` 中仍有价值的实现并入 `src/data_access/optimizers/`
- 查清 `src/data_access_pkg/tdengine_access.py` 与 `src/data_access/tdengine_access.py` 的体积差异和责任边界

主要参考：

- `.planning/phases/02-dead-code-inventory-removal/02-PLAN-02-redirect-callers.md`
- `.planning/phases/02-dead-code-inventory-removal/02-PLAN-03-merge-overlapping.md`

当前执行状态：

- 该优先级已开始执行
- 第一批已经完成：Wencai 调用方重定向、`database_optimization` 向 `src/data_access/optimizers/` 的合并、脚本/测试导入修复
- 尚未完成：`scripts/cicd_pipeline.sh` 的 `src.routes` 烟雾检查替换、`src/data_access_pkg/*` 其余覆盖率核实、真正的目录删除

### Priority 3: Delete Dead Layers Only After Approval

在你审批 `DELETION-CANDIDATES.md` 后，再执行真正的删除动作。

删除目标为：

- `src/routes/`
- `src/api/`
- `src/data_access_pkg/`
- `src/database_optimization/`
- `src/db_manager/`

这一步必须视为单独的批准点，不应与前两步合并执行。

主要参考：

- `.planning/phases/02-dead-code-inventory-removal/02-PLAN-04-approved-deletion.md`

### Priority 4: Phase 3 Frontend Structural Consolidation

Phase 2 收口后，下一梯队是前端结构收敛。

重点包括：

- 先确认真实 frontend entry truth source
- 合并大小写冲突目录
- 清理多余 `main-*` 入口
- 收敛 `views/composables/`
- 清理 `views/demo/` 与 `views/converted.archive/`

这是部署与模块解析风险，优先级高于命名美化类问题。

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

当前还能明确看到两项流程债：

- Phase 2 计划工件已存在，但自动进度统计未正确识别
- 当前工作树极度脏：`git status --short | wc -l` 为 `2887`

这会直接影响：

- 变更 blast radius 判断
- 回归定位
- 阶段验证可信度

---

## 5. Suggested Execution Sequence

建议按下面顺序推进：

1. 保持 `DELETION-CANDIDATES.md` 作为删除审批稿，并补充本批次已完成状态
2. 完成 Phase 2 剩余“非删除”动作：`scripts/cicd_pipeline.sh`、`src/data_access_pkg` 覆盖核实、残余 caller 清理
3. 复核 Phase 2 删除前验证命令
4. 经单独审批后删除历史层
5. 进入 Phase 3 前端结构收敛
6. 最后做 Phase 4 命名与 shim 收尾

---

## 6. Reference Files

- `/opt/claude/mystocks_spec/.planning/PROJECT.md`
- `/opt/claude/mystocks_spec/.planning/ROADMAP.md`
- `/opt/claude/mystocks_spec/.planning/codebase/CONCERNS.md`
- `/opt/claude/mystocks_spec/.planning/phases/01-python-lint-baseline/01-SUMMARY.md`
- `/opt/claude/mystocks_spec/.planning/phases/02-dead-code-inventory-removal/02-CONTEXT.md`
- `/opt/claude/mystocks_spec/.planning/phases/02-dead-code-inventory-removal/02-RESEARCH.md`
- `/opt/claude/mystocks_spec/.planning/phases/02-dead-code-inventory-removal/02-PLAN-01-inventory.md`
- `/opt/claude/mystocks_spec/.planning/phases/02-dead-code-inventory-removal/02-PLAN-02-redirect-callers.md`
- `/opt/claude/mystocks_spec/.planning/phases/02-dead-code-inventory-removal/02-PLAN-03-merge-overlapping.md`
- `/opt/claude/mystocks_spec/.planning/phases/02-dead-code-inventory-removal/02-PLAN-04-approved-deletion.md`
- `/opt/claude/mystocks_spec/reports/analysis/tech-debt-baseline.json`
- `/opt/claude/mystocks_spec/reports/analysis/tech-debt-current-real-week2-day5.json`
