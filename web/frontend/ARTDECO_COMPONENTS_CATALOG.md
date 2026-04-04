# ArtDeco Components Catalog

本目录是当前 MyStocks ArtDeco 生态的组件全景清单。

> 2026-04-01 盘点结果
>
> - `src/components/artdeco/` 下共 **73** 个 Vue 组件
> - `views/artdeco-pages/` 下共 **89** 个 ArtDeco 相关 Vue 页面/块/模板
> - 整个 ArtDeco 前端生态共盘点到 **162** 个 Vue 文件

## 1. 先看治理口径

本目录严格区分两条主线：

1. **Base / UI 资产**
   位于 `web/frontend/src/components/artdeco/`
2. **Domain / Business 承载**
   位于 `web/frontend/src/components/artdeco/{trading,advanced,specialized}` 与 `web/frontend/src/views/artdeco-pages/**`

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

## 6. Top-Level Containers / Templates

### 6.1 顶层 ArtDeco 页面容器（10）

`ArtDecoDashboard`、`ArtDecoDataAnalysis`、`ArtDecoMarketData`、`ArtDecoMarketQuotes`、`ArtDecoRiskManagement`、`ArtDecoSettings`、`ArtDecoStockManagement`、`ArtDecoTechnicalAnalysis`、`ArtDecoTradingCenter`、`ArtDecoTradingManagement`

### 6.2 模板页（2）

`ArtDecoPageTemplate`、`ExampleRiskManagement`

## 7. 当前生态总览

| 区域 | 数量 | 定位 |
|------|------|------|
| `src/components/artdeco/base+core+business+charts` | 48 | Base / UI 主链 |
| `src/components/artdeco/trading+advanced+specialized` | 25 | Domain reusable 主链 |
| `views/artdeco-pages/components` | 23 | 页面系统内部共享片段 |
| `views/artdeco-pages/*-tabs` 等域块 | 54 | 域内工作台块与子组件 |
| 顶层容器与模板 | 12 | 页面承载与模板壳层 |
| **合计** | **162** | 当前 ArtDeco 生态 Vue 文件总数 |

## 8. 维护规则

- 新增组件前先查本目录，避免重复造轮子。
- 组件职责变化时，先改 `ARTDECO_COMPONENT_GUIDE.md`，再改本目录。
- 不要把 `*-tabs` 误记为 reusable base assets。
- 不要把 `views/artdeco-pages/components/` 误记为 `src/components/artdeco/` 的替代品。
- 当目录结构变化时，必须同步更新：
  - `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md`
  - `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`
  - `docs/api/ArtDeco_System_Architecture_Summary.md`
