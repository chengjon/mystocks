# 已删除内容清单 — 2026-03-29 历史清单

> 日期: 2026-03-29
> 状态: 历史材料，仅供回溯，不代表当前主线状态。
> 说明: 该清单记录的是当时工作区中的候选删除项，不能作为当前删除依据。
> 命令查看: `git diff -- web/frontend/src/`

---

## A. 响应式 Media Query 块删除（87 文件，纯删除 0 新增）

**删除内容**: 每个文件中的 `@media (width <= 48rem) { ... }` 整段块
**理由**: 项目仅支持桌面端（最小 1280x720），48rem = 768px 的断点不会触发

### 按删除行数排序

| 删除行 | 文件路径 |
|--------|----------|
| 52 | `views/strategy/styles/StatsAnalysis.scss` |
| 48 | `views/errors/styles/ServiceUnavailable.scss` |
| 48 | `views/errors/Forbidden.vue` |
| 43 | `views/strategy/styles/StrategyList.scss` |
| 42 | `views/errors/NetworkError.vue` |
| 40 | `views/strategy/styles/BacktestGPU.scss` |
| 39 | `views/strategy/styles/SingleRun.scss` |
| 36 | `views/strategy/styles/BatchScan.scss` |
| 27 | `components/monitoring/styles/MonitoringDataTable.css` |
| 27 | `components/chart/styles/HealthRadarChart.css` |
| 27 | `components/artdeco/core/ArtDecoBreadcrumb.vue` |
| 26 | `views/system/styles/Architecture.scss` |
| 25 | `components/Charts/TreeChart.vue` |
| 24 | `views/demo/pyprofiling/components/styles/Prediction.scss` |
| 24 | `components/sse/styles/DashboardMetrics.scss` |
| 23 | `views/system/styles/PerformanceMonitor.css` |
| 23 | `components/monitoring/styles/MonitoringAlertPanel.css` |
| 22 | `views/system/styles/DatabaseMonitor.scss` |
| 22 | `views/monitoring/styles/MonitoringDashboard.scss` |
| 22 | `views/market/Realtime.vue` |
| 22 | `components/market/styles/SmartRecommendation.css` |
| 21 | `views/market/LHB.vue` |
| 21 | `views/demo/pyprofiling/components/Overview.vue` |
| 21 | `views/data/FundFlow.vue` |
| 21 | `views/announcement/styles/AnnouncementMonitor.scss` |
| 20 | `views/artdeco-pages/risk-tabs/RiskOverviewTab.vue` |
| 19 | `components/artdeco/base/ArtDecoDialog.vue` |
| 19 | `components/Charts/SankeyChart.vue` |
| 18 | `views/artdeco-pages/technical-tabs/TechnicalScannerTab.vue` |
| 18 | `views/artdeco-pages/stock-management-tabs/WatchlistManager.vue` |
| 18 | `views/artdeco-pages/market-tabs/MarketETFTab.vue` |
| 18 | `components/artdeco/base/ArtDecoSkipLink.vue` |
| 17 | `components/technical/KLineChart.vue` |
| 16 | `views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue` |
| 16 | `views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue` |
| 16 | `views/artdeco-pages/strategy-tabs/styles/StrategySignalsTab.scss` |
| 16 | `views/artdeco-pages/market-data-tabs/ETFAnalysis.vue` |
| 16 | `views/artdeco-pages/components/AnalysisIndicators.vue` |
| 15 | `views/strategy/styles/ResultsQuery.scss` |
| 15 | `views/demo/pyprofiling/components/API.vue` |
| 15 | `views/artdeco-pages/strategy-tabs/styles/StrategyParametersTab.scss` |
| 15 | `views/artdeco-pages/components/AnalysisScreener.vue` |
| 15 | `views/artdeco-pages/analysis-tabs/KLineAnalysis.vue` |
| 14 | `views/trade-management/components/PositionsTab.vue` |
| 13 | `views/artdeco-pages/components/MarketConcepts.vue` |
| 12 | `views/artdeco-pages/strategy-tabs/styles/ArtDecoStrategyOptimization.scss` |
| 12 | `views/artdeco-pages/strategy-tabs/styles/ArtDecoStrategyManagement.scss` |
| 12 | `views/artdeco-pages/strategy-tabs/components/styles/BacktestWorkbenchTabs.scss` |
| 12 | `views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue` |
| 12 | `views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue` |
| 12 | `views/artdeco-pages/market-data-tabs/DataQualityPanel.vue` |
| 12 | `views/artdeco-pages/components/ArtDecoTradingHistoryControls.vue` |
| 12 | `views/artdeco-pages/_templates/ExampleRiskManagement.vue` |
| 12 | `views/artdeco-pages/ArtDecoRiskManagement.vue` |
| 12 | `components/artdeco/charts/styles/DepthChart.scss` |
| 11 | `views/market/Technical.vue` |
| 11 | `views/demo/pyprofiling/components/Data.vue` |
| 11 | `views/data/Industry.vue` |
| 11 | `views/data/Concepts.vue` |
| 11 | `views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue` |
| 11 | `views/artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue` |
| 11 | `views/artdeco-pages/trading-tabs/ArtDecoSignalsView.vue` |
| 11 | `views/artdeco-pages/system-tabs/SystemHealthTab.vue` |
| 11 | `views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue` |
| 10 | `views/monitoring/styles/AlertRulesManagement.scss` |
| 10 | `views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` |
| 10 | `views/artdeco-pages/market-data-tabs/ConceptAnalysis.vue` |
| 10 | `views/artdeco-pages/analysis-tabs/BacktestAnalysis.vue` |
| 10 | `views/artdeco-pages/components/FinancialMetrics.vue` |
| 10 | `views/artdeco-pages/components/PanoramaIndices.vue` |
| 10 | `views/strategy/styles/StatsAnalysis.scss` |
| 9 | `views/artdeco-pages/components/AnomalyAlerts.vue` |
| 8 | `views/artdeco-pages/components/AnomalyPatterns.vue` |
| 8 | `views/artdeco-pages/components/PanoramaCapitalFlow.vue` |
| 8 | `components/artdeco/trading/ArtDecoTickerList.vue` |
| 7 | `views/artdeco-pages/strategy-tabs/styles/ArtDecoBacktestAnalysis.scss` |
| 7 | `views/artdeco-pages/components/OneilModel.vue` |
| 7 | `views/artdeco-pages/components/BuffettModel.vue` |
| 7 | `views/artdeco-pages/components/ArtDecoTradingSignalsControls.vue` |
| 6 | `views/artdeco-pages/strategy-tabs/components/styles/BacktestKpiGrid.scss` |
| 6 | `views/artdeco-pages/stock-management-tabs/PortfolioMonitor.vue` |
| 6 | `views/artdeco-pages/market-data-tabs/AuctionAnalysis.vue` |
| 6 | `views/artdeco-pages/components/PanoramaCapitalFlow.vue` |
| 6 | `views/artdeco-pages/components/LynchModel.vue` |
| 6 | `views/artdeco-pages/components/ArtDecoAttributionControls.vue` |
| 4 | `views/artdeco-pages/risk-tabs/ArtDecoRiskStatsGrid.vue` |
| 2 | `views/demo/OpenStockDemo.vue`（仅 media query 部分） |
| 1 | `components/Charts/styles/AdvancedHeatmap.scss` |
| 1 | `components/Charts/styles/RelationChart.scss` |

