# MyStocks 前端主线测试 Phase 4 详细推进表

> 日期：2026-04-03
> 上游总纲：`docs/plans/2026-04-02-frontend-mainline-testing-overall-plan.md`
> 范围：Phase 4 十个页面的 Mock / Real 双轨验证与修复推进

## 1. 目标

Phase 4 聚焦两条系统级主链：

1. 风险页是否能在 Mock / Real 下稳定表达预警、止损、组合风险与公告审阅能力。
2. 系统页是否能在 Mock / Real 下稳定完成健康探针、导出、配置视图与数据源批量写回链路。

本批次页面：

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

## 2. 进入条件

执行 Phase 4 前，固定先确认以下条件：

### 2.1 页面真值

- 路由真值：`web/frontend/src/router/index.ts`
- 功能树真值：`docs/FUNCTION_TREE.md`
- 主链清单真值：`docs/plans/frontend-page-optimization-list.md`

### 2.2 当前已知事实

- 上述 10 页均已在主链清单中标记为 Phase 4 页面。
- `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts` 已覆盖这 10 个路由的 real 子集入口。
- 当前仓库没有这 10 页的专用稳定 Phase 4 E2E，需要新增一份矩阵测试资产补缺。
- `Phase 3` 已完成，当前运行态口径为：
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

Phase 4 固定按以下顺序推进：

1. `Risk-Management`
2. `Risk-Overview`
3. `Risk-PnL`
4. `Risk-StopLoss`
5. `Risk-Alerts`
6. `Risk-News`
7. `System-Config`
8. `System-Health`
9. `System-API`
10. `System-Data`

原因：

- 先收口风险域的组合、规则、告警、公告与止损链，快速暴露监控与读链问题。
- 再进入系统域，收口健康探针、导出链、本地配置持久化与数据源批量写回链。

## 4. 统一执行模型

每个页面都固定跑以下 4 层：

1. `route-shell`
2. `mock-render`
3. `real-read`
4. `real-write/degrade`

对本批次而言，`real-write/degrade` 重点适用于：

- `System-API`
- `System-Data`
- `System-Config`

其中：

- `System-API` 重点验证导出链。
- `System-Data` 重点验证批量写回链。
- `System-Config` 当前仅存在本地持久化保存，不存在已确认的真实后端配置写链，必须明确按降级态记录。

## 5. Phase 4 页面矩阵

### 5.1 Risk-Management

- 路由：`/risk/management`
- 组件：`web/frontend/src/views/artdeco-pages/ArtDecoRiskManagement.vue`
- Canonical 接口：`/v1/trade/positions`
- Mock 轨要求：
  - 风险控制工作流壳层、风险统计卡、预警列表可见
  - `导出`、`设置` 入口存在
  - 风险表格能消费 positions payload 派生出的预警项
- Real 轨要求：
  - 真实持仓可映射为总资产、今日收益与预警动作
  - `REQ_ID:` 位可显化
  - 空仓位不白屏

### 5.2 Risk-Overview

- 路由：`/risk/overview`
- 组件：`web/frontend/src/views/artdeco-pages/risk-tabs/RiskOverviewTab.vue`
- Canonical 接口：`/v1/monitoring/alert-rules`
- Mock 轨要求：
  - 风险概览、规则清单、预警消息三页签均可见
  - 规则表格可消费风控规则 payload
  - 静态预警列表与刷新入口可见
- Real 轨要求：
  - 真实规则列表可映射为规则表
  - `REQ_ID:` 位可显化
  - 空规则时概览与预警页签仍能稳定展示

### 5.3 Risk-PnL

- 路由：`/risk/pnl`
- 组件：`web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`
- Canonical 接口：`/v1/trade/positions`
- Mock 轨要求：
  - 组合资产、今日盈亏、绩效归因、再平衡建议可见
  - 持仓列表可消费真实 positions 字段映射
- Real 轨要求：
  - 真实持仓可映射为资产统计与 Top Positions
  - 空数据时不崩溃
  - `REQ:` 位可显化

### 5.4 Risk-StopLoss

- 路由：`/risk/stop-loss`
- 组件：`web/frontend/src/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue`
- Canonical 接口族：
  - `/v1/monitoring/watchlists`
  - `/v1/monitoring/watchlists/{id}/stocks`
  - `/v1/market/quotes`
