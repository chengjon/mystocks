# ArtDeco Fintech Page Composition Audit

> 审查日期: 2026-03-25
> 审查目标: 页面级 ArtDeco 仪式感、构图继承度与运行时样式边界
> 审查方式: 基于当前 Vue 页面与样式源码抽样，不涉及视觉重写实施

> 2026-04-01 状态说明
>
> - 本文档聚焦“页面舞台层与工作台节奏”，不是样式真值文档，也不是组件目录文档。
> - 阅读本文件前，建议先看：`ARTDECO_START_HERE.md`、`ARTDECO_MASTER_INDEX.md`、`ARTDECO_FINTECH_UNIFIED_SPEC.md`。
> - 当前审查对象已覆盖三类页面承载模式：模板化工作台、直接 Tab 容器、功能树驱动总控容器。
>
## 1. 结论先行

当前项目的 ArtDeco 问题，已经不主要是 token 或字体问题，而是页面构图层一致性：

- 组件语言总体已经具备 ArtDeco Fintech 气质。
- 页面级表现曾经存在明显分层。
- 第一轮页面级治理已经完成，核心入口页已从“普通后台化”收敛到统一工作站骨架。
- 第二轮页面级治理已开始推进，正在继续缩小剩余页面的一致性缺口。
- 剩余问题主要集中在未专项治理页面与进一步模板化。

基于当前代码状态，可以明确判断：

- `ArtDecoDashboard.vue` 代表当前最强继承样本。
- `ArtDecoDataAnalysis.vue`、`ArtDecoMarketData.vue`、`ArtDecoTradingCenter.vue`、`ArtDecoSystemSettings.vue` 已完成第一轮页面骨架治理。
- `ArtDecoStockManagement.vue`、`ArtDecoMarketQuotes.vue`、`ArtDecoTradingManagement.vue`、`ArtDecoStrategyManagement.vue`、`ArtDecoStrategyOptimization.vue`、`ArtDecoBacktestAnalysis.vue`、`StrategyParametersTab.vue`、`StrategySignalsTab.vue`、`ArtDecoSignalsView.vue`、`ArtDecoMonitoringDashboard.vue`、`ArtDecoDataManagement.vue`、`SystemHealthTab.vue`、`ArtDecoRiskAlerts.vue`、`ArtDecoAnnouncementMonitor.vue`、`RiskOverviewTab.vue`、`StopLossMonitorTab.vue`、`MarketRealtimeTab.vue`、`MarketKLineTab.vue`、`MarketConceptTab.vue`、`DragonTigerAnalysis.vue`、`FundFlowAnalysis.vue`、`ArtDecoIndustryAnalysis.vue` 已完成第二轮页面治理中的核心补强。
- `ArtDecoRiskManagement.vue` 已完成第二轮页面治理中的风险控制页收敛。
- `ArtDecoLayoutEnhanced.vue` 已从旧兼容入口收敛到主 token 链。
- `ArtDecoMarketOverview.vue` 已不再是占位页。

## 2. 审查标准

本次按六个维度评估页面：

1. 头部仪式感
   页面是否存在明确的标题舞台、状态位、操作区、次级元信息。
2. 轴线与容器骨架
   页面是否具有 ArtDeco 的建筑感、中心节奏、外壳容器，而不是平铺堆组件。
3. 分区节奏
   页面是否通过 shell、divider、留白、stats strip、tabs shell 建立层级。
4. 图标与视觉语汇
   页面是否使用一致的 ArtDeco iconography，而不是 emoji 或杂糅表达。
5. 共享模式复用
   页面是否复用 `ArtDecoHeader`、`ArtDecoPageTemplate` 或等价骨架，而不是各自临时拼装。
6. 兼容层泄漏
   页面是否仍明显依赖兼容层或旧入口，导致风格表现偏行政后台化。

## 3. 抽样页评分

