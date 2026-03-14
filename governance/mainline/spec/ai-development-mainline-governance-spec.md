# AI 开发主线治理与防跑偏执行规范

> 版本：v0.2（已评审）
> 生效日期：2026-03-01
> 适用范围：MyStocks 全仓库（前端 / 后端 / 脚本 / 文档协作）
> 目标：让 AI 协作开发做到“目标明确、方向不变、增量可控、技术债可治理”

---

## 0. 与现有规范的关系（优先级）

本规范用于执行层落地，不替代上位规范：

1. 架构红线与审批门禁：`architecture/STANDARDS.md`（最高约束）
2. 提案与变更流程：`openspec/AGENTS.md`
3. 技术债治理章程：`docs/guides/technical-debt-governance-charter-v1.md`
4. 本文：把上位规则收敛为“任务卡 + 机器门禁 + CI 执行”

若冲突，以 1-3 项为准。

---

## 1. 核心治理目标（Single Mainline）

### 1.1 唯一主线原则
任何开发活动都必须映射到同一条主线目标树：

- L1 北极星目标（一个阶段仅 1 个）
- L2 里程碑目标（3-5 个）
- L3 可交付切片（可测试、可演示、可回滚）

准入规则：无法映射到 L2/L3 的任务，不进入当前迭代。

### 1.2 主线偏移判定
出现以下任一项，判定为偏离主线：

1. 引入未批准的新功能。
2. 修改任务白名单外模块。
3. 未声明副类型却发生跨类型改动。
4. 在无审批情况下进行架构/菜单/UI 风格调整。

### 1.3 主线偏移率（可审计口径）

- 公式：`主线偏移率 = 越界改动文件数 / 本次改动文件总数`
- 统计窗口：PR 维度 + 周维度（周报汇总）
- 数据源：`git diff` + `governance/mainline/reports/mainline-governance-report.json`

阶段阈值：

- 阶段 A（当前）：`<= 5%`
- 阶段 B（稳定后）：`<= 2%`
- 阶段 C（目标态）：`= 0%`

---

## 2. 治理落地节奏（分阶段双层）

### 2.1 Phase A（立即生效）

- PR 硬门禁：CI 必过，否则禁止合并。
- 本地校验：允许软提示，不阻断提交。

### 2.2 Phase B（1-2 周后）

- 本地 `pre-commit` 从软提示升级为硬门禁。
- 仍以 PR CI 结果为最终合并依据。

> 原则：先在 PR 建立客观约束，再逐步前移到开发端，避免一刀切卡死流程。

---

## 3. 任务卡制度（机器可执行）

### 3.1 文件组织

- 模板：`governance/mainline/templates/ai-task-card.yaml`
- Schema：`governance/mainline/schemas/ai-task-card.schema.json`
- 实例：`governance/mainline/task-cards/<task-or-pr-id>.yaml`
- `TASK.md` 仅保留索引与状态，不承载结构化字段。

### 3.2 必填字段（最小集合）

每个任务卡必须包含：

- `mainline.id`
- `classification.task_type`
- `classification.secondary_type`
- `function_tree.domain_id`
- `function_tree.node_id`
- `function_tree.affected_entrypoints`
- `function_tree.update_status`
- `scope.allowed_paths`
- `non_goals`
- `acceptance.checks`
- `risk_and_rollback.rollback_plan`
- `delivery.six_line_summary`
- `openspec.change_id`（Feature 必填）
- `openspec.approval_status`（Feature 必须为 `approved`）

---

## 4. 任务类型治理（主类型 + 受限副类型）

### 4.1 主类型

- `fix`：修补任务
- `feature`：新增任务
- `cleanup`：清理任务

### 4.2 副类型约束

允许声明一个副类型，但必须满足：

1. 明确 `classification.secondary_type != none`。
2. 提供 `classification.secondary_allowed_paths`。
3. 提供 `classification.secondary_change_budget_percent`。
4. 副类型预算不超过 20%。
5. 有审批标记（`governance.approval` 字段完整）。

副类型预算口径：

`副类型改动占比 = 副类型路径命中的改动文件数 / 本次改动文件总数`

超过预算即失败。

---

## 5. 三道门机制（机器化）

### 5.1 门一：准入门（开工前）

由 `mainline_scope_gate.py` 校验：

- 任务卡存在
- 任务卡符合 JSON Schema
- Feature 与 OpenSpec 审批状态匹配
- `function_tree` 声明与 catalog、git diff 一致
- 白名单路径合法

