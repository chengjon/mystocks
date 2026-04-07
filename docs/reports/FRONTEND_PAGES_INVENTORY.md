# MyStocks 前端页面完整清单

> **设计方案说明**:
> 本文件是架构设计、系统模型、功能结构、映射关系或规格方案，不是当前仓库共享规则、当前实现边界或当前主线契约的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内结构分层、字段约定、模块职责、功能清单和实施建议应结合当前代码与主线文档复核；若冲突，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


**生成时间**: 2026-01-08
**项目**: MyStocks 量化交易管理系统
**前端框架**: Vue 3 + Element Plus
**路由模式**: Hash Mode

---

## 📊 总览统计

| 统计项 | 数量 | 百分比 |
|--------|------|--------|
| **总页面数** | 31 | 100% |
| **可用页面** | 31 | 100% |
| **不可用页面** | 0 | 0% |
| **P0核心页面** | 6 | 19.4% |
| **P1重要页面** | 8 | 25.8% |
| **P2辅助页面** | 17 | 54.8% |

---

## 🎯 P0 核心页面 (6个) - 最高优先级

**定义**: 用户主要入口页面，系统核心功能，必须100%可用

| # | 路由名称 | 页面标题 | 文件路径 | 功能描述 | 测试状态 |
|---|---------|---------|---------|---------|---------|
| 1 | `dashboard` | 仪表盘 | `views/Dashboard.vue` | 系统首页，展示统计数据、图表、市场热度 | ✅ 87.5% |
| 2 | `market` | 市场行情 | `views/Market.vue` | 股票市场行情列表，搜索和筛选功能 | ✅ 100% |
| 3 | `stocks` | 股票管理 | `views/Stocks.vue` | 股票列表管理，支持搜索和筛选 | ✅ 100% |
| 4 | `analysis` | 数据分析 | `views/Analysis.vue` | 技术指标分析，图表展示 | ✅ 100% |
| 5 | `trade` | 交易管理 | `views/TradeManagement.vue` | 交易记录管理，持仓统计 | ✅ 87.5% |
| 6 | `settings` | 系统设置 | `views/Settings.vue` | 系统配置，用户偏好设置 | ✅ 83.3% |

**P0平均通过率**: 94.7% ✅

---

## 🔥 P1 重要页面 (8个) - 高优先级

**定义**: 重要业务功能页面，日常使用频率高

| # | 路由名称 | 页面标题 | 文件路径 | 功能描述 | 布局 |
|---|---------|---------|---------|---------|------|
| 1 | `stock-detail` | 股票详情 | `views/StockDetail.vue` | 单个股票的详细信息，K线图，技术指标 | MainLayout |
| 2 | `realtime` | 实时监控 | `views/RealTimeMonitor.vue` | 实时行情监控，WebSocket推送 | MarketLayout |
| 3 | `risk` | 风险监控 | `views/RiskMonitor.vue` | 投资风险评估，预警系统 | RiskLayout |
| 4 | `strategy` | 策略管理 | `views/StrategyManagement.vue` | 量化策略配置和管理 | StrategyLayout |
| 5 | `backtest` | 回测分析 | `views/BacktestAnalysis.vue` | 策略回测，性能分析报告 | StrategyLayout |
| 6 | `technical` | 技术分析 | `views/TechnicalAnalysis.vue` | 技术指标图表，趋势分析 | MainLayout |
| 7 | `portfolio` | 投资组合 | `views/PortfolioManagement.vue` | 投资组合管理，资产配置 | MainLayout |
| 8 | `indicators` | 指标库 | `views/IndicatorLibrary.vue` | 技术指标库，指标配置 | MainLayout |

**P1平均通过率**: ~90% ✅

---

## 📋 P2 辅助页面 (17个) - 标准优先级

**定义**: 辅助功能页面，演示页面，系统管理页面

### 2.1 市场数据分析页面 (5个)

