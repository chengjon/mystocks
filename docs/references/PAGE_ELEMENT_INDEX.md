# MyStocks 页面与元素编号手册

> 版本: v2.1 | 生成日期: 2026-07-15 | 数据来源: `web/frontend/src/router/index.ts` + 各页面 `.vue` 源码
> 编号规则: 一级 ABCD... 二级 1234... 元素 NN-NN 按 DOM 出现顺序
>
> **标注图索引**: http://localhost:3020/ELEMENT_MAPS.html — 分组导航 → 点击进入各页标注图
> 浏览器打开即可看到该页面所有元素的编号、类型和名称，颜色按类型区分

---

## 一、页面编号对照表

| 编号 | 路由 | 页面标题 | 源码组件 |
|------|------|---------|---------|
| **A** | `/dashboard` | **交易室** | `ArtDecoDashboard.vue` |
| **B** | `/market/*` | **市场行情** | |
| B1 | `/market/realtime` | 实时行情 | `market/Realtime.vue` |
| B2 | `/market/technical` | K线分析 | `market/Technical.vue` |
| B3 | `/market/lhb` | 龙虎榜 | `market/LHB.vue` |
| **C** | `/stock`, `/analysis/*` | **股票** | |
| C1 | `/stock` | 股票列表 | `Stock.vue` |
| C2 | `/analysis` | 数据分析 | `Analysis.vue` |
| C3 | `/analysis/industry-concept` | 行业概念分析 | `IndustryConceptAnalysis.vue` |
| **D** | `/data/*` | **数据分析** | |
| D1 | `/data/industry` | 板块动向 | `data/Industry.vue` |
| D2 | `/data/concept` | 概念动向 | `data/Concepts.vue` |
| D3 | `/data/fund-flow` | 资金流向 | `data/FundFlow.vue` |
| D4 | `/data/indicator` | 指标分析 | `ArtDecoDataAnalysis.vue` |
| **E** | `/watchlist/*` | **自选管理** | |
| E1 | `/watchlist/manage` | 组合管理 | `WatchlistManager.vue` |
| E2 | `/watchlist/signals` | 信号雷达 | `StrategySignalsTab.vue` |
| E3 | `/watchlist/screener` | 策略选股 | `Screener.vue` |
| **F** | `/strategy/*` | **策略管理** | |
| F1 | `/strategy/repo` | 策略仓库 | `ArtDecoStrategyManagement.vue` |
| F2 | `/strategy/parameters` | 策略参数 | `StrategyParametersTab.vue` |
| F3 | `/strategy/signals` | 策略信号 | `StrategySignalsTab.vue` |
| F4 | `/strategy/backtest` | 回测引擎 | `ArtDecoBacktestAnalysis.vue` |
| F5 | `/strategy/gpu` | 加速监控 | `BacktestGPU.vue` |
| F6 | `/strategy/opt` | 参数优化 | `ArtDecoStrategyOptimization.vue` |
| F7 | `/strategy/pos` | 仓位管理 | `ArtDecoTradingPositions.vue` |
| **G** | `/trade/*` | **交易管理** | |
| G1 | `/trade/positions` | 头寸管理 | `ArtDecoTradingPositions.vue` |
| G2 | `/trade/terminal` | 交易操作 | `TradingDashboard.vue` |
| G3 | `/trade/signals` | 信号监控 | `ArtDecoSignalsView.vue` |
| G4 | `/trade/portfolio` | 持仓透视 | `PortfolioOverviewTab.vue` |
| G5 | `/trade/history` | 历史对账 | `ArtDecoTradingHistory.vue` |
| **H** | `/risk/*` | **风险管理** | |
| H1 | `/risk/management` | 风险管理中心 | `ArtDecoRiskManagement.vue` |
| H2 | `/risk/overview` | 风险概览 | `RiskOverviewTab.vue` |
| H3 | `/risk/pnl` | 组合盈亏 | `PortfolioOverviewTab.vue` |
| H4 | `/risk/stop-loss` | 止损雷达 | `StopLossMonitorTab.vue` |
| H5 | `/risk/alerts` | 告警中心 | `ArtDecoRiskAlerts.vue` |
| H6 | `/risk/news` | 舆情预警 | `ArtDecoAnnouncementMonitor.vue` |
| **I** | `/system/*` | **系统设置** | |
| I1 | `/system/config` | 系统配置 | `ArtDecoSystemSettings.vue` |
| I2 | `/system/health` | 健康矩阵 | `SystemHealthTab.vue` |
| I3 | `/system/api` | API 终端 | `ArtDecoMonitoringDashboard.vue` |
| I4 | `/system/data` | 数据源管理 | `ArtDecoDataManagement.vue` |
| **J** | `/detail/:symbol/*` | **详情页** | |
| J1 | `/detail/graphics/:symbol` | 股票图形 | `KLineAnalysis.vue` |
| J2 | `/detail/news/:symbol` | 相关新闻 | `AnnouncementMonitor.vue` |
| **K** | `/login` | Login | `Login.vue` |
| **L** | `/*` | 404 Not Found | `NotFound.vue` |

> A–L 共 12 组，页面 A1–J2 共 38 个，加 K、L 共 **40 页**。

---

## 二、A1 交易室 (Dashboard)

> 源码: `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue` (518行)
> **标注图**: http://localhost:3020/A1_DASHBOARD_ELEMENT_MAP.html — 浏览器打开可看到 48 个编号标记在对应元素位置

