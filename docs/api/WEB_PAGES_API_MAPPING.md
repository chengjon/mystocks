# MyStocks Web前端页面API对接完整映射表

## 概述

本文档详细记录了MyStocks Web前端所有页面的元素显示与后端API函数的对应关系，为开发和维护提供参考。

**前端端口**: 3000-3009 (当前: 3001)
**后端端口**: 8000-8009 (当前: 8000)
**数据模式**: 真实数据 (REAL)

---

## 1. 仪表盘 (`/dashboard`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 智能数据源指示器 | Dashboard.vue | dataMode | `/api/data-quality/mode` | `dashboardApi.getDataMode()` |
| 总资产 | Dashboard.vue | totalAssets | `/api/v1/portfolio/summary` | `dashboardApi.getPortfolioSummary()` |
| 可用资金 | Dashboard.vue | availableCash | `/api/v1/portfolio/summary` | `dashboardApi.getPortfolioSummary()` |
| 持仓价值 | Dashboard.vue | positionValue | `/api/v1/portfolio/summary` | `dashboardApi.getPortfolioSummary()` |
| 总盈亏 | Dashboard.vue | totalPnL | `/api/v1/portfolio/summary` | `dashboardApi.getPortfolioSummary()` |
| 市场热度标签页 | Dashboard.vue | marketHeatData | `/api/market/heatmap` | `marketApi.getHeatmap()` |
| 领涨板块数据 | Dashboard.vue | leadingSectors | `/api/market/sector-leaders` | `marketApi.getSectorLeaders()` |
| 市场分布图表 | Dashboard.vue | marketDistribution | `/api/market/distribution` | `marketApi.getDistribution()` |
| 资金流向数据 | Dashboard.vue | fundFlowData | `/api/market/fund-flow` | `marketApi.getFundFlow()` |
| 行业资金流向图 | Dashboard.vue | industryFundFlow | `/api/market/industry-fund-flow` | `marketApi.getIndustryFundFlow()` |
| 板块表现表格 | Dashboard.vue | sectorPerformance | `/api/market/sector-performance` | `marketApi.getSectorPerformance()` |

---

## 2. 市场行情

### 2.1 实时行情 (`/market`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 总资产显示 | Market.vue | totalAssets | `/api/v1/portfolio/summary` | `dataApi.getMarketOverview()` |
| 可用资金显示 | Market.vue | availableCash | `/api/v1/portfolio/summary` | `dataApi.getMarketOverview()` |
| 持仓价值显示 | Market.vue | positionValue | `/api/v1/portfolio/summary` | `dataApi.getMarketOverview()` |
| 总盈亏显示 | Market.vue | totalPnL | `/api/v1/portfolio/summary` | `dataApi.getMarketOverview()` |
| 交易次数统计 | Market.vue | tradeStats | `/api/v1/trading/statistics` | `dataApi.getTradingStats()` |
| 资产分布数据 | Market.vue | assetDistribution | `/api/v1/portfolio/distribution` | `dataApi.getAssetDistribution()` |
| 持仓信息表格 | Market.vue | positions | `/api/v1/positions` | `dataApi.getPositions()` |

### 2.2 TDX行情 (`/tdx-market`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| TDX实时数据 | TdxMarket.vue | tdxRealTime | `/api/tdx/realtime` | `tdxApi.getRealTimeData()` |
| TDX历史K线 | TdxMarket.vue | tdxKline | `/api/tdx/kline` | `tdxApi.getKlineData()` |
| TDX分时图 | TdxMarket.vue | tdxIntraday | `/api/tdx/intraday` | `tdxApi.getIntradayData()` |

---

## 3. 市场数据

### 3.1 资金流向 (`/market-data/fund-flow`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 搜索表单数据 | FundFlowPanel.vue | searchForm | - | 本地状态管理 |
| 资金流向数据表 | FundFlowPanel.vue | fundFlowData | `/api/market/fund-flow` | `marketApi.getFundFlow()` |
| 交易日期列 | FundFlowPanel.vue | data[].date | `/api/market/fund-flow` | `marketApi.getFundFlow()` |
| 时间周期列 | FundFlowPanel.vue | data[].period | `/api/market/fund-flow` | `marketApi.getFundFlow()` |
| 主力净流入列 | FundFlowPanel.vue | data[].mainNetInflow | `/api/market/fund-flow` | `marketApi.getFundFlow()` |
| 主力净占比列 | FundFlowPanel.vue | data[].mainNetRatio | `/api/market/fund-flow` | `marketApi.getFundFlow()` |
| 散户净流入列 | FundFlowPanel.vue | data[].retailNetInflow | `/api/market/fund-flow` | `marketApi.getFundFlow()` |
| 散户净占比列 | FundFlowPanel.vue | data[].retailNetRatio | `/api/market/fund-flow` | `marketApi.getFundFlow()` |

