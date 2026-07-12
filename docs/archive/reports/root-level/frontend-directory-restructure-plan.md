# MyStocks 前端目录结构重组与文件整合方案（深度分析版）

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


**输出路径**: `/opt/claude/mystocks_spec/reports/frontend-directory-restructure-plan.md`
**分析范围**: `/opt/claude/mystocks_spec/web/frontend/src/views`
**分析日期**: 2026-03-02

---

## 1. 执行摘要

### 1.1 当前问题分析

基于现有审计与本次复核（Vue 页面 252 个）:

- 页面总量过大，目录聚集明显：
  - `artdeco-pages/` 86
  - 根目录 `views/` 44
  - `demo/` 25
  - `advanced-analysis/` 13
  - `converted.archive/` 9
- 已接入路由页面仅 35，未接入页面 217，存在明显“功能资产沉没”。
- 重复/同名页面组 13 组（例如 `BacktestAnalysis.vue`、`TechnicalAnalysis.vue`、`Wencai.vue` 等）。
- Demo / Archive / 示例目录页面数量大（58 个），与主业务导航体系割裂。
- 功能域边界不清：市场、数据、策略、交易、风险、系统能力散落于多个目录并行演进。

### 1.2 重组目标

1. 建立**按业务域组织**的目录（market/data/strategy/trade/risk/watchlist/system）。
2. 将“页面碎片化”收敛为“主页面 + 标签页 + 共享组件/Composable”。
3. 将 Demo/Archive 迁移到 `deprecated/` 治理区，主干目录只保留生产可用资产。
4. 控制目录规模：**每个一级域目录直接页面文件不超过 15**（通过 `tabs/`、`components/` 分层）。
5. 提供可执行的移动、合并、删除清单与分阶段路线图。

### 1.3 预期收益

- 路由与菜单维护复杂度下降（定位路径更短、更稳定）。
- 复用率上升（同类能力汇聚，减少重复实现）。
- 后续接入新功能更可控（按域扩展而非继续堆在根目录）。
- 与项目定位一致（个人/小团队本地化系统，避免过度架构）。

---

## 2. 当前目录结构分析

### 2.1 目录分布统计（Vue 页面）

- `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages`: 86
- `/opt/claude/mystocks_spec/web/frontend/src/views`（根）: 44
- `/opt/claude/mystocks_spec/web/frontend/src/views/demo`: 25
- `/opt/claude/mystocks_spec/web/frontend/src/views/advanced-analysis`: 13
- `/opt/claude/mystocks_spec/web/frontend/src/views/converted.archive`: 9
- `/opt/claude/mystocks_spec/web/frontend/src/views/market`: 8
- `/opt/claude/mystocks_spec/web/frontend/src/views/freqtrade-demo`: 6
- `/opt/claude/mystocks_spec/web/frontend/src/views/stock-analysis`: 6
- `/opt/claude/mystocks_spec/web/frontend/src/views/stocks`: 6
- `/opt/claude/mystocks_spec/web/frontend/src/views/strategy`: 6
- `/opt/claude/mystocks_spec/web/frontend/src/views/tdxpy-demo`: 5
- `/opt/claude/mystocks_spec/web/frontend/src/views/trade-management`: 5
- 其他小目录：`risk/settings/trading/trading-decision/system/errors/examples/components/...`

### 2.2 功能定位分析

- `artdeco-pages/`：当前主干业务页面与大量可复用子视图并存，是“事实主域”，但过于臃肿。
- 根目录：历史主页面、实验页、过渡页混杂。
- `market/strategy/risk/system/...`：存在业务域化雏形，但与 `artdeco-pages` 并行重复。
- `demo/converted.archive/examples/freqtrade-demo/tdxpy-demo`：实验/迁移残留，非主干。

### 2.3 目录关系与关键问题

1. **主干双轨并存**：`artdeco-pages` 与根级/旧域页面重复表达同类能力。
2. **页面与组件边界模糊**：大量“视图级组件”落在 `views` 下，导致页面统计虚高。
3. **路由接入率低**：仅 35/252 页面接入主路由。
4. **重名高频**：同名不同实现增加维护风险。

---

## 3. 重复功能识别

### 3.1 完全重复（内容级）

- 本次未发现“内容完全相同”的页面组（历史报告为 0 组）。

### 3.2 高度相似（同名/同职责）页面组（13 组）

