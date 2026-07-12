# MyStocks 前端未接入页面深度整合分析报告

> **历史分析说明**:
> 本文件是阶段性分析、审计、评估或复盘材料，不是当前基线、当前实施优先级或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内问题分级、差距判断、风险结论、审阅意见和建议动作如未重新复核，应视为历史分析结果，不得直接当作当前事实。


> 输出文件：`/opt/claude/mystocks_spec/reports/frontend-pages-integration-analysis.md`
> 数据来源：`/opt/claude/mystocks_spec/reports/frontend-pages-inventory.json` + 静态代码扫描（217 个未接入页面）
> 项目定位约束：个人/小型量化投资者，本地部署优先，避免企业级过度设计

## 1. 执行摘要

- 总页面数：252
- 已接入：35（现有菜单/路由主干）
- 未接入：217（本次分析对象）
- 未接入功能类型分布：交易工具 45, 表单和输入 45, 分析工具 41, 监控和告警 31, 数据表格 20, 系统工具 19, 数据可视化 10, 策略工具 6
- 未接入复用度分布：高 39 / 中 25 / 低 153
- 未接入组件形态：page 126, demo 49, component 33, archive 9
- 未接入功能域：综合/跨域 58, 数据分析 42, 市场行情 35, 交易管理 32, 系统设置 21, 策略管理 17, 风险管理 12

### 1.1 关键发现

1. **高价值复用集中在 ArtDeco 子组件与 trade-management/components**：可直接作为已接入页面的新模块接入，能快速提升功能密度。
2. **大量 `demo/converted.archive` 页面不建议直接接入**：应提炼“能力”而非“页面”，避免将实验性结构引入主干。
3. **分析/交易/市场三个域增益最大**：未接入页面中这三类占比高，且与现有 35 页主干高度互补。
4. **建议采用“主页面 + 标签页 + 可复用组件/Composable”整合路线**，而非继续扩展一级菜单，控制导航复杂度。

### 1.2 优先级建议（面向个人投资者）

- **P0（2-3 周）**：接入高复用且 clean 的交易/风险/策略子模块（先“可见收益”）。
- **P1（3-5 周）**：将 advanced-analysis 能力折叠入现有 data/market/strategy 标签页。
- **P2（持续）**：清理重复与 demo/archive 技术债，沉淀共享组件 + composables。

## 2. 功能分类清单（217 未接入页面）

### 2.1 按功能类型统计

| 功能类型 | 数量 | 代表页面（示例） |
|---|---:|---|
| 交易工具 | 45 | ArtDecoTest.vue<br>FreqtradeDemo.vue<br>MarketData.vue<br>SkeletonUsage.vue |
| 表单和输入 | 45 | BacktestAnalysis.vue<br>BacktestWizard.vue<br>IndicatorLibrary.vue<br>IndustryConceptAnalysis.vue |
| 分析工具 | 41 | AdvancedAnalysis.vue<br>Analysis.vue<br>StockAnalysisDemo.vue<br>TechnicalAnalysis.vue |
| 监控和告警 | 31 | EnhancedRiskMonitor.vue<br>MarketDataDemo.vue<br>RealTimeMonitor.vue<br>RiskMonitor.vue |
| 数据表格 | 20 | Dashboard.vue<br>EnhancedDashboard.vue<br>Market.vue<br>Phase4Dashboard.vue |
| 系统工具 | 19 | MinimalTest.vue<br>artdeco-pages/ArtDecoSettings.vue<br>artdeco-pages/components/ArtDecoPerformanceOverview.vue<br>artdeco-pages/components/PanoramaCapitalFlow.vue |
| 数据可视化 | 10 | DataVisualizationShowcase.vue<br>KLineDemo.vue<br>OpenStockDemo.vue<br>StockDetail.vue |
| 策略工具 | 6 | artdeco-pages/strategy-tabs/components/BacktestHeader.vue<br>artdeco-pages/strategy-tabs/components/BacktestKpiGrid.vue<br>artdeco-pages/strategy-tabs/components/BacktestWorkbenchTabs.vue<br>converted.archive/backtest-management.vue |

### 2.2 按功能域统计

| 功能域 | 未接入数量 | 已接入锚点页面（用于整合） |
|---|---:|---|
| 综合/跨域 | 58 | artdeco-pages/ArtDecoDashboard.vue<br>artdeco-pages/stock-management-tabs/WatchlistManager.vue<br>stocks/Screener.vue |
| 数据分析 | 42 | artdeco-pages/ArtDecoDataAnalysis.vue<br>artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue |
| 市场行情 | 35 | artdeco-pages/analysis-tabs/KLineAnalysis.vue<br>artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue<br>artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue |
| 交易管理 | 32 | TradingDashboard.vue<br>artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue<br>artdeco-pages/stock-management-tabs/PortfolioMonitor.vue |
| 系统设置 | 21 | announcement/AnnouncementMonitor.vue<br>artdeco-pages/system-tabs/ArtDecoDataManagement.vue<br>artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue |
| 策略管理 | 17 | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue<br>artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue<br>artdeco-pages/strategy-tabs/StrategyParametersTab.vue |
| 风险管理 | 12 | artdeco-pages/ArtDecoRiskManagement.vue<br>artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue<br>artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue |

### 2.3 按复用度统计

| 复用度 | 数量 | 策略 |
|---|---:|---|
| 高 | 39 | 优先整合到现有 35 页，尽量不新增路由 |
| 中 | 25 | 作为二期能力补充或抽象为 composable |
| 低 | 153 | 以清理/归档为主，仅提取局部代码片段 |

### 2.4 未接入页面功能明细（分组）

#### 交易工具（45）

| 页面 | 功能域 | 能力标签 | 复用度 | 健康度 |
|---|---|---|---|---|
| FreqtradeDemo.vue | 交易管理 | 监控告警、分析计算、交易操作 | 低 | clean |
| TradeManagement.vue | 交易管理 | 配置/输入、监控告警、分析计算 | 中 | clean |
| TradingDecisionCenter.vue | 交易管理 | 图表可视化、监控告警、分析计算 | 中 | clean |
| artdeco-pages/ArtDecoTradingManagement.vue | 交易管理 | 配置/输入、监控告警、分析计算 | 低 | error |
| artdeco-pages/components/ArtDecoTradingHistoryControls.vue | 交易管理 | 配置/输入、分析计算、交易操作 | 高 | clean |
| artdeco-pages/trading-tabs/ArtDecoHistoryView.vue | 交易管理 | 分析计算、交易操作、策略能力 | 低 | clean |
| artdeco-pages/trading-tabs/ArtDecoPositionMonitor.vue | 交易管理 | 监控告警、分析计算、交易操作 | 低 | clean |
| artdeco-pages/trading-tabs/ArtDecoTradingStats.vue | 交易管理 | 分析计算、交易操作 | 低 | clean |
| converted.archive/trading-management.vue | 交易管理 | 配置/输入、监控告警、分析计算 | 低 | clean |
| examples/TradingDashboard.migrated.vue | 交易管理 | 数据表格、配置/输入、监控告警 | 低 | clean |
| freqtrade-demo/FreqConfigTab.vue | 交易管理 | 监控告警、交易操作、策略能力 | 低 | error |
| freqtrade-demo/FreqOverviewTab.vue | 交易管理 | 监控告警、分析计算、交易操作 | 低 | clean |
| freqtrade-demo/FreqStatusTab.vue | 交易管理 | 监控告警、交易操作、系统管理 | 低 | clean |
| freqtrade-demo/FreqWebuiTab.vue | 交易管理 | 数据表格、监控告警、交易操作 | 低 | clean |
| risk/Positions.vue | 交易管理 | 监控告警、分析计算、交易操作 | 低 | clean |
| stocks/Portfolio.vue | 交易管理 | 数据表格、配置/输入、分析计算 | 低 | clean |
| trade-management/components/PortfolioOverview.vue | 交易管理 | 监控告警、交易操作 | 高 | clean |
| trade-management/components/PositionsTab.vue | 交易管理 | 数据表格、监控告警、交易操作 | 高 | clean |
| trade-management/components/StatisticsTab.vue | 交易管理 | 图表可视化、监控告警、交易操作 | 高 | clean |
| trade-management/components/TradeDialog.vue | 交易管理 | 配置/输入、监控告警、分析计算 | 高 | clean |
| trading-decision/DecisionHeader.vue | 交易管理 | 交易操作 | 低 | clean |
| trading-decision/DecisionPortfolio.vue | 交易管理 | 监控告警、交易操作 | 低 | clean |
| trading-decision/DecisionPositions.vue | 交易管理 | 交易操作 | 低 | clean |
| trading/Execution.vue | 交易管理 | 监控告警、交易操作 | 低 | clean |
| trading/History.vue | 交易管理 | 监控告警、交易操作、系统管理 | 低 | clean |
| trading/Orders.vue | 交易管理 | 监控告警、交易操作 | 低 | clean |
| trading/Positions.vue | 交易管理 | 监控告警、交易操作 | 低 | clean |
| MarketData.vue | 市场行情 | 交易操作 | 低 | clean |
| artdeco-pages/components/MarketConcepts.vue | 市场行情 | 交易操作 | 高 | clean |
| artdeco-pages/components/MarketFundFlow.vue | 市场行情 | 交易操作 | 高 | clean |
| artdeco-pages/market-data-tabs/ArtDecoMarketOverview.vue | 市场行情 | 交易操作 | 低 | clean |
| artdeco-pages/market-tabs/MarketETFTab.vue | 市场行情 | 交易操作、系统管理 | 低 | error |
| artdeco-pages/components/ArtDecoSignalHistory.vue | 策略管理 | 分析计算、交易操作、系统管理 | 高 | clean |
| artdeco-pages/components/ArtDecoSignalMonitoringMetrics.vue | 策略管理 | 监控告警、分析计算、交易操作 | 高 | clean |
| artdeco-pages/components/ArtDecoSignalMonitoringOverview.vue | 策略管理 | 监控告警、分析计算、交易操作 | 高 | clean |
| artdeco-pages/components/ArtDecoTradingSignalsControls.vue | 策略管理 | 分析计算、交易操作 | 高 | clean |
| ArtDecoTest.vue | 综合/跨域 | 交易操作 | 低 | clean |
| SkeletonUsage.vue | 综合/跨域 | 交易操作 | 低 | clean |
| Test.vue | 综合/跨域 | 交易操作 | 低 | clean |
| TestPage.vue | 综合/跨域 | 交易操作 | 低 | clean |
| artdeco-pages/components/FinancialMetrics.vue | 综合/跨域 | 交易操作 | 高 | clean |
| artdeco-pages/components/PanoramaIndices.vue | 综合/跨域 | 交易操作 | 高 | clean |
| converted.archive/stock-management.vue | 综合/跨域 | 交易操作 | 低 | clean |
| demo/PyprofilingDemo.vue | 综合/跨域 | 分析计算、交易操作、系统管理 | 低 | clean |
| errors/Forbidden.vue | 综合/跨域 | 监控告警、分析计算、交易操作 | 低 | clean |