### 3.2 ETF行情 (`/market-data/etf`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| ETF列表数据 | ETFDataTable.vue | etfList | `/api/market/etf/list` | `marketApi.getETFList()` |
| ETF代码列 | ETFDataTable.vue | data[].code | `/api/market/etf/list` | `marketApi.getETFList()` |
| ETF名称列 | ETFDataTable.vue | data[].name | `/api/market/etf/list` | `marketApi.getETFList()` |
| ETF价格列 | ETFDataTable.vue | data[].price | `/api/market/etf/list` | `marketApi.getETFList()` |
| ETF涨跌幅列 | ETFDataTable.vue | data[].changePct | `/api/market/etf/list` | `marketApi.getETFList()` |
| ETF成交额列 | ETFDataTable.vue | data[].turnover | `/api/market/etf/list` | `marketApi.getETFList()` |

### 3.3 竞价抢筹 (`/market-data/chip-race`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 抢筹数据表 | ChipRaceTable.vue | chipRaceData | `/api/market/chip-race` | `marketApi.getChipRace()` |
| 股票代码列 | ChipRaceTable.vue | data[].code | `/api/market/chip-race` | `marketApi.getChipRace()` |
| 股票名称列 | ChipRaceTable.vue | data[].name | `/api/market/chip-race` | `marketApi.getChipRace()` |
| 竞价金额列 | ChipRaceTable.vue | data[].amount | `/api/market/chip-race` | `marketApi.getChipRace()` |
| 竞价比例列 | ChipRaceTable.vue | data[].ratio | `/api/market/chip-race` | `marketApi.getChipRace()` |

### 3.4 龙虎榜 (`/market-data/lhb`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 龙虎榜数据 | LongHuBangTable.vue | lhbData | `/api/market/lhb` | `marketApi.getLHB()` |
| 营业部名称列 | LongHuBangTable.vue | data[].broker | `/api/market/lhb` | `marketApi.getLHB()` |
| 买入金额列 | LongHuBangTable.vue | data[].buyAmount | `/api/market/lhb` | `marketApi.getLHB()` |
| 卖出金额列 | LongHuBangTable.vue | data[].sellAmount | `/api/market/lhb` | `marketApi.getLHB()` |
| 净买入额列 | LongHuBangTable.vue | data[].netAmount | `/api/market/lhb` | `marketApi.getLHB()` |

### 3.5 问财筛选 (`/market-data/wencai`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 查询结果列表 | WencaiPanelV2.vue | queryResults | `/api/market/wencai/query` | `marketApi.getWencaiQuery()` |
| 预定义模板 | WencaiPanelV2.vue | templates | `/api/market/wencai/templates` | `marketApi.getWencaiTemplates()` |
| 查询历史 | WencaiPanelV2.vue | queryHistory | `/api/market/wencai/history` | `marketApi.getWencaiHistory()` |
| 查询统计 | WencaiPanelV2.vue | queryStats | `/api/market/wencai/stats` | `marketApi.getWencaiStats()` |

---

## 4. 股票管理

### 4.1 股票列表 (`/stocks`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 股票列表数据 | Stocks.vue | stocksList | `/api/data/stocks/basic` | `dataApi.getStocksBasic()` |
| 股票搜索框 | Stocks.vue | searchKeyword | `/api/data/stocks/search` | `dataApi.searchStocks()` |
| 股票代码列 | Stocks.vue | data[].symbol | `/api/data/stocks/basic` | `dataApi.getStocksBasic()` |
| 股票名称列 | Stocks.vue | data[].name | `/api/data/stocks/basic` | `dataApi.getStocksBasic()` |
| 当前价格列 | Stocks.vue | data[].price | `/api/data/stocks/basic` | `dataApi.getStocksBasic()` |
| 涨跌幅列 | Stocks.vue | data[].change_pct | `/api/data/stocks/basic` | `dataApi.getStocksBasic()` |
| 成交量列 | Stocks.vue | data[].volume | `/api/data/stocks/basic` | `dataApi.getStocksBasic()` |

### 4.2 股票详情 (`/stock-detail/:symbol`) - 已在前面详细列出

