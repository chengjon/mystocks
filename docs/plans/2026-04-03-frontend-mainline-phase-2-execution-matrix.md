# MyStocks 前端主线测试 Phase 2 详细推进表

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、任务方案或执行矩阵，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值和时间线如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


> Historical Plan Snapshot Date: 2026-04-03
> 上游总纲：`docs/plans/2026-04-02-frontend-mainline-testing-overall-plan.md`
> Historical Scope Snapshot: Phase 2 六个页面的 Mock / Real 双轨验证与修复推进

## 1. 目标

Phase 2 聚焦两条链：

1. 数据分析页是否能在 Mock / Real 下稳定表达真实读链。
2. 自选管理页是否至少具备最小读链和基本交互闭环。

本批次页面：

- `Data-Concept`
- `Data-FundFlow`
- `Data-Indicator`
- `Watchlist-Manage`
- `Watchlist-Signals`
- `Watchlist-Screener`

## 2. 进入条件

执行 Phase 2 前，固定先确认以下条件：

### 2.1 页面真值

- 路由真值：`web/frontend/src/router/index.ts`
- 功能树真值：`docs/FUNCTION_TREE.md`
- 主链清单真值：`docs/plans/frontend-page-optimization-list.md`

### 2.2 方案编写时已知事实

- `Data-Concept`、`Data-FundFlow`、`Data-Indicator`、`Watchlist-Manage`、`Watchlist-Signals`、`Watchlist-Screener` 已在 `frontend-page-optimization-list.md` 标记为主链活跃页。
- 方案编写时仓库没有这 6 页的专用稳定 Phase 2 E2E，需要新增一份矩阵测试资产补缺。
- 按方案编写时记录，`Phase 1` 已完成，当时运行态口径为：
  - `mystocks-backend`: `http://localhost:8020`
  - `mystocks-frontend`: `http://localhost:3020`
  - `http://localhost:8020/health/ready` = `200`

### 2.3 运行前提

Mock 轨：

- 前端可独立启动
- 后端可不在线
- Readiness probe 允许 stub

Real 轨：

- `mystocks-backend` 必须可访问
- `http://localhost:8020/health` 必须可达
- `http://localhost:8020/health/ready` 必须为 `200`

## 3. 执行顺序

Phase 2 固定按以下顺序推进：

1. `Data-Concept`
2. `Data-FundFlow`
3. `Data-Indicator`
4. `Watchlist-Manage`
5. `Watchlist-Signals`
6. `Watchlist-Screener`

原因：

- 先验证 3 个读链导向的数据分析页，快速暴露接口消费与映射问题。
- 再进入 3 个自选管理页，补读链与最小交互闭环。

## 4. 统一执行模型

每个页面都固定跑以下 4 层：

1. `route-shell`
2. `mock-render`
3. `real-read`
4. `real-write/degrade`

对本批次而言，`real-write/degrade` 重点适用于：

- `Watchlist-Manage`
- `Watchlist-Screener`

其余页面优先验证真实读链与空态/错态降级，不强求写链。

## 5. Phase 2 页面矩阵

## 5.1 Data-Concept

### 页面基线

- 路由：`/data/concept`
- 组件：`web/frontend/src/views/data/Concepts.vue`
- 功能域：数据分析 / 概念板块
- 当前已知关键 DOM：
  - `.market-concept-tab`
  - `概念板块工作台`
  - `概念强弱与龙头面板`
  - `刷新板块`
  - `REQ:`

### Canonical 接口

- `/api/v2/market/sector/fund-flow`
  - 参数：`sector_type=概念`
  - 参数：`timeframe=今日`
  - 参数：`limit=20`

### 现有可复用测试

- `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts`

### Mock 轨要求

- stub 概念板块接口后，工作台壳层、统计卡、表格区均可见
- 主力净流入和龙头股字段可映射展示
- 空数据时不白屏，仍保留表格结构

### Real 轨要求