### 2.1 页面头部区 (A1-01 ~ A1-06)

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| A1-01 | Header | QUANTIX 标题"QUANTIX" | 静态 |
| A1-02 | Header | 副标题"实时 洞察 策略 执行" | 静态 |
| A1-03 | Status | 市场状态指示(开盘/收盘/休市) | `marketStatus` |
| A1-04 | Badge | 策略运行中计数(如"3 策略运行中") | `activeStrategiesCount` |
| A1-05 | Badge | 今日收益(如"+1,234.56") | `todayPnLValue` |
| A1-06 | Button | 时钟显示 + "刷新数据"按钮 | `currentTime` + `refreshData()` |

### 2.2 元数据条 (A1-07 ~ A1-09)

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| A1-07 | Label | DATA: REAL 数据模式标签 | 静态 |
| A1-08 | Label | REQ 最近请求ID | `lastRequestId` |
| A1-09 | Label | TIME 请求处理耗时 | `displayProcessTime` |

### 2.3 市场资金流向概览卡片 (A1-10 ~ A1-15)

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| A1-10 | Card | 市场资金流向概览容器卡片 | — |
| A1-11 | Stat | 沪股通净流入(金额+较昨日变化,亿元) | `marketData.fundFlow.hgt` |
| A1-12 | Stat | 深股通净流入(金额+较昨日变化,亿元) | `marketData.fundFlow.sgt` |
| A1-13 | Stat | 北向资金总额(金额+本月累计) | `marketData.fundFlow.northTotal` |
| A1-14 | Stat | 主力净流入(金额+占比%) | `marketData.fundFlow.mainForce` |
| A1-15 | Chart | 资金流趋势图(ECharts折线,200px) | `fundFlowChartOption` |

### 2.4 主要市场指标卡片 (A1-16 ~ A1-20)

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| A1-16 | Card | 主要市场指标容器卡片 | — |
| A1-17 | Stat | 上证指数(指数值+涨跌幅%,金色发光) | `marketData.shanghai` |
| A1-18 | Stat | 深证成指(指数值+涨跌幅%,金色发光) | `marketData.shenzhen` |
| A1-19 | Stat | 创业板指(指数值+涨跌幅%,金色发光) | `marketData.chuangye` |
| A1-20 | Chart | 上证指数分时趋势(ECharts折线,200px) | `marketTrendOption` |

### 2.5 资金流向+市场状态卡片 (A1-21 ~ A1-26)

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| A1-21 | Card | 资金流向小卡片容器 | — |
| A1-22 | Stat | 北向资金(金额+涨跌幅%) | `marketData.northFund` |
| A1-23 | Gauge | 市场情绪(进度条0-100%+颜色) | `marketSentiment` |
| A1-24 | Card | 市场状态小卡片容器 | — |
| A1-25 | Stat | 涨跌家数(涨停数↑/跌停数↓) | `marketData.stocks` |
| A1-26 | Stat | 成交金额(市场总成交额) | `marketData.volume` |

### 2.6 技术指标概览可折叠面板 (A1-27 ~ A1-28)

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| A1-27 | Collapse | 技术指标概览可折叠面板 | `indicatorsExpanded` |
| A1-28 | List | 指标列表(名称/值/趋势信号) | `indicatorList` |

### 2.7 系统监控状态可折叠面板 (A1-29 ~ A1-30)

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| A1-29 | Collapse | 系统监控状态可折叠面板 | `monitoringExpanded` |
| A1-30 | List | 监控项列表(标签/值/状态正常或警告) | `systemHealth` |

### 2.8 内容网格区 (A1-31 ~ A1-48)

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| A1-31 | Card | 市场热度板块(ECharts热力图) | `heatmapOption` |
| A1-32 | Card | 资金流向热力图(ECharts热力图) | `capitalFlowHeatmapOption` |
| A1-33 | Card | 行业轮动雷达(ECharts雷达图) | `sectorRotationRadarOption` |
| A1-34 | Card | 一键压力测试面板 | — |
| A1-35 | Button | 执行压力测试按钮(点击触发本地估算) | `runOneClickStressTest()` |
| A1-36 | Stat | 预估最大回撤(%) | `stressTestResult.drawdown` |
| A1-37 | Stat | VaR(95%)(%) | `stressTestResult.var95` |
| A1-38 | Stat | 集中度风险(%) | `stressTestResult.concentrationRisk` |
| A1-39 | Card | 龙虎榜(ArtDecoLongHuBang组件) | 子组件内部数据 |
| A1-40 | Card | 大宗交易(ArtDecoBlockTrading组件) | 子组件内部数据 |
| A1-41 | Card | 资金流向持续排名(带Tab切换) | — |
| A1-42 | Tab | 排名Tab切换(板块/个股/ETF等) | `flowTabs` + `activeFlowTab` |
| A1-43 | List | 排名列表项(名称/代码/金额/涨跌幅) | `capitalFlowData` |
| A1-44 | Card | 我的股票池表现(带Tab切换) | — |
| A1-45 | Tab | 股票池Tab切换(今日/本周/本月等) | `poolTabs` + `activePoolTab` |
| A1-46 | List | 股票表现列表(名称/代码/价格/涨跌幅) | `topStocks` |
| A1-47 | Card | 快速导航卡片 | — |
| A1-48 | Link | 导航链接×6(市场行情/自选管理/数据分析/交易管理/策略中心/风险监控) | 静态 |

---

## 三、B 市场行情