---

## 5. 数据分析

### 5.1 数据分析概览 (`/analysis`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 分析概览数据 | Analysis.vue | overviewData | `/api/analysis/overview` | `analysisApi.getOverview()` |
| 技术分析数据 | Analysis.vue | technicalData | `/api/analysis/technical` | `analysisApi.getTechnical()` |
| 基本面数据 | Analysis.vue | fundamentalData | `/api/analysis/fundamental` | `analysisApi.getFundamental()` |
| 资金流向分析 | Analysis.vue | flowAnalysis | `/api/analysis/flow-analysis` | `analysisApi.getFlowAnalysis()` |

### 5.2 行业概念分析 (`/analysis/industry-concept`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 行业数据 | IndustryConceptAnalysis.vue | industryData | `/api/data/stocks/industries` | `dataApi.getStocksIndustries()` |
| 概念数据 | IndustryConceptAnalysis.vue | conceptData | `/api/data/stocks/concepts` | `dataApi.getStocksConcepts()` |
| 行业涨幅榜 | IndustryConceptAnalysis.vue | industryRanking | `/api/analysis/industry-ranking` | `analysisApi.getIndustryRanking()` |
| 概念热度图 | IndustryConceptAnalysis.vue | conceptHeatmap | `/api/analysis/concept-heatmap` | `analysisApi.getConceptHeatmap()` |

---

## 6. 技术分析

### 6.1 技术分析 (`/technical`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 股票搜索结果 | TechnicalAnalysis.vue | searchResults | `/api/data/stocks/search` | `dataApi.searchStocks()` |
| K线图数据 | TechnicalAnalysis.vue | klineData | `/api/market/kline` | `marketApi.getKline()` |
| 技术指标数据 | TechnicalAnalysis.vue | indicators | `/api/technical/{symbol}/indicators` | `technicalApi.getIndicators()` |
| 趋势指标 | TechnicalAnalysis.vue | trendIndicators | `/api/technical/{symbol}/trend` | `technicalApi.getTrendIndicators()` |
| 动量指标 | TechnicalAnalysis.vue | momentumIndicators | `/api/technical/{symbol}/momentum` | `technicalApi.getMomentumIndicators()` |
| 波动率指标 | TechnicalAnalysis.vue | volatilityIndicators | `/api/technical/{symbol}/volatility` | `technicalApi.getVolatilityIndicators()` |
| 成交量指标 | TechnicalAnalysis.vue | volumeIndicators | `/api/technical/{symbol}/volume` | `technicalApi.getVolumeIndicators()` |
| 交易信号 | TechnicalAnalysis.vue | signals | `/api/technical/{symbol}/signals` | `technicalApi.getSignals()` |

### 6.2 指标库 (`/indicators`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 指标总数统计 | IndicatorLibrary.vue | totalIndicators | `/api/technical/indicators/registry` | `technicalApi.getIndicatorRegistry()` |
| 指标分类统计 | IndicatorLibrary.vue | categoryStats | `/api/technical/indicators/registry` | `technicalApi.getIndicatorRegistry()` |
| 指标搜索结果 | IndicatorLibrary.vue | searchResults | `/api/technical/indicators/search` | `technicalApi.searchIndicators()` |
| 指标详情 | IndicatorLibrary.vue | indicatorDetail | `/api/technical/indicators/{id}` | `technicalApi.getIndicatorDetail()` |
| 缩写字段 | IndicatorLibrary.vue | data[].abbreviation | `/api/technical/indicators/registry` | `technicalApi.getIndicatorRegistry()` |
| 全称字段 | IndicatorLibrary.vue | data[].fullName | `/api/technical/indicators/registry` | `technicalApi.getIndicatorRegistry()` |
| 中文名字段 | IndicatorLibrary.vue | data[].chineseName | `/api/technical/indicators/registry` | `technicalApi.getIndicatorRegistry()` |
| 分类标签 | IndicatorLibrary.vue | data[].categories | `/api/technical/indicators/registry` | `technicalApi.getIndicatorRegistry()` |
| 描述字段 | IndicatorLibrary.vue | data[].description | `/api/technical/indicators/registry` | `technicalApi.getIndicatorRegistry()` |
| 参数表格 | IndicatorLibrary.vue | data[].parameters | `/api/technical/indicators/registry` | `technicalApi.getIndicatorRegistry()` |
| 输出字段列表 | IndicatorLibrary.vue | data[].outputFields | `/api/technical/indicators/registry` | `technicalApi.getIndicatorRegistry()` |
| 参考线列表 | IndicatorLibrary.vue | data[].referenceLines | `/api/technical/indicators/registry` | `technicalApi.getIndicatorRegistry()` |

