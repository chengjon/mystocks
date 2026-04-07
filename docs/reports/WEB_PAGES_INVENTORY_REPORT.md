# MyStocks Web端页面清单报告

> **历史总结说明**:
> 本文件是阶段性总结、报告、状态、修复记录、验证结果或交付回执，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内统计值、完成状态、结论、验证结果和修复结论如未重新复核，应视为历史快照，不得直接当作当前事实。


**生成时间**: 2026-01-02
**报告版本**: v1.0
**项目**: MyStocks量化交易数据管理系统

---

## 📊 统计概览

| 分类 | 数量 |
|------|------|
| **已实现页面** | 42 |
| **Demo页面** | 9 |
| **子页面** | 12 |
| **设计文档中未实现** | 约15+ |

---

## 一、已实现页面清单

### 1.1 核心业务页面 (MainLayout)

| 序号 | 页面名称 | 文件路径 | 路由路径 | 功能描述 | API接口 | 状态 |
|------|----------|----------|----------|----------|---------|------|
| 1 | **仪表盘** | `views/Dashboard.vue` | `/dashboard` | 市场总览、实时市场智能与投资组合监控，展示市场热度、板块表现、资金流向等 | `/api/market/overview`, `/api/market/fund-flow` | ✅ 已实现 |
| 2 | **数据分析** | `views/Analysis.vue` | `/analysis` | 数据分析中心，提供市场数据分析功能 | `/api/data/*` | ✅ 已实现 |
| 3 | **行业概念分析** | `views/IndustryConceptAnalysis.vue` | `/analysis/industry-concept` | 行业和概念板块分析，展示行业涨跌、资金流向 | `/api/industry-concept/*` | ✅ 已实现 |
| 4 | **股票管理** | `views/Stocks.vue` | `/stocks` | 股票列表管理，搜索、筛选、添加自选股 | `/api/stocks/*` | ✅ 已实现 |
| 5 | **股票详情** | `views/StockDetail.vue` | `/stock-detail/:symbol` | 单个股票详情，K线图、技术指标、财务数据 | `/api/market/kline`, `/api/stocks/:symbol` | ✅ 已实现 |
| 6 | **技术分析** | `views/TechnicalAnalysis.vue` | `/technical` | 技术分析工具，支持多种技术指标和图表 | `/api/technical/*` | ✅ 已实现 |
| 7 | **指标库** | `views/IndicatorLibrary.vue` | `/indicators` | 技术指标库，展示所有可用的技术指标 | `/api/indicators/*` | ✅ 已实现 |
| 8 | **交易管理** | `views/TradeManagement.vue` | `/trade` | 交易管理界面，下单、持仓查询、交易记录 | `/api/trade/*` | ✅ 已实现 |
| 9 | **任务管理** | `views/TaskManagement.vue` | `/tasks` | 任务管理，查看和管理系统后台任务 | `/api/tasks/*` | ✅ 已实现 |
| 10 | **系统设置** | `views/Settings.vue` | `/settings` | 系统设置，用户偏好、系统配置 | `/api/settings/*` | ✅ 已实现 |

### 1.2 市场行情页面 (MarketLayout)

| 序号 | 页面名称 | 文件路径 | 路由路径 | 功能描述 | API接口 | 状态 |
|------|----------|----------|----------|----------|---------|------|
| 11 | **市场行情** | `views/Market.vue` | `/market/list` | 市场行情列表，展示所有股票实时行情 | `/api/market/overview` | ✅ 已实现 |
| 12 | **TDX行情** | `views/TdxMarket.vue` | `/market/tdx-market` | 通达信行情数据接口展示 | `/api/tdx/*` | ✅ 已实现 |
| 13 | **实时监控** | `views/RealTimeMonitor.vue` | `/market/realtime` | 实时市场监控，SSE实时推送 | `/api/sse/*` | ✅ 已实现 |

### 1.3 市场数据页面 (DataLayout)