1. `BacktestAnalysis.vue`
   - `/opt/claude/mystocks_spec/web/frontend/src/views/BacktestAnalysis.vue`
   - `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/analysis-tabs/BacktestAnalysis.vue`
2. `OpenStockDemo.vue`
   - `/opt/claude/mystocks_spec/web/frontend/src/views/OpenStockDemo.vue`
   - `/opt/claude/mystocks_spec/web/frontend/src/views/demo/OpenStockDemo.vue`
3. `Overview.vue`
   - `/opt/claude/mystocks_spec/web/frontend/src/views/demo/pyprofiling/components/Overview.vue`
   - `/opt/claude/mystocks_spec/web/frontend/src/views/demo/stock-analysis/components/Overview.vue`
   - `/opt/claude/mystocks_spec/web/frontend/src/views/risk/Overview.vue`
4. `Phase4Dashboard.vue`
   - `/opt/claude/mystocks_spec/web/frontend/src/views/Phase4Dashboard.vue`
   - `/opt/claude/mystocks_spec/web/frontend/src/views/demo/Phase4Dashboard.vue`
5. `Portfolio.vue`
   - `/opt/claude/mystocks_spec/web/frontend/src/views/risk/Portfolio.vue`
   - `/opt/claude/mystocks_spec/web/frontend/src/views/stocks/Portfolio.vue`
6. `Positions.vue`
   - `/opt/claude/mystocks_spec/web/frontend/src/views/risk/Positions.vue`
   - `/opt/claude/mystocks_spec/web/frontend/src/views/trading/Positions.vue`
7. `PyprofilingDemo.vue`
   - `/opt/claude/mystocks_spec/web/frontend/src/views/PyprofilingDemo.vue`
   - `/opt/claude/mystocks_spec/web/frontend/src/views/demo/PyprofilingDemo.vue`
8. `Realtime.vue`
   - `/opt/claude/mystocks_spec/web/frontend/src/views/demo/stock-analysis/components/Realtime.vue`
   - `/opt/claude/mystocks_spec/web/frontend/src/views/market/Realtime.vue`
9. `RiskOverviewTab.vue`
   - `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/risk-tabs/RiskOverviewTab.vue`
   - `/opt/claude/mystocks_spec/web/frontend/src/views/components/RiskOverviewTab.vue`
10. `StockAnalysisDemo.vue`
    - `/opt/claude/mystocks_spec/web/frontend/src/views/StockAnalysisDemo.vue`
    - `/opt/claude/mystocks_spec/web/frontend/src/views/demo/StockAnalysisDemo.vue`
11. `TechnicalAnalysis.vue`
    - `/opt/claude/mystocks_spec/web/frontend/src/views/TechnicalAnalysis.vue`
    - `/opt/claude/mystocks_spec/web/frontend/src/views/technical/TechnicalAnalysis.vue`
12. `WatchlistManagement.vue`
    - `/opt/claude/mystocks_spec/web/frontend/src/views/demo/openstock/components/WatchlistManagement.vue`
    - `/opt/claude/mystocks_spec/web/frontend/src/views/monitoring/WatchlistManagement.vue`
13. `Wencai.vue`
    - `/opt/claude/mystocks_spec/web/frontend/src/views/Wencai.vue`
    - `/opt/claude/mystocks_spec/web/frontend/src/views/demo/Wencai.vue`

### 3.3 部分重叠（功能拆散在多页）

- 市场分析能力：`market/*` + `artdeco-pages/market-tabs/*` + `artdeco-pages/market-data-tabs/*`
- 策略能力：`strategy/*` + `artdeco-pages/strategy-tabs/*` + `stock-analysis/*`
- 交易能力：`trading/*` + `trade-management/*` + `trading-decision/*` + `artdeco-pages/trading-tabs/*`
- 风险能力：`risk/*` + `artdeco-pages/risk-tabs/*` + `monitoring/*`
- 系统能力：`settings/*` + `system/*` + `artdeco-pages/system-tabs/*`

---

## 4. 相近功能识别（按功能域）

### 4.1 市场行情域（可合并为“市场分析工作台”）

可合并来源：
- `artdeco-pages/market-tabs/MarketRealtimeTab.vue`
- `artdeco-pages/market-tabs/MarketKLineTab.vue`
- `artdeco-pages/market-tabs/MarketConceptTab.vue`
- `artdeco-pages/market-data-tabs/AuctionAnalysis.vue`
- `artdeco-pages/market-data-tabs/ETFAnalysis.vue`
- `artdeco-pages/market-data-tabs/FundFlow.vue`
- `artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue`

