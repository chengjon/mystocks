# MyStocks 量化交易数据管理系统 - iFlow 交互指南

## 项目概述

MyStocks 是一个专业的企业级量化交易数据管理系统和 Web 管理平台，采用科学的数据分类体系和智能路由策略，实现多数据库协同工作。系统基于适配器模式和工厂模式构建统一的数据访问层，提供配置驱动的自动化管理，确保数据的高效存储、快速查询和实时监控。

### 项目基本信息

- **项目类型**: Python 代码项目 (企业级量化交易数据管理系统)
- **当前版本**: v3.1.0 (2025-11-24)
- **Python 版本**: 3.12+ (当前使用 3.12.11)
- **创建者**: JohnC & Claude
- **许可证**: MIT
- **Git 仓库**: git@github.com:chengjon/mystocks.git
- **代码规模**: 1894个Python文件，288个文档文件

### 核心技术栈

- **后端语言**: Python 3.12+
- **Web 框架**: FastAPI + Vue 3 + Element Plus + Socket.IO
- **数据库**: TDengine 3.3.x + PostgreSQL 17.x (TimescaleDB扩展)
- **数据源**: akshare (1.17.83), baostock, tushare, efinance, 通达信等
- **GPU 加速**: RAPIDS (cuDF/cuML) - 支持 WSL2 环境
- **AI/ML**: 机器学习策略系统，12个量化策略，AI策略分析
- **回测引擎**: 高性能回测系统，支持GPU加速
- **监控**: Prometheus + Grafana (可选)
- **开发工具**: Claude Code Hooks 系统 v2.0
- **测试框架**: pytest + Playwright + 覆盖率分析

### 项目特点

- **🌐 现代化Web管理平台**: 基于 FastAPI + Vue 3 的全栈架构，支持实时通信
- **🤖 多智能体系统**: 集成多智能体系统，支持实时监控、技术分析、多数据源集成
- **📊 双数据库存储策略**: TDengine(高频时序) + PostgreSQL(通用数据)
- **🔧 智能数据调用**: 统一接口规范，自动路由策略
- **🏗️ 先进数据流设计**: 适配器模式、工厂模式、策略模式、观察者模式
- **🚀 GPU 加速支持**: RAPIDS 深度集成，支持 WSL2 环境，15-20倍回测加速
- **📈 完整量化系统**: 内置12个量化策略，机器学习预测，高性能回测引擎
- **🔍 技术债务修复**: 正在进行的代码质量提升，测试覆盖率从6%提升至72%

## 项目结构

### 📁 重组后的科学目录结构 (v3.1.0)

项目已完成全面重组，从42个杂乱的根目录精简到13个科学组织的目录，符合 Python 最佳实践。整体架构经过Phase 1-6的迭代开发，已形成完整的企业级量化交易系统。

