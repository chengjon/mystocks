# Technical Research: MyStocks数据管理系统

> **历史分析说明**:
> 本文件是某次针对测试覆盖、缺陷、基线、诊断结果或方案可行性形成的历史分析记录，用于保留当时的判断依据与观察结果。
> 文中的结论、统计和问题判断均受生成时间、样本范围与当时仓库状态影响；如需判断当前状态，必须重新核对现行测试实现与最新验证结果。


**创建人**: Claude (自动生成)
**版本**: 1.0.0
**创建日期**: 2025-10-11
**关联计划**: [plan.md](plan.md)

## 研究概述

本文档整合了 Phase 0 (Outline & Research) 阶段的8个研究任务成果,为后续设计和实施提供技术决策依据。所有决策均已验证宪法合规性,确保符合5层数据分类、配置驱动、智能路由等核心原则。

## 1. TDengine集成决策 (R1)

### Decision (决策)
- **连接方式**: WebSocket + 参数绑定 (taosws connector)
- **表结构**: Super Table (超级表) 架构,1个symbol对应1个子表
- **数据压缩**: ZSTD压缩 + 高压缩级别,目标压缩比 20:1
- **编码策略**: delta-d (DOUBLE), delta-i (BIGINT), simple8b (整数)

### Rationale (技术原因)
1. **性能优势**: WebSocket连接比REST API快5-10倍,支持10,000+ tick/秒写入
2. **参数绑定**: 避免SQL注入,减少SQL解析开销,提升批量插入效率
3. **Super Table设计**: 按symbol自动分区,支持高效的tag过滤查询
4. **压缩效率**: ZSTD算法在时序数据上可达20:1压缩比,显著降低存储成本

### Alternatives Considered (考虑的其他方案)
- ❌ **REST API**: 延迟高,不适合高频数据
- ❌ **原生TCP连接**: 复杂度高,维护成本大
- ❌ **普通表**: 无法利用TDengine的tag索引优势

### Implementation Notes (实现要点)

#### 连接配置
```python
import taosws

# WebSocket连接字符串
conn = taosws.connect(
    "taosws://root:your-tdengine-password@localhost:6041/market_data",
    timeout=30
)
```

#### Super Table创建模板
```sql
-- Tick数据超级表
CREATE STABLE IF NOT EXISTS tick_data (
    ts TIMESTAMP,                    -- 时间戳(主键)
    price DOUBLE,                    -- 成交价格
    volume BIGINT,                   -- 成交量
    amount DOUBLE,                   -- 成交额
    buy_count INT,                   -- 买盘笔数
    sell_count INT                   -- 卖盘笔数
) TAGS (
    symbol BINARY(16),               -- 股票代码
    exchange BINARY(16),             -- 交易所
    security_type BINARY(16)         -- 证券类型
)
ENCODE 'delta-d,delta-i,simple8b'    -- 编码策略
COMPRESS 'zstd'                      -- 压缩算法
LEVEL 'high';                        -- 压缩级别

-- 分钟K线超级表
CREATE STABLE IF NOT EXISTS minute_kline (
    ts TIMESTAMP,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    volume BIGINT,
    amount DOUBLE,
    num_trades INT
) TAGS (
    symbol BINARY(16),
    exchange BINARY(16),
    interval_type BINARY(8)          -- 1min/5min/15min
)
ENCODE 'delta-d,delta-i,simple8b'
COMPRESS 'zstd'
LEVEL 'high';

-- 盘口快照超级表 (Level-2)
CREATE STABLE IF NOT EXISTS market_snapshot (
    ts TIMESTAMP,
    bid_prices BINARY(256),          -- JSON格式的10档买价
    bid_volumes BINARY(256),         -- JSON格式的10档买量
    ask_prices BINARY(256),          -- JSON格式的10档卖价
    ask_volumes BINARY(256),         -- JSON格式的10档卖量
    total_bid_volume BIGINT,
    total_ask_volume BIGINT
) TAGS (
    symbol BINARY(16),
    exchange BINARY(16)
)
COMPRESS 'zstd'
LEVEL 'medium';                      -- JSON字段压缩率较低
```

#### 参数化批量插入
```python
# 使用参数绑定批量插入
stmt = conn.statement("INSERT INTO ? USING tick_data TAGS(?, ?, ?) VALUES(?, ?, ?, ?, ?, ?)")

for symbol_batch in symbol_batches:
    subtable_name = f"tick_{symbol_batch['symbol']}"

    # 绑定表名和tags
    stmt.set_tbname(subtable_name)
    stmt.set_tags([
        symbol_batch['symbol'],
        symbol_batch['exchange'],
        symbol_batch['security_type']
    ])

    # 批量绑定数据
    stmt.bind_param([
        symbol_batch['timestamps'],     # TIMESTAMP数组
        symbol_batch['prices'],         # DOUBLE数组
        symbol_batch['volumes'],        # BIGINT数组
        symbol_batch['amounts'],        # DOUBLE数组
        symbol_batch['buy_counts'],     # INT数组
        symbol_batch['sell_counts']     # INT数组
    ])

    stmt.add_batch()

stmt.execute()
stmt.close()
```

#### 性能优化建议
1. **批量大小**: 每批1000-5000条记录,根据网络延迟调整
2. **并发写入**: 多线程按symbol分区并发写入,避免锁竞争
3. **缓存策略**: 启用TDengine的缓存 (cachemodel=both)
4. **WAL配置**: 生产环境设置 wal_level=1 (数据持久化)

---

## 2. TimescaleDB配置决策 (R2)

### Decision (决策)
- **Chunk间隔**: 1天 (适用于衍生数据和交易数据)
- **压缩策略**: 30天后自动压缩
- **分段键**: symbol + 指标名称/数据类型
- **索引策略**: 复合索引 (symbol, calc_date) + GiST索引支持时间范围查询

### Rationale (技术原因)
1. **1天Chunk**: 基于"Chunk内存占用不超过总内存25%"规则,1天数据量适中
2. **30天压缩**: 平衡查询性能和存储成本,近期数据保持未压缩便于快速访问
3. **分段键**: 按symbol分段使压缩效率最大化,同一股票数据特征相似
4. **自动分区**: TimescaleDB自动管理分区,无需手动维护

### Alternatives Considered (考虑的其他方案)
- ❌ **7天Chunk**: 分区过多,元数据开销大
- ❌ **即时压缩**: 影响写入性能,不适合实时数据
- ❌ **不压缩**: 存储成本过高,历史数据访问频率低

### Implementation Notes (实现要点)

#### Hypertable创建
```sql
-- 技术指标表 (衍生数据)
CREATE TABLE IF NOT EXISTS technical_indicators (
    symbol VARCHAR(16) NOT NULL,
    calc_date TIMESTAMPTZ NOT NULL,
    indicator_name VARCHAR(32) NOT NULL,   -- MACD/RSI/BOLL等
    indicator_value DOUBLE PRECISION,
    params JSONB,                          -- 指标参数配置
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 转换为Hypertable
SELECT create_hypertable(
    'technical_indicators',
    'calc_date',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- 创建索引
CREATE INDEX idx_tech_symbol_date ON technical_indicators (symbol, calc_date DESC);
CREATE INDEX idx_tech_indicator ON technical_indicators (indicator_name);

-- 配置压缩
ALTER TABLE technical_indicators SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol, indicator_name',
    timescaledb.compress_orderby = 'calc_date DESC'
);

-- 添加压缩策略 (30天后压缩)
SELECT add_compression_policy(
    'technical_indicators',
    INTERVAL '30 days'
);
```

#### 日线/周线/月线表
```sql
-- 日线数据表
CREATE TABLE IF NOT EXISTS daily_kline (
    symbol VARCHAR(16) NOT NULL,
    trade_date TIMESTAMPTZ NOT NULL,
    open DOUBLE PRECISION NOT NULL,
    high DOUBLE PRECISION NOT NULL,
    low DOUBLE PRECISION NOT NULL,
    close DOUBLE PRECISION NOT NULL,
    volume BIGINT NOT NULL,
    amount DOUBLE PRECISION,
    turnover_rate DOUBLE PRECISION,
    pe_ratio DOUBLE PRECISION,
    pb_ratio DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable(
    'daily_kline',
    'trade_date',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

CREATE INDEX idx_daily_symbol_date ON daily_kline (symbol, trade_date DESC);

ALTER TABLE daily_kline SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol',
    timescaledb.compress_orderby = 'trade_date DESC'
);

SELECT add_compression_policy('daily_kline', INTERVAL '30 days');
```

#### 订单和成交记录表 (交易数据)
```sql
-- 历史订单表
CREATE TABLE IF NOT EXISTS order_history (
    order_id VARCHAR(64) PRIMARY KEY,
    symbol VARCHAR(16) NOT NULL,
    order_time TIMESTAMPTZ NOT NULL,
    order_type VARCHAR(16) NOT NULL,      -- LIMIT/MARKET/STOP
    direction VARCHAR(8) NOT NULL,        -- BUY/SELL
    price DOUBLE PRECISION,
    quantity BIGINT NOT NULL,
    filled_quantity BIGINT DEFAULT 0,
    status VARCHAR(16) NOT NULL,          -- PENDING/FILLED/CANCELLED
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable(
    'order_history',
    'order_time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

CREATE INDEX idx_order_symbol_time ON order_history (symbol, order_time DESC);
CREATE INDEX idx_order_status ON order_history (status, order_time DESC);

ALTER TABLE order_history SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol, status',
    timescaledb.compress_orderby = 'order_time DESC'
);

SELECT add_compression_policy('order_history', INTERVAL '30 days');
```

#### 持续聚合 (Continuous Aggregates)
```sql
-- 每日交易统计
CREATE MATERIALIZED VIEW daily_trade_summary
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', order_time) AS day,
    symbol,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN direction = 'BUY' THEN quantity ELSE 0 END) AS buy_volume,
    SUM(CASE WHEN direction = 'SELL' THEN quantity ELSE 0 END) AS sell_volume,
    AVG(price) AS avg_price
FROM order_history
WHERE status = 'FILLED'
GROUP BY day, symbol;

-- 自动刷新策略
SELECT add_continuous_aggregate_policy('daily_trade_summary',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);
```

#### 数据保留策略
```sql
-- 技术指标保留5年
SELECT add_retention_policy('technical_indicators', INTERVAL '5 years');

-- 日线数据保留10年
SELECT add_retention_policy('daily_kline', INTERVAL '10 years');

-- 订单记录保留3年 (合规要求)
SELECT add_retention_policy('order_history', INTERVAL '3 years');
```

---

