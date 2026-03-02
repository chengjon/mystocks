# MyStocks 菜单整合与优化技术方案 (V3.2 Elite)

## 1. 导航层级规范
*   **P0：核心驾驶舱 (The Dealing Room)**
    *   **路径**: `/dealing-room` (系统默认根路径 `/` 自动重定向至此)
    *   **特性**: 全局概览视图，**在侧边栏菜单中隐藏**。
*   **P1：业务域菜单 (Standard Menu)**
    *   **特性**: 侧边栏显性入口，分为 7 大核心业务域。
*   **P2：交互详情页 (Contextual Details)**
    *   **特性**: 无显性菜单入口，通过代码/新闻的左键或右键交互触发，支持动态参数。

## 2. 完整业务域映射表 (Menu-Route-API-Component)

| 业务域 | 功能项 | 路由路径 | 核心组件 (Component) | 支撑 API (Primary) |
| :--- | :--- | :--- | :--- | :--- |
| **市场行情** | 实时行情流 | `/market/realtime` | `MarketRealtimeTab.vue` | `/api/v1/market/quotes` |
| | K线分析 | `/market/technical`| `KLineAnalysis.vue` | `/api/v1/market/kline` |
| | 龙虎榜分析 | `/market/lhb` | `DragonTigerAnalysis.vue`| `/api/data/lhb` |
| **数据分析** | 板块动向 | `/data/industry` | `IndustryAnalysis.vue` | `/api/akshare_market/boards` |
| | 概念动向 | `/data/concept` | `ConceptAnalysis.vue` | `/api/akshare_market/boards` |
| | 资金流向 | `/data/fund-flow` | `FundFlowAnalysis.vue` | `/api/akshare_market/fund_flow`|
| **自选股管理** | 组合管理 | `/watchlist/manage`| `WatchlistManager.vue` | `/api/watchlist` |
| | 信号雷达 | `/watchlist/signals`| `StrategySignalsTab.vue` | `/api/v1/trade/signals` |
| | 策略选股 | `/watchlist/screener`| `Screener.vue` | `/api/data/stocks` |
| **策略管理** | 策略仓库 | `/strategy/repo` | `StrategyManagement.vue` | `/api/v1/strategy/list` |
| | 回测引擎 | `/strategy/backtest`| `BacktestAnalysis.vue` | `/api/v1/strategy/backtest` |
| | 加速监控 | `/strategy/gpu` | `BacktestGPU.vue` | `/gpu` |
| | 参数优化 | `/strategy/opt` | `StrategyOptimization.vue`| `/api/strategy/optimization`|
| | 仓位管理 | `/strategy/pos` | `PortfolioMonitor.vue` | `/api/v1/trade/positions` |
| **交易管理** | 头寸管理 | `/trade/positions` | `TradingPositions.vue` | `/api/v1/trade/positions` |
| | 交易终端 | `/trade/terminal` | `TradingDashboard.vue` | `/api/trade/routes` |
| | 信号监控 | `/trade/signals` | `SignalsView.vue` | `/api/v1/trade/signals` |
| | 持仓透视 | `/trade/portfolio` | `PortfolioOverview.vue` | `/api/v1/trade/positions` |
| | 历史对账 | `/trade/history` | `TradingHistory.vue` | `/api/trade/routes` |
| **风险管理** | 风险概览 | `/risk/overview` | `RiskOverviewTab.vue` | `/api/risk-management` |
| | 组合盈亏 | `/risk/pnl` | `PortfolioOverviewTab.vue`| `/api/v1/trade/positions` |
| | 止损雷达 | `/risk/stop-loss` | `StopLossMonitorTab.vue` | `/api/risk_v31/stop_loss` |
| | 告警中心 | `/risk/alerts` | `ArtDecoRiskAlerts.vue` | `/api/risk_v31/alerts` |
| | 舆情公告 | `/risk/news` | `AnnouncementMonitor.vue`| `/api/v1/announcement` |
| **系统设置** | 系统配置 | `/system/config` | `ArtDecoSystemSettings.vue`| N/A |
| | 健康矩阵 | `/system/health` | `SystemHealthTab.vue` | `/health` |
| | API 终端 | `/system/api` | `APIHealth.vue` (New) | `/metrics` |
| | 数据源管理 | `/system/data` | `DataSourceSettings.vue` | `/api/data_source_config` |

## 3. 详情页交互逻辑 (The Context Model)

### 3.1 股票详情 - 图形化 (Stock Graphics)
*   **交互**: 页面任何位置点击股票代码（如 `600519`）。
*   **路由**: `/detail/graphics/:symbol`
*   **页面构成**:
    *   **Tab 1: 分时图**: 接入 `/api/v1/market/quotes` 实时流。
    *   **Tab 2: K线图**: 接入 `/api/v1/market/kline` 历史流。
*   **组件**: 创建 `StockDetailView.vue` 作为包装容器。

### 3.2 股票详情 - 资讯 (Stock News)
*   **交互**: 股票代码右键菜单 -> **[查看相关新闻]**。
*   **路由**: `/detail/news/:symbol`
*   **组件**: 激活并重构 `demo/openstock/components/StockNews.vue`。

## 4. 激活与整合计划 (Orphan Cleanup)
1.  **转正高级分析组件**: 
    *   将 `advanced-analysis/ChipDistributionView.vue` (筹码分布) 以 Tab 形式整合进 `/market/technical`。
    *   将 `advanced-analysis/RadarAnalysisView.vue` (雷达图) 整合进 `/risk/overview`。
2.  **清理冗余路径**: 
    *   将 `/stocks/` 统一重写为 `/watchlist/`。
    *   将 `/monitoring/` 逻辑合并入 `/trade/` 和 `/risk/`。

## 5. 治理与规范 (Rules)
*   **Breadcrumbs**: 详情页面包屑必须包含 `[交易室] > [业务域] > [股票代码: 详情]` 结构。
*   **State**: 点击“返回”时，利用 `vue-router` 的 `scrollBehavior` 保持滚动位置。
*   **Uniform API**: 强制通过 `VERSION_MAPPING.py` 校验 API 路径有效性。