| 页面 | 评级 | 判断 |
|------|------|------|
| `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue` | A | 当前最接近 `ArtDeco Fintech` 舞台感 |
| `web/frontend/src/views/artdeco-pages/ArtDecoDataAnalysis.vue` | A- | 页面壳层已统一，剩余主要是共享模板复用层面 |
| `web/frontend/src/views/artdeco-pages/ArtDecoTechnicalAnalysis.vue` | B+ | 已补足 hero/stats/tabs/content 骨架 |
| `web/frontend/src/views/artdeco-pages/ArtDecoSettings.vue` | B+ | 已从配置后台页收敛到统一的设置控制面板 |
| `web/frontend/src/views/artdeco-pages/ArtDecoMarketData.vue` | B+ | 已补足 meta rail、stats strip、tabs shell 和 content shell |
| `web/frontend/src/views/artdeco-pages/ArtDecoStockManagement.vue` | B+ | 已补足工作流骨架，并明确空 tab 的占位表达 |
| `web/frontend/src/views/artdeco-pages/ArtDecoTradingCenter.vue` | B+ | 已从后台壳提升为 ArtDeco Fintech 工作站骨架 |
| `web/frontend/src/views/artdeco-pages/ArtDecoTradingManagement.vue` | B+ | 已补足执行工作流骨架，并统一 tab 元信息表达 |
| `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue` | B+ | 已补足独立路由工作台骨架，并兼容 TradingCenter 内嵌场景 |
| `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue` | B+ | 已补足优化候选工作台骨架，并兼容 TradingCenter 内嵌场景 |
| `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue` | B+ | 已补足独立路由/内嵌双态壳层，并将回测页收口到统一工作台节奏 |
| `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue` | B+ | 已从单页头参数卡片页收敛到参数工作台骨架 |
| `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue` | B+ | 已从信号时间轴单页提升为完整信号工作台骨架 |
| `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoSignalsView.vue` | B+ | 已补足独立路由/内嵌双态壳层，并收敛到交易信号工作台语法 |
| `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue` | B+ | 已补足独立路由/内嵌双态壳层，并收敛到交易历史工作台语法 |
| `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue` | B+ | 已补足独立路由/内嵌双态壳层，并收敛到持仓工作台语法 |
| `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue` | B+ | 已补足独立路由/内嵌双态壳层，并收敛到可观测性工作台语法 |
| `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue` | B+ | 已补足独立路由/内嵌双态壳层，并收敛到数据源治理工作台语法 |
| `web/frontend/src/views/artdeco-pages/system-tabs/SystemHealthTab.vue` | B+ | 已从基础探针页收敛到系统健康矩阵工作台骨架 |
| `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue` | B+ | 已补足独立路由/内嵌双态壳层，并收敛到告警治理工作台语法 |
| `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue` | B+ | 已补足独立路由/内嵌双态壳层，并收敛到公告/舆情治理工作台语法 |
| `web/frontend/src/views/artdeco-pages/risk-tabs/RiskOverviewTab.vue` | B+ | 已从轻量 tab 页收敛到完整风险总览工作台骨架 |
| `web/frontend/src/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue` | B+ | 已从监控卡片页收敛到止损雷达工作台骨架 |
| `web/frontend/src/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue` | B+ | 已从独立数据页收敛到实时行情工作台骨架 |
| `web/frontend/src/views/artdeco-pages/market-tabs/MarketKLineTab.vue` | B+ | 已从轻量 K 线页收敛到技术行情工作台骨架 |
| `web/frontend/src/views/artdeco-pages/market-tabs/MarketConceptTab.vue` | B+ | 已从概念表格页收敛到板块动向工作台骨架 |
| `web/frontend/src/views/artdeco-pages/market-tabs/MarketETFTab.vue` | B+ | 已从独立 ETF 数据页收敛到 ETF 市场工作台骨架 |
| `web/frontend/src/views/artdeco-pages/technical-tabs/TechnicalScannerTab.vue` | B+ | 已从技术筛选页收敛到技术扫描工作台骨架 |
| `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` | B+ | 已从资产页收敛到组合资产工作台骨架 |
| `web/frontend/src/views/artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue` | B+ | 已支持独立路由/ArtDecoMarketData 内嵌双态壳层，并收敛到龙虎榜工作台语法 |
| `web/frontend/src/views/artdeco-pages/market-data-tabs/FundFlowAnalysis.vue` | B+ | 已支持独立路由/ArtDecoMarketData 内嵌双态壳层，并收敛到资金流向工作台语法 |
| `web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue` | B+ | 已支持独立路由/TradingCenter 内嵌双态壳层，并收敛到板块动向工作台语法 |
| `web/frontend/src/views/artdeco-pages/ArtDecoRiskManagement.vue` | B+ | 已将风险页 tabs/content shell 收敛到统一工作台语法，并替换为语义化图标 |
| `web/frontend/src/views/artdeco-pages/ArtDecoMarketQuotes.vue` | B | 已去除调试残留并完成第一轮工作台化收敛 |
| `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue` | B+ | 已完成第一轮舞台层治理，表现不再后台化 |
| `web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue` | B | 布局层兼容入口已收口，但仍可继续做更深层统一 |