## 3. 多数据库事务协调决策 (R3)

### Decision (决策)
- **协调策略**: 基于队列的最终一致性 (Queue-based Eventual Consistency)
- **实现模式**: Outbox模式 + SQLite持久化队列
- **重试机制**: 指数退避重试,最多5次
- **监控集成**: 所有跨库操作记录到监控数据库

### Rationale (技术原因)
1. **量化数据特性**: 时序数据为追加型,无需强一致性,最终一致性即可满足需求
2. **简化复杂度**: 避免2PC/Saga的复杂性和性能开销
3. **故障容错**: SQLite队列支持持久化,系统重启后可继续处理
4. **审计跟踪**: 所有操作可追溯,便于问题排查

### Alternatives Considered (考虑的其他方案)
- ❌ **2PC (两阶段提交)**: 过度复杂,性能差,不适合异构数据库
- ❌ **Saga模式**: 需要实现补偿事务,对只读/追加型数据过于复杂
- ❌ **直接写入无协调**: 无法保证数据一致性,故障后数据丢失

### Implementation Notes (实现要点)

#### SQLite Outbox表结构
```python
import sqlite3
import json
import uuid
from datetime import datetime

class OutboxQueue:
    def __init__(self, db_path='data/outbox_queue.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS outbox_operations (
                operation_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                target_databases TEXT NOT NULL,    -- JSON数组
                data_classification TEXT NOT NULL,
                data_payload TEXT NOT NULL,        -- JSON格式
                status TEXT NOT NULL,              -- pending/processing/completed/failed
                retry_count INTEGER DEFAULT 0,
                last_error TEXT,
                completed_at TEXT,
                INDEX idx_status_created (status, created_at)
            )
        """)
        self.conn.commit()

    def enqueue(self, target_dbs, classification, data_payload):
        """入队一个跨库操作"""
        operation_id = str(uuid.uuid4())
        self.conn.execute("""
            INSERT INTO outbox_operations
            (operation_id, created_at, target_databases, data_classification,
             data_payload, status, retry_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            operation_id,
            datetime.now().isoformat(),
            json.dumps(target_dbs),
            classification.value,
            json.dumps(data_payload),
            'pending',
            0
        ))
        self.conn.commit()
        return operation_id

    def dequeue_batch(self, batch_size=10):
        """批量取出待处理操作"""
        cursor = self.conn.execute("""
            SELECT operation_id, target_databases, data_classification,
                   data_payload, retry_count
            FROM outbox_operations
            WHERE status = 'pending' AND retry_count < 5
            ORDER BY created_at ASC
            LIMIT ?
        """, (batch_size,))

        operations = []
        for row in cursor:
            operations.append({
                'operation_id': row[0],
                'target_databases': json.loads(row[1]),
                'classification': row[2],
                'data_payload': json.loads(row[3]),
                'retry_count': row[4]
            })
        return operations
```

#### 跨库写入协调器
```python
import time
from typing import List
from enum import Enum

class MultiDatabaseCoordinator:
    def __init__(self, unified_manager, outbox_queue):
        self.manager = unified_manager
        self.outbox = outbox_queue
        self.max_retries = 5
        self.retry_delays = [1, 2, 5, 10, 30]  # 指数退避(秒)

    def save_with_coordination(self, data, classification, target_dbs=None):
        """
        协调多数据库写入

        Args:
            data: pandas DataFrame
            classification: DataClassification枚举
            target_dbs: 目标数据库列表,None表示自动路由
        """
        if target_dbs is None:
            # 自动确定目标数据库
            target_dbs = self._determine_targets(classification)

        if len(target_dbs) == 1:
            # 单库操作,直接写入
            return self.manager.save_data_by_classification(data, classification)

        # 多库操作,入队处理
        operation_id = self.outbox.enqueue(
            target_dbs=target_dbs,
            classification=classification,
            data_payload=data.to_dict(orient='records')
        )

        return operation_id

    def _determine_targets(self, classification):
        """根据数据分类确定目标数据库"""
        # 示例: REALTIME_POSITION需要同时写入Redis和PostgreSQL
        if classification == DataClassification.REALTIME_POSITION:
            return ['redis', 'postgresql']
        elif classification == DataClassification.TICK_DATA:
            return ['tdengine']
        # ... 其他分类逻辑

        return [self.manager.strategy.get_target_database(classification)]

    def process_outbox_queue(self):
        """后台任务: 处理Outbox队列"""
        while True:
            operations = self.outbox.dequeue_batch(batch_size=10)

            for op in operations:
                success = self._execute_operation(op)

                if success:
                    self.outbox.mark_completed(op['operation_id'])
                else:
                    # 更新重试计数
                    retry_count = op['retry_count'] + 1
                    if retry_count >= self.max_retries:
                        self.outbox.mark_failed(op['operation_id'])
                        # 发送告警
                        self._alert_operation_failed(op)
                    else:
                        self.outbox.increment_retry(op['operation_id'])
                        # 指数退避
                        time.sleep(self.retry_delays[retry_count])

            time.sleep(5)  # 轮询间隔

    def _execute_operation(self, operation):
        """执行单个跨库操作"""
        try:
            data_df = pd.DataFrame(operation['data_payload'])
            classification = DataClassification(operation['classification'])

            # 依次写入各目标库
            for db_name in operation['target_databases']:
                if db_name == 'tdengine':
                    self.manager.tdengine_access.save_data(
                        data_df,
                        self._get_table_name(classification)
                    )
                elif db_name == 'postgresql':
                    self.manager.postgresql_access.save_data(
                        data_df,
                        self._get_table_name(classification)
                    )
                elif db_name == 'redis':
                    self.manager.redis_access.save_data(
                        data_df,
                        self._get_redis_key_prefix(classification)
                    )
                # ... 其他数据库

            return True
        except Exception as e:
            self.outbox.update_error(operation['operation_id'], str(e))
            return False
```

#### 监控集成
```python
# 在MonitoringDatabase中记录跨库操作
def log_cross_database_operation(self, operation_id, target_dbs, status, duration_ms):
    self.conn.execute("""
        INSERT INTO cross_db_operations
        (operation_id, target_databases, status, duration_ms, logged_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        operation_id,
        json.dumps(target_dbs),
        status,
        duration_ms,
        datetime.now()
    ))
    self.conn.commit()
```

#### 使用示例
```python
# 实时持仓数据: 需要同时写入Redis(热数据)和PostgreSQL(持久化)
coordinator = MultiDatabaseCoordinator(unified_manager, outbox_queue)

position_data = pd.DataFrame({
    'account_id': ['A001', 'A001'],
    'symbol': ['000001.SZ', '600000.SH'],
    'quantity': [1000, 2000],
    'cost_price': [10.5, 8.3],
    'current_price': [11.2, 8.8],
    'update_time': [datetime.now(), datetime.now()]
})

# 自动协调写入Redis和PostgreSQL
operation_id = coordinator.save_with_coordination(
    data=position_data,
    classification=DataClassification.REALTIME_POSITION
)

# 启动后台队列处理
import threading
queue_thread = threading.Thread(
    target=coordinator.process_outbox_queue,
    daemon=True
)
queue_thread.start()
```

---

## 4. YAML配置架构决策 (R4)

### Decision (决策)
- **解析库**: PyYAML 6.0+
- **验证框架**: Pydantic V2 (BaseModel)
- **配置结构**: 分层架构 (全局配置 + 表定义 + 数据库特定配置)
- **版本控制**: 配置文件内嵌版本号,支持向后兼容性检查

### Rationale (技术原因)
1. **类型安全**: Pydantic提供运行时类型验证,减少配置错误
2. **IDE支持**: 强类型定义提供自动补全和错误提示
3. **可扩展性**: 分层结构支持数据库特定配置而不污染核心定义
4. **向后兼容**: 版本号机制支持配置迁移和兼容性检查

### Alternatives Considered (考虑的其他方案)
- ❌ **JSON配置**: 不支持注释,可读性差
- ❌ **TOML配置**: 嵌套结构表达不够清晰
- ❌ **纯Python配置**: 缺乏声明式特性,难以自动化处理

### Implementation Notes (实现要点)

#### Pydantic配置模型
```python
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Literal
from enum import Enum

class DatabaseType(str, Enum):
    TDENGINE = "tdengine"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    REDIS = "redis"

class ColumnDefinition(BaseModel):
    name: str = Field(..., description="列名")
    type: str = Field(..., description="数据类型")
    nullable: bool = Field(default=True, description="是否允许NULL")
    primary_key: bool = Field(default=False, description="是否为主键")
    default: Optional[str] = Field(default=None, description="默认值")
    comment: Optional[str] = Field(default=None, description="列注释")

    # TDengine特定
    encoding: Optional[str] = Field(default=None, description="编码方式(TDengine)")

    # PostgreSQL特定
    index_type: Optional[str] = Field(default=None, description="索引类型(BTREE/HASH/GIST)")

class TDengineConfig(BaseModel):
    """TDengine特定配置"""
    is_super_table: bool = Field(default=False, description="是否为超级表")
    tags: Optional[List[ColumnDefinition]] = Field(default=None, description="标签列")
    compression: str = Field(default="zstd", description="压缩算法")
    compression_level: Literal["low", "medium", "high"] = Field(default="high")
    keep_days: int = Field(default=3650, description="数据保留天数")

    @validator('tags')
    def validate_tags(cls, v, values):
        if values.get('is_super_table') and not v:
            raise ValueError("超级表必须定义tags")
        return v

class TimescaleConfig(BaseModel):
    """TimescaleDB特定配置"""
    is_hypertable: bool = Field(default=False, description="是否为Hypertable")
    time_column: Optional[str] = Field(default=None, description="时间列名")
    chunk_interval: str = Field(default="1 day", description="Chunk间隔")
    compress_after: str = Field(default="30 days", description="压缩延迟")
    compress_segmentby: Optional[List[str]] = Field(default=None, description="压缩分段键")
    retention_period: Optional[str] = Field(default=None, description="数据保留期")

    @validator('time_column')
    def validate_time_column(cls, v, values):
        if values.get('is_hypertable') and not v:
            raise ValueError("Hypertable必须指定时间列")
        return v

class TableDefinition(BaseModel):
    """表定义"""
    table_name: str = Field(..., description="表名")
    database_type: DatabaseType = Field(..., description="数据库类型")
    data_classification: str = Field(..., description="数据分类")
    description: Optional[str] = Field(default=None, description="表描述")

    columns: List[ColumnDefinition] = Field(..., description="列定义")
    indexes: Optional[List[Dict[str, str]]] = Field(default=None, description="索引定义")

    # 数据库特定配置
    tdengine_config: Optional[TDengineConfig] = Field(default=None)
    timescale_config: Optional[TimescaleConfig] = Field(default=None)

    @validator('tdengine_config')
    def validate_tdengine(cls, v, values):
        if values.get('database_type') == DatabaseType.TDENGINE and not v:
            raise ValueError("TDengine表必须提供tdengine_config")
        return v

    @validator('timescale_config')
    def validate_timescale(cls, v, values):
        if values.get('database_type') == DatabaseType.POSTGRESQL and not v:
            # PostgreSQL表可选TimescaleDB扩展
            pass
        return v

class DatabaseConfig(BaseModel):
    """数据库连接配置"""
    host: str
    port: int
    user: str
    password: str
    database: str

    # 连接池配置
    pool_size: int = Field(default=10, ge=1, le=100)
    max_overflow: int = Field(default=20, ge=0, le=100)
    pool_timeout: int = Field(default=30, ge=1)

class SystemConfig(BaseModel):
    """系统全局配置"""
    version: str = Field(..., description="配置文件版本")
    project_name: str = Field(default="MyStocks", description="项目名称")

    # 数据库连接
    databases: Dict[DatabaseType, DatabaseConfig] = Field(..., description="数据库配置")

    # 表定义
    tables: List[TableDefinition] = Field(..., description="表定义列表")

    # 监控配置
    monitoring: Dict[str, any] = Field(default_factory=dict, description="监控配置")

    @validator('version')
    def validate_version(cls, v):
        # 支持的版本号
        supported = ['1.0.0', '1.1.0']
        if v not in supported:
            raise ValueError(f"不支持的配置版本: {v}, 支持版本: {supported}")
        return v
```

