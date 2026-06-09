# Secondary View Inventory

这是 `myweb-audit v2.1` 的二级资产库存清单。

用途：
- canonical route coverage matrix 清空 `?` 之后，作为第二阶段 backlog 入口
- 按 `候选待审 / 内嵌壳层 / Demo废弃` 三分类沉淀非主路由页面
- 直接复用 4 个启发式命中特征筛选高优 backlog

固定输出字段：页面路径、所属层级、是否含 selector、是否有 stats-strip / 指标卡、是否复用公共 composable、优先级标记。

## Summary

- generated_at: `2026-05-10T01:34:16.168Z`
- total_views: `272`
- routed_views: `42`
- unrouted_views: `230`
- classification_counts: `候选待审=70 / 内嵌壳层=104 / Demo废弃=56`
- priority_counts: `H=1 / M=123 / L=106`

## High-Priority Shortlist

| 页面路径 | 所属层级 | 分类 | selector | stats-strip/指标卡 | 公共 composable | 优先级 | 命中特征 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `web/frontend/src/views/ai/BatchAnalysis.vue` | ai | 候选待审 | Y | - | Y | H | selector, fallback-literal, shared-composable |

## Full Inventory

| 页面路径 | 所属层级 | 分类 | selector | stats-strip/指标卡 | 公共 composable | 优先级 | 命中特征 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `web/frontend/src/views/ai/BatchAnalysis.vue` | ai | 候选待审 | Y | - | Y | H | selector, fallback-literal, shared-composable |
| `web/frontend/src/views/advanced-analysis/AnomalyTrackingView.vue` | advanced-analysis | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/advanced-analysis/BatchAnalysisView.vue` | advanced-analysis | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/advanced-analysis/CapitalFlowView.vue` | advanced-analysis | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/advanced-analysis/ChipDistributionView.vue` | advanced-analysis | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/advanced-analysis/DecisionModelsView.vue` | advanced-analysis | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/advanced-analysis/FinancialValuationView.vue` | advanced-analysis | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/advanced-analysis/FundamentalAnalysisView.vue` | advanced-analysis | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/advanced-analysis/MarketPanoramaView.vue` | advanced-analysis | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/advanced-analysis/RadarAnalysisView.vue` | advanced-analysis | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/advanced-analysis/SentimentAnalysisView.vue` | advanced-analysis | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/advanced-analysis/TechnicalAnalysisView.vue` | advanced-analysis | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/advanced-analysis/TimeSeriesView.vue` | advanced-analysis | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/advanced-analysis/TradingSignalsView.vue` | advanced-analysis | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/AdvancedAnalysis.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/Analysis.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/BacktestAnalysis.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/BacktestWizard.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/Dashboard.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/EnhancedDashboard.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/EnhancedRiskMonitor.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/IndicatorLibrary.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/IndustryConceptAnalysis.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/Market.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/market/Auction.vue` | market | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/market/CapitalFlow.vue` | market | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/market/Concepts.vue` | market | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/market/Etf.vue` | market | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/market/MarketDataView.vue` | market | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/market/Tdx.vue` | market | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/MarketData.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/monitor.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/Phase4Dashboard.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/PortfolioManagement.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/RealTimeMonitor.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/risk/Portfolio.vue` | risk | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/risk/Positions.vue` | risk | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/RiskMonitor.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/Settings.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/settings/General.vue` | settings | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/settings/Notifications.vue` | settings | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/settings/Security.vue` | settings | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/settings/Theme.vue` | settings | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/StockDetail.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/Stocks.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/strategy/BatchScan.vue` | strategy | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/strategy/ResultsQuery.vue` | strategy | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/strategy/SingleRun.vue` | strategy | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/strategy/StatsAnalysis.vue` | strategy | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/strategy/StrategyList.vue` | strategy | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/StrategyManagement.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/system/Architecture.vue` | system | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/system/DatabaseMonitor.vue` | system | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/system/PerformanceMonitor.vue` | system | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/TaskManagement.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/TdxMarket.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/technical/TechnicalAnalysis.vue` | technical | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/TechnicalAnalysis.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/TestPage.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/TradeManagement.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/trading-decision/DecisionHeader.vue` | trading-decision | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/trading-decision/DecisionOrders.vue` | trading-decision | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/trading-decision/DecisionPortfolio.vue` | trading-decision | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/trading-decision/DecisionPositions.vue` | trading-decision | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/trading/Execution.vue` | trading | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/trading/History.vue` | trading | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/trading/Orders.vue` | trading | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/trading/Positions.vue` | trading | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/TradingDecisionCenter.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/Wencai.vue` | top-level | 候选待审 | - | - | - | M | - |
| `web/frontend/src/views/ai/components/AiSentimentHero.vue` | ai | 内嵌壳层 | - | Y | - | M | stats-strip |
| `web/frontend/src/views/ai/components/AiSentimentSummaryCards.vue` | ai | 内嵌壳层 | - | Y | - | M | stats-strip |
| `web/frontend/src/views/ai/components/AiSentimentWorkbenchPanels.vue` | ai | 内嵌壳层 | Y | - | - | M | selector, fallback-literal |
| `web/frontend/src/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue` | artdeco-embedded | 内嵌壳层 | Y | Y | Y | M | stats-strip, selector, fallback-literal, shared-composable |
| `web/frontend/src/views/artdeco-pages/_templates/ExampleRiskManagement.vue` | artdeco-embedded | 内嵌壳层 | Y | Y | - | M | stats-strip, selector, fallback-literal |
| `web/frontend/src/views/artdeco-pages/analysis-tabs/BacktestAnalysis.vue` | artdeco-embedded | 内嵌壳层 | - | Y | - | M | stats-strip |
| `web/frontend/src/views/artdeco-pages/ArtDecoMarketData.vue` | artdeco-embedded | 内嵌壳层 | Y | Y | - | M | stats-strip, selector, fallback-literal |
| `web/frontend/src/views/artdeco-pages/ArtDecoMarketQuotes.vue` | artdeco-embedded | 内嵌壳层 | Y | Y | - | M | stats-strip, selector, fallback-literal |
| `web/frontend/src/views/artdeco-pages/ArtDecoSettings.vue` | artdeco-embedded | 内嵌壳层 | Y | - | Y | M | selector, shared-composable |
| `web/frontend/src/views/artdeco-pages/ArtDecoStockManagement.vue` | artdeco-embedded | 内嵌壳层 | Y | Y | - | M | stats-strip, selector, fallback-literal |
| `web/frontend/src/views/artdeco-pages/ArtDecoTradingCenter.vue` | artdeco-embedded | 内嵌壳层 | Y | - | - | M | selector, fallback-literal |
| `web/frontend/src/views/artdeco-pages/ArtDecoTradingManagement.vue` | artdeco-embedded | 内嵌壳层 | Y | Y | Y | M | stats-strip, selector, shared-composable |
| `web/frontend/src/views/artdeco-pages/components/AnalysisIndicators.vue` | artdeco-embedded | 内嵌壳层 | Y | Y | - | M | stats-strip, selector |
| `web/frontend/src/views/artdeco-pages/components/AnomalyAlerts.vue` | artdeco-embedded | 内嵌壳层 | Y | - | - | M | selector |
| `web/frontend/src/views/artdeco-pages/components/ArtDecoAttributionAnalysis.vue` | artdeco-embedded | 内嵌壳层 | Y | - | - | M | selector |
| `web/frontend/src/views/artdeco-pages/components/ArtDecoAttributionControls.vue` | artdeco-embedded | 内嵌壳层 | Y | - | - | M | selector |
| `web/frontend/src/views/artdeco-pages/components/ArtDecoPerformanceOverview.vue` | artdeco-embedded | 内嵌壳层 | - | Y | - | M | stats-strip |
| `web/frontend/src/views/artdeco-pages/components/ArtDecoSignalHistory.vue` | artdeco-embedded | 内嵌壳层 | Y | - | - | M | selector |
| `web/frontend/src/views/artdeco-pages/components/ArtDecoSignalMonitoringOverview.vue` | artdeco-embedded | 内嵌壳层 | - | Y | - | M | stats-strip |
| `web/frontend/src/views/artdeco-pages/components/ArtDecoTradingHistoryControls.vue` | artdeco-embedded | 内嵌壳层 | Y | - | - | M | selector |
| `web/frontend/src/views/artdeco-pages/components/ArtDecoTradingSignalsControls.vue` | artdeco-embedded | 内嵌壳层 | Y | - | - | M | selector |
| `web/frontend/src/views/artdeco-pages/components/BuffettModel.vue` | artdeco-embedded | 内嵌壳层 | Y | - | - | M | selector |
| `web/frontend/src/views/artdeco-pages/components/LynchModel.vue` | artdeco-embedded | 内嵌壳层 | - | Y | - | M | stats-strip |
| `web/frontend/src/views/artdeco-pages/components/MarketFundFlow.vue` | artdeco-embedded | 内嵌壳层 | - | Y | - | M | stats-strip |
| `web/frontend/src/views/artdeco-pages/market-data-tabs/AuctionAnalysis.vue` | artdeco-embedded | 内嵌壳层 | - | Y | - | M | stats-strip |
| `web/frontend/src/views/artdeco-pages/market-data-tabs/ConceptAnalysis.vue` | artdeco-embedded | 内嵌壳层 | Y | Y | - | M | stats-strip, selector |
| `web/frontend/src/views/artdeco-pages/market-data-tabs/DataQualityPanel.vue` | artdeco-embedded | 内嵌壳层 | - | Y | - | M | stats-strip |
| `web/frontend/src/views/artdeco-pages/market-data-tabs/ETFAnalysis.vue` | artdeco-embedded | 内嵌壳层 | Y | Y | - | M | stats-strip, selector, fallback-literal |
| `web/frontend/src/views/artdeco-pages/market-data-tabs/FundFlow.vue` | artdeco-embedded | 内嵌壳层 | Y | Y | - | M | stats-strip, selector |
| `web/frontend/src/views/artdeco-pages/market-tabs/MarketETFTab.vue` | artdeco-embedded | 内嵌壳层 | Y | Y | Y | M | stats-strip, selector, fallback-literal, shared-composable |
| `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskStatsGrid.vue` | artdeco-embedded | 内嵌壳层 | - | Y | - | M | stats-strip |
| `web/frontend/src/views/artdeco-pages/settings/AppearanceSettings.vue` | artdeco-embedded | 内嵌壳层 | Y | - | - | M | selector |
| `web/frontend/src/views/artdeco-pages/settings/DataSourceSettings.vue` | artdeco-embedded | 内嵌壳层 | Y | - | - | M | selector |
| `web/frontend/src/views/artdeco-pages/settings/NotificationSettings.vue` | artdeco-embedded | 内嵌壳层 | Y | - | - | M | selector |
| `web/frontend/src/views/artdeco-pages/settings/SecuritySettings.vue` | artdeco-embedded | 内嵌壳层 | Y | - | - | M | selector |
| `web/frontend/src/views/artdeco-pages/settings/SystemInfoSettings.vue` | artdeco-embedded | 内嵌壳层 | Y | - | - | M | selector |
| `web/frontend/src/views/artdeco-pages/stock-management-tabs/PortfolioMonitor.vue` | artdeco-embedded | 内嵌壳层 | Y | Y | Y | M | stats-strip, selector, shared-composable |
| `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue` | artdeco-embedded | 内嵌壳层 | Y | Y | - | M | stats-strip, selector |
| `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue` | artdeco-embedded | 内嵌壳层 | Y | Y | - | M | stats-strip, selector |
| `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue` | artdeco-embedded | 内嵌壳层 | Y | Y | Y | M | stats-strip, selector, fallback-literal, shared-composable |
| `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue` | artdeco-embedded | 内嵌壳层 | Y | Y | Y | M | stats-strip, selector, fallback-literal, shared-composable |
| `web/frontend/src/views/artdeco-pages/strategy-tabs/components/BacktestKpiGrid.vue` | artdeco-embedded | 内嵌壳层 | - | Y | - | M | stats-strip |
| `web/frontend/src/views/artdeco-pages/strategy-tabs/components/BacktestWorkbenchTabs.vue` | artdeco-embedded | 内嵌壳层 | Y | - | - | M | selector |
| `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue` | artdeco-embedded | 内嵌壳层 | Y | Y | Y | M | stats-strip, selector, fallback-literal, shared-composable |
| `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue` | artdeco-embedded | 内嵌壳层 | - | Y | - | M | stats-strip |
| `web/frontend/src/views/artdeco-pages/technical-tabs/TechnicalScannerTab.vue` | artdeco-embedded | 内嵌壳层 | Y | Y | Y | M | stats-strip, selector, shared-composable |
| `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingSignals.vue` | artdeco-embedded | 内嵌壳层 | Y | - | - | M | selector |
| `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingStats.vue` | artdeco-embedded | 内嵌壳层 | - | Y | - | M | stats-strip |
| `web/frontend/src/views/components/RiskOverviewTab.vue` | components | 内嵌壳层 | Y | Y | - | M | stats-strip, selector, fallback-literal |
| `web/frontend/src/views/components/StopLossMonitoringTab.vue` | components | 内嵌壳层 | Y | - | Y | M | selector, shared-composable |
| `web/frontend/src/views/monitoring/AlertRulesManagement.vue` | monitoring | 内嵌壳层 | Y | - | Y | M | selector, shared-composable |
| `web/frontend/src/views/monitoring/RiskDashboard.vue` | monitoring | 内嵌壳层 | Y | Y | Y | M | stats-strip, selector, fallback-literal, shared-composable |
| `web/frontend/src/views/monitoring/WatchlistManagement.vue` | monitoring | 内嵌壳层 | Y | Y | Y | M | stats-strip, selector, fallback-literal, shared-composable |
| `web/frontend/src/views/stocks/Screener.vue` | stocks | 内嵌壳层 | Y | Y | - | M | stats-strip, selector, fallback-literal |
| `web/frontend/src/views/artdeco-pages/ArtDecoDataAnalysis.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/ArtDecoRiskManagement.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/ArtDecoTechnicalAnalysis.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/components/AnalysisResults.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/components/AnalysisScreener.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/components/AnomalyPatterns.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/components/ArtDecoSignalMonitoringMetrics.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/components/DupontAnalysis.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/components/FinancialMetrics.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/components/MarketConcepts.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/components/MarketPlaceholder.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/components/OneilModel.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/components/PanoramaCapitalFlow.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/components/PanoramaIndices.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoMarketAnalysis.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoMarketOverview.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoRealtimeMonitor.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/market-data-tabs/FundFlowAnalysis.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/market-tabs/MarketConceptTab.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/market-tabs/MarketKLineTab.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskMonitor.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskOverviewPanel.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskStockPanel.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/risk-tabs/RiskOverviewTab.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/strategy-tabs/components/BacktestHeader.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/system-tabs/SystemHealthTab.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoHistoryView.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPerformanceAnalysis.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPositionMonitor.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoSignalsView.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue` | artdeco-embedded | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/monitoring/MonitoringDashboard.vue` | monitoring | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/stocks/Activity.vue` | stocks | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/stocks/Concept.vue` | stocks | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/stocks/Industry.vue` | stocks | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/stocks/Portfolio.vue` | stocks | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/stocks/Watchlist.vue` | stocks | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/trade-management/components/PortfolioOverview.vue` | trade-management | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/trade-management/components/PositionsTab.vue` | trade-management | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/trade-management/components/StatisticsTab.vue` | trade-management | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/trade-management/components/TradeDialog.vue` | trade-management | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/trade-management/components/TradeHistoryTab.vue` | trade-management | 内嵌壳层 | - | - | - | L | - |
| `web/frontend/src/views/ArtDecoTest.vue` | top-level | Demo废弃 | - | Y | - | L | stats-strip |
| `web/frontend/src/views/DataVisualizationShowcase.vue` | top-level | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/demo/openstock/components/FeatureStatus.vue` | demo | Demo废弃 | - | - | - | L | - |
| `web/frontend/src/views/demo/openstock/components/HeatmapChart.vue` | demo | Demo废弃 | Y | - | - | L | selector, fallback-literal |
| `web/frontend/src/views/demo/openstock/components/KlineChart.vue` | demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/demo/openstock/components/StockNews.vue` | demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/demo/openstock/components/StockQuote.vue` | demo | Demo废弃 | Y | - | - | L | selector, fallback-literal |
| `web/frontend/src/views/demo/openstock/components/StockSearch.vue` | demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/demo/openstock/components/WatchlistManagement.vue` | demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/demo/OpenStockDemo.vue` | demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/demo/Phase4Dashboard.vue` | demo | Demo废弃 | Y | Y | Y | L | stats-strip, selector, shared-composable |
| `web/frontend/src/views/demo/pyprofiling/components/API.vue` | demo | Demo废弃 | - | - | - | L | - |
| `web/frontend/src/views/demo/pyprofiling/components/Data.vue` | demo | Demo废弃 | - | - | - | L | - |
| `web/frontend/src/views/demo/pyprofiling/components/Features.vue` | demo | Demo废弃 | - | - | - | L | - |
| `web/frontend/src/views/demo/pyprofiling/components/Overview.vue` | demo | Demo废弃 | - | - | - | L | - |
| `web/frontend/src/views/demo/pyprofiling/components/Prediction.vue` | demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/demo/pyprofiling/components/Profiling.vue` | demo | Demo废弃 | - | - | - | L | - |
| `web/frontend/src/views/demo/pyprofiling/components/Tech.vue` | demo | Demo废弃 | - | - | - | L | - |
| `web/frontend/src/views/demo/PyprofilingDemo.vue` | demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/demo/stock-analysis/components/Backtest.vue` | demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/demo/stock-analysis/components/DataParsing.vue` | demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/demo/stock-analysis/components/Overview.vue` | demo | Demo废弃 | - | - | - | L | - |
| `web/frontend/src/views/demo/stock-analysis/components/Realtime.vue` | demo | Demo废弃 | - | - | - | L | - |
| `web/frontend/src/views/demo/stock-analysis/components/Status.vue` | demo | Demo废弃 | - | - | - | L | - |
| `web/frontend/src/views/demo/stock-analysis/components/Strategy.vue` | demo | Demo废弃 | - | - | - | L | - |
| `web/frontend/src/views/demo/StockAnalysisDemo.vue` | demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/demo/Wencai.vue` | demo | Demo废弃 | Y | Y | - | L | stats-strip, selector, fallback-literal |
| `web/frontend/src/views/errors/Forbidden.vue` | demo | Demo废弃 | - | - | - | L | - |
| `web/frontend/src/views/errors/NetworkError.vue` | demo | Demo废弃 | Y | - | Y | L | selector, shared-composable |
| `web/frontend/src/views/errors/ServiceUnavailable.vue` | demo | Demo废弃 | - | - | - | L | - |
| `web/frontend/src/views/examples/PageConfigExample.vue` | demo | Demo废弃 | - | - | - | L | - |
| `web/frontend/src/views/examples/TradingDashboard.migrated.vue` | demo | Demo废弃 | Y | - | Y | L | selector, fallback-literal, shared-composable |
| `web/frontend/src/views/examples/WebSocketConfigExample.vue` | demo | Demo废弃 | Y | - | Y | L | selector, shared-composable |
| `web/frontend/src/views/freqtrade-demo/FreqBacktestTab.vue` | freqtrade-demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/freqtrade-demo/FreqConfigTab.vue` | freqtrade-demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/freqtrade-demo/FreqOverviewTab.vue` | freqtrade-demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/freqtrade-demo/FreqStatusTab.vue` | freqtrade-demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/freqtrade-demo/FreqStrategyTab.vue` | freqtrade-demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/freqtrade-demo/FreqWebuiTab.vue` | freqtrade-demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/FreqtradeDemo.vue` | top-level | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/KLineDemo.vue` | top-level | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/MarketDataDemo.vue` | top-level | Demo废弃 | Y | - | Y | L | selector, fallback-literal, shared-composable |
| `web/frontend/src/views/MinimalTest.vue` | top-level | Demo废弃 | - | - | - | L | - |
| `web/frontend/src/views/OpenStockDemo.vue` | top-level | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/PageTitleDemo.vue` | top-level | Demo废弃 | Y | - | Y | L | selector, shared-composable |
| `web/frontend/src/views/PyprofilingDemo.vue` | top-level | Demo废弃 | Y | - | Y | L | selector, shared-composable |
| `web/frontend/src/views/SkeletonUsage.vue` | top-level | Demo废弃 | - | - | - | L | - |
| `web/frontend/src/views/SmartDataSourceTest.vue` | top-level | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/StockAnalysisDemo.vue` | top-level | Demo废弃 | - | - | - | L | - |
| `web/frontend/src/views/tdxpy-demo/TdxApiTab.vue` | tdxpy-demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/tdxpy-demo/TdxExportTab.vue` | tdxpy-demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/tdxpy-demo/TdxInstallTab.vue` | tdxpy-demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/tdxpy-demo/TdxOverviewTab.vue` | tdxpy-demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/tdxpy-demo/TdxStatusTab.vue` | tdxpy-demo | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/TdxpyDemo.vue` | top-level | Demo废弃 | Y | - | - | L | selector |
| `web/frontend/src/views/Test.vue` | top-level | Demo废弃 | Y | - | - | L | selector |
