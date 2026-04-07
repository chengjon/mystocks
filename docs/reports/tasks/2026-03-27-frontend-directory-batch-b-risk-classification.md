# 2026-03-27 Frontend Directory Batch B：风险分级表

> **历史分析说明**:
> 本文件是阶段性分析、审计、评估或复盘材料，不是当前基线、当前实施优先级或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内问题分级、差距判断、风险结论、审阅意见和建议动作如未重新复核，应视为历史分析结果，不得直接当作当前事实。


> 目标：对当前 34 个活跃视图组件做风险分级，为后续迁移提供“先动谁、绝不动谁”的客观依据。
>
> 分级规则采用本轮确认的安全型 Batch B 标准：
>
> - **Level 1：零风险**
>   - 静态或近静态页面
>   - 单路由
>   - 无共享复用
>   - 无明显复杂业务链路
> - **Level 2：低风险**
>   - 独立页面
>   - 单路由
>   - 业务相对简单
>   - 可作为优先迁移候选
> - **Level 3：中风险**
>   - 被多路由复用
>   - 或承载复杂业务链路 / 交易 / 策略 / 回测 / 跨 Tab 上下文
> - **Level 4：高风险**
>   - 登录 / 404 / 首页 Dashboard / 监控页 / Screener / GPU 回测 / 主交易终端
>   - 当前批次绝对不动，最后处理

## 风险分级总表

