# 2026-03-27 Frontend Directory Batch A：活跃页真值清单

> **历史文档说明**:
> 本文件是某阶段的历史文档、过程记录或专题材料，不是当前基线、当前系统总览或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内描述、背景、结论和上下文如未重新复核，应视为历史快照，不得直接当作当前事实。


> 输出目标：建立“当前活跃路由 -> 当前文件路径 -> 当前桶位 -> 目标域归属”的真值表。
>
> 用途：
> - 作为后续目录治理的保护名单
> - 防止把仍在主线路由中的页面误判为可归档/可删除
> - 为后续 Batch B / Batch C / Batch E 提供输入

## 1. 统计结论

- 当前 `router/index.ts` 中命名路由数：`36`
- 活跃路由对应的唯一视图组件数：`34`
- 其中：
  - 位于 `artdeco-pages` 的唯一组件：`28`
  - 位于根层 `src/views/*.vue` 的唯一组件：`3`
    - `Login.vue`
    - `NotFound.vue`
    - `TradingDashboard.vue`
  - 位于其它域目录的唯一组件：`3`
    - `announcement/AnnouncementMonitor.vue`
    - `stocks/Screener.vue`
    - `strategy/BacktestGPU.vue`

## 2. 核心发现

### 2.1 当前主线仍高度依赖 `artdeco-pages`

当前 36 个命名路由里，绝大多数业务主线路由仍指向：

- `artdeco-pages`
- 以及其内部子目录：
  - `market-tabs`
  - `market-data-tabs`
  - `strategy-tabs`
  - `trading-tabs`
  - `risk-tabs`
  - `system-tabs`
  - `portfolio-tabs`
  - `analysis-tabs`

结论：

- `artdeco-pages` 目前仍是“活跃主线真值源”
- 在没有替换路由之前，不能把它视为历史目录整体清空

### 2.2 存在一对多路由复用组件

以下组件被多个命名路由复用：

- `StrategySignalsTab.vue`
  - `watchlist-signals`
  - `strategy-signals`
- `ArtDecoTradingPositions.vue`
  - `strategy-pos`
  - `trade-positions`
- `PortfolioOverviewTab.vue`
  - `trade-portfolio`
  - `risk-pnl`

结论：

- 后续迁移不能简单按“一个路由 = 一个页面文件”处理
- 这些组件需要在后续批次中先做“归属判定”，再决定是否拆分

### 2.3 存在必须单独决策的非 `artdeco-pages` 活跃页

- `watchlist-screener` -> `@/views/stocks/Screener.vue`
- `trade-terminal` -> `@/views/TradingDashboard.vue`
- `stock-news` -> `@/views/announcement/AnnouncementMonitor.vue`
- `strategy-gpu` -> `@/views/strategy/BacktestGPU.vue`
- `login` -> `@/views/Login.vue`
- `not-found` -> `@/views/NotFound.vue`

这些页面不能被简单纳入“按域迁移 artdeco-pages”的批次里。

## 3. 活跃页真值表