| # | 路由名称 | 页面标题 | 文件路径 | 功能描述 | 布局 |
|---|---------|---------|---------|---------|------|
| 1 | `market-data-fund-flow` | 资金流向 | `components/market/FundFlowPanel.vue` | 市场资金流向分析 | DataLayout |
| 2 | `market-data-etf` | ETF行情 | `components/market/ETFDataTable.vue` | ETF基金行情数据 | DataLayout |
| 3 | `market-data-chip-race` | 竞价抢筹 | `components/market/ChipRaceTable.vue` | 竞价抢筹数据分析 | DataLayout |
| 4 | `market-data-lhb` | 龙虎榜 | `components/market/LongHuBangTable.vue` | 龙虎榜数据展示 | DataLayout |
| 5 | `market-data-wencai` | 问财筛选 | `components/market/WencaiPanelV2.vue` | 同花顺问财筛选功能 | DataLayout |

### 2.2 系统管理页面 (4个)

| # | 路由名称 | 页面标题 | 文件路径 | 功能描述 | 布局 |
|---|---------|---------|---------|---------|------|
| 1 | `tasks` | 任务管理 | `views/TaskManagement.vue` | 系统任务管理，定时任务 | MainLayout |
| 2 | `system-architecture` | 系统架构 | `views/system/Architecture.vue` | 系统架构展示，文档 | MainLayout |
| 3 | `system-database-monitor` | 数据库监控 | `views/system/DatabaseMonitor.vue` | 数据库性能监控 | MainLayout |
| 4 | `announcement` | 公告监控 | `views/announcement/AnnouncementMonitor.vue` | 公司公告监控 | RiskLayout |

### 2.3 功能演示页面 (6个)

| # | 路由名称 | 页面标题 | 文件路径 | 功能描述 | 布局 |
|---|---------|---------|---------|---------|------|
| 1 | `openstock-demo` | OpenStock演示 | `views/OpenStockDemo.vue` | OpenStock库功能演示 | MainLayout |
| 2 | `pyprofiling-demo` | PyProfiling演示 | `views/PyprofilingDemo.vue` | PyProfiling性能分析演示 | MainLayout |
| 3 | `freqtrade-demo` | Freqtrade演示 | `views/FreqtradeDemo.vue` | Freqtrade交易机器人演示 | MainLayout |
| 4 | `stock-analysis-demo` | Stock-Analysis演示 | `views/StockAnalysisDemo.vue` | Stock-Analysis库演示 | MainLayout |
| 5 | `tdxpy-demo` | pytdx演示 | `views/TdxpyDemo.vue` | pytdx通达信接口演示 | MainLayout |
| 6 | `smart-data-test` | 智能数据源测试 | `views/SmartDataSourceTest.vue` | 智能数据源测试工具 | MainLayout |

### 2.4 其他页面 (2个)

| # | 路由名称 | 页面标题 | 文件路径 | 功能描述 | 布局 |
|---|---------|---------|---------|---------|------|
| 1 | `login` | 登录 | `views/Login.vue` | 用户登录页面 | 独立页面 |
| 2 | `tdx-market` | TDX行情 | `views/TdxMarket.vue` | 通达信行情数据 | MarketLayout |

**P2平均通过率**: ~85% ⚠️

---

## ❌ 不可用页面 (0个)

**当前状态**: 所有路由配置的页面文件都存在 ✅

### 已禁用的路由

| 路由名称 | 原因 | 说明 |
|---------|------|------|
| `gpu-monitoring` | 文件不存在 | 已在路由配置中注释，待实现 |

**路由注释位置**: `src/router/index.js:114-121`
```javascript
// CLI-5: GPU监控页面 (Phase 6 - T5.3)
// 暂时禁用 - 文件不存在
// {
//   path: 'gpu-monitoring',
//   name: 'gpu-monitoring',
//   component: () => import('@/views/GPUMonitoring.vue'),
//   meta: { title: 'GPU监控', icon: 'Monitor' }
// },
```