---

## 7. 风险监控

### 7.1 风险监控 (`/risk`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 风险仪表盘 | RiskMonitor.vue | dashboard | `/api/v1/risk/dashboard` | `riskApi.getDashboard()` |
| VaR/CVaR数据 | RiskMonitor.vue | varCvar | `/api/v1/risk/var-cvar` | `riskApi.getVarCvar()` |
| Beta系数 | RiskMonitor.vue | beta | `/api/v1/risk/beta` | `riskApi.getBeta()` |
| 风险指标历史 | RiskMonitor.vue | metricsHistory | `/api/v1/risk/metrics/history` | `riskApi.getMetricsHistory()` |
| 风险预警 | RiskMonitor.vue | alerts | `/api/v1/risk/alerts` | `riskApi.getAlerts()` |

### 7.2 公告监控 (`/announcement`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 公告列表 | AnnouncementMonitor.vue | announcements | `/api/announcements` | `announcementApi.getAnnouncements()` |
| 重要公告 | AnnouncementMonitor.vue | importantNews | `/api/announcements/important` | `announcementApi.getImportant()` |
| 公告分类 | AnnouncementMonitor.vue | categories | `/api/announcements/categories` | `announcementApi.getCategories()` |

---

## 8. 实时监控 (`/realtime`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| SSE连接状态 | RealTimeMonitor.vue | sseStatus | `/api/v1/sse/status` | `sseApi.getStatus()` |
| 实时推送数据 | RealTimeMonitor.vue | realtimeData | SSE Event Source | `sseApi.connect()` |
| 训练进度 | RealTimeMonitor.vue | trainingProgress | `/api/v1/sse/events` | `sseApi.subscribeTraining()` |
| 回测进度 | RealTimeMonitor.vue | backtestProgress | `/api/v1/sse/events` | `sseApi.subscribeBacktest()` |
| 风险告警 | RealTimeMonitor.vue | riskAlerts | `/api/v1/sse/events` | `sseApi.subscribeAlerts()` |
| 系统消息 | RealTimeMonitor.vue | systemMessages | `/api/v1/sse/events` | `sseApi.subscribeSystem()` |
| SSE连接测试 | RealTimeMonitor.vue | testResult | `/api/v1/sse/test` | `sseApi.testConnection()` |
| 数据推送测试 | RealTimeMonitor.vue | pushResult | `/api/v1/sse/push-test` | `sseApi.testPush()` |
| 错误模拟 | RealTimeMonitor.vue | errorResult | `/api/v1/sse/error-test` | `sseApi.testError()` |

---

## 9. 交易管理 (`/trade`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 交易表单 | TradeManagement.vue | tradeForm | `/api/v1/trade/execute` | `tradeApi.executeTrade()` |
| 交易历史 | TradeManagement.vue | tradeHistory | `/api/v1/trade/history` | `tradeApi.getHistory()` |
| 持仓信息 | TradeManagement.vue | positions | `/api/v1/positions` | `tradeApi.getPositions()` |
| 订单状态 | TradeManagement.vue | orderStatus | `/api/v1/trade/orders` | `tradeApi.getOrders()` |
| 可用资金 | TradeManagement.vue | availableCash | `/api/v1/portfolio/cash` | `tradeApi.getAvailableCash()` |

---

## 10. 量化策略

### 10.1 策略管理 (`/strategy`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 策略列表 | StrategyList.vue | strategies | `/api/v1/strategy/strategies` | `strategyApi.getStrategies()` |
| 策略创建 | StrategyManagement.vue | createForm | `/api/v1/strategy/strategies` | `strategyApi.createStrategy()` |
| 策略详情 | StrategyManagement.vue | strategyDetail | `/api/v1/strategy/strategies/{id}` | `strategyApi.getStrategy()` |
| 策略更新 | StrategyManagement.vue | updateForm | `/api/v1/strategy/strategies/{id}` | `strategyApi.updateStrategy()` |
| 策略删除 | StrategyManagement.vue | deleteResult | `/api/v1/strategy/strategies/{id}` | `strategyApi.deleteStrategy()` |

#### 子页面功能

