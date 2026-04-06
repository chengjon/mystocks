# MyStocks 前端主线测试 Phase 3 详细推进表

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、任务方案或执行矩阵，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值和时间线如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


> Historical Plan Snapshot Date: 2026-04-03
> 上游总纲：`docs/plans/2026-04-02-frontend-mainline-testing-overall-plan.md`
> Historical Scope Snapshot: Phase 3 十二个页面的 Mock / Real 双轨验证与修复推进

## 1. 目标

Phase 3 聚焦两条高价值主链：

1. 策略页是否能在 Mock / Real 下稳定表达策略配置、信号、回测与优化联动。
2. 交易页是否能在 Mock / Real 下稳定完成仓位、组合、信号、历史与终端控制的最小闭环。

本批次页面：

- `Strategy-Repo`
- `Strategy-Parameters`
- `Strategy-Signals`
- `Strategy-Backtest`
- `Strategy-GPU`
- `Strategy-Opt`
- `Strategy-Pos`
- `Trade-Positions`
- `Trade-Terminal`
- `Trade-Signals`
- `Trade-Portfolio`
- `Trade-History`

## 2. 进入条件

执行 Phase 3 前，固定先确认以下条件：

### 2.1 页面真值

- 路由真值：`web/frontend/src/router/index.ts`
- 功能树真值：`docs/FUNCTION_TREE.md`
- 主链清单真值：`docs/plans/frontend-page-optimization-list.md`

### 2.2 方案编写时已知事实

- `Strategy-Repo`、`Strategy-Parameters`、`Strategy-Signals`、`Strategy-Backtest`、`Strategy-GPU`、`Strategy-Opt`、`Strategy-Pos`、`Trade-Positions`、`Trade-Terminal`、`Trade-Signals`、`Trade-Portfolio`、`Trade-History` 已在主链清单中标记为 Phase 3 页面。
- `Strategy-Repo`、`Strategy-Backtest` 已存在可复用 E2E；
  其余页面需要补齐统一矩阵验证口径。
- 按方案编写时记录，Phase 2 已完成，当时运行态口径为：
  - `mystocks-backend`: `http://localhost:8020`
  - `mystocks-frontend`: `http://localhost:3020`
  - `http://localhost:8020/health/ready` = `200`

### 2.3 运行前提

Mock 轨：

- 前端可独立启动
- 后端可不在线
- Readiness probe 允许 stub
- 若测试依赖 Playwright route stub，必须显式关闭前端内置 mock 短路

Real 轨：

- `mystocks-backend` 必须可访问
- `http://localhost:8020/health` 必须可达
- `http://localhost:8020/health/ready` 必须为 `200`

## 3. 执行顺序

Phase 3 固定按以下顺序推进：

1. `Strategy-Repo`
2. `Strategy-Parameters`
3. `Strategy-Signals`
4. `Strategy-Backtest`
5. `Strategy-GPU`
6. `Strategy-Opt`
7. `Strategy-Pos`
8. `Trade-Positions`
9. `Trade-Terminal`
10. `Trade-Signals`
11. `Trade-Portfolio`
12. `Trade-History`

原因：

- 先走策略配置、参数、信号、回测、优化的上游链，确认策略域上下游上下文联动。
- 再走交易仓位、终端、信号、组合、历史，确认交易域读写闭环。

## 4. 统一执行模型

每个页面都固定跑以下 4 层：

1. `route-shell`
2. `mock-render`
3. `real-read`
4. `real-write/degrade`

对本批次而言，`real-write/degrade` 重点适用于：

- `Strategy-Repo`
- `Strategy-Backtest`
- `Trade-Terminal`

其余页面优先验证真实读链与空态/错态降级，不强求所有写动作都真闭环。

## 5. Phase 3 页面矩阵

### 5.1 Strategy-Repo

- 路由：`/strategy/repo`
- 组件：`web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue`
- Canonical 接口：`/api/v1/strategy/strategies`
- Mock 轨要求：
  - 策略表格、状态徽标、搜索与筛选工具条可见
  - create/update/delete/lifecycle 入口存在
- Real 轨要求：
  - 真实策略列表可映射为表格行
  - 快速回测、编辑、删除入口不静默失败

### 5.2 Strategy-Parameters

- 路由：`/strategy/parameters`
- 组件：`web/frontend/src/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue`
- Canonical 接口：`/api/v1/strategy/strategies`
- Mock 轨要求：
  - 参数工作台、快照区、优化联动统计卡可见
- Real 轨要求：
  - 真实策略列表/详情可映射为参数快照
  - query 上下文切换不破坏页面

### 5.3 Strategy-Signals

- 路由：`/strategy/signals`
- 组件：`web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
- Canonical 接口：`/api/v1/trade/signals`
- Mock 轨要求：
  - 信号时间轴、统计卡、请求元信息可见
- Real 轨要求：
  - 真实信号列表可映射为时间轴项
  - 空数据时不崩溃

### 5.4 Strategy-Backtest

- 路由：`/strategy/backtest`
- 组件：`web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
- Canonical 接口族：
  - `/api/v1/strategy/backtest/run`
  - `/api/v1/strategy/backtest/status/{id}`
  - `/api/v1/strategy/backtest/results/{id}`