---

## 🗂️ 按布局分组

### MainLayout (仪表盘/分析/设置/通用页面)

**路由前缀**: `/`

**包含页面** (19个):
1. dashboard - 仪表盘
2. analysis - 数据分析
3. industry-concept-analysis - 行业概念分析
4. stocks - 股票管理
5. stock-detail - 股票详情
6. technical - 技术分析
7. indicators - 指标库
8. trade - 交易管理
9. tasks - 任务管理
10. settings - 系统设置
11. portfolio - 投资组合
12. system-architecture - 系统架构
13. system-database-monitor - 数据库监控
14. openstock-demo - OpenStock演示
15. pyprofiling-demo - PyProfiling演示
16. freqtrade-demo - Freqtrade演示
17. stock-analysis-demo - Stock-Analysis演示
18. tdxpy-demo - pytdx演示
19. smart-data-test - 智能数据源测试

**特点**:
- 核心业务页面
- 顶部导航栏
- 侧边栏菜单
- 面包屑导航

---

### MarketLayout (市场行情/TDX行情/实时监控)

**路由前缀**: `/market`

**包含页面** (3个):
1. market - 市场行情
2. tdx-market - TDX行情
3. realtime - 实时监控

**特点**:
- 市场数据展示
- WebSocket实时更新
- 高频刷新

---

### DataLayout (市场数据分析/资金流向/ETF/龙虎榜等)

**路由前缀**: `/market-data`

**包含页面** (5个):
1. fund-flow - 资金流向
2. etf - ETF行情
3. chip-race - 竞价抢筹
4. lhb - 龙虎榜
5. wencai - 问财筛选

**特点**:
- 深度数据分析
- 表格展示
- 数据筛选和导出

---

### RiskLayout (风险监控/公告监控)

**路由前缀**: `/risk-monitor`

**包含页面** (2个):
1. risk - 风险监控
2. announcement - 公告监控

**特点**:
- 风险预警
- 监控仪表板
- 告警系统

---

### StrategyLayout (策略管理/回测分析/交易信号)

**路由前缀**: `/strategy-hub`

**包含页面** (2个):
1. strategy - 策略管理
2. backtest - 回测分析

**特点**:
- 策略配置
- 回测报告
- 性能分析

---

## 📁 文件组织结构

```
web/frontend/src/views/
├── MainLayout页面 (19个)
│   ├── Dashboard.vue              # 仪表盘 (P0)
│   ├── Analysis.vue               # 数据分析 (P0)
│   ├── IndustryConceptAnalysis.vue # 行业概念分析 (P2)
│   ├── Stocks.vue                 # 股票管理 (P0)
│   ├── StockDetail.vue            # 股票详情 (P1)
│   ├── TechnicalAnalysis.vue      # 技术分析 (P1)
│   ├── IndicatorLibrary.vue       # 指标库 (P1)
│   ├── TradeManagement.vue        # 交易管理 (P0)
│   ├── TaskManagement.vue         # 任务管理 (P2)
│   ├── Settings.vue               # 系统设置 (P0)
│   ├── PortfolioManagement.vue    # 投资组合 (P1)
│   ├── OpenStockDemo.vue          # OpenStock演示 (P2)
│   ├── PyprofilingDemo.vue        # PyProfiling演示 (P2)
│   ├── FreqtradeDemo.vue          # Freqtrade演示 (P2)
│   ├── StockAnalysisDemo.vue      # Stock-Analysis演示 (P2)
│   ├── TdxpyDemo.vue              # pytdx演示 (P2)
│   └── SmartDataSourceTest.vue    # 智能数据源测试 (P2)
│
├── MarketLayout页面 (3个)
│   ├── Market.vue                 # 市场行情 (P0)
│   ├── TdxMarket.vue              # TDX行情 (P2)
│   └── RealTimeMonitor.vue        # 实时监控 (P1)
│
├── DataLayout页面 (5个)
│   └── ../components/market/
│       ├── FundFlowPanel.vue      # 资金流向 (P2)
│       ├── ETFDataTable.vue       # ETF行情 (P2)
│       ├── ChipRaceTable.vue      # 竞价抢筹 (P2)
│       ├── LongHuBangTable.vue    # 龙虎榜 (P2)
│       └── WencaiPanelV2.vue      # 问财筛选 (P2)
│
├── RiskLayout页面 (2个)
│   ├── RiskMonitor.vue            # 风险监控 (P1)
│   └── announcement/
│       └── AnnouncementMonitor.vue # 公告监控 (P2)
│
├── StrategyLayout页面 (2个)
│   ├── StrategyManagement.vue     # 策略管理 (P1)
│   └── BacktestAnalysis.vue       # 回测分析 (P1)
│
├── 系统管理页面 (2个)
│   ├── system/
│   │   ├── Architecture.vue       # 系统架构 (P2)
│   │   └── DatabaseMonitor.vue    # 数据库监控 (P2)
│
└── 认证页面 (1个)
    └── Login.vue                   # 登录 (P2)
```