## 4. 主要发现

### 4.1 强样本: Dashboard

`web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue` 与 `web/frontend/src/views/artdeco-pages/styles/ArtDecoDashboard.scss` 已经具备较强的页面级继承：

- 使用 `ArtDecoHeader` 作为主舞台。
- 存在 `request-meta-bar` 这类次级信息轨。
- 页面外壳有中心装饰线和戏剧性背景。
- `summary-section`、`charts-section`、`flow-section` 等分区节奏明确。

这类页面说明当前项目不是不会做页面级 ArtDeco，而是没有把这套模式推广成统一约束。

### 4.2 中上样本: DataAnalysis

`web/frontend/src/views/artdeco-pages/ArtDecoDataAnalysis.vue` 的优点在于：

- 有 `eyebrow`、`card-shell`、`stats-overview`、`tabs shell`。
- 页面不是简单堆组件，而是先建立容器层再放内容。
- 标题与正文、stats、tabs、content 之间层级关系清楚。

第一轮整改后：

- 主 tab 的 emoji 已替换成 `ArtDecoIcon` 语义。
- 分类侧栏的 emoji 也已被统一图标语汇替换。
- 页面已具备完整的 `hero + stats + tabs + content` 骨架。

它当前剩余的问题不再是视觉退化，而是“已经非常接近共享模板能力，但仍在手写页面壳层”。

### 4.3 已整改样本: MarketData

`web/frontend/src/views/artdeco-pages/ArtDecoMarketData.vue` 原本是最典型的“组件 ArtDeco，页面不 ArtDeco”。第一轮整改后已完成：

- `mainTabs` 已切换为统一的 `ArtDecoIcon` 语义。
- 页面已补齐 `hero/meta/stats/tabs/content` 骨架。
- 内联 `margin-top` 写法已清理。
- 页面已从“分类按钮条”提升为更完整的市场情报工作站面板。

### 4.4 已整改样本: TradingCenter

`web/frontend/src/views/artdeco-pages/ArtDecoTradingCenter.vue` 与 `web/frontend/src/views/artdeco-pages/styles/ArtDecoTradingCenter.scss` 的原问题不在组件，而在总构图。第一轮整改后：

- 已补足 `hero shell + stats strip + workstation shell`。
- 左侧功能树和右侧动态内容区都已拥有统一的面板头与元信息轨。
- 整体不再只是“左树 + 右内容”的后台壳，而是明确的工作站结构。

另外，`web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoMarketOverview.vue` 也已经从占位内容替换成可用的市场总览入口面板，不再拖累 Trading Center 的整体完成度。

### 4.5 已整改样本: SystemSettings

`web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue` 的原问题很直接，但第一轮整改后已明显收敛：

- 已切换到 `ArtDecoHeader`。
- 已补足 hero、stats、tabs、content 四层舞台。
- 样式入口已切换为 `@use '@/styles/artdeco-tokens.scss' as *;`。
- 当前已经达到“合格且统一”的工作站子页水准。

### 4.6 已整改样本: Settings / TechnicalAnalysis

`web/frontend/src/views/artdeco-pages/ArtDecoSettings.vue` 与 `web/frontend/src/views/artdeco-pages/ArtDecoTechnicalAnalysis.vue` 在第一轮整改前属于“可用但不够完成”的页面；当前状态是：

- `Settings` 已完成 hero/stats/tabs/content 骨架收敛，且设置 tab 已去除 emoji。
- `TechnicalAnalysis` 已补足完整的页面舞台层和 tab 元信息结构。

它们现在更适合归类为“第一轮整改已完成，后续可做精修”，而不是“待补救”。

### 4.7 已整改样本: RiskManagement

