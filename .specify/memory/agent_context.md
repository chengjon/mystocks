# Agent Context - 股票数据扩展功能集成

**Last Updated**: 2025-10-14
**Feature**: 003-inside-mystocks
**Phase**: Phase 1 - Design Complete

---

## 技术栈更新

### 后端技术栈 (Backend)

#### 现有技术 (EXISTING)
- **语言**: Python 3.12
- **Web框架**: FastAPI 0.104.1
- **数据处理**: pandas 2.1.3, numpy 1.26.2
- **技术指标**: TA-Lib 0.4.28 (161个指标已实现)
- **数据库ORM**: SQLAlchemy 2.0.23
- **数据库驱动**:
  - PostgreSQL: psycopg2-binary 2.9.9
  - MySQL: pymysql 1.1.0
  - Redis: redis 5.0.1
  - TDengine: taos 2.7.0 (可选)

#### 新增技术 (NEW)
- **数据源适配器**:
  - akshare 1.12.0+ (ENHANCE - 扩展4个新方法)
  - requests 2.31.0 (用于TQLEX接口)
- **策略引擎**: 自研 (基于TA-Lib)
- **回测引擎**: 自研 (NumPy-based)

### 前端技术栈 (Frontend)

#### 现有技术 (EXISTING)
- **框架**: Vue 3.3.8
- **路由**: Vue Router 4.2.5
- **状态管理**: Pinia 2.1.7
- **UI组件库**: Element Plus 2.4.3
- **HTTP客户端**: Axios 1.6.2
- **K线图表**: klinecharts 9.6.0 ✅ (已实现，支持161个指标叠加)

#### 新增技术 (NEW)
- **数据可视化**: ECharts 5.4.3 (用于资金流向图表)
- **新增页面**:
  - 市场行情模块 (MarketData/)
  - 策略管理模块 (Strategy/)
  - 回测分析模块 (BacktestAnalysis/)

### 数据库技术栈 (Databases)

#### PostgreSQL + TimescaleDB (EXISTING + ENHANCE)
**用途**: 主数据库，存储时序数据
**新增表** (7个hypertable):
- `stock_fund_flow` - 个股资金流向
- `etf_spot_data` - ETF实时数据
- `chip_race_data` - 竞价抢筹数据
- `stock_lhb_detail` - 龙虎榜数据
- `strategy_signals` - 策略信号
- `backtest_trades` - 回测交易明细
- `backtest_results` - 回测结果汇总 (非hypertable)

**优化策略**:
- 时间分区: 按月分区 (chunk_time_interval = 1 month)
- 自动压缩: 30天后压缩 (压缩率 5:1 到 10:1)
- 数据保留: 3年历史数据

#### MySQL/MariaDB (EXISTING + ENHANCE)
**用途**: 参考数据和元数据
**新增表** (2个):
- `strategy_configs` - 策略配置
- `dividend_data` - 分红配送数据

#### Redis (EXISTING)
**用途**: 实时缓存
**缓存策略**:
- 实时行情: TTL 5分钟
- 策略信号: TTL 1小时
- 技术指标: TTL 1天

---

## 架构组件更新

### 数据适配器层 (Adapters)

#### 1. akshare_adapter.py (EXISTING + ENHANCE)
**状态**: 80%复用 + 20%扩展
**现有方法** (100%复用):
- `get_stock_daily()` - 股票日线数据 ✅
- `get_index_daily()` - 指数日线数据 ✅
- `get_stock_basic()` - 股票基本信息 ✅
- `get_real_time_data()` - 实时行情 ✅
- `get_ths_industry_summary()` - 同花顺行业数据 ✅

**新增方法** (ENHANCE):
- `get_etf_spot()` - ETF实时行情 🆕
- `get_stock_fund_flow()` - 个股资金流向 🆕
- `get_stock_lhb_detail()` - 龙虎榜数据 🆕
- `get_block_trade()` - 大宗交易数据 🆕