### B1 实时行情

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| B1-01 | Header | 页面头部"实时行情工作台"+状态指示 | `pageStatusText` |
| B1-02 | Button | 刷新行情按钮(头部) | `fetchOverview` |
| B1-03 | Stat | 市场总成交额 | `marketData.totalAmount` |
| B1-04 | Stat | 市场情绪(涨色/跌色) | `marketData.mood` |
| B1-05 | Stat | 统计窗口(今日/3日/5日) | `activeWindow` |
| B1-06 | Stat | 市场范围(全市场/主板/创业板) | `activeBoard` |
| B1-07 | Filter | 时间窗口下拉(今日/3日/5日) | `activeWindow` v-model |
| B1-08 | Filter | 市场范围下拉(全市场/主板/创业板) | `activeBoard` v-model |
| B1-09 | Button | 刷新行情(工具栏) | `fetchOverview` |
| B1-10 | Card | 指数快照卡片 | — |
| B1-11 | Table | 指数快照表(指数/最新价/涨跌幅/成交额/换手率) | `indexData` |
| B1-12 | Card | 涨跌分布卡片 | — |
| B1-13 | Chart | 涨跌分布条形图(涨/平/跌三段) | `marketMood` |
| B1-14 | Stat | 市场情绪文本 | `marketMood` |

### B2 K线分析

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| B2-01 | Header | 页面头部"K线分析工作台"+状态指示 | `pageStatusText` |
| B2-02 | Button | 刷新K线按钮 | `loadKline` |
| B2-03 | Stat | 当前标的(如 000001) | `symbol` |
| B2-04 | Stat | 最新收盘价(涨跌色) | `klineData.close[-1]` |
| B2-05 | Stat | 最新开盘价 | `klineData.open[-1]` |
| B2-06 | Stat | 最新成交量(万) | `klineData.vol[-1]` |
| B2-07 | Chart | K线图占位(技术分析大图标+状态文本) | `klineChartOption` |
| B2-08 | Table | 原始K线数据表(DATE/OPEN/HIGH/LOW/CLOSE/VOL) | `klineData` |

### B3 龙虎榜

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| B3-01 | Header | 页面头部"龙虎榜工作台"+状态指示 | `pageStatusText` |
| B3-02 | Button | 刷新榜单按钮 | `fetchLHB` |
| B3-03 | Stat | 榜单条目数 | `lhbData.length` |
| B3-04 | Stat | 当前日期 | `selectedDate` |
| B3-05 | Stat | 当前榜单类型(买入/卖出/机构) | `activeListType` |
| B3-06 | Stat | 最高换手率 | `maxTurnover` |
| B3-07 | Card | 龙虎榜数据卡片 | — |
| B3-08 | Filter | 日期下拉(今日/昨日/前日) | `selectedDate` |
| B3-09 | Tab | 榜单筛选按钮组(买入/卖出/机构) | `activeListType` |
| B3-10 | Table | 龙虎榜表格(排名/交易日/股票/原因/买入/卖出/净买入/换手率) | `lhbData` |
| B3-11 | Alert | 错误提示条 | `fetchErrorMessage` |

---

## 四、C 股票

### C1 股票列表

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| C1-01 | Header | 页面头部"PORTFOLIO MANAGEMENT" | 静态 |
| C1-02 | Filter | 筛选栏(搜索/重置/切换) | `filterConfig` |
| C1-03 | Button | REFRESH DATA 按钮 | `refresh` |
| C1-04 | Card | 装饰卡片(含表格) | — |
| C1-05 | Badge | PORTFOLIO ASSETS 徽标 | 静态 |
| C1-06 | Stat | TOTAL STOCKS 总数 | `stocks.length` |
| C1-07 | Table | 股票表格(SYMBOL/NAME/PRICE/CHANGE/CHANGE%/VOLUME/MARKET) | `stocks` |
| C1-08 | Button | 行操作按钮(详情/自选) | 行数据 |
| C1-09 | Pagination | 分页组件(ElPagination) | `pagination` |

### C2 数据分析

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| C2-01 | Header | 页面头部+分析配置区 | — |
| C2-02 | Form | 股票代码输入 | `symbol` |
| C2-03 | Form | 日期范围选择 | `startDate/endDate` |
| C2-04 | Form | 分析周期选择(日/周/月) | `period` |
| C2-05 | Form | 指标复选框组(MA/MACD/RSI/KDJ/BOLL) | `selectedIndicators` |
| C2-06 | Button | 开始分析按钮 | `runAnalysis` |
| C2-07 | Button | 导出数据按钮 | `exportData` |
| C2-08 | Button | 重置按钮 | `reset` |
| C2-09 | Chart | 主图表区域(TimeSeriesChart) | `chartData` |
| C2-10 | Chart | 成交量图表(TimeSeriesChart) | `volumeData` |
| C2-11 | Table | 分析结果表格 | `analysisResult` |

### C3 行业概念分析

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| C3-01 | Header | 页面头部"行业概念分析" | 静态 |
| C3-02 | Tab | 行业/概念标签切换按钮组 | `activeTab` |
| C3-03 | Filter | 行业分类下拉(`<select>`) | `industryType` |
| C3-04 | Filter | 排序方式下拉(`<select>`) | `sortBy` |
| C3-05 | Stat | 行业数量统计 | `industryCount` |
| C3-06 | Stat | 概念数量统计 | `conceptCount` |
| C3-07 | Stat | 上涨行业数 | `upCount` |
| C3-08 | Stat | 下跌行业数 | `downCount` |
| C3-09 | Chart | 饼图(行业分布) | `pieData` |
| C3-10 | Chart | 柱状图(涨跌排名) | `barData` |
| C3-11 | Form | 搜索输入框 | `searchKeyword` |
| C3-12 | Table | 行业/概念列表表格 | `listData` |
| C3-13 | Pagination | 分页导航 | `pagination` |
| C3-14 | Button | 导出按钮 | `exportCSV` |

---

## 五、D 数据分析