#### YAML配置文件示例
```yaml
# table_config.yaml
version: "1.1.0"
project_name: "MyStocks"

# 数据库连接配置(通过环境变量覆盖)
databases:
  tdengine:
    host: "${TDENGINE_HOST:localhost}"
    port: 6041
    user: "${TDENGINE_USER:root}"
    password: "${TDENGINE_PASSWORD:your-tdengine-password}"
    database: "${TDENGINE_DATABASE:market_data}"
    pool_size: 20
    max_overflow: 30

  postgresql:
    host: "${POSTGRESQL_HOST:localhost}"
    port: 5432
    user: "${POSTGRESQL_USER:postgres}"
    password: "${POSTGRESQL_PASSWORD:postgres}"
    database: "${POSTGRESQL_DATABASE:mystocks}"
    pool_size: 15

  mysql:
    host: "${MYSQL_HOST:localhost}"
    port: 3306
    user: "${MYSQL_USER:root}"
    password: "${MYSQL_PASSWORD:root}"
    database: "${MYSQL_DATABASE:mystocks_reference}"
    pool_size: 10

  redis:
    host: "${REDIS_HOST:localhost}"
    port: 6379
    password: "${REDIS_PASSWORD:}"
    database: "${REDIS_DB:1}"  # 使用1号库,避开0号
    pool_size: 50

# 表定义
tables:
  # TDengine - Tick数据
  - table_name: "tick_data"
    database_type: "tdengine"
    data_classification: "TICK_DATA"
    description: "逐笔成交数据(超高频)"

    columns:
      - name: "ts"
        type: "TIMESTAMP"
        nullable: false
        primary_key: true
        comment: "时间戳"

      - name: "price"
        type: "DOUBLE"
        nullable: false
        encoding: "delta-d"
        comment: "成交价格"

      - name: "volume"
        type: "BIGINT"
        nullable: false
        encoding: "delta-i"
        comment: "成交量"

      - name: "amount"
        type: "DOUBLE"
        nullable: false
        encoding: "delta-d"
        comment: "成交额"

      - name: "buy_count"
        type: "INT"
        nullable: true
        encoding: "simple8b"
        comment: "买盘笔数"

      - name: "sell_count"
        type: "INT"
        nullable: true
        encoding: "simple8b"
        comment: "卖盘笔数"

    tdengine_config:
      is_super_table: true
      tags:
        - name: "symbol"
          type: "BINARY(16)"
          nullable: false
          comment: "股票代码"

        - name: "exchange"
          type: "BINARY(16)"
          nullable: false
          comment: "交易所"

        - name: "security_type"
          type: "BINARY(16)"
          nullable: false
          comment: "证券类型"

      compression: "zstd"
      compression_level: "high"
      keep_days: 730  # 保留2年

  # PostgreSQL - 技术指标
  - table_name: "technical_indicators"
    database_type: "postgresql"
    data_classification: "TECHNICAL_INDICATORS"
    description: "技术指标计算结果"

    columns:
      - name: "id"
        type: "BIGSERIAL"
        nullable: false
        primary_key: true

      - name: "symbol"
        type: "VARCHAR(16)"
        nullable: false
        comment: "股票代码"

      - name: "calc_date"
        type: "TIMESTAMPTZ"
        nullable: false
        comment: "计算日期"

      - name: "indicator_name"
        type: "VARCHAR(32)"
        nullable: false
        comment: "指标名称"

      - name: "indicator_value"
        type: "DOUBLE PRECISION"
        nullable: true
        comment: "指标值"

      - name: "params"
        type: "JSONB"
        nullable: true
        comment: "指标参数"

      - name: "created_at"
        type: "TIMESTAMPTZ"
        nullable: false
        default: "NOW()"

    indexes:
      - name: "idx_tech_symbol_date"
        columns: "symbol, calc_date DESC"
        type: "BTREE"

      - name: "idx_tech_indicator"
        columns: "indicator_name"
        type: "BTREE"

    timescale_config:
      is_hypertable: true
      time_column: "calc_date"
      chunk_interval: "1 day"
      compress_after: "30 days"
      compress_segmentby: ["symbol", "indicator_name"]
      retention_period: "5 years"

  # MySQL - 股票基础信息
  - table_name: "stock_info"
    database_type: "mysql"
    data_classification: "STOCK_INFO"
    description: "股票基础信息(参考数据)"

    columns:
      - name: "id"
        type: "BIGINT UNSIGNED"
        nullable: false
        primary_key: true
        comment: "自增主键"

      - name: "symbol"
        type: "VARCHAR(16)"
        nullable: false
        comment: "股票代码"

      - name: "name"
        type: "VARCHAR(64)"
        nullable: false
        comment: "股票名称"

      - name: "exchange"
        type: "VARCHAR(16)"
        nullable: false
        comment: "交易所"

      - name: "list_date"
        type: "DATE"
        nullable: true
        comment: "上市日期"

      - name: "delist_date"
        type: "DATE"
        nullable: true
        comment: "退市日期"

      - name: "status"
        type: "VARCHAR(16)"
        nullable: false
        default: "'ACTIVE'"
        comment: "状态"

      - name: "updated_at"
        type: "TIMESTAMP"
        nullable: false
        default: "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"

    indexes:
      - name: "uk_symbol"
        columns: "symbol"
        type: "UNIQUE"

      - name: "idx_exchange_status"
        columns: "exchange, status"

# 监控配置
monitoring:
  database_url: "${MONITOR_DB_URL:postgresql://localhost/mystocks_monitor}"
  retention_days:
    operation_logs: 30
    performance_metrics: 90
    data_quality_checks: 7
  alert_channels:
    - type: "log"
      level: "ERROR"
    - type: "webhook"
      url: "${ALERT_WEBHOOK_URL:}"
```

#### 配置加载器
```python
import yaml
import os
import re
from typing import Any

class ConfigLoader:
    """配置加载器,支持环境变量替换"""

    @staticmethod
    def load_config(config_path: str) -> SystemConfig:
        """加载并验证配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            raw_config = yaml.safe_load(f)

        # 环境变量替换
        processed_config = ConfigLoader._replace_env_vars(raw_config)

        # Pydantic验证
        try:
            config = SystemConfig(**processed_config)
            return config
        except Exception as e:
            raise ValueError(f"配置文件验证失败: {e}")

    @staticmethod
    def _replace_env_vars(obj: Any) -> Any:
        """递归替换配置中的环境变量"""
        if isinstance(obj, dict):
            return {k: ConfigLoader._replace_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [ConfigLoader._replace_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            # 匹配 ${VAR_NAME:default_value} 格式
            pattern = r'\$\{([^:}]+)(?::([^}]*))?\}'

            def replacer(match):
                var_name = match.group(1)
                default_value = match.group(2) or ''
                return os.getenv(var_name, default_value)

            return re.sub(pattern, replacer, obj)
        else:
            return obj

# 使用示例
config = ConfigLoader.load_config('table_config.yaml')

# 访问配置
print(f"项目名称: {config.project_name}")
print(f"配置版本: {config.version}")
print(f"表数量: {len(config.tables)}")

# 遍历表定义
for table in config.tables:
    print(f"\n表: {table.table_name}")
    print(f"  数据库: {table.database_type}")
    print(f"  分类: {table.data_classification}")
    print(f"  列数: {len(table.columns)}")

    if table.tdengine_config and table.tdengine_config.is_super_table:
        print(f"  TDengine超级表,标签数: {len(table.tdengine_config.tags)}")

    if table.timescale_config and table.timescale_config.is_hypertable:
        print(f"  TimescaleDB Hypertable,Chunk间隔: {table.timescale_config.chunk_interval}")
```

