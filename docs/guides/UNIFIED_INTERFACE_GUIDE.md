# 统一接口抽象层使用指南

## 概述

统一接口抽象层为MyStocks项目提供了一致、智能、高效的数据访问能力。通过统一的接口设计，开发者可以透明地在PostgreSQL和TDengine之间切换，无需关心底层实现细节。

## 快速开始

### 1. 基础使用

```python
from src.data_access.unified_data_access_manager import UnifiedDataAccessManager, DataAccessConfig, DataAccessMode
from src.data_access.interfaces.i_data_access import DataQuery, QueryOperation

# 创建统一数据访问管理器
manager = UnifiedDataAccessManager(
    config=DataAccessConfig(
        mode=DataAccessMode.AUTO,  # 自动路由模式
        enable_query_optimization=True,  # 启用查询优化
        enable_caching=True,            # 启用缓存
        enable_metrics=True              # 启用指标收集
    )
)

# 初始化管理器
await manager.initialize()

# 执行查询 - 自动路由到最优数据库
query = DataQuery(
    operation=QueryOperation.SELECT,
    table_name="watchlist",
    filters={"user_id": 123},
    columns=["symbol", "name", "added_at"],
    limit=100
)

result = await manager.execute_query(query)
print(f"查询成功，返回 {len(result.data)} 条记录")
```

### 2. 保存数据

```python
from src.data_access.interfaces.i_data_access import DataRecord

# 创建数据记录
records = [
    DataRecord(
        table_name="stock_price",
        data={
            "symbol": "AAPL",
            "price": 150.25,
            "timestamp": datetime.now()
        }
    ),
    DataRecord(
        table_name="stock_price",
        data={
            "symbol": "GOOGL",
            "price": 2800.50,
            "timestamp": datetime.now()
        }
    )
]

# 保存数据 - 自动路由到合适数据库
result = await manager.save_data(records)
print(f"保存成功: {result.inserted_count} 条记录")
```

## 核心概念

### 1. DataQuery - 统一查询对象

DataQuery是统一接口的核心，用于描述数据访问操作：

```python
query = DataQuery(
    operation=QueryOperation.SELECT,        # 操作类型
    table_name="stock_ohlcv",              # 表名
    columns=["symbol", "price", "timestamp"],  # 查询列
    filters={                              # 过滤条件
        "symbol": "AAPL",
        "price > 100,
        "timestamp": "2024-01-01"
    },
    order_by=["timestamp DESC"],           # 排序
    limit=100,                             # 限制
    offset=0                               # 偏移
)
```

**操作类型**:
- `QueryOperation.SELECT` - 查询数据
- `QueryOperation.INSERT` - 插入数据
- `QueryOperation.UPDATE` - 更新数据
- `QueryOperation.DELETE` - 删除数据
- `QueryOperation.UPSERT` - 插入或更新
- `QueryOperation.BATCH_INSERT` - 批量插入

### 2. 智能路由

统一接口会根据查询特征自动选择最优数据库：

```python
# 时间序列数据自动路由到TDengine
time_series_query = DataQuery(
    operation=QueryOperation.SELECT,
    table_name="stock_minute_data"  # 包含时间特征，自动路由到TDengine
)

# 关系型数据自动路由到PostgreSQL
relational_query = DataQuery(
    operation=QueryOperation.SELECT,
    table_name="users",
    join_clauses=[{"table": "profiles", "on": "users.id = profiles.user_id"}]  # 包含JOIN，路由到PostgreSQL
)
```

**路由规则**:
- 时序数据 → TDengine
- 关系型查询 → PostgreSQL
- 高频写入 → TDengine
- 复杂事务 → PostgreSQL
- 批量操作 → 自动选择最优数据库

### 3. 查询优化

启用查询优化后，系统会自动优化查询性能：

```python
# 自动优化示例
query = DataQuery(
    operation=QueryOperation.SELECT,
    table_name="orders",
    join_clauses=[
        {"table": "users", "on": "orders.user_id = users.id"},
        {"table": "products", "on": "orders.product_id = products.id"}
    ],
    filters={"status": "completed"},
    limit=1000  # 会自动添加LIMIT优化
)

# 系统会自动应用优化：
# - JOIN重排 (PostgreSQL)
# - 标签过滤优化 (TDengine)
# - 索引提示
# - 谓词下推
# - 列裁剪
```

## 高级用法

### 1. 自定义路由规则

```python
from src.data_access.routers.query_router import get_global_router

router = get_global_router()

# 添加自定义路由规则
def custom_routing_rule(query: DataQuery) -> bool:
    """自定义路由规则：高频交易数据路由到专用数据库"""
    return (
        query.table_name == "trades" and
        query.operation == QueryOperation.BATCH_INSERT
    )

from src.data_access.postgresql_access import PostgreSQLDataAccess

# 注册自定义规则
router.add_routing_rule(
    rule=custom_routing_rule,
    target=PostgreSQLDataAccess()
)
```