| 子页面 | 元素 | 组件位置 | API端点 | 对接函数 |
|-------|------|---------|---------|----------|
| 单次运行 | 执行按钮 | SingleRun.vue | `/api/strategy/run/single` | `strategyApi.runSingle()` |
| 批量扫描 | 扫描配置 | BatchScan.vue | `/api/strategy/run/batch` | `strategyApi.runBatch()` |
| 结果查询 | 查询表单 | ResultsQuery.vue | `/api/strategy/results` | `strategyApi.getResults()` |
| 统计分析 | 收益图表 | StatsAnalysis.vue | `/api/strategy/stats/summary` | `strategyApi.getStats()` |

### 10.2 回测分析 (`/backtest`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 回测配置 | BacktestAnalysis.vue | backtestConfig | `/api/v1/strategy/backtest/run` | `strategyApi.runBacktest()` |
| 回测结果 | BacktestAnalysis.vue | backtestResults | `/api/v1/strategy/backtest/results` | `strategyApi.getBacktestResults()` |
| 回测图表 | BacktestAnalysis.vue | chartData | `/api/v1/strategy/backtest/chart-data` | `strategyApi.getBacktestChartData()` |
| 回测报告 | BacktestAnalysis.vue | reportData | `/api/v1/strategy/backtest/report` | `strategyApi.getBacktestReport()` |

---

## 11. 任务管理 (`/tasks`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 任务列表 | TaskManagement.vue | tasks | `/api/v1/tasks` | `taskApi.getTasks()` |
| 任务创建 | TaskManagement.vue | createTaskForm | `/api/v1/tasks` | `taskApi.createTask()` |
| 任务状态 | TaskManagement.vue | taskStatus | `/api/v1/tasks/{id}/status` | `taskApi.getTaskStatus()` |
| 任务日志 | TaskManagement.vue | taskLogs | `/api/v1/tasks/{id}/logs` | `taskApi.getTaskLogs()` |
| 任务执行 | TaskManagement.vue | executeResult | `/api/v1/tasks/{id}/execute` | `taskApi.executeTask()` |

---

## 12. 系统设置 (`/settings`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 用户配置 | Settings.vue | userConfig | `/api/v1/settings/user` | `settingsApi.getUserSettings()` |
| 系统配置 | Settings.vue | systemConfig | `/api/v1/settings/system` | `settingsApi.getSystemSettings()` |
| 主题设置 | Settings.vue | themeConfig | `/api/v1/settings/theme` | `settingsApi.getThemeSettings()` |
| 通知设置 | Settings.vue | notificationConfig | `/api/v1/settings/notifications` | `settingsApi.getNotificationSettings()` |

---

## 13. 系统管理

### 13.1 系统架构 (`/system/architecture`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 架构概览 | Architecture.vue | architectureInfo | `/api/v1/system/architecture` | `systemApi.getArchitecture()` |
| 数据库连接 | Architecture.vue | dbConnections | `/api/v1/system/db-connections` | `systemApi.getDbConnections()` |
| 连接池状态 | Architecture.vue | poolStatus | `/api/v1/system/pool-status` | `systemApi.getPoolStatus()` |
| 健康检查 | Architecture.vue | healthStatus | `/api/health/detailed` | `monitoringApi.getDetailedHealthCheck()` |
| 性能指标 | Architecture.vue | performanceMetrics | `/api/v1/system/metrics` | `systemApi.getMetrics()` |

### 13.2 数据库监控 (`/system/database-monitor`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 数据库状态 | DatabaseMonitor.vue | dbStatus | `/api/v1/system/database/status` | `databaseApi.getStatus()` |
| 连接池监控 | DatabaseMonitor.vue | poolMetrics | `/api/v1/system/database/pool` | `databaseApi.getPoolMetrics()` |
| 查询性能 | DatabaseMonitor.vue | queryPerformance | `/api/v1/system/database/queries` | `databaseApi.getQueryPerformance()` |
| 慢查询日志 | DatabaseMonitor.vue | slowQueries | `/api/v1/system/database/slow-queries` | `databaseApi.getSlowQueries()` |

### 13.3 智能数据源测试 (`/smart-data-test`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 数据源状态 | SmartDataSourceTest.vue | dataSourceStatus | `/api/data-quality/status` | `dataQualityApi.getStatus()` |
| 数据质量报告 | SmartDataSourceTest.vue | qualityReport | `/api/data-quality/report` | `dataQualityApi.getReport()` |
| 测试结果 | SmartDataSourceTest.vue | testResults | `/api/data-quality/test` | `dataQualityApi.runTest()` |

---

## 14. 功能演示