### D1 板块动向

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| D1-01 | Header | 页面头部"板块动向工作台"+状态指示 | `pageStatusText` |
| D1-02 | Stat | 板块总数 | `boardData.length` |
| D1-03 | Stat | 上涨板块数(涨色) | `upBoardCount` |
| D1-04 | Stat | 下跌板块数(跌色) | `downBoardCount` |
| D1-05 | Stat | 主力净流入总额 | `totalNetInflow` |
| D1-06 | Card | 板块排名表格卡片 | — |
| D1-07 | Table | 板块排名表(名称/涨跌幅/资金净流入/领涨股) | `boardData` |
| D1-08 | Card | 行业轮动列表卡片 | — |
| D1-09 | List | 行业轮动列表(行业名+资金流向趋势条) | `rotationData` |

### D2 概念动向

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| D2-01 | Header | 页面头部"概念动向工作台"+状态指示 | `pageStatusText` |
| D2-02 | Stat | 概念总数 | `conceptData.length` |
| D2-03 | Stat | 上涨概念数(涨色) | `upConceptCount` |
| D2-04 | Stat | 下跌概念数(跌色) | `downConceptCount` |
| D2-05 | Stat | 当前排序方式 | `sortBy` |
| D2-06 | Card | 概念排名表格卡片 | — |
| D2-07 | Table | 概念排名表(名称/涨跌幅/趋势迷你柱) | `conceptData` |

### D3 资金流向

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| D3-01 | Header | 页面头部"资金流向工作台"+状态指示 | `pageStatusText` |
| D3-02 | Stat | 北向资金净流入 | `northFlow` |
| D3-03 | Stat | 主力资金净流入 | `mainFlow` |
| D3-04 | Stat | 散户资金净流入 | `retailFlow` |
| D3-05 | Stat | 资金流向趋势判断 | `flowTrend` |
| D3-06 | Chart | 资金流向趋势折线图 | `flowChartOption` |
| D3-07 | Tab | 筛选按钮组(全部/北向/主力/散户) | `flowFilter` |
| D3-08 | Filter | 排名方式下拉 | `rankBy` |
| D3-09 | Table | 资金流向排名表 | `flowRankData` |
| D3-10 | Alert | 错误提示条 | `fetchError` |

### D4 指标分析

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| D4-01 | Header | 页面头部"数据分析中心" | 静态 |
| D4-02 | Button | 刷新数据按钮 | `refresh` |
| D4-03 | Button | 执行筛选按钮 | `runScreener` |
| D4-04 | Stat | 可用指标数 | `availableIndicators.length` |
| D4-05 | Stat | 自定义指标数 | `customIndicators.length` |
| D4-06 | Stat | 筛选股票数(涨色) | `screenedStocks.length` |
| D4-07 | Stat | 今日筛选次数 | `todayScreenCount` |
| D4-08 | Stat | 符合条件数(涨跌色) | `qualifiedCount` |
| D4-09 | Tab | 主标签导航(指标库/编辑器/智能选股/筛选结果) | `activeMainTab` |
| D4-10 | SubPage | 指标库子页(分类/指标/筛选) | AnalysisIndicators |
| D4-11 | SubPage | 智能选股子页(筛选器/指标/操作符) | AnalysisScreener |
| D4-12 | SubPage | 筛选结果子页(表格:代码/名称/最新价/涨跌幅) | AnalysisResults |
| D4-13 | Card | 指标编辑器占位卡片 | — |

---

## 六、E 自选管理

### E1 组合管理

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| E1-01 | Stat | 组合数量统计卡 | `displayWatchlists.length` |
| E1-02 | Stat | 当前股票数统计卡 | `stocksCount` |
| E1-03 | Stat | 上涨家数统计卡 | `upCount` |
| E1-04 | Stat | 下跌家数统计卡 | `downCount` |
| E1-05 | Tab | Watchlist 标签按钮组(名称+股票数) | `displayWatchlists` |
| E1-06 | Button | "+" 添加清单按钮 | `handleAddList` |
| E1-07 | Button | 导入 JSON 按钮 | `handleImport` |
| E1-08 | Button | 导出 JSON 按钮 | `handleExport` |
| E1-09 | Card | 组合持仓明细卡片 | — |
| E1-10 | Table | 持仓明细表(列通过 columns prop 定义) | `displayCurrentStocks` |
| E1-11 | Button | 行删除按钮 | `handleRemoveStock` |

### E2 信号雷达（与 F3 策略信号共用组件）

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| E2-01 | Header | Hero 区域+元数据(REQ_ID/FOCUS/STATUS) | `lastRequestId` |
| E2-02 | Header | 页面头部"策略信号工作台"+副标题+状态 | `pageStatusText` |
| E2-03 | Button | 刷新信号按钮 | `fetchSignals` |
| E2-04 | Stat | 总信号数统计卡 | `signals.length` |
| E2-05 | Stat | 买入信号数统计卡 | `buySignalCount` |
| E2-06 | Stat | 卖出信号数统计卡 | `sellSignalCount` |
| E2-07 | Stat | 观望信号数统计卡 | `holdSignalCount` |
| E2-08 | Header | Content Shell "实时信号时间轴" | — |
| E2-09 | List | 信号时间轴列表(marker+类型标签+时间+股票+价格+策略) | `signals` |
| E2-10 | Card | 空态提示"当前暂无策略信号" | 空态 |

### E3 策略选股

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| E3-01 | Header | 页面头部+元数据 | — |
| E3-02 | Form | 搜索股票代码输入 | `searchCode` |
| E3-03 | Form | 搜索股票名称输入 | `searchName` |
| E3-04 | Filter | 市场类型下拉(A股/港股/美股) | `market` |
| E3-05 | Filter | 行业筛选下拉 | `industry` |
| E3-06 | Form | PE范围输入(min/max) | `peMin/peMax` |
| E3-07 | Form | 市值范围输入(min/max) | `mcapMin/mcapMax` |
| E3-08 | Form | 涨跌幅范围输入(min/max) | `changeMin/changeMax` |
| E3-09 | Button | 搜索/筛选按钮 | `doSearch` |
| E3-10 | Button | 重置按钮 | `reset` |
| E3-11 | Table | 筛选结果表格 | `results` |
| E3-12 | Pagination | 分页组件 | `pagination` |

