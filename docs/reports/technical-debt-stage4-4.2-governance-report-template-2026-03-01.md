# Stage 4.2 首轮治理报告模板（含误伤率与交付影响）

> **历史总结说明**:
> 本文件是阶段性总结、报告、状态、修复记录、验证结果或交付回执，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内统计值、完成状态、结论、验证结果和修复结论如未重新复核，应视为历史快照，不得直接当作当前事实。


## 1. 基本信息
- 报告周期：
- 试点范围：
- 版本/分支：
- 报告负责人：
- 评审人（Tech Lead / 模块负责人）：

## 2. 核心结论（执行摘要）
- no-new-debt 门禁结论：
- 基线不增门禁结论：
- baseline drift 复核结论：
- 例外双签流程结论：
- 是否建议进入全仓推广：是 / 否（说明原因）

## 3. 指标对比（试点起始 vs 当前）
| 指标 | 起始值 | 当前值 | 变化 | 结论 |
|---|---:|---:|---:|---|
| frontend_type_errors |  |  |  |  |
| frontend_suppressions_count |  |  |  |  |
| skip_xfail_count |  |  |  |  |
| backend_todo_count |  |  |  |  |
| backend_placeholder_count |  |  |  |  |
| test_placeholder_assert_count |  |  |  |  |

## 4. 门禁效果评估
### 4.1 阻断统计
- 总阻断次数：
- 有效阻断次数：
- 误伤阻断次数：

### 4.2 误伤率
- 误伤率 = 误伤阻断次数 / 总阻断次数
- 目标阈值（建议）：<= 10%

### 4.3 典型误伤案例（Top 3）
1. 现象：
   - 根因：
   - 处理：
   - 是否需规则调整：
2. ...

### 4.4 baseline drift 复核
- 基线文件：
- 当前实测文件：
- drift 报告文件：
- gated drift 项：
- observed drift 项：
- 结论：观察项是否被错误计入阻断结论？

## 5. 交付影响评估
- PR 平均 lead time（前后对比）：
- CI 平均耗时（前后对比）：
- 因治理门禁导致的返工次数：
- 主观反馈（开发/测试/评审）：

## 6. 例外治理审计
| PR | owner | issue | ttl | reason | remediation | 双签是否齐全 | 结论 |
|---|---|---|---|---|---|---|---|

## 7. 风险与改进项
- 当前风险：
- 改进动作：
- 预计完成时间：

## 8. 评审结论
- 结论：通过 / 有条件通过 / 不通过
- 进入 4.3 条件：
- 待办事项：
- 证据命令：
  - `python scripts/dev/quality_gate/collect_tech_debt_baseline.py --output <current-metrics-json>`
  - `python scripts/dev/quality_gate/tech_debt_governance_gate.py baseline-drift-report --baseline reports/analysis/tech-debt-baseline.json --current <current-metrics-json> --output <drift-report-json> --only-drifted`
