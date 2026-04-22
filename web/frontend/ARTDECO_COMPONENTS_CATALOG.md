# ArtDeco Components Catalog

> **参考指南说明**:
> 本文件用于提供 Web 子系统的使用方法、操作指引、接口接入说明、排障提示或结构参考，帮助理解局部实现与协作方式。
> 其中的步骤、示例、端口、目录和操作建议应先与 `architecture/STANDARDS.md`、当前代码实现及最新验证结果核对；若涉及仓库执行流程、命令或协作约束，再补充参考根目录 `AGENTS.md`。本文件不得单独视为仓库共享规则或当前状态的唯一事实来源。


本目录是当前 MyStocks ArtDeco 生态的组件全景清单。

> 2026-04-19 盘点结果
>
> - `src/components/artdeco/` 下共 **73** 个 Vue 组件
> - `views/artdeco-pages/` 下共 **89** 个 ArtDeco 相关 Vue 页面/块/模板
> - 整个 ArtDeco 前端生态共盘点到 **162** 个 Vue 文件
> - 另有 **1** 个共享运行时 composable：`src/composables/useHeaderSummary.ts`
>
> 口径说明
>
> - 这里统计的是 **ArtDeco 生态资产存量**，不是全部活跃业务路由页面数。
> - 当前活跃业务路由真值仍需回到 `web/frontend/src/router/index.ts` 与 `web/frontend/src/views/<domain>/*.vue`。
> - `artdeco-pages/**` 既包含工作台块，也包含模板页和兼容包装层。

## 1. 先看治理口径

本目录严格区分两条主线：

1. **Base / UI 资产**
   位于 `web/frontend/src/components/artdeco/`
2. **Domain / Business 承载**
   位于 `web/frontend/src/components/artdeco/{trading,advanced,specialized}` 与 `web/frontend/src/views/artdeco-pages/**`
3. **活跃路由 canonical entry**
   多数已经位于 `web/frontend/src/views/<domain>/*.vue`，只有少数 ArtDeco 页面仍直接作为路由入口
4. **Shared runtime state helpers**
   位于 `web/frontend/src/composables/`，用于 2+ 消费者之间的布局级状态桥接，不属于组件目录但属于当前生态实现链

判断原则：

- 要长期沉淀、跨页面复用，放 `src/components/artdeco/**`
- 只属于 ArtDeco 页面系统内部复用，放 `views/artdeco-pages/components/`
- 只属于域内工作台块，放 `views/artdeco-pages/*-tabs/`

## 2. Reusable Assets: Base / UI

### 2.1 `base/` 原子 UI（14）

`ArtDecoAlert`、`ArtDecoBadge`、`ArtDecoButton`、`ArtDecoCard`、`ArtDecoCardCompact`、`ArtDecoCollapsible`、`ArtDecoDialog`、`ArtDecoInput`、`ArtDecoLanguageSwitcher`、`ArtDecoProgress`、`ArtDecoSelect`、`ArtDecoSkipLink`、`ArtDecoStatCard`、`ArtDecoSwitch`

### 2.2 `core/` 壳层与框架能力（14）

`ArtDecoAnalysisDashboard`、`ArtDecoBreadcrumb`、`ArtDecoFooter`、`ArtDecoFunctionTree`、`ArtDecoFundamentalAnalysis`、`ArtDecoHeader`、`ArtDecoIcon`、`ArtDecoLoading`、`ArtDecoLoadingOverlay`、`ArtDecoRadarAnalysis`、`ArtDecoSkeleton`、`ArtDecoStatusIndicator`、`ArtDecoTechnicalAnalysis`、`ArtDecoToast`

### 2.3 `business/` 通用业务交互（11）

`ArtDecoAlertRule`、`ArtDecoBacktestConfig`、`ArtDecoButtonGroup`、`ArtDecoCodeEditor`、`ArtDecoDataSourceTable`、`ArtDecoDateRange`、`ArtDecoFilterBar`、`ArtDecoInfoCard`、`ArtDecoMechanicalSwitch`、`ArtDecoSlider`、`ArtDecoStatus`

### 2.4 `charts/` 通用图表能力（9）

`ArtDecoChart`、`ArtDecoKLineChartContainer`、`ArtDecoRomanNumeral`、`CorrelationMatrix`、`DepthChart`、`DrawdownChart`、`HeatmapCard`、`PerformanceTable`、`TimeSeriesChart`

### 2.5 Base / UI 小结

Base / UI 主链共 **48** 个 Vue 组件，负责：

- 原子 UI
- 页面壳层
- 通用业务交互
- 图表基础能力

### 2.6 当前与 `DESIGN.md` 强相关的基础资产