---

## 七、F 策略管理

### F1 策略仓库

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| F1-01 | Header | Hero+元数据(REQ_ID/TIME/SOURCE) | `traceRequestId` |
| F1-02 | Header | 页面头部"策略管理工作台"+状态 | `pageStatusText` |
| F1-03 | Button | 刷新策略按钮 | `loadStrategies` |
| F1-04 | Stat | 策略总数统计卡 | `displayStrategies.length` |
| F1-05 | Stat | 活跃策略统计卡 | `activeCount` |
| F1-06 | Stat | 已暂停统计卡 | `pausedCount` |
| F1-07 | Stat | 异常统计卡 | `errorCount` |
| F1-08 | Form | 搜索输入(策略名称/ID/类型) | `keyword` |
| F1-09 | Filter | 状态筛选下拉(全部/活跃/暂停/停止/异常) | `statusFilter` |
| F1-10 | Table | 策略表格(策略/类型/状态/标的/回测/参数/操作) | `displayStrategies` |
| F1-11 | Button | 行操作按钮(启动/暂停/停止/详情) | 行数据 |

### F2 策略参数

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| F2-01 | Header | Hero+元数据 | `lastRequestId` |
| F2-02 | Header | 页面头部"策略参数工作台"+状态 | `pageStatusText` |
| F2-03 | Stat | 参数总数统计卡 | `parameters.length` |
| F2-04 | Stat | 当前策略统计卡 | `selectedStrategy.name` |
| F2-05 | Filter | 策略选择下拉 | `selectedStrategy` |
| F2-06 | Table | 参数表格(参数名/当前值/默认值/范围/类型/操作) | `parameters` |
| F2-07 | Button | 保存参数按钮 | `saveParameters` |
| F2-08 | Button | 恢复默认按钮 | `resetDefaults` |

### F3 策略信号（同 E2）

### F4 回测引擎

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| F4-01 | Header | Hero+元数据 | `traceRequestId` |
| F4-02 | Header | 页面头部"回测引擎工作台"+状态 | `pageStatusText` |
| F4-03 | Button | 运行回测按钮 | `runBacktest` |
| F4-04 | Button | 刷新历史按钮 | `loadHistory` |
| F4-05 | Stat | 回测次数统计卡 | `history.length` |
| F4-06 | Stat | 胜率统计卡 | `winRate` |
| F4-07 | Stat | 累计收益统计卡 | `totalReturn` |
| F4-08 | Stat | 最大回撤统计卡 | `maxDrawdown` |
| F4-09 | Form | 策略选择下拉 | `strategyId` |
| F4-10 | Form | 股票代码输入 | `symbol` |
| F4-11 | Form | 日期范围选择 | `startDate/endDate` |
| F4-12 | Form | 初始资金输入 | `initialCapital` |
| F4-13 | Chart | 收益曲线图 | `equityCurveOption` |
| F4-14 | Chart | 回撤曲线图 | `drawdownOption` |
| F4-15 | Table | 交易明细表 | `trades` |
| F4-16 | Table | 回测历史表 | `history` |

### F5 加速监控(GPU)

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| F5-01 | Header | 页面头部"GPU加速监控"+状态 | `gpuStatus` |
| F5-02 | Stat | GPU状态(可用/不可用) | `gpuStatus.available` |
| F5-03 | Stat | GPU型号 | `gpuStatus.model` |
| F5-04 | Stat | 加速倍数统计卡 | `accelerationRatio` |
| F5-05 | Stat | 性能提升统计卡 | `performanceGain` |
| F5-06 | Stat | 能效比统计卡 | `energyEfficiency` |
| F5-07 | Card | GPU状态卡片(名称/驱动/温度/利用率) | `gpuStatus` |
| F5-08 | Card | GPU内存卡片(已用/总/空闲+环进度) | `gpuStatus` |
| F5-09 | Card | GPU温度卡片(当前/最高/最低/平均) | `gpuStatus` |
| F5-10 | Card | 加速性能对比卡片 | — |
| F5-11 | Card | 控制面板(计算模式radio+监控频率select+运行基准/重置按钮) | — |
| F5-12 | Tab | 日志与告警标签(实时日志/性能指标) | `activeLogTab` |
| F5-13 | List | 实时日志列表 | `realtimeLogs` |

### F6 参数优化

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| F6-01 | Header | Hero+元数据 | `traceRequestId` |
| F6-02 | Header | 页面头部"策略优化工作台"+状态 | `pageStatusText` |
| F6-03 | Button | 刷新候选按钮 | `refreshOptimizationRows` |
| F6-04 | Stat | 候选总数统计卡 | `optimizationRows.length` |
| F6-05 | Stat | 当前筛选统计卡 | `displayedRows.length` |
| F6-06 | Stat | 异常策略统计卡 | `errorCandidateCount` |
| F6-07 | Stat | 当前焦点统计卡 | `optimizationFocusLabel` |
| F6-08 | Card | 优化候选卡片 | — |
| F6-09 | Info | 当前策略上下文条(ID/status/参数/回测/评分) | `selectedSnapshot` |
| F6-10 | Form | 搜索输入(策略名称/类型) | `keyword` |
| F6-11 | Filter | 状态筛选下拉 | `statusFilter` |
| F6-12 | Table | 优化候选表(策略/状态/参数/回测/评分/时间/回写操作) | `displayedRows` |
| F6-13 | Button | 回写按钮(管理/参数/回测) | writeback |
| F6-14 | Card | 优化合约摘要(策略ID/status/parameters/backtest/source) | `selectedSnapshot` |