| 序号 | 页面名称 | 文件路径 | 路由路径 | 功能描述 | API接口 | 状态 |
|------|----------|----------|----------|----------|---------|------|
| 14 | **资金流向** | `components/market/FundFlowPanel.vue` | `/market-data/fund-flow` | 市场资金流向分析，板块资金流入流出 | `/api/market/fund-flow` | ✅ 已实现 |
| 15 | **ETF行情** | `components/market/ETFDataTable.vue` | `/market-data/etf` | ETF基金行情列表和查询 | `/api/market/etf/list` | ✅ 已实现 |
| 16 | **竞价抢筹** | `components/market/ChipRaceTable.vue` | `/market-data/chip-race` | 竞价抢筹数据表 | `/api/market/chip-race` | ✅ 已实现 |
| 17 | **龙虎榜** | `components/market/LongHuBangTable.vue` | `/market-data/lhb` | 龙虎榜数据，展示异动股票 | `/api/market/lhb` | ✅ 已实现 |
| 18 | **问财筛选** | `components/market/WencaiPanelV2.vue` | `/market-data/wencai` | 问财智能选股工具 | `/api/wencai/*` | ✅ 已实现 |

### 1.4 风险监控页面 (RiskLayout)

| 序号 | 页面名称 | 文件路径 | 路由路径 | 功能描述 | API接口 | 状态 |
|------|----------|----------|----------|----------|---------|------|
| 19 | **风险监控** | `views/RiskMonitor.vue` | `/risk-monitor/overview` | 风险监控仪表板，展示投资组合风险指标 | `/api/risk/*` | ✅ 已实现 |
| 20 | **公告监控** | `views/announcement/AnnouncementMonitor.vue` | `/risk-monitor/announcement` | 上市公司公告实时监控 | `/api/announcement/*` | ✅ 已实现 |

### 1.5 策略中心页面 (StrategyLayout)

| 序号 | 页面名称 | 文件路径 | 路由路径 | 功能描述 | API接口 | 状态 |
|------|----------|----------|----------|----------|---------|------|
| 21 | **策略管理** | `views/StrategyManagement.vue` | `/strategy-hub/management` | 策略CRUD管理，创建、编辑、删除策略 | `/api/v1/strategy/*` | ✅ 已实现 |
| 22 | **回测分析** | `views/BacktestAnalysis.vue` | `/strategy-hub/backtest` | 策略回测，查看回测结果和性能指标 | `/api/v1/strategy/backtest` | ✅ 已实现 |

### 1.6 系统监控页面 (System)

| 序号 | 页面名称 | 文件路径 | 路由路径 | 功能描述 | API接口 | 状态 |
|------|----------|----------|----------|----------|---------|------|
| 23 | **系统架构** | `views/system/Architecture.vue` | `/system/architecture` | 系统架构可视化，展示模块依赖关系 | `/api/system/architecture` | ✅ 已实现 |
| 24 | **数据库监控** | `views/system/DatabaseMonitor.vue` | `/system/database-monitor` | 数据库性能监控，连接池、查询性能 | `/api/monitoring/database` | ✅ 已实现 |
| 25 | **监控仪表板** | `views/monitoring/MonitoringDashboard.vue` | 子路由 | 监控仪表板，展示系统性能指标 | `/api/monitoring/*` | ✅ 已实现 |
| 26 | **告警规则管理** | `views/monitoring/AlertRulesManagement.vue` | 子路由 | 告警规则配置和管理 | `/api/monitoring/alerts` | ✅ 已实现 |

### 1.7 策略子页面 (Strategy Sub-pages)

| 序号 | 页面名称 | 文件路径 | 功能描述 | API接口 | 状态 |
|------|----------|----------|----------|---------|------|
| 27 | **策略列表** | `views/strategy/StrategyList.vue` | 策略列表展示 | `/api/v1/strategy/*` | ✅ 已实现 |
| 28 | **单次运行** | `views/strategy/SingleRun.vue` | 单次策略执行 | `/api/v1/strategy/run` | ✅ 已实现 |
| 29 | **批量扫描** | `views/strategy/BatchScan.vue` | 批量股票扫描 | `/api/v1/strategy/batch-scan` | ✅ 已实现 |
| 30 | **结果查询** | `views/strategy/ResultsQuery.vue` | 策略运行结果查询 | `/api/v1/strategy/results` | ✅ 已实现 |
| 31 | **统计分析** | `views/strategy/StatsAnalysis.vue` | 策略统计分析 | `/api/v1/strategy/stats` | ✅ 已实现 |