- 真实响应可映射为概念板块行
- `REQ:` 位可显化
- 真实空数据时页面结构保持完整

### 通过条件

- 工作台标题可见
- 概念表格可见
- 至少一行概念数据可见
- 刷新按钮可点击且不破坏页面

### 高概率问题分类

- `backend contract/runtime gap`
- `frontend render gap`

## 5.2 Data-FundFlow

### 页面基线

- 路由：`/data/fund-flow`
- 组件：`web/frontend/src/views/data/FundFlow.vue`
- 功能域：数据分析 / 资金流向
- 当前已知关键 DOM：
  - `.fund-flow-analysis`
  - `资金流向工作台`
  - `近30日资金流向趋势`
  - `个股资金流向排行`
  - `刷新资金流`

### Canonical 接口族

- `/api/akshare/market/fund-flow/hsgt-summary`
- `/api/akshare/market/fund-flow/big-deal`

### 现有可复用测试

- `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts`

### Mock 轨要求

- stub 北向资金与大单排行后，概览卡、趋势图、排行表格均可见
- 时间窗口和排序方式控件可见
- 任一单条接口失败时不白屏

### Real 轨要求

- 真实北向资金摘要可映射为概览卡与趋势图
- 真实大单排行可映射为表格
- 真实空数据时工作台结构保持完整

### 通过条件

- 工作台标题可见
- 趋势图容器可见
- 排行表格可见
- 刷新按钮可点击

### 高概率问题分类

- `backend contract/runtime gap`
- `frontend render gap`

## 5.3 Data-Indicator

### 页面基线

- 路由：`/data/indicator`
- 路由入口：`web/frontend/src/views/data/Advanced.vue`
- 实际组件：`web/frontend/src/views/artdeco-pages/ArtDecoDataAnalysis.vue`
- 功能域：数据分析 / 指标分析与选股
- 当前已知关键 DOM：
  - `.artdeco-data-analysis`
  - `数据分析中心`
  - `可用指标`
  - `执行筛选`
  - `筛选结果`

### Canonical 接口族

- `/api/v1/indicators/registry`
- `/api/v1/data/stocks/basic`

### 现有可复用测试

- `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts`

### Mock 轨要求

- stub 指标注册表与股票池后，统计卡和主 Tab 壳层完整
- 点击 `执行筛选` 后可切到结果页
- 结果表格可渲染，不出现关键 console error

### Real 轨要求

- 真实指标注册表可映射为可用指标统计
- 真实股票池可映射为筛选结果行
- 页面在真实空数据下不崩溃

### 通过条件

- 页面标题可见
- 统计卡可见
- Tab 切换正常
- 执行筛选后结果区域可见

### 高概率问题分类

- `backend contract/runtime gap`
- `frontend render gap`

## 5.4 Watchlist-Manage

### 页面基线

- 路由：`/watchlist/manage`
- 组件：`web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`
- 功能域：自选管理 / 组合管理
- 当前已知关键 DOM：
  - `.watchlist-manager`
  - `组合持仓明细`
  - `导入`
  - `导出`
  - `删除`

### Canonical 接口族

- 读链：
  - `/api/v1/monitoring/watchlists`
  - `/api/v1/monitoring/watchlists/{id}/stocks`
- 写链：
  - `/api/v1/monitoring/watchlists`
  - `/api/v1/monitoring/watchlists/{id}/stocks/{code}`

### 现有可复用测试

- `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts`
- `web/frontend/tests/e2e/artdeco-config-integration.spec.ts`

### Mock 轨要求

- stub 组合列表与持仓详情后，统计卡、Tab、表格均可见
- 新建组合按钮可触发最小创建流程
- 删除持仓动作可触发最小删除流程

### Real 轨要求

- 真实组合读链与持仓读链可消费
- 若写链可用，则至少一次 create/remove 不报未处理异常
- 若写链未闭环，必须有明确降级，不允许静默失败

### 通过条件