| 组件 | 当前路径 | 路由数 | 约行数 | 风险等级 | 主要原因 |
|---|---|---:|---:|---|---|
| `ArtDecoDashboard.vue` | `artdeco-pages/ArtDecoDashboard.vue` | 1 | 518 | L4 | 首页 Dashboard，主线核心入口 |
| `Login.vue` | `Login.vue` | 1 | 417 | L4 | 登录入口，认证链路 |
| `NotFound.vue` | `NotFound.vue` | 1 | 226 | L4 | 全局 404 错误页 |
| `TradingDashboard.vue` | `TradingDashboard.vue` | 1 | 349 | L4 | 主交易终端，活跃核心页 |
| `AnnouncementMonitor.vue` | `announcement/AnnouncementMonitor.vue` | 1 | 454 | L4 | 公告/详情监控页，当前不应迁移 |
| `Screener.vue` | `stocks/Screener.vue` | 1 | 374 | L4 | 策略选股核心页，且位于旧目录 |
| `BacktestGPU.vue` | `strategy/BacktestGPU.vue` | 1 | 324 | L4 | GPU 回测关键页 |
| `ArtDecoMonitoringDashboard.vue` | `artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue` | 1 | 370 | L4 | 监控工作台，系统观测核心页 |
| `ArtDecoStrategyManagement.vue` | `artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue` | 1 | 941 | L3 | 策略仓库主链，CRUD/生命周期/跨 Tab 复杂 |
| `StrategyParametersTab.vue` | `artdeco-pages/strategy-tabs/StrategyParametersTab.vue` | 1 | 268 | L3 | 策略参数上下文页，依赖策略链路 |
| `ArtDecoBacktestAnalysis.vue` | `artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue` | 1 | 307 | L3 | 回测执行链路 |
| `ArtDecoStrategyOptimization.vue` | `artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue` | 1 | 463 | L3 | 参数优化 + writeback 链路 |
| `StrategySignalsTab.vue` | `artdeco-pages/strategy-tabs/StrategySignalsTab.vue` | 2 | 189 | L3 | 被 `watchlist` / `strategy` 双路由复用 |
| `ArtDecoTradingPositions.vue` | `artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue` | 2 | 463 | L3 | 被 `trade` / `strategy` 双路由复用 |
| `PortfolioOverviewTab.vue` | `artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` | 2 | 533 | L3 | 被 `trade` / `risk` 双路由复用 |
| `ArtDecoSignalsView.vue` | `artdeco-pages/trading-tabs/ArtDecoSignalsView.vue` | 1 | 464 | L3 | 交易信号视图，业务链复杂 |
| `ArtDecoTradingHistory.vue` | `artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue` | 1 | 451 | L3 | 历史对账，交易数据链 |
| `ArtDecoRiskManagement.vue` | `artdeco-pages/ArtDecoRiskManagement.vue` | 1 | 317 | L3 | 风险管理中心，模板驱动核心页 |
| `DragonTigerAnalysis.vue` | `artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue` | 1 | 345 | L1 | 单路由、功能边界清晰、无复用 |
| `KLineAnalysis.vue` | `artdeco-pages/analysis-tabs/KLineAnalysis.vue` | 1 | 206 | L1 | 单路由详情页，边界清晰 |
| `SystemHealthTab.vue` | `artdeco-pages/system-tabs/SystemHealthTab.vue` | 1 | 317 | L1 | 独立系统页，可单独迁移设计 |
| `MarketRealtimeTab.vue` | `artdeco-pages/market-tabs/MarketRealtimeTab.vue` | 1 | 319 | L2 | 单路由，市场域页面 |
| `MarketKLineTab.vue` | `artdeco-pages/market-tabs/MarketKLineTab.vue` | 1 | 285 | L2 | 单路由，技术分析入口 |
| `ArtDecoIndustryAnalysis.vue` | `artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue` | 1 | 372 | L2 | 单路由，数据域页面 |
| `MarketConceptTab.vue` | `artdeco-pages/market-tabs/MarketConceptTab.vue` | 1 | 271 | L2 | 单路由，数据域页面 |
| `FundFlowAnalysis.vue` | `artdeco-pages/market-data-tabs/FundFlowAnalysis.vue` | 1 | 454 | L2 | 单路由，业务独立但数据较多 |
| `ArtDecoDataAnalysis.vue` | `artdeco-pages/ArtDecoDataAnalysis.vue` | 1 | 347 | L2 | 单路由，数据分析主页面 |
| `WatchlistManager.vue` | `artdeco-pages/stock-management-tabs/WatchlistManager.vue` | 1 | 315 | L2 | 单路由，自选管理页 |
| `RiskOverviewTab.vue` | `artdeco-pages/risk-tabs/RiskOverviewTab.vue` | 1 | 365 | L2 | 单路由，风险概览页 |
| `StopLossMonitorTab.vue` | `artdeco-pages/risk-tabs/StopLossMonitorTab.vue` | 1 | 369 | L2 | 单路由，止损页 |
| `ArtDecoRiskAlerts.vue` | `artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue` | 1 | 340 | L2 | 单路由，告警页 |
| `ArtDecoAnnouncementMonitor.vue` | `artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue` | 1 | 309 | L2 | 单路由，风险新闻页 |
| `ArtDecoSystemSettings.vue` | `artdeco-pages/system-tabs/ArtDecoSystemSettings.vue` | 1 | 299 | L2 | 单路由，系统配置页 |
| `ArtDecoDataManagement.vue` | `artdeco-pages/system-tabs/ArtDecoDataManagement.vue` | 1 | 386 | L2 | 单路由，数据源管理页 |

## 风险分级结论

### Level 4：绝对不动，最后处理

- `ArtDecoDashboard.vue`
- `Login.vue`
- `NotFound.vue`
- `TradingDashboard.vue`
- `AnnouncementMonitor.vue`
- `Screener.vue`
- `BacktestGPU.vue`
- `ArtDecoMonitoringDashboard.vue`

### Level 3：不适合 Batch C 直接迁移

- `ArtDecoStrategyManagement.vue`
- `StrategyParametersTab.vue`
- `ArtDecoBacktestAnalysis.vue`
- `ArtDecoStrategyOptimization.vue`
- `StrategySignalsTab.vue`
- `ArtDecoTradingPositions.vue`
- `PortfolioOverviewTab.vue`
- `ArtDecoSignalsView.vue`
- `ArtDecoTradingHistory.vue`
- `ArtDecoRiskManagement.vue`

### Level 1 / Level 2：可进入后续白名单评估

- 其余单路由、边界相对清晰的页面

## 建议

- Batch C 只从 `L1 + L2` 中筛白名单
- `L3` 页面只允许在后续“试点迁移域”之后再进入候选
- `L4` 当前批次绝对冻结