```
/opt/claude/mystocks_spec/
├── 📄 核心入口文件
│   ├── README.md                    # 项目主文档 (44.97 KB)
│   ├── CLAUDE.md                    # Claude Code 集成指南
│   ├── CHANGELOG.md                 # 版本变更日志
│   ├── LICENSE                      # MIT 许可证
│   ├── requirements.txt             # Python 依赖清单
│   ├── core.py                      # 核心模块入口点
│   ├── unified_manager.py           # 统一管理器入口点
│   ├── data_access.py               # 数据访问入口点
│   ├── monitoring.py                # 监控模块入口点
│   ├── __init__.py                  # Python 包标识
│   ├── .env                         # 环境变量 (2.20 KB)
│   ├── .env.example                 # 环境变量模板 (2.21 KB)
│   ├── .pylintrc                    # Pylint配置 (1.15 KB)
│   ├── mypy.ini                     # MyPy配置 (1.26 KB)
│   ├── .pre-commit-config.yaml      # 预提交钩子 (2.31 KB)
│   └── pytest.ini                  # Pytest配置 (603 B)
│
├── 📦 src/                          # 所有源代码 (1894个Python文件)
│   ├── adapters/                    # 数据源适配器 (7个核心适配器)
│   │   ├── tdx_adapter.py           # 通达信直连适配器 (1058行)
│   │   ├── financial_adapter.py     # 财务数据适配器 (1078行)
│   │   ├── akshare_adapter.py       # Akshare适配器 (510行)
│   │   ├── byapi_adapter.py         # BYAPI适配器 (625行)
│   │   ├── customer_adapter.py      # 自定义适配器 (378行)
│   │   ├── baostock_adapter.py      # Baostock适配器 (257行)
│   │   └── tushare_adapter.py       # Tushare适配器 (199行)
│   │
│   ├── core/                        # 核心管理类
│   │   ├── data_classification.py   # 数据分类系统
│   │   ├── data_manager.py          # 数据管理器 (90%覆盖率)
│   │   ├── unified_manager.py       # 统一管理器 (65%覆盖率)
│   │   ├── config_loader.py         # 配置加载器 (100%覆盖率)
│   │   ├── logging.py               # 日志系统 (62%覆盖率)
│   │   ├── exceptions.py            # 异常处理 (100%覆盖率)
│   │   └── batch_failure_strategy.py # 批处理失败策略 (82%覆盖率)
│   │
│   ├── ml_strategy/                 # 机器学习策略系统
│   │   ├── strategy/                # 12个量化策略
│   │   ├── backtest/                # 高性能回测引擎
│   │   ├── automation/              # 策略自动化
│   │   ├── indicators/              # 技术指标计算
│   │   ├── realtime/                # 实时策略执行
│   │   ├── feature_engineering.py   # 特征工程
│   │   ├── price_predictor.py       # 价格预测模型
│   │   └── ml_strategy.py           # 主策略控制器
│   │
│   ├── gpu/                         # GPU 加速系统
│   │   ├── api_system/              # GPU API服务 (100%测试覆盖)
│   │   └── accelerated/             # GPU加速计算
│   │
│   ├── monitoring/                  # 监控和告警系统
│   │   ├── performance_monitor.py   # 性能监控
│   │   ├── data_quality_monitor.py  # 数据质量监控
│   │   ├── alert_manager.py         # 告警管理器
│   │   └── monitoring_database.py   # 监控数据库
│   │
│   ├── data_access/                 # 数据库访问层
│   │   ├── tdengine_access.py       # TDengine访问 (56%覆盖率)
│   │   └── postgresql_access.py     # PostgreSQL访问 (67%覆盖率)
│   │
│   ├── interfaces/                  # 接口定义
│   ├── storage/                     # 存储层
│   │   ├── database/                # 数据库管理
│   │   └── mock_data_storage.py     # Mock数据存储
│   ├── api/                         # API 接口
│   ├── utils/                       # 工具函数
│   ├── backup_recovery/             # 备份恢复
│   ├── contract_testing/            # 契约测试
│   ├── data_sources/                # 数据导入模块
│   │   ├── factory.py               # 数据源工厂
│   │   ├── mock_data_source.py      # Mock数据源统一接口
│   │   └── mock/                    # Mock数据源实现
│   │       ├── business_mock.py     # 业务Mock数据
│   │       ├── relational_mock.py   # 关系Mock数据
│   │       └── timeseries_mock.py   # 时序Mock数据
│   ├── database_optimization/       # 数据库优化
│   ├── reporting/                   # 报告生成
│   ├── visualization/               # 可视化工具
│   └── mock/                        # 页面级Mock数据 (40+个模块)
│       ├── mock_Dashboard.py        # 仪表盘Mock数据
│       ├── mock_Market.py           # 市场行情Mock数据
│       ├── mock_Stocks.py           # 股票详情Mock数据
│       ├── mock_TechnicalAnalysis.py # 技术分析Mock数据
│       ├── mock_Wencai.py           # 问财查询Mock数据
│       ├── mock_StrategyManagement.py # 策略管理Mock数据
│       ├── mock_RealTimeMonitor.py  # 实时监控Mock数据
│       └── mock_IndicatorLibrary.py # 指标库Mock数据
│
├── 🌐 web/                          # Web 管理平台
│   ├── backend/                     # FastAPI 后端 (461行main.py)
│   │   ├── app/
│   │   │   ├── api/endpoints/       # API端点 (50+个端点)
│   │   │   │   ├── data.py          # 数据API
│   │   │   │   ├── monitoring.py    # 监控API
│   │   │   │   ├── technical_analysis.py # 技术分析API
│   │   │   │   ├── multi_source.py  # 多数据源API
│   │   │   │   ├── sse_endpoints.py # SSE实时推送
│   │   │   │   ├── cache.py         # 缓存管理API
│   │   │   │   └── pool_monitoring.py # 连接池监控
│   │   │   ├── core/                # 核心服务
│   │   │   ├── models/              # 数据模型
│   │   │   ├── services/            # 业务服务
│   │   │   └── main.py              # 应用入口
│   │   └── requirements.txt         # 后端依赖
│   │
│   └── frontend/                    # Vue 3 前端
│       ├── src/
│       │   ├── components/          # Vue组件 (Element Plus)
│       │   ├── views/               # 页面视图
│       │   ├── router/              # Vue Router配置
│       │   ├── stores/              # Pinia状态管理
│       │   ├── services/            # API调用服务
│       │   └── main.ts              # 应用入口
│       ├── package.json             # 前端依赖
│       ├── vite.config.ts           # Vite构建配置
│       └── .env                     # 环境变量
│
├── ⚙️ config/                        # 配置文件
│   ├── table_config.yaml            # 完整表结构配置
│   ├── adapter_priority_config.yaml # 适配器优先级配置
│   ├── strategy_config.yaml         # 策略配置
│   ├── docker-compose.yml           # Docker编排
│   └── lnav/                        # 日志查看器配置
│
├── 🔧 scripts/                       # 脚本工具
│   ├── tests/                        # 测试脚本
│   ├── runtime/                      # 运行时脚本
│   ├── database/                     # 数据库脚本
│   └── dev/                          # 开发工具
│
├── 📚 docs/                          # 完整文档 (288个文档文件)
│   ├── guides/                       # 用户指南
│   │   ├── Vue_FastAPI_AI_Strategy_Implementation_Guide.md
│   │   ├── Vue_FastAPI_GPU_System_Implementation_Guide.md
│   │   └── Vue_FastAPI_Implementation_Master_Guide.md
│   ├── architecture/                 # 架构设计文档
│   ├── api/                          # API 文档
│   ├── features/                     # 功能特性文档
│   └── reports/                      # 项目报告
│       ├── PROJECT_STATUS_REPORT.md  # 项目状态报告
│       ├── technical_debt_analysis_report.md # 技术债务分析
│       └── TEST_COVERAGE_SUMMARY.md  # 测试覆盖率报告
│
├── 🧪 tests/                         # 测试代码
│   ├── 单元测试                      # pytest单元测试
│   ├── 集成测试                      # 集成测试
│   └── 端到端测试                    # Playwright E2E测试
│
├── 📖 examples/                      # 示例代码
├── 📝 logs/                          # 日志目录
├── 💾 data/                          # 数据文件
├── 📊 reports/                       # 分析报告
├── 🎯 load_test_reports/             # 性能测试报告
├── 🏗️ specs/                         # 规范文档
├── 🔍 metrics/                       # 指标监控
├── 🤖 .claude/                       # Claude Code系统
│   ├── hooks/                        # 7个生产级Hooks
│   ├── skills/                       # 技能配置
│   └── agents/                       # 代理配置
└── 📦 .archive/                      # 归档内容
    ├── old_code/                     # 旧代码备份
    └── old_docs/                     # 旧文档备份
```

### 项目开发进度

```
Phase 1: 实时监控和告警系统 ████████████████████ 100% ✅
Phase 2: 增强技术分析 (26个技术指标) ████████████████ 100% ✅
Phase 3: 多数据源集成 ████████████████████ 100% ✅
Phase 4: GPU API System ████████████████████ 100% ✅
Phase 5: Backtest Engine (12个量化策略) ████████████████ 100% ✅
Phase 6: 技术债务修复 ████████░░░░░░░░░░░░ 40% 🔄 (进行中)
```

**Phase 6 技术债务修复进展**:
- ✅ 代码质量配置 (Pylint, MyPy, Pre-commit)
- ✅ 测试覆盖率从6%提升至72% (+66%)
- 🔄 Pylint错误修复: 215 → 目标0
- 🔄 持续提升至80%覆盖率目标

## 核心架构设计

### 数据分类体系

系统采用 5 大数据分类体系，基于数据特性选择最优存储策略：