| 路由名 | 当前 URL | 当前组件 | 当前桶位 | 目标域归属 | Batch A 结论 |
|---|---|---|---|---|---|
| `dashboard` | `/dashboard` | `@/views/artdeco-pages/ArtDecoDashboard.vue` | `artdeco-pages root` | `dashboard/home` | 活跃核心页，后续只能替换式迁移 |
| `market-realtime` | `/market/realtime` | `@/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue` | `artdeco-pages/market-tabs` | `market` | 后续可作为 market 域迁移候选 |
| `market-technical` | `/market/technical` | `@/views/artdeco-pages/market-tabs/MarketKLineTab.vue` | `artdeco-pages/market-tabs` | `market` | 后续可作为 market 域迁移候选 |
| `market-lhb` | `/market/lhb` | `@/views/artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue` | `artdeco-pages/market-data-tabs` | `market` | 后续可作为 market 域迁移候选 |
| `data-industry` | `/data/industry` | `@/views/artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue` | `artdeco-pages/market-data-tabs` | `data` | 活跃页，属于 data 候选 |
| `data-concept` | `/data/concept` | `@/views/artdeco-pages/market-tabs/MarketConceptTab.vue` | `artdeco-pages/market-tabs` | `data` | 活跃页，属于 data 候选 |
| `data-fund-flow` | `/data/fund-flow` | `@/views/artdeco-pages/market-data-tabs/FundFlowAnalysis.vue` | `artdeco-pages/market-data-tabs` | `data` | 活跃页，属于 data 候选 |
| `data-indicator` | `/data/indicator` | `@/views/artdeco-pages/ArtDecoDataAnalysis.vue` | `artdeco-pages root` | `data` | 活跃核心页 |
| `watchlist-manage` | `/watchlist/manage` | `@/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue` | `artdeco-pages/stock-management-tabs` | `watchlist` | 候选迁移页 |
| `watchlist-signals` | `/watchlist/signals` | `@/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue` | `artdeco-pages/strategy-tabs` | `watchlist` | 与 `strategy-signals` 共享组件，需先判归属 |
| `watchlist-screener` | `/watchlist/screener` | `@/views/stocks/Screener.vue` | `stocks` | `watchlist` | 活跃页，当前已脱离 `artdeco-pages`，需单独决策 |
| `strategy-repo` | `/strategy/repo` | `@/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue` | `artdeco-pages/strategy-tabs` | `strategy` | 活跃核心页 |
| `strategy-parameters` | `/strategy/parameters` | `@/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue` | `artdeco-pages/strategy-tabs` | `strategy` | 活跃页 |
| `strategy-signals` | `/strategy/signals` | `@/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue` | `artdeco-pages/strategy-tabs` | `strategy` | 与 `watchlist-signals` 共享组件，需先判归属 |
| `strategy-backtest` | `/strategy/backtest` | `@/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue` | `artdeco-pages/strategy-tabs` | `strategy` | 活跃页 |
| `strategy-gpu` | `/strategy/gpu` | `@/views/strategy/BacktestGPU.vue` | `strategy` | `strategy` | 已在目标域，优先保护 |
| `strategy-opt` | `/strategy/opt` | `@/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue` | `artdeco-pages/strategy-tabs` | `strategy` | 活跃页 |
| `strategy-pos` | `/strategy/pos` | `@/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue` | `artdeco-pages/trading-tabs` | `strategy` | 与 `trade-positions` 共享组件，需先判归属 |
| `trade-positions` | `/trade/positions` | `@/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue` | `artdeco-pages/trading-tabs` | `trade` | 与 `strategy-pos` 共享组件，需先判归属 |
| `trade-terminal` | `/trade/terminal` | `@/views/TradingDashboard.vue` | `views root` | `trade` | 主动交易页，必须单独判定去向 |
| `trade-signals` | `/trade/signals` | `@/views/artdeco-pages/trading-tabs/ArtDecoSignalsView.vue` | `artdeco-pages/trading-tabs` | `trade` | 活跃页 |
| `trade-portfolio` | `/trade/portfolio` | `@/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` | `artdeco-pages/portfolio-tabs` | `trade` | 与 `risk-pnl` 共享组件，需先判归属 |
| `trade-history` | `/trade/history` | `@/views/artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue` | `artdeco-pages/trading-tabs` | `trade` | 活跃页 |
| `risk-management` | `/risk/management` | `@/views/artdeco-pages/ArtDecoRiskManagement.vue` | `artdeco-pages root` | `risk` | 活跃核心页 |
| `risk-overview` | `/risk/overview` | `@/views/artdeco-pages/risk-tabs/RiskOverviewTab.vue` | `artdeco-pages/risk-tabs` | `risk` | 活跃页 |
| `risk-pnl` | `/risk/pnl` | `@/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` | `artdeco-pages/portfolio-tabs` | `risk` | 与 `trade-portfolio` 共享组件，需先判归属 |
| `risk-stop-loss` | `/risk/stop-loss` | `@/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue` | `artdeco-pages/risk-tabs` | `risk` | 活跃页 |
| `risk-alerts` | `/risk/alerts` | `@/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue` | `artdeco-pages/risk-tabs` | `risk` | 活跃页 |
| `risk-news` | `/risk/news` | `@/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue` | `artdeco-pages/risk-tabs` | `risk` | 活跃页 |
| `system-config` | `/system/config` | `@/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue` | `artdeco-pages/system-tabs` | `system` | 活跃页 |
| `system-health` | `/system/health` | `@/views/artdeco-pages/system-tabs/SystemHealthTab.vue` | `artdeco-pages/system-tabs` | `system` | 活跃页 |
| `system-api` | `/system/api` | `@/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue` | `artdeco-pages/system-tabs` | `system` | 活跃页 |
| `system-data` | `/system/data` | `@/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue` | `artdeco-pages/system-tabs` | `system` | 活跃页 |
| `stock-graphics` | `/detail/graphics/:symbol` | `@/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue` | `artdeco-pages/analysis-tabs` | `detail` | 详情页，需单独保留策略 |
| `stock-news` | `/detail/news/:symbol` | `@/views/announcement/AnnouncementMonitor.vue` | `announcement` | `detail` | 当前依附于 announcement 目录，需单独决策 |
| `login` | `/login` | `@/views/Login.vue` | `views root` | `auth/errors` | 根层保留，禁止迁移到业务域 |
| `not-found` | `/:pathMatch(.*)*` | `@/views/NotFound.vue` | `views root` | `errors` | 根层保留，禁止迁移到业务域 |

## 4. Batch A 结论

### 4.1 当前绝不能做的事

- 不能直接清空 `artdeco-pages`
- 不能按旧任务把 `strategy-signals` / `trade-positions` / `portfolio` 相关页简单搬走
- 不能把根层 `TradingDashboard.vue` / `Login.vue` / `NotFound.vue` 一并纳入同一迁移批次

### 4.2 后续批次输入

基于本真值表，后续批次应按以下顺序衔接：

- Batch B：
  - 做“历史/示例页隔离清单”
- Batch C：
  - 做“根层视图文件分类表”
- Batch D：
  - 做“共享资产依赖地图”
- Batch E：
  - 只选择一个域做试点迁移

## 5. 建议审批口径

如果继续推进目录治理，下一步建议审批为：

`同意执行 Batch B：历史/示例页隔离清单`