#### 2. tqlex_adapter.py (NEW)
**状态**: 全新适配器
**数据源**: 通达信TQLEX接口
**方法**:
- `get_chip_race_open()` - 早盘抢筹数据 🆕
- `get_chip_race_end()` - 尾盘抢筹数据 🆕

**设计特点**:
- 复用akshare_adapter的重试机制模式
- 使用requests库进行HTTP请求
- 支持Token认证

#### 3. financial_adapter.py (EXISTING)
**状态**: 无变更，继续复用
**用途**: 财务数据获取

### 服务层 (Services)

#### 1. indicator_calculator.py (EXISTING)
**状态**: 100%复用，无需修改
**功能**: 计算161个TA-Lib技术指标
**使用场景**:
- 前端技术分析模块
- 策略引擎内部调用
- 回测引擎内部调用

#### 2. data_service.py (EXISTING)
**状态**: 100%复用
**功能**:
- 从PostgreSQL加载OHLCV数据
- 自动从Akshare获取缺失数据 (auto-fetch)
- 数据格式转换 (DataFrame → NumPy arrays)

#### 3. strategy_engine.py (NEW)
**文件路径**: `web/backend/app/services/strategy_engine.py`
**功能**: 策略管理和信号生成
**核心类**:
- `StrategyBase` - 策略抽象基类
- `StrategyRegistry` - 策略注册表 (单例)
- 10个预定义策略类:
  1. `VolumeBreakoutStrategy` - 成交量突破策略
  2. `MAGoldenCrossStrategy` - 均线金叉策略
  3. `TurtleTradingStrategy` - 海龟交易法则
  4. `RSIReversalStrategy` - RSI反转策略
  5. `MACDDivergenceStrategy` - MACD背离策略
  6. `BollingerBreakoutStrategy` - 布林带突破策略
  7. `KDJOverboughtStrategy` - KDJ超买超卖策略
  8. `VolumePriceTrendStrategy` - 量价背离策略
  9. `DualMovingAverageStrategy` - 双均线策略
  10. `PriceChannelBreakoutStrategy` - 价格通道突破策略

**依赖**:
- `indicator_calculator` (EXISTING) - 计算技术指标
- `data_service` (EXISTING) - 获取OHLCV数据

#### 4. backtest_engine.py (NEW)
**文件路径**: `web/backend/app/services/backtest_engine.py`
**功能**: 策略回测和性能分析
**核心类**:
- `BacktestEngine` - 回测引擎
- `BacktestConfig` - 回测配置 (佣金、滑点、仓位)
- `BacktestResult` - 回测结果 (7个性能指标)

**性能指标**:
1. 总收益率 (Total Return)
2. 年化收益率 (Annual Return)
3. 夏普比率 (Sharpe Ratio)
4. 最大回撤 (Max Drawdown)
5. 胜率 (Win Rate)
6. 盈亏比 (Profit Factor)
7. 总交易次数 (Total Trades)

**依赖**:
- `strategy_engine` (NEW) - 生成交易信号
- `data_service` (EXISTING) - 获取历史数据

### API端点层 (API Endpoints)

#### 新增端点 (NEW)

**1. 市场行情API** (`/api/market/*`)
- `GET /market/fund-flow` - 个股资金流向
- `GET /market/etf/list` - ETF列表
- `GET /market/chip-race` - 竞价抢筹
- `GET /market/long-hu-bang` - 龙虎榜
- `GET /market/block-trade` - 大宗交易
- `GET /market/dividend` - 分红配送

**2. 策略管理API** (`/api/strategies/*`)
- `GET /strategies/list` - 策略列表
- `GET /strategies/{id}` - 策略详情
- `PUT /strategies/{id}/config` - 更新配置

**3. 信号API** (`/api/signals/*`)
- `POST /signals/generate` - 生成实时信号
- `GET /signals/history` - 历史信号查询

**4. 回测API** (`/api/backtest/*`)
- `POST /backtest/run` - 运行回测
- `GET /backtest/{id}` - 获取回测详情
- `GET /backtest/history` - 回测历史