#### 配置驱动表创建
```python
class ConfigDrivenTableManager:
    def __init__(self, config: SystemConfig):
        self.config = config
        self.db_connections = self._init_connections()

    def create_all_tables(self):
        """根据配置创建所有表"""
        for table_def in self.config.tables:
            try:
                self._create_single_table(table_def)
                print(f"✅ 表创建成功: {table_def.table_name}")
            except Exception as e:
                print(f"❌ 表创建失败: {table_def.table_name}, 错误: {e}")

    def _create_single_table(self, table_def: TableDefinition):
        """创建单个表"""
        if table_def.database_type == DatabaseType.TDENGINE:
            self._create_tdengine_table(table_def)
        elif table_def.database_type == DatabaseType.POSTGRESQL:
            self._create_postgresql_table(table_def)
        elif table_def.database_type == DatabaseType.MYSQL:
            self._create_mysql_table(table_def)
        # Redis无需创建表结构

    def _create_tdengine_table(self, table_def: TableDefinition):
        """创建TDengine表"""
        conn = self.db_connections[DatabaseType.TDENGINE]
        td_config = table_def.tdengine_config

        if td_config.is_super_table:
            # 构建超级表SQL
            columns_sql = ", ".join([
                f"{col.name} {col.type}"
                for col in table_def.columns
            ])

            tags_sql = ", ".join([
                f"{tag.name} {tag.type}"
                for tag in td_config.tags
            ])

            # 提取编码配置
            encodings = [col.encoding for col in table_def.columns if col.encoding]
            encode_clause = f"ENCODE '{','.join(encodings)}'" if encodings else ""

            sql = f"""
                CREATE STABLE IF NOT EXISTS {table_def.table_name} (
                    {columns_sql}
                ) TAGS (
                    {tags_sql}
                )
                {encode_clause}
                COMPRESS '{td_config.compression}'
                LEVEL '{td_config.compression_level}'
                KEEP {td_config.keep_days};
            """

            conn.execute(sql)

    def _create_postgresql_table(self, table_def: TableDefinition):
        """创建PostgreSQL表"""
        conn = self.db_connections[DatabaseType.POSTGRESQL]

        # 构建普通表SQL
        columns_sql = ", ".join([
            f"{col.name} {col.type} "
            f"{'NOT NULL' if not col.nullable else ''} "
            f"{'PRIMARY KEY' if col.primary_key else ''} "
            f"{'DEFAULT ' + col.default if col.default else ''}"
            for col in table_def.columns
        ])

        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_def.table_name} (
                {columns_sql}
            );
        """
        conn.execute(create_sql)

        # 如果是Hypertable,转换
        ts_config = table_def.timescale_config
        if ts_config and ts_config.is_hypertable:
            conn.execute(f"""
                SELECT create_hypertable(
                    '{table_def.table_name}',
                    '{ts_config.time_column}',
                    chunk_time_interval => INTERVAL '{ts_config.chunk_interval}',
                    if_not_exists => TRUE
                );
            """)

            # 配置压缩
            segmentby = ', '.join(ts_config.compress_segmentby) if ts_config.compress_segmentby else ''
            conn.execute(f"""
                ALTER TABLE {table_def.table_name} SET (
                    timescaledb.compress,
                    timescaledb.compress_segmentby = '{segmentby}',
                    timescaledb.compress_orderby = '{ts_config.time_column} DESC'
                );
            """)

            # 添加压缩策略
            conn.execute(f"""
                SELECT add_compression_policy(
                    '{table_def.table_name}',
                    INTERVAL '{ts_config.compress_after}'
                );
            """)

        # 创建索引
        if table_def.indexes:
            for idx in table_def.indexes:
                conn.execute(f"""
                    CREATE INDEX IF NOT EXISTS {idx['name']}
                    ON {table_def.table_name} ({idx['columns']});
                """)
```

---

## 5. 数据源API策略决策 (R5)

### Decision (决策)
**优先级顺序**:
1. **Akshare** (主要数据源) - 综合免费数据,API丰富
2. **Baostock** (快速获取历史) - 无需认证,35+年历史数据
3. **Tushare** (深度财务/历史) - 需要token,积分系统
4. **Efinance** (实时行情) - 东方财富数据,通过CustomerAdapter集成
5. **RiceQuant/Byapi** - 不推荐 (商业限制)

### Rationale (技术原因)
1. **Akshare全面性**: 覆盖A股/港股/美股/期货/基金/宏观数据,免费无限制
2. **Baostock可靠性**: 证券宝官方,数据质量高,回溯测试必备
3. **Tushare专业性**: 财务数据结构化好,但需积分管理
4. **Efinance实时性**: 东方财富官方接口,Level-2数据支持
5. **避免商业风险**: RiceQuant需付费,API使用受限

### Alternatives Considered (考虑的其他方案)
- ❌ **Wind/Choice**: 成本过高(万元级年费)
- ❌ **纯爬虫方案**: 不稳定,法律风险
- ❌ **单一数据源**: 无冗余,故障时无法回退

### Implementation Notes (实现要点)

#### 统一数据源接口
```python
from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Optional
from datetime import datetime

class IDataSource(ABC):
    """数据源统一接口"""

    @abstractmethod
    def get_stock_list(self) -> pd.DataFrame:
        """
        获取股票列表

        Returns:
            DataFrame with columns: symbol, name, exchange, list_date
        """
        pass

    @abstractmethod
    def get_daily_kline(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取日线数据

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            DataFrame with columns: symbol, trade_date, open, high, low, close, volume, amount
        """
        pass

    @abstractmethod
    def get_realtime_quotes(self, symbols: List[str]) -> pd.DataFrame:
        """
        获取实时行情

        Args:
            symbols: 股票代码列表

        Returns:
            DataFrame with columns: symbol, current_price, volume, amount, bid_price, ask_price, ...
        """
        pass

    @abstractmethod
    def get_financial_report(self, symbol: str, report_type: str) -> pd.DataFrame:
        """
        获取财务报表

        Args:
            symbol: 股票代码
            report_type: 报表类型 (balance_sheet/income_statement/cash_flow)

        Returns:
            DataFrame with financial metrics
        """
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        """数据源名称"""
        pass

    @property
    @abstractmethod
    def supported_markets(self) -> List[str]:
        """支持的市场列表"""
        pass
```

#### Akshare适配器 (主要数据源)
```python
import akshare as ak

class AkshareDataSource(IDataSource):
    """Akshare数据源适配器"""

    @property
    def source_name(self) -> str:
        return "Akshare"

    @property
    def supported_markets(self) -> List[str]:
        return ["CN_A", "HK", "US", "FUTURES", "FUND"]

    def get_stock_list(self) -> pd.DataFrame:
        """获取A股列表"""
        try:
            # 沪深A股列表
            df = ak.stock_info_a_code_name()
            df = df.rename(columns={
                'code': 'symbol',
                'name': 'name'
            })
            # 添加交易所信息
            df['exchange'] = df['symbol'].apply(
                lambda x: 'SH' if x.startswith('6') else 'SZ'
            )
            return df
        except Exception as e:
            raise DataSourceError(f"Akshare获取股票列表失败: {e}")

    def get_daily_kline(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取日线数据"""
        try:
            # Akshare日线接口
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date.replace('-', ''),
                end_date=end_date.replace('-', ''),
                adjust="qfq"  # 前复权
            )

            # 统一列名
            df = df.rename(columns={
                '日期': 'trade_date',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume',
                '成交额': 'amount'
            })

            df['symbol'] = symbol
            return df[['symbol', 'trade_date', 'open', 'high', 'low', 'close', 'volume', 'amount']]
        except Exception as e:
            raise DataSourceError(f"Akshare获取日线数据失败: {e}")

    def get_realtime_quotes(self, symbols: List[str]) -> pd.DataFrame:
        """获取实时行情"""
        try:
            # Akshare实时行情接口
            df = ak.stock_zh_a_spot_em()

            # 过滤目标股票
            df = df[df['代码'].isin(symbols)]

            # 统一列名
            df = df.rename(columns={
                '代码': 'symbol',
                '名称': 'name',
                '最新价': 'current_price',
                '涨跌幅': 'change_pct',
                '成交量': 'volume',
                '成交额': 'amount',
                '买一价': 'bid_price_1',
                '卖一价': 'ask_price_1'
            })

            return df
        except Exception as e:
            raise DataSourceError(f"Akshare获取实时行情失败: {e}")

    def get_financial_report(self, symbol: str, report_type: str) -> pd.DataFrame:
        """获取财务报表"""
        try:
            if report_type == "balance_sheet":
                df = ak.stock_financial_report_sina(stock=symbol, symbol="资产负债表")
            elif report_type == "income_statement":
                df = ak.stock_financial_report_sina(stock=symbol, symbol="利润表")
            elif report_type == "cash_flow":
                df = ak.stock_financial_report_sina(stock=symbol, symbol="现金流量表")
            else:
                raise ValueError(f"不支持的报表类型: {report_type}")

            return df
        except Exception as e:
            raise DataSourceError(f"Akshare获取财务报表失败: {e}")

    def get_industry_classification(self, standard: str = "申万一级") -> pd.DataFrame:
        """获取行业分类"""
        try:
            if standard == "申万一级":
                df = ak.stock_board_industry_name_em()
            elif standard == "概念":
                df = ak.stock_board_concept_name_em()
            return df
        except Exception as e:
            raise DataSourceError(f"Akshare获取行业分类失败: {e}")
```

#### Baostock适配器 (历史数据备份)
```python
import baostock as bs

class BaostockDataSource(IDataSource):
    """Baostock数据源适配器"""

    def __init__(self):
        self.logged_in = False

    def __enter__(self):
        """上下文管理器: 登录"""
        lg = bs.login()
        if lg.error_code != '0':
            raise DataSourceError(f"Baostock登录失败: {lg.error_msg}")
        self.logged_in = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器: 登出"""
        if self.logged_in:
            bs.logout()

    @property
    def source_name(self) -> str:
        return "Baostock"

    @property
    def supported_markets(self) -> List[str]:
        return ["CN_A"]

    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        try:
            rs = bs.query_stock_basic()
            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())

            df = pd.DataFrame(data_list, columns=rs.fields)
            df = df.rename(columns={
                'code': 'symbol',
                'code_name': 'name',
                'ipoDate': 'list_date'
            })
            return df
        except Exception as e:
            raise DataSourceError(f"Baostock获取股票列表失败: {e}")

    def get_daily_kline(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取日线数据"""
        try:
            # Baostock需要格式: sh.600000 或 sz.000001
            bs_symbol = self._convert_symbol(symbol)

            rs = bs.query_history_k_data_plus(
                bs_symbol,
                "date,code,open,high,low,close,volume,amount,turn",
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="2"  # 前复权
            )

            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())

            df = pd.DataFrame(data_list, columns=rs.fields)
            df = df.rename(columns={
                'date': 'trade_date',
                'code': 'symbol'
            })

            # 数据类型转换
            for col in ['open', 'high', 'low', 'close', 'volume', 'amount']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            return df[['symbol', 'trade_date', 'open', 'high', 'low', 'close', 'volume', 'amount']]
        except Exception as e:
            raise DataSourceError(f"Baostock获取日线数据失败: {e}")

    def get_realtime_quotes(self, symbols: List[str]) -> pd.DataFrame:
        """Baostock不支持实时行情"""
        raise NotImplementedError("Baostock不提供实时行情接口")

    def get_financial_report(self, symbol: str, report_type: str) -> pd.DataFrame:
        """获取财务报表"""
        try:
            bs_symbol = self._convert_symbol(symbol)

            if report_type == "balance_sheet":
                rs = bs.query_balance_data(code=bs_symbol, year=2023, quarter=4)
            elif report_type == "income_statement":
                rs = bs.query_profit_data(code=bs_symbol, year=2023, quarter=4)
            elif report_type == "cash_flow":
                rs = bs.query_cash_flow_data(code=bs_symbol, year=2023, quarter=4)
            else:
                raise ValueError(f"不支持的报表类型: {report_type}")

            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())

            return pd.DataFrame(data_list, columns=rs.fields)
        except Exception as e:
            raise DataSourceError(f"Baostock获取财务报表失败: {e}")

    @staticmethod
    def _convert_symbol(symbol: str) -> str:
        """转换股票代码格式: 600000 -> sh.600000"""
        if symbol.startswith('6'):
            return f"sh.{symbol}"
        else:
            return f"sz.{symbol}"
```