- Mock 轨要求：
  - 止损雷达壳层、统计卡、监控卡片可见
  - 能同时覆盖 triggered 与 critical 两类距离状态
- Real 轨要求：
  - watchlist -> stocks -> quotes 三段读链可消费
  - 空 watchlist 或空股票列表不崩溃
  - `REQ_ID:` 位可显化

### 5.5 Risk-Alerts

- 路由：`/risk/alerts`
- 组件：`web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue`
- Canonical 接口族：
  - `/v1/monitoring/alert-rules`
  - `/v1/monitoring/alerts`
- Mock 轨要求：
  - 近期告警与规则列表双表格可见
  - 未读告警、高优先级统计可随 payload 变化
- Real 轨要求：
  - 真实规则和告警记录可分别映射到两张表
  - `REQ_ID:` 位可显化
  - 任一单链失败时另一张表不应拖垮整页

### 5.6 Risk-News

- 路由：`/risk/news`
- 组件：`web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue`
- Canonical 接口：`/announcement/list`
- Mock 轨要求：
  - 公告总数、重要公告、原文链接统计卡可见
  - 公告列表与 `查看原文` 入口可见
- Real 轨要求：
  - 真实公告列表可映射为表格
  - 空列表不崩溃
  - `REQ_ID:` 位可显化

### 5.7 System-Config

- 路由：`/system/config`
- 组件：`web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue`
- Canonical 接口族：
  - `/health/detailed`
  - `/health`
- 降级说明：
  - `保存本地设置` 仅写本地 `localStorage`
  - 当前页面明确显示 `统一系统配置后端契约仍未建立`
- Mock 轨要求：
  - `数据源`、`系统设置`、`系统监控` 三页签可见
  - 健康监控表格能消费 detailed/slim health payload
  - 本地设置保存后能写入本地持久化
- Real 轨要求：
  - 真实健康接口至少能驱动监控表格非空或健康摘要
  - 必须将“无真实配置写链”按降级态写入报告，不可伪装为已闭环写链

### 5.8 System-Health

- 路由：`/system/health`
- 组件：`web/frontend/src/views/artdeco-pages/system-tabs/SystemHealthTab.vue`
- Canonical 接口：`/health`
- Mock 轨要求：
  - 健康矩阵壳层、中间件面板、说明卡可见
  - 服务名、版本、状态可消费 health payload
- Real 轨要求：
  - 真实 health payload 可映射为服务状态与版本
  - `REQ_ID:` 位可显化
  - 非 healthy 状态要能保留页面结构

### 5.9 System-API

- 路由：`/system/api`
- 组件：`web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue`
- Canonical 接口族：
  - `/health`
  - `/health/detailed`
- Mock 轨要求：
  - 系统监控工作台、遥测面板与导出按钮可见
  - `导出报告` 动作能触发 detailed health 读取
- Real 轨要求：
  - `health` 读链稳定
  - `导出报告` 至少能触发真实导出读取或给出明确失败提示
  - `REQ_ID:` 位可显化

### 5.10 System-Data

- 路由：`/system/data`
- 组件：`web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue`
- Canonical 接口族：
  - `/v1/data-sources/config/`
  - `/v1/data-sources/config/batch`
- Mock 轨要求：
  - 配置表、启停按钮、`保存配置`、`恢复默认` 入口可见
  - 启用/禁用切换后可构造 batch payload
- Real 轨要求：
  - 真实配置列表可映射为表格
  - 保存动作失败时需显式提示，不允许静默失败
  - `REQ_ID:` 位可显化

## 6. 推荐验证资产

- 现有可复用：
  - `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts`
- 本阶段应新增：
  - `web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts`

## 7. 报告要求

Phase 4 每轮推进后，报告中至少包含：

- 每页 `Mock / Real` 结论
- 问题分类：
  - `route/config drift`
  - `frontend render gap`
  - `backend contract/runtime gap`
- 是否存在未闭环写链或仅降级保留链
- E2E 实际执行命令、浏览器项目、通过/失败/跳过数量
- PM2 与地址状态：
  - `mystocks-backend`: `http://localhost:8020`
  - `mystocks-frontend`: `http://localhost:3020`

## 8. 预期产出物

- `docs/plans/2026-04-03-frontend-mainline-phase-4-execution-matrix.md`
- `web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts`
- `reports/analysis/frontend-mainline-phase-4-matrix.md`
- `reports/analysis/frontend-mainline-phase-4-status.json`
