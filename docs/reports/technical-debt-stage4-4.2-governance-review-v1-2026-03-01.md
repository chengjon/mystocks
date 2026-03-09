# 技术债治理 4.2 评审版 v1（试点第1周）

- 版本：v1
- 评审对象：`refactor-technical-debt-remediation-wave1`（4.2）
- 周期：第 1 周（待补：YYYY-MM-DD ~ YYYY-MM-DD）
- 试点范围：
  - 前端：`web/frontend/src/views/artdeco-pages/`、`web/frontend/src/composables/`、`web/frontend/src/api/adapters/`
  - 后端：`web/backend/app/api/trade/`
- 报告负责人：待补
- 评审人（Tech Lead / 模块负责人）：待补

---

## 1. 评审结论（本周）

**结论：有条件通过（继续试点，不进入全仓推广）**

依据：
1. 门禁机制已具备：no-new-debt、baseline 对比、例外双签规则均已落地。
2. 指标趋势未稳定：当前仍存在类型错误高位与口径时间点差异（183/190）。
3. 误伤率与交付影响数据尚未补齐，无法支持 4.3 全仓推广决策。

---

## 2. 核心指标快照（自动采集）

| 指标 | baseline | current | 变化 | 结论 |
|---|---:|---:|---:|---|
| frontend_type_errors | 190 | 189 | -1 | 改善（仍高位） |
| frontend_suppressions_count | 68 | 68 | 0 | 持平 |
| skip_xfail_count | 234 | 234 | 0 | 持平 |
| backend_todo_count | 54 | 54 | 0 | 持平 |
| backend_placeholder_count | 548 | 548 | 0 | 持平 |
| test_placeholder_assert_count | 298 | 298 | 0 | 持平 |

补充：
- `type_check_exit_code = 2`
- `generated_suppressions_count = 3`

---

## 3. 门禁结果（评审必看）

- no-new-debt：**FAIL**
  - 原因：`frontend_type_errors` 当前值高于所用门禁基线（历史报告口径）
- baseline-non-increase：**FAIL**
  - 原因：报告中存在 `proposed > previous` 的基线回归告警
- exception-compliance-rate：`0.035842293906810034`
- ttl-cleanup-rate：`1.0`

> 说明：当前“183/190”口径差异来自基线时间点不一致；第2周必须锁定同一基线文件版本后再做趋势结论。

---

## 4. 风险热点（Top 5）

1. `web/frontend/src/api/types/generated-types.ts`
2. `web/backend/app/api/tasks.py`
3. `web/backend/app/api/dashboard.py`
4. `web/frontend/src/api/types/common/all.ts`
5. `web/backend/app/api/notification.py`

---

## 5. 误伤率与交付影响（待补齐后复审）

### 5.1 误伤率
- 总阻断次数：待补
- 有效阻断次数：待补
- 误伤阻断次数：待补
- 误伤率：待补（目标 <= 10%）

### 5.2 交付影响
- PR 平均 lead time：待补
- CI 平均耗时增幅：待补（目标 <= 15%）
- 门禁返工次数：待补

---

## 6. 例外审计（双签）

必需字段：
- `debt-exception-tech-lead-approved: yes`
- `debt-exception-module-owner-approved: yes`

| PR | owner | issue | ttl | reason | remediation | 双签齐全 | 结论 |
|---|---|---|---|---|---|---|---|
| 待补 | 待补 | 待补 | 待补 | 待补 | 待补 | 待补 | 待补 |

---

## 7. 评审决定与进入条件

### 本周决定
- [x] 继续 4.1 试点第 2 周
- [ ] 暂不进入 4.3 全仓推广

### 进入 4.3 的前置条件（全部满足）
1. 连续 1 周误伤率 <= 10%
2. CI 平均耗时增幅 <= 15%
3. 双签例外合规率 >= 95%
4. 无阻塞性事故

---

## 8. 下周动作（执行清单）

1. 锁定单一 baseline 文件版本（消除 183/190 口径漂移）
2. 完成误伤样本台账 Top 3（含根因归类）
3. 完成双签例外审计表
4. 第 2 周结束后复审并给出“通过/有条件通过/不通过”最终结论