#### 数据源工厂 (多源路由)
```python
from typing import Optional

class DataSourceFactory:
    """数据源工厂: 自动选择最佳数据源"""

    def __init__(self):
        self.sources = {
            'akshare': AkshareDataSource(),
            'baostock': BaostockDataSource(),
            'tushare': TushareDataSource(),  # 需实现
            'efinance': EfinanceDataSource()  # 需实现
        }

        # 数据类型优先级映射
        self.priority_map = {
            'stock_list': ['akshare', 'baostock'],
            'daily_kline': ['akshare', 'baostock', 'tushare'],
            'realtime_quotes': ['efinance', 'akshare'],
            'financial_report': ['tushare', 'akshare', 'baostock'],
            'industry_classification': ['akshare']
        }

    def get_data(self, data_type: str, fallback=True, **kwargs) -> pd.DataFrame:
        """
        智能获取数据,支持自动降级

        Args:
            data_type: 数据类型
            fallback: 是否启用降级策略
            **kwargs: 传递给数据源方法的参数

        Returns:
            DataFrame
        """
        priorities = self.priority_map.get(data_type, ['akshare'])

        for source_name in priorities:
            try:
                source = self.sources[source_name]

                # 动态调用方法
                method = getattr(source, f"get_{data_type}", None)
                if method:
                    print(f"🔍 尝试数据源: {source.source_name}")
                    result = method(**kwargs)
                    print(f"✅ {source.source_name} 成功")
                    return result

            except Exception as e:
                print(f"❌ {source_name} 失败: {e}")
                if not fallback:
                    raise
                # 继续下一个数据源

        raise DataSourceError(f"所有数据源均失败,数据类型: {data_type}")

# 使用示例
factory = DataSourceFactory()

# 自动选择最佳数据源获取日线数据
df_daily = factory.get_data(
    'daily_kline',
    symbol='000001',
    start_date='2024-01-01',
    end_date='2024-10-11'
)

# 实时行情优先使用Efinance
df_realtime = factory.get_data(
    'realtime_quotes',
    symbols=['000001', '600000']
)
```

#### 关键API对比表
| 数据类型 | Akshare | Baostock | Tushare | Efinance |
|---------|---------|----------|---------|----------|
| 股票列表 | ✅ 免费 | ✅ 免费 | ⚠️ 需积分 | ❌ |
| 日线数据 | ✅ 免费 | ✅ 35+年 | ⚠️ 需积分 | ✅ 免费 |
| 实时行情 | ✅ 免费 | ❌ | ⚠️ 需积分 | ✅ 最快 |
| 分钟数据 | ✅ 免费 | ❌ | ⚠️ 需积分 | ✅ 免费 |
| 财务报表 | ✅ 基础 | ✅ 完整 | ✅ 最全 | ❌ |
| 行业分类 | ✅ 多标准 | ✅ 申万 | ✅ 多标准 | ✅ 东财概念 |
| Level-2 | ❌ | ❌ | ⚠️ 需积分 | ✅ 免费 |

---

## 6. Redis持久化与固化决策 (R6)

### Decision (决策)
- **持久化策略**: AOF + RDB 混合持久化
- **AOF配置**: appendfsync everysec (每秒同步)
- **固化机制**: 基于定时任务的主动固化 (240秒周期)
- **TTL策略**: 热数据TTL设置为300秒
- **批量优化**: Pipeline批量读取,减少网络往返

**重要约束**: 使用 Redis 数据库编号 1-15,避开 0 号数据库 (已分配给其他程序)

### Rationale (技术原因)
1. **数据安全**: AOF确保最多丢失1秒数据,RDB提供定期完整快照
2. **性能平衡**: everysec在性能和安全性之间取得最佳平衡
3. **定时固化**: 避免依赖Keyspace Notification (性能开销大,不可靠)
4. **TTL管理**: 自动清理过期数据,防止内存溢出

### Alternatives Considered (考虑的其他方案)
- ❌ **仅RDB**: 数据丢失风险高 (最多丢失数分钟)
- ❌ **appendfsync always**: 性能损失严重 (每次写入同步磁盘)
- ❌ **基于Keyspace Notification**: CPU开销大,生产环境不推荐
- ❌ **无TTL策略**: 内存无限增长,OOM风险

### Implementation Notes (实现要点)

#### Redis服务器配置 (redis.conf)
```conf
# 持久化配置
# 1. RDB快照 (定期备份)
save 900 1        # 900秒内至少1个key变化则保存
save 300 10       # 300秒内至少10个key变化则保存
save 60 10000     # 60秒内至少10000个key变化则保存

dbfilename dump.rdb
dir /var/lib/redis

# 2. AOF持久化 (实时日志)
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec              # 每秒同步,平衡性能和安全性

# AOF重写配置
auto-aof-rewrite-percentage 100   # AOF文件增长100%时触发重写
auto-aof-rewrite-min-size 64mb    # AOF最小64MB时才重写

# 3. 混合持久化 (Redis 4.0+)
aof-use-rdb-preamble yes          # AOF重写时使用RDB格式

# 内存管理
maxmemory 4gb
maxmemory-policy allkeys-lru      # 内存满时使用LRU淘汰

# Keyspace Notification (默认关闭,仅调试时开启)
notify-keyspace-events ""         # 生产环境不开启,避免性能损失

# 数据库编号配置
databases 16                      # 默认16个数据库(0-15)
# 注意: 本项目使用数据库1-15,避开0号
```

#### Redis数据访问层 (带固化支持)
```python
import redis
import json
import pickle
from typing import Any, List, Dict
from datetime import datetime, timedelta

class RedisDataAccess:
    """Redis数据访问层,支持热数据固化"""

    def __init__(self, host='localhost', port=6379, password='', db=1):  # 默认使用1号库
        """
        初始化Redis连接

        Args:
            db: Redis数据库编号 (1-15),避开0号
        """
        if db == 0:
            raise ValueError("不允许使用0号数据库,请使用1-15号库")

        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            password=password,
            db=db,
            max_connections=50,
            decode_responses=False  # 支持二进制数据
        )
        self.redis = redis.Redis(connection_pool=self.pool)

        # 固化配置
        self.ttl_seconds = 300      # 热数据TTL: 5分钟
        self.fixation_interval = 240  # 固化周期: 4分钟

    def save_realtime_position(self, account_id: str, positions: pd.DataFrame):
        """
        保存实时持仓数据

        Args:
            account_id: 账户ID
            positions: DataFrame with columns [symbol, quantity, cost_price, current_price]
        """
        key = f"position:{account_id}"

        # 序列化为JSON
        positions_json = positions.to_json(orient='records')

        # 写入Redis并设置TTL
        self.redis.setex(
            name=key,
            time=self.ttl_seconds,
            value=positions_json
        )

        # 记录到固化候选集合
        self.redis.sadd("fixation:candidates", key)

    def get_realtime_position(self, account_id: str) -> Optional[pd.DataFrame]:
        """获取实时持仓数据"""
        key = f"position:{account_id}"
        value = self.redis.get(key)

        if value:
            return pd.read_json(value, orient='records')
        return None

    def save_market_snapshot(self, symbols: List[str], snapshots: pd.DataFrame):
        """
        保存市场快照 (Level-2盘口数据)

        Args:
            symbols: 股票代码列表
            snapshots: DataFrame with Level-2 data
        """
        pipe = self.redis.pipeline(transaction=False)

        for symbol in symbols:
            snapshot_data = snapshots[snapshots['symbol'] == symbol].iloc[0]
            key = f"snapshot:{symbol}"

            # 使用Hash存储结构化数据
            pipe.hset(key, mapping={
                'current_price': snapshot_data['current_price'],
                'bid_prices': json.dumps(snapshot_data['bid_prices']),
                'ask_prices': json.dumps(snapshot_data['ask_prices']),
                'bid_volumes': json.dumps(snapshot_data['bid_volumes']),
                'ask_volumes': json.dumps(snapshot_data['ask_volumes']),
                'timestamp': datetime.now().isoformat()
            })
            pipe.expire(key, self.ttl_seconds)

            # 加入固化候选
            pipe.sadd("fixation:candidates", key)

        pipe.execute()

    def batch_get_snapshots(self, symbols: List[str]) -> Dict[str, dict]:
        """批量获取市场快照 (Pipeline优化)"""
        pipe = self.redis.pipeline(transaction=False)

        for symbol in symbols:
            pipe.hgetall(f"snapshot:{symbol}")

        results = pipe.execute()

        # 解析结果
        snapshots = {}
        for symbol, data in zip(symbols, results):
            if data:
                # 解码二进制数据
                decoded = {k.decode(): v.decode() for k, v in data.items()}
                decoded['bid_prices'] = json.loads(decoded['bid_prices'])
                decoded['ask_prices'] = json.loads(decoded['ask_prices'])
                snapshots[symbol] = decoded

        return snapshots

    def fixate_hot_data(self, postgresql_access):
        """
        固化热数据到PostgreSQL

        Args:
            postgresql_access: PostgreSQL数据访问对象
        """
        # 获取所有候选key
        candidates = self.redis.smembers("fixation:candidates")

        if not candidates:
            print("无待固化数据")
            return

        print(f"🔄 开始固化 {len(candidates)} 条热数据...")

        for key in candidates:
            key_str = key.decode()

            try:
                # 根据key类型决定固化策略
                if key_str.startswith("position:"):
                    self._fixate_position(key_str, postgresql_access)
                elif key_str.startswith("snapshot:"):
                    self._fixate_snapshot(key_str, postgresql_access)
                elif key_str.startswith("account:"):
                    self._fixate_account(key_str, postgresql_access)

                # 固化成功后从候选集合移除
                self.redis.srem("fixation:candidates", key)

            except Exception as e:
                print(f"❌ 固化失败 {key_str}: {e}")
                # 保留在候选集合,下次重试

        print(f"✅ 固化完成")

    def _fixate_position(self, key: str, pg_access):
        """固化持仓数据"""
        value = self.redis.get(key)
        if not value:
            return

        account_id = key.split(':')[1]
        positions_df = pd.read_json(value, orient='records')

        # 添加元数据
        positions_df['account_id'] = account_id
        positions_df['snapshot_time'] = datetime.now()

        # 写入PostgreSQL
        pg_access.save_data(positions_df, 'position_history')

    def _fixate_snapshot(self, key: str, pg_access):
        """固化市场快照"""
        snapshot = self.redis.hgetall(key)
        if not snapshot:
            return

        symbol = key.split(':')[1]

        # 解码并转换为DataFrame
        decoded = {k.decode(): v.decode() for k, v in snapshot.items()}
        df = pd.DataFrame([{
            'symbol': symbol,
            'current_price': float(decoded['current_price']),
            'bid_prices': decoded['bid_prices'],
            'ask_prices': decoded['ask_prices'],
            'timestamp': decoded['timestamp']
        }])

        pg_access.save_data(df, 'market_snapshot_history')

    def _fixate_account(self, key: str, pg_access):
        """固化账户数据"""
        account = self.redis.hgetall(key)
        if not account:
            return

        account_id = key.split(':')[1]

        # 转换为DataFrame
        decoded = {k.decode(): v.decode() for k, v in account.items()}
        df = pd.DataFrame([{
            'account_id': account_id,
            'total_asset': float(decoded['total_asset']),
            'available_cash': float(decoded['available_cash']),
            'market_value': float(decoded['market_value']),
            'snapshot_time': datetime.now()
        }])

        pg_access.save_data(df, 'account_history')
```