### F7 仓位管理（同 G1）

---

## 八、G 交易管理

### G1 头寸管理

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| G1-01 | Header | Hero+元数据 | `displayRequestId` |
| G1-02 | Header | 页面头部"持仓工作台"+状态 | `pageStatusText` |
| G1-03 | Button | 刷新持仓按钮 | `loadPositions` |
| G1-04 | Stat | 持仓标的数统计卡 | `displayPositions.length` |
| G1-05 | Stat | 盈利标的数统计卡 | `positiveCount` |
| G1-06 | Stat | 组合市值统计卡(¥) | `totalMarketValue` |
| G1-07 | Stat | 最高仓位统计卡(%) | `highestWeight` |
| G1-08 | Card | 持仓明细卡片 | — |
| G1-09 | Table | 持仓表(股票/持股数/平均成本/当前价/市值/盈亏/盈亏%/仓位%) | `displayPositions` |
| G1-10 | Chart | 仓位百分比进度条(行内) | `positionPercent` |

### G2 交易操作

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| G2-01 | Header | 页面头部"实时交易监控仪表板" | 静态 |
| G2-02 | Button | 启动/停止交易按钮(红色/绿色切换) | `tradingActive` |
| G2-03 | Button | 刷新数据按钮 | `refreshData` |
| G2-04 | Button | 策略管理按钮(弹出Dialog) | `showStrategyDialog` |
| G2-05 | Button | 风险报告按钮(弹出Dialog) | `showRiskDialog` |
| G2-06 | Stat | 4个指标卡(循环:图标+数值+标签+变化值) | `metrics` |
| G2-07 | Card | 交易状态面板(交易状态/会话状态标签) | `tradingStatus` |
| G2-08 | Table | 策略表现表(策略名称/状态标签/性能指标/详情按钮) | `strategies` |
| G2-09 | Card | 市场数据快照(各symbol:价格/涨跌值/涨跌%) | `marketData` |
| G2-10 | Card | 风险监控面板(回撤/当日盈亏/活跃头寸/最后更新) | `riskMetrics` |
| G2-11 | Dialog | 策略管理对话框(Tab:添加/移除+Form+Table) | `showStrategyDialog` |
| G2-12 | Dialog | 风险报告对话框(Alert+指标详情+建议) | `showRiskDialog` |

### G3 信号监控

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| G3-01 | Header | 页面头部"交易信号工作台"+状态 | `pageStatusText` |
| G3-02 | Button | 刷新信号按钮 | `fetchSignals` |
| G3-03 | Stat | 可见信号统计卡 | `visibleCount` |
| G3-04 | Stat | 买入信号统计卡 | `buyCount` |
| G3-05 | Stat | 卖出信号统计卡 | `sellCount` |
| G3-06 | Stat | 高置信度统计卡 | `highConfidenceCount` |
| G3-07 | Chart | 信号监控概览(accuracy/responseTime/coverage/qualityScore) | ArtDecoSignalMonitoringOverview |
| G3-08 | Filter | 信号筛选栏(全部/买入/卖出/高置信度+导出+批量执行) | ArtDecoTradingSignalsControls |
| G3-09 | List | 信号列表 | ArtDecoTradingSignals |
| G3-10 | Chart | 信号质量指标(win/loss/avgProfit/avgLoss+趋势突破等) | ArtDecoSignalMonitoringMetrics |
| G3-11 | List | 信号执行历史(最近6条) | ArtDecoSignalHistory |

### G4 持仓透视

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| G4-01 | Header | 页面头部"组合资产工作台"+状态 | `pageStatusText` |
| G4-02 | Button | 刷新资产按钮 | `loadPortfolio` |
| G4-03 | Stat | 总资产统计卡(¥,金色) | `totalAsset` |
| G4-04 | Stat | 今日盈亏统计卡(¥+%,涨跌色) | `todayPnl` |
| G4-05 | Stat | 持仓数量统计卡 | `positionCount` |
| G4-06 | Stat | 再平衡建议统计卡 | `rebalanceCount` |
| G4-07 | Card | 资产大卡片(总资产+今日盈亏+金色边框) | — |
| G4-08 | List | Top Positions 持仓列表(名称/代码/市值/盈亏%) | `topPositions` |
| G4-09 | List | 绩效归因列表(权重%+收益贡献%) | `attribution` |
| G4-10 | List | 自动再平衡建议列表(当前%→目标%/加仓减仓) | `rebalanceSuggestions` |

### G5 历史对账

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| G5-01 | Header | 页面头部"交易历史工作台"+状态 | `pageStatusText` |
| G5-02 | Button | 刷新历史按钮 | `loadHistory` |
| G5-03 | Stat | 总笔数统计卡 | `history.length` |
| G5-04 | Stat | 已成交统计卡(涨色) | `executedCount` |
| G5-05 | Stat | 待成交统计卡 | `pendingCount` |
| G5-06 | Stat | 成交总额统计卡(¥) | `totalAmount` |
| G5-07 | Card | 交易历史记录卡片 | — |
| G5-08 | Table | 交易历史表(时间/股票/类型/价格/数量/金额/手续费/状态) | `history` |

---

## 九、H 风险管理

### H1 风险管理中心

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| H1-01 | Button | 导出按钮 | `export` |
| H1-02 | Button | 设置按钮 | `openSettings` |
| H1-03 | Chart | 风险统计网格 | ArtDecoRiskStatsGrid |
| H1-04 | Header | 页面头部"风险控制工作流"+副标题 | — |
| H1-05 | Tab | 导航标签栏(概览/个股,带图标) | `activeTab` |
| H1-06 | Panel | 风险概览面板 | ArtDecoRiskOverviewPanel |
| H1-07 | Panel | 个股风险面板 | ArtDecoRiskStockPanel |
| H1-08 | Footer | 页脚信息栏(更新频率+最后更新时间) | `lastUpdate` |