`web/frontend/src/views/artdeco-pages/ArtDecoRiskManagement.vue` 原本虽然已经接入 `ArtDecoPageTemplate`，但仍停留在“模板可用、页面壳层偏薄”的状态；当前已完成：

- `riskTabs` 已切换到 `RiskManagement` / `StockAnalysis` 语义图标。
- tabs 区域补足 `eyebrow + title + description + trace` 的壳层信息。
- content 区域补足当前焦点和更新时间的 meta header，不再只是直接堆叠面板。
- 风险子面板样式入口已切换为 `@use '@/styles/artdeco-tokens.scss' as *;`。

它现在已经进入与 StockManagement / TradingManagement 同一组的“工作台化风险控制页”序列。

### 4.8 已整改样本: StrategyManagement

`web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue` 原本更像“功能完整但构图偏薄的仓库表格页”；当前已完成：

- 独立路由态补足 `hero + stats + content shell` 工作台骨架。
- 页面头部将 `REQ_ID / PROCESS / SOURCE` 提升为明确的 meta rail，而不再只停留在表格卡片头部。
- 新增策略总数、运行中、异常数和当前焦点四个 stats strip 指标，强化页面级节奏。
- 通过 `embedded` 退化模式兼容 `ArtDecoTradingCenter.vue` 内嵌场景，避免双重 hero/tabs 壳层叠加。

它现在已经从“策略列表页”提升为真正的策略仓库工作台，同时保持与 TradingCenter 的组合关系稳定。

### 4.9 已整改样本: StrategyOptimization

`web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue` 原本更接近“优化结果表格 + 右侧 contract 卡”的功能页；当前已完成：

- 独立路由态补足 `hero + stats + content shell`，让优化候选页具备完整的工作台节奏。
- 页面头部把 `REQ_ID / PROCESS / SOURCE` 提升为明确的 meta rail，而不再只放在卡片头部。
- 新增候选总数、当前筛选、异常策略和当前焦点四个 stats 指标，建立页面级优先级。
- 保留 `embedded` 退化模式，兼容 `ArtDecoTradingCenter.vue` 内嵌时不重复渲染外层舞台。

它现在已经和 StrategyManagement 一起构成策略研发链路里的双工作台节点，而不是单纯的附属子页。

### 4.10 已整改样本: BacktestAnalysis

`web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue` 原本已经有较强的 domain 组件，但在页面承载上仍缺少“独立路由页”和 “TradingCenter 内嵌页”之间的显式边界；当前已完成：

- 独立路由态继续保留 `BacktestHeader + KPI grid` 作为主舞台，不再只是普通内容堆叠。
- 增加 `embedded` 摘要壳层，使其在 TradingCenter 内嵌时不再直接裸露完整页头。
- `BacktestWorkbenchTabs` 已补足 tabs rail header，不再只是孤立的按钮条。
- 本地样式入口已切换为 `@use '@/styles/artdeco-tokens.scss' as *;`。
- 回测页因此获得了与策略仓库、策略优化相同的“双态工作台”承载逻辑。

它现在可以被视为策略研发链路中的第三个稳定工作台节点。

### 4.11 已整改样本: StrategyParameters / StrategySignals

`web/frontend/src/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue` 与 `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue` 原本都更接近“有内容但页面构图偏薄”的路由子页；当前已完成：

- 两页都补足了 `hero + stats + content shell` 的工作台骨架。
- 参数页现在明确暴露策略可见数、参数总项、优化联动和当前焦点，不再只是卡片堆叠。
- 信号页现在明确暴露买入/卖出/观望分布，并把时间轴收纳在统一内容壳层里。
- 两页样式入口都已切换为 `@use` 主链。

它们现在已经和策略仓库、策略优化、策略回测一起构成完整的策略域工作台链路。

### 4.12 已整改样本: MonitoringDashboard / DataManagement

`web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue` 与 `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue` 原本都更接近“TradingCenter 内部功能面板”，缺少独立路由态与内嵌态之间的显式承载边界；当前已完成：

- 两页都补足了独立路由 `hero + stats + content shell` 工作台骨架。
- 两页都补上了 `embedded` 退化模式，避免在 `ArtDecoTradingCenter.vue` 内嵌时叠出双重舞台。
- 监控页现在明确暴露服务状态、服务名、版本和中间件项，形成可观测性工作台。
- 数据源页现在明确暴露数据源数量、启用数、写回能力和当前请求，形成数据治理工作台。

