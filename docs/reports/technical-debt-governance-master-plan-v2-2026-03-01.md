# 技术债治理执行主计划 v2（防重复发生导向）

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


- 日期：2026-03-01
- 关联 OpenSpec：`refactor-technical-debt-remediation-wave1`
- 适用范围：`web/frontend`、`web/backend/app`、`src`、`tests`
- 目标：在不牺牲交付稳定性的前提下，实现“新增技术债零增量 + 存量可持续下降 + 问题不重复发生”。

---

## 1. 治理目标与验收口径

### 1.1 北极星目标
1. 新增技术债（suppressions / 裸 TODO / 占位断言）在 PR 维度为 0。
2. 基线指标按迭代可审计下降（允许持平，不允许无审批上升）。
3. 技术债例外可追踪、可到期、可清理（双签 + TTL）。

### 1.2 统一指标（SoT）
以 `reports/analysis/tech-debt-baseline.json` 为准：
- `frontend_type_errors`
- `frontend_suppressions_count`
- `skip_xfail_count`
- `backend_todo_count`
- `backend_placeholder_count`
- `test_placeholder_assert_count`

---

## 2. 周节奏（Week-by-Week）

### Week 1（试点周）
- 范围：交易链路（前端关键页面/composable + 后端 trade API）
- 动作：
  - 启用 no-new-debt 门禁
  - 启用 baseline 比对门禁
  - 启用 debt-exception 双签校验
- 产物：
  - `reports/analysis/tech-debt-weekly-report.md`
  - `reports/analysis/tech-debt-kpi-report.json`

### Week 2（复审周）
- 动作：
  - 汇总误伤率、交付影响、审批 SLA
  - 评估是否进入全仓推广（4.3）
- 产物：
  - `docs/reports/technical-debt-stage4-4.2-governance-review-v1-2026-03-01.md`
  - `docs/reports/technical-debt-stage4-4.2-week2-review-skeleton-2026-03-08.md`

### Week 3-4（全仓分阶段推广）
- Phase A：API/composables/core paths
- Phase B：views/services/tests
- Phase C：全仓执行 + 例外到期自动清理

---

## 3. 门禁体系（执行顺序）

1. **no-new-debt gate**
   - 阻断新增 suppressions 与裸 TODO/FIXME/HACK。
2. **baseline-non-increase gate**
   - 当前指标高于基线即失败（无审批）。
3. **debt-exception 双签 gate**
   - 必须包含 owner/issue/ttl/reason/remediation
   - PR body 必须双签字段：
     - `debt-exception-tech-lead-approved: yes`
     - `debt-exception-module-owner-approved: yes`
4. **ttl-expiry gate**
   - 到期例外自动失败，必须续期审批或清理。

---

## 4. RACI（责任矩阵）

| 活动 | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| 基线采集与更新 | QA/效能 | Tech Lead | 模块负责人 | 全体开发 |
| no-new-debt 规则维护 | 平台工程 | Tech Lead | 前后端负责人 | 全体开发 |
| 例外审批 | 模块负责人 | Tech Lead | QA/效能 | 提交人 |
| 周报产出 | QA/效能 | Tech Lead | 模块负责人 | 管理层/项目成员 |
| 推广节点评审 | 模块负责人 | Tech Lead | 架构/测试 | 全体开发 |

---

## 5. 决策闸门（Go / No-Go）

### 进入 4.3 推广前必须满足
1. 误伤率 <= 10%
2. CI 平均耗时增幅 <= 15%
3. 双签例外合规率 >= 95%
4. 连续 1 周无阻塞性事故

### 回滚触发条件
- 误伤率 > 20%
- 关键流水线阻塞 > 2 小时
- 出现 P0/P1 交付事故

---

## 6. 与 OpenSpec 任务映射

- 4.1 试点：对应本计划第2节 Week1。
- 4.2 复审：对应本计划第2节 Week2 + 第5节决策闸门。
- 4.3 推广：对应本计划第2节 Week3-4 + RACI/回滚策略。

---

## 7. 审批建议

建议按“有条件批准”执行：
1. 立即执行 4.1 试点两周（按既定范围）。
2. 周末进行 4.2 评审（必须提交误伤样本与审批 SLA 数据）。
3. 达到闸门阈值后进入 4.3；未达标则留在试点并优先修复误伤源。

---

## 8. 任务卡模板引用（执行标准化）

为保证治理任务描述与验收口径一致，执行阶段统一使用：
- `docs/guides/templates/task-card-standard-template.md`

使用要求：
1. 每个治理任务必须具备“背景/目标/执行项/验收命令/风险回滚”。
2. 涉及 debt-exception 时必须填写例外元数据与双签字段。
3. 周报中的行动项必须能回溯到对应任务卡。
