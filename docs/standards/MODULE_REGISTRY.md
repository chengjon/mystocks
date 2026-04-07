# MyStocks 项目模块清单

> **补充规范说明**:
> 本文件是项目补充标准、执行细则或专题规范，不是仓库共享规则的唯一事实来源。
> 仓库级共享规则总入口仍以 `architecture/STANDARDS.md` 为准；执行流程、命令与协作约束再参考根目录 `AGENTS.md`。本文件用于补充某一专题的执行细则、约束或参考模板。
>
> 若本文件与 `architecture/STANDARDS.md`、根目录 `AGENTS.md` 或当前已批准执行口径不一致，应优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md` 与当前实现；若无冲突，则按本文件的专题范围执行。


**创建日期**: 2025-10-24
**维护人**: JohnC & Claude
**版本**: 3.0.0
**用途**: 记录项目所有业务模块/功能及其来源，便于后续维护和扩展

---

## 📋 文档说明

本文档记录MyStocks项目的所有模块、功能及其来源，分为以下类别：
- **原生模块**: JohnC或Claude从零开发的模块
- **引入模块**: 从其他开源项目迁移或参考的模块
- **扩展模块**: 基于第三方库扩展开发的模块

---

## 🏗️ 一、核心架构层

### 1.1 数据分类与路由系统 ⭐ **原生**

| 模块 | 文件路径 | 功能 | 作者 | 代码行数 |
|------|---------|------|------|---------|
| 数据分类体系 | `core.py` | 5大数据分类枚举、存储策略映射 | JohnC & Claude | ~500行 |
| 统一管理器 | `unified_manager.py` | 统一数据访问、自动路由、系统初始化 | JohnC & Claude | ~800行 |
| 数据访问层 | `data_access.py` | 多数据库访问器、统一数据接口 | JohnC & Claude | ~600行 |

**设计理念**:
- 配置驱动：YAML配置管理所有表结构
- 自动路由：根据数据分类自动选择存储引擎
- 统一接口：一套API访问所有数据库

**Week 3简化**:
- 从4数据库架构简化为PostgreSQL单库
- 保留Redis用于实时缓存（待激活）

---

### 1.2 监控与告警系统 ⭐ **原生**

| 模块 | 文件路径 | 功能 | 作者 | 代码行数 |
|------|---------|------|------|---------|
| 监控数据库 | `monitoring.py` | 操作日志、性能监控、数据质量检查 | JohnC & Claude | ~1200行 |
| 告警管理器 | `monitoring.py` | 多渠道告警、阈值监控 | JohnC & Claude | 包含在上 |
| 性能监控 | `monitoring/performance_monitor.py` | 慢查询检测、响应时间统计 | JohnC & Claude | ~300行 |
| 数据质量监控 | `monitoring/data_quality_monitor.py` | 完整性、准确性、新鲜度检查 | JohnC & Claude | ~400行 |

**特性**:
- 独立监控数据库（PostgreSQL独立schema）
- 自动记录所有数据库操作
- 多维度数据质量评分

---

### 1.3 数据库管理层 ⭐ **原生**

| 模块 | 文件路径 | 功能 | 作者 | 代码行数 |
|------|---------|------|------|---------|
| 数据库管理器 | `db_manager/database_manager.py` | 多数据库连接、表管理 | JohnC & Claude | ~800行 |
| 配置驱动表管理 | `core.py` | YAML驱动的表结构自动创建 | JohnC & Claude | 包含在core |
| 表配置文件 | `table_config.yaml` | 完整表结构定义（YAML） | JohnC & Claude | ~2000行 |

**Week 3更新**:
- 移除TDengine、MySQL连接管理
- 简化为PostgreSQL单库管理
- 保留Redis连接池（待激活）

---

## 🔌 二、数据源适配器层

### 2.1 核心生产适配器 ⭐ **原生**（7个）

#### A. v2.1核心推荐适配器

| 适配器 | 文件路径 | 数据源 | 功能 | 作者 | 代码行数 | 状态 |
|--------|---------|--------|------|------|---------|------|
| TDX适配器 | `adapters/tdx_adapter.py` | pytdx | 通达信直连、多周期K线、无限流 | JohnC & Claude | 1058行 | ⭐生产 |
| Byapi适配器 | `adapters/byapi_adapter.py` | biyingapi.com | REST API、涨跌停股池、技术指标 | JohnC & Claude | 625行 | ⭐生产 |

**特点**:
- TDX: 本地pytdx库（temp/pytdx/），可二次开发，智能服务器切换
- Byapi: 内置频率控制（300次/分钟），完整API文档

#### B. 稳定生产适配器

| 适配器 | 文件路径 | 数据源 | 功能 | 作者 | 代码行数 | 推荐度 |
|--------|---------|--------|------|------|---------|--------|
| 财务适配器 | `adapters/financial_adapter.py` | efinance+easyquotation | 双数据源自动切换、财务数据全能 | JohnC & Claude | 1078行 | ⭐⭐⭐⭐ |
| AkShare适配器 | `adapters/akshare_adapter.py` | akshare | 免费全面、历史数据研究 | JohnC & Claude | 510行 | ⭐⭐⭐⭐ |
| BaoStock适配器 | `adapters/baostock_adapter.py` | baostock | 高质量历史数据、复权数据 | JohnC & Claude | 257行 | ⭐⭐⭐ |
| Customer适配器 | `adapters/customer_adapter.py` | efinance+easyquotation | 实时行情专用 | JohnC & Claude | 378行 | ⭐⭐⭐ |
| Tushare适配器 | `adapters/tushare_adapter.py` | tushare | 专业级数据（需token） | JohnC & Claude | 199行 | ⭐⭐⭐ |

**设计模式**:
- 统一接口（IDataSource）
- 工厂模式创建
- 自动重试和降级

### 2.2 辅助适配器工具

| 模块 | 文件路径 | 功能 | 作者 |
|------|---------|------|------|
| AkShare代理 | `adapters/akshare_proxy_adapter.py` | AkShare代理封装、额外错误处理 | JohnC & Claude |
| 数据源管理器 | `adapters/data_source_manager.py` | 统一管理和调度多个数据源 | JohnC & Claude |

---

## 🌐 三、Web管理平台

### 3.1 后端API系统 ⭐ **原生 + 迁移**

#### A. 核心业务API（原生）

| API模块 | 文件路径 | 功能 | 端点数量 | 作者 |
|---------|---------|------|---------|------|
| 认证授权 | `web/backend/app/api/auth.py` | JWT认证、用户管理 | 5个 | JohnC & Claude |
| 数据管理 | `web/backend/app/api/data.py` | 数据导入导出、查询 | 8个 | JohnC & Claude |
| 市场数据 | `web/backend/app/api/market.py` | 行情数据、K线数据 | 12个 | JohnC & Claude |
| 市场数据v2 | `web/backend/app/api/market_v2.py` | 增强版市场数据API | 10个 | JohnC & Claude |
| 通达信API | `web/backend/app/api/tdx.py` | 通达信数据接口 | 6个 | JohnC & Claude |
| 问财API | `web/backend/app/api/wencai.py` | 同花顺问财查询 | 8个 | JohnC & Claude |
| 自选股管理 | `web/backend/app/api/watchlist.py` | 自选股分组管理 | 12个 | JohnC & Claude |
| 股票搜索 | `web/backend/app/api/stock_search.py` | 智能股票搜索 | 4个 | JohnC & Claude |
| 任务管理 | `web/backend/app/api/tasks.py` | 后台任务管理 | 6个 | JohnC & Claude |
| 系统管理 | `web/backend/app/api/system.py` | 系统状态、配置管理 | 15个 | JohnC & Claude |
| 指标库 | `web/backend/app/api/indicators.py` | 技术指标配置 | 8个 | JohnC & Claude |
| TradingView | `web/backend/app/api/tradingview.py` | TradingView集成 | 4个 | JohnC & Claude |
| 通知管理 | `web/backend/app/api/notification.py` | 消息通知管理 | 6个 | JohnC & Claude |
| 机器学习 | `web/backend/app/api/ml.py` | ML模型预测API | 8个 | JohnC & Claude |
| 策略管理 | `web/backend/app/api/strategy.py` | 策略定义和回测 | 10个 | JohnC & Claude |

#### B. 迁移API（Phase 1-3）

| API模块 | 文件路径 | 功能 | 端点数量 | 来源项目 | 迁移阶段 |
|---------|---------|------|---------|---------|----------|
| 实时监控 | `web/backend/app/api/monitoring.py` | 告警规则、实时行情、龙虎榜 | 12个 |  | Phase 1 |
| 技术分析 | `web/backend/app/api/technical_analysis.py` | 26个技术指标、交易信号 | 8个 |  | Phase 2 |
| 多数据源 | `web/backend/app/api/multi_source.py` | 数据源健康、优先级路由 | 12个 |  | Phase 3 |
| 公告监控 | `web/backend/app/api/announcement.py` | 官方公告、监控规则 | 11个 |  | Phase 3 |

**迁移总结**:
- **Phase 1**: 实时监控和告警系统（7种告警类型）
- **Phase 2**: 增强技术分析系统（26个指标，4大类别）
- **Phase 3**: 多数据源集成系统（EastMoney + Cninfo）

---

### 3.2 后端服务层

#### A. 原生业务服务

| 服务模块 | 文件路径 | 功能 | 作者 |
|---------|---------|------|------|
| 股票搜索服务 | `web/backend/app/services/stock_search_service.py` | 智能搜索、拼音匹配 | JohnC & Claude |
| TradingView服务 | `web/backend/app/services/tradingview_widget_service.py` | TradingView小部件生成 | JohnC & Claude |
| 任务管理服务 | `web/backend/app/services/task_manager.py` | 后台任务调度 | JohnC & Claude |
| ML预测服务 | `web/backend/app/services/ml_prediction_service.py` | 机器学习预测 | JohnC & Claude |

#### B. 迁移服务

| 服务模块 | 文件路径 | 功能 | 来源项目 | 迁移阶段 |
|---------|---------|------|---------|----------|
| 监控服务 | `web/backend/app/services/monitoring_service.py` | 实时监控、告警管理 |  | Phase 1 |
| 技术分析服务 | `web/backend/app/services/technical_analysis_service.py` | 26个技术指标计算 |  | Phase 2 |
| 多数据源管理器 | `web/backend/app/services/multi_source_manager.py` | 数据源路由、故障转移 |  | Phase 3 |
| 公告服务 | `web/backend/app/services/announcement_service.py` | 公告获取、监控评估 |  | Phase 3 |

---

### 3.3 后端适配器层（Web专用）

| 适配器 | 文件路径 | 功能 | 来源 |
|--------|---------|------|------|
| 基础适配器 | `web/backend/app/adapters/base.py` | 适配器基类 |  Phase 3 |
| 东方财富适配器 | `web/backend/app/adapters/eastmoney_enhanced.py` | EastMoney API封装 |  Phase 3 |
| 巨潮资讯适配器 | `web/backend/app/adapters/cninfo_adapter.py` | Cninfo公告接口 |  Phase 3 |
| AkShare扩展 | `web/backend/app/adapters/akshare_extension.py` | AkShare增强封装 | 原生扩展 |
| 问财适配器 | `web/backend/app/adapters/wencai_adapter.py` | 同花顺问财接口 | 原生 |

---

### 3.4 前端视图层 ⭐ **原生**

#### A. 核心业务视图（20个）

| 视图组件 | 文件路径 | 功能 | 作者 |
|---------|---------|------|------|
| 仪表板 | `web/frontend/src/views/Dashboard.vue` | 系统总览、数据展示 | JohnC & Claude |
| 登录页 | `web/frontend/src/views/Login.vue` | 用户登录 | JohnC & Claude |
| 市场行情 | `web/frontend/src/views/Market.vue` | 市场概览 | JohnC & Claude |
| 市场数据 | `web/frontend/src/views/MarketData.vue` | 详细行情数据 | JohnC & Claude |
| 通达信市场 | `web/frontend/src/views/TdxMarket.vue` | 通达信数据展示 | JohnC & Claude |
| 股票列表 | `web/frontend/src/views/Stocks.vue` | 股票列表管理 | JohnC & Claude |
| 技术分析 | `web/frontend/src/views/TechnicalAnalysis.vue` | 技术指标图表 | JohnC & Claude |
| 指标库 | `web/frontend/src/views/IndicatorLibrary.vue` | 指标配置管理 | JohnC & Claude |
| 问财查询 | `web/frontend/src/views/Wencai.vue` | 问财智能查询 | JohnC & Claude |
| 分析页面 | `web/frontend/src/views/Analysis.vue` | 综合分析 | JohnC & Claude |
| 设置页面 | `web/frontend/src/views/Settings.vue` | 系统设置 | JohnC & Claude |
| 任务管理 | `web/frontend/src/views/TaskManagement.vue` | 任务监控 | JohnC & Claude |
| 策略管理 | `web/frontend/src/views/StrategyManagement.vue` | 策略配置 | JohnC & Claude |
| 交易管理 | `web/frontend/src/views/TradeManagement.vue` | 交易记录 | JohnC & Claude |
| 回测分析 | `web/frontend/src/views/BacktestAnalysis.vue` | 回测结果展示 | JohnC & Claude |
| 风险监控 | `web/frontend/src/views/RiskMonitor.vue` | 风险指标监控 | JohnC & Claude |
| 404页面 | `web/frontend/src/views/NotFound.vue` | 错误页面 | JohnC & Claude |

#### B. 演示/Demo视图（5个）

| 视图组件 | 文件路径 | 功能 | 参考项目 |
|---------|---------|------|---------|
| OpenStock演示 | `web/frontend/src/views/OpenStockDemo.vue` | OpenStock集成演示 | temp/OpenStock |
| Freqtrade演示 | `web/frontend/src/views/FreqtradeDemo.vue` | Freqtrade策略演示 | temp/freqtrade |
| Pyprofiling演示 | `web/frontend/src/views/PyprofilingDemo.vue` | ML回测演示 | temp/pyprofiling |
| 股票分析演示 | `web/frontend/src/views/StockAnalysisDemo.vue` | 综合分析演示 | temp/stock-analysis |
| Tdxpy演示 | `web/frontend/src/views/TdxpyDemo.vue` | Tdxpy数据演示 | temp/tdxpy |

---

### 3.5 前端组件层

| 组件目录 | 功能 | 组件数量 | 作者 |
|---------|------|---------|------|
| `chart/` | 图表组件（K线、指标图） | ~8个 | JohnC & Claude |
| `config/` | 配置管理组件 | ~5个 | JohnC & Claude |
| `indicators/` | 指标展示组件 | ~10个 | JohnC & Claude |
| `market/` | 市场数据组件 | ~15个 | JohnC & Claude |
| `quant/` | 量化分析组件 | ~6个 | JohnC & Claude |
| `strategy/` | 策略管理组件 | ~8个 | JohnC & Claude |
| `task/` | 任务管理组件 | ~4个 | JohnC & Claude |
| `technical/` | 技术分析组件 | ~12个 | JohnC & Claude |
| `watchlist/` | 自选股组件 | ~6个 | JohnC & Claude |

---

## 🤖 四、机器学习与策略模块

### 4.1 ML策略系统 ⭐ **原生**

| 模块 | 文件路径 | 功能 | 作者 | 代码行数 |
|------|---------|------|------|---------|
| 价格预测器 | `ml_strategy/price_predictor.py` | LSTM价格预测模型 | JohnC & Claude | ~400行 |
| 特征工程 | `ml_strategy/feature_engineering.py` | 技术指标特征提取 | JohnC & Claude | ~300行 |
| ML策略主模块 | `ml_strategy/ml_strategy.py` | 策略框架、模型管理 | JohnC & Claude | ~500行 |

### 4.2 策略执行系统 ⭐ **原生**

| 模块 | 文件路径 | 功能 | 作者 |
|------|---------|------|------|
| 基础策略类 | `ml_strategy/strategy/base_strategy.py` | 策略抽象基类 | JohnC & Claude |
| 策略执行器 | `ml_strategy/strategy/strategy_executor.py` | 策略运行引擎 | JohnC & Claude |
| 信号管理器 | `ml_strategy/strategy/signal_manager.py` | 交易信号管理 | JohnC & Claude |
| 股票筛选器 | `ml_strategy/strategy/stock_screener.py` | 条件选股 | JohnC & Claude |

### 4.3 策略模板 ⭐ **原生**

| 模板 | 文件路径 | 策略类型 | 作者 |
|------|---------|---------|------|
| 动量策略模板 | `ml_strategy/strategy/templates/momentum_template.py` | 动量交易 | JohnC & Claude |
| 均值回归模板 | `ml_strategy/strategy/templates/mean_reversion_template.py` | 均值回归 | JohnC & Claude |
| 自定义模板 | `ml_strategy/strategy/templates/custom_template.py` | 自定义策略 | JohnC & Claude |

### 4.4 回测系统 ⭐ **原生**

| 模块 | 文件路径 | 功能 | 作者 |
|------|---------|------|------|
| 回测引擎 | `ml_strategy/backtest/backtest_engine.py` | 历史回测、性能评估 | JohnC & Claude |

### 4.5 实时数据系统 ⭐ **原生**

| 模块 | 文件路径 | 功能 | 作者 |
|------|---------|------|------|
| Tick接收器 | `ml_strategy/realtime/tick_receiver.py` | 实时行情接收 | JohnC & Claude |

### 4.6 自动化系统 ⭐ **原生**

| 模块 | 文件路径 | 功能 | 作者 |
|------|---------|------|------|
| 调度器 | `ml_strategy/automation/scheduler.py` | 定时任务调度 | JohnC & Claude |
| 通知管理器 | `ml_strategy/automation/notification_manager.py` | 多渠道通知 | JohnC & Claude |
| 预定义任务 | `ml_strategy/automation/predefined_tasks.py` | 常用任务模板 | JohnC & Claude |

---

## 🛠️ 五、工具与辅助模块

### 5.1 核心工具 ⭐ **原生**

| 工具模块 | 文件路径 | 功能 | 作者 |
|---------|---------|------|------|
| 列名映射器 | `utils/column_mapper.py` | 统一列名转换、中英文映射 | JohnC & Claude |
| 日期工具 | `utils/date_utils.py` | 日期格式化、交易日计算 | JohnC & Claude |
| 股票代码工具 | `utils/symbol_utils.py` | 股票代码格式转换 | JohnC & Claude |
| TDX服务器配置 | `utils/tdx_server_config.py` | 通达信服务器管理 | JohnC & Claude |
| 数据库健康检查 | `utils/check_db_health.py` | 数据库连接检查 | JohnC & Claude |
| API健康检查 | `utils/check_api_health.py` | API端点检查 | JohnC & Claude |
| API健康检查v2 | `utils/check_api_health_v2.py` | 增强版API检查 | JohnC & Claude |
| 测试日志API | `utils/test_logs_api.py` | 日志测试工具 | JohnC & Claude |
| Python头部添加器 | `utils/add_python_headers.py` | 批量添加文件头 | JohnC & Claude |
| 文档元数据添加器 | `utils/add_doc_metadata.py` | 批量添加文档元数据 | JohnC & Claude |
| Gitignore验证器 | `utils/validate_gitignore.py` | .gitignore规则检查 | JohnC & Claude |
| 测试命名验证器 | `utils/validate_test_naming.py` | 测试文件命名检查 | JohnC & Claude |

---

## 🧪 六、测试模块

### 6.1 核心功能测试 ⭐ **原生**

| 测试模块 | 文件路径 | 测试对象 | 作者 |
|---------|---------|---------|------|
| 统一管理器测试 | `tests/test_unified_manager.py` | 核心管理器 | JohnC & Claude |
| 数据库管理器测试 | `tests/test_database_manager.py` | 数据库连接 | JohnC & Claude |
| 数据库健康检查测试 | `tests/test_check_db_health.py` | 健康检查 | JohnC & Claude |
| AkShare适配器测试 | `tests/test_akshare_adapter.py` | AkShare数据源 | JohnC & Claude |
| TDX适配器测试 | `tests/test_tdx_adapter.py` | 通达信数据源 | JohnC & Claude |
| TDX二进制读取测试 | `tests/test_tdx_binary_read.py` | TDX数据解析 | JohnC & Claude |
| 自动化测试 | `tests/test_automation.py` | 自动化系统 | JohnC & Claude |
| ML集成测试 | `tests/test_ml_integration.py` | 机器学习模块 | JohnC & Claude |
| 回测组件测试 | `tests/test_backtest_components.py` | 回测引擎 | JohnC & Claude |

### 6.2 Web API测试 ⭐ **原生**

| 测试脚本 | 文件路径 | 测试对象 | 作者 |
|---------|---------|---------|------|
| 市场API测试v2 | `web/backend/scripts/test_market_v2_api.py` | 市场数据API | JohnC & Claude |
| 技术分析API测试 | `web/backend/scripts/test_technical_analysis_api.py` | 技术分析API | JohnC & Claude |
| 监控API测试 | `web/backend/scripts/test_monitoring_api.py` | 监控系统API | JohnC & Claude |
| 策略API测试 | `web/backend/scripts/test_strategy_api.py` | 策略管理API | JohnC & Claude |
| Phase 3 API测试 | `web/backend/scripts/test_phase3_api.py` | 多数据源API | JohnC & Claude |

---

## 📦 七、引入的第三方项目

### 7.1 已迁移功能 🔗 **引入**

**来源**: https://github.com/valuecell-project (假设)
**引入时间**: 2025-10-15 ~ 2025-10-23
**引入方式**: 代码迁移 + API重构

**迁移内容**:

#### Phase 1: 实时监控和告警系统
- **数据库表**: 5个（alert_rule, alert_record, realtime_monitoring, dragon_tiger_list, monitoring_statistics）
- **API端点**: 12个监控API
- **前端组件**: 监控仪表板、告警管理（未完全迁移）
- **功能**: 7种告警类型、龙虎榜跟踪、资金流向分析

#### Phase 2: 增强技术分析系统
- **技术指标**: 26个（趋势、动量、波动、成交量4大类）
- **API端点**: 8个技术分析API
- **服务**: 指标计算、交易信号生成
- **功能**: 批量指标计算、信号生成和分析

#### Phase 3: 多数据源集成系统
- **数据库表**: 6个（data_source_config, data_source_health, announcement等）
- **API端点**: 23个（12个多数据源 + 11个公告）
- **适配器**: EastMoney、Cninfo
- **功能**: 优先级路由、自动故障转移、官方公告监控

**项目位置**: `temp/valuecell/`

---

### 7.2 OpenStock项目 🔗 **引入**

**来源**: https://github.com/openstock-project (假设)
**引入时间**: 2025-10-20
**引入方式**: Demo演示页面

**引入内容**:
- **前端Demo**: `web/frontend/src/views/OpenStockDemo.vue`
- **功能**: 股票市场数据展示、热力图、板块分析
- **依赖**: OpenStock API（temp/OpenStock/）

**项目位置**: `temp/OpenStock/`

---

### 7.3 Pyprofiling项目 🔗 **引入**

**来源**: https://github.com/pyprofiling-project (假设)
**引入时间**: 2025-10-21
**引入方式**: Demo演示页面 + ML回测参考

**引入内容**:
- **前端Demo**: `web/frontend/src/views/PyprofilingDemo.vue`
- **功能**: ML特征工程、回测分析、策略优化
- **依赖**: Pyprofiling库（temp/pyprofiling/）

**项目位置**: `temp/pyprofiling/`

---

### 7.4 Freqtrade项目 🔗 **引入**

**来源**: https://github.com/freqtrade/freqtrade
**引入时间**: 2025-10-21
**引入方式**: Demo演示页面

**引入内容**:
- **前端Demo**: `web/frontend/src/views/FreqtradeDemo.vue`
- **功能**: 加密货币交易策略演示
- **依赖**: Freqtrade策略模板（temp/freqtrade/）

**项目位置**: `temp/freqtrade/`

---

### 7.5 Stock-Analysis项目 🔗 **引入**

**来源**: https://github.com/stock-analysis-project (假设)
**引入时间**: 2025-10-21
**引入方式**: Demo演示页面

**引入内容**:
- **前端Demo**: `web/frontend/src/views/StockAnalysisDemo.vue`
- **功能**: 综合股票分析、基本面分析
- **依赖**: 分析工具（temp/stock-analysis/）

**项目位置**: `temp/stock-analysis/`

---

### 7.6 Tdxpy项目 🔗 **引入**

**来源**: https://github.com/tdxpy-project (假设)
**引入时间**: 2025-10-21
**引入方式**: Demo演示页面 + pytdx库本地化

**引入内容**:
- **前端Demo**: `web/frontend/src/views/TdxpyDemo.vue`
- **本地pytdx库**: `temp/pytdx/`（tdx_adapter.py使用）
- **功能**: 通达信数据解析、多周期K线

**项目位置**: `temp/tdxpy/`

---

### 7.7 Instock项目 🔗 **引入**

**来源**: https://github.com/instock-project (假设)
**引入时间**: 2025-10-18
**引入方式**: 参考项目

**引入内容**:
- **功能**: 股票数据下载、指标计算参考

**项目位置**: `temp/instock/`

---

## 📊 八、数据库架构

### 8.1 当前数据库架构（Week 3简化后）

| 数据库 | 用途 | 状态 | 表数量 |
|--------|------|------|--------|
| **PostgreSQL** (mystocks) | 主数据库，包含所有数据类型 | ✅ 使用中 | ~50张 |
| **Redis** (db0) | 实时数据缓存 | ⏸️ 待激活 | 3 keys |

### 8.2 已移除的数据库

| 数据库 | 原用途 | 移除时间 | 迁移情况 |
|--------|--------|---------|---------|
| MySQL (quant_research) | 元数据和参考数据 | 2025-10-19 | 已迁移到PostgreSQL（299行） |
| TDengine | 高频时序数据 | 2025-10-19 | 仅5条测试数据，已删除 |

### 8.3 PostgreSQL表分类（~50张表）

#### A. 参考数据表（从MySQL迁移）
- `symbols` - 股票基础信息（299行）
- `trade_calendar` - 交易日历
- `index_components` - 指数成分股
- 等18张表

#### B. 市场数据表（原生）
- `stock_daily` - 日线数据
- `stock_minute` - 分钟数据（TimescaleDB hypertable）
- `realtime_quotes` - 实时行情

#### C. 迁移表（Phase 1-3）
- `alert_rule`, `alert_record` - 告警系统（Phase 1）
- `realtime_monitoring`, `dragon_tiger_list` - 监控数据（Phase 1）
- `data_source_config`, `data_source_health` - 多数据源（Phase 3）
- `announcement`, `announcement_monitor` - 公告系统（Phase 3）

#### D. 策略与ML表（原生）
- `strategy_definition` - 策略定义
- `strategy_result` - 策略结果
- `strategy_backtest` - 回测结果

#### E. 用户与系统表（原生）
- `users` - 用户管理
- `watchlist_group` - 自选股分组
- `watchlist_stock` - 自选股股票
- `indicator_configurations` - 指标配置

---

## 📈 九、项目统计

### 9.1 代码量统计

| 层次 | 模块数量 | 代码行数（估算） |
|------|---------|-----------------|
| **核心架构层** | 3个核心模块 | ~2000行 |
| **数据源适配器** | 7个生产适配器 + 2个辅助 | ~4500行 |
| **Web后端API** | 19个API模块 | ~8000行 |
| **Web后端服务** | 8个服务模块 | ~3000行 |
| **Web前端视图** | 25个视图组件 | ~15000行 |
| **Web前端组件** | ~70个组件 | ~10000行 |
| **ML与策略** | 13个模块 | ~3000行 |
| **工具模块** | 12个工具 | ~1500行 |
| **测试模块** | 14个测试 | ~2000行 |
| **合计** | ~200个模块 | ~49000行 |

### 9.2 功能模块分布

```
原生开发: 85% (~42000行)
  - 核心架构: 100%
  - 数据适配器: 100%
  - Web前后端: 75%
  - ML策略: 100%
  - 工具测试: 100%