#### 现有端点 (EXISTING - 无变更)
- `GET /api/indicators/registry` - 指标注册表
- `POST /api/indicators/calculate` - 计算指标
- `GET /api/data/stocks/daily` - 股票日线数据

### 前端组件层 (Frontend Components)

#### 新增页面 (NEW)

**1. 市场行情模块** (`src/views/MarketData/`)
- `FundFlowPanel.vue` - 资金流向面板 (ECharts柱状图)
- `ETFMonitor.vue` - ETF监控面板
- `ChipRacePanel.vue` - 竞价抢筹面板
- `LongHuBangPanel.vue` - 龙虎榜面板

**2. 策略管理模块** (`src/views/Strategy/`)
- `StrategyList.vue` - 策略列表
- `StrategyEditor.vue` - 策略参数编辑器
- `BacktestRunner.vue` - 回测运行器
- `BacktestResults.vue` - 回测结果展示

**3. 新增组件** (`src/components/`)
- `market/FundFlowChart.vue` - 资金流向图表 (ECharts)
- `strategy/ParameterEditor.vue` - 参数编辑器
- `strategy/BacktestChart.vue` - 回测权益曲线图 (ECharts)
- `strategy/PerformanceMetrics.vue` - 性能指标卡片

#### 现有组件 (EXISTING - 100%复用)
- `technical/KLineChart.vue` ✅ - K线图 (klinecharts)
- `technical/IndicatorSelector.vue` ✅ - 指标选择器
- `layout/index.vue` ✅ - 主布局

---

## 数据分类和路由策略

### 5-Tier 数据分类体系 (Constitution Principle I)

**新增数据类型分类**:

| 数据类型 | DataClassification | 目标数据库 | 更新频率 |
|---------|-------------------|-----------|---------|
| 个股资金流向 | `FUND_FLOW` | PostgreSQL+TSDB | 每日收盘后 |
| ETF数据 | `ETF_DATA` | PostgreSQL+TSDB | 每日收盘后 |
| 竞价抢筹 | `TRADING_ANALYSIS` | PostgreSQL+TSDB | 早盘/尾盘 |
| 龙虎榜 | `INSTITUTIONAL_FLOW` | PostgreSQL+TSDB | 每日收盘后 |
| 大宗交易 | `INSTITUTIONAL_FLOW` | PostgreSQL+TSDB | 每日收盘后 |
| 分红配送 | `CORPORATE_ACTION` | MySQL | 按公告更新 |
| 策略配置 | `STRATEGY_CONFIG` | MySQL | 用户配置 |
| 策略信号 | `TRADING_SIGNAL` | PostgreSQL+TSDB | 实时生成 |
| 回测结果 | `BACKTEST_RESULT` | PostgreSQL | 按需计算 |

### 自动路由流程 (Constitution Principle II)

```
[数据源] → [Adapter] → [UnifiedManager]
    ↓
[DataClassification.auto_route()]
    ↓
[目标数据库] (PostgreSQL / MySQL / Redis)
    ↓
[MonitoringDatabase] (日志记录)
```

---

## 开发工作流

### Phase 0: Research (✅ 已完成)
- ✅ 东方财富网API接口分析
- ✅ TQLEX接口集成设计
- ✅ 策略引擎架构设计
- ✅ 回测引擎实现方案
- ✅ 数据库Schema扩展设计
- ✅ 前端组件库集成方案

### Phase 1: Design (✅ 已完成)
- ✅ `data-model.md` - 13个实体的详细Schema
- ✅ `contracts/` - 4个OpenAPI规范文件
- ✅ `quickstart.md` - 环境搭建指南
- ✅ `agent_context.md` - 技术栈更新 (本文件)

### Phase 2: Tasks (⏳ 下一步)
运行 `/speckit.tasks` 生成实施任务列表

---

## 关键技术决策

### 1. 为什么选择ECharts而不是Chart.js?
**理由**:
- ✅ ECharts对大数据量渲染性能更好 (Canvas渲染)
- ✅ 内置丰富的金融图表类型 (K线图、柱状图、热力图)
- ✅ 与Element Plus生态集成良好
- ✅ 中文文档完善，社区活跃