#### 1. 市场数据 (Market Data)
- **TDengine 专用**: Tick 数据、分钟 K 线、深度数据
- **PostgreSQL**: 日线数据、实时行情快照

#### 2. 参考数据 (Reference Data)
- **PostgreSQL**: 股票信息、成分股信息、交易日历

#### 3. 衍生数据 (Derived Data)
- **PostgreSQL + TimescaleDB**: 技术指标、量化因子、模型输出、交易信号

#### 4. 交易数据 (Transaction Data)
- **PostgreSQL**: 订单记录、成交记录、持仓记录、账户资金

#### 5. 元数据 (Meta Data)
- **PostgreSQL**: 数据源状态、任务调度、策略参数、系统配置

### 数据库分工与存储方案

| 数据库 | 专业定位 | 适用数据 | 核心优势 |
|--------|----------|----------|----------|
| **TDengine** | 高频时序数据专用库 | Tick 数据、分钟 K 线、实时深度 | 极高压缩比(20:1)、超强写入性能、列式存储 |
| **PostgreSQL + TimescaleDB** | 通用数据仓库+分析引擎 | 日线 K 线、技术指标、量化因子、参考数据、交易数据、元数据 | 自动分区、复杂查询、ACID 事务、JSON 支持 |

**Week 3 简化成果**:
- ✅ MySQL 数据迁移到 PostgreSQL（18张表，299行数据）
- ✅ Redis 移除（配置的 db1 为空）
- ✅ 系统复杂度降低 50%

## 核心功能模块

### 1. 统一管理器 (unified_manager.py)

提供简单易用的统一接口，所有操作都通过 2 行代码完成，支持智能路由和自动优化：

```python
# 保存数据 - 自动路由到最优数据库
manager.save_data_by_classification(
    DataClassification.TICK_DATA, tick_df, 'tick_600000'
)

# 加载数据 - 统一语法，自动优化
data = manager.load_data_by_classification(
    DataClassification.DAILY_KLINE, 'daily_kline',
    filters={'symbol': '600000'}
)

# 智能批处理 - 自动故障转移和重试
results = manager.batch_process_with_failover(
    data_sources=['akshare', 'tdx'],
    operation='get_stock_daily',
    symbols=['600000', '000001']
)
```

### 2. 数据源适配器系统 (adapters/)

每个数据源都有专门的适配器实现统一接口，支持优先级路由和故障转移：

- **tdx_adapter.py**: 通达信直连，无限流，多周期 K 线 (1058行)
- **financial_adapter.py**: 双数据源(efinance+easyquotation)，财务数据全能 (1078行)
- **akshare_adapter.py**: 免费全面，历史数据研究首选 (510行)
- **byapi_adapter.py**: REST API，涨跌停股池，技术指标 (625行)
- **customer_adapter.py**: 实时行情专用 (378行)
- **baostock_adapter.py**: 高质量历史数据 (257行)
- **tushare_adapter.py**: 专业级，需 token (199行)

**智能路由特性**:
- 优先级配置: `config/adapter_priority_config.yaml`
- 自动故障转移: 失败时自动切换到备用数据源
- 健康监控: 实时监控各数据源状态
- 负载均衡: 智能分配请求负载

### 3. 机器学习策略系统 (ml_strategy/)

企业级量化策略平台，内置12个成熟策略和完整的ML流水线：

```python
# 策略回测示例
from src.ml_strategy import MLStrategySystem

ml_system = MLStrategySystem()

# 12个内置策略
strategies = [
    'momentum_reversal',    # 动量反转策略
    'volume_price_trend',   # 量价趋势策略
    'mean_reversion',       # 均值回归策略
    'statistical_arbitrage', # 统计套利策略
    'risk_parity',          # 风险平价策略
    'momentum_enhanced',    # 增强动量策略
    'volatility_targeting', # 波动率目标策略
    'trend_following',      # 趋势跟随策略
    'pairs_trading',        # 配对交易策略
    'factor_momentum',      # 因子动量策略
    'adaptive_allocation',  # 自适应配置策略
    'ai_enhanced'           # AI增强策略
]

# GPU加速回测
results = ml_system.backtest_strategy(
    strategy='ai_enhanced',
    symbol='600000',
    start_date='2020-01-01',
    end_date='2024-12-31',
    use_gpu=True,
    initial_capital=1000000
)

print(f"年化收益率: {results.annual_return:.2%}")
print(f"夏普比率: {results.sharpe_ratio:.3f}")
print(f"最大回撤: {results.max_drawdown:.2%}")
```