#### 定时固化调度器
```python
import schedule
import time
import threading

class RedisFixationScheduler:
    """Redis数据固化调度器"""

    def __init__(self, redis_access, postgresql_access):
        self.redis_access = redis_access
        self.postgresql_access = postgresql_access
        self.running = False

    def start(self):
        """启动定时固化任务"""
        self.running = True

        # 每240秒固化一次 (TTL=300秒,留60秒缓冲)
        schedule.every(240).seconds.do(self._run_fixation)

        # 后台线程运行
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(10)

        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        print("✅ Redis固化调度器已启动 (周期: 240秒)")

    def stop(self):
        """停止调度器"""
        self.running = False
        schedule.clear()
        print("⏹️ Redis固化调度器已停止")

    def _run_fixation(self):
        """执行固化任务"""
        try:
            self.redis_access.fixate_hot_data(self.postgresql_access)
        except Exception as e:
            print(f"❌ 固化任务执行失败: {e}")

# 使用示例
redis_access = RedisDataAccess(db=1)  # 使用1号库
postgresql_access = PostgreSQLDataAccess()

scheduler = RedisFixationScheduler(redis_access, postgresql_access)
scheduler.start()

# 应用运行中...
# 固化任务会每240秒自动执行

# 优雅关闭
# scheduler.stop()
```

#### 性能优化: Pipeline批量操作
```python
def batch_save_positions(self, positions_dict: Dict[str, pd.DataFrame]):
    """
    批量保存多账户持仓数据 (Pipeline优化)

    Args:
        positions_dict: {account_id: positions_df}
    """
    pipe = self.redis.pipeline(transaction=False)

    for account_id, positions in positions_dict.items():
        key = f"position:{account_id}"
        value = positions.to_json(orient='records')

        pipe.setex(key, self.ttl_seconds, value)
        pipe.sadd("fixation:candidates", key)

    # 一次性提交所有命令
    pipe.execute()
    print(f"✅ 批量保存 {len(positions_dict)} 个账户持仓")
```

---

## 7. 监控数据库选型决策 (R7)

### Decision (决策)
- **数据库选择**: PostgreSQL (独立实例)
- **扩展插件**: pg_partman (自动分区) + pg_cron (定时清理)
- **分区策略**: 按时间范围分区 (按月)
- **保留策略**: 操作日志30天,性能指标90天,质量检查7天
- **索引策略**: JSONB GIN索引 + 时间戳BRIN索引

### Rationale (技术原因)
1. **JSONB优势**: PostgreSQL对JSON数据的查询和索引支持远超MySQL
2. **时序优化**: BRIN索引适合时间戳字段,空间占用小、性能高
3. **自动化**: pg_partman自动创建和管理分区,pg_cron定时清理过期数据
4. **独立性**: 监控数据库与业务数据库隔离,互不影响

### Alternatives Considered (考虑的其他方案)
- ❌ **MySQL**: JSONB支持弱,时序分区管理复杂
- ❌ **TDengine**: 监控数据量较小,不需要时序数据库的极致压缩
- ❌ **InfluxDB**: 增加技术栈复杂度,PostgreSQL足够胜任

### Implementation Notes (实现要点)

#### 监控数据库表结构
```sql
-- 1. 操作日志表 (保留30天)
CREATE TABLE IF NOT EXISTS operation_logs (
    id BIGSERIAL NOT NULL,
    operation_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    operation_type VARCHAR(64) NOT NULL,         -- save/load/delete/query
    database_target VARCHAR(32) NOT NULL,        -- tdengine/postgresql/mysql/redis
    table_name VARCHAR(128),
    data_classification VARCHAR(64),
    record_count BIGINT,
    operation_details JSONB,                     -- 操作详细信息
    success BOOLEAN NOT NULL,
    error_message TEXT,
    duration_ms BIGINT,                          -- 执行耗时(毫秒)
    PRIMARY KEY (id, operation_time)
) PARTITION BY RANGE (operation_time);

-- 创建BRIN索引 (时间戳)
CREATE INDEX idx_oplog_time ON operation_logs USING BRIN (operation_time);

-- 创建GIN索引 (JSONB)
CREATE INDEX idx_oplog_details ON operation_logs USING GIN (operation_details);

-- 创建复合索引
CREATE INDEX idx_oplog_type_time ON operation_logs (operation_type, operation_time DESC);
CREATE INDEX idx_oplog_target_time ON operation_logs (database_target, operation_time DESC);

-- 2. 性能指标表 (保留90天)
CREATE TABLE IF NOT EXISTS performance_metrics (
    id BIGSERIAL NOT NULL,
    metric_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metric_name VARCHAR(64) NOT NULL,            -- query_duration/write_throughput/connection_count
    metric_value DOUBLE PRECISION NOT NULL,
    metric_unit VARCHAR(32),                     -- ms/records_per_sec/count
    database_target VARCHAR(32),
    tags JSONB,                                  -- 额外维度标签
    PRIMARY KEY (id, metric_time)
) PARTITION BY RANGE (metric_time);

CREATE INDEX idx_perf_time ON performance_metrics USING BRIN (metric_time);
CREATE INDEX idx_perf_name_time ON performance_metrics (metric_name, metric_time DESC);

-- 3. 数据质量检查表 (保留7天)
CREATE TABLE IF NOT EXISTS data_quality_checks (
    id BIGSERIAL NOT NULL,
    check_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    check_type VARCHAR(64) NOT NULL,             -- completeness/freshness/accuracy
    data_classification VARCHAR(64) NOT NULL,
    table_name VARCHAR(128),
    expected_count BIGINT,
    actual_count BIGINT,
    missing_count BIGINT,
    completeness_rate DOUBLE PRECISION,
    freshness_delay_seconds BIGINT,
    check_result VARCHAR(32) NOT NULL,           -- pass/warning/fail
    check_details JSONB,
    PRIMARY KEY (id, check_time)
) PARTITION BY RANGE (check_time);

CREATE INDEX idx_quality_time ON data_quality_checks USING BRIN (check_time);
CREATE INDEX idx_quality_result_time ON data_quality_checks (check_result, check_time DESC);

-- 4. 告警记录表 (保留90天)
CREATE TABLE IF NOT EXISTS alert_records (
    id BIGSERIAL NOT NULL,
    alert_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    alert_level VARCHAR(16) NOT NULL,            -- INFO/WARNING/ERROR/CRITICAL
    alert_source VARCHAR(64) NOT NULL,           -- monitoring/quality/performance
    alert_message TEXT NOT NULL,
    alert_context JSONB,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_time TIMESTAMPTZ,
    resolved_by VARCHAR(64),
    PRIMARY KEY (id, alert_time)
) PARTITION BY RANGE (alert_time);

CREATE INDEX idx_alert_time ON alert_records USING BRIN (alert_time);
CREATE INDEX idx_alert_level_time ON alert_records (alert_level, alert_time DESC);
CREATE INDEX idx_alert_unresolved ON alert_records (resolved, alert_time DESC) WHERE resolved = FALSE;
```

#### pg_partman自动分区配置
```sql
-- 安装pg_partman扩展
CREATE EXTENSION IF NOT EXISTS pg_partman;

-- 配置operation_logs自动分区 (按月)
SELECT partman.create_parent(
    p_parent_table := 'public.operation_logs',
    p_control := 'operation_time',
    p_type := 'native',
    p_interval := '1 month',
    p_premake := 3,                              -- 预创建3个月分区
    p_start_partition := '2024-10-01'
);

-- 配置自动维护
UPDATE partman.part_config
SET retention = '30 days',                       -- 保留30天
    retention_keep_table = false,                -- 过期后删除表
    infinite_time_partitions = true
WHERE parent_table = 'public.operation_logs';

-- 配置performance_metrics自动分区
SELECT partman.create_parent(
    p_parent_table := 'public.performance_metrics',
    p_control := 'metric_time',
    p_type := 'native',
    p_interval := '1 month',
    p_premake := 3
);

UPDATE partman.part_config
SET retention = '90 days',
    retention_keep_table = false
WHERE parent_table = 'public.performance_metrics';

-- 配置data_quality_checks自动分区
SELECT partman.create_parent(
    p_parent_table := 'public.data_quality_checks',
    p_control := 'check_time',
    p_type := 'native',
    p_interval := '1 day',                       -- 按天分区(数据量小)
    p_premake := 7
);

UPDATE partman.part_config
SET retention = '7 days',
    retention_keep_table = false
WHERE parent_table = 'public.data_quality_checks';
```

#### pg_cron定时清理任务
```sql
-- 安装pg_cron扩展
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- 配置定时分区维护 (每天凌晨4点)
SELECT cron.schedule(
    'partman-maintenance',
    '0 4 * * *',                                 -- Cron表达式: 每天4:00
    $$CALL partman.run_maintenance_proc()$$
);

-- 配置告警清理 (每周日凌晨3点)
SELECT cron.schedule(
    'cleanup-resolved-alerts',
    '0 3 * * 0',                                 -- 每周日3:00
    $$DELETE FROM alert_records
      WHERE resolved = TRUE
      AND resolved_time < NOW() - INTERVAL '30 days'$$
);

-- 查看定时任务
SELECT * FROM cron.job;
```