---

## 🧪 测试覆盖情况

### E2E测试完成度

| 优先级 | 页面数 | 已测试 | 覆盖率 | 状态 |
|--------|--------|--------|--------|------|
| **P0** | 6 | 6 | 100% | ✅ 完成 |
| **P1** | 8 | 8 | 100% | ✅ 完成 |
| **P2** | 17 | 14 | 82.4% | ⚠️ 部分完成 |

### P0测试详细结果

| 页面 | 通过率 | 检查项 | 状态 | 截图 |
|------|--------|--------|------|------|
| Dashboard | 87.5% | 8/8 | ✅ | dashboard_p0.png |
| Market | 100% | 5/5 | ✅ | market_p0.png |
| Stocks | 100% | 6/6 | ✅ | stocks_p0.png |
| Analysis | 100% | 6/6 | ✅ | analysis_p0.png |
| Trade | 87.5% | 7/8 | ✅ | trade_p0.png |
| Settings | 83.3% | 5/6 | ✅ | settings_p0.png |

**详细报告**: [P0测试验证报告](./P0_TEST_VALIDATION_REPORT.md)

---

## 📊 页面访问路径

### 完整URL列表

```
http://localhost:3020/#/login
http://localhost:3020/#/dashboard
http://localhost:3020/#/analysis
http://localhost:3020/#/analysis/industry-concept
http://localhost:3020/#/stocks
http://localhost:3020/#/stock-detail/000001
http://localhost:3020/#/technical
http://localhost:3020/#/indicators
http://localhost:3020/#/trade
http://localhost:3020/#/tasks
http://localhost:3020/#/settings
http://localhost:3020/#/portfolio
http://localhost:3020/#/system/architecture
http://localhost:3020/#/system/database-monitor
http://localhost:3020/#/openstock-demo
http://localhost:3020/#/pyprofiling-demo
http://localhost:3020/#/freqtrade-demo
http://localhost:3020/#/stock-analysis-demo
http://localhost:3020/#/tdxpy-demo
http://localhost:3020/#/smart-data-test
http://localhost:3020/#/market/list
http://localhost:3020/#/market/tdx-market
http://localhost:3020/#/market/realtime
http://localhost:3020/#/market-data/fund-flow
http://localhost:3020/#/market-data/etf
http://localhost:3020/#/market-data/chip-race
http://localhost:3020/#/market-data/lhb
http://localhost:3020/#/market-data/wencai
http://localhost:3020/#/risk-monitor/overview
http://localhost:3020/#/risk-monitor/announcement
http://localhost:3020/#/strategy-hub/management
http://localhost:3020/#/strategy-hub/backtest
```

---

## 🔍 快速查找