合并建议：`market/Overview.vue` + `market/tabs/{Realtime,Kline,Concept,Industry,FundFlow,ETF,Auction}.vue`

### 4.2 数据分析域（可合并为“高级分析中心”）

可合并来源：
- `advanced-analysis/*` 13 页
- `artdeco-pages/ArtDecoDataAnalysis.vue`
- `artdeco-pages/components/Analysis*.vue`
- `technical/TechnicalAnalysis.vue`

合并建议：`data/Advanced.vue` 统一承载多分析标签页。

### 4.3 策略管理域（可合并为“策略工作台”）

可合并来源：
- `artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue`
- `artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
- `artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`
- `artdeco-pages/strategy-tabs/StrategyParametersTab.vue`
- `strategy/{SingleRun,BatchScan,ResultsQuery,StatsAnalysis,StrategyList}.vue`

合并建议：`strategy/Workbench.vue` + 标签页（仓库/单次运行/批扫/回测/优化/参数/结果/统计）。

### 4.4 交易管理域（可合并为“交易中心”）

可合并来源：
- `artdeco-pages/trading-tabs/*`
- `trading/*`
- `trade-management/components/*`
- `trading-decision/*`

合并建议：`trade/Center.vue` + 标签页（头寸/订单/历史/执行/统计/信号/决策）。

### 4.5 风险管理域（可合并为“风险中心”）

可合并来源：
- `artdeco-pages/risk-tabs/*`
- `risk/*`
- `monitoring/RiskDashboard.vue`
- `components/RiskOverviewTab.vue`

合并建议：`risk/Center.vue` + 标签页（概览/告警/止损/组合盈亏/舆情）。

### 4.6 系统设置域（可合并为“系统设置中心”）

可合并来源：
- `artdeco-pages/system-tabs/*`
- `settings/*`
- `system/*`
- `monitoring/MonitoringDashboard.vue`

合并建议：`system/Settings.vue` + 标签页（通用/数据源/API/健康/性能/数据库）。

---

## 5. 新目录结构设计

> 设计目标：域内页面 <= 15；通过 tabs/components/composables 分层控制规模

```text
/opt/claude/mystocks_spec/web/frontend/src/views/
├── market/
│   ├── Overview.vue
│   ├── Realtime.vue
│   ├── Technical.vue
│   ├── Concepts.vue
│   ├── CapitalFlow.vue
│   ├── ETF.vue
│   ├── Auction.vue
│   ├── tabs/
│   └── components/
├── data/
│   ├── Overview.vue
│   ├── Advanced.vue
│   ├── Industry.vue
│   ├── Concepts.vue
│   ├── FundFlow.vue
│   ├── Indicator.vue
│   ├── tabs/
│   └── components/
├── strategy/
│   ├── List.vue
│   ├── Workbench.vue
│   ├── Backtest.vue
│   ├── Optimization.vue
│   ├── Parameters.vue
│   ├── Results.vue
│   ├── Stats.vue
│   ├── tabs/
│   └── components/
├── trade/
│   ├── Center.vue
│   ├── Signals.vue
│   ├── Portfolio.vue
│   ├── History.vue
│   ├── tabs/
│   └── components/
├── risk/
│   ├── Center.vue
│   ├── Overview.vue
│   ├── Alerts.vue
│   ├── StopLoss.vue
│   ├── News.vue
│   ├── tabs/
│   └── components/
├── watchlist/
│   ├── Manage.vue
│   ├── Screener.vue
│   ├── Signals.vue
│   └── components/
├── system/
│   ├── Settings.vue
│   ├── Health.vue
│   ├── API.vue
│   ├── DataSource.vue
│   ├── Performance.vue
│   ├── Database.vue
│   ├── tabs/
│   └── components/
├── shared/
│   ├── components/
│   ├── composables/
│   └── utils/
├── errors/
│   ├── 404.vue
│   ├── 403.vue
│   └── 500.vue
└── deprecated/
    ├── demo/
    ├── archive/
    ├── examples/
    └── migrations/
```

### 5.1 每个目录功能定位

- `market`: 行情与盘面分析
- `data`: 深度分析与研究
- `strategy`: 策略全生命周期
- `trade`: 交易执行与结果
- `risk`: 风险监测与告警
- `watchlist`: 自选与选股
- `system`: 运行配置与运维
- `shared`: 横向复用
- `deprecated`: 历史资产隔离区

---

## 6. 详细整合方案（按功能域）

## 目录：market/（市场行情）

### 当前状态
- 主要来源：
  - `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-tabs/*`
  - `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-data-tabs/*`
  - `/opt/claude/mystocks_spec/web/frontend/src/views/market/*`
- 现状问题：K线/概念/ETF/资金流分散在多目录。

### 目标状态
- 7 个主页面：Overview/Realtime/Technical/Concepts/CapitalFlow/ETF/Auction
- 其余能力进入 tabs/components

### 整合步骤
1. 保留并重命名主干来源（优先已接入 ArtDeco 页面）。
2. 将 `market/*` 中有价值逻辑并入同名主页面。
3. `ArtDecoMarketOverview/ArtDecoMarketAnalysis` 折叠到 `Overview + tabs`。
4. 非主干旧页迁入 `deprecated/market-legacy`。

### 工作量估算
- 合并 6~8 组能力：10h
- 路由和菜单重指向：2h
- 回归测试：3h
- **合计：15h**

### 风险评估
- 中风险：K线/资金流图表依赖迁移

### 优先级
- **P0**

---

## 目录：data/（数据分析）

### 当前状态
- 主要来源：`advanced-analysis/*` + `ArtDecoDataAnalysis.vue` + 分析类组件。

### 目标状态
- `Overview.vue` + `Advanced.vue`（多标签）+ `Industry.vue` + `Concepts.vue` + `FundFlow.vue`。

### 整合步骤
1. 将 13 个 `advanced-analysis` 页面合并成统一标签体系。
2. 抽离重复指标/图表块到 `shared/components`。
3. 关闭根目录 `AdvancedAnalysis.vue/Analysis.vue/TechnicalAnalysis.vue` 的直接路由计划。

### 工作量估算
- 13→1 工作台整合：18h
- 共享抽取：6h
- 测试：4h
- **合计：28h**

### 风险评估
- 中风险：分析结果展示一致性

### 优先级
- **P1**

---

## 目录：strategy/（策略管理）

### 当前状态
- 来源分散：`artdeco-pages/strategy-tabs/*` + `strategy/*` + `stock-analysis/*`。

### 目标状态
- `List.vue` + `Workbench.vue` + `Backtest.vue` + `Optimization.vue` + `Parameters.vue` + `Results.vue` + `Stats.vue`

### 整合步骤
1. 保留已接入主干（`ArtDecoStrategyManagement/Backtest/Optimization/Parameters`）。
2. `strategy/*.vue` 迁移为 Workbench 内标签。
3. `stock-analysis/*` 仅保留可复用数据面板，页面本体下沉至 Workbench。

### 工作量估算
- 功能整合：14h
- 抽取策略共享逻辑：5h
- 测试：4h
- **合计：23h**

### 风险评估
- 中风险：策略参数与回测数据流对齐

### 优先级
- **P0**

---

## 目录：trade/（交易管理）

### 当前状态
- 来源：`artdeco-pages/trading-tabs/*` + `trading/*` + `trade-management/components/*` + `trading-decision/*`。

### 目标状态
- `Center.vue` + `Signals.vue` + `Portfolio.vue` + `History.vue`

### 整合步骤
1. 以 `ArtDecoSignalsView`、`ArtDecoTradingPositions`、`ArtDecoTradingHistory` 为主干。
2. `trade-management/components/*` 提升为共享子组件并挂入 `Center.vue` 标签。
3. `trading-decision/*` 作为 `Center.vue` 决策子模块。

### 工作量估算
- 合并与抽取：16h
- 路由重映射：2h
- 测试：4h
- **合计：22h**

### 风险评估
- 中风险：交易面板交互回归

### 优先级
- **P0**

---

## 目录：risk/（风险管理）

### 当前状态
- 来源：`artdeco-pages/risk-tabs/*` + `risk/*` + `monitoring/RiskDashboard.vue`。

### 目标状态
- `Center.vue` + `Overview.vue` + `Alerts.vue` + `StopLoss.vue` + `News.vue`

### 整合步骤
1. 主干保留 `RiskOverviewTab`、`ArtDecoRiskAlerts`、`StopLossMonitorTab`、`ArtDecoAnnouncementMonitor`。
2. `risk/*.vue` 作为兼容层逐步淘汰。
3. 监控类视图能力抽取为 `risk/components`。

### 工作量估算
- 整合：10h
- 抽取：3h
- 测试：3h
- **合计：16h**

### 风险评估
- 低~中风险

### 优先级
- **P0**

---

## 目录：watchlist/（自选管理）

### 当前状态
- 来源：`WatchlistManager.vue` + `StrategySignalsTab.vue` + `stocks/Screener.vue`

### 目标状态
- `Manage.vue` + `Signals.vue` + `Screener.vue`

### 整合步骤
1. 三页保持轻量，不新增冗余层。
2. 将 `WatchlistManagement` 重名实现（demo/monitoring）统一为单实现。

### 工作量估算
- 轻整合：5h

### 风险评估
- 低风险

### 优先级
- **P1**

---

## 目录：system/（系统设置）

### 当前状态
- 来源：`artdeco-pages/system-tabs/*` + `settings/*` + `system/*` + `monitoring/*`

### 目标状态
- `Settings.vue` + `Health.vue` + `API.vue` + `DataSource.vue` + `Performance.vue` + `Database.vue`

### 整合步骤
1. 主干保留 `ArtDecoSystemSettings/SystemHealthTab/ArtDecoMonitoringDashboard/ArtDecoDataManagement`。
2. `settings/*` 与 `system/*` 页面合并为 Settings 子标签。
3. 非核心监控面板收敛到 `system/components`。

### 工作量估算
- 合并：12h
- 抽取：4h
- 测试：3h
- **合计：19h**

### 风险评估
- 中风险：系统配置项映射

### 优先级
- **P1**

---

## 7. 共享组件提取方案

建议优先提取到 `/opt/claude/mystocks_spec/web/frontend/src/views/shared/components`：

1. `KlineChart.vue`（来源：market/demo/openstock）
2. `TechnicalIndicatorsPanel.vue`
3. `CapitalFlowChart.vue`
4. `RiskMetricsPanel.vue`
5. `BacktestKpiGrid.vue`（已有策略组件可提升）
6. `SignalMonitoringMetrics.vue`
7. `TradeDialog.vue`
8. `PortfolioSummaryCard.vue`
9. `AnalysisResultsPanel.vue`
10. `SystemHealthMatrix.vue`

使用场景：市场、策略、风险、交易跨域复用，减少同类图表/表格重复实现。

---

## 8. 共享 Composable 提取方案

建议提取到 `/opt/claude/mystocks_spec/web/frontend/src/views/shared/composables`：

1. `useMarketData.ts`（行情拉取/刷新/缓存）
2. `useKlineAnalysis.ts`（K线与指标计算）
3. `useFundFlow.ts`（资金流聚合）
4. `useStrategyRun.ts`（单次运行/批量扫描统一接口）
5. `useBacktestWorkbench.ts`（回测参数、执行、结果状态）
6. `useTradeCenter.ts`（持仓/订单/历史统一状态）
7. `useRiskMonitor.ts`（风险阈值、告警规则、止损联动）
8. `useSystemHealth.ts`（健康检查/API 状态）
9. `useDomainTabs.ts`（通用标签页状态管理）
10. `usePageFilters.ts`（筛选器序列化、URL 同步）

---

## 9. 实施路线图

### Phase 0（1 周）- 冻结与标记
- 冻结新页面增量到旧目录。
- 建立 `deprecated/` 目录并标记 58 个删除候选（先迁移后物删）。

### Phase 1（2 周）- P0 域重组
- 完成 market/strategy/trade/risk 四域主页面重组。
- 路由与菜单只保留新域路径。

### Phase 2（2 周）- P1 域重组
- 完成 data/system/watchlist 整合。
- `advanced-analysis/*` 全部折叠入 `data/Advanced.vue` 标签体系。

### Phase 3（1~2 周）- 共享资产抽取
- 提取 shared/components + shared/composables。
- 移除重复实现与兼容壳页面。

### Phase 4（持续）- 收尾与治理
- 物理删除 deprecated 中确认废弃页面。
- 建立目录健康阈值（每域<=15主页面）。

总估算：**约 14~16 人日（单人）**。

---

## 10. 附录

## A. 完整文件删除清单（58）

> 原则：先迁移至 deprecated，经过一个发布周期后物理删除

1. `/opt/claude/mystocks_spec/web/frontend/src/views/FreqtradeDemo.vue`
2. `/opt/claude/mystocks_spec/web/frontend/src/views/KLineDemo.vue`
3. `/opt/claude/mystocks_spec/web/frontend/src/views/MarketDataDemo.vue`
4. `/opt/claude/mystocks_spec/web/frontend/src/views/OpenStockDemo.vue`
5. `/opt/claude/mystocks_spec/web/frontend/src/views/PageTitleDemo.vue`
6. `/opt/claude/mystocks_spec/web/frontend/src/views/PyprofilingDemo.vue`
7. `/opt/claude/mystocks_spec/web/frontend/src/views/StockAnalysisDemo.vue`
8. `/opt/claude/mystocks_spec/web/frontend/src/views/TdxpyDemo.vue`
9. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue`
10. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/_templates/ExampleRiskManagement.vue`
11. `/opt/claude/mystocks_spec/web/frontend/src/views/converted.archive/backtest-management.vue`
12. `/opt/claude/mystocks_spec/web/frontend/src/views/converted.archive/dashboard.vue`
13. `/opt/claude/mystocks_spec/web/frontend/src/views/converted.archive/data-analysis.vue`
14. `/opt/claude/mystocks_spec/web/frontend/src/views/converted.archive/market-data.vue`
15. `/opt/claude/mystocks_spec/web/frontend/src/views/converted.archive/market-quotes.vue`
16. `/opt/claude/mystocks_spec/web/frontend/src/views/converted.archive/risk-management.vue`
17. `/opt/claude/mystocks_spec/web/frontend/src/views/converted.archive/setting.vue`
18. `/opt/claude/mystocks_spec/web/frontend/src/views/converted.archive/stock-management.vue`
19. `/opt/claude/mystocks_spec/web/frontend/src/views/converted.archive/trading-management.vue`
20. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/OpenStockDemo.vue`
21. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/Phase4Dashboard.vue`
22. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/PyprofilingDemo.vue`
23. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/StockAnalysisDemo.vue`
24. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/Wencai.vue`
25. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/openstock/components/FeatureStatus.vue`
26. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/openstock/components/HeatmapChart.vue`
27. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/openstock/components/KlineChart.vue`
28. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/openstock/components/StockNews.vue`
29. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/openstock/components/StockQuote.vue`
30. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/openstock/components/StockSearch.vue`
31. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/openstock/components/WatchlistManagement.vue`
32. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/pyprofiling/components/API.vue`
33. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/pyprofiling/components/Data.vue`
34. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/pyprofiling/components/Features.vue`
35. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/pyprofiling/components/Overview.vue`
36. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/pyprofiling/components/Prediction.vue`
37. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/pyprofiling/components/Profiling.vue`
38. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/pyprofiling/components/Tech.vue`
39. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/stock-analysis/components/Backtest.vue`
40. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/stock-analysis/components/DataParsing.vue`
41. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/stock-analysis/components/Overview.vue`
42. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/stock-analysis/components/Realtime.vue`
43. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/stock-analysis/components/Status.vue`
44. `/opt/claude/mystocks_spec/web/frontend/src/views/demo/stock-analysis/components/Strategy.vue`
45. `/opt/claude/mystocks_spec/web/frontend/src/views/examples/PageConfigExample.vue`
46. `/opt/claude/mystocks_spec/web/frontend/src/views/examples/TradingDashboard.migrated.vue`
47. `/opt/claude/mystocks_spec/web/frontend/src/views/examples/WebSocketConfigExample.vue`
48. `/opt/claude/mystocks_spec/web/frontend/src/views/freqtrade-demo/FreqBacktestTab.vue`
49. `/opt/claude/mystocks_spec/web/frontend/src/views/freqtrade-demo/FreqConfigTab.vue`
50. `/opt/claude/mystocks_spec/web/frontend/src/views/freqtrade-demo/FreqOverviewTab.vue`
51. `/opt/claude/mystocks_spec/web/frontend/src/views/freqtrade-demo/FreqStatusTab.vue`
52. `/opt/claude/mystocks_spec/web/frontend/src/views/freqtrade-demo/FreqStrategyTab.vue`
53. `/opt/claude/mystocks_spec/web/frontend/src/views/freqtrade-demo/FreqWebuiTab.vue`
54. `/opt/claude/mystocks_spec/web/frontend/src/views/tdxpy-demo/TdxApiTab.vue`
55. `/opt/claude/mystocks_spec/web/frontend/src/views/tdxpy-demo/TdxExportTab.vue`
56. `/opt/claude/mystocks_spec/web/frontend/src/views/tdxpy-demo/TdxInstallTab.vue`
57. `/opt/claude/mystocks_spec/web/frontend/src/views/tdxpy-demo/TdxOverviewTab.vue`
58. `/opt/claude/mystocks_spec/web/frontend/src/views/tdxpy-demo/TdxStatusTab.vue`

## B. 完整文件合并清单（13 组）

1. `BacktestAnalysis.vue` 组（保留 ArtDeco）
2. `OpenStockDemo.vue` 组（整体废弃）
3. `Overview.vue` 组（保留 risk 业务概览）
4. `Phase4Dashboard.vue` 组（整体废弃）
5. `Portfolio.vue` 组（并入 trade/portfolio）
6. `Positions.vue` 组（并入 trade/positions）
7. `PyprofilingDemo.vue` 组（整体废弃）
8. `Realtime.vue` 组（保留 market/Realtime）
9. `RiskOverviewTab.vue` 组（保留 artdeco-pages/risk-tabs）
10. `StockAnalysisDemo.vue` 组（整体废弃）
11. `TechnicalAnalysis.vue` 组（保留 technical/TechnicalAnalysis 能力并入 data）
12. `WatchlistManagement.vue` 组（保留 monitoring 业务实现）
13. `Wencai.vue` 组（保留根目录业务页，demo 废弃）

## C. 完整文件移动清单（核心重组范围）

> 以下为重组后目标路径（建议），用于后续执行阶段

### C1. 路由已接入主干页面移动

1. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/market/Realtime.vue`
2. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-tabs/MarketKLineTab.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/market/Technical.vue`
3. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/market/LHB.vue`
4. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/data/Industry.vue`
5. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-tabs/MarketConceptTab.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/data/Concepts.vue`
6. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-data-tabs/FundFlowAnalysis.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/data/FundFlow.vue`
7. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/ArtDecoDataAnalysis.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/data/Advanced.vue`
8. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/watchlist/Manage.vue`
9. `/opt/claude/mystocks_spec/web/frontend/src/views/stocks/Screener.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/watchlist/Screener.vue`
10. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/watchlist/Signals.vue`
11. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/strategy/List.vue`
12. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/strategy/Parameters.vue`
13. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/strategy/Backtest.vue`
14. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/strategy/Optimization.vue`
15. `/opt/claude/mystocks_spec/web/frontend/src/views/strategy/BacktestGPU.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/strategy/GPU.vue`
16. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/trade/Center.vue`
17. `/opt/claude/mystocks_spec/web/frontend/src/views/TradingDashboard.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/trade/Terminal.vue`
18. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoSignalsView.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/trade/Signals.vue`
19. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/trade/Portfolio.vue`
20. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/trade/History.vue`
21. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/ArtDecoRiskManagement.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/risk/Center.vue`
22. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/risk-tabs/RiskOverviewTab.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/risk/Overview.vue`
23. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/risk/StopLoss.vue`
24. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/risk/Alerts.vue`
25. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/risk/News.vue`
26. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/system/Settings.vue`
27. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/system-tabs/SystemHealthTab.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/system/Health.vue`
28. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/system/API.vue`
29. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/system/DataSource.vue`
30. `/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/trade/DealingRoom.vue`

### C2. 可复用未接入页面移动（纳入新结构）

31. `/opt/claude/mystocks_spec/web/frontend/src/views/market/Auction.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/market/Auction.vue`（保留）
32. `/opt/claude/mystocks_spec/web/frontend/src/views/market/CapitalFlow.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/market/CapitalFlow.vue`（保留）
33. `/opt/claude/mystocks_spec/web/frontend/src/views/market/Concepts.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/market/Concepts.vue`（保留）
34. `/opt/claude/mystocks_spec/web/frontend/src/views/market/Etf.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/market/ETF.vue`
35. `/opt/claude/mystocks_spec/web/frontend/src/views/market/Technical.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/market/TechnicalLegacy.vue`
36. `/opt/claude/mystocks_spec/web/frontend/src/views/advanced-analysis/BatchAnalysisView.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/data/tabs/BatchAnalysis.vue`
37. `/opt/claude/mystocks_spec/web/frontend/src/views/advanced-analysis/CapitalFlowView.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/data/tabs/CapitalFlow.vue`
38. `/opt/claude/mystocks_spec/web/frontend/src/views/advanced-analysis/ChipDistributionView.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/data/tabs/ChipDistribution.vue`
39. `/opt/claude/mystocks_spec/web/frontend/src/views/advanced-analysis/SentimentAnalysisView.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/data/tabs/Sentiment.vue`
40. `/opt/claude/mystocks_spec/web/frontend/src/views/advanced-analysis/TechnicalAnalysisView.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/data/tabs/Technical.vue`
41. `/opt/claude/mystocks_spec/web/frontend/src/views/advanced-analysis/TimeSeriesView.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/data/tabs/TimeSeries.vue`
42. `/opt/claude/mystocks_spec/web/frontend/src/views/advanced-analysis/FundamentalAnalysisView.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/data/tabs/Fundamental.vue`
43. `/opt/claude/mystocks_spec/web/frontend/src/views/advanced-analysis/FinancialValuationView.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/data/tabs/Valuation.vue`
44. `/opt/claude/mystocks_spec/web/frontend/src/views/advanced-analysis/AnomalyTrackingView.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/data/tabs/Anomaly.vue`
45. `/opt/claude/mystocks_spec/web/frontend/src/views/advanced-analysis/TradingSignalsView.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/strategy/tabs/Signals.vue`
46. `/opt/claude/mystocks_spec/web/frontend/src/views/strategy/SingleRun.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/strategy/tabs/SingleRun.vue`
47. `/opt/claude/mystocks_spec/web/frontend/src/views/strategy/BatchScan.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/strategy/tabs/BatchScan.vue`
48. `/opt/claude/mystocks_spec/web/frontend/src/views/strategy/ResultsQuery.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/strategy/Results.vue`
49. `/opt/claude/mystocks_spec/web/frontend/src/views/strategy/StatsAnalysis.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/strategy/Stats.vue`
50. `/opt/claude/mystocks_spec/web/frontend/src/views/trading/Orders.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/trade/tabs/Orders.vue`
51. `/opt/claude/mystocks_spec/web/frontend/src/views/trading/Execution.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/trade/tabs/Execution.vue`
52. `/opt/claude/mystocks_spec/web/frontend/src/views/trading/Positions.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/trade/tabs/Positions.vue`
53. `/opt/claude/mystocks_spec/web/frontend/src/views/trading/History.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/trade/tabs/HistoryLegacy.vue`
54. `/opt/claude/mystocks_spec/web/frontend/src/views/trade-management/components/PortfolioOverview.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/trade/components/PortfolioOverview.vue`
55. `/opt/claude/mystocks_spec/web/frontend/src/views/trade-management/components/PositionsTab.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/trade/components/PositionsTab.vue`
56. `/opt/claude/mystocks_spec/web/frontend/src/views/trade-management/components/StatisticsTab.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/trade/components/StatisticsTab.vue`
57. `/opt/claude/mystocks_spec/web/frontend/src/views/trade-management/components/TradeDialog.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/shared/components/TradeDialog.vue`
58. `/opt/claude/mystocks_spec/web/frontend/src/views/risk/Portfolio.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/risk/tabs/PortfolioRisk.vue`
59. `/opt/claude/mystocks_spec/web/frontend/src/views/risk/Positions.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/risk/tabs/PositionsRisk.vue`
60. `/opt/claude/mystocks_spec/web/frontend/src/views/monitoring/AlertRulesManagement.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/risk/components/AlertRulesManagement.vue`
61. `/opt/claude/mystocks_spec/web/frontend/src/views/monitoring/RiskDashboard.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/risk/components/RiskDashboard.vue`
62. `/opt/claude/mystocks_spec/web/frontend/src/views/settings/General.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/system/tabs/General.vue`
63. `/opt/claude/mystocks_spec/web/frontend/src/views/settings/Notifications.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/system/tabs/Notifications.vue`
64. `/opt/claude/mystocks_spec/web/frontend/src/views/settings/Security.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/system/tabs/Security.vue`
65. `/opt/claude/mystocks_spec/web/frontend/src/views/settings/Theme.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/system/tabs/Theme.vue`
66. `/opt/claude/mystocks_spec/web/frontend/src/views/system/PerformanceMonitor.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/system/Performance.vue`
67. `/opt/claude/mystocks_spec/web/frontend/src/views/system/DatabaseMonitor.vue` -> `/opt/claude/mystocks_spec/web/frontend/src/views/system/Database.vue`

---

## 结论

本方案在不改动业务代码的前提下，给出可直接执行的目录重组蓝图与清单。建议先执行 P0（market/strategy/trade/risk + 58 项 deprecated 迁移），再推进 P1/P2，确保风险可控、收益尽快落地。
