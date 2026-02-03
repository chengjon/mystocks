# MyStocks 数据自动路由与更新机制详解

**Note**: MySQL has been removed; use PostgreSQL. This legacy guide is kept for reference.

## 概述

MyStocks系统实现了一套科学的5层数据分类框架，配合智能自动路由机制，将不同类型的数据自动保存到最适合的数据库中，实现性能优化和管理简化。

## 1. 数据分类与存储策略

### 核心设计理念

```python
# 来自 core.py
class DataClassification(Enum):
    MARKET_DATA = "market_data"           # 市场数据 → TDengine
    REFERENCE_DATA = "reference_data"     # 参考数据 → PostgreSQL
    DERIVED_DATA = "derived_data"         # 衍生数据 → PostgreSQL+TimescaleDB
    TRANSACTION_DATA = "transaction_data" # 交易数据 → Redis(热) + PostgreSQL(冷)
    META_DATA = "meta_data"              # 元数据 → PostgreSQL

    # 具体业务分类
    TICK_DATA = "tick_data"              # Tick数据 → TDengine
    DAILY_KLINE = "daily_kline"          # 日K线数据 → PostgreSQL+TimescaleDB
    REALTIME_POSITIONS = "realtime_positions"  # 实时持仓 → Redis
    SYMBOLS_INFO = "symbols_info"        # 股票信息 → PostgreSQL
    TECHNICAL_INDICATORS = "technical_indicators"  # 技术指标 → PostgreSQL
```

### 自动路由策略

```python
# 来自 core.py 的 DataStorageStrategy.get_target_database()
routing_rules = {
    DataClassification.TICK_DATA: DatabaseTarget.TDENGINE,
    DataClassification.DAILY_KLINE: DatabaseTarget.POSTGRESQL,
    DataClassification.REALTIME_POSITIONS: DatabaseTarget.REDIS,
    DataClassification.SYMBOLS_INFO: DatabaseTarget.POSTGRESQL,
    DataClassification.TECHNICAL_INDICATORS: DatabaseTarget.POSTGRESQL,
}
```

## 2. efinance 实时数据的自动路由过程

### 数据获取流程

```python
# save_realtime_market_data.py 中的实现
def get_realtime_market_data(self):
    """使用efinance获取沪深市场A股实时数据"""
    # 1. 直接调用 efinance API
    data = self.customer_ds.ef.stock.get_realtime_quotes()

    # 2. 数据验证和格式化
    if self.config['add_timestamp_column']:
        data['data_update_time'] = datetime.now()
        data['trade_date'] = datetime.now().date()

    return data
```

### 双重保存策略

实时股票数据采用**双重保存**策略，确保数据的实时性和持久性：

#### 策略1: 实时数据 → Redis (热数据)
```python
# 分类: REALTIME_POSITIONS
self.unified_manager.save_data_by_classification(
    data,
    DataClassification.REALTIME_POSITIONS
)
# 自动路由到: Redis
# 目的: 快速访问、实时查询、缓存
```

#### 策略2: 日线数据 → PostgreSQL+TimescaleDB (持久化)
```python
# 分类: DAILY_KLINE
daily_data = self._prepare_daily_data(data)
self.unified_manager.save_data_by_classification(
    daily_data,
    DataClassification.DAILY_KLINE
)
# 自动路由到: PostgreSQL+TimescaleDB
# 目的: 持久化存储、复杂分析、历史查询
```

#### 策略3: Tick数据 → TDengine (可选)
```python
# 分类: TICK_DATA (可选启用)
tick_data = self._prepare_tick_data(data)
self.unified_manager.save_data_by_classification(
    tick_data,
    DataClassification.TICK_DATA
)
# 自动路由到: TDengine
# 目的: 高频时序存储、历史回测
```

## 3. 自动路由实现机制

### 统一管理器 (MyStocksUnifiedManager)