#### 表单和输入（45）

| 页面 | 功能域 | 能力标签 | 复用度 | 健康度 |
|---|---|---|---|---|
| trade-management/components/TradeHistoryTab.vue | 交易管理 | 数据表格、配置/输入、监控告警 | 高 | clean |
| IndustryConceptAnalysis.vue | 市场行情 | 图表可视化、配置/输入、分析计算 | 低 | clean |
| TdxMarket.vue | 市场行情 | 图表可视化、配置/输入、监控告警 | 低 | clean |
| artdeco-pages/ArtDecoMarketData.vue | 市场行情 | 配置/输入、监控告警、分析计算 | 中 | clean |
| artdeco-pages/ArtDecoMarketQuotes.vue | 市场行情 | 配置/输入、监控告警、分析计算 | 低 | error |
| artdeco-pages/market-data-tabs/ConceptAnalysis.vue | 市场行情 | 配置/输入、分析计算、交易操作 | 低 | clean |
| artdeco-pages/market-data-tabs/FundFlow.vue | 市场行情 | 配置/输入、分析计算、交易操作 | 低 | clean |
| demo/openstock/components/StockQuote.vue | 市场行情 | 配置/输入、监控告警、分析计算 | 中 | error |
| market/Concepts.vue | 市场行情 | 数据表格、配置/输入、监控告警 | 低 | clean |
| market/Etf.vue | 市场行情 | 数据表格、配置/输入、监控告警 | 低 | clean |
| market/Realtime.vue | 市场行情 | 数据表格、配置/输入、监控告警 | 低 | clean |
| market/Tdx.vue | 市场行情 | 图表可视化、配置/输入、监控告警 | 低 | clean |
| BacktestAnalysis.vue | 数据分析 | 图表可视化、数据表格、配置/输入 | 低 | clean |
| IndicatorLibrary.vue | 数据分析 | 图表可视化、配置/输入、监控告警 | 低 | clean |
| artdeco-pages/components/AnalysisScreener.vue | 数据分析 | 配置/输入、分析计算 | 高 | clean |
| demo/stock-analysis/components/DataParsing.vue | 数据分析 | 数据表格、配置/输入、监控告警 | 中 | clean |
| stock-analysis/StockStrategyTab.vue | 数据分析 | 配置/输入、监控告警、分析计算 | 低 | warning |
| strategy/StatsAnalysis.vue | 数据分析 | 数据表格、配置/输入、分析计算 | 低 | clean |
| technical/TechnicalAnalysis.vue | 数据分析 | 数据表格、配置/输入、监控告警 | 低 | clean |
| BacktestWizard.vue | 策略管理 | 数据表格、配置/输入、分析计算 | 低 | clean |
| StrategyManagement.vue | 策略管理 | 配置/输入、监控告警、分析计算 | 低 | clean |
| artdeco-pages/trading-tabs/ArtDecoTradingSignals.vue | 策略管理 | 配置/输入、分析计算、交易操作 | 低 | clean |
| strategy/BatchScan.vue | 策略管理 | 配置/输入、监控告警、分析计算 | 低 | clean |
| strategy/ResultsQuery.vue | 策略管理 | 配置/输入、监控告警、分析计算 | 低 | clean |
| strategy/SingleRun.vue | 策略管理 | 配置/输入、监控告警、分析计算 | 低 | clean |
| strategy/StrategyList.vue | 策略管理 | 配置/输入、监控告警、分析计算 | 低 | clean |
| Settings.vue | 系统设置 | 数据表格、配置/输入、监控告警 | 低 | clean |
| artdeco-pages/settings/AppearanceSettings.vue | 系统设置 | 配置/输入、分析计算、系统管理 | 低 | clean |
| PageTitleDemo.vue | 综合/跨域 | 配置/输入、监控告警、分析计算 | 低 | clean |
| PyprofilingDemo.vue | 综合/跨域 | 数据表格、配置/输入、监控告警 | 低 | clean |
| SmartDataSourceTest.vue | 综合/跨域 | 配置/输入、监控告警、分析计算 | 低 | clean |
| Stocks.vue | 综合/跨域 | 配置/输入、监控告警、分析计算 | 低 | warning |
| TaskManagement.vue | 综合/跨域 | 配置/输入、监控告警、分析计算 | 中 | clean |
| artdeco-pages/ArtDecoStockManagement.vue | 综合/跨域 | 配置/输入、监控告警、交易操作 | 低 | error |
| artdeco-pages/_templates/ArtDecoPageTemplate.vue | 综合/跨域 | 配置/输入、监控告警、系统管理 | 低 | clean |
| artdeco-pages/components/ArtDecoAttributionControls.vue | 综合/跨域 | 配置/输入、分析计算 | 高 | clean |
| converted.archive/setting.vue | 综合/跨域 | 配置/输入、监控告警、分析计算 | 低 | clean |
| demo/Wencai.vue | 综合/跨域 | 配置/输入、监控告警、分析计算 | 低 | clean |
| demo/openstock/components/StockNews.vue | 综合/跨域 | 配置/输入、监控告警、分析计算 | 中 | error |
| demo/openstock/components/StockSearch.vue | 综合/跨域 | 数据表格、配置/输入、监控告警 | 中 | error |
| demo/pyprofiling/components/Features.vue | 综合/跨域 | 数据表格、配置/输入、监控告警 | 中 | clean |
| examples/WebSocketConfigExample.vue | 综合/跨域 | 配置/输入、监控告警、分析计算 | 低 | clean |
| tdxpy-demo/TdxOverviewTab.vue | 综合/跨域 | 配置/输入、监控告警、交易操作 | 低 | clean |
| components/StopLossMonitoringTab.vue | 风险管理 | 数据表格、配置/输入、监控告警 | 高 | clean |
| monitoring/AlertRulesManagement.vue | 风险管理 | 配置/输入、监控告警、分析计算 | 低 | clean |

#### 分析工具（41）