### 2. 事务管理

```python
from src.data_access.interfaces.i_data_access import IsolationLevel

# 开始事务
transaction = await manager.begin_transaction(
    isolation_level=IsolationLevel.READ_COMMITTED
)

try:
    # 在事务中执行多个操作
    await manager.save_data(record1)
    await manager.update_data(criteria1, updates1)
    await manager.delete_data(criteria1)

    # 提交事务
    await manager.commit_transaction(transaction)

except Exception as e:
    # 回滚事务
    await manager.rollback_transaction(transaction)
    raise
```

### 3. 批量操作

```python
# 批量查询
queries = [
    DataQuery(operation=QueryOperation.SELECT, table_name="users"),
    DataQuery(operation=QueryOperation.SELECT, table_name="orders"),
    DataQuery(operation=QueryOperation.SELECT, table_name="products")
]

results = await manager.batch_fetch(queries)

# 批量保存
record_batches = [
    batch1,  # List[DataRecord]
    batch2,  # List[DataRecord]
    batch3   # List[DataRecord]
]

save_results = await manager.batch_save(record_batches)
```

### 4. 性能监控

```python
# 获取查询指标
metrics = manager.get_metrics()
print(f"总查询数: {metrics.query_count}")
print(f"平均执行时间: {metrics.total_execution_time/metrics.query_count:.3f}s")
print(f"缓存命中率: {metrics.cache_hits/(metrics.cache_hits+metrics.cache_misses):.1%}")

# 获取路由指标
routing_metrics = manager.get_routing_metrics()
print(f"数据库使用分布: {routing_metrics.database_usage}")

# 获取优化统计
opt_stats = manager.get_optimization_statistics()
print(f"优化规则应用: {opt_stats['total_optimizations']}")
print(f"平均性能提升: {opt_stats['average_improvement']:.1%}")
```

## 配置选项

### 1. 数据访问配置

```python
from src.data_access.unified_data_access_manager import DataAccessConfig, DataAccessMode

config = DataAccessConfig(
    # 访问模式
    mode=DataAccessMode.AUTO,
    # 或者使用特定模式
    # mode=DataAccessMode.POSTGRESQL_ONLY,
    # mode=DataAccessMode.TDENGINE_ONLY,

    # 功能开关
    enable_query_optimization=True,  # 启用查询优化
    enable_caching=True,              # 启用缓存
    enable_metrics=True,              # 启用指标收集
    failover_enabled=True,            # 启用故障转移

    # 性能参数
    max_connections_per_db=10,         # 每个数据库最大连接数
    query_timeout=30,                 # 查询超时时间(秒)
    retry_attempts=3,                  # 重试次数
    retry_delay=1.0,                   # 重试延迟(秒)

    # 健康检查
    health_check_interval=60           # 健康检查间隔(秒)
)
```

### 2. 访问模式说明

**DataAccessMode.AUTO** (推荐)
- 自动选择最优数据库
- 支持故障转移
- 性能最优

**DataAccessMode.POSTGRESQL_ONLY**
- 只使用PostgreSQL
- 适用于关系型数据主导的场景
- 支持完整ACID事务

**DataAccessMode.TDENGINE_ONLY**
- 只使用TDengine
- 适用于时序数据主导的场景
- 优秀的写入性能

**DataAccessMode.FAILOVER**
- 主备模式，故障时切换
- 提高可用性

**DataAccessMode.LOAD_BALANCE**
- 负载均衡模式
- 提高性能和资源利用率

## 最佳实践

### 1. 查询设计最佳实践

**使用合适的过滤条件**:
```python
# 好的做法 - 使用具体过滤条件
query = DataQuery(
    operation=QueryOperation.SELECT,
    table_name="stock_ohlcv",
    filters={
        "symbol": "AAPL",
        "timestamp": "2024-01-01",  # 具体日期
        "min_volume": 1000           # 具体数值
    }
)

# 避免 - 使用模糊或低选择性条件
# query = DataQuery(
#     operation=QueryOperation.SELECT,
#     table_name="stock_ohlcv",
#     filters={"symbol": "A%"}  # 低选择性
# )
```

**合理使用LIMIT**:
```python
# 好的做法 - 限制返回结果数量
query = DataQuery(
    operation=QueryOperation.SELECT,
    table_name="stock_ohlcv",
    limit=100  # 合理的LIMIT
)

# 注意：大数据集查询如果没有LIMIT可能会影响性能
```

### 2. 数据模型设计

**表名命名**:
- 时序数据: `*_minute_data`, `*_tick_data`, `*_ohlcv`
- 关系型数据: `users`, `orders`, `products`
- 配置数据: `settings`, `config`

