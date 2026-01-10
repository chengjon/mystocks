# Web前端页面API对接完整映射表

**生成时间**: 2026-01-09
**版本**: v1.0
**项目**: MyStocks Web前端

---

## 📋 目录

1. [仪表盘 (Dashboard)](#1-仪表盘-dashboard)
2. [市场行情 (Market)](#2-市场行情-market)
3. [市场数据 (Market Data)](#3-市场数据-market-data)
4. [股票管理 (Stocks)](#4-股票管理-stocks)
5. [数据分析 (Analysis)](#5-数据分析-analysis)
6. [技术分析 (Technical Analysis)](#6-技术分析-technical-analysis)
7. [指标库 (Indicator Library)](#7-指标库-indicator-library)
8. [风险监控 (Risk Monitor)](#8-风险监控-risk-monitor)
9. [公告监控 (Announcement Monitor)](#9-公告监控-announcement-monitor)
10. [实时监控 (Real-time Monitor)](#10-实时监控-real-time-monitor)
11. [交易管理 (Trade Management)](#11-交易管理-trade-management)
12. [策略管理 (Strategy Management)](#12-策略管理-strategy-management)
13. [回测分析 (Backtest Analysis)](#13-回测分析-backtest-analysis)
14. [任务管理 (Task Management)](#14-任务管理-task-management)
15. [系统设置 (Settings)](#15-系统设置-settings)

---

## 1. 仪表盘 (Dashboard)

**路由**: `/dashboard`
**组件文件**: `web/frontend/src/views/Dashboard.vue`

### 页面元素映射表

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|---------|---------|---------|
| **页面标题** | `<h1 class="page-title">` | 硬编码 "MARKET OVERVIEW" | - | - |
| **副标题** | `<p class="page-subtitle">` | 硬编码 "REAL-TIME MARKET INTELLIGENCE..." | - | - |
| **统计卡片1** | `<BloombergStatCard label="TOTAL STOCKS">` | `:value="5216"` | `GET /api/market/statistics` | `marketApi.getMarketStatistics()` |
| **统计卡片2** | `<BloombergStatCard label="RISING">` | `:value="2456"` | `GET /api/market/statistics` | `marketApi.getMarketStatistics()` |
| **统计卡片3** | `<BloombergStatCard label="FALLING">` | `:value="1892"` | `GET /api/market/statistics` | `marketApi.getMarketStatistics()` |
| **统计卡片4** | `<BloombergStatCard label="UNCHANGED">` | `:value="868"` | `GET /api/market/statistics` | `marketApi.getMarketStatistics()` |
| **市场热度分析图表** | `<div ref="marketHeatChartRef">` | `marketHeatChart: ECharts` | `GET /api/market/heatmap` | `marketApi.getMarketHeatmap()` |
| **行业资金流向图表** | `<div ref="industryChartRef">` | `industryChart: ECharts` | `GET /api/market/fund-flow` | `marketApi.getFundFlow()` |
| **板块表格-自选** | `<el-table :data="getSectorData()">` | `favoriteStocks: ref<StockRow[]>` | `GET /api/market/sectors` | `marketApi.getSectorPerformance()` |
| **板块表格-策略** | `<el-table :data="strategyStocks">` | `strategyStocks: ref<StockRow[]>` | `GET /api/market/sectors` | `marketApi.getSectorPerformance()` |
| **板块表格-行业** | `<el-table :data="industryStocks">` | `industryStocks: ref<StockRow[]>` | `GET /api/market/sectors` | `marketApi.getSectorPerformance()` |
| **板块表格-概念** | `<el-table :data="conceptStocks">` | `conceptStocks: ref<StockRow[]>` | `GET /api/market/sectors` | `marketApi.getSectorPerformance()` |
| **刷新按钮** | `<el-button @click="handleRetry">` | `loading: ref(false)` | - | `loadData()` |
| **重新加载按钮** | `<el-button @click="handleRefresh">` | - | - | `loadData()` |
| **行业标准选择器** | `<select v-model="industryStandard">` | `industryStandard: ref('csrc')` | - | `updateIndustryChart()` |

### API服务引用

```typescript
import { marketApi } from '@/api/market'

// 使用示例
const statistics = await marketApi.getMarketStatistics()
const heatmap = await marketApi.getMarketHeatmap()
const fundFlow = await marketApi.getFundFlow()
const sectors = await marketApi.getSectorPerformance()
```

---

## 2. 市场行情 (Market)

**路由**: `/market/list`
**组件文件**: `web/frontend/src/views/Market.vue`

### 页面元素映射表

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|---------|---------|---------|
| **页面标题** | `<h1 class="market-title">` | 硬编码 "MARKET OVERVIEW" | - | - |
| **副标题** | `<p class="market-subtitle">` | 硬编码 "PORTFOLIO TRACKING..." | - | - |
| **统计卡片1-总资产** | `<BloombergStatCard label="TOTAL ASSETS">` | `portfolio.total_assets` | `GET /api/trade/account-overview` | `tradeApi.getAccountOverview()` |
| **统计卡片2-可用现金** | `<BloombergStatCard label="AVAILABLE CASH">` | `portfolio.available_cash` | `GET /api/trade/account-overview` | `tradeApi.getAccountOverview()` |
| **统计卡片3-持仓市值** | `<BloombergStatCard label="POSITION VALUE">` | `portfolio.position_value` | `GET /api/trade/account-overview` | `tradeApi.getAccountOverview()` |
| **统计卡片4-总盈亏** | `<BloombergStatCard label="TOTAL PROFIT">` | `portfolio.total_profit` | `GET /api/trade/account-overview` | `tradeApi.getAccountOverview()` |
| **市场数据卡片** | `<el-card class="market-data-card">` | - | - | - |
| **交易统计-总交易数** | `<span class="mini-stat-value">{{ stats.total_trades }}` | `stats.total_trades` | `GET /api/trade/statistics` | `tradeApi.getTradeStatistics()` |
| **交易统计-买入数** | `<span class="mini-stat-value buy">{{ stats.buy_count }}` | `stats.buy_count` | `GET /api/trade/statistics` | `tradeApi.getTradeStatistics()` |
| **交易统计-卖出数** | `<span class="mini-stat-value sell">{{ stats.sell_count }}` | `stats.sell_count` | `GET /api/trade/statistics` | `tradeApi.getTradeStatistics()` |
| **标签页-持仓** | `activeTab === 'positions'` | `activeTab: ref('stats')` | - | - |
| **标签页-历史** | `activeTab === 'history'` | - | - | - |
| **标签页-待办** | `activeTab === 'pending'` | - | - | - |
| **刷新数据按钮** | `<el-button @click="handleRefresh">` | `loading: ref(false)` | `GET /api/market/refresh` | `marketApi.refreshMarketData()` |

### API服务引用

```typescript
import { tradeApi } from '@/api/trade'
import { marketApi } from '@/api/market'

// 使用示例
const accountOverview = await tradeApi.getAccountOverview()
const tradeStats = await tradeApi.getTradeStatistics()
const marketData = await marketApi.refreshMarketData('all')
```

---

## 3. 市场数据 (Market Data)

**路由布局**: `/market-data/*`
**父布局组件**: `DataLayout.vue`

### 3.1 资金流向 (Fund Flow)

**路由**: `/market-data/fund-flow`
**组件文件**: `web/frontend/src/components/market/FundFlowPanel.vue`

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|---------|---------|---------|
| **资金流向图表** | `<div ref="chartRef">` | `fundFlowData: ref<FundFlowChartPoint[]>` | `GET /api/market/fund-flow` | `marketApi.getFundFlow()` |
| **日期范围选择器** | `<el-date-picker v-model="dateRange">` | `dateRange: ref<Date[]>` | - | `updateChart()` |
| **市场选择器** | `<el-select v-model="selectedMarket">` | `selectedMarket: ref('SH')` | - | `updateChart()` |
| **刷新按钮** | `<el-button @click="handleRefresh">` | `loading: ref(false)` | `GET /api/market/fund-flow` | `marketApi.getFundFlow()` |

### 3.2 ETF行情 (ETF Data)

**路由**: `/market-data/etf`
**组件文件**: `web/frontend/src/components/market/ETFDataTable.vue`

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|---------|---------|---------|
| **ETF数据表格** | `<el-table :data="etfData">` | `etfData: ref<ETFDataItem[]>` | `GET /api/market/etf` | `marketApi.getETFData()` |
| **分页组件** | `<el-pagination>` | `pagination: reactive({...})` | - | `handlePageChange()` |
| **搜索框** | `<el-input v-model="searchQuery">` | `searchQuery: ref('')` | - | `handleSearch()` |
| **排序功能** | `<el-table @sort-change="handleSort">` | - | - | `handleSort()` |

### 3.3 竞价抢筹 (Chip Race)

**路由**: `/market-data/chip-race`
**组件文件**: `web/frontend/src/components/market/ChipRaceTable.vue`

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|---------|---------|---------|
| **竞价抢筹表格** | `<el-table :data="chipRaceData">` | `chipRaceData: ref<ChipRaceItem[]>` | `GET /api/market/chip-race` | `marketApi.getChipRaceData()` |
| **自动刷新开关** | `<el-switch v-model="autoRefresh">` | `autoRefresh: ref(false)` | - | `toggleAutoRefresh()` |
| **刷新间隔选择** | `<el-select v-model="refreshInterval">` | `refreshInterval: ref(5000)` | - | `updateRefreshInterval()` |

### 3.4 龙虎榜 (LongHu Bang)

**路由**: `/market-data/lhb`
**组件文件**: `web/frontend/src/components/market/LongHuBangTable.vue`

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|---------|---------|---------|
| **龙虎榜表格** | `<el-table :data="lhbData">` | `lhbData: ref<LongHuBangItem[]>` | `GET /api/market/longhubang` | `marketApi.getLongHuBangData()` |
| **日期选择器** | `<el-date-picker v-model="selectedDate">` | `selectedDate: ref(new Date())` | `GET /api/market/longhubang` | `fetchLhbData()` |
| **市场选择** | `<el-radio-group v-model="marketType">` | `marketType: ref('all')` | `GET /api/market/longhubang` | `fetchLhbData()` |

### 3.5 问财筛选 (Wencai)

**路由**: `/market-data/wencai`
**组件文件**: `web/frontend/src/components/market/WencaiPanelV2.vue`

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|---------|---------|---------|
| **问财查询输入框** | `<el-input v-model="wencaiQuery">` | `wencaiQuery: ref('')` | `POST /api/market/wencai/query` | `marketApi.queryWencai()` |
| **查询结果表格** | `<el-table :data="wencaiResults">` | `wencaiResults: ref<WencaiResult[]>` | `POST /api/market/wencai/query` | `marketApi.queryWencai()` |
| **查询历史** | `<div class="query-history">` | `queryHistory: ref<string[]>` | `GET /api/market/wencai/history` | `marketApi.getWencaiHistory()` |
| **保存查询按钮** | `<el-button @click="saveQuery">` | - | `POST /api/market/wencai/save` | `marketApi.saveWencaiQuery()` |

---

## 4. 股票管理 (Stocks)

**路由**: `/stocks`
**组件文件**: `web/frontend/src/views/Stocks.vue`

### 页面元素映射表

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|---------|---------|---------|
| **页面标题** | `<PageHeader title="股票列表">` | 硬编码 "股票列表" | - | - |
| **筛选栏** | `<FilterBar :filters="filterConfig">` | `filterConfig: FilterConfig[]` | - | `handleFilterChange()` |
| **股票列表表格** | `<StockListTable :data="stocks">` | `stocks: ref<StockItem[]>` | `GET /api/stocks/list` | `dataApi.getStockList()` |
| **分页栏** | `<PaginationBar v-model:page="pagination">` | `pagination: reactive({...})` | - | `handlePageChange()` |
| **搜索功能** | `FilterBar @search="handleSearch">` | `searchQuery: ref('')` | `GET /api/stocks/search` | `dataApi.searchStocks()` |
| **市场筛选** | `<el-select v-model="filters.market">` | `filters.market: ref('')` | `GET /api/stocks/list` | `dataApi.getStockList()` |
| **行业筛选** | `<el-select v-model="filters.industry">` | `filters.industry: ref('')` | `GET /api/stocks/list` | `dataApi.getStockList()` |
| **排序功能** | `StockListTable @sort-change="handleSort">` | - | - | `handleSort()` |
| **股票详情跳转** | `@row-click="handleRowClick"` | - | - | `router.push('/stock-detail/:symbol')` |
| **刷新按钮** | `<button @click="handleRefresh">` | `loading: ref(false)` | `GET /api/stocks/list` | `loadStocks()` |

### API服务引用

```typescript
import { dataApi } from '@/api'

// 使用示例
const stockList = await dataApi.getStockList({
  page: 1,
  pageSize: 20,
  market: 'SH',
  industry: '银行'
})

const searchResults = await dataApi.searchStocks('平安', 20)
```

---

## 5. 数据分析 (Analysis)

**路由**: `/analysis`
**组件文件**: `web/frontend/src/views/Analysis.vue`

### 页面元素映射表

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|---------|---------|---------|
| **页面标题** | `<PageHeader title="数据分析">` | 硬编码 "数据分析" | - | - |
| **分析类型选择** | `<el-tabs v-model="activeTab">` | `activeTab: ref('overview')` | - | - |
| **概览图表** | `activeTab === 'overview'` | `overviewData: ref<any>` | `GET /api/analysis/overview` | `analysisApi.getOverview()` |
| **趋势图表** | `activeTab === 'trend'` | `trendData: ref<any>` | `GET /api/analysis/trend` | `analysisApi.getTrend()` |
| **相关性分析** | `activeTab === 'correlation'` | `correlationData: ref<any>` | `GET /api/analysis/correlation` | `analysisApi.getCorrelation()` |
| **数据导出按钮** | `<el-button @click="exportData">` | - | `POST /api/analysis/export` | `analysisApi.exportData()` |

---

## 6. 技术分析 (Technical Analysis)

**路由**: `/technical`
**组件文件**: `web/frontend/src/views/TechnicalAnalysis.vue`

### 页面元素映射表

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|---------|---------|---------|
| **页面标题** | `<h1 class="page-title">` | 硬编码 "TECHNICAL ANALYSIS" | - | - |
| **股票搜索栏** | `<StockSearchBar v-model="selectedSymbol">` | `selectedSymbol: ref('600519')` | `GET /api/stock-search` | `marketApi.searchStocks()` |
| **日期范围选择器** | `<el-date-picker v-model="dateRange">` | `dateRange: ref<Date[]>` | - | `fetchKlineData()` |
| **周期选择器** | `<el-radio-group v-model="selectedPeriod">` | `selectedPeriod: ref('day')` | `GET /api/market/kline` | `marketApi.getKLineData()` |
| **K线图表** | `<KLineChart :data="chartData.ohlcv">` | `chartData.ohlcv: KLineData[]` | `GET /api/market/kline` | `marketApi.getKLineData()` |
| **指标面板** | `<IndicatorPanel v-model="showIndicatorPanel">` | `showIndicatorPanel: ref(false)` | `GET /api/indicators/list` | `indicatorApi.getIndicators()` |
| **选中指标列表** | `:selected-indicators="selectedIndicators"` | `selectedIndicators: ref<string[]>` | - | - |
| **添加指标** | `@add-indicator="handleAddIndicator"` | - | `POST /api/indicators/calculate` | `indicatorApi.calculateIndicator()` |
| **移除指标** | `@remove-indicator="handleRemoveIndicator"` | - | - | - |
| **刷新按钮** | `<el-button @click="refreshData">` | `loading: ref(false)` | `GET /api/market/kline` | `fetchKlineData()` |
| **配置保存** | `<el-dropdown @command="handleConfigCommand">` | - | `POST /api/user/config/save` | `userApi.saveConfig()` |
| **配置加载** | `command="load"` | - | `GET /api/user/config/load` | `userApi.loadConfig()` |

### API服务引用

```typescript
import { marketApi } from '@/api/market'
import { indicatorApi } from '@/api/indicatorApi'
import { userApi } from '@/api/user'

// 使用示例
const klineData = await marketApi.getKLineData({
  symbol: '600519',
  interval: '1d',
  startDate: '2024-01-01',
  endDate: '2024-12-31',
  limit: 100
})

const indicators = await indicatorApi.getIndicators()
const calculated = await indicatorApi.calculateIndicator({
  symbol: '600519',
  indicator: 'MA',
  params: { periods: [5, 10, 20] }
})
```

---

## 7. 指标库 (Indicator Library)

**路由**: `/indicators`
**组件文件**: `web/frontend/src/views/IndicatorLibrary.vue`

### 页面元素映射表

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|---------|---------|---------|
| **页面标题** | `<h1 class="page-title">` | 硬编码 "INDICATOR LIBRARY" | - | - |
| **副标题-统计数** | `<p class="page-subtitle">` | `registry?.total_count` | `GET /api/indicators/registry` | `indicatorApi.getRegistry()` |
| **统计卡片** | `<MonitoringStatCard>` | `registry?.categories` | `GET /api/indicators/registry` | `indicatorApi.getRegistry()` |
| **分类标签** | `<el-tag>{{ getCategoryLabel() }}</el-tag>` | `indicator.category` | - | - |
| **面板类型标签** | `<el-tag type="info">{{ getPanelLabel() }}</el-tag>` | `indicator.panel_type` | - | - |
| **指标缩写** | `<span class="indicator-abbr">` | `indicator.abbreviation` | - | - |
| **指标全名** | `<h3>{{ indicator.full_name }}</h3>` | `indicator.full_name` | - | - |
| **指标中文名** | `<h4>{{ indicator.chinese_name }}</h4>` | `indicator.chinese_name` | - | - |
| **指标描述** | `<p class="description">` | `indicator.description` | - | - |
| **参数列表** | `<div class="params-grid">` | `indicator.parameters[]` | - | - |
| **输出字段** | `<div class="outputs-grid">` | `indicator.outputs[]` | - | - |
| **参考线** | `<div class="reference-section">` | `indicator.reference_lines[]` | - | - |
| **搜索功能** | `<el-input v-model="searchQuery">` | `searchQuery: ref('')` | - | `handleSearch()` |
| **分类筛选** | `<el-select v-model="selectedCategory">` | `selectedCategory: ref('all')` | - | `handleFilterChange()` |
| **面板筛选** | `<el-select v-model="selectedPanel">` | `selectedPanel: ref('all')` | - | `handleFilterChange()` |

### API服务引用

```typescript
import { indicatorApi } from '@/api/indicatorApi'

// 使用示例
const registry = await indicatorApi.getRegistry()
console.log('Total indicators:', registry.total_count)
console.log('Categories:', registry.categories)

const indicatorDetail = await indicatorApi.getIndicatorDetail('MA')
```

---

## 8. 风险监控 (Risk Monitor)

**路由**: `/risk-monitor/overview`
**组件文件**: `web/frontend/src/views/RiskMonitor.vue`

### 页面元素映射表

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|---------|---------|---------|
| **页面标题** | `<PageHeader title="风险监控">` | 硬编码 "风险监控" | - | - |
| **风险仪表板** | `<RiskDashboard>` | `riskData: ref<RiskData>` | `GET /api/risk/overview` | `riskApi.getRiskOverview()` |
| **风险等级指示器** | `<el-progress :percentage="riskScore">` | `riskScore: ref(0)` | `GET /api/risk/score` | `riskApi.getRiskScore()` |
| **风险预警列表** | `<el-table :data="alerts">` | `alerts: ref<RiskAlert[]>` | `GET /api/risk/alerts` | `riskApi.getRiskAlerts()` |
| **风险趋势图** | `<div ref="riskTrendChart">` | `riskTrendData: ref<any>` | `GET /api/risk/trend` | `riskApi.getRiskTrend()` |
| **持仓风险分析** | `<el-table :data="positionRisks">` | `positionRisks: ref<any[]>` | `GET /api/risk/positions` | `riskApi.getPositionRisks()` |
| **压力测试按钮** | `<el-button @click="runStressTest">` | - | `POST /api/risk/stress-test` | `riskApi.runStressTest()` |

### API服务引用

```typescript
import { riskApi } from '@/api'

// 使用示例
const riskOverview = await riskApi.getRiskOverview()
const riskScore = await riskApi.getRiskScore()
const alerts = await riskApi.getRiskAlerts()
const trend = await riskApi.getRiskTrend()
```

---

## 9. 公告监控 (Announcement Monitor)

**路由**: `/risk-monitor/announcement`
**组件文件**: `web/frontend/src/views/announcement/AnnouncementMonitor.vue`

### 页面元素映射表

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|---------|---------|---------|
| **页面标题** | `<PageHeader title="公告监控">` | 硬编码 "公告监控" | - | - |
| **公告列表表格** | `<el-table :data="announcements">` | `announcements: ref<Announcement[]>` | `GET /api/announcements/list` | `announcementApi.getAnnouncements()` |
| **公告类型筛选** | `<el-select v-model="selectedType">` | `selectedType: ref('all')` | `GET /api/announcements/list` | `fetchAnnouncements()` |
| **关键词搜索** | `<el-input v-model="searchKeyword">` | `searchKeyword: ref('')` | `GET /api/announcements/search` | `announcementApi.searchAnnouncements()` |
| **日期范围选择** | `<el-date-picker v-model="dateRange">` | `dateRange: ref<Date[]>` | `GET /api/announcements/list` | `fetchAnnouncements()` |
| **标记已读按钮** | `<el-button @click="markAsRead">` | - | `POST /api/announcements/mark-read` | `announcementApi.markAsRead()` |
| **导出功能** | `<el-button @click="exportAnnouncements">` | - | `POST /api/announcements/export` | `announcementApi.exportAnnouncements()` |
| **自动刷新开关** | `<el-switch v-model="autoRefresh">` | `autoRefresh: ref(false)` | - | `toggleAutoRefresh()` |

---

## 10. 实时监控 (Real-time Monitor)

**路由**: `/market/realtime`
**组件文件**: `web/frontend/src/views/RealTimeMonitor.vue`

### 页面元素映射表

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|---------|---------|---------|
| **页面标题** | `<PageHeader title="实时监控">` | 硬编码 "实时监控" | - | - |
| **实时行情表格** | `<el-table :data="realtimeQuotes">` | `realtimeQuotes: ref<Quote[]>` | `WS /api/realtime/quotes` | `realtimeService.connectQuotes()` |
| **监控列表** | `<el-table :data="watchlist">` | `watchlist: ref<WatchlistItem[]>` | `GET /api/watchlist/list` | `watchlistApi.getWatchlist()` |
| **添加监控按钮** | `<el-button @click="addToWatchlist">` | - | `POST /api/watchlist/add` | `watchlistApi.addToWatchlist()` |
| **移除监控** | `<el-button @click="removeFromWatchlist">` | - | `DELETE /api/watchlist/remove` | `watchlistApi.removeFromWatchlist()` |
| **价格预警设置** | `<el-dialog v-model="alertDialog">` | `alertConfig: reactive({...})` | `POST /api/alerts/create` | `alertsApi.createAlert()` |
| **刷新间隔** | `<el-select v-model="refreshInterval">` | `refreshInterval: ref(3000)` | - | `updateRefreshInterval()` |
| **连接状态指示器** | `<el-tag :type="connectionStatus">` | `connectionStatus: ref('disconnected')` | - | - |

### API服务引用

```typescript
import { watchlistApi } from '@/api'
import { realtimeService } from '@/services/realtimeMarket'

// WebSocket连接
realtimeService.connectQuotes({
  onMessage: (quote) => {
    console.log('实时报价:', quote)
  },
  onError: (error) => {
    console.error('连接错误:', error)
  }
})

// Watchlist管理
const watchlist = await watchlistApi.getWatchlist()
await watchlistApi.addToWatchlist('600519', 'SH')
```

---

## 11. 交易管理 (Trade Management)

**路由**: `/trade`
**组件文件**: `web/frontend/src/views/TradeManagement.vue`

### 页面元素映射表

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|---------|---------|---------|
| **页面标题** | `<h1 class="page-title">` | 硬编码 "TRADE MANAGEMENT" | - | - |
| **新建交易按钮** | `<el-button @click="openTradeDialog('buy')">` | `tradeType: ref<'buy' \| 'sell'>` | - | - |
| **投资组合概览** | `<PortfolioOverview>` | `portfolioData: ref<any>` | `GET /api/trade/account-overview` | `tradeApi.getAccountOverview()` |
| **持仓标签页** | `activeTab === 'positions'` | `activeTab: ref('positions')` | `GET /api/trade/positions` | `tradeApi.getPositions()` |
| **持仓表格** | `<PositionsTab>` | `positions: ref<Position[]>` | `GET /api/trade/positions` | `tradeApi.getPositions()` |
| **交易历史标签页** | `activeTab === 'trades'` | - | `GET /api/trade/history` | `tradeApi.getTradeHistory()` |
| **交易历史表格** | `<TradeHistoryTab>` | `tradeHistory: ref<Trade[]>` | `GET /api/trade/history` | `tradeApi.getTradeHistory()` |
| **统计标签页** | `activeTab === 'statistics'` | - | `GET /api/trade/statistics` | `tradeApi.getTradeStatistics()` |
| **统计图表** | `<StatisticsTab>` | `statistics: ref<any>` | `GET /api/trade/statistics` | `tradeApi.getTradeStatistics()` |
| **交易对话框** | `<TradeDialog>` | `tradeDialogVisible: ref(false)` | `POST /api/trade/execute` | `tradeApi.executeTrade()` |
| **快速卖出按钮** | `@quick-sell="handleQuickSell"` | - | `POST /api/trade/quick-sell` | `tradeApi.quickSell()` |

### API服务引用

```typescript
import { tradeApi } from '@/api/trade'

// 使用示例
const accountOverview = await tradeApi.getAccountOverview()
const positions = await tradeApi.getPositions()
const tradeHistory = await tradeApi.getTradeHistory({
  page: 1,
  pageSize: 20
})
const statistics = await tradeApi.getTradeStatistics()

// 执行交易
await tradeApi.executeTrade({
  symbol: '600519',
  type: 'buy',
  quantity: 100,
  price: 1650.00
})
```

---

## 12. 策略管理 (Strategy Management)

**路由**: `/strategy-hub/management`
**组件文件**: `web/frontend/src/views/StrategyManagement.vue`

### 页面元素映射表

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|---------|---------|---------|
| **页面标题** | `<PageHeader title="策略管理">` | 硬编码 "策略管理" | - | - |
| **策略列表表格** | `<el-table :data="strategies">` | `strategies: ref<StrategyListItemVM[]>` | `GET /api/strategy/list` | `strategyApi.getStrategies()` |
| **创建策略按钮** | `<el-button @click="createStrategy">` | - | `POST /api/strategy` | `strategyApi.createStrategy()` |
| **编辑策略** | `<el-button @click="editStrategy">` | - | `PUT /api/strategy/:id` | `strategyApi.updateStrategy()` |
| **删除策略** | `<el-button @click="deleteStrategy">` | - | `DELETE /api/strategy/:id` | `strategyApi.deleteStrategy()` |
| **启动策略** | `<el-button @click="startStrategy">` | - | `POST /api/strategy/:id/start` | `strategyApi.startStrategy()` |
| **停止策略** | `<el-button @click="stopStrategy">` | - | `POST /api/strategy/:id/stop` | `strategyApi.stopStrategy()` |
| **策略详情对话框** | `<el-dialog v-model="detailDialog">` | `selectedStrategy: ref<any>` | `GET /api/strategy/:id` | `strategyApi.getStrategy()` |
| **策略类型筛选** | `<el-select v-model="filterType">` | `filterType: ref('all')` | `GET /api/strategy/list` | `fetchStrategies()` |
| **策略状态筛选** | `<el-select v-model="filterStatus">` | `filterStatus: ref('all')` | `GET /api/strategy/list` | `fetchStrategies()` |

### API服务引用

```typescript
import { strategyApi } from '@/api/strategy'

// 使用示例
const strategies = await strategyApi.getStrategies({
  type: 'trend',
  status: 'active'
})

const strategyDetail = await strategyApi.getStrategy('strategy-001')

// 创建策略
const newStrategy = await strategyApi.createStrategy({
  name: 'MA Cross Strategy',
  type: 'trend',
  code: '...',
  parameters: { shortPeriod: 5, longPeriod: 20 }
})

// 启动策略
await strategyApi.startStrategy('strategy-001', { initialCapital: 100000 })
```

---

## 13. 回测分析 (Backtest Analysis)

**路由**: `/strategy-hub/backtest`
**组件文件**: `web/frontend/src/views/BacktestAnalysis.vue`

### 页面元素映射表

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|---------|---------|---------|
| **页面标题** | `<PageHeader title="回测分析">` | 硬编码 "回测分析" | - | - |
| **回测表单** | `<el-form :model="backtestForm">` | `backtestForm: reactive({...})` | - | - |
| **策略选择** | `<el-select v-model="backtestForm.strategyId">` | `backtestForm.strategyId` | `GET /api/strategy/list` | `strategyApi.getStrategies()` |
| **日期范围** | `<el-date-picker v-model="backtestForm.dateRange">` | `backtestForm.dateRange` | - | - |
| **初始资金** | `<el-input-number v-model="backtestForm.initialCapital">` | `backtestForm.initialCapital` | - | - |
| **运行回测按钮** | `<el-button @click="runBacktest">` | `loading: ref(false)` | `POST /api/strategy/backtest` | `strategyApi.runBacktest()` |
| **回测结果表格** | `<el-table :data="backtestResults">` | `backtestResults: ref<BacktestResultVM[]>` | `GET /api/strategy/:id/backtests` | `strategyApi.getBacktestResults()` |
| **回测详情对话框** | `<el-dialog v-model="detailDialog">` | `selectedBacktest: ref<any>` | `GET /api/backtest/:id` | `strategyApi.getBacktestDetails()` |
| **性能指标卡片** | `<StatCard>` | `performance: ref<any>` | `GET /api/backtest/:id/performance` | `backtestApi.getPerformance()` |
| **收益曲线图** | `<div ref="equityChart">` | `equityData: ref<any>` | `GET /api/backtest/:id/equity` | `backtestApi.getEquityCurve()` |
| **交易记录表格** | `<el-table :data="trades">` | `trades: ref<any[]>` | `GET /api/backtest/:id/trades` | `backtestApi.getTrades()` |
| **导出报告按钮** | `<el-button @click="exportReport">` | - | `POST /api/backtest/:id/export` | `backtestApi.exportReport()` |

### API服务引用

```typescript
import { strategyApi } from '@/api/strategy'

// 运行回测
const backtestResult = await strategyApi.runBacktest({
  strategyId: 'strategy-001',
  symbol: '600519',
  startDate: '2024-01-01',
  endDate: '2024-12-31',
  initialCapital: 100000,
  parameters: {
    shortPeriod: 5,
    longPeriod: 20
  }
})

// 获取回测结果
const results = await strategyApi.getBacktestResults('strategy-001')
const details = await strategyApi.getBacktestDetails('backtest-001')
```

---

## 14. 任务管理 (Task Management)

**路由**: `/tasks`
**组件文件**: `web/frontend/src/views/TaskManagement.vue`

### 页面元素映射表

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|---------|---------|---------|
| **页面标题** | `<PageHeader title="任务管理">` | 硬编码 "任务管理" | - | - |
| **任务列表表格** | `<TaskTable :tasks="tasks">` | `tasks: ref<Task[]>` | `GET /api/tasks/list` | `taskApi.getTasks()` |
| **创建任务按钮** | `<el-button @click="openCreateDialog">` | - | - | - |
| **创建任务表单** | `<TaskForm @submit="handleCreateTask">` | `taskForm: reactive({...})` | `POST /api/tasks/create` | `taskApi.createTask()` |
| **编辑任务** | `<TaskForm @submit="handleUpdateTask">` | `taskForm: reactive({...})` | `PUT /api/tasks/:id` | `taskApi.updateTask()` |
| **删除任务** | `<el-button @click="deleteTask">` | - | `DELETE /api/tasks/:id` | `taskApi.deleteTask()` |
| **启动任务** | `<el-button @click="startTask">` | - | `POST /api/tasks/:id/start` | `taskApi.startTask()` |
| **停止任务** | `<el-button @click="stopTask">` | - | `POST /api/tasks/:id/stop` | `taskApi.stopTask()` |
| **任务执行历史** | `<ExecutionHistory :task-id="selectedTaskId">` | `executions: ref<any[]>` | `GET /api/tasks/:id/executions` | `taskApi.getExecutions()` |
| **任务状态筛选** | `<el-select v-model="filterStatus">` | `filterStatus: ref('all')` | `GET /api/tasks/list` | `fetchTasks()` |
| **任务类型筛选** | `<el-select v-model="filterType">` | `filterType: ref('all')` | `GET /api/tasks/list` | `fetchTasks()` |

---

## 15. 系统设置 (Settings)

**路由**: `/settings`
**组件文件**: `web/frontend/src/views/Settings.vue`

### 页面元素映射表

| 页面元素 | Vue组件位置 | 数据变量 | API端点 | 对接函数 |
|---------|------------|---------|---------|---------|
| **页面标题** | `<PageHeader title="系统设置">` | 硬编码 "系统设置" | - | - |
| **设置标签页** | `<el-tabs v-model="activeTab">` | `activeTab: ref('general')` | - | - |
| **通用设置** | `activeTab === 'general'` | `generalSettings: reactive({...})` | `GET /api/settings/general` | `settingsApi.getGeneralSettings()` |
| **主题选择** | `<el-select v-model="generalSettings.theme">` | `generalSettings.theme` | - | - |
| **语言选择** | `<el-select v-model="generalSettings.language">` | `generalSettings.language` | - | - |
| **时区设置** | `<el-select v-model="generalSettings.timezone">` | `generalSettings.timezone` | - | - |
| **数据源设置** | `activeTab === 'datasource'` | `datasourceSettings: reactive({...})` | `GET /api/settings/datasource` | `settingsApi.getDatasourceSettings()` |
| **数据源测试** | `<el-button @click="testDatasource">` | - | `POST /api/datasource/test` | `datasourceApi.testConnection()` |
| **通知设置** | `activeTab === 'notification'` | `notificationSettings: reactive({...})` | `GET /api/settings/notification` | `settingsApi.getNotificationSettings()` |
| **邮件通知开关** | `<el-switch v-model="notificationSettings.email">` | `notificationSettings.email` | - | - |
| **浏览器通知开关** | `<el-switch v-model="notificationSettings.browser">` | `notificationSettings.browser` | - | - |
| **保存设置按钮** | `<el-button @click="saveSettings">` | `loading: ref(false)` | `POST /api/settings/save` | `settingsApi.saveSettings()` |
| **重置设置按钮** | `<el-button @click="resetSettings">` | - | `POST /api/settings/reset` | `settingsApi.resetSettings()` |

---

## 📌 附录

### A. API服务完整索引

| API文件 | 导出服务 | 主要功能 |
|--------|---------|---------|
| `market.ts` | `marketApi` | 市场数据、行情、K线、资金流向 |
| `strategy.ts` | `strategyApi` | 策略管理、回测执行 |
| `trade.ts` | `tradeApi` | 交易管理、持仓、历史、统计 |
| `indicatorApi.ts` | `indicatorApi` | 技术指标计算、指标库查询 |
| `monitoring.ts` | `monitoringApi` | 监控数据、告警管理 |
| `user.ts` | `userApi` | 用户配置、权限管理 |
| `index.js` | `dataApi`, `riskApi`, `watchlistApi` | 数据查询、风险分析、监控清单 |

### B. 常用数据类型定义

```typescript
// 市场数据类型
interface MarketOverviewVM {
  totalStocks: number
  rising: number
  falling: number
  unchanged: number
}

// K线数据类型
interface KLineData {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

// 策略配置类型
interface StrategyConfigVM {
  id: string
  name: string
  type: string
  parameters: any
  status: 'active' | 'inactive' | 'error'
}

// 交易记录类型
interface Trade {
  id: string
  symbol: string
  type: 'buy' | 'sell'
  quantity: number
  price: number
  timestamp: string
}
```

### C. 错误处理模式

```typescript
// 统一错误处理
try {
  const data = await marketApi.getMarketOverview()
  // 处理成功响应
} catch (error) {
  if (error.response?.status === 401) {
    // 处理未授权
  } else if (error.response?.status === 500) {
    // 处理服务器错误
  }
  ElMessage.error('加载数据失败')
}
```

---

**文档结束**

*最后更新: 2026-01-09*
*维护者: Claude Code*
*版本: v1.0*