#### 监控数据库访问层
```python
import psycopg2
import json
from datetime import datetime

class MonitoringDatabase:
    """监控数据库访问层"""

    def __init__(self, connection_string):
        """
        初始化监控数据库连接

        Args:
            connection_string: PostgreSQL连接字符串
                格式: postgresql://user:password@host:port/database
        """
        self.conn = psycopg2.connect(connection_string)
        self.conn.autocommit = True

    def log_operation(self, operation_type, database_target, table_name,
                     data_classification, record_count, success,
                     duration_ms, error_message=None, details=None):
        """记录操作日志"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO operation_logs (
                operation_time, operation_type, database_target, table_name,
                data_classification, record_count, operation_details,
                success, error_message, duration_ms
            ) VALUES (
                NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            operation_type,
            database_target,
            table_name,
            data_classification,
            record_count,
            json.dumps(details) if details else None,
            success,
            error_message,
            duration_ms
        ))
        cursor.close()

    def record_performance_metric(self, metric_name, metric_value,
                                  metric_unit, database_target=None, tags=None):
        """记录性能指标"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO performance_metrics (
                metric_time, metric_name, metric_value, metric_unit,
                database_target, tags
            ) VALUES (
                NOW(), %s, %s, %s, %s, %s
            )
        """, (
            metric_name,
            metric_value,
            metric_unit,
            database_target,
            json.dumps(tags) if tags else None
        ))
        cursor.close()

    def log_quality_check(self, check_type, data_classification, table_name,
                         expected_count, actual_count, check_result,
                         freshness_delay=None, details=None):
        """记录数据质量检查"""
        completeness_rate = (actual_count / expected_count * 100) if expected_count > 0 else 0
        missing_count = max(0, expected_count - actual_count)

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO data_quality_checks (
                check_time, check_type, data_classification, table_name,
                expected_count, actual_count, missing_count,
                completeness_rate, freshness_delay_seconds,
                check_result, check_details
            ) VALUES (
                NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            check_type,
            data_classification,
            table_name,
            expected_count,
            actual_count,
            missing_count,
            completeness_rate,
            freshness_delay,
            check_result,
            json.dumps(details) if details else None
        ))
        cursor.close()

    def create_alert(self, alert_level, alert_source, alert_message, context=None):
        """创建告警"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO alert_records (
                alert_time, alert_level, alert_source, alert_message, alert_context
            ) VALUES (
                NOW(), %s, %s, %s, %s
            )
        """, (
            alert_level,
            alert_source,
            alert_message,
            json.dumps(context) if context else None
        ))
        cursor.close()

        print(f"🚨 [{alert_level}] {alert_message}")

    def get_recent_failures(self, hours=24, limit=50):
        """查询近期失败的操作"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT operation_time, operation_type, database_target,
                   table_name, error_message
            FROM operation_logs
            WHERE success = FALSE
              AND operation_time > NOW() - INTERVAL '%s hours'
            ORDER BY operation_time DESC
            LIMIT %s
        """, (hours, limit))

        results = cursor.fetchall()
        cursor.close()
        return results

    def get_slow_queries(self, threshold_ms=5000, hours=24):
        """查询慢操作"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT operation_time, operation_type, database_target,
                   table_name, duration_ms
            FROM operation_logs
            WHERE duration_ms > %s
              AND operation_time > NOW() - INTERVAL '%s hours'
            ORDER BY duration_ms DESC
            LIMIT 100
        """, (threshold_ms, hours))

        results = cursor.fetchall()
        cursor.close()
        return results

# 使用示例
monitor_db = MonitoringDatabase('postgresql://postgres:password@localhost/mystocks_monitor')

# 记录操作日志
import time
start = time.time()
# ... 执行数据库操作 ...
duration = (time.time() - start) * 1000

monitor_db.log_operation(
    operation_type='save',
    database_target='tdengine',
    table_name='tick_data',
    data_classification='TICK_DATA',
    record_count=10000,
    success=True,
    duration_ms=duration,
    details={'batch_size': 5000}
)

# 记录性能指标
monitor_db.record_performance_metric(
    metric_name='write_throughput',
    metric_value=10000 / (duration / 1000),  # records/sec
    metric_unit='records_per_sec',
    database_target='tdengine',
    tags={'table': 'tick_data'}
)

# 创建告警
if duration > 5000:
    monitor_db.create_alert(
        alert_level='WARNING',
        alert_source='performance',
        alert_message=f'慢写入操作: {duration:.0f}ms',
        context={'table': 'tick_data', 'duration_ms': duration}
    )
```

---

## 8. Python类型系统决策 (R8)

### Decision (决策)
- **类型提示**: Python 3.8+ 原生类型提示 + typing模块
- **DataFrame验证**: Pandera框架 + 自定义Schema
- **静态检查**: mypy (严格模式)
- **运行时验证**: Pydantic V2 (配置文件) + Pandera (DataFrame)

### Rationale (技术原因)
1. **早期错误发现**: 类型提示让IDE和mypy在编码阶段发现错误
2. **DataFrame安全**: Pandera提供DataFrame schema验证,防止脏数据进入系统
3. **文档价值**: 类型提示即文档,提升代码可读性
4. **重构支持**: 强类型系统让重构更安全,降低回归风险

### Alternatives Considered (考虑的其他方案)
- ❌ **无类型提示**: 运行时错误多,维护困难
- ❌ **仅Pydantic**: 无法验证DataFrame结构
- ❌ **Great Expectations**: 过于复杂,学习曲线陡峭

### Implementation Notes (实现要点)

#### Pandera DataFrame Schema定义
```python
import pandas as pd
import pandera as pa
from pandera.typing import DataFrame, Series
from typing import Optional
from datetime import datetime

# 1. 股票日线数据Schema
class DailyKlineSchema(pa.DataFrameModel):
    """日线数据Schema"""

    symbol: Series[str] = pa.Field(
        str_matches=r'^[0-9]{6}$',               # 6位数字代码
        description="股票代码"
    )

    trade_date: Series[pd.DatetimeTZDtype] = pa.Field(
        description="交易日期"
    )

    open: Series[float] = pa.Field(
        ge=0,                                    # >= 0
        description="开盘价"
    )

    high: Series[float] = pa.Field(
        ge=0,
        description="最高价"
    )

    low: Series[float] = pa.Field(
        ge=0,
        description="最低价"
    )

    close: Series[float] = pa.Field(
        ge=0,
        description="收盘价"
    )

    volume: Series[int] = pa.Field(
        ge=0,
        description="成交量"
    )

    amount: Series[float] = pa.Field(
        ge=0,
        nullable=True,
        description="成交额"
    )

    @pa.dataframe_check
    def check_ohlc_logic(cls, df: pd.DataFrame) -> pd.Series:
        """验证OHLC逻辑: high >= max(open, close), low <= min(open, close)"""
        return (
            (df['high'] >= df[['open', 'close']].max(axis=1)) &
            (df['low'] <= df[['open', 'close']].min(axis=1))
        )

    class Config:
        strict = True                            # 严格模式: 不允许额外列
        coerce = True                            # 自动类型转换

# 2. 实时持仓Schema
class PositionSchema(pa.DataFrameModel):
    """实时持仓Schema"""

    account_id: Series[str] = pa.Field(
        str_length={'min_value': 4, 'max_value': 32},
        description="账户ID"
    )

    symbol: Series[str] = pa.Field(
        str_matches=r'^[0-9]{6}$',
        description="股票代码"
    )

    quantity: Series[int] = pa.Field(
        ge=0,
        description="持仓数量"
    )

    cost_price: Series[float] = pa.Field(
        ge=0,
        description="成本价"
    )

    current_price: Series[float] = pa.Field(
        ge=0,
        description="当前价"
    )

    update_time: Series[pd.DatetimeTZDtype] = pa.Field(
        description="更新时间"
    )

    @pa.dataframe_check
    def check_quantity_lot_size(cls, df: pd.DataFrame) -> pd.Series:
        """验证数量为100的倍数 (A股1手=100股)"""
        return (df['quantity'] % 100 == 0) | (df['quantity'] == 0)

# 3. 技术指标Schema
class TechnicalIndicatorSchema(pa.DataFrameModel):
    """技术指标Schema"""

    symbol: Series[str]
    calc_date: Series[pd.DatetimeTZDtype]
    indicator_name: Series[str] = pa.Field(isin=['MACD', 'RSI', 'BOLL', 'KDJ', 'MA'])
    indicator_value: Series[float] = pa.Field(nullable=True)

    class Config:
        strict = False                           # 允许额外列(如indicator_params)
```

#### 类型安全的数据操作
```python
from typing import List, Optional, Literal
from pandera.typing import DataFrame

class TypeSafeDataManager:
    """类型安全的数据管理器"""

    @pa.check_types
    def save_daily_kline(
        self,
        data: DataFrame[DailyKlineSchema],       # Pandera验证
        classification: DataClassification
    ) -> bool:
        """
        保存日线数据 (类型安全)

        Args:
            data: 日线DataFrame,自动验证schema
            classification: 数据分类枚举

        Returns:
            bool: 是否成功
        """
        # Pandera自动验证data是否符合DailyKlineSchema
        # 不符合会抛出SchemaError异常

        return self.unified_manager.save_data_by_classification(
            data,
            classification
        )

    @pa.check_types
    def load_daily_kline(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> DataFrame[DailyKlineSchema]:
        """
        加载日线数据 (类型安全)

        Returns:
            验证后的日线DataFrame
        """
        data = self.unified_manager.load_data_by_classification(
            classification=DataClassification.DAILY_KLINE,
            filters={'symbol': symbol, 'start_date': start_date, 'end_date': end_date}
        )

        # Pandera自动验证返回值
        return data

    @pa.check_types
    def save_position(
        self,
        positions: DataFrame[PositionSchema]
    ) -> bool:
        """保存持仓数据 (类型安全)"""
        return self.unified_manager.save_data_by_classification(
            positions,
            DataClassification.REALTIME_POSITION
        )

# 使用示例
manager = TypeSafeDataManager()

# 正确的数据
valid_data = pd.DataFrame({
    'symbol': ['000001', '600000'],
    'trade_date': pd.to_datetime(['2024-10-10', '2024-10-10'], utc=True),
    'open': [10.5, 8.3],
    'high': [11.0, 8.9],
    'low': [10.2, 8.1],
    'close': [10.8, 8.7],
    'volume': [1000000, 2000000],
    'amount': [10800000.0, 17400000.0]
})

manager.save_daily_kline(valid_data, DataClassification.DAILY_KLINE)  # ✅ 通过

# 错误的数据 (high < close)
invalid_data = pd.DataFrame({
    'symbol': ['000001'],
    'trade_date': pd.to_datetime(['2024-10-10'], utc=True),
    'open': [10.5],
    'high': [10.0],  # ❌ high < close,违反OHLC逻辑
    'low': [10.2],
    'close': [10.8],
    'volume': [1000000],
    'amount': [10800000.0]
})

try:
    manager.save_daily_kline(invalid_data, DataClassification.DAILY_KLINE)
except pa.errors.SchemaError as e:
    print(f"❌ Schema验证失败: {e}")
    # 输出: ❌ Schema验证失败: <SchemaError: Check 'check_ohlc_logic' failed>
```

