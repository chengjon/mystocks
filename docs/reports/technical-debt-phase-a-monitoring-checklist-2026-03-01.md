# Phase A 推广监控清单（Week 1）

> **历史任务说明**:
> 本文件用于保留某次历史任务拆解、检查清单或阶段性待办，不代表当前仍需按原样执行。
> 其中的勾选状态、优先级和执行顺序仅对应当时上下文；继续沿用前应先对照当前需求、现行实现与最新验证结果重新校准。

**执行范围：** `web/frontend/src/api/**` + `web/frontend/src/composables/**` + `web/backend/app/api/**`  
**启动时间：** 2026-03-01  
**监控周期：** Week 1 Day 1-5  
**目标：** 验证误伤率 ≤10%、CI 增幅 ≤15%、双签合规 ≥95%、无阻塞事故

---

## 1. 日常监控指标（Day 1-5 每日采集）

### 1.1 误伤率（False Positive Rate）
- [ ] Day 1：采集 no-new-debt 触发次数 + 有效阻断数 + 误伤数
- [ ] Day 2：采集并对比 Day 1 趋势
- [ ] Day 3：采集并对比 Day 1-2 平均值
- [ ] Day 4：采集并对比 Day 1-3 平均值
- [ ] Day 5：采集并计算 Week 1 最终误伤率
  - **目标：** ≤ 10%
  - **数据源：** `reports/analysis/tech-debt-kpi-report-week1-phase-a-*.json`
  - **计算公式：** 误伤数 / 总触发数

### 1.2 CI 平均耗时增幅（CI Time Increase）
- [ ] Day 1：记录 CI 平均耗时（baseline）
- [ ] Day 2：记录 CI 平均耗时 + 计算增幅 %
- [ ] Day 3：记录 CI 平均耗时 + 计算增幅 %
- [ ] Day 4：记录 CI 平均耗时 + 计算增幅 %
- [ ] Day 5：记录 CI 平均耗时 + 计算 Week 1 平均增幅
  - **目标：** ≤ 15%
  - **数据源：** CI/CD 日志 + `reports/analysis/ci-performance-week1-phase-a-*.json`
  - **计算公式：** (当前耗时 - baseline) / baseline × 100%

### 1.3 双签合规率（Exception Compliance Rate）
- [ ] Day 1：采集异常审批数 + 双签通过数
- [ ] Day 2：采集并对比 Day 1 趋势
- [ ] Day 3：采集并对比 Day 1-2 平均值
- [ ] Day 4：采集并对比 Day 1-3 平均值
- [ ] Day 5：采集并计算 Week 1 最终合规率
  - **目标：** ≥ 95%
  - **数据源：** `reports/analysis/exception-compliance-week1-phase-a-*.json`
  - **计算公式：** 双签通过数 / 总异常数

### 1.4 TTL 清理率（TTL Cleanup Rate）
- [ ] Day 1：采集 TTL 清理覆盖数 + 总 TODO 数
- [ ] Day 2：采集并对比 Day 1 趋势
- [ ] Day 3：采集并对比 Day 1-2 平均值
- [ ] Day 4：采集并对比 Day 1-3 平均值
- [ ] Day 5：采集并计算 Week 1 最终清理率
  - **目标：** ≥ 100%（全覆盖）
  - **数据源：** `reports/analysis/ttl-gate-report-week1-phase-a-*.json`
  - **计算公式：** 清理覆盖数 / 总 TODO 数

---

## 2. 阻塞事故监控（Day 1-5 实时）

### 2.1 门禁阻塞事故
- [ ] Day 1：记录是否有 no-new-debt 门禁阻塞 PR 合并
  - 若有：记录 PR 号、阻塞原因、解决时间
  - 若无：记录"无阻塞"
- [ ] Day 2：同上
- [ ] Day 3：同上
- [ ] Day 4：同上
- [ ] Day 5：同上
  - **目标：** 连续 1 周无阻塞（≤ 0 次）
  - **数据源：** Git 提交日志 + CI/CD 日志 + Slack 告警

### 2.2 CI 超时事故
- [ ] Day 1：记录是否有 CI 超时（>30min）
  - 若有：记录原因、影响范围、解决时间
  - 若无：记录"无超时"
- [ ] Day 2：同上
- [ ] Day 3：同上
- [ ] Day 4：同上
- [ ] Day 5：同上
  - **目标：** 无 P0 超时事故
  - **数据源：** CI/CD 日志 + 告警系统

### 2.3 双签审批延迟
- [ ] Day 1：记录异常审批平均延迟时间
- [ ] Day 2：记录异常审批平均延迟时间
- [ ] Day 3：记录异常审批平均延迟时间
- [ ] Day 4：记录异常审批平均延迟时间
- [ ] Day 5：记录异常审批平均延迟时间 + 计算 Week 1 平均
  - **目标：** ≤ 2 小时
  - **数据源：** 审批系统日志

---

## 3. 代码质量监控（Day 1-5 每日采集）

### 3.1 新增债务检测
- [ ] Day 1：采集新增债务模式数（no-new-debt violations）
- [ ] Day 2：采集新增债务模式数 + 对比 Day 1
- [ ] Day 3：采集新增债务模式数 + 对比 Day 1-2 平均
- [ ] Day 4：采集新增债务模式数 + 对比 Day 1-3 平均
- [ ] Day 5：采集新增债务模式数 + 计算 Week 1 总数
  - **目标：** = 0（零新增）
  - **数据源：** `reports/analysis/tech-debt-kpi-report-week1-phase-a-*.json`

