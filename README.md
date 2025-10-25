# MyStocks 量化交易数据管理系统

**创建人**: JohnC & Claude
**版本**: 3.0.0
**批准日期**: 2025-10-15
**最后修订**: 2025-10-24
**本次修订内容**: Week 3数据库简化完成 + Adapter整理 + ValueCell Phase 3完成

---

## ⚡ Week 3 重大更新 (2025-10-19)

**数据库架构简化**: 4数据库 → 2数据库 (TDengine + PostgreSQL)

**简化成果**:
- ✅ MySQL数据迁移到PostgreSQL（18张表，299行数据）
- ✅ **TDengine保留**: 专用于高频时序数据（tick/分钟线）
- ✅ **PostgreSQL**: 处理所有其他数据类型（含TimescaleDB扩展）
- ✅ Redis移除（配置的db1为空）
- ✅ 系统复杂度降低50%

**核心原则**: **专库专用，简洁胜于过度复杂**

详细评估请参阅：[ADAPTER_AND_DATABASE_ARCHITECTURE_EVALUATION.md](./ADAPTER_AND_DATABASE_ARCHITECTURE_EVALUATION.md)

---

[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](./CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-green.svg)](https://fastapi.tiangolo.com)
[![Vue](https://img.shields.io/badge/Vue-3.4%2B-brightgreen.svg)](https://vuejs.org)

MyStocks 是一个专业的量化交易数据管理系统和 Web 管理平台，采用科学的数据分类体系和智能路由策略，实现多数据库协同工作。系统基于适配器模式和工厂模式构建统一的数据访问层，提供配置驱动的自动化管理，确保数据的高效存储、快速查询和实时监控。

**最新特性 (ValueCell Migration)**:
- ✅ **Phase 1**: 实时监控和告警系统（龙虎榜、资金流向、自定义规则）
- ✅ **Phase 2**: 增强技术分析系统（26个技术指标、交易信号生成）
- ✅ **Phase 3**: 多数据源集成系统（优先级路由、自动故障转移、公告监控）

## 🎯 核心特点

### 🌐 现代化 Web 管理平台
基于 FastAPI + Vue 3 的全栈架构，提供直观的可视化管理界面：
- **FastAPI 后端**: 高性能异步 API，支持 WebSocket 实时推送
- **Vue 3 前端**: Element Plus UI 组件库，响应式设计
- **RESTful API**: 完整的 API 文档（Swagger/OpenAPI）
- **实时监控**: 龙虎榜、资金流向、告警通知实时展示
- **技术分析**: 26个技术指标可视化，交易信号图表
- **多数据源**: 数据源健康监控、优先级配置、故障转移管理

### 🤖 ValueCell 多智能体系统迁移
从 ValueCell 项目迁移的核心功能，实现专业的量化交易支持：
- **实时监控系统** (Phase 1): 7种告警规则类型，龙虎榜跟踪，资金流向分析
- **增强技术分析** (Phase 2): 26个专业技术指标，4大类别（趋势、动量、波动、成交量）
- **多数据源集成** (Phase 3): 优先级路由、自动故障转移、官方公告监控（类似SEC Agent）

### 📊 双数据库存储策略 (Week 3后)
基于数据特性和访问频率的专业化存储方案：
- **高频时序数据** (Tick/分钟线) → TDengine（极致压缩比20:1，超强写入性能）
- **历史K线数据** (日线/周线/月线) → PostgreSQL + TimescaleDB扩展（复杂时序查询）
- **参考数据** (股票信息、交易日历) → PostgreSQL标准表（从MySQL迁移299行）
- **衍生数据** (技术指标、量化因子) → PostgreSQL标准表（AI/ML计算结果）
- **交易数据** (订单、成交、持仓) → PostgreSQL标准表（ACID事务保证）
- **监控数据** → PostgreSQL独立schema（系统运维监控）

### 🔧 智能的数据调用与操作方法
提供统一、简洁的数据访问接口，自动处理底层复杂性：
- **统一接口规范**: 一套API访问所有数据库
- **自动路由策略**: 根据数据类型智能选择存储引擎
- **配置驱动管理**: YAML配置自动创建表结构
- **实时数据缓存**: 热数据毫秒级访问
- **批量操作优化**: 高效的数据读写策略

### 🏗️ 先进的数据流与调用方案
采用现代软件工程设计模式，实现高效的多源数据管理：
- **适配器模式**: 统一不同数据源的访问接口
- **工厂模式**: 动态创建和管理数据源实例
- **策略模式**: 灵活的数据存储和查询策略
- **观察者模式**: 实时监控和告警机制

## 📊 一、数据分类与存储策略

### 5大数据分类体系
基于数据特性、访问频率和使用场景的科学分类，确保每类数据都能获得最优的存储和查询性能：

#### 第1类：市场数据 (Market Data)
**特点**: 高频时序数据，写入密集，时间范围查询
- **Tick数据** → **TDengine** (超高频实时处理，毫秒级延迟)
- **分钟K线** → **TDengine** (高频时序存储，20:1压缩比)
- **日线数据** → **PostgreSQL + TimescaleDB** (历史分析，复杂查询)
- **深度数据** → **TDengine** (实时订单簿，列式存储)

#### 第2类：参考数据 (Reference Data)
**特点**: 相对静态，关系型结构，频繁JOIN操作
- **股票信息** → **PostgreSQL** (基础信息，从MySQL迁移)
- **成分股信息** → **PostgreSQL** (指数成分股，支持JSON)
- **交易日历** → **PostgreSQL** (交易日、节假日，ACID保证)

#### 第3类：衍生数据 (Derived Data)
**特点**: 计算密集，时序分析，复杂查询
- **技术指标** → **PostgreSQL + TimescaleDB** (复杂计算结果，自动分区)
- **量化因子** → **PostgreSQL + TimescaleDB** (因子计算，物化视图)
- **模型输出** → **PostgreSQL + TimescaleDB** (AI/ML结果，JSON支持)
- **交易信号** → **PostgreSQL + TimescaleDB** (策略信号，触发器支持)

#### 第4类：交易数据 (Transaction Data)
**特点**: 事务完整性要求高，需要ACID保证
- **订单记录** → **PostgreSQL** (完整事务日志，持久化存储)
- **成交记录** → **PostgreSQL** (历史交易数据，复杂关联查询)
- **持仓记录** → **PostgreSQL** (持仓历史，审计追踪)
- **账户状态** → **PostgreSQL** (账户管理，强一致性保证)

#### 第5类：元数据 (Meta Data)
**特点**: 配置管理，系统状态，结构化存储
- **数据源状态** → **PostgreSQL** (数据源管理，从MySQL迁移)
- **任务调度** → **PostgreSQL** (定时任务配置，JSON存储)
- **策略参数** → **PostgreSQL** (策略配置，版本控制)
- **系统配置** → **PostgreSQL** (系统设置，集中管理)

### 数据库分工与存储方案 (Week 3简化后)

| 数据库 | 专业定位 | 适用数据 | 核心优势 |
|--------|----------|----------|----------|
| **TDengine** | 高频时序数据专用库 | Tick数据、分钟K线、实时深度 | 极高压缩比(20:1)、超强写入性能、列式存储 |
| **PostgreSQL + TimescaleDB** | 通用数据仓库+分析引擎 | 日线K线、技术指标、量化因子、参考数据、交易数据、元数据 | 自动分区、复杂查询、ACID事务、JSON支持 |

**说明**:
- ✅ **TDengine**: 专注高频市场数据（毫秒级Tick、分钟K线），极致压缩和写入性能
- ✅ **PostgreSQL**: 处理所有其他数据类型，TimescaleDB扩展提供时序优化
- ❌ **MySQL已移除**: 所有参考数据和元数据已迁移至PostgreSQL（299行数据）
- ❌ **Redis已移除**: 配置的db1为空，未在生产环境使用

## 🔧 二、数据调用与操作方法

### 统一接口规范
所有数据操作都通过统一的接口进行，隐藏底层数据库差异：

```python
from unified_manager import MyStocksUnifiedManager
from core import DataClassification

# 创建统一管理器
manager = MyStocksUnifiedManager()

# 自动路由保存 - 系统自动选择最优数据库
manager.save_data_by_classification(data, DataClassification.TICK_DATA)     # → TDengine (高频时序)
manager.save_data_by_classification(data, DataClassification.SYMBOLS_INFO)  # → PostgreSQL (参考数据)
manager.save_data_by_classification(data, DataClassification.DAILY_KLINE)   # → PostgreSQL + TimescaleDB (日线数据)

# 智能查询 - 统一语法，自动优化
data = manager.load_data_by_classification(
    DataClassification.DAILY_KLINE,
    filters={'symbol': '600000', 'date': '>2024-01-01'},
    order_by='date DESC',
    limit=1000
)
```

### 数据更新策略
支持多种数据更新模式，适应不同业务场景：

- **增量更新**: 只同步新增和变更的数据
- **批量更新**: 高效的大量数据批量处理
- **实时更新**: 毫秒级的实时数据推送
- **定时更新**: 自动化的定期数据同步

### 数据流工作流程 (Week 3简化后)

```mermaid
graph TD
    A[数据源] --> B[适配器层]
    B --> C[统一管理器]
    C --> D{数据分类识别}
    D -->|高频市场数据<br/>Tick/分钟线| E[TDengine]
    D -->|日线K线| F[PostgreSQL<br/>TimescaleDB]
    D -->|参考数据| F
    D -->|衍生数据<br/>技术指标/因子| F
    D -->|交易数据<br/>订单/持仓| F
    D -->|元数据<br/>系统配置| F
    J[监控系统] --> K[PostgreSQL<br/>独立schema]
    C --> J

    style E fill:#ff9999
    style F fill:#99ccff
    style K fill:#ccffcc
```

### 数据缓存方法 (Week 3简化后)

#### 两层缓存架构
1. **L1缓存**: 应用层缓存 (微秒级访问，Python字典/LRU缓存)
2. **L2缓存**: 数据库查询缓存 (毫秒级访问，PostgreSQL查询缓存/TDengine内存优化)

**说明**: Redis缓存层已移除，应用层缓存通过Python内置cachetools和functools.lru_cache实现

#### 智能缓存策略
- **热点数据预加载**: 自动识别并预加载热点数据到应用层缓存
- **LRU自动淘汰**: 最近最少使用数据自动清理 (cachetools.LRUCache)
- **分级缓存更新**: 根据数据重要性设置不同的更新频率和TTL

## 🏗️ 三、数据流与调用方案

### 数据源整合的核心设计模式

#### 适配器模式 (Adapter Pattern)
统一不同数据源的访问接口，屏蔽底层API差异：

```python
# 所有数据源都实现统一接口
class IDataSource:
    def get_stock_daily(self, symbol, start_date, end_date): pass
    def get_real_time_data(self, symbol): pass

# 不同数据源的适配器实现
class AkshareAdapter(IDataSource): ...
class TushareAdapter(IDataSource): ...
class FinancialAdapter(IDataSource): ...
```

#### 工厂模式 (Factory Pattern)
动态创建和管理数据源实例，支持运行时切换：

```python
# 工厂类根据配置创建相应的数据源
class DataSourceFactory:
    @staticmethod
    def create_data_source(source_type: str) -> IDataSource:
        if source_type == 'akshare':
            return AkshareAdapter()
        elif source_type == 'tushare':
            return TushareAdapter()
        # 支持运行时动态扩展
```

#### 策略模式 (Strategy Pattern)
灵活的数据存储和查询策略，根据数据特性自动优化：

```python
class DataStorageStrategy:
    # 数据分类到数据库的智能映射（Week 3简化后 - 仅2数据库）
    CLASSIFICATION_TO_DATABASE = {
        # 高频时序数据 → TDengine
        DataClassification.TICK_DATA: DatabaseTarget.TDENGINE,
        DataClassification.MINUTE_KLINE: DatabaseTarget.TDENGINE,

        # 所有其他数据 → PostgreSQL
        DataClassification.DAILY_KLINE: DatabaseTarget.POSTGRESQL,
        DataClassification.SYMBOLS_INFO: DatabaseTarget.POSTGRESQL,
        DataClassification.FINANCIAL_DATA: DatabaseTarget.POSTGRESQL,
        DataClassification.TECHNICAL_INDICATORS: DatabaseTarget.POSTGRESQL,
        DataClassification.TRADING_ORDERS: DatabaseTarget.POSTGRESQL,
    }
```

#### 观察者模式 (Observer Pattern)
实时监控和告警机制，自动响应系统状态变化：

```python
# 监控系统自动观察所有数据库操作
class MonitoringDatabase:
    def log_operation_start(self, operation_details): ...
    def log_operation_result(self, success, metrics): ...
    
# 告警管理器响应异常情况
class AlertManager:
    def create_alert(self, level, title, message): ...
```

### 高效管理多源数据

#### 数据源负载均衡
- **主备切换**: 主数据源失败时自动切换到备用源
- **并发控制**: 智能控制API调用频率，避免超限
- **错误重试**: 指数退避重试机制，提高成功率

#### 数据质量保证
- **实时验证**: 数据写入时进行格式和范围检查
- **异常检测**: 基于统计学的异常值自动识别
- **数据修复**: 自动修复常见的数据质量问题

## 📋 四、系统架构概览

### 核心模块组织

```
MyStocks 系统架构
├── core.py                    # 数据分类与路由策略
├── data_access.py             # 统一数据访问层
├── monitoring.py              # 独立监控与告警系统
├── unified_manager.py         # 统一管理器与自动化
├── system_demo.py             # 完整功能演示
├── table_config.yaml          # 配置驱动表管理
├── adapters/                  # 数据源适配器
│   ├── financial_adapter.py   # 财务数据适配器
│   ├── akshare_adapter.py     # Akshare数据源
│   └── tushare_adapter.py     # Tushare数据源
└── db_manager/                # 数据库管理基础
    ├── database_manager.py    # 数据库连接管理
    └── init_db_monitor.py     # 监控数据库初始化
```

### 技术特性

- **🎯 配置驱动**: YAML配置文件管理所有表结构，避免手工干预
- **⚡ 高性能**: TDengine时序数据库实现极致写入性能
- **🔍 智能监控**: 独立监控数据库，完整记录所有操作
- **🛡️ 数据安全**: 完善的权限管理和数据验证机制
- **🔄 自动维护**: 定时任务和自动化运维，减少人工成本

## 🚀 快速开始

### 1. 环境准备

#### 数据库服务（Week 3简化后 - 双数据库架构）
确保以下数据库服务正常运行：

**必需数据库**:
- **TDengine 3.3.x** (高频时序数据专用)
  - 用途: Tick数据、分钟K线、实时深度
  - 端口: 6030 (WebSocket), 6041 (REST API)
  - 数据库: `market_data`

- **PostgreSQL 17.x** (通用数据仓库)
  - TimescaleDB 2.x 扩展：日线K线时序优化
  - 标准表：参考数据、衍生数据、交易数据、元数据
  - 端口: 5432 (默认) 或 5438
  - 数据库: `mystocks`

#### Python环境
```bash
# 基础依赖
pip install pandas numpy pyyaml

# 数据库驱动（Week 3简化后 - 双数据库）
pip install psycopg2-binary taospy

# 数据源适配器
pip install akshare efinance schedule loguru

# 可选：性能优化
pip install ujson numba cachetools
```

#### 环境配置（Week 3简化版 - 双数据库）
创建 `.env` 文件：
```bash
# TDengine高频时序数据库（必需）
TDENGINE_HOST=192.168.123.104
TDENGINE_PORT=6030
TDENGINE_USER=root
TDENGINE_PASSWORD=taosdata
TDENGINE_DATABASE=market_data

# PostgreSQL主数据库（必需）
POSTGRESQL_HOST=192.168.123.104
POSTGRESQL_PORT=5438
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your_password
POSTGRESQL_DATABASE=mystocks

# 监控数据库（使用PostgreSQL同库独立schema）
MONITOR_DB_URL=postgresql://postgres:password@192.168.123.104:5438/mystocks

# 应用层缓存配置
CACHE_EXPIRE_SECONDS=300
LRU_CACHE_MAXSIZE=1000
```

### 2. 系统初始化

```python
from unified_manager import MyStocksUnifiedManager

# 创建统一管理器
manager = MyStocksUnifiedManager()

# 自动初始化系统（创建表结构、配置监控）
results = manager.initialize_system()

if results['config_loaded']:
    print("✅ 系统初始化成功!")
    print(f"📊 创建表数量: {len(results['tables_created'])}")
else:
    print("❌ 系统初始化失败，请检查配置")
```

### 3. 数据操作示例

```python
import pandas as pd
from datetime import datetime
from core import DataClassification

# 1. 保存股票基本信息 (自动路由到PostgreSQL)
symbols_data = pd.DataFrame({
    'symbol': ['600000', '000001', '000002'],
    'name': ['浦发银行', '平安银行', '万科A'],
    'exchange': ['SH', 'SZ', 'SZ'],
    'sector': ['银行', '银行', '房地产']
})
manager.save_data_by_classification(symbols_data, DataClassification.SYMBOLS_INFO)

# 2. 保存高频Tick数据 (自动路由到TDengine)
tick_data = pd.DataFrame({
    'ts': [datetime.now()],
    'symbol': ['600000'],
    'price': [10.50],
    'volume': [1000],
    'amount': [10500.0]
})
manager.save_data_by_classification(tick_data, DataClassification.TICK_DATA)

# 3. 保存日线数据 (自动路由到PostgreSQL)
daily_data = pd.DataFrame({
    'symbol': ['600000'],
    'trade_date': [datetime.now().date()],
    'open': [10.45],
    'high': [10.55],
    'low': [10.40],
    'close': [10.50],
    'volume': [1000000]
})
manager.save_data_by_classification(daily_data, DataClassification.DAILY_KLINE)

# 4. 智能查询数据
# 查询股票信息
symbols = manager.load_data_by_classification(
    DataClassification.SYMBOLS_INFO,
    filters={'exchange': 'SH'}
)

# 查询历史数据
history = manager.load_data_by_classification(
    DataClassification.DAILY_KLINE,
    filters={'symbol': '600000', 'trade_date': '>2024-01-01'},
    order_by='trade_date DESC',
    limit=100
)

print(f"查询到 {len(symbols)} 只上海股票")
print(f"查询到 {len(history)} 条历史数据")
```

### 4. 实时数据获取和保存

#### 使用efinance获取沪深A股实时行情

```python
# 使用改进的customer_adapter和自动路由保存
from adapters.customer_adapter import CustomerDataSource
from unified_manager import MyStocksUnifiedManager
from core import DataClassification

# 1. 创建数据适配器（启用列名标准化）
adapter = CustomerDataSource(use_column_mapping=True)

# 2. 获取沪深市场A股最新状况
realtime_data = adapter.get_market_realtime_quotes()
print(f"获取到 {len(realtime_data)} 只股票的实时行情")

# 3. 使用统一管理器和自动路由保存数据
manager = MyStocksUnifiedManager()
success = manager.save_data_by_classification(
    data=realtime_data,
    classification=DataClassification.DAILY_KLINE,  # 自动路由到PostgreSQL
    table_name='realtime_market_quotes'
)

if success:
    print("✅ 实时行情数据已保存到PostgreSQL数据库")
```

#### 命令行方式运行

```bash
# 测试数据获取
python run_realtime_market_saver.py --test-adapter

# 单次运行保存数据
python run_realtime_market_saver.py

# 持续运行（每5分钟获取一次）
python run_realtime_market_saver.py --count -1 --interval 300
```

### 5. 监控系统使用

```python
# 获取系统状态
status = manager.get_system_status()
print(f"总操作数: {status['monitoring']['operation_statistics']['total_operations']}")
print(f"成功率: {status['performance']['summary']['success_rate']:.2%}")

# 生成数据质量报告
quality_report = manager.quality_monitor.generate_quality_report()
print(f"数据质量评分: {quality_report['overall_score']:.2f}")
```

## 📁 文件功能说明

### 核心文件
- `core.py` - 数据分类枚举、路由策略、配置驱动表管理
- `unified_manager.py` - 统一管理器、系统入口、自动化维护
- `data_access.py` - 各数据库专用访问器、统一数据接口
- `monitoring.py` - 完整监控系统、告警机制、数据质量检查
- `system_demo.py` - 系统功能全面演示和使用指南
- `run_realtime_market_saver.py` - 沪深A股实时数据保存系统（efinance版）

### 数据源适配器模块（7个核心适配器）

#### ⭐ v2.1核心适配器（推荐）
- `adapters/tdx_adapter.py` (1058行) - 通达信直连，无限流，多周期K线
- `adapters/byapi_adapter.py` (625行) - REST API，涨跌停股池，技术指标

#### 稳定生产适配器
- `adapters/financial_adapter.py` (1078行) - 双数据源（efinance+easyquotation），财务数据全能
- `adapters/akshare_adapter.py` (510行) - 免费全面，历史数据研究首选
- `adapters/baostock_adapter.py` (257行) - 高质量历史数据，复权数据
- `adapters/customer_adapter.py` (378行) - 实时行情专用
- `adapters/tushare_adapter.py` (199行) - 专业级，需token

详细特性对比请参阅：[ADAPTER_AND_DATABASE_ARCHITECTURE_EVALUATION.md](./ADAPTER_AND_DATABASE_ARCHITECTURE_EVALUATION.md)

### 工具模块
- `utils/column_mapper.py` - 统一列名映射管理器，支持中英文列名转换

### 配置文件
- `table_config.yaml` - 完整表结构配置，支持所有5大数据分类
- `.env` - 环境变量配置，数据库连接信息

### 扩展模块
- `adapters/` - 数据源适配器，统一多种数据源接口
- `db_manager/` - 数据库管理基础设施
- `save_realtime_data.py` - 实时数据保存工具

## 🔧 高级功能

### 自动化维护
- **定时任务**: 数据质量检查、性能监控、备份操作
- **告警机制**: 多渠道告警，支持邮件、Webhook、日志
- **自动优化**: 数据库优化、索引管理、日志清理

### 监控体系
- **操作监控**: 所有数据库操作自动记录到独立监控数据库
- **性能监控**: 慢查询检测、响应时间统计、资源使用监控
- **质量监控**: 数据完整性、准确性、新鲜度实时检查

### 扩展性设计
- **插件化架构**: 易于添加新的数据源和数据库支持
- **配置驱动**: 通过YAML配置文件扩展表结构和存储策略
- **标准接口**: 统一的数据访问接口，便于系统集成

## 🌐 Web 平台使用

### 启动 Web 服务

#### 后端服务
```bash
cd web/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 前端服务
```bash
cd web/frontend
npm install
npm run dev
```

访问：
- **API 文档**: http://localhost:8000/api/docs
- **前端界面**: http://localhost:5173

### Web API 端点总览

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

## 📚 更多信息

- **项目模块清单**: [PROJECT_MODULES.md](./PROJECT_MODULES.md) - 详细的模块来源和分类
- **ValueCell Phase 1 完成报告**: [VALUECELL_PHASE1_COMPLETION.md](./VALUECELL_PHASE1_COMPLETION.md)
- **ValueCell Phase 2 完成报告**: [VALUECELL_PHASE2_COMPLETION.md](./VALUECELL_PHASE2_COMPLETION.md)
- **ValueCell Phase 3 完成报告**: [VALUECELL_PHASE3_COMPLETION.md](./VALUECELL_PHASE3_COMPLETION.md)
- **详细使用指南**: [example.md](./example.md)
- **适配器使用**: [adapters/example.md](./adapters/example.md)
- **数据库管理**: [db_manager/example.md](./db_manager/example.md)

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 📄 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。