### 按功能分类

**市场数据**:
- Market (市场行情) - P0
- TdxMarket (TDX行情) - P2
- RealTimeMonitor (实时监控) - P1
- FundFlowPanel (资金流向) - P2
- ETFDataTable (ETF行情) - P2
- ChipRaceTable (竞价抢筹) - P2
- LongHuBangTable (龙虎榜) - P2
- WencaiPanelV2 (问财筛选) - P2

**分析工具**:
- Analysis (数据分析) - P0
- TechnicalAnalysis (技术分析) - P1
- IndicatorLibrary (指标库) - P1
- IndustryConceptAnalysis (行业概念分析) - P2
- StockDetail (股票详情) - P1

**交易管理**:
- TradeManagement (交易管理) - P0
- PortfolioManagement (投资组合) - P1
- Stocks (股票管理) - P0

**策略回测**:
- StrategyManagement (策略管理) - P1
- BacktestAnalysis (回测分析) - P1

**风险监控**:
- RiskMonitor (风险监控) - P1
- AnnouncementMonitor (公告监控) - P2

**系统管理**:
- Dashboard (仪表盘) - P0
- Settings (系统设置) - P0
- TaskManagement (任务管理) - P2
- Architecture (系统架构) - P2
- DatabaseMonitor (数据库监控) - P2

**功能演示**:
- OpenStockDemo - P2
- PyprofilingDemo - P2
- FreqtradeDemo - P2
- StockAnalysisDemo - P2
- TdxpyDemo - P2
- SmartDataSourceTest - P2

---

## 📝 附录

### A. 未使用的Vue文件

以下文件存在但未在路由中注册：

```
views/EnhancedDashboard.vue        # 增强版仪表盘（未使用）
views/Phase4Dashboard.vue          # Phase4仪表板（未使用）
views/KLineDemo.vue                # K线演示（未使用）
views/MarketData.vue               # 市场数据（未使用）
views/Wencai.vue                   # 问财旧版（未使用）
views/monitor.vue                  # 监控页面（未使用）
views/demo/Wencai.vue              # 问财演示（未使用）
views/demo/Phase4Dashboard.vue     # Phase4演示（未使用）
views/market/MarketDataView.vue    # 市场数据视图（未使用）
views/monitoring/                  # 监控模块（未使用）
├── AlertRulesManagement.vue
├── MonitoringDashboard.vue
├── RiskDashboard.vue
└── WatchlistManagement.vue
views/strategy/                    # 策略模块（未使用）
├── BatchScan.vue
├── ResultsQuery.vue
├── SingleRun.vue
├── StatsAnalysis.vue
└── StrategyList.vue
views/technical/                   # 技术分析模块（未使用）
└── TechnicalAnalysis.vue
views/trade-management/            # 交易管理组件（未使用）
└── components/
    ├── PortfolioOverview.vue
    ├── PositionsTab.vue
    ├── StatisticsTab.vue
    ├── TradeDialog.vue
    └── TradeHistoryTab.vue
```

**说明**: 这些文件可能是旧版本、备份文件或待集成的功能模块。

### B. 路由配置文件

**位置**: `web/frontend/src/router/index.js`

**配置结构**:
- Hash模式路由
- 5个嵌套布局 (MainLayout, MarketLayout, DataLayout, RiskLayout, StrategyLayout)
- 31个注册页面
- 认证守卫已禁用

### C. 相关文档

- 📖 [E2E优化完成报告](./E2E_OPTIMIZATION_COMPLETION_REPORT.md)
- 📖 [P0测试验证报告](./P0_TEST_VALIDATION_REPORT.md)
- 📖 [E2E自动化测试完成报告](./E2E_AUTOMATED_TESTING_COMPLETION_REPORT.md)

---

**报告生成时间**: 2026-01-08
**下次更新**: 根据页面变更动态更新
**维护者**: Main CLI (Claude Code)
