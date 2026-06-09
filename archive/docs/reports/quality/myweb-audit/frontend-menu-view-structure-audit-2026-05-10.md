# Frontend Menu View Structure Audit - 2026-05-10

## 结论

本次核对以前端 Web 页面菜单为主轴，只采用两层结构：一级业务域 + 二级页面入口。

当前 `web/frontend/src/views/` 下 `.vue` 文件总量为 271 个，但这不是当前菜单页面数量。当前路由实际动态导入 view 约 42 个，ArtDeco 菜单配置声明 43 个 path（含一级域 path 与 `/dashboard` 特殊首页）。

造成 view 文件很多的主要原因：

- 当前 canonical 路由页：主要位于 `views/market`、`views/data`、`views/watchlist`、`views/strategy`、`views/trade`、`views/risk`、`views/system`。
- ArtDeco 兼容壳与内嵌 tab：仍保留在 `views/artdeco-pages/`，部分仍被当前路由复用。
- 历史迁移遗留页：如 `views/stocks`、`views/trading`、`views/monitoring`、`views/technical`、根目录旧页面。
- Demo / example / archive 型页面：如 `views/demo`、`views/examples`、`views/freqtrade-demo`、`views/tdxpy-demo`。
- 页面内部组件：部分目录虽然在 `views/` 下，但实际承担局部组件或 tab 功能，不应进入主菜单。

## 真相源

当前建议采用以下真相源顺序：

| 类型 | 文件 | 结论 |
|---|---|---|
| 路由真相源 | `web/frontend/src/router/index.ts` | 判定页面是否可访问的第一依据 |
| 当前 ArtDeco 菜单 | `web/frontend/src/layouts/MenuConfig.ts` | 当前两层主菜单配置，和路由基本对齐 |
| 旧侧边栏菜单 | `web/frontend/src/config/menu.config.js` | 存在旧路径漂移，不应继续作为菜单真相源 |
| 结构说明 | `docs/guides/frontend-structure.md` | 已明确 active routed business pages 通常应落在 `views/<domain>/*.vue` |

## 当前两层菜单结构

| 一级菜单 | 二级入口 | 当前实现 |
|---|---|---|
| 交易室 | `/dashboard` | `views/artdeco-pages/ArtDecoDashboard.vue`，特殊首页，不在侧边栏主菜单中 |
| 市场行情 | `/market/realtime` | `views/market/Realtime.vue` |
| 市场行情 | `/market/technical` | `views/market/Technical.vue` |
| 市场行情 | `/market/lhb` | `views/market/LHB.vue` |
| 数据分析 | `/data/industry` | `views/data/Industry.vue` |
| 数据分析 | `/data/indicator` | `views/data/Advanced.vue` |
| 数据分析 | `/data/concept` | `views/data/Concepts.vue` |
| 数据分析 | `/data/fund-flow` | `views/data/FundFlow.vue` |
| 自选管理 | `/watchlist/manage` | `views/watchlist/Manage.vue` |
| 自选管理 | `/watchlist/signals` | `views/watchlist/Signals.vue` |
| 自选管理 | `/watchlist/screener` | `views/watchlist/Screener.vue` |
| 策略管理 | `/strategy/repo` | `views/strategy/List.vue` |
| 策略管理 | `/strategy/parameters` | `views/strategy/Parameters.vue` |
| 策略管理 | `/strategy/signals` | `views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue` |
| 策略管理 | `/strategy/backtest` | `views/strategy/Backtest.vue` |
| 策略管理 | `/strategy/gpu` | `views/strategy/BacktestGPU.vue` |
| 策略管理 | `/strategy/opt` | `views/strategy/Optimization.vue` |
| 策略管理 | `/strategy/pos` | `views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue` |
| 交易管理 | `/trade/positions` | `views/trade/Center.vue` |
| 交易管理 | `/trade/terminal` | `views/TradingDashboard.vue` |
| 交易管理 | `/trade/execution` | `views/trade/Execution.vue` |
| 交易管理 | `/trade/signals` | `views/trade/Signals.vue` |
| 交易管理 | `/trade/portfolio` | `views/trade/Portfolio.vue` |
| 交易管理 | `/trade/history` | `views/trade/History.vue` |
| 交易管理 | `/trade/reconciliation` | `views/trade/Reconciliation.vue` |
| 风险管理 | `/risk/management` | `views/risk/Center.vue` |
| 风险管理 | `/risk/overview` | `views/risk/Overview.vue` |
| 风险管理 | `/risk/pnl` | `views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` |
| 风险管理 | `/risk/stop-loss` | `views/risk/StopLoss.vue` |
| 风险管理 | `/risk/alerts` | `views/risk/Alerts.vue` |
| 风险管理 | `/risk/news` | `views/risk/News.vue` |
| 系统设置 | `/system/config` | `views/system/Settings.vue` |
| 系统设置 | `/system/health` | `views/system/Health.vue` |
| 系统设置 | `/system/api` | `views/system/API.vue` |
| 系统设置 | `/system/resources` | `views/system/Resources.vue` |
| 系统设置 | `/system/data` | `views/system/DataSource.vue` |