迁移: 10% (~5000行)
  - Phase 1: 监控告警系统
  - Phase 2: 技术分析系统
  - Phase 3: 多数据源集成

第三方Demo: 5% (~2000行)
  - OpenStock Demo
  - Freqtrade Demo
  - Pyprofiling Demo
  - 等
```

### 9.3 API端点统计

| API类别 | 端点数量 | 来源 |
|---------|---------|------|
| 原生业务API | ~100个 | JohnC & Claude |
| 迁移API | ~43个 |  Phase 1-3 |
| **合计** | **~143个** | - |

---

## 🔄 十、维护指南

### 10.1 添加新模块时

请在本文档中添加：
1. **模块名称**
2. **文件路径**
3. **功能描述**
4. **来源**（原生/引入/扩展）
5. **作者/参考项目**
6. **代码行数**（可选）

### 10.2 模块分类标准

- **原生（⭐）**: JohnC或Claude从零开发
- **引入（🔗）**: 从其他项目迁移，并注明来源
- **扩展（🔧）**: 基于第三方库扩展开发

### 10.3 更新频率

建议每次重大功能更新时同步更新本文档。

---

## 📝 变更历史

| 日期 | 版本 | 变更内容 | 维护人 |
|------|------|---------|--------|
| 2025-10-24 | 1.0.0 | 初始版本，全面整理所有模块 | Claude |
| 2025-10-24 | 1.0.1 | 添加Week 3数据库简化说明 | Claude |

---

**文档结束**