### 1.8 技术分析子页面

| 序号 | 页面名称 | 文件路径 | 功能描述 | API接口 | 状态 |
|------|----------|----------|----------|---------|------|
| 32 | **技术分析** | `views/technical/TechnicalAnalysis.vue` | 技术分析工具 | `/api/technical/*` | ✅ 已实现 |

### 1.9 Demo页面

| 序号 | 页面名称 | 文件路径 | 路由路径 | 功能描述 | API接口 | 状态 |
|------|----------|----------|----------|----------|---------|------|
| 33 | **OpenStock演示** | `views/OpenStockDemo.vue` | `/openstock-demo` | OpenStock库功能演示 | Mock数据 | ✅ Demo |
| 34 | **PyProfiling演示** | `views/PyprofilingDemo.vue` | `/pyprofiling-demo` | PyProfiling性能分析演示 | Mock数据 | ✅ Demo |
| 35 | **Freqtrade演示** | `views/FreqtradeDemo.vue` | `/freqtrade-demo` | Freqtrade交易机器人演示 | Mock数据 | ✅ Demo |
| 36 | **StockAnalysis演示** | `views/StockAnalysisDemo.vue` | `/stock-analysis-demo` | 股票分析功能演示 | Mock数据 | ✅ Demo |
| 37 | **pytdx演示** | `views/TdxpyDemo.vue` | `/tdxpy-demo` | pytdx通达信接口演示 | `/api/tdx/*` | ✅ Demo |
| 38 | **智能数据源测试** | `views/SmartDataSourceTest.vue` | `/smart-data-test` | 智能数据源切换测试 | `/api/multi-source/*` | ✅ Demo |
| 39 | **问财演示** | `views/demo/Wencai.vue` | - | 问财功能演示 | `/api/wencai/*` | ✅ Demo |
| 40 | **市场数据视图** | `views/market/MarketDataView.vue` | - | 市场数据展示 | `/api/market/*` | ✅ Demo |
| 41 | **K线Demo** | `views/KLineDemo.vue` | - | K线图示例 | Mock数据 | ✅ Demo |

### 1.10 其他页面

| 序号 | 页面名称 | 文件路径 | 路由路径 | 功能描述 | API接口 | 状态 |
|------|----------|----------|----------|----------|---------|------|
| 42 | **登录** | `views/Login.vue` | `/login` | 用户登录页面 | `/api/auth/*` | ✅ 已实现 |
| 43 | **404** | `views/NotFound.vue` | `/:pathMatch(.*)*` | 404错误页面 | - | ✅ 已实现 |
| 44 | **监控页面** | `views/monitor.vue` | - | 系统监控页面 | `/api/monitoring/*` | ✅ 已实现 |

---

## 二、设计文档中已设计但未实现的页面

### 2.1 根据设计文档（docs/design/）

| 序号 | 页面名称 | 设计文档 | 功能描述 | 优先级 |
|------|----------|----------|----------|--------|
| 1 | **GPU监控页面** | GPU加速设计文档 | GPU使用率、内存、温度监控 | 高 |
| 2 | **用户管理** | 系统设计文档 | 用户CRUD、权限管理 | 中 |
| 3 | **数据源管理** | 多数据源设计文档 | 数据源配置、健康检查、切换 | 高 |
| 4 | **报警通知管理** | 监控系统设计 | 报警规则、通知渠道、历史记录 | 中 |
| 5 | **数据备份恢复** | 运维管理文档 | 数据备份、恢复、迁移 | 高 |
| 6 | **报表中心** | 报表设计文档 | 各类统计报表、导出 | 中 |
| 7 | **量化策略商城** | 策略管理文档 | 策略分享、订阅、评分 | 低 |
| 8 | **模拟交易** | 交易管理文档 | 模拟账户、虚拟资金、比赛 | 中 |
| 9 | **社区论坛** | 社区设计文档 | 策略讨论、经验分享 | 低 |
| 10 | **帮助中心** | 用户帮助文档 | 使用教程、FAQ、视频 | 中 |

### 2.2 根据路由配置但未实现