- 组合表格可见
- 组合 Tab 可切换
- 导入/导出入口可见
- 至少一个最小交互动作可执行

### 高概率问题分类

- `backend contract/runtime gap`
- `frontend render gap`

## 5.5 Watchlist-Signals

### 页面基线

- 路由：`/watchlist/signals`
- 组件：`web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
- 功能域：自选管理 / 信号雷达
- 当前已知关键 DOM：
  - `.strategy-signals-tab`
  - `策略信号工作台`
  - `实时信号时间轴`
  - `刷新信号`
  - `REQ_ID:`

### Canonical 接口

- `/api/v1/trade/signals`

### 现有可复用测试

- `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts`

### Mock 轨要求

- stub 信号列表后，统计卡、时间轴、信号卡均可见
- 空信号时工作台保留壳层
- 刷新动作可点击

### Real 轨要求

- 真实信号响应可映射为时间轴
- `REQ_ID` 可显化
- 真实空数据时显示等待/空态，不崩溃

### 通过条件

- 工作台标题可见
- 时间轴区域可见
- 至少一个信号卡可见
- 刷新按钮可点击

### 高概率问题分类

- `backend contract/runtime gap`
- `frontend render gap`

## 5.6 Watchlist-Screener

### 页面基线

- 路由：`/watchlist/screener`
- 组件：`web/frontend/src/views/stocks/Screener.vue`
- 功能域：自选管理 / 策略选股
- 当前已知关键 DOM：
  - `.screener-container`
  - `STOCK SCREENER`
  - `SCREENING CRITERIA`
  - `SCREENING RESULTS`
  - `RUN SCREENING`
  - `CLEAR FILTERS`

### Canonical 接口

- `/api/v1/data/stocks/basic`

### 现有可复用测试

- `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts`

### Mock 轨要求

- stub 股票池后，筛选器和结果表格均可见
- `RUN SCREENING` 可触发最小筛选流程
- `CLEAR FILTERS` 可执行且不打崩页面

### Real 轨要求

- 真实股票池响应可映射为选股结果表
- 真实空数据时表格结构不塌陷
- 页面不因筛选动作产生未处理异常

### 通过条件

- 页面标题可见
- 筛选器区域可见
- 结果表格可见
- 两个主按钮可点击

### 高概率问题分类

- `backend contract/runtime gap`
- `frontend render gap`

## 6. 批次执行命令建议

## 6.1 Mock 轨

建议先跑：

```bash
cd web/frontend
npx playwright test tests/e2e/phase2-mainline-matrix.spec.ts --project=chromium
```

## 6.2 Real 轨

建议执行：

```bash
cd web/frontend
npx playwright test tests/e2e/comprehensive-all-pages.spec.ts --project=chromium --grep "Data-Concept|Data-FundFlow|Data-Indicator|Watchlist-Manage|Watchlist-Signals|Watchlist-Screener"
```

## 7. 批次报告要求

Phase 2 每轮推进后，报告中至少包含：

- 页面范围：6 页
- Mock：
  - 通过数 / 失败数 / 跳过数
- Real：
  - 通过数 / 失败数 / 跳过数
- 问题分类计数：
  - `route/config drift`
  - `frontend render gap`
  - `backend contract/runtime gap`
- 质量门禁：
  - 结构性语法错误
  - 类型错误是否高于基线
  - PM2 服务状态
  - 服务地址
- 当前阻塞项
- 下一批进入条件

## 8. 预期结论

Phase 2 结束后，必须能明确回答：

1. 数据分析 3 页是否能在 Mock / Real 双轨下稳定消费真实读链。
2. `Watchlist-Manage` 是否至少具备最小交互闭环。
3. `Watchlist-Signals` 是否能映射真实信号时间轴。
4. `Watchlist-Screener` 是否能在真实股票池下完成最小筛选表达。
5. 当前主要问题究竟集中在：
   - 配置漂移
   - 前端未实现
   - 后端契约/运行异常