**删除的典型内容示例**:

```scss
// 每个文件中删除的都是这种格式的块：
@media (width <= 48rem) {
  .xxx {
    flex-direction: column;
    // ... 响应式样式规则
  }
}
```

---

## B. Code-Simplifier 修复（已提交，3 文件）

| 文件 | 删除内容 | 替换为 |
|------|----------|--------|
| `KLineChart.vue` | `_measurePerformance` 导入（未使用） | 直接删除 |
| `KLineChart.vue` | `style="margin-right: 4px; cursor: pointer;"` 内联样式 | `.indicator-toggle-icon` CSS class |
| `StockSearchBar.vue` | 冗余 `@media (width <= 48rem)` 重新声明 `width: 100%` | 直接删除（基类已声明） |

---

## C. 非本次会话产生的变更（工作区预存状态）

以下变更在我介入前已存在于工作区，**不是我做的**:

| 文件 | 变更 | 说明 |
|------|------|------|
| `views/demo/styles/Wencai.scss` | +170/-172 | 样式重排/格式化 |
| `views/demo/OpenStockDemo.vue` | +95/-101 | 组件重排 |
| `components/Charts/styles/AdvancedHeatmap.scss` | +1/-1 | 微调 |
| `components/Charts/styles/RelationChart.scss` | +1/-1 | 微调 |
| `components/monitoring/MonitoringStatCard.vue` | +1/-19 | 样式重构 |
| `api/types/*.ts` (9 文件) | 各 +1/-1 | 类型文件微调 |

---

## 总计

| 类别 | 文件数 | 删除行数 |
|------|--------|----------|
| A. 响应式 media query 删除 | 87 | ~1,620 |
| B. Code-simplifier 修复（已提交） | 3 | ~20 |
| C. 预存变更（非本次操作） | 14 | ~180 |

**A 类删除的验证状态**: 构建 `✓ built in 24.07s`，单元测试 33 files / 354 tests 全部通过。