| 序号 | 路由路径 | 配置状态 | 说明 |
|----------|----------|----------|------|
| 1 | `/gpu-monitoring` | 已注释掉 | GPUMonitoring.vue文件不存在 |
| 2 | `/signals` | 未配置 | 交易信号页面未实现 |

---

## 三、API接口清单

### 3.1 市场数据API (`/api/market/`)

| 端点 | 方法 | 功能 | 使用页面 |
|------|------|------|----------|
| `/overview` | GET | 市场总览 | Dashboard |
| `/fund-flow` | GET | 资金流向 | Dashboard, FundFlowPanel |
| `/kline` | GET | K线数据 | StockDetail, TechnicalAnalysis |
| `/etf/list` | GET | ETF列表 | ETFDataTable |
| `/lhb` | GET | 龙虎榜 | LongHuBangTable |
| `/chip-race` | GET | 竞价抢筹 | ChipRaceTable |

### 3.2 策略API (`/api/v1/strategy/`)

| 端点 | 方法 | 功能 | 使用页面 |
|------|------|------|----------|
| `/strategies` | GET | 策略列表 | StrategyManagement |
| `/strategies` | POST | 创建策略 | StrategyManagement |
| `/strategies/:id` | GET | 策略详情 | StrategyManagement |
| `/strategies/:id` | PUT | 更新策略 | StrategyManagement |
| `/strategies/:id` | DELETE | 删除策略 | StrategyManagement |
| `/backtest` | POST | 执行回测 | BacktestAnalysis |

### 3.3 交易API (`/api/trade/`)

| 端点 | 方法 | 功能 | 使用页面 |
|------|------|------|----------|
| `/orders` | GET | 订单列表 | TradeManagement |
| `/orders` | POST | 创建订单 | TradeManagement |
| `/positions` | GET | 持仓查询 | TradeManagement |
| `/balance` | GET | 账户余额 | TradeManagement |

### 3.4 监控API (`/api/monitoring/`)

| 端点 | 方法 | 功能 | 使用页面 |
|------|------|------|----------|
| `/database` | GET | 数据库监控 | DatabaseMonitor |
| `/alerts` | GET | 告警列表 | AlertRulesManagement |
| `/alerts` | POST | 创建告警 | AlertRulesManagement |
| `/metrics` | GET | 性能指标 | MonitoringDashboard |

### 3.5 技术分析API (`/api/technical/`)

| 端点 | 方法 | 功能 | 使用页面 |
|------|------|------|----------|
| `/indicators` | GET | 指标列表 | IndicatorLibrary |
| `/calculate` | POST | 计算指标 | TechnicalAnalysis |
| `/patterns` | GET | 形态识别 | TechnicalAnalysis |

### 3.6 其他API

| 端点 | 方法 | 功能 | 使用页面 |
|------|------|------|----------|
| `/api/announcement/*` | GET | 公告数据 | AnnouncementMonitor |
| `/api/tdx/*` | GET | TDX数据 | TdxMarket |
| `/api/wencai/*` | POST | 问财选股 | WencaiPanel |
| `/api/risk/*` | GET | 风险评估 | RiskMonitor |
| `/api/auth/login` | POST | 用户登录 | Login |
| `/api/tasks/*` | GET | 任务列表 | TaskManagement |

---

## 四、页面功能说明

### 4.1 Dashboard（仪表盘）

**主要功能**:
- 市场热度分析图表
- 行业资金流向
- 板块表现监控
- 自选股票列表
- 策略信号展示

**数据来源**:
- 市场总览API
- 资金流向API
- 板块数据API

**交互功能**:
- 实时刷新
- 数据筛选
- 图表交互
- 快捷操作

### 4.2 StockDetail（股票详情）

**主要功能**:
- K线图表展示
- 技术指标叠加
- 财务数据展示
- 新闻公告
- 交易信号

**数据来源**:
- K线数据API
- 财务数据API
- 新闻API

**交互功能**:
- 周期切换
- 指标选择
- 时间范围调整
- 添加自选

### 4.3 StrategyManagement（策略管理）

**主要功能**:
- 策略列表展示
- 创建新策略
- 编辑策略参数
- 删除策略
- 启用/禁用策略

**数据来源**:
- 策略API
- 回测API