| 页面 | 功能域 | 能力标签 | 复用度 | 健康度 |
|---|---|---|---|---|
| advanced-analysis/MarketPanoramaView.vue | 市场行情 | 分析计算 | 低 | clean |
| artdeco-pages/market-data-tabs/ArtDecoMarketAnalysis.vue | 市场行情 | 分析计算、交易操作 | 低 | clean |
| artdeco-pages/market-data-tabs/AuctionAnalysis.vue | 市场行情 | 分析计算 | 低 | clean |
| artdeco-pages/market-data-tabs/ETFAnalysis.vue | 市场行情 | 分析计算、交易操作、系统管理 | 低 | clean |
| market/CapitalFlow.vue | 市场行情 | 数据表格、监控告警、分析计算 | 低 | clean |
| AdvancedAnalysis.vue | 数据分析 | 图表可视化、配置/输入、监控告警 | 中 | clean |
| Analysis.vue | 数据分析 | 图表可视化、配置/输入、监控告警 | 低 | clean |
| StockAnalysisDemo.vue | 数据分析 | 监控告警、分析计算、交易操作 | 低 | clean |
| TechnicalAnalysis.vue | 数据分析 | 图表可视化、配置/输入、分析计算 | 低 | clean |
| advanced-analysis/AnomalyTrackingView.vue | 数据分析 | 分析计算 | 低 | clean |
| advanced-analysis/BatchAnalysisView.vue | 数据分析 | 分析计算 | 低 | clean |
| advanced-analysis/CapitalFlowView.vue | 数据分析 | 分析计算、系统管理 | 低 | clean |
| advanced-analysis/ChipDistributionView.vue | 数据分析 | 分析计算 | 低 | clean |
| advanced-analysis/DecisionModelsView.vue | 数据分析 | 分析计算 | 低 | clean |
| advanced-analysis/FinancialValuationView.vue | 数据分析 | 分析计算 | 低 | clean |
| advanced-analysis/FundamentalAnalysisView.vue | 数据分析 | 数据表格、监控告警、分析计算 | 低 | clean |
| advanced-analysis/RadarAnalysisView.vue | 数据分析 | 图表可视化、监控告警、分析计算 | 低 | clean |
| advanced-analysis/SentimentAnalysisView.vue | 数据分析 | 分析计算 | 低 | clean |
| advanced-analysis/TechnicalAnalysisView.vue | 数据分析 | 配置/输入、监控告警、分析计算 | 低 | clean |
| advanced-analysis/TimeSeriesView.vue | 数据分析 | 分析计算 | 低 | clean |
| advanced-analysis/TradingSignalsView.vue | 数据分析 | 配置/输入、分析计算 | 低 | clean |
| artdeco-pages/ArtDecoTechnicalAnalysis.vue | 数据分析 | 图表可视化、监控告警、分析计算 | 低 | error |
| artdeco-pages/analysis-tabs/BacktestAnalysis.vue | 数据分析 | 分析计算、交易操作、策略能力 | 低 | clean |
| artdeco-pages/components/AnalysisIndicators.vue | 数据分析 | 配置/输入、分析计算、交易操作 | 高 | clean |
| artdeco-pages/components/AnalysisResults.vue | 数据分析 | 分析计算 | 高 | clean |
| artdeco-pages/components/ArtDecoAttributionAnalysis.vue | 数据分析 | 分析计算、交易操作 | 高 | clean |
| artdeco-pages/components/DupontAnalysis.vue | 数据分析 | 监控告警、分析计算、交易操作 | 高 | clean |
| artdeco-pages/trading-tabs/ArtDecoPerformanceAnalysis.vue | 数据分析 | 分析计算、交易操作、系统管理 | 低 | clean |
| converted.archive/data-analysis.vue | 数据分析 | 分析计算、交易操作 | 低 | clean |
| demo/StockAnalysisDemo.vue | 数据分析 | 监控告警、分析计算、交易操作 | 低 | clean |
| demo/stock-analysis/components/Overview.vue | 数据分析 | 监控告警、分析计算、交易操作 | 高 | clean |
| demo/stock-analysis/components/Realtime.vue | 数据分析 | 配置/输入、监控告警、分析计算 | 中 | clean |
| demo/stock-analysis/components/Status.vue | 数据分析 | 监控告警、分析计算、交易操作 | 高 | clean |
| demo/stock-analysis/components/Strategy.vue | 数据分析 | 配置/输入、监控告警、分析计算 | 中 | clean |
| stock-analysis/StockOverviewTab.vue | 数据分析 | 监控告警、分析计算、交易操作 | 低 | clean |
| stock-analysis/StockStatusTab.vue | 数据分析 | 监控告警、分析计算、交易操作 | 低 | clean |
| artdeco-pages/components/AnomalyPatterns.vue | 综合/跨域 | 分析计算、交易操作 | 高 | clean |
| artdeco-pages/components/BuffettModel.vue | 综合/跨域 | 分析计算、交易操作 | 高 | clean |
| artdeco-pages/components/LynchModel.vue | 综合/跨域 | 分析计算、交易操作 | 高 | clean |
| artdeco-pages/components/OneilModel.vue | 综合/跨域 | 分析计算、交易操作 | 高 | clean |
| artdeco-pages/technical-tabs/TechnicalScannerTab.vue | 综合/跨域 | 分析计算、交易操作、策略能力 | 低 | error |

#### 监控和告警（31）

| 页面 | 功能域 | 能力标签 | 复用度 | 健康度 |
|---|---|---|---|---|
| artdeco-pages/ArtDecoTradingCenter.vue | 交易管理 | 配置/输入、监控告警、分析计算 | 中 | clean |
| risk/Portfolio.vue | 交易管理 | 监控告警、分析计算、交易操作 | 低 | clean |
| MarketDataDemo.vue | 市场行情 | 监控告警、交易操作、系统管理 | 低 | clean |
| artdeco-pages/market-data-tabs/ArtDecoRealtimeMonitor.vue | 市场行情 | 监控告警、交易操作 | 低 | clean |
| artdeco-pages/market-data-tabs/DataQualityPanel.vue | 市场行情 | 监控告警、交易操作 | 低 | clean |
| converted.archive/market-quotes.vue | 市场行情 | 图表可视化、监控告警、分析计算 | 低 | clean |
| market/Auction.vue | 市场行情 | 数据表格、监控告警、分析计算 | 低 | clean |
| stock-analysis/StockDataTab.vue | 数据分析 | 数据表格、配置/输入、监控告警 | 低 | clean |
| stock-analysis/StockRealtimeTab.vue | 数据分析 | 配置/输入、监控告警、分析计算 | 低 | clean |
| RealTimeMonitor.vue | 系统设置 | 监控告警、策略能力、系统管理 | 中 | clean |
| demo/pyprofiling/components/API.vue | 系统设置 | 数据表格、监控告警、分析计算 | 高 | clean |
| monitor.vue | 系统设置 | 监控告警、分析计算、系统管理 | 低 | clean |
| monitoring/MonitoringDashboard.vue | 系统设置 | 数据表格、监控告警、分析计算 | 低 | clean |
| TdxpyDemo.vue | 综合/跨域 | 图表可视化、监控告警、系统管理 | 低 | clean |
| Wencai.vue | 综合/跨域 | 监控告警、系统管理 | 低 | clean |
| converted.archive/dashboard.vue | 综合/跨域 | 监控告警、分析计算、交易操作 | 低 | clean |
| demo/pyprofiling/components/Overview.vue | 综合/跨域 | 监控告警、交易操作 | 高 | clean |
| demo/pyprofiling/components/Prediction.vue | 综合/跨域 | 监控告警、分析计算、系统管理 | 中 | clean |
| errors/NetworkError.vue | 综合/跨域 | 监控告警、分析计算、交易操作 | 低 | clean |
| examples/PageConfigExample.vue | 综合/跨域 | 监控告警、交易操作、系统管理 | 低 | clean |
| tdxpy-demo/TdxStatusTab.vue | 综合/跨域 | 监控告警、交易操作、系统管理 | 低 | clean |
| EnhancedRiskMonitor.vue | 风险管理 | 配置/输入、监控告警、分析计算 | 中 | clean |
| RiskMonitor.vue | 风险管理 | 图表可视化、数据表格、监控告警 | 低 | clean |
| artdeco-pages/_templates/ExampleRiskManagement.vue | 风险管理 | 数据表格、配置/输入、监控告警 | 低 | clean |
| artdeco-pages/components/AnomalyAlerts.vue | 风险管理 | 监控告警、分析计算、交易操作 | 高 | clean |
| artdeco-pages/risk-tabs/ArtDecoRiskMonitor.vue | 风险管理 | 监控告警、交易操作 | 低 | clean |
| components/RiskOverviewTab.vue | 风险管理 | 图表可视化、配置/输入、监控告警 | 高 | clean |
| converted.archive/risk-management.vue | 风险管理 | 监控告警、交易操作 | 低 | clean |
| monitoring/RiskDashboard.vue | 风险管理 | 监控告警、分析计算、交易操作 | 低 | clean |
| risk/Alerts.vue | 风险管理 | 监控告警、系统管理 | 低 | clean |
| risk/Overview.vue | 风险管理 | 监控告警、交易操作 | 低 | clean |

#### 数据表格（20）

