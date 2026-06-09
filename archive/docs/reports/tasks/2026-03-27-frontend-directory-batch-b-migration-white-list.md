# 2026-03-27 Frontend Directory Batch B：迁移白名单

> **历史文档说明**:
> 本文件是某阶段的历史文档、过程记录或专题材料，不是当前基线、当前系统总览或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内描述、背景、结论和上下文如未重新复核，应视为历史快照，不得直接当作当前事实。


> 目标：从 34 个活跃组件中筛出“下一批最安全可迁移候选”，供 Batch C 使用。

## 白名单筛选规则

满足以下条件的页面才进入白名单：

1. 单路由使用
2. 不被多路由复用
3. 不在冻结列表
4. 不在根层关键入口
5. 不属于当前明显高风险交易/策略核心链路

## 白名单页面

### Market / Data 候选

1. [MarketRealtimeTab.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue)
2. [MarketKLineTab.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-tabs/MarketKLineTab.vue)
3. [DragonTigerAnalysis.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue)
4. [ArtDecoIndustryAnalysis.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue)
5. [MarketConceptTab.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-tabs/MarketConceptTab.vue)
6. [FundFlowAnalysis.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-data-tabs/FundFlowAnalysis.vue)
7. [ArtDecoDataAnalysis.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/ArtDecoDataAnalysis.vue)

### Watchlist 候选

8. [WatchlistManager.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue)

### Risk 候选

9. [RiskOverviewTab.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/risk-tabs/RiskOverviewTab.vue)
10. [StopLossMonitorTab.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue)
11. [ArtDecoRiskAlerts.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue)
12. [ArtDecoAnnouncementMonitor.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue)

### System 候选

13. [ArtDecoSystemSettings.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue)
14. [SystemHealthTab.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/system-tabs/SystemHealthTab.vue)
15. [ArtDecoDataManagement.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue)

### Detail 候选

16. [KLineAnalysis.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue)

## 不进入白名单的典型页面

### 因冻结而排除

- `Login.vue`
- `NotFound.vue`
- `TradingDashboard.vue`
- `Screener.vue`
- `AnnouncementMonitor.vue`
- `BacktestGPU.vue`
- `ArtDecoDashboard.vue`
- `ArtDecoMonitoringDashboard.vue`

### 因复用 / 高复杂度而排除

- `StrategySignalsTab.vue`
- `ArtDecoTradingPositions.vue`
- `PortfolioOverviewTab.vue`
- `ArtDecoStrategyManagement.vue`
- `StrategyParametersTab.vue`
- `ArtDecoBacktestAnalysis.vue`
- `ArtDecoStrategyOptimization.vue`
- `ArtDecoSignalsView.vue`
- `ArtDecoTradingHistory.vue`
- `ArtDecoRiskManagement.vue`

## 白名单使用规则

白名单只表示：

- 这些页面可以进入下一批“迁移可行性”讨论

白名单不表示：

- 这些页面可以直接移动
- 可以跳过 import 依赖盘点
- 可以跳过路由验证

## Batch C 建议

若继续执行，建议 Batch C 从白名单中只选一个试点域：

### 推荐优先级

1. `market/data`
2. `risk`
3. `system`

### 不建议首批试点

- `strategy`
- `trade`
- 任意被冻结页面

## 结论

当前白名单共 16 个页面，足以支持下一步小批次试点迁移设计。  
后续 Batch C 不应超出该白名单范围启动目录迁移。