```python
# unified_manager.py 中的核心方法
def save_data_by_classification(self, data, classification: DataClassification) -> bool:
    """按数据分类自动路由保存"""

    # 1. 根据分类确定目标数据库
    target_db = DataStorageStrategy.get_target_database(classification)

    # 2. 获取对应的数据访问层
    if target_db == DatabaseTarget.REDIS:
        accessor = self.redis_access
    elif target_db == DatabaseTarget.POSTGRESQL:
        accessor = self.postgresql_access
    elif target_db == DatabaseTarget.TDENGINE:
        accessor = self.tdengine_access

    # 3. 执行保存操作
    success = accessor.save_data(data, table_name, **params)

    # 4. 记录监控信息
    self.monitoring_db.log_operation_result(operation_id, success)

    return success
```

### 数据库专业化

每个数据库都针对特定的数据特征进行了优化：

#### TDengine (时序数据专家)
- **专长**: 高频Tick数据、分钟级K线
- **优势**: 20:1压缩比、极高写入性能
- **配置**: 时序表、超级表、标签系统

#### PostgreSQL+TimescaleDB (分析数据专家)
- **专长**: 日K线、技术指标、衍生数据
- **优势**: 复杂查询、自动分区、SQL兼容
- **配置**: 超表、时间分区、索引优化

#### Redis (实时数据专家)
- **专长**: 实时行情、持仓状态、热点数据
- **优势**: 毫秒级访问、内存存储
- **配置**: 过期策略、持久化、集群

#### PostgreSQL (参考/元数据)
- **专长**: 股票信息、配置数据、元数据
- **优势**: ACID事务、复杂关联
- **配置**: 索引优化、外键约束

## 4. 数据更新机制

### 增量更新策略

```python
# 实时数据更新
def update_realtime_data():
    """实时数据增量更新"""
    # Redis: 直接覆盖更新（基于key）
    # 自动过期机制(CACHE_EXPIRE_SECONDS)

# 历史数据更新
def update_historical_data():
    """历史数据智能更新"""
    # PostgreSQL: 基于 (symbol, trade_date) 唯一键
    # ON CONFLICT UPDATE 或 UPSERT 策略

# 时序数据追加
def append_timeseries_data():
    """时序数据追加更新"""
    # TDengine: 基于时间戳追加
    # 自动去重和排序
```

### 并发控制

```python
# 监控数据库记录所有操作
operation_id = monitoring_db.log_operation_start(
    table_name, database_type, database_name, operation_type
)

try:
    # 执行数据操作
    result = perform_database_operation()
    monitoring_db.log_operation_result(operation_id, True, data_count)
except Exception as e:
    monitoring_db.log_operation_result(operation_id, False, 0, str(e))
```

## 5. 配置驱动的灵活性

### 环境变量配置
```bash
# .env 文件控制数据库连接
POSTGRESQL_HOST=192.168.123.104
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=c790414J
POSTGRESQL_PORT=5438
POSTGRESQL_DATABASE=mystocks

# 配置文件控制保存策略
SAVE_AS_REALTIME=true      # 是否保存到Redis
SAVE_AS_DAILY=true         # 是否保存到PostgreSQL
SAVE_AS_TICK=false         # 是否保存到TDengine
```

### YAML表结构配置
```yaml
# table_config.yaml 定义所有表结构
tables:
  - database_type: PostgreSQL
    database_name: mystocks
    table_name: daily_kline
    columns:
      - name: symbol
        type: VARCHAR
        length: 20
      - name: trade_date
        type: DATE
```

## 6. 监控和运维

### 完整监控体系
- **操作监控**: 每个数据库操作都被记录
- **性能监控**: 慢查询检测和告警
- **质量监控**: 数据完整性、新鲜度检查
- **健康监控**: 数据库连接状态、资源使用

### 自动化运维
- **表结构管理**: 配置驱动的自动建表
- **数据验证**: 自动检查数据质量
- **异常处理**: 自动重试和故障转移
- **清理策略**: 自动过期和归档

## 总结

MyStocks的数据自动路由机制通过以下特性实现了高效的数据管理：

1. **智能分类**: 根据数据特征自动选择最优存储
2. **配置驱动**: 灵活的配置系统支持各种需求
3. **监控完备**: 全面的监控确保系统健康
4. **性能优化**: 每个数据库发挥最大优势
5. **运维简化**: 自动化减少人工干预

这套机制使得开发者只需要关注业务逻辑，而数据存储的复杂性被完全抽象化，实现了"写一次，智能路由"的理想状态。