- Mock 轨要求：
  - 回测工作流、任务区、日志区、报告区可见
  - run/status/result 最小链可在 stub 下闭环
- Real 轨要求：
  - 真实回测读链可进入任务/结果视图
  - 写链失败时要有明确提示

### 5.5 Strategy-GPU

- 路由：`/strategy/gpu`
- 组件：`web/frontend/src/views/strategy/BacktestGPU.vue`
- Canonical 接口族：
  - `/api/gpu/status`
  - `/api/gpu/performance`
- Mock 轨要求：
  - GPU 状态卡、监控面板、基准测试入口可见
- Real 轨要求：
  - 真实状态与性能读链可消费
  - benchmark/reset 至少能清晰降级

### 5.6 Strategy-Opt

- 路由：`/strategy/opt`
- 组件：`web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`
- Canonical 接口：`/api/v1/strategy/strategies`
- Mock 轨要求：
  - 优化候选表、回写入口、状态摘要可见
- Real 轨要求：
  - 真实策略候选或空态可稳定渲染
  - 回写跳转链不静默失败

### 5.7 Strategy-Pos

- 路由：`/strategy/pos`
- 组件：`web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue`
- Canonical 接口：`/api/v1/trade/positions`
- Mock 轨要求：
  - 持仓表、统计卡、请求元信息可见
- Real 轨要求：
  - 真实持仓列表可映射为仓位行
  - 空数据时不塌陷

### 5.8 Trade-Positions

- 路由：`/trade/positions`
- 组件：`web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue`
- Canonical 接口：`/api/v1/trade/positions`
- Mock / Real 轨要求与 `Strategy-Pos` 类似，但按交易域路由独立验证

### 5.9 Trade-Terminal

- 路由：`/trade/terminal`
- 组件：`web/frontend/src/views/TradingDashboard.vue`
- Canonical 接口族：
  - `/api/trading/status`
  - `/api/trading/strategies/performance`
  - `/api/trading/market/snapshot`
  - `/api/trading/risk/metrics`
  - `/api/trading/start`
  - `/api/trading/stop`
- Mock 轨要求：
  - 终端总览、状态区、启动/停止入口可见
  - stub 写链后能给出明确反馈
- Real 轨要求：
  - 四条主读链可达
  - 启停等写链失败时不静默

### 5.10 Trade-Signals

- 路由：`/trade/signals`
- 组件：`web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoSignalsView.vue`
- Canonical 接口：`/api/v1/trade/signals`
- Mock 轨要求：
  - 信号卡、质量评估区、历史区可见
- Real 轨要求：
  - 真实信号响应可映射到交易信号视图

### 5.11 Trade-Portfolio

- 路由：`/trade/portfolio`
- 组件：`web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`
- Canonical 接口：`/api/v1/trade/positions`
- Mock 轨要求：
  - 组合统计卡、资产面板、列表区可见
- Real 轨要求：
  - 真实持仓可映射为组合统计

### 5.12 Trade-History

- 路由：`/trade/history`
- 组件：`web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue`
- Canonical 接口：`/api/v1/trade/trades`
- Mock 轨要求：
  - 历史记录表、金额统计、筛选区可见
- Real 轨要求：
  - 真实成交记录可映射为历史表格
  - 空态/错态不崩溃

## 6. 推荐验证资产

- 现有可复用：
  - `web/frontend/tests/e2e/strategy-management-chain.spec.ts`
  - `web/frontend/tests/e2e/strategy-backtest.spec.ts`
  - `web/frontend/tests/e2e/strategy-monitor.spec.ts`
  - `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts`
- 本阶段应新增：
  - 一份 `Phase 3` 专用主线矩阵测试资产，补齐 `Trade-*` 与剩余 `Strategy-*` 页面

## 7. 报告要求

Phase 3 每轮推进后，报告中至少包含：

- 每页 `Mock / Real` 结论
- 问题分类：
  - `route/config drift`
  - `frontend render gap`
  - `backend contract/runtime gap`
- 实际执行命令
- 浏览器项目
- 通过/失败/跳过数量
- PM2 服务状态与访问地址

## 8. 下一批进入条件

Phase 3 结束后，必须能明确回答：

1. 策略域是否具备从仓库到参数、信号、回测、优化的最小闭环。
2. 交易域是否具备从头寸到终端、信号、组合、历史的最小闭环。
3. 哪些页面仍是“真实读链可用、真实写链待补”的状态。

下一批为：

- `Risk-Management`
- `Risk-Overview`
- `Risk-PnL`
- `Risk-StopLoss`
- `Risk-Alerts`
- `Risk-News`
- `System-Config`
- `System-Health`
- `System-API`
- `System-Data`
