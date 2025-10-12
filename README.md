# MyStocks 量化交易数据管理系统

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](./CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

MyStocks 是一个专业的量化交易数据管理系统，采用科学的数据分类体系和智能路由策略，实现多数据库协同工作。系统基于适配器模式和工厂模式构建统一的数据访问层，提供配置驱动的自动化管理，确保数据的高效存储、快速查询和实时监控。

## 🎯 核心特点

### 📊 科学的数据分类与存储策略
基于数据特性和访问模式的5大分类体系，每类数据匹配最优的存储方案：
- **时序数据** → TDengine高性能时序数据库
- **分析数据** → PostgreSQL+TimescaleDB复杂查询
- **参考数据** → MySQL/MariaDB关系型存储
- **实时数据** → Redis内存缓存
- **监控数据** → 独立监控数据库

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
- **Tick数据** → TDengine (超高频实时处理)
- **分钟K线** → TDengine (高频时序存储)
- **日线数据** → PostgreSQL + TimescaleDB (历史分析)
- **深度数据** → TDengine (实时订单簿)

#### 第2类：参考数据 (Reference Data)
**特点**: 相对静态，关系型结构，频繁JOIN操作
- **股票信息** → MySQL (相对稳定的基础信息)
- **成分股信息** → MySQL (指数成分股)
- **交易日历** → MySQL (交易日、节假日)

#### 第3类：衍生数据 (Derived Data)
**特点**: 计算密集，时序分析，复杂查询
- **技术指标** → PostgreSQL + TimescaleDB (复杂计算结果)
- **量化因子** → PostgreSQL + TimescaleDB (因子计算)
- **模型输出** → PostgreSQL + TimescaleDB (AI/ML结果)
- **交易信号** → PostgreSQL + TimescaleDB (策略信号)

#### 第4类：交易数据 (Transaction Data)
**特点**: 冷热分离，实时性要求高
- **订单记录** → PostgreSQL (冷数据长期存储)
- **成交记录** → PostgreSQL (历史交易数据)
- **持仓记录** → PostgreSQL (持仓历史)
- **实时持仓** → Redis (热数据快速访问)
- **实时账户** → Redis (实时状态缓存)

#### 第5类：元数据 (Meta Data)
**特点**: 配置管理，系统状态，结构化存储
- **数据源状态** → MySQL (数据源管理)
- **任务调度** → MySQL (定时任务配置)
- **策略参数** → MySQL (策略配置)
- **系统配置** → MySQL (系统设置)

### 数据库分工与存储方案

| 数据库 | 专业定位 | 适用数据 | 核心优势 |
|--------|----------|----------|----------|
| **TDengine** | 高频时序数据专用库 | Tick数据、分钟K线 | 极高压缩比(20:1)、超强写入性能 |
| **PostgreSQL+TimescaleDB** | 历史数据仓库+分析引擎 | 日线数据、技术指标、因子 | 自动分区、复杂时序查询 |
| **MySQL/MariaDB** | 参考数据与元数据中心 | 股票信息、系统配置 | 事务完整性、关系查询 |
| **Redis** | 实时状态与缓存中心 | 实时持仓、热点数据 | 毫秒级访问、内存存储 |

## 🔧 二、数据调用与操作方法

### 统一接口规范
所有数据操作都通过统一的接口进行，隐藏底层数据库差异：

```python
from unified_manager import MyStocksUnifiedManager
from core import DataClassification

# 创建统一管理器
manager = MyStocksUnifiedManager()

# 自动路由保存 - 系统自动选择最优数据库
manager.save_data_by_classification(data, DataClassification.TICK_DATA)     # → TDengine
manager.save_data_by_classification(data, DataClassification.SYMBOLS_INFO)  # → MySQL
manager.save_data_by_classification(data, DataClassification.DAILY_KLINE)   # → PostgreSQL

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

### 数据流工作流程

```mermaid
graph TD
    A[数据源] --> B[适配器层]
    B --> C[统一管理器]
    C --> D{数据分类识别}
    D -->|市场数据| E[TDengine]
    D -->|参考数据| F[MySQL]
    D -->|衍生数据| G[PostgreSQL]
    D -->|交易数据| H[Redis/PostgreSQL]
    D -->|元数据| I[MySQL]
    J[监控系统] --> K[独立监控数据库]
    C --> J
```

### 数据缓存方法

#### 多层缓存架构
1. **L1缓存**: Redis内存缓存 (毫秒级访问)
2. **L2缓存**: 应用层缓存 (微秒级访问)
3. **L3缓存**: 数据库查询缓存 (秒级访问)

#### 智能缓存策略
- **热点数据预加载**: 自动识别并预加载热点数据
- **LRU自动淘汰**: 最近最少使用数据自动清理
- **分级缓存更新**: 根据数据重要性设置不同的更新频率

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
    # 数据分类到数据库的智能映射
    CLASSIFICATION_TO_DATABASE = {
        DataClassification.TICK_DATA: DatabaseTarget.TDENGINE,
        DataClassification.DAILY_KLINE: DatabaseTarget.POSTGRESQL,
        DataClassification.SYMBOLS_INFO: DatabaseTarget.MYSQL,
        DataClassification.REALTIME_POSITIONS: DatabaseTarget.REDIS,
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

#### 数据库服务
确保以下数据库服务正常运行：
- **MySQL/MariaDB**: 参考数据和元数据存储
- **PostgreSQL**: 分析数据和历史数据仓库  
- **TDengine**: 高频时序数据专用库
- **Redis**: 实时状态缓存

#### Python环境
```bash
# 基础依赖
pip install pandas numpy pyyaml

# 数据库驱动
pip install pymysql psycopg2-binary redis taospy

# 数据源适配器
pip install efinance schedule loguru

# 可选：性能优化
pip install ujson numba
```

#### 环境配置
创建 `.env` 文件：
```bash
# MySQL配置
MYSQL_HOST=192.168.123.104
MYSQL_PORT=3306
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=quant_research

# PostgreSQL配置
POSTGRESQL_HOST=192.168.123.104
POSTGRESQL_PORT=5438
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your_password
POSTGRESQL_DATABASE=mystocks

# TDengine配置
TDENGINE_HOST=192.168.123.104
TDENGINE_PORT=6030
TDENGINE_USER=root
TDENGINE_PASSWORD=taosdata
TDENGINE_DATABASE=market_data

# Redis配置
REDIS_HOST=192.168.123.104
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# 监控数据库
MONITOR_DB_URL=mysql+pymysql://user:password@host:port/db_monitor
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

# 1. 保存股票基本信息 (自动路由到MySQL)
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

### 适配器模块
- `adapters/customer_adapter.py` - 自定义数据源适配器，efinance+easyquotation双库管理
- `adapters/financial_adapter.py` - 综合财务数据适配器
- `adapters/akshare_adapter.py` - Akshare数据源适配器

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

## 📚 更多信息

- **详细使用指南**: [example.md](./example.md)
- **适配器使用**: [adapters/example.md](./adapters/example.md)
- **数据库管理**: [db_manager/example.md](./db_manager/example.md)

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 📄 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。