**字段选择**:
```python
# 只查询需要的列，避免 `SELECT *`
query = DataQuery(
    operation=QueryOperation.SELECT,
    columns=["symbol", "price", "timestamp"],  # 只选择必要列
    table_name="stock_price"
)
```

### 3. 性能优化建议

**缓存使用**:
```python
# 启用缓存以提升重复查询性能
manager = UnifiedDataAccessManager(
    config=DataAccessConfig(enable_caching=True)
)

# 对于频繁访问的数据，考虑使用缓存
```

**批量操作**:
```python
# 使用批量操作提升性能
records = [DataRecord(...) for _ in range(1000)]
await manager.save_data(records)  # 批量插入
```

**事务优化**:
```python
# 避免长时间事务
# 好的做法：小事务，快速提交
await manager.begin_transaction()
await manager.save_data(records[:100])
await manager.commit_transaction()

# 避免的做法：大事务，长时间保持
```

## 错误处理

### 1. 常见错误类型

```python
try:
    result = await manager.execute_query(query)

except DatabaseConnectionError as e:
    # 数据库连接错误
    logger.error(f"数据库连接失败: {e}")
    # 可以重试或使用备用数据库

except DatabaseTimeoutError as e:
    # 查询超时
    logger.error(f"查询超时: {e}")
    # 考虑优化查询或增加超时时间

except ValidationError as e:
    # 数据验证错误
    logger.error(f"数据验证失败: {e}")
    # 检查数据格式和约束

except Exception as e:
    # 其他未预期的错误
    logger.error(f"查询执行失败: {e}")
    # 记录错误并向上传播
    raise
```

### 2. 重试机制

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def execute_with_retry(query: DataQuery):
    return await manager.execute_query(query)
```

## 迁移指南

### 1. 从旧接口迁移

**旧代码**:
```python
# 旧的方式 - 直接使用特定数据库
from src.data_access.postgresql_access import PostgreSQLDataAccess

pg_access = PostgreSQLDataAccess()
await pg_access.connect()

# SQL字符串查询
sql = "SELECT * FROM watchlist WHERE user_id = %s"
cursor = await pg_access.execute_query(sql, (user_id,))
results = cursor.fetchall()
```

**新代码**:
```python
# 新的方式 - 使用统一接口
manager = UnifiedDataAccessManager()
await manager.initialize()

# 统一查询对象
query = DataQuery(
    operation=QueryOperation.SELECT,
    table_name="watchlist",
    filters={"user_id": user_id}
)

result = await manager.execute_query(query)
results = result.data
```

### 2. 渐进式迁移策略

1. **阶段1**: 保持旧代码并行运行，新功能使用统一接口
2. **阶段2**: 逐步将现有功能迁移到统一接口
3. **阶段3**: 移除旧接口，完全使用统一接口

### 3. 兼容性检查

```python
# 检查旧代码依赖
def check_legacy_dependencies():
    import sys
    for name in dir(sys.modules):
        if 'postgresql_access' in name or 'tdengine_access' in name:
            print(f"发现旧接口依赖: {name}")
```

## 故障排查

### 1. 查询性能问题

```python
# 启用详细日志
import logging
logging.getLogger('src.data_access').setLevel(logging.DEBUG)

# 获取执行计划
plan = await manager.optimizer.analyze_query_plan(query, DatabaseType.POSTGRESQL)
print(f"查询计划: {plan}")

# 获取索引建议
index_suggestions = await manager.optimizer.suggest_indexes(query, DatabaseType.POSTGRESQL)
print(f"索引建议: {index_suggestions}")
```

### 2. 路由问题

```python
# 获取路由决策信息
decision = await manager.router._make_routing_decision(query)
print(f"路由决策: {decision.target_database}")
print(f"路由原因: {decision.reasoning}")
print(f"替代方案: {decision.alternative_options}")
```

### 3. 连接问题

```python
# 检查连接池状态
for db_type in [DatabaseType.POSTGRESQL, DatabaseType.TDENGINE]:
    if db_type in manager.adapters:
        for adapter in manager.adapters[db_type]:
            stats = await adapter.get_connection_pool_stats()
            print(f"{db_type.value}连接池: {stats}")
```

## 总结

统一接口抽象层提供了以下核心价值：

1. **简化开发**: 统一的API减少了学习成本和开发复杂度
2. **自动优化**: 智能路由和优化提升了查询性能
3. **高可用性**: 故障转移和负载均衡提高了系统可用性
4. **可扩展性**: 易于添加新数据库类型和功能
5. **可观测性**: 完整的监控和指标体系

通过遵循本指南的最佳实践，您可以充分利用统一接口抽象层的所有功能，构建高性能、高可用的数据访问应用。