### 2. 为什么策略引擎不使用backtrader?
**理由**:
- ✅ 项目已有161个TA-Lib指标实现，复用成本最低
- ✅ 自研引擎更轻量，依赖更少
- ✅ 与MyStocksUnifiedManager深度集成
- ✅ 完全掌控代码，方便定制和调试

### 3. 为什么使用TimescaleDB而不是InfluxDB?
**理由**:
- ✅ TimescaleDB基于PostgreSQL，无需学习新SQL
- ✅ 支持标准SQL JOIN操作
- ✅ 与现有PostgreSQL数据库无缝集成
- ✅ 压缩率高 (5:1 到 10:1)
- ✅ 自动分区和数据保留策略

### 4. 为什么TQLEX接口使用requests而不是httpx?
**理由**:
- ✅ requests是Python标准HTTP库，稳定性更好
- ✅ 项目现有依赖已包含requests
- ✅ TQLEX接口不需要异步请求
- ✅ 简单的重试机制已足够

---

## 性能优化策略

### 后端优化
1. **数据库查询优化**:
   - 所有时序表使用hypertable自动分区
   - 索引策略: (symbol, trade_date DESC)
   - 查询时间范围限制: 默认最多1年数据

2. **缓存策略**:
   - Redis缓存实时行情 (TTL 5分钟)
   - Redis缓存策略信号 (TTL 1小时)
   - 技术指标计算结果可选缓存

3. **异步处理**:
   - 回测任务异步执行 (Celery或FastAPI BackgroundTasks)
   - 大宗数据导入使用批量插入 (bulk_insert)

### 前端优化
1. **组件懒加载**:
   - 路由级别代码分割
   - 重量级图表组件按需加载

2. **虚拟滚动**:
   - 大数据量表格使用虚拟滚动 (Element Plus table-v2)
   - K线图只渲染可见区域

3. **数据缓存**:
   - Pinia状态持久化 (localStorage)
   - API响应缓存 (axios-cache-adapter)

---

## 测试策略

### 单元测试
- 策略引擎: pytest + pytest-mock
- 回测引擎: pytest + numpy.testing
- 数据适配器: pytest + responses (mock HTTP)

### 集成测试
- API端点: pytest + httpx
- 数据库操作: pytest + pytest-postgresql

### E2E测试
- 前端: Playwright或Cypress
- 关键流程:
  1. 登录 → 技术分析 → 指标计算
  2. 登录 → 策略管理 → 回测运行
  3. 登录 → 市场行情 → 资金流向查询

---

## 监控和日志

### 日志级别
- **DEBUG**: 详细的调试信息 (仅开发环境)
- **INFO**: 正常业务日志 (数据获取成功、策略执行等)
- **WARNING**: 警告信息 (数据源降级、缓存失效等)
- **ERROR**: 错误信息 (API调用失败、计算异常等)

### 监控指标
- API响应时间 (P50, P95, P99)
- 数据库查询耗时
- 策略计算耗时
- 回测任务完成率

---

## 安全考虑

### 1. 数据源Token管理
- 所有Token存储在 `.env` 文件
- 生产环境使用环境变量或密钥管理服务
- TQLEX_TOKEN定期轮换

### 2. API认证
- JWT Bearer Token认证
- Token过期时间: 24小时
- Refresh Token机制

### 3. 数据库安全
- 使用参数化查询 (防SQL注入)
- 数据库连接使用SSL
- 敏感字段加密存储

---

## 下一步行动

1. ✅ **Phase 1 Design 已完成** - 所有设计文档就绪
2. ⏳ **运行 `/speckit.tasks`** - 生成实施任务列表
3. ⏳ **Phase 2: Implementation** - 按任务列表实施
4. ⏳ **Phase 3: Testing** - 单元测试和集成测试
5. ⏳ **Phase 4: Deployment** - 生产环境部署

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-14
**Status**: ✅ Phase 1 Complete, Ready for Task Generation