## 已实现但未进入当前 ArtDeco 主菜单

| 路由 | 当前实现 | 建议 |
|---|---|---|
| `/ai/sentiment` | `views/ai/Sentiment.vue` | 若 AI 是正式业务域，应补入 `MenuConfig.ts`；否则标记为非主菜单实验域 |
| `/ai/ml` | `views/ai/MlWorkbench.vue` | 同上 |
| `/detail/graphics/:symbol` | `views/artdeco-pages/analysis-tabs/KLineAnalysis.vue` | 保持详情页，不进入主菜单 |
| `/detail/news/:symbol` | `views/announcement/AnnouncementMonitor.vue` | 保持详情页，不进入主菜单 |
| `/login` | `views/Login.vue` | Blank layout，不进入主菜单 |
| `/:pathMatch(.*)*` | `views/NotFound.vue` | Blank layout，不进入主菜单 |

## 二级资产库存摘要

以下目录不建议直接按文件数映射为菜单，只作为后续治理库存：

| 目录 / 类型 | 状态判断 | 处理建议 |
|---|---|---|
| `views/artdeco-pages/` | 兼容壳、嵌入 tab、少量仍为 canonical 例外 | 保留，但禁止继续沉淀为第二套页面真相源 |
| `views/market/` | 当前市场域 canonical 目录，同时含未入菜单页 | 菜单只保留 `realtime`、`technical`、`lhb`；其余按候选待审处理 |
| `views/data/` | 当前数据域 canonical 目录 | 保持两层目录 |
| `views/watchlist/` | 当前自选域 canonical 目录 | 保持两层目录 |
| `views/strategy/` | 当前策略域 canonical 目录，含扩展页 | 菜单已覆盖主入口；额外页按 backlog 判断 |
| `views/trade/` | 当前交易域 canonical 目录 | 保持两层目录 |
| `views/risk/` | 当前风险域 canonical 目录，含额外页 | 菜单已覆盖主入口；额外页按 backlog 判断 |
| `views/system/` | 当前系统域 canonical 目录，含旧监控页 | 菜单已覆盖主入口；旧页按静态壳/废弃候选判断 |
| `views/ai/` | 路由已实现但菜单未纳入 | 需要产品决策：正式一级域或实验域 |
| `views/stocks/`、`views/trading/`、`views/monitoring/`、`views/technical/` | 旧目录遗留 | 不进入主菜单；先标记兼容/废弃候选，禁止直接删除 |
| `views/demo/`、`views/examples/`、`views/freqtrade-demo/`、`views/tdxpy-demo/` | Demo / 示例 | 不进入主菜单；后续可迁入 demo 区或归档 |
| 根目录旧页面，如 `Wencai.vue`、`Market.vue`、`TradeManagement.vue` | 历史入口或兼容页 | 不作为当前菜单依据；逐个登记状态 |

## 旧菜单漂移问题

`web/frontend/src/config/menu.config.js` 中存在多处和当前路由不一致的路径，例如：

- `/market/wencai`
- `/technical/indicators`
- `/technical/analysis`
- `/strategy/management`
- `/strategy/risk`
- `/monitoring/watchlists`
- `/risk/announcement`
- `/stocks/management`
- `/stocks/portfolio`
- `/system/architecture`
- `/system/database-monitor`
- `/system/monitoring`
- `/system/logs`
- `/system/settings`
- `/data/import`

这些路径不应作为当前页面目录规划依据。若仍有组件引用该旧配置，应单独做“菜单配置收口批次”：要么迁移消费者到 `layouts/MenuConfig.ts`，要么把旧配置降级为兼容导出并加明确退场条件。

## 建议的收口规则

1. 主菜单固定两层：`一级业务域 / 二级页面入口`，不继续向三级菜单扩展。
2. 当前 canonical 目录固定为 `views/<domain>/<Page>.vue`，domain 仅限 `market`、`data`、`watchlist`、`strategy`、`trade`、`risk`、`system`，AI 需单独决策。
3. `/dashboard`、`/login`、`404`、`/detail/*` 属于特殊页，不纳入主菜单层级。
4. `artdeco-pages/` 只允许作为兼容壳、嵌入 tab 或少数已声明例外，不再作为新页面主目录。
5. 旧目录和 demo 目录先登记状态，不直接删除；删除前必须完成“代码路径判定 + 功能树判定”。
6. 后续页面审计应以 `MenuConfig.ts -> router/index.ts -> views/<domain>` 作为唯一对账链路。

## 下一步建议

建议拆成三个小批次：

| 批次 | 目标 | 产物 |
|---|---|---|
| batch-menu-01 | 统一菜单真相源 | 标记或迁移 `config/menu.config.js` 的旧路径消费者 |
| batch-menu-02 | 生成 view 库存三分类 | 候选待审 / 内嵌兼容 / Demo 废弃清单 |
| batch-menu-03 | 按菜单二级入口补齐审计状态 | 每个菜单页面标记已审、待复核、未审 |

