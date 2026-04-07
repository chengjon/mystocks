# 技术债治理试点第 1 周周报（初稿）

> **历史总结说明**:
> 本文件是阶段性总结、报告、状态、修复记录、验证结果或交付回执，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内统计值、完成状态、结论、验证结果和修复结论如未重新复核，应视为历史快照，不得直接当作当前事实。


- 周期：第 1 周（待补：YYYY-MM-DD ~ YYYY-MM-DD）
- 试点范围：
  - 前端：`web/frontend/src/views/artdeco-pages/`、`web/frontend/src/composables/`、`web/frontend/src/api/adapters/`
  - 后端：`web/backend/app/api/trade/`
- 报告负责人：待补
- 评审人（Tech Lead / 模块负责人）：待补

---

## 1. 执行摘要

- no-new-debt 门禁：**已启用**，可运行。
- 基线对比门禁：**已启用**，当前判定为 **FAIL**（`frontend_type_errors` 高于冻结基线）。
- debt-exception 双签流程：**已落地规则与模板**，本周未补齐人工审批台账（待补）。
- 当前结论：
  - 机制层（门禁与脚本）已具备试点条件；
  - 指标层显示存在存量波动，暂不建议直接扩大范围，需先完成第 2 周观测与误伤复盘。

---

## 2. 指标快照（自动采集）

> 数据来源：
> - `reports/analysis/tech-debt-baseline.json`
> - `reports/analysis/tech-debt-current.json`
> - `reports/analysis/tech-debt-kpi-report.json`

| 指标 | 试点起始（baseline） | 当前（current） | 变化 | 结论 |
|---|---:|---:|---:|---|
| frontend_type_errors | 190 | 189 | -1 | 改善（仍高位） |
| frontend_suppressions_count | 68 | 68 | 0 | 持平 |
| skip_xfail_count | 234 | 234 | 0 | 持平 |
| backend_todo_count | 54 | 54 | 0 | 持平 |
| backend_placeholder_count | 548 | 548 | 0 | 持平 |
| test_placeholder_assert_count | 298 | 298 | 0 | 持平 |

补充信息：
- `type_check_exit_code = 2`（存在类型错误，命令非零退出）
- `generated_suppressions_count = 3`

---

## 3. KPI 与门禁结果

> 数据来源：`reports/analysis/tech-debt-kpi-report.json`

- no-new-debt 结果：**FAIL**
  - 违规项：`frontend_type_errors regressed: current=189 > baseline=183`（来自既有 KPI 报告）
- baseline-non-increase：**FAIL**
  - 违规项：`baseline metric frontend_type_errors increased: proposed=189 > previous=183`
- exception-compliance-rate：`0.035842293906810034`
- ttl-cleanup-rate：`1.0`

说明：
- 本周已完成 SoT 迁移与采集口径修正，部分历史报告基线时间点不同（183/190）会造成口径对照偏差；
- 第 2 周建议固定“同一基线文件版本”后再做趋势结论。

---

## 4. 风险热点（Top 10）

> 数据来源：`reports/analysis/tech-debt-weekly-report.md`

1. `web/frontend/src/api/types/generated-types.ts`（score 59603）
2. `web/backend/app/api/tasks.py`（11606）
3. `web/backend/app/api/dashboard.py`（9405）
4. `web/frontend/src/api/types/common/all.ts`（8984）
5. `web/backend/app/api/notification.py`（7659）
6. `tests/unit/monitoring/test_monitoring_service.py`（5850）
7. `web/frontend/src/views/artdeco-pages/ArtDecoRiskManagement.vue`（5148）
8. `tests/ci/test_continuous_integration.py`（3612）
9. `web/frontend/src/views/converted.archive/market-quotes.vue`（3423）
10. `tests/chaos/test_fault_injection.py`（2994）

---

## 5. 误伤率与交付影响（待人工补充）

### 5.1 阻断统计（待补）
- 总阻断次数：待补
- 有效阻断次数：待补
- 误伤阻断次数：待补
- 误伤率：待补（目标 <= 10%）

### 5.2 交付影响（待补）
- PR 平均 lead time（前后对比）：待补
- CI 平均耗时（前后对比）：待补
- 因门禁返工次数：待补
- 研发/测试/评审反馈：待补

---

## 6. 例外治理审计（待补）

> 双签要求：
> - `debt-exception-tech-lead-approved: yes`
> - `debt-exception-module-owner-approved: yes`

| PR | owner | issue | ttl | reason | remediation | 双签齐全 | 结论 |
|---|---|---|---|---|---|---|---|
| 待补 | 待补 | 待补 | 待补 | 待补 | 待补 | 待补 | 待补 |

---

## 7. 本周结论与下周动作

### 本周结论
1. 试点框架（门禁 + 模板 + 基线采集）已跑通。
2. 指标层面暂未形成稳定下降趋势，仍需第 2 周观测。
3. 当前不建议直接进入 4.3 全仓推广，应先完成 4.2 正式评审。

### 下周动作（建议）
1. 固定并锁定基线文件版本（避免口径漂移）。
2. 补齐误伤样本台账（Top 3）与双签例外明细。
3. 对 `frontend_type_errors` 回归项做定向清偿（优先交易主链路）。
4. 形成第 2 周报告后召开 4.2 评审会（通过/有条件通过/不通过）。

---

## 8. 审核清单（给评审人）

请重点确认：
- [ ] 本周指标是否采用同一基线口径进行对比
- [ ] 误伤率统计口径是否可复现
- [ ] 例外项双签是否真实可审计
- [ ] 是否满足进入 4.2 正式结论的前置条件