### H2 风险概览

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| H2-01 | Header | 页面头部"风险概览工作台"+状态 | `pageStatusText` |
| H2-02 | Button | 刷新概览按钮 | `loadOverview` |
| H2-03 | Stat | 规则总数统计卡 | `rules.length` |
| H2-04 | Stat | 启用规则统计卡(涨色) | `enabledCount` |
| H2-05 | Stat | 今日告警统计卡(跌色) | `alertCount` |
| H2-06 | Stat | 仓位集中度统计卡(%) | `concentration` |
| H2-07 | Tab | 子标签组(风险概览/规则清单/预警消息) | `subTab` |
| H2-08 | Card | 组合风险摘要卡片+表格(指标/当前值/状态) | — |
| H2-09 | Card | 风险规则卡片+表格(规则名/类型/目标/状态/优先级) | — |
| H2-10 | Card | 实时预警卡片+列表(等级/内容/时间) | `alerts` |

### H3 组合盈亏（同 G4）

### H4 止损雷达

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| H4-01 | Header | 页面头部"止损雷达工作台"+状态 | `pageStatusText` |
| H4-02 | Button | 刷新雷达按钮 | `loadStopLoss` |
| H4-03 | Stat | 监控标的数统计卡 | `monitoredStocks.length` |
| H4-04 | Stat | 已触发统计卡(跌色) | `triggeredCount` |
| H4-05 | Stat | 临界标的统计卡 | `nearLimitCount` |
| H4-06 | Stat | 最近止损距离统计卡(%) | `closestDistance` |
| H4-07 | Card | 止损监控卡网格(风险色条+代码/名称+当前价VS止损价+距离%) | `stopLossData` |
| H4-08 | Overlay | "TRIGGERED"覆盖层(已触发标的) | `triggered` |

### H5 告警中心

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| H5-01 | Header | 页面头部"风险告警工作台"+状态 | `pageStatusText` |
| H5-02 | Button | 刷新告警按钮 | `loadAlerts` |
| H5-03 | Stat | 规则总数统计卡 | `rules.length` |
| H5-04 | Stat | 启用规则统计卡 | `enabledCount` |
| H5-05 | Stat | 未读告警统计卡 | `unreadCount` |
| H5-06 | Stat | 高优先级统计卡(跌色) | `highPriorityCount` |
| H5-07 | Card | 摘要统计网格(规则总数/启用/未读/高优先级) | — |
| H5-08 | Table | 近期告警表(代码/名称/类型/等级tag/内容/时间) | `alerts` |
| H5-09 | Table | 规则列表表(规则名/类型/标的/启用状态tag/更新时间) | `rules` |

### H6 舆情预警

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| H6-01 | Header | 页面头部"公告与舆情工作台"+状态 | `pageStatusText` |
| H6-02 | Button | 刷新公告按钮 | `loadAnnouncements` |
| H6-03 | Stat | 公告总数统计卡 | `announcements.length` |
| H6-04 | Stat | 今日公告统计卡(涨色) | `todayCount` |
| H6-05 | Stat | 重要公告统计卡(跌色) | `importantCount` |
| H6-06 | Stat | 原文链接统计卡 | `linkCount` |
| H6-07 | Card | 摘要统计网格(公告总数/今日/重要/链接) | — |
| H6-08 | Table | 公告列表(代码/名称/类型/标题/重要性tag/时间/查看原文) | `announcements` |

---

## 十、I 系统设置

### I1 系统配置

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| I1-01 | Header | 页面头部+元数据栏(DATA/REQ_ID/TIME) | — |
| I1-02 | Button | 保存配置按钮 | `saveAll` |
| I1-03 | Tab | 标签页导航(数据源/系统设置/系统监控) | `activeTab` |
| I1-04 | Stat | 可用数据源统计卡(金色) | `4`(静态) |
| I1-05 | Stat | 健康状态统计卡(涨色,"3/4") | — |
| I1-06 | Stat | 今日调用统计卡(金色,"28,412") | — |
| I1-07 | Stat | 异常告警统计卡(跌色) | `2`(静态) |
| I1-08 | Card | 数据源优先级卡片+表格(数据源/优先级/状态/延迟/配额) | `dataSources` |
| I1-09 | Card | 核心参数卡片+表单(后端地址/回测并发/滑点/手续费) | `form` |
| I1-10 | Card | API性能监控卡片+表格(接口/QPS/P95延迟/错误率) | `apiMetrics` |

### I2 健康矩阵

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| I2-01 | Header | 面部+元数据(REQ_ID/STATUS/FOCUS) | — |
| I2-02 | Header | 页面头部"系统健康矩阵"+副标题+状态标签 | `healthStatus` |
| I2-03 | Button | 刷新矩阵按钮 | `refresh` |
| I2-04 | Stat | 服务状态统计卡 | `serviceStatus` |
| I2-05 | Stat | 服务名称统计卡 | `serviceName` |
| I2-06 | Stat | 版本统计卡 | `version` |
| I2-07 | Stat | 中间件项统计卡 | `middlewareCount` |
| I2-08 | Card | 后端服务状态卡片(状态指示灯+Service/Version行) | `backendHealth` |
| I2-09 | Card | 中间件层卡片(3个中间件+启用状态) | `middlewareStatus` |
| I2-10 | Card | 可观测性说明卡片(UUID v4跟踪) | — |