#### mypy静态类型检查配置
```ini
# mypy.ini
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True              # 强制所有函数添加类型提示
disallow_any_unimported = False
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
check_untyped_defs = True
strict_equality = True

# 第三方库存根配置
[mypy-pandas.*]
ignore_missing_imports = True

[mypy-numpy.*]
ignore_missing_imports = True

[mypy-akshare.*]
ignore_missing_imports = True

[mypy-taosws.*]
ignore_missing_imports = True
```

#### 完整类型提示示例
```python
from typing import List, Dict, Optional, Union, Literal, TypedDict
from datetime import datetime
from enum import Enum

# 枚举类型
class DataClassification(str, Enum):
    TICK_DATA = "TICK_DATA"
    MINUTE_KLINE = "MINUTE_KLINE"
    DAILY_KLINE = "DAILY_KLINE"
    # ... 其他分类

class DatabaseTarget(str, Enum):
    TDENGINE = "tdengine"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    REDIS = "redis"

# TypedDict (结构化字典)
class QueryFilter(TypedDict, total=False):
    """查询过滤器"""
    symbol: str
    start_date: str
    end_date: str
    limit: int

class ConnectionConfig(TypedDict):
    """数据库连接配置"""
    host: str
    port: int
    user: str
    password: str
    database: str
    pool_size: int

# 完整类型提示的类
class MyStocksUnifiedManager:
    """统一数据管理器 (完整类型提示)"""

    def __init__(
        self,
        config_path: str,
        monitor_db_url: str
    ) -> None:
        self.config_path: str = config_path
        self.monitor_db_url: str = monitor_db_url
        self.connections: Dict[DatabaseTarget, Any] = {}

    @pa.check_types
    def save_data_by_classification(
        self,
        data: DataFrame[DailyKlineSchema],       # Pandera验证
        classification: DataClassification,
        target_db: Optional[DatabaseTarget] = None
    ) -> bool:
        """
        保存数据 (根据分类自动路由)

        Args:
            data: 数据DataFrame
            classification: 数据分类
            target_db: 目标数据库 (None表示自动路由)

        Returns:
            是否成功

        Raises:
            ValueError: 不支持的数据分类
            DatabaseError: 数据库操作失败
        """
        if target_db is None:
            target_db = self._auto_route(classification)

        return self._execute_save(data, target_db)

    def _auto_route(
        self,
        classification: DataClassification
    ) -> DatabaseTarget:
        """自动路由逻辑"""
        routing_map: Dict[DataClassification, DatabaseTarget] = {
            DataClassification.TICK_DATA: DatabaseTarget.TDENGINE,
            DataClassification.DAILY_KLINE: DatabaseTarget.POSTGRESQL,
            # ... 其他映射
        }

        if classification not in routing_map:
            raise ValueError(f"不支持的数据分类: {classification}")

        return routing_map[classification]

    def load_data_by_classification(
        self,
        classification: DataClassification,
        filters: Optional[QueryFilter] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        加载数据 (根据分类自动路由)

        Args:
            classification: 数据分类
            filters: 查询过滤条件
            limit: 返回记录数限制

        Returns:
            DataFrame
        """
        target_db = self._auto_route(classification)
        return self._execute_load(target_db, filters, limit)

    def batch_save(
        self,
        datasets: List[tuple[pd.DataFrame, DataClassification]]
    ) -> Dict[DataClassification, bool]:
        """
        批量保存多个数据集

        Args:
            datasets: [(data1, classification1), (data2, classification2), ...]

        Returns:
            {classification: success_status}
        """
        results: Dict[DataClassification, bool] = {}

        for data, classification in datasets:
            success = self.save_data_by_classification(data, classification)
            results[classification] = success

        return results
```

#### 运行时验证装饰器
```python
from functools import wraps
import inspect

def validate_dataframe_schema(schema_class):
    """
    装饰器: 验证DataFrame参数

    Usage:
        @validate_dataframe_schema(DailyKlineSchema)
        def process_kline(df: pd.DataFrame):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 查找DataFrame类型的参数
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)

            for param_name, param_value in bound_args.arguments.items():
                if isinstance(param_value, pd.DataFrame):
                    # 验证schema
                    try:
                        schema_class.validate(param_value)
                    except pa.errors.SchemaError as e:
                        raise ValueError(
                            f"参数 '{param_name}' DataFrame验证失败: {e}"
                        )

            return func(*args, **kwargs)
        return wrapper
    return decorator

# 使用示例
@validate_dataframe_schema(DailyKlineSchema)
def calculate_moving_average(df: pd.DataFrame, window: int) -> pd.DataFrame:
    """计算移动平均 (自动验证输入DataFrame)"""
    df['MA'] = df['close'].rolling(window=window).mean()
    return df
```

---

## 9. 依赖清单

基于上述8个研究决策,最终确认的Python依赖清单:

### requirements.txt
```txt
# === 核心依赖 ===
pandas>=2.0.0                   # 数据处理
numpy>=1.24.0                   # 数值计算
pyyaml>=6.0                     # YAML配置解析

# === 数据库驱动 ===
# TDengine
taospy>=2.7.0                   # TDengine原生连接器(WebSocket)

# PostgreSQL + TimescaleDB
psycopg2-binary>=2.9.5          # PostgreSQL驱动
sqlalchemy>=2.0.0               # ORM支持(可选)

# MySQL/MariaDB
pymysql>=1.0.2                  # MySQL驱动

# Redis
redis>=4.5.0                    # Redis客户端

# === 数据源适配器 ===
akshare>=1.11.0                 # 主要数据源
baostock>=0.9.0                 # 历史数据备份
tushare>=1.3.0                  # 深度财务数据(可选)
efinance>=0.5.0                 # 实时行情(通过CustomerAdapter)

# === 类型验证 ===
pydantic>=2.0.0                 # 配置文件验证
pandera>=0.17.0                 # DataFrame schema验证

# === 监控和日志 ===
schedule>=1.2.0                 # 定时任务调度

# === 开发工具 ===
mypy>=1.5.0                     # 静态类型检查
pytest>=7.4.0                   # 单元测试
pytest-cov>=4.1.0               # 测试覆盖率

# === 可选依赖 ===
# requests>=2.31.0              # HTTP请求(数据源备用)
# beautifulsoup4>=4.12.0        # HTML解析(爬虫备用)
```

### 环境要求
- **Python版本**: 3.8+ (推荐3.10+)
- **操作系统**: Linux (生产环境推荐) / Windows / macOS
- **内存**: 最低8GB,推荐16GB+
- **存储**: SSD推荐 (TDengine/TimescaleDB性能依赖磁盘IO)

### 数据库服务端版本
- **TDengine**: 3.0+ (支持WebSocket连接)
- **PostgreSQL**: 14+ (支持TimescaleDB 2.x)
- **TimescaleDB**: 2.10+
- **MySQL/MariaDB**: 8.0+ / 10.6+
- **Redis**: 6.0+ (支持AOF+RDB混合持久化)

### PostgreSQL扩展要求
```sql
-- 监控数据库必需扩展
CREATE EXTENSION IF NOT EXISTS pg_partman;
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- 业务数据库必需扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
```

---

## 10. 研究成果总结

### 关键技术决策矩阵

| 研究主题 | 决策方案 | 核心优势 | 风险/限制 |
|---------|---------|---------|----------|
| **R1: TDengine集成** | WebSocket + Super Table + ZSTD压缩 | 5-10x性能提升,20:1压缩比 | 学习曲线,需WebSocket支持 |
| **R2: TimescaleDB配置** | 1天Chunk + 30天压缩 | 自动分区,查询性能好 | PostgreSQL依赖 |
| **R3: 多库事务** | SQLite Outbox队列 + 最终一致性 | 简单可靠,故障容错 | 非强一致性 |
| **R4: YAML架构** | PyYAML + Pydantic V2 | 类型安全,IDE支持 | 配置复杂度增加 |
| **R5: 数据源策略** | Akshare主 + Baostock/Tushare备 | 免费全面,多源冗余 | API稳定性依赖 |
| **R6: Redis持久化** | AOF+RDB混合 + 定时固化 | 最多丢1秒,性能好 | 需定时任务 |
| **R7: 监控数据库** | PostgreSQL + pg_partman + pg_cron | JSONB强大,自动化维护 | 需PostgreSQL专业知识 |
| **R8: Python类型** | 原生类型提示 + Pandera + mypy | 早期错误发现,DataFrame安全 | 开发时间增加10-15% |

### 宪法合规性验证

所有8个研究决策均已验证符合项目宪法7大核心原则:

✅ **I. 5层数据分类体系**: 研究成果明确支持23个数据子项的路由策略
✅ **II. 配置驱动设计**: YAML + Pydantic架构完全符合
✅ **III. 智能自动路由**: DataStorageStrategy映射逻辑已定义
✅ **IV. 多数据库协同**: 4种数据库职责明确,技术选型合理
✅ **V. 完整可观测性**: 独立监控数据库 + pg_partman自动化
✅ **VI. 统一访问接口**: MyStocksUnifiedManager类型安全封装
✅ **VII. 安全优先**: 环境变量 + .env隔离,Redis避开0号库

### 下一步行动

1. **Phase 1: Design & Contracts** (预计8-10小时)
   - 生成 `data-model.md` (23个实体schema定义)
   - 创建 `contracts/` 目录 (3个API契约文档)
   - 编写 `quickstart.md` (安装和快速开始指南)

2. **Phase 2: Tasks Generation** (预计2小时)
   - 运行 `/speckit.tasks` 生成依赖排序的任务清单
   - 验证任务覆盖所有功能需求

3. **Phase 3-4: Implementation** (预计40-60小时)
   - 按任务清单顺序实施
   - 每完成5个任务运行一次集成测试

---

**研究完成日期**: 2025-10-11
**研究总耗时**: 约7小时 (8个并行研究任务)
**下一阶段**: Phase 1 - Design & Contracts