它们现在已经进入系统治理链路的工作台序列，而不再只是“系统标签页里的功能块”。

### 4.13 已整改样本: SystemHealth / RiskAlerts / Announcement / RiskOverview / StopLoss / RiskMonitor Placeholder

`web/frontend/src/views/artdeco-pages/system-tabs/SystemHealthTab.vue` 与 `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue` 原本都更偏向“基础功能页”；当前已完成：

- `SystemHealthTab.vue` 已补足 `hero + stats + content shell`，不再只是探针信息块的平铺。
- `ArtDecoRiskAlerts.vue` 已补足独立路由/TradingCenter 内嵌双态壳层，进入标准的风险治理工作台语法。
- `ArtDecoAnnouncementMonitor.vue` 已补足独立路由/TradingCenter 内嵌双态壳层，进入标准的公告与舆情治理工作台语法。
- `RiskOverviewTab.vue` 已补足 `hero + stats + tabs + content shell`，成为风险总览路由的标准工作台入口。
- `StopLossMonitorTab.vue` 已补足 `hero + stats + content shell`，成为止损雷达路由的标准工作台入口。
- `ArtDecoRiskMonitor.vue` 虽仍是占位页，但历史失效样式已经被标准化占位壳层替换，不再继续扩散旧 ArtDeco 兼容写法。

这意味着系统健康矩阵、风险告警中心、公告舆情中心、风险概览页和止损雷达页都已经进入第二轮治理基线，而风险监控主面板至少完成了“占位也要符合当前工作台语法”的最小收口。

### 4.14 已整改样本: MarketRealtime / MarketKLine / MarketConcept

`web/frontend/src/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue`、`web/frontend/src/views/artdeco-pages/market-tabs/MarketKLineTab.vue` 与 `web/frontend/src/views/artdeco-pages/market-tabs/MarketConceptTab.vue` 原本都更偏向“路由级数据页”，页面壳层明显弱于当前工作台基线；当前已完成：

- 三页都补足了 `hero + stats + content shell` 的独立工作台骨架。
- 实时行情页现在明确暴露窗口、市场范围、情绪和指数快照之间的关系。
- K线页现在明确暴露当前标的、最新价格、样本点和图形占位区之间的结构关系。
- 概念页现在明确暴露上涨/下跌概念数量和龙头股，板块表格不再裸露在单层页头之下。

它们现在已经不再只是市场域的“子路由数据页”，而是具备标准 ArtDeco 工作台承载的市场入口节点。

### 4.15 已整改样本: MarketETF / TechnicalScanner / PortfolioOverview

`web/frontend/src/views/artdeco-pages/market-tabs/MarketETFTab.vue`、`web/frontend/src/views/artdeco-pages/technical-tabs/TechnicalScannerTab.vue` 与 `web/frontend/src/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue` 原本都更偏向“独立数据页”或“功能页”；当前已完成：

- 三页都补足了独立路由态的 `hero + stats + content shell` 工作台骨架。
- ETF 页现在明确暴露样本数量、上涨数量、总成交量和头部产品。
- Technical Scanner 页现在明确暴露多头信号、超买信号和平均趋势分值。
- Portfolio Overview 页现在把资产规模、持仓数量和再平衡建议一起提升到页面级舞台。

它们现在已经进入市场/技术/组合三个子域的独立工作台序列，不再停留在旧的轻量页头语法。

### 4.15 已整改样本: DragonTiger / FundFlow / IndustryAnalysis

`web/frontend/src/views/artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue`、`web/frontend/src/views/artdeco-pages/market-data-tabs/FundFlowAnalysis.vue` 与 `web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue` 原本都存在“既被独立路由使用、又被容器页内嵌，但页面承载没有显式区分”的问题；当前已完成：

- `DragonTigerAnalysis.vue` 与 `FundFlowAnalysis.vue` 都已支持独立路由工作台和 `ArtDecoMarketData.vue` 内嵌退化态。
- `ArtDecoIndustryAnalysis.vue` 已支持独立路由工作台和 `ArtDecoTradingCenter.vue` 内嵌退化态。
- 三页都补足了独立路由态的 `hero + stats + content shell` 结构。
- 三页样式入口都已切到 `@use` 主链，不再延续旧的局部页头写法。