| 页面 | 功能域 | 能力标签 | 复用度 | 健康度 |
|---|---|---|---|---|
| PortfolioManagement.vue | 交易管理 | 图表可视化、数据表格、配置/输入 | 低 | clean |
| trading-decision/DecisionOrders.vue | 交易管理 | 数据表格、配置/输入、监控告警 | 低 | clean |
| Market.vue | 市场行情 | 数据表格、监控告警、交易操作 | 低 | clean |
| converted.archive/market-data.vue | 市场行情 | 数据表格、配置/输入、监控告警 | 低 | clean |
| market/MarketDataView.vue | 市场行情 | 数据表格、监控告警、交易操作 | 中 | clean |
| stocks/Concept.vue | 市场行情 | 数据表格、配置/输入、监控告警 | 低 | clean |
| stocks/Industry.vue | 市场行情 | 数据表格、配置/输入、监控告警 | 低 | clean |
| demo/stock-analysis/components/Backtest.vue | 数据分析 | 数据表格、配置/输入、监控告警 | 中 | clean |
| stock-analysis/StockBacktestTab.vue | 数据分析 | 数据表格、配置/输入、监控告警 | 低 | clean |
| monitoring/WatchlistManagement.vue | 系统设置 | 数据表格、配置/输入、监控告警 | 低 | clean |
| Dashboard.vue | 综合/跨域 | 图表可视化、数据表格、配置/输入 | 中 | clean |
| EnhancedDashboard.vue | 综合/跨域 | 图表可视化、数据表格、配置/输入 | 低 | clean |
| Phase4Dashboard.vue | 综合/跨域 | 数据表格、监控告警、交易操作 | 低 | clean |
| demo/Phase4Dashboard.vue | 综合/跨域 | 图表可视化、数据表格、监控告警 | 低 | clean |
| demo/openstock/components/WatchlistManagement.vue | 综合/跨域 | 数据表格、配置/输入、监控告警 | 高 | clean |
| demo/pyprofiling/components/Data.vue | 综合/跨域 | 数据表格、监控告警、分析计算 | 中 | clean |
| demo/pyprofiling/components/Profiling.vue | 综合/跨域 | 数据表格、监控告警、分析计算 | 高 | clean |
| demo/pyprofiling/components/Tech.vue | 综合/跨域 | 数据表格、监控告警、交易操作 | 中 | clean |
| stocks/Activity.vue | 综合/跨域 | 数据表格、配置/输入、监控告警 | 低 | clean |
| stocks/Watchlist.vue | 综合/跨域 | 数据表格、配置/输入、分析计算 | 低 | clean |

#### 系统工具（19）

| 页面 | 功能域 | 能力标签 | 复用度 | 健康度 |
|---|---|---|---|---|
| artdeco-pages/ArtDecoSettings.vue | 系统设置 | 分析计算、系统管理 | 低 | clean |
| artdeco-pages/components/PanoramaCapitalFlow.vue | 系统设置 | 交易操作、系统管理 | 高 | clean |
| artdeco-pages/settings/DataSourceSettings.vue | 系统设置 | 配置/输入、监控告警、分析计算 | 低 | clean |
| artdeco-pages/settings/NotificationSettings.vue | 系统设置 | 配置/输入、监控告警、分析计算 | 低 | clean |
| artdeco-pages/settings/SecuritySettings.vue | 系统设置 | 配置/输入、监控告警、分析计算 | 低 | clean |
| artdeco-pages/settings/SystemInfoSettings.vue | 系统设置 | 监控告警、系统管理 | 低 | clean |
| settings/General.vue | 系统设置 | 监控告警、系统管理 | 低 | clean |
| settings/Notifications.vue | 系统设置 | 监控告警、系统管理 | 低 | clean |
| settings/Security.vue | 系统设置 | 监控告警、系统管理 | 低 | clean |
| settings/Theme.vue | 系统设置 | 监控告警、系统管理 | 低 | clean |
| system/Architecture.vue | 系统设置 | 图表可视化、数据表格、监控告警 | 低 | clean |
| system/DatabaseMonitor.vue | 系统设置 | 监控告警、系统管理 | 低 | clean |
| system/PerformanceMonitor.vue | 系统设置 | 配置/输入、监控告警、策略能力 | 低 | clean |
| tdxpy-demo/TdxApiTab.vue | 系统设置 | 图表可视化、数据表格、监控告警 | 低 | clean |
| MinimalTest.vue | 综合/跨域 | 通用页面容器 | 低 | clean |
| artdeco-pages/components/ArtDecoPerformanceOverview.vue | 综合/跨域 | 系统管理 | 高 | clean |
| errors/ServiceUnavailable.vue | 综合/跨域 | 监控告警、分析计算、系统管理 | 低 | clean |
| tdxpy-demo/TdxExportTab.vue | 综合/跨域 | 监控告警、交易操作、系统管理 | 低 | error |
| tdxpy-demo/TdxInstallTab.vue | 综合/跨域 | 数据表格、配置/输入、监控告警 | 低 | error |

#### 数据可视化（10）

| 页面 | 功能域 | 能力标签 | 复用度 | 健康度 |
|---|---|---|---|---|
| KLineDemo.vue | 市场行情 | 图表可视化、交易操作 | 低 | clean |
| artdeco-pages/components/MarketPlaceholder.vue | 市场行情 | 通用页面容器 | 高 | clean |
| demo/openstock/components/KlineChart.vue | 市场行情 | 图表可视化、配置/输入、监控告警 | 中 | error |
| market/Technical.vue | 市场行情 | 图表可视化、配置/输入、分析计算 | 低 | clean |
| DataVisualizationShowcase.vue | 综合/跨域 | 图表可视化、配置/输入、监控告警 | 中 | clean |
| OpenStockDemo.vue | 综合/跨域 | 图表可视化、监控告警、交易操作 | 低 | clean |
| StockDetail.vue | 综合/跨域 | 图表可视化、配置/输入、分析计算 | 低 | error |
| demo/OpenStockDemo.vue | 综合/跨域 | 图表可视化、监控告警、交易操作 | 低 | clean |
| demo/openstock/components/FeatureStatus.vue | 综合/跨域 | 图表可视化、监控告警、交易操作 | 中 | clean |
| demo/openstock/components/HeatmapChart.vue | 综合/跨域 | 图表可视化、监控告警、交易操作 | 中 | error |

#### 策略工具（6）

| 页面 | 功能域 | 能力标签 | 复用度 | 健康度 |
|---|---|---|---|---|
| artdeco-pages/strategy-tabs/components/BacktestHeader.vue | 策略管理 | 监控告警、策略能力 | 高 | clean |
| artdeco-pages/strategy-tabs/components/BacktestKpiGrid.vue | 策略管理 | 策略能力 | 高 | clean |
| artdeco-pages/strategy-tabs/components/BacktestWorkbenchTabs.vue | 策略管理 | 策略能力 | 高 | clean |
| converted.archive/backtest-management.vue | 策略管理 | 配置/输入、监控告警、分析计算 | 低 | clean |
| freqtrade-demo/FreqBacktestTab.vue | 策略管理 | 数据表格、监控告警、分析计算 | 低 | error |
| freqtrade-demo/FreqStrategyTab.vue | 策略管理 | 监控告警、分析计算、交易操作 | 低 | error |

## 3. 复用机会识别

### 3.1 高复用组件机会（Top 20）

| 源页面 | 推荐接入目标 | 整合方式 | 价值 |
|---|---|---|---|
| trade-management/components/PortfolioOverview.vue | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 作为现有页新模块嵌入 | 补齐交易闭环 |
| artdeco-pages/components/AnalysisIndicators.vue | artdeco-pages/market-tabs/MarketKLineTab.vue | 作为现有页新模块嵌入 | 补齐分析链路 |
| artdeco-pages/components/ArtDecoSignalMonitoringOverview.vue | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 作为现有页新模块嵌入 | 提升功能密度与一致性 |
| artdeco-pages/components/MarketFundFlow.vue | artdeco-pages/market-tabs/MarketKLineTab.vue | 作为现有页新模块嵌入 | 提升功能密度与一致性 |
| artdeco-pages/components/ArtDecoTradingSignalsControls.vue | artdeco-pages/market-tabs/MarketKLineTab.vue | 作为现有页新模块嵌入 | 提升功能密度与一致性 |
| artdeco-pages/components/AnalysisScreener.vue | artdeco-pages/ArtDecoDataAnalysis.vue | 作为现有页新模块嵌入 | 补齐分析链路 |
| artdeco-pages/components/MarketConcepts.vue | artdeco-pages/market-tabs/MarketKLineTab.vue | 作为现有页新模块嵌入 | 提升功能密度与一致性 |
| artdeco-pages/components/LynchModel.vue | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 作为现有页新模块嵌入 | 提升功能密度与一致性 |
| artdeco-pages/components/BuffettModel.vue | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 作为现有页新模块嵌入 | 提升功能密度与一致性 |
| artdeco-pages/components/OneilModel.vue | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | 作为现有页新模块嵌入 | 提升功能密度与一致性 |
| artdeco-pages/components/PanoramaCapitalFlow.vue | artdeco-pages/market-tabs/MarketKLineTab.vue | 作为现有页新模块嵌入 | 提升功能密度与一致性 |
| artdeco-pages/components/DupontAnalysis.vue | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 作为现有页新模块嵌入 | 补齐分析链路 |
| artdeco-pages/components/ArtDecoPerformanceOverview.vue | artdeco-pages/system-tabs/ArtDecoSystemSettings.vue | 作为现有页新模块嵌入 | 提升功能密度与一致性 |
| artdeco-pages/components/AnomalyAlerts.vue | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 作为现有页新模块嵌入 | 增强风险可视化与告警 |
| artdeco-pages/components/FinancialMetrics.vue | artdeco-pages/market-tabs/MarketKLineTab.vue | 作为现有页新模块嵌入 | 提升功能密度与一致性 |
| artdeco-pages/components/PanoramaIndices.vue | artdeco-pages/market-tabs/MarketKLineTab.vue | 作为现有页新模块嵌入 | 提升功能密度与一致性 |
| artdeco-pages/components/AnomalyPatterns.vue | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 作为现有页新模块嵌入 | 提升功能密度与一致性 |
| artdeco-pages/strategy-tabs/components/BacktestHeader.vue | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | 作为现有页新模块嵌入 | 提升功能密度与一致性 |
| artdeco-pages/components/ArtDecoAttributionControls.vue | artdeco-pages/ArtDecoDashboard.vue | 作为现有页新模块嵌入 | 提升功能密度与一致性 |
| artdeco-pages/components/MarketPlaceholder.vue | artdeco-pages/market-tabs/MarketKLineTab.vue | 作为现有页新模块嵌入 | 提升功能密度与一致性 |