### 3.2 基线指标变化
- [ ] Day 1：记录 baseline 指标快照（frontend_type_errors 等）
- [ ] Day 2：记录当前指标 + 对比 baseline + 输出 drift 分类
- [ ] Day 3：记录当前指标 + 对比 baseline + 输出 drift 分类
- [ ] Day 4：记录当前指标 + 对比 baseline + 输出 drift 分类
- [ ] Day 5：记录当前指标 + 计算 Week 1 变化趋势 + 汇总 drift 分类
  - **目标：** 指标不增加（≤ baseline）
  - **数据源：** `reports/analysis/tech-debt-baseline-drift-report-week1-phase-a-*.json`
  - **记录要求：** 每日区分 `gated drift` 与 `observed drift`，观察项不得直接计入阻断事故。

### 3.3 误伤样本分析
- [ ] Day 1：采集误伤样本（false positive 文件列表）
- [ ] Day 2：采集误伤样本 + 分析模式
- [ ] Day 3：采集误伤样本 + 分析模式
- [ ] Day 4：采集误伤样本 + 分析模式
- [ ] Day 5：采集误伤样本 + 生成 Top 5 误伤文件报告
  - **数据源：** `reports/analysis/false-positive-analysis-week1-phase-a-*.json`
  - **输出：** `docs/reports/technical-debt-phase-a-false-positive-analysis-2026-03-05.md`

---

## 4. 周末汇总（Day 5 下午）

### 4.1 生成 Week 1 Phase A 执行报告
- [ ] 汇总所有日常指标（误伤率、CI 增幅、双签合规、TTL 清理）
- [ ] 汇总所有阻塞事故（门禁、CI、审批延迟）
- [ ] 汇总代码质量变化（新增债务、基线变化、误伤样本）
- [ ] 汇总 baseline drift 结论（gated/observed 分列）
- [ ] 生成报告文件：`docs/reports/technical-debt-phase-a-week1-execution-report-2026-03-05.md`

### 4.2 评估 Phase B 进入条件
- [ ] 误伤率 ≤ 10%？ ✓ / ✗
- [ ] CI 增幅 ≤ 15%？ ✓ / ✗
- [ ] 双签合规 ≥ 95%？ ✓ / ✗
- [ ] 连续 1 周无阻塞？ ✓ / ✗
- [ ] **决策：** 是否启动 Phase B？

### 4.3 更新 tasks.md
- [ ] 标记 Phase A 完成状态
- [ ] 记录 Week 1 最终指标
- [ ] 更新 Phase B 启动状态（若满足条件）

### 4.4 生成 Phase B 任务卡（若启动）
- [ ] 创建 `docs/reports/technical-debt-task-card-sample-04-rollout-phase-b-2026-03-08.md`
- [ ] 定义 Phase B 执行范围：`web/frontend/src/views/**` + `web/backend/app/services/**` + `tests/**`
- [ ] 定义 Phase B 启动时间：2026-03-08（Week 2）

---

## 5. 数据源清单

| 指标 | 数据源文件 | 采集频率 | 负责人 |
|------|----------|--------|------|
| 误伤率 | `tech-debt-kpi-report-week1-phase-a-day*.json` | 每日 | QA/Efficiency |
| CI 增幅 | CI/CD 日志 + `ci-performance-week1-phase-a-*.json` | 每日 | DevOps |
| 双签合规 | `exception-compliance-week1-phase-a-*.json` | 每日 | Tech Lead |
| TTL 清理 | `ttl-gate-report-week1-phase-a-*.json` | 每日 | QA/Efficiency |
| 阻塞事故 | Git 日志 + CI 日志 + Slack | 实时 | 所有人 |
| 新增债务 | `tech-debt-kpi-report-week1-phase-a-*.json` | 每日 | QA/Efficiency |
| 基线变化 | `tech-debt-baseline-drift-report-week1-phase-a-*.json` | 每日 | QA/Efficiency |
| 误伤样本 | `false-positive-analysis-week1-phase-a-*.json` | 每日 | QA/Efficiency |

---

## 6. 风险回滚触发条件

**若出现以下情况，立即启动回滚：**

- [ ] 误伤率 > 20%（严重误伤）
- [ ] CI 增幅 > 30%（严重性能下降）
- [ ] 双签合规 < 50%（审批流程崩溃）
- [ ] 连续 2 次 P0 阻塞事故（门禁失效）
- [ ] 新增债务 > 5 个（防线突破）

**回滚步骤：**
1. 禁用 Phase A 范围内的所有门禁规则
2. 恢复 baseline 对比为"警告"模式（非阻塞）
3. 生成回滚报告：`docs/reports/technical-debt-phase-a-rollback-report-*.md`
4. 分析根本原因并调整规则
5. 重新启动 Phase A（修正版）

---

## 7. 检查清单使用说明

**每日操作流程：**
1. 上午：采集前一天的指标数据
2. 中午：分析数据趋势，识别异常
3. 下午：更新本清单，记录发现
4. 晚间：若有阻塞事故，立即通知 Tech Lead

**周末操作流程：**
1. 汇总 Week 1 所有数据
2. 生成执行报告
3. 评估 Phase B 进入条件
4. 若满足条件，启动 Phase B 任务卡生成

---

**清单生成时间：** 2026-03-01  
**清单版本：** v1.0  
**维护人：** QA/Efficiency Team + Tech Lead