这意味着市场数据域中“既能独立打开、又能作为内容面板复用”的页面现在已经具备清晰的双态承载语法。

### 4.16 已整改样本: ETF / Auction / Concept / DataQuality Embedded Modules

`web/frontend/src/views/artdeco-pages/market-data-tabs/ETFAnalysis.vue`、`web/frontend/src/views/artdeco-pages/market-data-tabs/AuctionAnalysis.vue` 与 `web/frontend/src/views/artdeco-pages/market-data-tabs/ConceptAnalysis.vue` 虽然不是独立路由页，但仍承担 `ArtDecoMarketData.vue` 内容面板内的主要域模块职责；当前已完成：

- 三个模块都补足了内部 `module header + meta + stats` 的工作台化表达。
- ETF 模块已从硬编码概览收敛到基于传入排行数据的动态摘要。
- Auction 模块已从静态概览收敛到基于传入数据的轻量指标。
- Concept 模块已从“双卡片直接并排”收敛到带模块 header 和摘要的概念热度面板。
- `DataQualityPanel.vue` 已从单卡片指标块收敛到带模块 header 和源健康摘要的治理模块。

这意味着市场数据工作台内的核心 domain 模块现在也开始遵循统一的内部编排语言，而不再只是“把卡片堆进去”。

### 4.17 已整改样本: RealtimeMonitor / MarketAnalysis Placeholder

`web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoRealtimeMonitor.vue` 与 `web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoMarketAnalysis.vue` 仍然不是完整业务实现，但当前已经完成：

- 历史失效样式和裸占位内容已被标准化的 ArtDeco 占位壳层替换。
- 占位态现在也具备清晰的 `eyebrow + title + subtitle + meta + next-step cards` 结构。
- 后续即使继续实现真实实时监控/市场分析能力，也会在统一工作台壳层内展开，而不是从杂乱占位重新起步。

这意味着市场数据域中“尚未完成实现”的页面也开始纳入当前的页面编排治理，而不再持续输出旧风格占位。

### 4.18 已整改样本: History / Position / Performance Placeholder

`web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoHistoryView.vue`、`web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPositionMonitor.vue` 与 `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPerformanceAnalysis.vue` 当前仍不是完整业务实现，但已经完成：

- 历史失效样式和裸占位内容已被标准化的 ArtDeco 占位工作台替换。
- 三页占位态现在都具备一致的 `eyebrow + title + subtitle + meta + next-step cards` 结构。
- 后续即使继续落地真实交易历史、头寸监控或绩效分析能力，也会在统一的交易工作台壳层内展开。

这意味着交易域中尚未落地的页面不再继续扩散旧样式债，而是已经进入统一的占位治理基线。

### 4.19 已整改样本: SignalsView

`web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoSignalsView.vue` 原本已经有真实数据与执行逻辑，但页面承载仍更接近“功能块堆叠”；当前已完成：

- 独立路由态补足 `hero + stats + content shell` 工作台骨架。
- `TradingCenter` 内嵌态会退化到内容面板，不再重复叠出完整舞台。
- 信号数量、买卖分布和高置信度数量现在被显式提升到页面级 stats strip。
- 现有的信号总览、过滤器、实时列表、质量分析和历史追踪模块被纳入统一内容壳层编排。

它现在已经从“信号功能页”提升为交易域里的标准信号工作台。

### 4.20 已整改样本: TradingHistory / TradingPositions

`web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue` 与 `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue` 原本虽然已有真实数据装配逻辑，但页面承载仍停留在“内嵌表格组件”层级；当前已完成：

- 两页都补足了独立路由态的 `hero + stats + content shell` 工作台骨架。
- 两页在 `ArtDecoTradingManagement.vue` 内嵌时会退化成内容面板，不再重复叠出完整舞台。
- 交易历史页现在将总笔数、已成交、待成交和成交总额提升为页面级 stats。
- 持仓页现在将持仓标的数、盈利标的数、组合市值和最高仓位提升为页面级 stats。

它们现在已经从“表格型子组件”提升为交易域里的标准历史/持仓工作台。

## 5. 当前最突出的页面级反模式