### 3.2 逻辑复用机会（应抽象为 composable）

| 可复用逻辑 | 来源 | 建议 Composable | 使用场景 |
|---|---|---|---|
| 策略生命周期控制（启动/暂停/恢复/停止） | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | `useStrategyLifecycleActions` | 策略管理/信号/回测 |
| 分页+筛选+搜索（表格通用） | trade-management/components/*.vue | `usePagedFilterTable` | 交易、持仓、历史、风险列表 |
| 告警规则 CRUD 与状态切换 | monitoring/AlertRulesManagement.vue | `useAlertRuleManagement` | 风险管理中心/系统监控 |
| 批量分析结果聚合与评分 | advanced-analysis/BatchAnalysisView.vue | `useBatchAnalysisAggregation` | 数据分析/策略筛选 |
| 监控面板指标卡聚合 | EnhancedRiskMonitor.vue, system/PerformanceMonitor.vue | `useMonitoringKpi` | 风险概览/系统健康 |

### 3.3 功能补充缺口（对现有 35 页）

| 现有已接入页 | 缺口 | 候选来源页 | 建议 |
|---|---|---|---|
| artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 告警规则管理入口弱 | monitoring/AlertRulesManagement.vue | 新增“规则管理”子标签 |
| artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue | 回测工作台联动不足 | artdeco-pages/strategy-tabs/components/BacktestWorkbenchTabs.vue | 增加工作台子模块 |
| TradingDashboard.vue | 交易统计与归因不足 | trade-management/components/StatisticsTab.vue, artdeco-pages/components/ArtDecoAttributionAnalysis.vue | 新增“统计/归因”区域 |
| artdeco-pages/ArtDecoDataAnalysis.vue | 批量分析结果展示弱 | advanced-analysis/BatchAnalysisView.vue | 增加批量分析结果面板 |
| artdeco-pages/system-tabs/SystemHealthTab.vue | 性能诊断颗粒度不足 | system/PerformanceMonitor.vue | 增加性能诊断标签 |

## 4. 整合方案（按优先级）

### 4.1 P0 高优先级（建议立即执行）

| # | 目标页面（已接入） | 源页面（未接入） | 功能描述 | 整合方式 | 复杂度 | 工作量 | 风险 |
|---:|---|---|---|---|---|---|---|
| 1 | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | trade-management/components/PortfolioOverview.vue | 监控告警、交易操作 | 作为现有页新模块嵌入 | 简单 | 0.5-1d / 80-180 LOC | 低风险，主要是接口对齐与样式一致性 |
| 2 | artdeco-pages/market-tabs/MarketKLineTab.vue | artdeco-pages/components/AnalysisIndicators.vue | 配置/输入、分析计算 | 作为现有页新模块嵌入 | 简单 | 0.5-1d / 80-180 LOC | 低风险，主要是接口对齐与样式一致性 |
| 3 | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | artdeco-pages/components/ArtDecoSignalMonitoringOverview.vue | 监控告警、分析计算 | 作为现有页新模块嵌入 | 简单 | 0.5-1d / 80-180 LOC | 低风险，主要是接口对齐与样式一致性 |
| 4 | artdeco-pages/market-tabs/MarketKLineTab.vue | artdeco-pages/components/MarketFundFlow.vue | 交易操作 | 作为现有页新模块嵌入 | 简单 | 0.5-1d / 80-180 LOC | 低风险，主要是接口对齐与样式一致性 |
| 5 | artdeco-pages/market-tabs/MarketKLineTab.vue | artdeco-pages/components/ArtDecoTradingSignalsControls.vue | 分析计算、交易操作 | 作为现有页新模块嵌入 | 简单 | 0.5-1d / 80-180 LOC | 低风险，主要是接口对齐与样式一致性 |
| 6 | artdeco-pages/ArtDecoDataAnalysis.vue | artdeco-pages/components/AnalysisScreener.vue | 配置/输入、分析计算 | 作为现有页新模块嵌入 | 简单 | 0.5-1d / 80-180 LOC | 低风险，主要是接口对齐与样式一致性 |
| 7 | artdeco-pages/market-tabs/MarketKLineTab.vue | artdeco-pages/components/MarketConcepts.vue | 交易操作 | 作为现有页新模块嵌入 | 简单 | 0.5-1d / 80-180 LOC | 低风险，主要是接口对齐与样式一致性 |
| 8 | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | artdeco-pages/components/LynchModel.vue | 分析计算、交易操作 | 作为现有页新模块嵌入 | 简单 | 0.5-1d / 80-180 LOC | 低风险，主要是接口对齐与样式一致性 |
| 9 | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | artdeco-pages/components/BuffettModel.vue | 分析计算、交易操作 | 作为现有页新模块嵌入 | 简单 | 0.5-1d / 80-180 LOC | 低风险，主要是接口对齐与样式一致性 |
| 10 | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | artdeco-pages/components/OneilModel.vue | 分析计算、交易操作 | 作为现有页新模块嵌入 | 简单 | 0.5-1d / 80-180 LOC | 低风险，主要是接口对齐与样式一致性 |

### 4.2 P1 中优先级（批次化推进）

| # | 目标页面 | 源页面 | 功能描述 | 整合方式 | 复杂度 | 工作量 | 风险 |
|---:|---|---|---|---|---|---|---|
| 1 | artdeco-pages/market-tabs/MarketKLineTab.vue | artdeco-pages/components/PanoramaCapitalFlow.vue | 交易操作、系统管理 | 作为现有页新模块嵌入 | 简单 | 0.5-1d / 80-180 LOC | 低风险，主要是接口对齐与样式一致性 |
| 2 | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | artdeco-pages/components/DupontAnalysis.vue | 监控告警、分析计算 | 作为现有页新模块嵌入 | 简单 | 0.5-1d / 80-180 LOC | 低风险，主要是接口对齐与样式一致性 |
| 3 | artdeco-pages/system-tabs/ArtDecoSystemSettings.vue | artdeco-pages/components/ArtDecoPerformanceOverview.vue | 系统管理 | 作为现有页新模块嵌入 | 简单 | 0.5-1d / 80-180 LOC | 低风险，主要是接口对齐与样式一致性 |
| 4 | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | artdeco-pages/components/AnomalyAlerts.vue | 监控告警、分析计算 | 作为现有页新模块嵌入 | 简单 | 0.5-1d / 80-180 LOC | 低风险，主要是接口对齐与样式一致性 |
| 5 | artdeco-pages/market-tabs/MarketKLineTab.vue | artdeco-pages/components/FinancialMetrics.vue | 交易操作 | 作为现有页新模块嵌入 | 简单 | 0.5-1d / 80-180 LOC | 低风险，主要是接口对齐与样式一致性 |
| 6 | artdeco-pages/market-tabs/MarketKLineTab.vue | artdeco-pages/components/PanoramaIndices.vue | 交易操作 | 作为现有页新模块嵌入 | 简单 | 0.5-1d / 80-180 LOC | 低风险，主要是接口对齐与样式一致性 |
| 7 | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | artdeco-pages/components/AnomalyPatterns.vue | 分析计算、交易操作 | 作为现有页新模块嵌入 | 简单 | 0.5-1d / 80-180 LOC | 低风险，主要是接口对齐与样式一致性 |
| 8 | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | artdeco-pages/strategy-tabs/components/BacktestHeader.vue | 监控告警、策略能力 | 作为现有页新模块嵌入 | 简单 | 0.5-1d / 80-180 LOC | 低风险，主要是接口对齐与样式一致性 |
| 9 | artdeco-pages/ArtDecoDashboard.vue | artdeco-pages/components/ArtDecoAttributionControls.vue | 配置/输入、分析计算 | 作为现有页新模块嵌入 | 简单 | 0.5-1d / 80-180 LOC | 低风险，主要是接口对齐与样式一致性 |
| 10 | artdeco-pages/market-tabs/MarketKLineTab.vue | artdeco-pages/components/MarketPlaceholder.vue | 通用页面容器 | 作为现有页新模块嵌入 | 简单 | 0.5-1d / 80-180 LOC | 低风险，主要是接口对齐与样式一致性 |

### 4.3 P2 技术债批（不直接暴露菜单）

- `demo/`、`examples/`、`converted.archive/` 页面统一进入“能力提取池”，只提炼组件/逻辑，不直接接路由。
- 对重复 stem 页面先做主从判定（优先已接入 ArtDeco 路径），再做代码合并。
- 大文件（>500 行）先拆分为主视图 + 子组件 + composable，再评估接入。

### 4.4 单项方案模板（执行步骤）

1. 在目标已接入页面新增子标签或折叠模块入口（不新增一级菜单）。
2. 抽取源页面可复用组件到 `src/components/...` 或 `artdeco-pages/components/...`。
3. 抽取数据与状态逻辑到 composable，统一错误处理与 loading。
4. 接入现有 API 客户端层（`src/api/*`），避免页面直接请求。
5. 增加最小单元测试/集成测试与路由冒烟测试。
6. 在风险页与系统页补充监控指标，避免“功能可用但不可观察”。

## 5. 组件提取建议

| 建议组件名 | 来源页面 | 功能描述 | 推荐落位 | 使用场景 |
|---|---|---|---|---|
| StrategyActionToolbar | trade-management/components/TradeDialog.vue + ArtDecoStrategyManagement.vue | 策略/交易统一操作条（启动、暂停、回测、跳转） | `src/components/strategy/` | 策略仓库、信号、回测 |
| AnalysisResultCardGroup | advanced-analysis/BatchAnalysisView.vue + artdeco-pages/components/AnalysisResults.vue | 批量分析结果卡片组 | `src/components/analysis/` | 数据分析、策略评估 |
| RiskAlertRuleTable | monitoring/AlertRulesManagement.vue | 告警规则表格 + 启停 | `src/components/risk/` | 风险中心、系统监控 |
| TradeStatisticsPanel | trade-management/components/StatisticsTab.vue | 交易 KPI/胜率/盈亏统计面板 | `src/components/trade/` | 交易操作、历史对账 |
| AttributionPanel | artdeco-pages/components/ArtDecoAttributionAnalysis.vue | 收益归因面板 | `src/components/analysis/` | 策略回顾、交易复盘 |
| SignalMonitoringMetrics | artdeco-pages/components/ArtDecoSignalMonitoringMetrics.vue | 信号监控 KPI 组件 | `src/components/strategy/` | 信号雷达、策略信号 |

## 6. Composable 提取建议

| Composable 名称 | 来源能力 | 功能描述 | 主要输入/输出 | 适用页面 |
|---|---|---|---|---|
| useStrategyLifecycleActions | 策略启停/重试 | 封装 start/pause/resume/stop + 错误重试 | in: strategyId/action; out: running/error/retry | 策略管理、信号 |
| useUnifiedTableState | 分页/筛选/排序 | 统一表格状态、分页、关键字过滤 | in: rows/pageSize; out: pagedRows/query/actions | 交易、风险、市场列表 |
| useBatchAnalysisAggregation | 批量分析聚合 | 聚合多模型结果、平均分、关键指标提取 | in: resultMap; out: summary/metrics | 数据分析、策略优化 |
| useAlertRulesCrud | 告警规则管理 | 规则列表、增删改、启停、校验 | in: apiClient; out: rules/actions/state | 风险告警、系统监控 |
| useMonitoringKpi | 监控指标标准化 | 将监控数据映射为统一 KPI 卡片结构 | in: rawMetrics; out: cards/trends | 风险概览、系统健康 |
| useCrossTabNavigation | 跨标签跳转上下文 | 策略-回测-信号跨页参数传递与恢复 | in: route context; out: buildRoute/restoreState | 策略域全链路 |

## 7. 技术债清理建议

### 7.1 重复代码消除

- 重名/重复 stem 组：13 组（例如 BacktestAnalysis、OpenStockDemo、RiskOverviewTab 等）。
- 处理策略：保留“已接入 + 健康 + ArtDeco 主路径”版本，其余迁移后归档。

### 7.2 依赖与层次优化

- 禁止页面层直接引入散乱 API 调用，统一走 `src/api/services/*` 与 adapter。
- 将 demo 专用依赖与样式与生产页面解耦，避免 bundle 膨胀。

### 7.3 性能与可维护性

- 对超大页面（>500 行）执行拆分（视图壳 + 子组件 + composable）。
- 高频列表页统一虚拟滚动/分页策略，减少渲染压力。
- 图表组件统一 loading/error 空态规范，避免“白屏图表”。

## 8. 附录：217 个未接入页面完整功能清单

| 序号 | 页面 | 功能域 | 主功能类型 | 复用度 | 健康度 | 推荐整合目标 | 复杂度 |
|---:|---|---|---|---|---|---|---|
| 1 | AdvancedAnalysis.vue | 数据分析 | 分析工具 | 中 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 2 | Analysis.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 3 | ArtDecoTest.vue | 综合/跨域 | 交易工具 | 低 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 中等 |
| 4 | BacktestAnalysis.vue | 数据分析 | 表单和输入 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 5 | BacktestWizard.vue | 策略管理 | 表单和输入 | 低 | clean | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | 中等 |
| 6 | Dashboard.vue | 综合/跨域 | 数据表格 | 中 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 7 | DataVisualizationShowcase.vue | 综合/跨域 | 数据可视化 | 中 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 8 | EnhancedDashboard.vue | 综合/跨域 | 数据表格 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 9 | EnhancedRiskMonitor.vue | 风险管理 | 监控和告警 | 中 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 10 | FreqtradeDemo.vue | 交易管理 | 交易工具 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 中等 |
| 11 | IndicatorLibrary.vue | 数据分析 | 表单和输入 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 12 | IndustryConceptAnalysis.vue | 市场行情 | 表单和输入 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 13 | KLineDemo.vue | 市场行情 | 数据可视化 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 14 | Market.vue | 市场行情 | 数据表格 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 15 | MarketData.vue | 市场行情 | 交易工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 16 | MarketDataDemo.vue | 市场行情 | 监控和告警 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 17 | MinimalTest.vue | 综合/跨域 | 系统工具 | 低 | clean | artdeco-pages/ArtDecoDashboard.vue | 简单 |
| 18 | OpenStockDemo.vue | 综合/跨域 | 数据可视化 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 19 | PageTitleDemo.vue | 综合/跨域 | 表单和输入 | 低 | clean | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | 复杂 |
| 20 | Phase4Dashboard.vue | 综合/跨域 | 数据表格 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 21 | PortfolioManagement.vue | 交易管理 | 数据表格 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 复杂 |
| 22 | PyprofilingDemo.vue | 综合/跨域 | 表单和输入 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 23 | RealTimeMonitor.vue | 系统设置 | 监控和告警 | 中 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 复杂 |
| 24 | RiskMonitor.vue | 风险管理 | 监控和告警 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 25 | Settings.vue | 系统设置 | 表单和输入 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 中等 |
| 26 | SkeletonUsage.vue | 综合/跨域 | 交易工具 | 低 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 简单 |
| 27 | SmartDataSourceTest.vue | 综合/跨域 | 表单和输入 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 28 | StockAnalysisDemo.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 29 | StockDetail.vue | 综合/跨域 | 数据可视化 | 低 | error | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 30 | Stocks.vue | 综合/跨域 | 表单和输入 | 低 | warning | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 31 | StrategyManagement.vue | 策略管理 | 表单和输入 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 复杂 |
| 32 | TaskManagement.vue | 综合/跨域 | 表单和输入 | 中 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 复杂 |
| 33 | TdxMarket.vue | 市场行情 | 表单和输入 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 34 | TdxpyDemo.vue | 综合/跨域 | 监控和告警 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 35 | TechnicalAnalysis.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 36 | Test.vue | 综合/跨域 | 交易工具 | 低 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 简单 |
| 37 | TestPage.vue | 综合/跨域 | 交易工具 | 低 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 简单 |
| 38 | TradeManagement.vue | 交易管理 | 交易工具 | 中 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 中等 |
| 39 | TradingDecisionCenter.vue | 交易管理 | 交易工具 | 中 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 40 | Wencai.vue | 综合/跨域 | 监控和告警 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 41 | advanced-analysis/AnomalyTrackingView.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/ArtDecoDataAnalysis.vue | 简单 |
| 42 | advanced-analysis/BatchAnalysisView.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 简单 |
| 43 | advanced-analysis/CapitalFlowView.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 简单 |
| 44 | advanced-analysis/ChipDistributionView.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 简单 |
| 45 | advanced-analysis/DecisionModelsView.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 简单 |
| 46 | advanced-analysis/FinancialValuationView.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/ArtDecoDataAnalysis.vue | 简单 |
| 47 | advanced-analysis/FundamentalAnalysisView.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 48 | advanced-analysis/MarketPanoramaView.vue | 市场行情 | 分析工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 简单 |
| 49 | advanced-analysis/RadarAnalysisView.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 50 | advanced-analysis/SentimentAnalysisView.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/ArtDecoDataAnalysis.vue | 简单 |
| 51 | advanced-analysis/TechnicalAnalysisView.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 简单 |
| 52 | advanced-analysis/TimeSeriesView.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/ArtDecoDataAnalysis.vue | 简单 |
| 53 | advanced-analysis/TradingSignalsView.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | 简单 |
| 54 | artdeco-pages/ArtDecoMarketData.vue | 市场行情 | 表单和输入 | 中 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 55 | artdeco-pages/ArtDecoMarketQuotes.vue | 市场行情 | 表单和输入 | 低 | error | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 56 | artdeco-pages/ArtDecoSettings.vue | 系统设置 | 系统工具 | 低 | clean | artdeco-pages/system-tabs/ArtDecoSystemSettings.vue | 中等 |
| 57 | artdeco-pages/ArtDecoStockManagement.vue | 综合/跨域 | 表单和输入 | 低 | error | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 中等 |
| 58 | artdeco-pages/ArtDecoTechnicalAnalysis.vue | 数据分析 | 分析工具 | 低 | error | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 59 | artdeco-pages/ArtDecoTradingCenter.vue | 交易管理 | 监控和告警 | 中 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 60 | artdeco-pages/ArtDecoTradingManagement.vue | 交易管理 | 交易工具 | 低 | error | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 61 | artdeco-pages/_templates/ArtDecoPageTemplate.vue | 综合/跨域 | 表单和输入 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 中等 |
| 62 | artdeco-pages/_templates/ExampleRiskManagement.vue | 风险管理 | 监控和告警 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 63 | artdeco-pages/analysis-tabs/BacktestAnalysis.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | 中等 |
| 64 | artdeco-pages/components/AnalysisIndicators.vue | 数据分析 | 分析工具 | 高 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 简单 |
| 65 | artdeco-pages/components/AnalysisResults.vue | 数据分析 | 分析工具 | 高 | clean | artdeco-pages/ArtDecoDataAnalysis.vue | 简单 |
| 66 | artdeco-pages/components/AnalysisScreener.vue | 数据分析 | 表单和输入 | 高 | clean | artdeco-pages/ArtDecoDataAnalysis.vue | 简单 |
| 67 | artdeco-pages/components/AnomalyAlerts.vue | 风险管理 | 监控和告警 | 高 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 简单 |
| 68 | artdeco-pages/components/AnomalyPatterns.vue | 综合/跨域 | 分析工具 | 高 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 简单 |
| 69 | artdeco-pages/components/ArtDecoAttributionAnalysis.vue | 数据分析 | 分析工具 | 高 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 70 | artdeco-pages/components/ArtDecoAttributionControls.vue | 综合/跨域 | 表单和输入 | 高 | clean | artdeco-pages/ArtDecoDashboard.vue | 简单 |
| 71 | artdeco-pages/components/ArtDecoPerformanceOverview.vue | 综合/跨域 | 系统工具 | 高 | clean | artdeco-pages/system-tabs/ArtDecoSystemSettings.vue | 简单 |
| 72 | artdeco-pages/components/ArtDecoSignalHistory.vue | 策略管理 | 交易工具 | 高 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 73 | artdeco-pages/components/ArtDecoSignalMonitoringMetrics.vue | 策略管理 | 交易工具 | 高 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 中等 |
| 74 | artdeco-pages/components/ArtDecoSignalMonitoringOverview.vue | 策略管理 | 交易工具 | 高 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 简单 |
| 75 | artdeco-pages/components/ArtDecoTradingHistoryControls.vue | 交易管理 | 交易工具 | 高 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 中等 |
| 76 | artdeco-pages/components/ArtDecoTradingSignalsControls.vue | 策略管理 | 交易工具 | 高 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 简单 |
| 77 | artdeco-pages/components/BuffettModel.vue | 综合/跨域 | 分析工具 | 高 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 简单 |
| 78 | artdeco-pages/components/DupontAnalysis.vue | 数据分析 | 分析工具 | 高 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 简单 |
| 79 | artdeco-pages/components/FinancialMetrics.vue | 综合/跨域 | 交易工具 | 高 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 简单 |
| 80 | artdeco-pages/components/LynchModel.vue | 综合/跨域 | 分析工具 | 高 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 简单 |
| 81 | artdeco-pages/components/MarketConcepts.vue | 市场行情 | 交易工具 | 高 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 简单 |
| 82 | artdeco-pages/components/MarketFundFlow.vue | 市场行情 | 交易工具 | 高 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 简单 |
| 83 | artdeco-pages/components/MarketPlaceholder.vue | 市场行情 | 数据可视化 | 高 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 简单 |
| 84 | artdeco-pages/components/OneilModel.vue | 综合/跨域 | 分析工具 | 高 | clean | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | 简单 |
| 85 | artdeco-pages/components/PanoramaCapitalFlow.vue | 系统设置 | 系统工具 | 高 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 简单 |
| 86 | artdeco-pages/components/PanoramaIndices.vue | 综合/跨域 | 交易工具 | 高 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 简单 |
| 87 | artdeco-pages/market-data-tabs/ArtDecoMarketAnalysis.vue | 市场行情 | 分析工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 简单 |
| 88 | artdeco-pages/market-data-tabs/ArtDecoMarketOverview.vue | 市场行情 | 交易工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 简单 |
| 89 | artdeco-pages/market-data-tabs/ArtDecoRealtimeMonitor.vue | 市场行情 | 监控和告警 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 90 | artdeco-pages/market-data-tabs/AuctionAnalysis.vue | 市场行情 | 分析工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 简单 |
| 91 | artdeco-pages/market-data-tabs/ConceptAnalysis.vue | 市场行情 | 表单和输入 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 92 | artdeco-pages/market-data-tabs/DataQualityPanel.vue | 市场行情 | 监控和告警 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 93 | artdeco-pages/market-data-tabs/ETFAnalysis.vue | 市场行情 | 分析工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 94 | artdeco-pages/market-data-tabs/FundFlow.vue | 市场行情 | 表单和输入 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 95 | artdeco-pages/market-tabs/MarketETFTab.vue | 市场行情 | 交易工具 | 低 | error | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 96 | artdeco-pages/risk-tabs/ArtDecoRiskMonitor.vue | 风险管理 | 监控和告警 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 复杂 |
| 97 | artdeco-pages/settings/AppearanceSettings.vue | 系统设置 | 表单和输入 | 低 | clean | artdeco-pages/system-tabs/ArtDecoSystemSettings.vue | 中等 |
| 98 | artdeco-pages/settings/DataSourceSettings.vue | 系统设置 | 系统工具 | 低 | clean | artdeco-pages/system-tabs/ArtDecoSystemSettings.vue | 中等 |
| 99 | artdeco-pages/settings/NotificationSettings.vue | 系统设置 | 系统工具 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 中等 |
| 100 | artdeco-pages/settings/SecuritySettings.vue | 系统设置 | 系统工具 | 低 | clean | artdeco-pages/system-tabs/ArtDecoSystemSettings.vue | 简单 |
| 101 | artdeco-pages/settings/SystemInfoSettings.vue | 系统设置 | 系统工具 | 低 | clean | artdeco-pages/system-tabs/ArtDecoSystemSettings.vue | 中等 |
| 102 | artdeco-pages/strategy-tabs/components/BacktestHeader.vue | 策略管理 | 策略工具 | 高 | clean | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | 简单 |
| 103 | artdeco-pages/strategy-tabs/components/BacktestKpiGrid.vue | 策略管理 | 策略工具 | 高 | clean | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | 简单 |
| 104 | artdeco-pages/strategy-tabs/components/BacktestWorkbenchTabs.vue | 策略管理 | 策略工具 | 高 | clean | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | 简单 |
| 105 | artdeco-pages/technical-tabs/TechnicalScannerTab.vue | 综合/跨域 | 分析工具 | 低 | error | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 106 | artdeco-pages/trading-tabs/ArtDecoHistoryView.vue | 交易管理 | 交易工具 | 低 | clean | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | 复杂 |
| 107 | artdeco-pages/trading-tabs/ArtDecoPerformanceAnalysis.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 简单 |
| 108 | artdeco-pages/trading-tabs/ArtDecoPositionMonitor.vue | 交易管理 | 交易工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 109 | artdeco-pages/trading-tabs/ArtDecoTradingSignals.vue | 策略管理 | 表单和输入 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 110 | artdeco-pages/trading-tabs/ArtDecoTradingStats.vue | 交易管理 | 交易工具 | 低 | clean | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | 简单 |
| 111 | components/RiskOverviewTab.vue | 风险管理 | 监控和告警 | 高 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 112 | components/StopLossMonitoringTab.vue | 风险管理 | 表单和输入 | 高 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 中等 |
| 113 | converted.archive/backtest-management.vue | 策略管理 | 策略工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 114 | converted.archive/dashboard.vue | 综合/跨域 | 监控和告警 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 115 | converted.archive/data-analysis.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 简单 |
| 116 | converted.archive/market-data.vue | 市场行情 | 数据表格 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 117 | converted.archive/market-quotes.vue | 市场行情 | 监控和告警 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 118 | converted.archive/risk-management.vue | 风险管理 | 监控和告警 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 简单 |
| 119 | converted.archive/setting.vue | 综合/跨域 | 表单和输入 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 120 | converted.archive/stock-management.vue | 综合/跨域 | 交易工具 | 低 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 简单 |
| 121 | converted.archive/trading-management.vue | 交易管理 | 交易工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 122 | demo/OpenStockDemo.vue | 综合/跨域 | 数据可视化 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 123 | demo/Phase4Dashboard.vue | 综合/跨域 | 数据表格 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 124 | demo/PyprofilingDemo.vue | 综合/跨域 | 交易工具 | 低 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 中等 |
| 125 | demo/StockAnalysisDemo.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | 中等 |
| 126 | demo/Wencai.vue | 综合/跨域 | 表单和输入 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 127 | demo/openstock/components/FeatureStatus.vue | 综合/跨域 | 数据可视化 | 中 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 128 | demo/openstock/components/HeatmapChart.vue | 综合/跨域 | 数据可视化 | 中 | error | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 129 | demo/openstock/components/KlineChart.vue | 市场行情 | 数据可视化 | 中 | error | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 130 | demo/openstock/components/StockNews.vue | 综合/跨域 | 表单和输入 | 中 | error | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 131 | demo/openstock/components/StockQuote.vue | 市场行情 | 表单和输入 | 中 | error | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 132 | demo/openstock/components/StockSearch.vue | 综合/跨域 | 表单和输入 | 中 | error | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 133 | demo/openstock/components/WatchlistManagement.vue | 综合/跨域 | 数据表格 | 高 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 134 | demo/pyprofiling/components/API.vue | 系统设置 | 监控和告警 | 高 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 中等 |
| 135 | demo/pyprofiling/components/Data.vue | 综合/跨域 | 数据表格 | 中 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 136 | demo/pyprofiling/components/Features.vue | 综合/跨域 | 表单和输入 | 中 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 137 | demo/pyprofiling/components/Overview.vue | 综合/跨域 | 监控和告警 | 高 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 复杂 |
| 138 | demo/pyprofiling/components/Prediction.vue | 综合/跨域 | 监控和告警 | 中 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 中等 |
| 139 | demo/pyprofiling/components/Profiling.vue | 综合/跨域 | 数据表格 | 高 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 140 | demo/pyprofiling/components/Tech.vue | 综合/跨域 | 数据表格 | 中 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 141 | demo/stock-analysis/components/Backtest.vue | 数据分析 | 数据表格 | 中 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 142 | demo/stock-analysis/components/DataParsing.vue | 数据分析 | 表单和输入 | 中 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 143 | demo/stock-analysis/components/Overview.vue | 数据分析 | 分析工具 | 高 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 复杂 |
| 144 | demo/stock-analysis/components/Realtime.vue | 数据分析 | 分析工具 | 中 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 145 | demo/stock-analysis/components/Status.vue | 数据分析 | 分析工具 | 高 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 146 | demo/stock-analysis/components/Strategy.vue | 数据分析 | 分析工具 | 中 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 147 | errors/Forbidden.vue | 综合/跨域 | 交易工具 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 复杂 |
| 148 | errors/NetworkError.vue | 综合/跨域 | 监控和告警 | 低 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 复杂 |
| 149 | errors/ServiceUnavailable.vue | 综合/跨域 | 系统工具 | 低 | clean | artdeco-pages/system-tabs/ArtDecoSystemSettings.vue | 中等 |
| 150 | examples/PageConfigExample.vue | 综合/跨域 | 监控和告警 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 151 | examples/TradingDashboard.migrated.vue | 交易管理 | 交易工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 152 | examples/WebSocketConfigExample.vue | 综合/跨域 | 表单和输入 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 复杂 |
| 153 | freqtrade-demo/FreqBacktestTab.vue | 策略管理 | 策略工具 | 低 | error | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 简单 |
| 154 | freqtrade-demo/FreqConfigTab.vue | 交易管理 | 交易工具 | 低 | error | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 中等 |
| 155 | freqtrade-demo/FreqOverviewTab.vue | 交易管理 | 交易工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 简单 |
| 156 | freqtrade-demo/FreqStatusTab.vue | 交易管理 | 交易工具 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 简单 |
| 157 | freqtrade-demo/FreqStrategyTab.vue | 策略管理 | 策略工具 | 低 | error | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 158 | freqtrade-demo/FreqWebuiTab.vue | 交易管理 | 交易工具 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 简单 |
| 159 | market/Auction.vue | 市场行情 | 监控和告警 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 160 | market/CapitalFlow.vue | 市场行情 | 分析工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 161 | market/Concepts.vue | 市场行情 | 表单和输入 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 162 | market/Etf.vue | 市场行情 | 表单和输入 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 163 | market/MarketDataView.vue | 市场行情 | 数据表格 | 中 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 164 | market/Realtime.vue | 市场行情 | 表单和输入 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 165 | market/Tdx.vue | 市场行情 | 表单和输入 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 166 | market/Technical.vue | 市场行情 | 数据可视化 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 167 | monitor.vue | 系统设置 | 监控和告警 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 中等 |
| 168 | monitoring/AlertRulesManagement.vue | 风险管理 | 表单和输入 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 中等 |
| 169 | monitoring/MonitoringDashboard.vue | 系统设置 | 监控和告警 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 复杂 |
| 170 | monitoring/RiskDashboard.vue | 风险管理 | 监控和告警 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 171 | monitoring/WatchlistManagement.vue | 系统设置 | 数据表格 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 复杂 |
| 172 | risk/Alerts.vue | 风险管理 | 监控和告警 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 简单 |
| 173 | risk/Overview.vue | 风险管理 | 监控和告警 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 简单 |
| 174 | risk/Portfolio.vue | 交易管理 | 监控和告警 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 简单 |
| 175 | risk/Positions.vue | 交易管理 | 交易工具 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 简单 |
| 176 | settings/General.vue | 系统设置 | 系统工具 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 简单 |
| 177 | settings/Notifications.vue | 系统设置 | 系统工具 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 简单 |
| 178 | settings/Security.vue | 系统设置 | 系统工具 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 简单 |
| 179 | settings/Theme.vue | 系统设置 | 系统工具 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 简单 |
| 180 | stock-analysis/StockBacktestTab.vue | 数据分析 | 数据表格 | 低 | clean | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | 中等 |
| 181 | stock-analysis/StockDataTab.vue | 数据分析 | 监控和告警 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 182 | stock-analysis/StockOverviewTab.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 183 | stock-analysis/StockRealtimeTab.vue | 数据分析 | 监控和告警 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 184 | stock-analysis/StockStatusTab.vue | 数据分析 | 分析工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 185 | stock-analysis/StockStrategyTab.vue | 数据分析 | 表单和输入 | 低 | warning | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | 中等 |
| 186 | stocks/Activity.vue | 综合/跨域 | 数据表格 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 中等 |
| 187 | stocks/Concept.vue | 市场行情 | 数据表格 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 188 | stocks/Industry.vue | 市场行情 | 数据表格 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 189 | stocks/Portfolio.vue | 交易管理 | 交易工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 190 | stocks/Watchlist.vue | 综合/跨域 | 数据表格 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 191 | strategy/BatchScan.vue | 策略管理 | 表单和输入 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 192 | strategy/ResultsQuery.vue | 策略管理 | 表单和输入 | 低 | clean | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | 复杂 |
| 193 | strategy/SingleRun.vue | 策略管理 | 表单和输入 | 低 | clean | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | 中等 |
| 194 | strategy/StatsAnalysis.vue | 数据分析 | 表单和输入 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 复杂 |
| 195 | strategy/StrategyList.vue | 策略管理 | 表单和输入 | 低 | clean | artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue | 中等 |
| 196 | system/Architecture.vue | 系统设置 | 系统工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 197 | system/DatabaseMonitor.vue | 系统设置 | 系统工具 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 中等 |
| 198 | system/PerformanceMonitor.vue | 系统设置 | 系统工具 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 复杂 |
| 199 | tdxpy-demo/TdxApiTab.vue | 系统设置 | 系统工具 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 200 | tdxpy-demo/TdxExportTab.vue | 综合/跨域 | 系统工具 | 低 | error | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 201 | tdxpy-demo/TdxInstallTab.vue | 综合/跨域 | 系统工具 | 低 | error | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 202 | tdxpy-demo/TdxOverviewTab.vue | 综合/跨域 | 表单和输入 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 简单 |
| 203 | tdxpy-demo/TdxStatusTab.vue | 综合/跨域 | 监控和告警 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 简单 |
| 204 | technical/TechnicalAnalysis.vue | 数据分析 | 表单和输入 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 205 | trade-management/components/PortfolioOverview.vue | 交易管理 | 交易工具 | 高 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 简单 |
| 206 | trade-management/components/PositionsTab.vue | 交易管理 | 交易工具 | 高 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 207 | trade-management/components/StatisticsTab.vue | 交易管理 | 交易工具 | 高 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 中等 |
| 208 | trade-management/components/TradeDialog.vue | 交易管理 | 交易工具 | 高 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 复杂 |
| 209 | trade-management/components/TradeHistoryTab.vue | 交易管理 | 表单和输入 | 高 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 中等 |
| 210 | trading-decision/DecisionHeader.vue | 交易管理 | 交易工具 | 低 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 中等 |
| 211 | trading-decision/DecisionOrders.vue | 交易管理 | 数据表格 | 低 | clean | artdeco-pages/market-tabs/MarketKLineTab.vue | 中等 |
| 212 | trading-decision/DecisionPortfolio.vue | 交易管理 | 交易工具 | 低 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 中等 |
| 213 | trading-decision/DecisionPositions.vue | 交易管理 | 交易工具 | 低 | clean | artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | 简单 |
| 214 | trading/Execution.vue | 交易管理 | 交易工具 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 简单 |
| 215 | trading/History.vue | 交易管理 | 交易工具 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 简单 |
| 216 | trading/Orders.vue | 交易管理 | 交易工具 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 简单 |
| 217 | trading/Positions.vue | 交易管理 | 交易工具 | 低 | clean | artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue | 简单 |