以下组件已直接承接 2026-04 设计契约增强：

- `base/ArtDecoButton.vue`
  - 承接 `200ms / 400ms` 混合过渡预算
  - 适合“单面板单主按钮”规则落地
- `base/ArtDecoBadge.vue`
  - 作为 header summary 与 filter/status chip 的 canonical shared surface
  - 当前已吸收 `default / active / neutral / profit / loss / holding / pending / warning / gold` 语义
  - `artdeco-pages` 范围内的页面级 `status-chip / status-badge` 残留已完成回收，不再鼓励局部重复定义
- `business/ArtDecoStatus.vue`
  - 保持 dot-status 专责，不承接 chip / badge 语义所有权
  - 当前仅负责 `online / warning / offline / loading / success / error` 的点状状态呈现
- `core/ArtDecoHeader.vue`
  - 当前品牌 chrome 已去装饰化，默认不再输出静态 `MyStocks ArtDeco` 文本
- `trading/ArtDecoCollapsibleSidebar.vue`
  - 当前品牌框边线已移除，运行时更偏向数据优先

## 3. Reusable Assets: Domain / Business

### 3.1 `trading/` 交易域组件（13）

`ArtDecoCollapsibleSidebar`、`ArtDecoDynamicSidebar`、`ArtDecoLoader`、`ArtDecoOrderBook`、`ArtDecoPositionCard`、`ArtDecoRiskGauge`、`ArtDecoSidebar`、`ArtDecoStrategyCard`、`ArtDecoTable`、`ArtDecoTicker`、`ArtDecoTickerList`、`ArtDecoTopBar`、`ArtDecoTradeForm`

### 3.2 `advanced/` 高阶分析组件（10）

`ArtDecoAnomalyTracking`、`ArtDecoBatchAnalysisView`、`ArtDecoCapitalFlow`、`ArtDecoChipDistribution`、`ArtDecoDecisionModels`、`ArtDecoFinancialValuation`、`ArtDecoMarketPanorama`、`ArtDecoSentimentAnalysis`、`ArtDecoTimeSeriesAnalysis`、`ArtDecoTradingSignals`

### 3.3 `specialized/` 专题资产（2）

`ArtDecoBlockTrading`、`ArtDecoLongHuBang`

### 3.4 Domain Reusable 小结

Domain reusable 主链共 **25** 个 Vue 组件，处理：

- 交易工作台的稳定域能力
- 高阶分析展示
- 强专题场景

## 4. Page-Level Shared Fragments

目录：`web/frontend/src/views/artdeco-pages/components/`（23）

`AnalysisIndicators`、`AnalysisResults`、`AnalysisScreener`、`AnomalyAlerts`、`AnomalyPatterns`、`ArtDecoAttributionAnalysis`、`ArtDecoAttributionControls`、`ArtDecoPerformanceOverview`、`ArtDecoSignalHistory`、`ArtDecoSignalMonitoringMetrics`、`ArtDecoSignalMonitoringOverview`、`ArtDecoTradingHistoryControls`、`ArtDecoTradingSignalsControls`、`BuffettModel`、`DupontAnalysis`、`FinancialMetrics`、`LynchModel`、`MarketConcepts`、`MarketFundFlow`、`MarketPlaceholder`、`OneilModel`、`PanoramaCapitalFlow`、`PanoramaIndices`

这组组件的职责不是“全站 UI 组件库”，而是 ArtDeco 页面系统内部的共享工作台片段。

## 5. Domain Tab / Workbench Blocks

### 5.1 `market-data-tabs/`（11）

`ArtDecoIndustryAnalysis`、`ArtDecoMarketAnalysis`、`ArtDecoMarketOverview`、`ArtDecoRealtimeMonitor`、`AuctionAnalysis`、`ConceptAnalysis`、`DataQualityPanel`、`DragonTigerAnalysis`、`ETFAnalysis`、`FundFlow`、`FundFlowAnalysis`

### 5.2 `market-tabs/`（4）

`MarketConceptTab`、`MarketETFTab`、`MarketKLineTab`、`MarketRealtimeTab`

### 5.3 `trading-tabs/`（8）

`ArtDecoHistoryView`、`ArtDecoPerformanceAnalysis`、`ArtDecoPositionMonitor`、`ArtDecoSignalsView`、`ArtDecoTradingHistory`、`ArtDecoTradingPositions`、`ArtDecoTradingSignals`、`ArtDecoTradingStats`

### 5.4 `strategy-tabs/`（5）与其子组件（3）

主页面块：

`ArtDecoBacktestAnalysis`、`ArtDecoStrategyManagement`、`ArtDecoStrategyOptimization`、`StrategyParametersTab`、`StrategySignalsTab`