### 14.1 Phase 4 Dashboard (`/demo/phase4-dashboard`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 演示数据1 | Phase4Dashboard.vue | demoData1 | `/api/demo/data1` | `demoApi.getData1()` |
| 演示数据2 | Phase4Dashboard.vue | demoData2 | `/api/demo/data2` | `demoApi.getData2()` |

### 14.2 Wencai (`/demo/wencai`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 预定义查询模板 | Wencai.vue | queryTemplates | `/api/market/wencai/templates` | `marketApi.getWencaiTemplates()` |
| 查询结果 | Wencai.vue | queryResults | `/api/market/wencai/query` | `marketApi.getWencaiQuery()` |
| 我的查询 | Wencai.vue | myQueries | `/api/market/wencai/my-queries` | `marketApi.getMyQueries()` |
| 查询分析 | Wencai.vue | queryAnalysis | `/api/market/wencai/analysis` | `marketApi.getQueryAnalysis()` |
| 使用指南 | Wencai.vue | guideContent | `/api/market/wencai/guide` | `marketApi.getGuide()` |

### 14.3 OpenStock (`/demo/openstock`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| OpenStock数据 | OpenStockDemo.vue | openStockData | `/api/demo/openstock` | `demoApi.getOpenStockData()` |

### 14.4 PyProfiling (`/demo/pyprofiling`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 性能分析数据 | PyprofilingDemo.vue | profilingData | `/api/demo/pyprofiling` | `demoApi.getProfilingData()` |

### 14.5 Freqtrade (`/demo/freqtrade`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| Freqtrade数据 | FreqtradeDemo.vue | freqtradeData | `/api/demo/freqtrade` | `demoApi.getFreqtradeData()` |

### 14.6 Stock Analysis (`/demo/stock-analysis`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 股票分析数据 | StockAnalysisDemo.vue | analysisData | `/api/demo/stock-analysis` | `demoApi.getStockAnalysis()` |

### 14.7 TDX Python (`/demo/tdxpy`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| TDX数据演示 | TdxpyDemo.vue | tdxDemoData | `/api/demo/tdxpy` | `demoApi.getTdxpyData()` |

---

## 15. 特殊页面

### 15.1 登录页 (`/login`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 登录表单 | Login.vue | loginForm | `/api/auth/login` | `authApi.login()` |
| 记住我 | Login.vue | rememberMe | - | 本地存储 |

### 15.2 404页面 (`/not-found`)

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|----------|---------|----------|
| 错误信息 | NotFound.vue | - | - | 静态内容 |

---

## API通用配置

### 请求拦截器配置
- **文件位置**: `/src/api/index.js:20-41`
- **认证方式**: Bearer Token
- **开发环境**: 自动使用mock token
- **生产环境**: 从localStorage获取token

### 响应拦截器配置
- **文件位置**: `/src/api/index.js:44-75`
- **错误处理**: 统一错误消息提示
- **状态码处理**: 401/403/404/500

### 缓存策略
- **缓存管理器**: `/src/utils/cache.js`
- **默认缓存时间**:
  - 股票基础数据: 5分钟
  - K线数据: 5分钟
  - 股票详情: 15分钟
  - 行业概念数据: 1小时

---

## 数据格式规范

### 通用数据格式
- **价格**: 2位小数 (如: 150.25)
- **百分比**: 2位小数带%符号 (如: +5.23%)
- **金额**: 千分位分隔 (如: 1,000,000)
- **日期**: YYYY-MM-DD
- **时间**: HH:mm:ss
- **成交量**: 自动转换万/亿单位

### 状态码规范
- **成功响应**: `{ success: true, data: {...} }`
- **失败响应**: `{ success: false, msg: "错误信息" }`
- **时间戳**: ISO格式 `datetime.now().isoformat()`

---

## 常用API快速参考

| 功能分类 | API前缀 | 主要端点 |
|---------|---------|----------|
| 数据获取 | `/api/data/` | stocks, markets, kline |
| 市场行情 | `/api/market/` | quotes, fund-flow, etf |
| 技术分析 | `/api/technical/` | indicators, signals |
| 交易相关 | `/api/v1/trade/` | execute, history, orders |
| 策略管理 | `/api/v1/strategy/` | strategies, backtest |
| 风险管理 | `/api/v1/risk/` | dashboard, alerts |
| 系统监控 | `/api/health` | status, detailed |
| 实时推送 | `/api/v1/sse/` | status, events |

---

**最后更新**: 2025-12-06
**版本**: v1.0
**维护者**: MyStocks开发团队