### I3 API 终端

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| I3-01 | Header | 面部+元数据(REQ_ID/STATUS/FOCUS) | — |
| I3-02 | Header | 页面头部"系统监控工作台"+状态 | — |
| I3-03 | Button | 刷新探针按钮 | `refresh` |
| I3-04 | Stat | 服务状态/名称/版本/中间件统计卡(同I2) | — |
| I3-05 | Card | 后端服务状态卡片(同I2) | — |
| I3-06 | Card | 中间件层卡片(中文版:性能追踪/统一响应/Redis缓存) | — |
| I3-07 | Button | 刷新按钮 | `refresh` |
| I3-08 | Button | 导出报告按钮 | `exportReport` |
| I3-09 | Card | 可观测性说明卡片(中文版) | — |

### I4 数据源管理

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| I4-01 | Header | 面部+元数据(REQ_ID/WRITES/FOCUS) | — |
| I4-02 | Header | 页面头部"数据源治理工作台"+状态 | — |
| I4-03 | Button | 刷新配置按钮 | `refresh` |
| I4-04 | Stat | 数据源总数统计卡 | `dataSources.length` |
| I4-05 | Stat | 已启用统计卡 | `enabledCount` |
| I4-06 | Stat | 写回能力统计卡 | `writeEnabled` |
| I4-07 | Stat | 当前请求统计卡 | `requestCount` |
| I4-08 | Card | 数据源配置卡片+表格(名称/状态Badge/端点/操作按钮) | `dataSources` |
| I4-09 | Button | 刷新按钮 | `refresh` |
| I4-10 | Button | 保存配置按钮 | `saveConfig` |
| I4-11 | Button | 恢复默认按钮 | `resetDefaults` |
| I4-12 | Card | 提示说明卡片 | 静态 |

---

## 十一、J 详情页

### J1 股票图形(K线分析)

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| J1-01 | Header | "K线指标分析面板"元数据(SYMBOL/PERIOD/POINTS) | route params |
| J1-02 | Form | 股票代码输入(带label) | `symbol` |
| J1-03 | Filter | 分析周期下拉(1分钟/5分钟/日线/周线) | `period` |
| J1-04 | Button | 开始分析按钮 | `runAnalysis` |
| J1-05 | Card | 技术指标概览卡片+指标网格(名称/数值/信号) | `indicatorList` |
| J1-06 | Card | 趋势分析卡片+折线图(ECharts) | `trendOption` |

### J2 相关新闻(公告监控)

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| J2-01 | Header | 页面标题"ANNOUNCEMENT MONITOR" | 静态 |
| J2-02 | Card | 功能说明横幅(实时获取/智能分析/自定义规则/重要提醒 tag) | — |
| J2-03 | Stat | 公告总数统计卡(Document图标) | `totalCount` |
| J2-04 | Stat | 今日公告统计卡(Calendar图标) | `todayCount` |
| J2-05 | Stat | 重要公告统计卡(Warning图标) | `importantCount` |
| J2-06 | Stat | 已触发统计卡(Bell图标) | `triggeredCount` |
| J2-07 | Card | 搜索筛选卡片+表单(代码/类型/重要性/日期范围/搜索/刷新) | `filters` |
| J2-08 | Table | 公告列表(代码/名称/标题/类型/重要性星级/情感tag/日期/来源/查看原文) | `announcements` |
| J2-09 | Pagination | 分页组件(10/20/50/100) | `pagination` |
| J2-10 | Card | 监控规则管理卡片+表格+新增按钮 | `rules` |
| J2-11 | Dialog | 规则编辑对话框+表单(名称/股票/关键词/重要性/通知/启用) | `ruleForm` |
| J2-12 | Card | 触发记录卡片+表格(规则/股票/公告/关键词/时间) | `triggerLogs` |

---

## 十二、K Login

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| K-01 | Header | "MYSTOCKS"品牌标题+"LOGIN"副标题 | 静态 |
| K-02 | Form | 登录表单 | — |
| K-03 | Form | 用户名输入(USERNAME) | `username` |
| K-04 | Form | 密码输入(PASSWORD) | `password` |
| K-05 | Button | SIGN IN 提交按钮(含loading spinner) | `handleLogin` |
| K-06 | List | 测试账号提示区(ADMIN/USER凭据) | 静态 |

---

## 十三、L 404

| 编号 | 类型 | 名称 | 数据来源 |
|------|------|------|---------|
| L-01 | Header | 大字号"404" | 静态 |
| L-02 | Header | "页面未找到"标题 | 静态 |
| L-03 | Text | 错误描述文字 | 静态 |
| L-04 | Button | 返回首页按钮(含房子SVG图标) | `router.push('/')` |
| L-05 | Image | 错误插图(SVG圆形警示图标) | 静态 |

---

## 十四、统计汇总

| 分组 | 页面数 | 元素总数 |
|------|--------|---------|
| A Dashboard | 1 | 48 |
| B 市场行情 | 3 | 34 |
| C 股票 | 3 | 36 |
| D 数据分析 | 4 | 39 |
| E 自选管理 | 3 | 32 |
| F 策略管理 | 7 | ~80 |
| G 交易管理 | 5 | ~52 |
| H 风险管理 | 6 | ~48 |
| I 系统设置 | 4 | 41 |
| J 详情页 | 2 | 18 |
| K Login | 1 | 6 |
| L 404 | 1 | 5 |
| **总计** | **40** | **~439** |

---

## 十五、使用约定

- **引用页面**: `A1`、`B3`、`F4` 等编号
- **引用元素**: `A1-17`(上证指数)、`B3-10`(龙虎榜表格)
- **批量引用**: `B1-B3`(市场行情全部)、`G4-03~G4-06`(持仓透视统计卡)
- **描述示例**: "B1-11 指数快照表格无数据，排查 `indexData` 接口"
- `(同G4)` 表示共用组件，元素编号一致