工作台子组件：

`BacktestHeader`、`BacktestKpiGrid`、`BacktestWorkbenchTabs`

### 5.5 `risk-tabs/`（8）

`ArtDecoAnnouncementMonitor`、`ArtDecoRiskAlerts`、`ArtDecoRiskMonitor`、`ArtDecoRiskOverviewPanel`、`ArtDecoRiskStatsGrid`、`ArtDecoRiskStockPanel`、`RiskOverviewTab`、`StopLossMonitorTab`

### 5.6 `system-tabs/`（4）

`ArtDecoDataManagement`、`ArtDecoMonitoringDashboard`、`ArtDecoSystemSettings`、`SystemHealthTab`

### 5.7 其他域内页面块

- `stock-management-tabs/`（2）：
  `PortfolioMonitor`、`WatchlistManager`
- `portfolio-tabs/`（1）：
  `PortfolioOverviewTab`
- `analysis-tabs/`（2）：
  `BacktestAnalysis`、`KLineAnalysis`
- `technical-tabs/`（1）：
  `TechnicalScannerTab`
- `settings/`（5）：
  `AppearanceSettings`、`DataSourceSettings`、`NotificationSettings`、`SecuritySettings`、`SystemInfoSettings`

### 5.8 Domain Blocks 小结

域内页签块与工作台页面块共 **51** 个，另有 `strategy-tabs/components/` 下 **3** 个工作台子组件。

## 5.9 Shared Runtime State Helpers（非 Vue 组件）

目录：`web/frontend/src/composables/`

当前与 ArtDeco 生态直接相关的共享运行时桥接层：

- `useHeaderSummary.ts`

职责：

- 为 `ArtDecoLayoutEnhanced.vue` 提供统一头部摘要状态
- 接收 `useArtDecoDashboard.ts` 推送的 `marketStatus / activeStrategiesCount / todayPnLValue / currentTime / refreshing`
- 让 Dashboard 的摘要指标进入 layout-level header，而不是继续绑定在单页 header 中

这类文件不应统计进 Vue 组件数，但在文档链中必须被视为当前生态的一部分。

## 6. Top-Level Containers / Templates

### 6.1 顶层 ArtDeco 页面容器（10）

`ArtDecoDashboard`、`ArtDecoDataAnalysis`、`ArtDecoMarketData`、`ArtDecoMarketQuotes`、`ArtDecoRiskManagement`、`ArtDecoSettings`、`ArtDecoStockManagement`、`ArtDecoTechnicalAnalysis`、`ArtDecoTradingCenter`、`ArtDecoTradingManagement`

### 6.2 模板页（2）

`ArtDecoPageTemplate`、`ExampleRiskManagement`

### 6.3 当前仍直接参与路由的 ArtDeco 例外入口

以下文件应被视为“ArtDeco 生态中的活跃路由例外”，不是一般性的目录事实推断依据：

- `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
- `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
- `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue`
- `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue`

当某个 ArtDeco 文件被路由直接引用时，应以 router 为准逐项确认，而不是默认整个目录都是主业务入口。

## 7. 当前生态总览

| 区域 | 数量 | 定位 |
|------|------|------|
| `src/components/artdeco/base+core+business+charts` | 48 | Base / UI 主链 |
| `src/components/artdeco/trading+advanced+specialized` | 25 | Domain reusable 主链 |
| `views/artdeco-pages/components` | 23 | 页面系统内部共享片段 |
| `views/artdeco-pages/*-tabs` 等域块 | 54 | 域内工作台块与子组件 |
| 顶层容器与模板 | 12 | 页面承载与模板壳层 |
| `src/composables/useHeaderSummary.ts` | 1 | 共享运行时摘要状态桥接 |
| **合计** | **162** | 当前 ArtDeco 生态 Vue 文件总数 |

> 说明：
>
> - 上表最后一行 `162` 仍只统计 Vue 文件。
> - `useHeaderSummary.ts` 是额外补充的运行时桥接资产，不改变 Vue 资产总数。

## 8. 维护规则

- 新增组件前先查本目录，避免重复造轮子。
- 组件职责变化时，先改 `ARTDECO_COMPONENT_GUIDE.md`，再改本目录。
- 不要把 `*-tabs` 误记为 reusable base assets。
- 不要把 `views/artdeco-pages/components/` 误记为 `src/components/artdeco/` 的替代品。
- 不要把 `views/artdeco-pages/**` 误记为当前所有业务路由的 canonical 页面目录。
- 当目录结构变化时，必须同步更新：
  - `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md`
  - `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`
  - `docs/api/ArtDeco_System_Architecture_Summary.md`