**核心组件**:
- **strategy/**: 12个量化策略实现
- **backtest/**: 高性能GPU回测引擎
- **automation/**: 策略自动化执行
- **indicators/**: 26个技术指标计算
- **realtime/**: 实时策略监控和执行
- **feature_engineering.py**: 高级特征工程
- **price_predictor.py**: AI价格预测模型

### 4. GPU 加速系统 (gpu/)

企业级GPU加速平台，提供15-20倍性能提升：

```python
from src.gpu.api_system import GPUApiServer

# 初始化GPU环境(WSL2支持)
gpu_server = GPUApiServer()

# 智能缓存系统
cache_stats = gpu_server.get_cache_statistics()
print(f"缓存命中率: {cache_stats.hit_rate:.2%}")
print(f"预加载命中率: {cache_stats.prefetch_hit_rate:.2%}")

# 批量GPU计算
import cupy as cp
data_gpu = cp.array(historical_data)
predictions = gpu_server.predict_batch(data_gpu, model='transformer')
```

**核心特性**:
- **RAPIDS深度集成**: cuDF/cuML一体化GPU加速
- **智能三级缓存**: 命中率从80%提升至90%+
  - L1: 应用层LRU缓存
  - L2: GPU内存缓存
  - L3: 智能预加载缓存
- **WSL2完整支持**: 解决WSL2环境下GPU访问问题
- **160+测试用例**: 100%测试覆盖率
- **6大优化策略**:
  1. 访问模式学习 (EWMA预测算法)
  2. 查询结果缓存 (MD5指纹去重)
  3. 负缓存机制 (缓存不存在数据)
  4. 自适应TTL管理 (4级热度分区)
  5. 智能压缩 (选择性压缩)
  6. 预测性预加载 (并发预加载)

### 5. Web管理平台 (web/)

现代化全栈Web应用，支持实时通信和响应式设计：

```bash
# 启动后端 (端口8000-8010自动检测)
cd web/backend && python -m uvicorn app.main:app --reload

# 启动前端 (端口3000-3010自动检测)
cd web/frontend && npm run dev

# 访问地址
# API文档: http://localhost:8000/api/docs
# 前端界面: http://localhost:3000
```

**前端特性** (Vue 3 + Element Plus):
- 响应式设计，适配桌面和移动端
- 实时数据推送 (Socket.IO + SSE)
- K线图表和技术指标可视化
- 策略回测结果展示
- 实时监控仪表板

**后端特性** (FastAPI + Socket.IO):
- 50+ API端点，完整RESTful设计
- Socket.IO实时通信
- CSRF安全保护
- 连接池监控
- 缓存管理API
- 数据库性能监控

### 6. 监控与告警系统

企业级监控解决方案，7×24小时系统监控：

- **操作监控**: 所有数据库操作自动记录，结构化日志
- **性能监控**: 慢查询检测、响应时间统计、连接池监控
- **质量监控**: 数据完整性、准确性、新鲜度检查
- **告警机制**: 7种告警类型 (价格突破、成交量激增等)
- **实时推送**: Socket.IO实时告警通知
- **多渠道支持**: 邮件、Webhook、日志记录

### 7. Claude Code Hooks 系统

生产级自动化工具链，提升开发效率：

**7个生产级Hooks**:
1. **user-prompt-submit-skill-activation.sh** - 智能技能激活
2. **post-tool-use-file-edit-tracker.sh** - 文件编辑追踪
3. **post-tool-use-database-schema-validator.sh** - 数据库架构验证
4. **post-tool-use-document-organizer.sh** - 文档组织检查
5. **stop-python-quality-gate.sh** - Python代码质量门禁
6. **session-start-task-master-injector.sh** - 会话开始任务注入
7. **session-end-cleanup.sh** - 会话结束清理

**状态**: ✅ 100%完成，92%成功率 (12/13测试通过)

## Mock 数据使用规则

### 🎯 概述

MyStocks 项目提供了完整的 Mock 数据系统，专为开发、测试和演示环境设计。系统基于环境变量控制，可以在真实数据源和 Mock 数据之间无缝切换，确保代码质量和数据管理的一致性。

**核心原则**: 所有模拟数据必须通过 Mock 数据模块提供，**严禁在业务代码中直接硬编码数据**。

### 🏗️ Mock 数据架构

#### 三层数据源架构

```
┌─────────────────────────────────────────────────────────────┐
│                    业务数据源 (Business)                      │
│                       business_mock.py                       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────┐    ┌──────────────────────┐       │
│  │  时序数据源            │    │  关系数据源           │       │
│  │  (TimeSeries)         │    │  (Relational)        │       │
│  │  timeseries_mock.py   │    │  relational_mock.py  │       │
│  └──────────────────────┘    └──────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

#### 环境变量控制机制

通过环境变量控制数据源类型：

| 环境变量 | 可选值 | 说明 |
|---------|--------|------|
| `USE_MOCK_DATA` | `true`/`false` | 全局 Mock 开关 |
| `TIMESERIES_DATA_SOURCE` | `mock`/`tdengine` | 时序数据源 |
| `RELATIONAL_DATA_SOURCE` | `mock`/`postgresql` | 关系数据源 |
| `BUSINESS_DATA_SOURCE` | `mock`/`composite` | 业务数据源 |

### 📁 Mock 数据文件结构

#### 1. 核心数据源模块 (`src/data_sources/`)

| 文件路径 | 用途 | 关键接口 |
|---------|------|---------|
| `factory.py` | 数据源工厂 | `get_timeseries_source()`, `get_relational_source()`, `get_business_source()` |
| `mock_data_source.py` | 统一 Mock 数据源 | 实现完整 DataSourceInterface 接口 |
| `mock/timeseries_mock.py` | Mock 时序数据 | `get_realtime_quotes()`, `get_kline_data()`, `get_fund_flow()` |
| `mock/relational_mock.py` | Mock 关系数据 | `get_watchlist()`, `get_strategy_configs()`, `search_stocks()` |
| `mock/business_mock.py` | Mock 业务数据 | `get_dashboard_summary()`, `execute_backtest()`, `calculate_risk_metrics()` |

#### 2. 页面 Mock 模块 (`src/mock/`)

| 文件名 | 用途 | 主要函数 |
|--------|------|---------|
| `mock_Dashboard.py` | 仪表盘数据 | `get_market_hot()`, `get_plate_performance()`, `get_fund_flow()` |
| `mock_Market.py` | 市场行情 | `get_market_heatmap()`, `get_real_time_quotes()`, `get_etf_list()` |
| `mock_Stocks.py` | 股票详情 | `get_stock_list()`, `get_real_time_quote()`, `get_history_profit()` |
| `mock_TechnicalAnalysis.py` | 技术分析 | `get_stock_kline()`, `get_technical_indicators()`, `get_signal_analysis()` |
| `mock_Wencai.py` | 问财查询 | `get_wencai_queries()`, `get_query_results()` |
| `mock_StrategyManagement.py` | 策略管理 | `get_strategy_definitions()`, `run_strategy_single()`, `get_strategy_results()` |
| `mock_RealTimeMonitor.py` | 实时监控 | `get_realtime_alerts()`, `get_monitoring_summary()` |
| `mock_IndicatorLibrary.py` | 指标库 | `get_indicator_list()`, `get_indicator_detail()` |

#### 3. 后端统一 Mock 管理 (`web/backend/app/mock/`)

| 文件名 | 用途 | 主要函数 |
|--------|------|---------|
| `unified_mock_data.py` | 统一 Mock 管理 | `get_dashboard_data()`, `get_stocks_data()`, `get_technical_data()` |

### 🚀 使用方法

#### 环境配置

**开发环境配置 (.env)**:
```bash
# 启用 Mock 数据系统
USE_MOCK_DATA=true
DATA_SOURCE=mock

# 后端服务配置
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8888
FRONTEND_PORT=3000

# CORS 配置
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**前端环境配置 (web/frontend/.env)**:
```bash
# API 基础 URL（指向 Mock 后端）
VITE_API_BASE_URL=http://localhost:8888

# Mock 模式标识
VITE_APP_MODE=mock
VITE_APP_TITLE=MyStocks Mock System

# 开发工具配置
VITE_DEBUG=true
VITE_LOG_LEVEL=debug
```

#### 使用规则

**规则 1: 通过工厂函数获取数据源** ✅
```python
from src.data_sources.factory import get_timeseries_source

source = get_timeseries_source(source_type="mock")
data = source.get_realtime_quotes(['600000', '000001'])
```

**规则 2: 使用统一数据接口** ✅
```python
from src.data_sources.mock_data_source import MockDataSource

source = MockDataSource()
stock_list = source.get_stock_list({'market': 'sh'})
indicators = source.get_technical_indicators('600000', '2024-01-01', '2024-12-31')
```

**规则 3: 禁止硬编码数据** ❌
```python
# 错误示例 - 严禁！
def get_stock_info():
    return {
        "symbol": "600000",
        "name": "浦发银行",
        "price": 12.50
    }
```

#### 统一数据获取示例

**时序数据获取**:
```python
from src.data_sources.factory import get_timeseries_source

source = get_timeseries_source(source_type="mock")

# K 线数据
kline_df = source.get_kline_data("600000", start_time, end_time, interval="1d")

# 实时行情
quotes = source.get_realtime_quotes(["600000", "000001"])

# 资金流向
fund_flow = source.get_fund_flow("600000", days=30)

# 市场概览
overview = source.get_market_overview()
```

**关系数据获取**:
```python
from src.data_sources.factory import get_relational_source

source = get_relational_source(source_type="mock")

# 自选股
watchlist = source.get_watchlist(user_id="123")

# 股票搜索
results = source.search_stocks(keyword="银行")

# 行业列表
industries = source.get_industry_list()
```

**业务数据获取**:
```python
from src.data_sources.factory import get_business_source

source = get_business_source(source_type="mock")

# 仪表盘数据
dashboard = source.get_dashboard_summary()

# 回测执行
backtest_result = source.execute_backtest(strategy_config, start_date, end_date)

# 风险指标
risk_metrics = source.calculate_risk_metrics(portfolio_id="123")
```

### 🛠️ 快速启动

#### 方式 1: 使用专用启动脚本
```bash
# 使用 Mock 数据启动完整系统
./scripts/dev/start_with_mock.sh

# 查看服务状态
./scripts/dev/start_with_mock.sh --check

# 停止服务
./scripts/dev/start_with_mock.sh --stop
```

#### 方式 2: 手动启动
```bash
# 1. 启动后端 Mock 服务
cd web/backend
export USE_MOCK_DATA=true
python -m uvicorn app.main:app --host 0.0.0.0 --port 8888 &

# 2. 启动前端服务
cd web/frontend
npm run dev

# 3. 访问地址
# API 文档: http://localhost:8888/api/docs
# 前端界面: http://localhost:3000
```

#### 方式 3: 使用 Docker
```bash
# 启动 Mock 数据环境
docker-compose -f config/docker-compose.yml up -d
```

### 🧪 API 端点示例

#### 监控模块
```bash
# 获取监控摘要
curl http://localhost:8888/api/monitoring/summary

# 获取实时告警
curl http://localhost:8888/api/monitoring/realtime/alerts
```

#### 问财模块
```bash
# 获取预定义查询
curl http://localhost:8888/api/market/wencai/queries

# 执行查询
curl -X POST http://localhost:8888/api/market/wencai/query \
  -H "Content-Type: application/json" \
  -d '{"query_name": "qs_1"}'
```

#### 技术分析模块
```bash
# 获取技术指标
curl http://localhost:8888/api/technical/600000/indicators

# 获取趋势指标
curl http://localhost:8888/api/technical/600000/trend
```

#### 策略管理模块
```bash
# 获取策略定义
curl http://localhost:8888/api/strategy/definitions

# 执行单策略
curl -X POST http://localhost:8888/api/strategy/single \
  -H "Content-Type: application/json" \
  -d '{"strategy_code": "volume_surge", "symbols": ["600000"]}'
```

### 🔧 高级功能

#### 支持随机种子保证可复现
```python
from src.data_sources.factory import get_timeseries_source

source = get_timeseries_source(source_type="mock")
source.set_random_seed(42)  # 设置随机种子

# 现在生成的数据是可复现的
data1 = source.get_kline_data("600000", start, end)

# 重新设置相同种子，得到相同数据
source.set_random_seed(42)
data2 = source.get_kline_data("600000", start, end)
# data1 == data2
```

#### 保持数据结构一致性
Mock 数据结构与真实 API 返回一致，便于无缝切换：
```python
def get_stock_quote(symbol: str) -> Dict:
    return {
        "symbol": symbol,           # 股票代码
        "name": "示例股票",          # 股票名称
        "price": 25.50,             # 当前价格
        "change": 0.35,             # 涨跌额
        "change_pct": 1.39,         # 涨跌幅%
        "volume": 12345678,         # 成交量
        "amount": 315678900,        # 成交额
        "high": 26.00,              # 最高价
        "low": 24.80,               # 最低价
        "open": 25.20,              # 开盘价
        "pre_close": 25.15,         # 昨收价
        "timestamp": datetime.now().isoformat()
    }
```

### 🔍 故障排查

#### 常见问题解决

**1. 端口占用**
```bash
# 检查端口占用
lsof -i :8888
lsof -i :3000

# 清理进程
pkill -f uvicorn
pkill -f "npm run dev"
```

**2. 环境变量未生效**
```bash
# 重新加载环境变量
source .env

# 检查变量设置
echo $USE_MOCK_DATA
```

**3. Mock 数据格式错误**
```bash
# 验证 API 响应
curl -s http://localhost:8888/api/monitoring/summary | jq '.'

# 检查 Mock 模块导入
python -c "from src.mock.mock_Wencai import get_wencai_queries; print(get_wencai_queries())"
```

#### 性能基准
```bash
# 响应时间测试
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:8888/api/monitoring/summary

# 并发测试
ab -n 1000 -c 10 http://localhost:8888/api/market/wencai/queries
```

**预期性能指标**:
- API 响应时间: < 50ms
- 并发支持: 100+ 请求/秒
- 数据一致性: 100%
- Mock 数据覆盖率: >90%

### 📋 代码审查检查清单

在代码审查时，请检查以下项目：

- [ ] 没有硬编码的模拟数据
- [ ] 所有数据通过工厂函数或 Mock 模块的 getter 函数获取
- [ ] 导入路径正确
- [ ] 函数有类型注解和文档字符串
- [ ] 数据结构与预期 API 一致
- [ ] 新增的 Mock 函数已添加到对应模块
- [ ] 支持随机种子实现可复现性
- [ ] 没有使用通配符导入

### 📚 相关文件索引

| 文件 | 说明 |
|------|------|
| `src/data_sources/factory.py` | 数据源工厂（入口） |
| `src/data_sources/mock_data_source.py` | 统一 Mock 数据源实现 |
| `src/data_sources/mock/` | Mock 数据源实现目录 |
| `src/mock/` | 页面级 Mock 数据目录 |
| `web/backend/app/mock/` | 后端统一 Mock 管理 |
| `scripts/dev/start_with_mock.sh` | Mock 环境启动脚本 |
| `scripts/tests/test_mock_*.py` | Mock 测试脚本 |
| `docs/guides/MOCK_DATA_USAGE_RULES.md` | Mock 数据使用详细规则 |
| `docs/MOCK_DATA_SYSTEM_GUIDE.md` | Mock 数据系统完整指南 |

## 构建和运行

### 环境要求

- **Python**: 3.12+ (当前使用 3.12.11)
- **TDengine**: 3.3.x (高频时序数据专用)
- **PostgreSQL**: 17.x + TimescaleDB扩展
- **GPU**: NVIDIA GPU + CUDA 12.x+ (可选，用于GPU加速)
- **Node.js**: 18+ (Web前端，vite 5.4+)
- **数据库**: 支持Docker部署或本地安装

### 快速开始

#### 1. 环境配置
```bash
# 克隆项目
git clone git@github.com:chengjon/mystocks.git
cd mystocks_spec

# 复制环境变量模板
cp .env.example .env

# 编辑.env文件配置数据库连接
# 数据库连接、API密钥等配置
```

#### 2. 安装依赖
```bash
# 基础Python依赖
pip install -r requirements.txt

# 开发依赖 (可选)
pip install -r requirements-mock.txt
pip install -r requirements-security.txt

# 后端依赖
cd web/backend
pip install -r requirements.txt

# 前端依赖
cd web/frontend
npm install
```

#### 3. 数据库服务启动
```bash
# 使用Docker启动数据库服务
docker-compose up -d tdengine postgresql

# 检查数据库状态
python scripts/database/check_tdengine_tables.py
python scripts/database/check_postgresql_tables.py
```

#### 4. GPU 加速依赖(可选)
```bash
# RTX 2080 GPU加速支持 (需要CUDA 12.x)
pip install cupy-cuda12x>=13.6.0
pip install cudf-cu12>=25.10.0 cuml-cu12>=25.10.0

# 检查GPU状态
nvidia-smi
python src/gpu/api_system/wsl2_gpu_init.py
```

#### 5. 系统初始化
```python
from unified_manager import MyStocksUnifiedManager
from core import DataClassification

# 创建统一管理器
manager = MyStocksUnifiedManager()

# 自动初始化系统
results = manager.initialize_system()
if results['config_loaded']:
    print("✅ 系统初始化成功!")

# 运行系统演示
python scripts/runtime/system_demo.py
```

#### 6. Web 平台启动 (自动端口检测)
```bash
# 启动后端 (端口8000-8010自动检测)
cd web/backend
python -m uvicorn app.main:app --reload

# 启动前端 (端口3000-3010自动检测)
cd web/frontend
npm run dev

# 或使用生产模式
npm run build
npm run preview
```

**访问地址**:
- API文档: http://localhost:8000/api/docs
- 前端界面: http://localhost:3000
- 实时监控: WebSocket连接自动建立

#### 7. 实时数据获取
```bash
# 使用akshare获取实时行情并保存
python run_realtime_market_saver.py

# 持续运行(每5分钟获取一次)
python run_realtime_market_saver.py --count -1 --interval 300

# 多数据源获取
python -c "
from src.factories.data_source_factory import get_data_source
source = get_data_source()
data = source.get_data_with_failover('realtime_quote', 'get_stock_daily', symbol='600000')
print('获取到实时数据:', len(data) if data else 0)
"

#### 8. GPU 加速系统启动
```bash
# 初始化GPU环境(WSL2环境支持)
cd src/gpu/api_system
python wsl2_gpu_init.py

# 启动GPU API服务
python main_server.py

# 运行性能测试 (160+用例，100%覆盖率)
./run_tests.sh all

# 查看缓存优化效果
python -c "
from gpu.api_system.services.cache_optimization_enhanced import get_cache_stats
stats = get_cache_stats()
print(f'缓存命中率: {stats.hit_rate:.2%}')
print(f'预加载命中率: {stats.prefetch_hit_rate:.2%}')
"
```

#### 9. 机器学习策略执行
```python
# 运行策略回测
python -c "
from src.ml_strategy import MLStrategySystem
ml = MLStrategySystem()

# 运行12个策略的回测
results = ml.run_all_strategies_backtest(
    symbols=['600000', '000001', '000002'],
    start_date='2020-01-01',
    end_date='2024-12-31',
    use_gpu=True
)

print('策略回测结果:')
for strategy, result in results.items():
    print(f'{strategy}: 年化收益率 {result.annual_return:.2%}')
"
```

#### 10. 测试系统运行
```bash
# 运行所有测试
pytest tests/ -v --cov=src --cov-report=html

# 特定模块测试
pytest tests/test_core/ -v
pytest tests/test_gpu/ -v

# 端到端测试
npx playwright test

# 代码质量检查
pylint src/
mypy src/
black src/ --check
```

#### 11. Claude Code Hooks
```bash
# 测试Hooks系统
.claude/hooks/post-tool-use-file-edit-tracker.sh --test

# 运行代码质量门禁
.claude/hooks/stop-python-quality-gate.sh

# 会话任务注入
.claude/hooks/session-start-task-master-injector.sh
```

## 数据源适配器使用

### 基础使用示例

```python
# 使用 akshare 适配器
from src.adapters.akshare_adapter import AkshareDataSource
import pandas as pd

# 创建数据源实例
adapter = AkshareDataSource()

# 获取股票基本信息
stock_info = adapter.get_stock_basic()
print(f"获取到 {len(stock_info)} 只股票信息")

# 获取日线数据
daily_data = adapter.get_stock_daily('600000', '2024-01-01', '2024-12-31')
print(f"获取到 {len(daily_data)} 条日线数据")

# 通过统一管理器保存数据
from unified_manager import MyStocksUnifiedManager
from core import DataClassification

manager = MyStocksUnifiedManager()
manager.save_data_by_classification(daily_data, DataClassification.DAILY_KLINE)
```

### 财务数据适配器

```python
# 使用财务数据适配器(双数据源)
from src.adapters.financial_adapter import FinancialDataSource

adapter = FinancialDataSource()

# 获取股票财务数据
financial_data = adapter.get_stock_financial('600000')
print(f"获取到财务数据: {financial_data.shape}")

# 获取基本面数据
basic_info = adapter.get_stock_basic_info('600000')
print(f"获取到基本面信息: {basic_info}")
```

### 通达信适配器

```python
# 使用通达信适配器(直连，无限流)
from src.adapters.tdx_adapter import TdxDataSource

adapter = TdxDataSource()

# 获取多周期 K 线数据
kline_data = adapter.get_kline_data('600000', '1min', '2024-01-01', '2024-12-31')
print(f"获取到1分钟 K 线数据: {len(kline_data)} 条")
```

## Web API 使用

### 核心 API 端点

#### 实时监控系统 (Phase 1)
```
GET  /api/monitoring/alert-rules          # 获取告警规则
POST /api/monitoring/alert-rules          # 创建告警规则
GET  /api/monitoring/realtime             # 获取实时行情
POST /api/monitoring/realtime/fetch       # 获取最新实时数据
GET  /api/monitoring/dragon-tiger         # 获取龙虎榜
GET  /api/monitoring/summary              # 获取监控摘要
```

#### 技术分析系统 (Phase 2)
```
GET  /api/technical/{symbol}/indicators   # 获取所有技术指标
GET  /api/technical/{symbol}/trend        # 获取趋势指标
GET  /api/technical/{symbol}/momentum     # 获取动量指标
GET  /api/technical/{symbol}/volatility   # 获取波动性指标
GET  /api/technical/{symbol}/signals      # 获取交易信号
POST /api/technical/batch/indicators      # 批量获取指标
```

#### 多数据源系统 (Phase 3)
```
GET  /api/multi-source/health             # 获取所有数据源健康状态
GET  /api/multi-source/realtime-quote     # 获取实时行情（多数据源）
GET  /api/multi-source/fund-flow          # 获取资金流向（多数据源）
GET  /api/announcement/today              # 获取今日公告
GET  /api/announcement/important          # 获取重要公告
POST /api/announcement/monitor/evaluate   # 评估监控规则
```

### API 使用示例

```python
import requests

# 获取实时行情
response = requests.get('http://localhost:8888/api/monitoring/realtime')
real_time_data = response.json()

# 获取技术指标
response = requests.get('http://localhost:8888/api/technical/600000/indicators')
indicators = response.json()

# 获取数据源健康状态
response = requests.get('http://localhost:8888/api/multi-source/health')
health_status = response.json()
```

## 核心功能特性

### 1. 实时监控系统
- **告警规则**: 7种告警类型(价格突破、成交量激增等)
- **龙虎榜跟踪**: 实时监控大单交易
- **资金流向分析**: 主力资金流入流出统计
- **自定义规则**: 用户自定义监控条件

### 2. 技术分析系统
- **26个技术指标**: 趋势(MA、MACD)、动量(RSI、KDJ)、波动(ATR)、成交量(OBV)
- **交易信号生成**: 基于技术指标的买卖信号
- **可视化图表**: 实时 K 线图和指标图表
- **批量计算**: 高效的批量指标计算

### 3. 多数据源集成
- **优先级路由**: 智能数据源选择和故障转移
- **数据源健康监控**: 实时监控各数据源状态
- **公告监控**: 类似 SEC Agent 的官方公告监控
- **API 限流管理**: 智能控制 API 调用频率

### 4. GPU 加速系统 (Phase 4)
- **RAPIDS 深度集成**: cuDF/cuML 一体化 GPU 加速
- **15-20倍回测加速**: 高性能策略回测
- **智能三级缓存**: L1 应用层 + L2 GPU 内存 + L3 Redis，命中率>90%
- **WSL2 支持**: 完整解决 WSL2 下 RAPIDS GPU 访问问题
- **测试覆盖**: 160+ 测试用例，100% 测试覆盖率

## 开发规范

### 代码风格
- **Python**: 遵循 PEP 8 规范，使用类型注解
- **配置驱动**: 所有表结构通过 YAML 配置管理
- **模块化设计**: 适配器模式，统一数据源接口
- **错误处理**: 完善的异常处理和日志记录
- **监控集成**: 所有操作自动记录到监控数据库

### 测试规范
- **单元测试**: pytest 框架，覆盖核心功能
- **集成测试**: 数据库连接、适配器功能
- **性能测试**: GPU 加速效果、缓存命中率
- **端到端测试**: 完整工作流程验证
- **契约测试**: API 接口契约验证

### 部署规范
- **配置分离**: 环境变量和配置文件分离
- **数据库监控**: 健康检查、性能监控
- **日志管理**: 结构化日志，便于问题排查
- **备份策略**: 自动数据备份和恢复

### Claude Code 集成
- **Hooks 系统**: 7 个生产就绪的自动化脚本
- **Skills 配置**: 8 个专业技能模板
- **Agents 配置**: 9 个专门代理配置
- **质量门禁**: 自动化代码质量检查

## 性能优化

### 缓存策略
- **L1 缓存**: 应用层 LRU 缓存，命中率>90%
- **L2 缓存**: PostgreSQL 查询缓存
- **L3 缓存**: TDengine 内存优化

### 数据库优化
- **TDengine**: 超高压缩比(20:1)，列式存储
- **PostgreSQL**: TimescaleDB 扩展，自动分区
- **索引策略**: 基于查询模式的智能索引

### GPU 优化
- **并行计算**: 多策略同时回测
- **内存管理**: 智能 GPU 内存分配和释放
- **批处理**: 大数据集分批 GPU 处理
- **智能缓存**: 三级缓存系统，命中率>90%

## 故障排查

### 常见问题
1. **数据库连接失败**: 检查网络和配置
2. **TDengine 初始化错误**: 已修复，参考 TDENGINE_FIX_COMPLETION_REPORT.md
3. **GPU 初始化失败**: 检查 CUDA 和驱动版本，WSL2 需要特殊配置
4. **Web 服务启动失败**: 确认端口占用和依赖
5. **数据源 API 限流**: 调整请求频率和重试策略

### 日志位置
- **系统日志**: `mystocks_system.log`
- **适配器日志**: `adapters/*.log`
- **Web 日志**: `web/backend/logs/`
- **GPU 日志**: `gpu_api_system/logs/`
- **Hooks 日志**: `.claude/logs/`

### 监控面板
- **Grafana 面板**: http://localhost:3000 (如果配置了)
- **TDengine 控制台**: http://localhost:6041
- **PostgreSQL 控制台**: pgAdmin (如果配置了)
- **Claude Code**: http://localhost:3001 (如果配置了)

## 项目版本历史

### v3.1.0 (2025-11-24)
- **企业级量化系统**: 完整机器学习策略系统，12个量化策略
- **Phase 6 技术债务修复**: 测试覆盖率从6%提升至72%，代码质量持续改善
- **GPU回测引擎**: 15-20倍性能提升，支持大规模回测
- **AI策略分析**: 集成AI增强策略，机器学习预测模型
- **Web平台完善**: Socket.IO实时通信，CSRF安全保护
- **监控系统增强**: 7种告警类型，实时性能监控

### v1.3.1 (2025-11-12)
- **Claude Code Hooks 系统完善**: 修复 PostToolUse:Write Hooks JSON 错误处理
- **测试验证**: 6 个测试场景全部通过
- **文档更新**: 详细修复历史和配置指南
- **架构优化**: 文档结构优化，路径修正，版本信息更新

### v1.3.0 (2025-11-04)
- **GPU 缓存优化**: 6 大核心优化策略，命中率从 80% 提升至 90%+
- **WSL2 GPU 支持**: 完全解决 WSL2 环境下 RAPIDS GPU 访问问题
- **测试系统**: 160+ 测试用例，100% 测试覆盖率

### v3.0.0 (2025-10-19)
- **Week 3 简化**: 数据库架构从 4 库简化为 2 库
- **集成**: 完成 Phase 1-3 功能迁移
- **项目重组**: 从 42 个目录精简到 13 个科学组织目录
- **Web 界面**: 完整的 FastAPI + Vue 3 管理平台
- **GPU 支持**: RAPIDS 加速系统，包含 WSL2 支持

## 快速参考

### 启动命令速查
```bash
# 数据库服务
docker-compose up -d tdengine postgresql

# 系统初始化
python scripts/runtime/system_demo.py

# 后端服务
cd web/backend && python -m uvicorn app.main:app --reload

# 前端服务
cd web/frontend && npm run dev

# GPU 服务
cd src/gpu/api_system && python main_server.py

# 实时数据
python run_realtime_market_saver.py --count -1 --interval 300

# 测试系统
pytest tests/ -v

# Claude Code
.claude/hooks/session-start-task-master-injector.sh
```

### 文件导入速查
```python
# 核心模块
from src.core import MyStocksUnifiedManager, DataClassification

# 数据源适配器
from src.adapters import AkshareDataSource, TdxDataSource

# 数据库访问
from src.data_access import TDengineDataAccess, PostgreSQLDataAccess

# 监控
from src.monitoring import PerformanceMonitor, AlertManager

# Web 后端
from web.backend.app.main import app

# GPU 系统 (集成在 src 目录下)
from src.gpu.api_system.services.gpu_api_server import GPUApiServer
```

### 配置检查
```bash
# 环境变量
cat .env

# 数据库连接
python scripts/database/check_tdengine_tables.py
python scripts/database/check_postgresql_tables.py

# GPU 状态
nvidia-smi
python src/gpu/api_system/wsl2_gpu_init.py

# Claude Code
.claude/hooks/post-tool-use-file-edit-tracker.sh --test
```

## 扩展开发

### 添加新数据源
1. 实现 `IDataSource` 接口
2. 创建适配器类，继承基础适配器
3. 注册到 DataSourceFactory
4. 在配置文件中添加连接参数

### 自定义技术指标
1. 在 `src/monitoring/technical_indicators.py` 中实现指标逻辑
2. 添加到指标注册表
3. 配置计算参数和缓存策略

### Web 页面开发
1. 后端: 在 `web/backend/app/api/` 中添加 API 端点
2. 前端: 在 `web/frontend/src/components/` 中添加 Vue 组件
3. 路由: 在 `web/frontend/src/router/` 中配置路由
4. 状态管理: 在 `web/frontend/src/stores/` 中添加 Pinia store
5. 样式: 使用 Element Plus 组件库

### Claude Code Hooks 开发
1. 在 `.claude/hooks/` 中创建脚本
2. 添加执行权限：`chmod +x script_name.sh`
3. 配置到 `.claude/config.json`
4. 测试 Hooks 功能

## 最佳实践

### 数据管理
- 定期备份关键数据
- 监控数据质量和完整性
- 合理设置数据保留策略
- 及时清理过期日志

### 性能调优
- 定期分析慢查询
- 优化数据库连接池
- 调整缓存大小和 TTL
- 监控 GPU 利用率

### 安全措施
- 定期更新依赖包
- 加密存储敏感信息
- 限制数据库访问权限
- 记录操作审计日志

### Claude Code 使用
- 定期更新 Hooks 脚本
- 监控 Hook 执行状态
- 备份配置文件
- 保持文档同步

## 支持和联系

- **项目状态**: 最新状态参考 `PROJECT_STATUS_QUICK_INDEX.md`
- **详细文档**: 参见 `docs/` 目录下的完整文档
- **变更日志**: 详见 `CHANGELOG.md`
- **问题排查**: 参考各模块的故障排查文档
- **Claude Code**: 参见 `CLAUDE.md` 集成指南

---

*本文档基于 MyStocks v3.1.0 生成，最后更新: 2025-11-24*
*用于 iFlow CLI 交互指导，项目完整概览和快速入门参考*
