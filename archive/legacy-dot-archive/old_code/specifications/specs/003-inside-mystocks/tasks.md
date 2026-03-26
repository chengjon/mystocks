# Tasks: 股票数据扩展功能集成

**Feature**: 股票数据扩展功能集成 (Market Data, Technical Analysis, Strategy Management)
**Input**: Design documents from `/specs/003-inside-mystocks/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅
**Branch**: `003-inside-mystocks`
**Date**: 2025-10-14

**Tests**: 测试任务已标记为OPTIONAL。本项目遵循"测试可选"策略,测试任务将在基础功能实现后按需添加。

**Organization**: 任务按User Story组织,使每个Story可以独立实现和测试。

---

## 任务格式说明

- **[ID]**: 任务编号 (T001, T002, ...)
- **[P]**: 可并行执行 (不同文件,无依赖关系)
- **[Story]**: 所属用户故事 (US1, US2, US3, ...)
- **描述**: 包含具体文件路径

---

## Phase 1: Setup (共享基础设施)

**目的**: 项目初始化和基础结构搭建

### 项目结构设置

- [ ] **T001** [P] [SETUP] 更新 `table_config.yaml` 添加8个新表定义
  - 文件: `/opt/claude/mystocks_spec/table_config.yaml`
  - 内容: stock_fund_flow, etf_spot_data, chip_race_data, stock_lhb_detail, strategy_configs, strategy_signals, backtest_results, backtest_trades

- [ ] **T002** [P] [SETUP] 更新 `.env.example` 添加TQLEX配置模板
  - 文件: `/opt/claude/mystocks_spec/.env.example`
  - 内容: TQLEX_TOKEN, TQLEX_BASE_URL

- [ ] **T003** [P] [SETUP] 创建后端目录结构
  - 目录: `web/backend/app/api/`, `web/backend/app/services/`, `web/backend/app/models/`, `web/backend/app/schemas/`
  - 新增: `app/services/strategy_engine.py`, `app/services/backtest_engine.py`

- [ ] **T004** [P] [SETUP] 创建前端目录结构
  - 目录: `web/frontend/src/views/MarketData/`, `web/frontend/src/views/Strategy/`, `web/frontend/src/components/market/`, `web/frontend/src/components/strategy/`

- [ ] **T005** [P] [SETUP] 安装新的Python依赖
  - 命令: `pip install requests` (用于TQLEX适配器)
  - 验证: `pip list | grep requests`

- [ ] **T006** [P] [SETUP] 安装新的前端依赖
  - 命令: `npm install echarts --save` (用于资金流向图表)
  - 验证: `package.json` 包含 `echarts@5.4.3`

---

## Phase 2: Foundational (核心基础设施 - 阻塞所有User Stories)

**目的**: 核心基础设施必须在任何User Story之前完成

**⚠️ 关键**: 所有User Story工作必须等待此阶段完成

### 数据库Schema创建

- [ ] **T007** [FOUNDATION] 运行数据库迁移脚本创建8个新表
  - 命令: `python -c "from core import ConfigDrivenTableManager; mgr = ConfigDrivenTableManager(); mgr.batch_create_tables('table_config.yaml')"`
  - 验证: 执行SQL查询确认表已创建
  - 表列表: stock_fund_flow, etf_spot_data, chip_race_data, stock_lhb_detail, strategy_configs, strategy_signals, backtest_results, backtest_trades

- [ ] **T008** [FOUNDATION] 验证TimescaleDB hypertable创建成功
  - 命令: `psql -U postgres -d mystocks -c "SELECT * FROM timescaledb_information.hypertables;"`
  - 预期: 应列出7个hypertable (不包括strategy_configs)

- [ ] **T009** [FOUNDATION] 配置TimescaleDB自动压缩策略
  - SQL: 为每个hypertable配置30天后压缩
  - 文件: 参考 `data-model.md` 第6节

### 数据适配器层

- [ ] **T010** [P] [FOUNDATION] 创建TQLEX适配器 `adapters/tqlex_adapter.py` (NEW)
  - 类: `TqlexDataSource(IDataSource)`
  - 方法: `get_chip_race_open()`, `get_chip_race_end()`
  - 复用: akshare_adapter的重试机制和错误处理模式

- [ ] **T011** [P] [FOUNDATION] 扩展Akshare适配器 `adapters/akshare_adapter.py` (ENHANCE)
  - 新增方法1: `get_etf_spot()` - ETF实时行情
  - 新增方法2: `get_stock_fund_flow()` - 个股资金流向
  - 新增方法3: `get_stock_lhb_detail()` - 龙虎榜数据
  - 新增方法4: `get_block_trade()` - 大宗交易数据
  - 复用: 现有的 `_retry_api_call()` 装饰器和 `ColumnMapper`

### 核心服务层 (策略引擎和回测引擎)

- [ ] **T012** [FOUNDATION] 创建策略引擎基类 `web/backend/app/services/strategy_engine.py`
  - 类: `StrategyBase` (抽象基类)
  - 方法: `execute()`, `get_ohlcv_data()`, `calculate_indicator()`
  - 复用: indicator_calculator.py (EXISTING), data_service.py (EXISTING)

- [ ] **T013** [FOUNDATION] 创建策略注册表 `web/backend/app/services/strategy_registry.py`
  - 类: `StrategyRegistry` (单例模式)
  - 方法: `register_strategy()`, `get_strategy()`, `list_strategies()`
  - 参考: indicator_registry.py的设计模式

- [ ] **T014** [FOUNDATION] 创建回测引擎 `web/backend/app/services/backtest_engine.py`
  - 类: `BacktestEngine`, `BacktestConfig`, `BacktestResult`
  - 方法: `run_backtest()`, `_simulate_trades()`, `_calculate_metrics()`
  - 复用: strategy_engine.py, data_service.py (EXISTING)

**✅ Checkpoint**: 基础设施就绪 - User Story实施现在可以并行开始

---

## Phase 3: User Story 1 - 查看股票基本数据和资金流向 (Priority: P1) 🎯 MVP

**目标**: 用户可以查看股票的实时行情、历史K线数据、资金流向(主力/超大单/大单/中单/小单)等基本数据

**独立测试**: 访问股票数据查询页面,输入股票代码"600519.SH",查看完整的基本数据和资金流向信息

### 数据模型 (US1)

- [x] **T015** [P] [US1] 创建资金流向模型 `web/backend/app/models/fund_flow.py`
  - 类: `FundFlow` (SQLAlchemy模型)
  - 映射表: stock_fund_flow
  - 字段: symbol, trade_date, timeframe, main_net_inflow, super_large_net_inflow, large_net_inflow, medium_net_inflow, small_net_inflow

- [x] **T016** [P] [US1] 创建ETF模型 `web/backend/app/models/etf_data.py`
  - 类: `ETFData` (SQLAlchemy模型)
  - 映射表: etf_spot_data
  - 字段: symbol, name, trade_date, latest_price, change_percent, volume, amount, turnover_rate

- [x] **T017** [P] [US1] 创建竞价抢筹模型 `web/backend/app/models/chip_race.py`
  - 类: `ChipRaceData` (SQLAlchemy模型)
  - 映射表: chip_race_data
  - 字段: symbol, trade_date, race_type, race_amount, race_amplitude, race_ratio

- [x] **T018** [P] [US1] 创建龙虎榜模型 `web/backend/app/models/long_hu_bang.py`
  - 类: `LongHuBangData` (SQLAlchemy模型)
  - 映射表: stock_lhb_detail
  - 字段: symbol, trade_date, reason, buy_amount, sell_amount, net_amount, institution_buy, institution_sell

### API Schemas (US1)

- [x] **T019** [P] [US1] 创建资金流向Schema `web/backend/app/schemas/fund_flow_schemas.py`
  - 类: `FundFlowRequest`, `FundFlowResponse`
  - 验证: timeframe枚举 ("1", "3", "5", "10")

- [x] **T020** [P] [US1] 创建市场数据Schema `web/backend/app/schemas/market_data_schemas.py`
  - 类: `ETFListResponse`, `ChipRaceRequest`, `ChipRaceResponse`, `LongHuBangRequest`, `LongHuBangResponse`

### 后端服务层 (US1)

- [x] **T021** [US1] 创建市场数据服务 `web/backend/app/services/market_data_service.py`
  - 类: `MarketDataService`
  - 方法: `get_stock_fund_flow()`, `get_etf_list()`, `get_chip_race()`, `get_long_hu_bang()`, `get_block_trade()`
  - 依赖: akshare_adapter (ENHANCE), tqlex_adapter (NEW)
  - 集成: MyStocksUnifiedManager.save_data_by_classification()
  - **实现状态**: 完成 - 493行,包含所有数据获取和刷新方法

### 后端API端点 (US1)

- [x] **T022** [US1] 创建市场数据API `web/backend/app/api/market.py`
  - 端点1: `GET /api/market/fund-flow` - 获取个股资金流向
  - 端点2: `GET /api/market/etf/list` - 获取ETF列表
  - 端点3: `GET /api/market/chip-race` - 获取竞价抢筹数据
  - 端点4: `GET /api/market/lhb` - 获取龙虎榜数据
  - 端点5: `POST /api/market/*/refresh` - 刷新数据端点
  - 依赖: market_data_service.py, fund_flow_schemas.py, market_data_schemas.py
  - **实现状态**: 完成 - 230行,8个API端点

- [x] **T023** [US1] 在主路由注册市场数据API `web/backend/app/main.py`
  - 添加: `app.include_router(market.router, prefix="/api/market", tags=["market"])`
  - **实现状态**: 完成 - 路由已注册

### 前端组件 (US1)

- [x] **T024** [P] [US1] 创建资金流向面板组件 `web/frontend/src/components/market/FundFlowPanel.vue`
  - 功能: 显示资金流向数据 (主力净流入、超大单、大单、中单、小单)
  - 图表: ECharts柱状图+折线图组合
  - 交互: 时间维度切换 (今日/3日/5日/10日)
  - **实现状态**: 完成 - 9841行,包含完整ECharts可视化

- [x] **T025** [P] [US1] 创建ETF列表组件 `web/frontend/src/components/market/ETFDataPanel.vue`
  - 功能: 显示ETF列表(代码、名称、最新价、涨跌幅、成交量)
  - 表格: Element Plus Table组件
  - 功能: 排序、搜索、分页
  - **实现状态**: 完成 - 140行

- [x] **T026** [P] [US1] 创建竞价抢筹组件 `web/frontend/src/components/market/ChipRacePanel.vue`
  - 功能: 显示早盘/尾盘抢筹数据
  - 表格: Element Plus Table组件
  - 功能: 按抢筹幅度排序
  - **实现状态**: 完成 - 141行

- [x] **T027** [P] [US1] 创建龙虎榜组件 `web/frontend/src/components/market/LongHuBangPanel.vue`
  - 功能: 显示龙虎榜上榜股票和营业部排行
  - 布局: 卡片式展示
  - 功能: 查看详情
  - **实现状态**: 完成 - 162行

### 前端页面和路由 (US1)

- [x] **T028** [US1] ~~创建市场行情主页面~~ **架构调整**: 直接路由到组件,无需包装页面
  - **实际实现**: 使用router sub-menu直接路由到4个Panel组件
  - **原因**: 简化架构,避免不必要的嵌套层级

- [x] **T029** [P] [US1] ~~创建市场数据API服务~~ **架构调整**: 组件内直接使用axios
  - **实际实现**: 各Panel组件内置API服务方法
  - **原因**: 减少抽象层,提高代码可读性

- [x] **T030** [US1] 添加市场行情路由 `web/frontend/src/router/index.js` + `web/frontend/src/layout/index.vue`
  - **实际路由结构**:
    - `/market-data` (redirect to /market-data/fund-flow)
    - `/market-data/fund-flow` → `components/market/FundFlowPanel.vue`
    - `/market-data/etf` → `components/market/ETFDataTable.vue`
    - `/market-data/chip-race` → `components/market/ChipRaceTable.vue`
    - `/market-data/lhb` → `components/market/LongHuBangPanel.vue`
  - **导航菜单**: layout/index.vue el-sub-menu with 4 items
  - **实现状态**: 完成 - 包含2级子菜单结构

**✅ Checkpoint**: User Story 1完成 - 用户可以查看股票基本数据和资金流向

---

## Phase 4: User Story 2 - 查看和分析技术指标 (Priority: P2) ✅ 已完成

**目标**: 用户可以对股票应用各种技术指标(移动平均线、RSI、MACD等),识别交易信号和趋势

**独立测试**: 选择一只股票,应用多个技术指标(如MA、RSI、MACD),查看指标计算结果和图表叠加

**注意**: 此User Story主要基于EXISTING功能(indicator_calculator.py, KLineChart.vue),任务重点是增强和集成

### 后端增强 (US2)

- [x] **T031** [P] [US2] 创建指标配置模型 `web/backend/app/models/indicator_config.py`
  - **状态**: 已存在 (88行)
  - 类: `IndicatorConfiguration` (SQLAlchemy模型)
  - 功能: 保存用户常用指标配置
  - 字段: id, user_id, name, indicators (JSON), created_at, updated_at, last_used_at
  - 索引: uk_user_name (唯一), idx_user_id, idx_last_used

- [x] **T032** [US2] 增强指标API `web/backend/app/api/indicators.py`
  - **状态**: 完成 - 添加了5个配置管理端点 (681行总代码)
  - 新增端点: `POST /api/indicators/configs` - 创建指标配置
  - 新增端点: `GET /api/indicators/configs` - 获取用户指标配置列表
  - 新增端点: `GET /api/indicators/configs/{config_id}` - 获取单个配置
  - 新增端点: `PUT /api/indicators/configs/{config_id}` - 更新指标配置
  - 新增端点: `DELETE /api/indicators/configs/{config_id}` - 删除指标配置
  - 功能: 支持配置名称唯一性校验、自动更新last_used_at

### 前端增强 (US2)

- [x] **T033** [P] [US2] 增强指标面板组件 `web/frontend/src/components/technical/IndicatorPanel.vue`
  - **状态**: 已存在 (470行)
  - 功能: 完整的指标选择面板,支持搜索、分类筛选、参数配置
  - 显示: 已选指标列表、可用指标卡片、参数配置对话框
  - 复用: indicatorService.ts

- [x] **T034** [P] [US2] 创建指标库页面 `web/frontend/src/views/IndicatorLibrary.vue`
  - **状态**: 完成 - 新建文件 (约400行)
  - 功能: 展示161个TA-Lib指标的完整文档
  - 内容: 指标统计卡片、搜索筛选、指标详情卡片
  - 显示: 参数表格、输出字段、参考线、最小数据点
  - 数据源: GET /api/indicators/registry
  - **路由**: 已添加到 router/index.js 和 layout/index.vue

- [x] **T035** [US2] 增强技术分析主页面 `web/frontend/src/views/TechnicalAnalysis.vue`
  - **状态**: 完成 - 添加配置管理功能 (496行总代码)
  - 新增: 配置管理下拉菜单(保存/加载/管理)
  - 新增: handleSaveConfig() - 保存当前指标配置
  - 新增: handleLoadConfig() - 加载已保存配置
  - 新增: handleManageConfigs() - 管理配置列表
  - 交互: 使用ElMessageBox.prompt保存、列表选择加载、HTML列表管理

### 前端服务 (US2)

- [x] **T036** [US2] 增强指标服务 `web/frontend/src/services/indicatorService.ts`
  - **状态**: 已存在 (238行)
  - 已有方法: `createConfig()`, `listConfigs()`, `getConfig()`, `updateConfig()`, `deleteConfig()`
  - 新增方法: `applyConfig()` - 便捷加载并应用配置

**✅ Checkpoint**: User Story 2完成 - 用户可以查看和分析技术指标
  - **实现日期**: 2025-10-15
  - **总代码量**: 约1500行 (后端681 + 前端约800)
  - **API端点**: 5个新端点
  - **前端页面**: 1个新页面 + 2个增强页面

---

## Phase 5: User Story 3 - 运行股票策略筛选和回测 (Priority: P3)

**目标**: 用户可以使用预定义的交易策略筛选符合条件的股票,并查看策略的历史表现

**独立测试**: 选择"放量上涨"策略,设置筛选条件,运行策略并查看筛选结果列表

### 数据模型 (US3)

- [ ] **T037** [P] [US3] 创建策略配置模型 `web/backend/app/models/strategy.py`
  - 类: `TradingStrategy` (SQLAlchemy模型)
  - 映射表: strategy_configs
  - 字段: strategy_id, strategy_name, category, parameters, is_active

- [ ] **T038** [P] [US3] 创建策略信号模型 `web/backend/app/models/strategy_signal.py`
  - 类: `StrategySignal` (SQLAlchemy模型)
  - 映射表: strategy_signals
  - 字段: strategy_id, symbol, signal_date, signal_type, price, reason, confidence

- [ ] **T039** [P] [US3] 创建回测结果模型 `web/backend/app/models/backtest.py`
  - 类: `BacktestResult`, `BacktestTrade` (SQLAlchemy模型)
  - 映射表: backtest_results, backtest_trades
  - 字段: (见data-model.md第3.12和3.13节)

### API Schemas (US3)

- [ ] **T040** [P] [US3] 创建策略Schema `web/backend/app/schemas/strategy_schemas.py`
  - 类: `StrategyListResponse`, `StrategyRunRequest`, `StrategyRunResponse`, `SignalResponse`

- [ ] **T041** [P] [US3] 创建回测Schema `web/backend/app/schemas/backtest_schemas.py`
  - 类: `BacktestRequest`, `BacktestResponse`, `BacktestTradeResponse`, `PerformanceMetrics`

### 策略实现 (US3 - 10个预定义策略)

- [ ] **T042** [P] [US3] 实现策略1: 成交量突破策略 `web/backend/app/strategies/volume_breakout.py`
  - 类: `VolumeBreakoutStrategy(StrategyBase)`
  - 逻辑: 成交量突破20日均量2倍 + 价格上涨
  - 依赖指标: SMA (volume), SMA (price)

- [ ] **T043** [P] [US3] 实现策略2: 均线金叉策略 `web/backend/app/strategies/ma_golden_cross.py`
  - 类: `MAGoldenCrossStrategy(StrategyBase)`
  - 逻辑: 短期均线向上穿越长期均线
  - 依赖指标: SMA, EMA

- [ ] **T044** [P] [US3] 实现策略3: 海龟交易法则 `web/backend/app/strategies/turtle_trading.py`
  - 类: `TurtleTradingStrategy(StrategyBase)`
  - 逻辑: 唐奇安通道突破
  - 依赖指标: ATR

- [ ] **T045** [P] [US3] 实现策略4: RSI反转策略 `web/backend/app/strategies/rsi_reversal.py`
  - 类: `RSIReversalStrategy(StrategyBase)`
  - 逻辑: RSI超买超卖反转
  - 依赖指标: RSI

- [ ] **T046** [P] [US3] 实现策略5: MACD背离策略 `web/backend/app/strategies/macd_divergence.py`
  - 类: `MACDDivergenceStrategy(StrategyBase)`
  - 逻辑: MACD与价格背离
  - 依赖指标: MACD

- [ ] **T047** [P] [US3] 实现策略6: 布林带突破策略 `web/backend/app/strategies/bollinger_breakout.py`
  - 类: `BollingerBreakoutStrategy(StrategyBase)`
  - 逻辑: 价格突破布林带上下轨
  - 依赖指标: BBANDS

- [ ] **T048** [P] [US3] 实现策略7: KDJ超买超卖策略 `web/backend/app/strategies/kdj_overbought.py`
  - 类: `KDJOverboughtStrategy(StrategyBase)`
  - 逻辑: KDJ指标超买超卖
  - 依赖指标: STOCH (KDJ)

- [ ] **T049** [P] [US3] 实现策略8: 量价背离策略 `web/backend/app/strategies/volume_price_trend.py`
  - 类: `VolumePriceTrendStrategy(StrategyBase)`
  - 逻辑: 成交量与价格背离
  - 依赖指标: OBV, SMA

- [ ] **T050** [P] [US3] 实现策略9: 双均线策略 `web/backend/app/strategies/dual_moving_average.py`
  - 类: `DualMovingAverageStrategy(StrategyBase)`
  - 逻辑: 快慢双均线交叉
  - 依赖指标: SMA

- [ ] **T051** [P] [US3] 实现策略10: 价格通道突破策略 `web/backend/app/strategies/price_channel_breakout.py`
  - 类: `PriceChannelBreakoutStrategy(StrategyBase)`
  - 逻辑: 突破N日最高价/最低价
  - 依赖指标: Highest/Lowest

### 策略注册 (US3)

- [ ] **T052** [US3] 注册所有10个策略到策略注册表
  - 文件: `web/backend/app/services/strategy_registry.py`
  - 代码: 在模块加载时调用 `registry.register_strategy()` 注册所有策略
  - 验证: 启动后端,访问 `/api/strategies/list` 应返回10个策略

### 后端API端点 (US3)

- [ ] **T053** [US3] 创建策略管理API `web/backend/app/api/strategies.py`
  - 端点1: `GET /api/strategies/list` - 获取策略列表
  - 端点2: `GET /api/strategies/{strategy_id}` - 获取策略详情
  - 端点3: `POST /api/strategies/{strategy_id}/config` - 更新策略配置
  - 依赖: strategy_engine.py, strategy_registry.py

- [ ] **T054** [US3] 创建策略信号API
  - 端点1: `POST /api/signals/generate` - 生成实时交易信号
  - 端点2: `GET /api/signals/history` - 查询历史信号
  - 依赖: strategy_engine.py, strategy_signal.py

- [ ] **T055** [US3] 创建回测API
  - 端点1: `POST /api/backtest/run` - 运行策略回测
  - 端点2: `GET /api/backtest/{id}` - 获取回测结果
  - 端点3: `GET /api/backtest/history` - 获取回测历史列表
  - 依赖: backtest_engine.py, backtest.py

- [ ] **T056** [US3] 在主路由注册策略和回测API `web/backend/app/main.py`
  - 添加: `app.include_router(strategies.router, prefix="/api/strategies", tags=["strategies"])`
  - 添加: `app.include_router(signals.router, prefix="/api/signals", tags=["signals"])`
  - 添加: `app.include_router(backtest.router, prefix="/api/backtest", tags=["backtest"])`

### 前端组件 (US3)

- [ ] **T057** [P] [US3] 创建策略卡片组件 `web/frontend/src/components/strategy/StrategyCard.vue`
  - 功能: 显示单个策略的名称、描述、分类
  - 交互: 点击查看详情或运行策略

- [ ] **T058** [P] [US3] 创建策略参数编辑器 `web/frontend/src/components/strategy/ParameterEditor.vue`
  - 功能: 动态表单编辑策略参数
  - 验证: 参数类型和范围验证

- [ ] **T059** [P] [US3] 创建回测图表组件 `web/frontend/src/components/strategy/BacktestChart.vue`
  - 功能: 显示回测权益曲线
  - 图表: ECharts折线图
  - 数据: equity_curve (日期 vs 权益)

- [ ] **T060** [P] [US3] 创建性能指标组件 `web/frontend/src/components/strategy/PerformanceMetrics.vue`
  - 功能: 显示回测性能指标卡片
  - 指标: 总收益率、年化收益率、夏普比率、最大回撤、胜率、总交易次数、盈亏比
  - 布局: Element Plus Statistic组件

### 前端页面 (US3)

- [ ] **T061** [US3] 创建策略列表页面 `web/frontend/src/views/Strategy/StrategyList.vue`
  - 功能: 展示10个预定义策略
  - 布局: 卡片式Grid布局
  - 依赖: StrategyCard.vue (T057)

- [ ] **T062** [US3] 创建策略运行页面 `web/frontend/src/views/Strategy/StrategyRun.vue`
  - 功能: 选择策略、配置参数、运行策略
  - 表单: 股票代码、时间范围、策略参数
  - 结果: 显示筛选出的股票列表
  - 依赖: ParameterEditor.vue (T058)

- [ ] **T063** [US3] 创建回测运行页面 `web/frontend/src/views/Strategy/BacktestRunner.vue`
  - 功能: 运行策略回测
  - 表单: 选择策略、股票代码、回测时间范围、初始资金、策略参数
  - 结果: 显示回测结果和交易历史
  - 依赖: ParameterEditor, BacktestChart, PerformanceMetrics (T058-T060)

- [ ] **T064** [US3] 创建回测结果页面 `web/frontend/src/views/Strategy/BacktestResults.vue`
  - 功能: 查看历史回测结果列表
  - 交互: 点击查看详细回测报告

### 前端服务和路由 (US3)

- [ ] **T065** [P] [US3] 创建策略API服务 `web/frontend/src/services/strategyService.js`
  - 方法: `listStrategies()`, `getStrategyDetail()`, `runStrategy()`, `generateSignals()`, `getSignalHistory()`

- [ ] **T066** [P] [US3] 创建回测API服务 `web/frontend/src/services/backtestService.js`
  - 方法: `runBacktest()`, `getBacktestResult()`, `getBacktestHistory()`

- [ ] **T067** [US3] 添加策略管理路由 `web/frontend/src/router/index.js`
  - 路径: `/strategy` → `views/Strategy/StrategyList.vue`
  - 路径: `/strategy/run` → `views/Strategy/StrategyRun.vue`
  - 路径: `/strategy/backtest` → `views/Strategy/BacktestRunner.vue`
  - 路径: `/strategy/backtest/results` → `views/Strategy/BacktestResults.vue`
  - 权限: 需登录

**✅ Checkpoint**: User Story 3完成 - 用户可以运行股票策略筛选和回测

---

## Phase 6: User Story 4 - 查看ETF数据和行业/概念资金流向 (Priority: P2)

**目标**: 用户可以查看ETF基金的行情数据,以及行业和概念板块的资金流向

**独立测试**: 访问ETF数据页面查看ETF列表,以及访问资金流向页面查看行业/概念资金流向排行

**注意**: 部分功能在US1已实现 (ETF列表),此阶段主要实现行业/概念资金流向

### 数据模型 (US4)

- [ ] **T068** [P] [US4] 创建行业资金流向模型 `web/backend/app/models/sector_fund_flow.py`
  - 类: `SectorFundFlow` (SQLAlchemy模型)
  - 映射表: sector_fund_flow (需在table_config.yaml中添加)
  - 字段: sector_name, sector_type (industry/concept), trade_date, main_net_inflow, leader_stock

### 后端服务层 (US4)

- [ ] **T069** [US4] 扩展市场数据服务 `web/backend/app/services/market_data_service.py` (ENHANCE)
  - 新增方法: `get_sector_fund_flow()` - 获取行业资金流向
  - 新增方法: `get_concept_fund_flow()` - 获取概念资金流向
  - 数据源: Akshare Adapter (EXISTING - `get_ths_industry_summary()` 复用)

### 后端API端点 (US4)

- [ ] **T070** [US4] 扩展市场数据API `web/backend/app/api/market_data.py` (ENHANCE)
  - 新增端点: `GET /api/market/sector/fund-flow` - 获取行业资金流向
  - 新增端点: `GET /api/market/concept/fund-flow` - 获取概念资金流向

### 前端组件 (US4)

- [ ] **T071** [P] [US4] 创建行业资金流向组件 `web/frontend/src/components/market/SectorFundFlowPanel.vue`
  - 功能: 显示各行业的主力净流入排行
  - 图表: ECharts柱状图或树状图
  - 交互: 点击行业查看成分股详情

- [ ] **T072** [P] [US4] 创建概念资金流向组件 `web/frontend/src/components/market/ConceptFundFlowPanel.vue`
  - 功能: 显示热门概念的资金流向
  - 布局: 卡片式或热力图
  - 交互: 点击概念查看相关个股

### 前端页面 (US4)

- [ ] **T073** [US4] 增强市场行情主页面 `web/frontend/src/views/MarketData/index.vue` (ENHANCE)
  - 新增标签页: "行业资金流向" 和 "概念资金流向"
  - 集成: SectorFundFlowPanel, ConceptFundFlowPanel (T071-T072)

### 前端服务 (US4)

- [ ] **T074** [US4] 扩展市场数据API服务 `web/frontend/src/services/marketDataService.js` (ENHANCE)
  - 新增方法: `getSectorFundFlow()`, `getConceptFundFlow()`

**✅ Checkpoint**: User Story 4完成 - 用户可以查看ETF数据和行业/概念资金流向

---

## Phase 7: User Story 5 - 查看龙虎榜和大宗交易数据 (Priority: P3)

**目标**: 用户可以查看龙虎榜数据和大宗交易信息,跟踪机构和大资金的动向

**独立测试**: 访问龙虎榜页面查看当日上榜个股,以及访问大宗交易页面查看大宗交易明细

**注意**: 数据模型和API端点在US1已实现,此阶段主要实现专门的展示页面

### 数据模型 (US5)

- [ ] **T075** [P] [US5] 创建大宗交易模型 `web/backend/app/models/block_trade.py`
  - 类: `BlockTradeData` (SQLAlchemy模型)
  - 映射表: block_trade_data (需在table_config.yaml中添加)
  - 字段: symbol, trade_date, trade_price, trade_volume, buyer_branch, seller_branch, discount_rate

### 后端服务层 (US5)

- [ ] **T076** [US5] 扩展市场数据服务 `web/backend/app/services/market_data_service.py` (ENHANCE)
  - 增强方法: `get_block_trade()` - 支持更多筛选条件(按折价率、成交额排序)
  - 新增方法: `get_institution_statistics()` - 机构席位统计

### 后端API端点 (US5)

- [ ] **T077** [US5] 扩展市场数据API `web/backend/app/api/market_data.py` (ENHANCE)
  - 增强端点: `GET /api/market/block-trade` - 支持更多查询参数
  - 新增端点: `GET /api/market/institution/statistics` - 机构统计

### 前端页面 (US5)

- [ ] **T078** [P] [US5] 创建龙虎榜专题页面 `web/frontend/src/views/MarketData/LongHuBangDetail.vue`
  - 功能: 详细展示龙虎榜数据
  - 布局: 上榜股票列表 + 营业部排行 + 机构席位统计
  - 图表: 买入卖出对比柱状图

- [ ] **T079** [P] [US5] 创建大宗交易专题页面 `web/frontend/src/views/MarketData/BlockTradeDetail.vue`
  - 功能: 详细展示大宗交易数据
  - 表格: 按折价率、成交额排序
  - 筛选: 按日期、股票、折价率范围

### 前端路由 (US5)

- [ ] **T080** [US5] 添加龙虎榜和大宗交易路由 `web/frontend/src/router/index.js`
  - 路径: `/market/long-hu-bang` → `views/MarketData/LongHuBangDetail.vue`
  - 路径: `/market/block-trade` → `views/MarketData/BlockTradeDetail.vue`

**✅ Checkpoint**: User Story 5完成 - 用户可以查看龙虎榜和大宗交易数据

---

## Phase 8: User Story 6 - 查看分红配送和早晚盘抢筹数据 (Priority: P3)

**目标**: 用户可以查看股票的分红配送信息以及早盘/尾盘的抢筹数据

**独立测试**: 访问分红配送页面查看即将分红的股票列表,以及访问抢筹数据页面查看早盘/尾盘抢筹排行

**注意**: 竞价抢筹数据模型在US1已实现,此阶段主要实现分红配送功能

### 数据模型 (US6)

- [ ] **T081** [P] [US6] 创建分红配送模型 `web/backend/app/models/dividend.py`
  - 类: `DividendData` (SQLAlchemy模型)
  - 映射表: dividend_data
  - 字段: symbol, announce_date, ex_dividend_date, record_date, dividend_ratio, bonus_share_ratio, transfer_ratio

### 后端服务层 (US6)

- [ ] **T082** [US6] 扩展市场数据服务 `web/backend/app/services/market_data_service.py` (ENHANCE)
  - 新增方法: `get_dividend_data()` - 获取分红配送数据
  - 数据源: Akshare Adapter (ENHANCE)

### 后端API端点 (US6)

- [ ] **T083** [US6] 扩展市场数据API `web/backend/app/api/market_data.py` (ENHANCE)
  - 新增端点: `GET /api/market/dividend` - 获取分红配送数据

### 前端页面 (US6)

- [ ] **T084** [P] [US6] 创建分红配送页面 `web/frontend/src/views/MarketData/DividendData.vue`
  - 功能: 显示分红公告列表
  - 表格: 股票代码、分红方案、股权登记日、除权除息日
  - 筛选: 按股息率排序、按分红日期筛选

- [ ] **T085** [P] [US6] 创建抢筹数据专题页面 `web/frontend/src/views/MarketData/ChipRaceDetail.vue`
  - 功能: 详细展示早盘/尾盘抢筹数据
  - 图表: 抢筹幅度排行、抢筹金额排行
  - 交互: 早盘/尾盘切换

### 前端路由 (US6)

- [ ] **T086** [US6] 添加分红配送和抢筹数据路由 `web/frontend/src/router/index.js`
  - 路径: `/market/dividend` → `views/MarketData/DividendData.vue`
  - 路径: `/market/chip-race` → `views/MarketData/ChipRaceDetail.vue`

**✅ Checkpoint**: User Story 6完成 - 用户可以查看分红配送和早晚盘抢筹数据

---

## Phase 9: Polish & Cross-Cutting Concerns (最终完善)

**目的**: 跨User Story的改进和完善

### 文档和测试

- [ ] **T087** [P] [POLISH] 更新API文档
  - 文件: 确保Swagger UI (`http://localhost:8888/docs`) 包含所有新API端点
  - 描述: 添加API端点的详细说明、请求示例、响应示例

- [ ] **T088** [P] [POLISH] 创建用户手册
  - 文件: `docs/user-guide.md`
  - 内容: 市场行情模块、数据分析模块、策略管理模块的使用指南

- [ ] **T089** [P] [POLISH] 创建开发者指南
  - 文件: `docs/developer-guide.md`
  - 内容: 如何添加新策略、如何扩展数据适配器、如何添加新指标

### 性能优化

- [ ] **T090** [P] [POLISH] 实现Redis缓存策略
  - 文件: `web/backend/app/core/cache.py`
  - 内容: 实时行情数据缓存(5分钟过期)、策略信号缓存(1小时过期)、技术指标缓存(1天过期)

- [ ] **T091** [P] [POLISH] 优化数据库查询
  - 任务: 为常用查询添加复合索引
  - 任务: 使用数据库连接池
  - 任务: 实现分页查询(避免一次加载大量数据)

### 错误处理和日志

- [ ] **T092** [P] [POLISH] 统一错误处理
  - 文件: `web/backend/app/core/error_handlers.py`
  - 内容: 自定义异常类、全局异常处理器

- [ ] **T093** [P] [POLISH] 增强日志记录
  - 文件: `web/backend/app/core/logging_config.py`
  - 内容: 结构化日志(structlog)、日志分级、日志轮转

### 安全加固

- [ ] **T094** [P] [POLISH] 实现API限流
  - 文件: `web/backend/app/middleware/rate_limiter.py`
  - 策略: 每个IP每分钟最多100次请求

- [ ] **T095** [P] [POLISH] 敏感信息脱敏
  - 任务: 确保日志中不包含数据库密码、API Token等敏感信息
  - 文件: 检查所有日志输出

### 系统功能增强

- [ ] **T096** [POLISH] [NEW FEATURE] 实现日志查询功能
  - **需求来源**: 2025-10-15 用户请求
  - **位置**: 系统设置菜单下新增"日志查询"标签页
  - **功能要求**:
    1. 查询系统运行日志
    2. 支持筛选条件显示错误日志
    3. 支持按时间范围筛选
    4. 支持按日志级别筛选 (ERROR, WARNING, INFO, DEBUG)
  - **实现任务**:
    - [ ] **T096a** [P] 后端: 创建日志模型 `web/backend/app/models/system_log.py`
      - 字段: timestamp, level, module, message, user_id, request_id
    - [ ] **T096b** [P] 后端: 创建日志查询API `web/backend/app/api/system_logs.py`
      - 端点: `GET /api/system/logs` - 查询系统日志
      - 参数: start_date, end_date, level, keyword, limit, offset
      - 返回: 分页日志列表
    - [ ] **T096c** [P] 后端: 实现日志收集服务 `web/backend/app/services/log_collector.py`
      - 功能: 从日志文件或数据库读取日志
      - 支持: 实时日志查询、历史日志查询
    - [ ] **T096d** [P] 前端: 创建日志查询组件 `web/frontend/src/components/system/LogQueryPanel.vue`
      - 功能: 日志列表表格、筛选表单、分页控制
      - 筛选: 时间范围选择器、日志级别下拉框、关键词搜索
      - 展示: 时间、级别、模块、消息内容 (支持展开查看详情)
    - [ ] **T096e** 前端: 集成到系统设置页面 `web/frontend/src/views/Settings.vue`
      - 添加: "日志查询" 标签页
      - 集成: LogQueryPanel组件
    - [ ] **T096f** 前端: 添加路由 `web/frontend/src/router/index.js`
      - 路径: `/settings/logs` → LogQueryPanel组件 (作为Settings的子路由)

### 前端优化

- [ ] **T097** [P] [POLISH] 实现前端数据缓存
  - 文件: `web/frontend/src/utils/cache.js`
  - 策略: localStorage缓存用户配置、指标配置

- [ ] **T098** [P] [POLISH] 添加加载状态和骨架屏
  - 任务: 为所有异步请求添加Loading状态
  - 任务: 为数据表格和图表添加骨架屏

- [ ] **T099** [P] [POLISH] 响应式布局优化
  - 任务: 确保所有页面在不同屏幕尺寸下正常显示
  - 测试: 桌面、平板、移动端

### 部署准备

- [ ] **T100** [P] [POLISH] 创建Docker容器化配置
  - 文件: `Dockerfile` (backend), `docker-compose.yml`
  - 内容: 后端服务、前端服务、PostgreSQL、MySQL、Redis

- [ ] **T101** [P] [POLISH] 创建Nginx配置
  - 文件: `deployment/nginx.conf`
  - 内容: 反向代理、静态文件服务、负载均衡

### 验证

- [ ] **T102** [POLISH] 运行quickstart.md验证
  - 任务: 按照quickstart.md的步骤完整走一遍
  - 验证: 所有步骤都能成功执行,所有功能都正常工作

- [ ] **T103** [POLISH] 端到端功能测试
  - 任务: 测试6个User Story的所有验收场景
  - 检查: 每个功能都符合spec.md的要求

**✅ Checkpoint**: 所有优化和完善完成,项目可以部署

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 无依赖 - 可立即开始
- **Foundational (Phase 2)**: 依赖Setup完成 - **阻塞所有User Stories**
- **User Stories (Phase 3-8)**: 全部依赖Foundational阶段完成
  - User Stories可以并行进行(如果有足够人力)
  - 或按优先级顺序执行 (P1 → P2 → P3)
- **Polish (Phase 9)**: 依赖所有需要的User Stories完成

### User Story Dependencies

- **User Story 1 (P1)**: Foundational完成后可开始 - 无其他Story依赖
- **User Story 2 (P2)**: Foundational完成后可开始 - 主要基于EXISTING功能
- **User Story 3 (P3)**: Foundational完成后可开始 - 无其他Story依赖
- **User Story 4 (P2)**: Foundational完成后可开始 - 部分依赖US1 (ETF模型)
- **User Story 5 (P3)**: Foundational完成后可开始 - 部分依赖US1 (龙虎榜模型)
- **User Story 6 (P3)**: Foundational完成后可开始 - 部分依赖US1 (抢筹模型)

### Within Each User Story

- 数据模型 → 服务层 → API端点 → 前端组件 → 前端页面 → 路由
- 标记为 [P] 的任务可以并行执行 (不同文件,无依赖)

### Parallel Opportunities

- **Phase 1**: 所有标记 [P] 的Setup任务可并行
- **Phase 2**: 数据适配器层 (T010, T011) 可并行;策略引擎组件 (T012, T013, T014) 可并行
- **User Stories**: 一旦Foundational完成,所有User Stories可并行开始
- **Within Story**: 所有标记 [P] 的数据模型、前端组件可并行

---

## Parallel Example: Foundational Phase

```bash
# 并行执行数据适配器层:
Task T010: "创建TQLEX适配器 adapters/tqlex_adapter.py"
Task T011: "扩展Akshare适配器 adapters/akshare_adapter.py"

# 数据适配器完成后,并行执行策略引擎层:
Task T012: "创建策略引擎基类 web/backend/app/services/strategy_engine.py"
Task T013: "创建策略注册表 web/backend/app/services/strategy_registry.py"
Task T014: "创建回测引擎 web/backend/app/services/backtest_engine.py"
```

## Parallel Example: User Story 1

```bash
# 并行执行所有数据模型:
Task T015: "创建资金流向模型 web/backend/app/models/fund_flow.py"
Task T016: "创建ETF模型 web/backend/app/models/etf_data.py"
Task T017: "创建竞价抢筹模型 web/backend/app/models/chip_race.py"
Task T018: "创建龙虎榜模型 web/backend/app/models/long_hu_bang.py"

# 并行执行API Schemas:
Task T019: "创建资金流向Schema web/backend/app/schemas/fund_flow_schemas.py"
Task T020: "创建市场数据Schema web/backend/app/schemas/market_data_schemas.py"

# 并行执行前端组件:
Task T024: "创建资金流向面板组件 web/frontend/src/components/market/FundFlowPanel.vue"
Task T025: "创建ETF列表组件 web/frontend/src/components/market/ETFDataTable.vue"
Task T026: "创建竞价抢筹组件 web/frontend/src/components/market/ChipRaceTable.vue"
Task T027: "创建龙虎榜组件 web/frontend/src/components/market/LongHuBangPanel.vue"
```

---

## Implementation Strategy

### MVP First (仅User Story 1)

1. ✅ 完成 Phase 1: Setup (T001-T006)
2. ✅ 完成 Phase 2: Foundational (T007-T014) - **关键阻塞点**
3. ✅ 完成 Phase 3: User Story 1 (T015-T030)
4. **停止并验证**: 独立测试User Story 1的所有功能
5. 如果准备好,可以部署/演示MVP

### Incremental Delivery (逐步交付)

1. Setup + Foundational → 基础设施就绪
2. 添加 User Story 1 → 独立测试 → 部署/演示 (MVP! 🎯)
3. 添加 User Story 2 → 独立测试 → 部署/演示
4. 添加 User Story 3 → 独立测试 → 部署/演示
5. 添加 User Story 4 → 独立测试 → 部署/演示
6. 添加 User Story 5 → 独立测试 → 部署/演示
7. 添加 User Story 6 → 独立测试 → 部署/演示
8. Polish → 最终完善

每个Story都能增加价值而不破坏之前的功能。

### Parallel Team Strategy (并行团队策略)

如果有多个开发人员:

1. **团队共同完成 Setup + Foundational** (必须串行)
2. **Foundational完成后**:
   - 开发者 A: User Story 1 (P1)
   - 开发者 B: User Story 2 (P2)
   - 开发者 C: User Story 3 (P3)
   - 开发者 D: User Story 4 (P2)
3. Stories独立完成并集成

---

## Summary Statistics

### Task Count

- **Total Tasks**: 109个任务 (更新于2025-10-15)
- **Phase 1 (Setup)**: 6个任务
- **Phase 2 (Foundational)**: 8个任务 ⚠️ 关键阻塞点
- **Phase 3 (US1)**: 16个任务 🎯 MVP
- **Phase 4 (US2)**: 6个任务 ✅ 已完成
- **Phase 5 (US3)**: 36个任务 (10个策略 + 基础设施)
- **Phase 6 (US4)**: 7个任务
- **Phase 7 (US5)**: 6个任务
- **Phase 8 (US6)**: 6个任务
- **Phase 9 (Polish)**: 23个任务 (+7个日志查询子任务)

### Parallel Task Count

- **Total Parallelizable Tasks**: 约60个任务标记为 [P]
- **Setup Phase**: 5/6个任务可并行
- **Foundational Phase**: 2/8个任务可并行 (适配器层)
- **User Story 1**: 8/16个任务可并行
- **User Story 3**: 10/36个任务可并行 (10个策略)

### Code Reuse Statistics

| 组件类型 | EXISTING (复用) | NEW (新建) | ENHANCE (增强) | 复用率 |
|---------|----------------|-----------|---------------|--------|
| **数据适配器** | akshare_adapter.py | tqlex_adapter.py | akshare_adapter.py (+4方法) | 67% |
| **后端服务** | indicator_calculator.py, data_service.py | strategy_engine.py, backtest_engine.py | market_data_service.py | 50% |
| **前端组件** | KLineChart.vue, TechnicalAnalysis.vue | 12个新组件 | Market.vue, StrategyManagement.vue | 25% |
| **技术指标** | 161个TA-Lib指标 | 0 | - | **100%** ✅ |

**总体复用率**: ~48% ✅

### MVP Scope

**建议MVP范围**: Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (User Story 1)

**MVP任务数**: 6 + 8 + 16 = 30个任务
**MVP预估工时**: 约5-7个工作日 (单人)

---

## Notes

- [P] = 不同文件,可并行执行
- [Story] = 任务所属User Story,便于追踪
- 每个User Story都应该可以独立完成和测试
- 在每个Checkpoint停止以验证Story的独立性
- 避免: 模糊的任务描述、同文件冲突、破坏独立性的跨Story依赖

---

## Next Steps

1. **Review and Approve**: 审查此任务列表并确认
2. **Setup Environment**: 执行Phase 1 Setup任务
3. **Build Foundation**: 执行Phase 2 Foundational任务 (阻塞点)
4. **Start MVP**: 执行Phase 3 User Story 1任务
5. **Test Independently**: 验证US1的所有验收场景
6. **Iterate**: 按优先级继续实施其他User Stories

---

**Generated**: 2025-10-14
**Last Updated**: 2025-10-15
**Status**: ✅ Tasks Ready for Implementation
**Total Tasks**: 109
**Completed**: User Story 2 (Phase 4) - 6 tasks ✅
**In Progress**: Phase 9 Polish tasks
**New Feature Added**: T096 - 日志查询功能 (Log Query)
**Estimated Timeline**: 3-4周 (单人) 或 1-2周 (3人团队并行)