**交互功能**:
- 表格排序筛选
- 策略配置表单
- 参数验证
- 批量操作

### 4.4 BacktestAnalysis（回测分析）

**主要功能**:
- 回测参数设置
- 回测结果展示
- 收益曲线图
- 性能指标表
- 交易记录明细

**数据来源**:
- 回测API
- K线数据API

**交互功能**:
- 参数优化
- 结果对比
- 报告导出
- 策略对比

---

## 五、技术架构

### 5.1 前端技术栈

- **框架**: Vue 3.4+ (Composition API)
- **路由**: Vue Router 4
- **UI库**: Element Plus
- **图表**: ECharts
- **状态管理**: Pinia
- **HTTP客户端**: Axios
- **样式**: SCSS + ArtDeco主题

### 5.2 后端技术栈

- **框架**: FastAPI 0.114+
- **数据库**: PostgreSQL 17+, TDengine 3.3+
- **ORM**: SQLAlchemy 2.0+
- **认证**: JWT
- **文档**: Swagger/OpenAPI
- **日志**: Structlog

### 5.3 布局系统

项目使用5种布局组件：

1. **MainLayout**: 主布局（仪表盘、分析、设置等）
2. **MarketLayout**: 市场布局（行情、TDX、实时监控）
3. **DataLayout**: 数据布局（资金流向、ETF、龙虎榜等）
4. **RiskLayout**: 风险布局（风险监控、公告监控）
5. **StrategyLayout**: 策略布局（策略管理、回测分析）

---

## 六、开发建议

### 6.1 优先开发页面

根据业务价值和技术复杂度，建议优先开发：

1. **GPU监控页面** - 配合GPU加速引擎
2. **数据源管理页面** - 多数据源切换需求
3. **用户管理页面** - 多用户系统需求
4. **报警通知管理** - 运维监控需求

### 6.2 需要优化的页面

1. **Dashboard** - 数据量大时性能优化
2. **StockDetail** - K线图表加载速度
3. **StrategyManagement** - 表格性能优化
4. **BacktestAnalysis** - 回测结果展示优化

### 6.3 可以合并的页面

1. 多个Demo页面可以合并为一个Demo中心
2. 监控相关页面可以统一到监控布局

---

## 七、附录

### 7.1 文件目录结构

```
web/frontend/src/
├── views/                    # 页面组件
│   ├── Dashboard.vue         # 仪表盘
│   ├── Market.vue            # 市场行情
│   ├── StockDetail.vue       # 股票详情
│   ├── StrategyManagement.vue # 策略管理
│   ├── BacktestAnalysis.vue  # 回测分析
│   ├── RiskMonitor.vue       # 风险监控
│   ├── TechnicalAnalysis.vue # 技术分析
│   ├── announcement/         # 公告相关
│   ├── demo/                 # Demo页面
│   ├── market/               # 市场数据
│   ├── monitoring/           # 监控相关
│   ├── strategy/             # 策略子页面
│   ├── system/               # 系统页面
│   └── technical/            # 技术分析
├── layouts/                  # 布局组件
│   ├── MainLayout.vue
│   ├── MarketLayout.vue
│   ├── DataLayout.vue
│   ├── RiskLayout.vue
│   └── StrategyLayout.vue
├── components/               # 公共组件
│   └── market/               # 市场数据组件
├── router/                   # 路由配置
├── api/                      # API服务
│   └── services/             # API服务层
└── stores/                   # 状态管理
```

### 7.2 API服务文件

```
web/frontend/src/api/services/
├── marketService.ts          # 市场数据API
├── strategyService.ts        # 策略API
├── apiClient.ts              # API客户端
└── types/                    # TypeScript类型定义
    └── generated-types.ts    # 自动生成的类型
```

### 7.3 后端API模块

```
web/backend/app/api/
├── market.py                 # 市场数据路由
├── strategy.py               # 策略路由
├── trade/                    # 交易路由
├── technical/                # 技术分析路由
├── monitoring/               # 监控路由
├── announcement/             # 公告路由
└── contract/                 # API契约管理
```

---

**报告结束**

**下一步**: 根据此清单，为每个页面生成HTML样本文件到 `docs/design/html_sample/` 目录。