### 5.1 Emoji 图标进入 ArtDeco 页面骨架

此问题在第一轮整改中已被直接处理。以下页面和数据源层原本存在 emoji 图标残留：

- `web/frontend/src/views/artdeco-pages/ArtDecoMarketData.vue`
- `web/frontend/src/views/artdeco-pages/ArtDecoDataAnalysis.vue`
- `web/frontend/src/composables/useArtDecoSettings.ts`
- `web/frontend/src/composables/market/useDataAnalysis.ts`

当前这些入口已统一切换到 `ArtDecoIcon` 语义。

### 5.2 只做 tab bar，不做 tabs shell

多个页面虽然有 tab，但缺少更完整的 `tabs-shell + trace/meta rail + content shell` 结构。

项目里其实已有现成模式：

- `web/frontend/src/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue`

说明不是缺能力，而是页面没有统一执行。

### 5.3 页面头部回退成通用后台头

以下页面原本偏离共享头部模式：

- `web/frontend/src/views/artdeco-pages/ArtDecoSettings.vue`
- `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue`

当前这两个页面都已经补足等价强度的页面仪式感。

### 5.4 兼容层气质外溢到页面体验

`web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue` 原本仍通过 `@import '@/styles/artdeco-main.css';` 进入旧兼容入口。

当前这一点已处理：它已切换到主 token 链，不再依赖 `artdeco-main.css`。

## 6. 建议的统一页面骨架

后续页面整改应优先收敛到下列顺序，而不是继续自由拼接：

1. `ArtDecoHeader` 或 `ArtDecoPageTemplate` 头部主舞台
2. meta rail / trace rail / request rail
3. stats strip 或 section divider
4. tabs shell
5. content shell
6. panel 内部再放 domain 组件

换句话说：

- 先做页面舞台，再做业务面板。
- 先建立 ArtDeco 轴线，再安排 dashboard 内容。
- 不要反过来把业务组件铺满，再希望它“看起来像 ArtDeco”。

## 7. 建议整改优先级

### P2-A: 第一波优先页

1. `web/frontend/src/views/artdeco-pages/ArtDecoMarketData.vue`
   状态: 已完成
2. `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue`
   状态: 已完成
3. `web/frontend/src/views/artdeco-pages/ArtDecoTradingCenter.vue`
   状态: 已完成

### P2-B: 第二波提升页

4. `web/frontend/src/views/artdeco-pages/ArtDecoTechnicalAnalysis.vue`
5. `web/frontend/src/views/artdeco-pages/ArtDecoSettings.vue`
6. `web/frontend/src/views/artdeco-pages/ArtDecoDataAnalysis.vue`

这组页面状态：已完成第一轮提升。

### P2-C: 基础设施收口

7. `web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue`
   状态: 已完成
8. `web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoMarketOverview.vue`
   状态: 已完成

## 8. 审查结论

当前项目已经完成了：

- token 真值统一
- 字体主链统一
- 兼容层边界显式化
- 页面级 P2 第一轮治理
- 页面级第二轮治理的首批补强
- 风险控制页已纳入第二轮页面治理基线

下一阶段真正该做的，不再是补救核心入口页，而是：

- 对剩余未专项治理页面做第二轮一致性审查
- 将已证明有效的页面骨架进一步模板化
- 继续缩小历史兼容层影响范围

最重要的一句判断是：

> 当前项目的 ArtDeco Fintech 已经在核心页面层基本成立，后续重点是把这套页面编排语言继续扩展到剩余页面，并收敛为更强的共享模板能力。

## 9. 执行门禁

根据 `architecture/STANDARDS.md` 的方案先行准则：

- 本文档作为页面级 UI/UX 整改的审查与方案依据。
- 若要进入实际页面重构，应先基于本审查结果确认整改范围与优先顺序，再执行代码修改。

---

**相关文档**

- `docs/guides/web/ARTDECO_SCSS_GOVERNANCE_BASELINE.md`
- `docs/guides/web/ARTDECO_FINTECH_UNIFIED_SPEC.md`
- `docs/guides/web/ARTDECO_FINTECH_IMPLEMENTATION_AUDIT.md`
- `docs/guides/web/ARTDECO_PAGE_TEMPLATE_GUIDE.md`