### 5.2 门二：输出门（开发后）

六行摘要必须结构化写入 `delivery.six_line_summary`：

1. `change_purpose`
2. `modified_scope`
3. `dependency_changes`
4. `legacy_logic_impact`
5. `rollback_ready`
6. `risk_and_rollback_point`

缺失任一字段判定不合规。

### 5.3 门三：提交门（合并前）

必须通过“本次改动范围冗余自检”：

1. 未使用变量/函数/类
2. 重复逻辑
3. 注释掉的废弃代码
4. 可合并重复片段
5. 死代码

规则：只清理本次引入，不扩大范围。

---

## 6. Feature 强绑定 OpenSpec

当 `classification.task_type = feature` 时：

1. `openspec.change_id` 必填且非空。
2. `openspec.approval_status` 必须为 `approved`。
3. 未满足上述条件，CI 直接失败。

---

## 7. Stop Rules（触发、恢复、SLA）

### 7.1 触发条件（任一满足即触发）

1. 质量门连续失败（lint/test/typecheck/style）。
2. 同模块短周期重复返工 > 2 次。
3. 新功能依赖历史补丁层叠加才能继续。
4. 核心文件复杂度持续上升且无拆分计划。

### 7.2 状态机

`triggered -> remediation -> verified -> resumed`

- `triggered`：暂停 Feature，仅允许 Fix/Cleanup。
- `remediation`：执行治理计划。
- `verified`：满足恢复条件，等待审批。
- `resumed`：恢复 Feature 开发。

### 7.3 恢复条件（必须全部满足）

1. 连续 2 次完整质量门通过。
2. 无新增技术债（不高于基线）。
3. 责任人和治理截止时间已登记。
4. 审批字段齐全（owner + note + timestamp）。

### 7.4 SLA

- 默认治理响应 SLA：24 小时内进入 `remediation`。
- 默认冻结上限：72 小时，超时必须升级决策。

---

## 8. 技术债治理配额（与章程一致）

- 迭代债务配额下限：`>= 15%`
- Stop Rule 触发后临时提升：`30%`
- 回落条件：关键基线回到阈值内

基线和周报沿用：

- `reports/analysis/tech-debt-baseline.json`
- `reports/analysis/tech-debt-weekly-report.md`
- `reports/analysis/tech-debt-kpi-report.json`

---

## 9. 自动化文件与职责

### 9.1 模板与 Schema

- `governance/mainline/templates/ai-task-card.yaml`：人工填写模板
- `governance/mainline/schemas/ai-task-card.schema.json`：机器校验规则

### 9.2 门禁脚本

- `governance/mainline/scripts/mainline_scope_gate.py`

能力：

- 任务卡 Schema 校验
- OpenSpec 绑定校验
- function-tree catalog 校验
- `function_tree` 节点 / 入口 / 跨域 / 自举校验
- 白名单/黑名单路径校验
- 主线偏移率计算
- 副类型预算校验
- 输出 JSON 报告

### 9.3 CI 工作流

- `.github/workflows/mainline-governance.yml`

Phase A：仅在 PR 硬门禁。

---

## 10. 评估指标（可审计）

1. 主线偏移率：`越界文件数 / 改动文件总数`
2. 返工率：`同模块重复修复次数 / 模块总修复次数`
3. 冗余引入率：`(本次新增冗余项数 / 本次改动文件数)`
4. 一次通过率：`首次通过门禁任务数 / 总任务数`

指标必须记录：公式、阈值、数据源、统计窗口。

---

## 11. 执行清单

### 11.1 开工前

- [ ] 任务卡已创建并通过 Schema
- [ ] 任务主类型已锁定
- [ ] 若有副类型，预算与审批字段完整
- [ ] 白名单路径已定义
- [ ] 验收标准可执行

### 11.2 开发中

- [ ] 无越界改动
- [ ] 无未声明的副类型改动
- [ ] 仅交付最小可完成切片

### 11.3 提交前

- [ ] 六行摘要已完整填写
- [ ] 冗余自检通过
- [ ] 质量门通过
- [ ] 可回滚方案可执行

---

## 12. 结论

AI 长期不跑偏，必须从“口头约束”升级为“可验证机制”：

- 有边界：主线 + 路径白名单 + 非目标
- 有粒度：主类型 + 受限副类型
- 有门禁：Schema + Scope Gate + CI
- 有恢复：Stop Rule 状态机 + SLA
- 有数据：指标公式化、周报化、可审计
