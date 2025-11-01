# 核心功能

**类别**: core
**模块数**: 32
**类数**: 31
**函数数**: 262
**代码行数**: 10461

## 概述


核心功能模块实现系统的主要业务逻辑和数据编排。这些模块是系统的核心，
负责统一数据访问、数据分类路由、以及系统初始化和配置。

**关键特性**:
- 系统主入口点和编排逻辑
- 统一数据访问接口（Unified Manager）
- 5 层数据分类系统实现
- 智能数据路由策略
- 多数据库协调管理

**设计模式**: Manager Pattern, Strategy Pattern, Facade Pattern


## 模块列表

### core

**文件**: `core.py`

**说明**:

MyStocks 量化交易数据管理系统 - 重构版
完全基于原始设计理念实现的配置驱动、自动化管理系统

设计理念：
1. 配置驱动 - 通过YAML配置文件管理所有表结构
2. 自动化管理 - 避免人工手工管理数据库和表
3. 完整监控 - 专门的监控数据库记录所有操作
4. 数据分类 - 基于数据特性的5大分类体系
5. 业务分离 - 监控数据库与业务数据库完全分离

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-09-21

#### 类

##### `DataClassification`

数据分类体系 - 基于原始设计的5大分类

**继承**: `Enum`

##### `DatabaseTarget`

目标数据库类型 - 基于数据特性选择

**继承**: `Enum`

##### `DeduplicationStrategy`

数据去重策略 - 智能去重决策体系

**继承**: `Enum`

##### `DataStorageStrategy`

数据存储策略映射 - 实现自动路由

**方法**:

- `get_target_database(cls, classification: DataClassification)` → `DatabaseTarget` [core.py:134]
  - 根据数据分类获取目标数据库
- `get_database_name(cls, classification: DataClassification)` → `str` [core.py:139]
  - 根据数据分类获取数据库名称
- `get_smart_deduplication_strategy(cls, classification: DataClassification, data_characteristics: Dict = None)` → `DeduplicationStrategy` [core.py:158]
  - 智能决策去重策略 - 基于用户提供的判断标准

##### `ConfigDrivenTableManager`

配置驱动的表管理器 - 核心自动化管理组件

**方法**:

- `__init__(self, config_file: str = "table_config.yaml")` → `None` [core.py:220]
  - 初始化配置驱动的表管理器
- `load_configuration(self)` → `Dict` [core.py:234]
  - 加载YAML配置文件
- `create_default_config(self)` → `None` [core.py:251]
  - 创建默认配置文件
- `_generate_default_config(self)` → `Dict` [core.py:261]
  - 生成默认配置结构
- `_generate_default_tables(self)` → `List[Dict]` [core.py:328]
  - 生成默认表配置
- `auto_create_all_tables(self)` → `Dict[(str, bool)]` [core.py:470]
  - 根据配置文件自动创建所有表
- `_create_table_from_config(self, table_config: Dict)` → `bool` [core.py:508]
  - 根据配置创建单个表
- `_convert_column_config(self, column_configs: List[Dict])` → `List[Dict]` [core.py:566]
  - 转换列配置格式
- `_create_indexes(self, table_config: Dict, db_type: DatabaseType)` → `None` [core.py:598]
  - 创建表索引
- `validate_all_table_structures(self)` → `Dict[(str, Any)]` [core.py:614]
  - 验证所有表结构
- `_validate_single_table_structure(self, table_config: Dict)` → `bool` [core.py:659]
  - 验证单个表结构
- `get_table_config_by_classification(self, classification: DataClassification)` → `Optional[Dict]` [core.py:691]
  - 根据数据分类获取表配置
- `cleanup(self)` → `None` [core.py:710]
  - 清理资源

---

### core.__init__

**文件**: `core/__init__.py`

---

### core.data_classification

**文件**: `core/data_classification.py`

**说明**:

数据分类枚举模块

定义MyStocks系统的5层数据分类体系(23个子项)和数据库类型枚举。
这是整个系统架构的基础,所有数据路由决策都基于这些枚举。

创建日期: 2025-10-11
版本: 1.0.0

#### 类

##### `DataClassification`

数据分类枚举 - 23个子项完整定义

基于宪法第I节: 5层数据分类体系 (不可协商)
所有数据必须归属以下23个分类之一

**继承**: `str`, `Enum`

**方法**:

- `get_all_classifications(cls)` → `List[str]` [core/data_classification.py:141]
  - 返回所有23个数据分类的列表
- `get_market_data_classifications(cls)` → `List[str]` [core/data_classification.py:146]
  - 返回市场数据分类 (6项)
- `get_reference_data_classifications(cls)` → `List[str]` [core/data_classification.py:158]
  - 返回参考数据分类 (9项)
- `get_derived_data_classifications(cls)` → `List[str]` [core/data_classification.py:173]
  - 返回衍生数据分类 (6项)
- `get_transaction_data_classifications(cls)` → `List[str]` [core/data_classification.py:185]
  - 返回交易数据分类 (7项)
- `get_metadata_classifications(cls)` → `List[str]` [core/data_classification.py:198]
  - 返回元数据分类 (6项)

##### `DatabaseTarget`

数据库类型枚举

定义系统支持的4种数据库类型,每种数据库针对特定数据特性优化

**继承**: `str`, `Enum`

**方法**:

- `get_all_targets(cls)` → `List[str]` [core/data_classification.py:230]
  - 返回所有数据库类型列表

---

### data_access

**文件**: `data_access.py`

**说明**:

MyStocks 量化交易数据管理系统 - 统一数据访问层
完全按照原始设计理念实现的5大数据分类体系和自动化路由

设计理念：
1. 5大数据分类：市场数据、参考数据、衍生数据、交易数据、元数据
2. 自动路由：根据数据特性自动选择最适合的数据库
3. TDengine为高频数据核心：专门处理Tick和分钟级数据
4. 监控集成：所有操作自动记录到监控数据库
5. 配置驱动：表结构和访问模式完全由配置文件管理

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-09-21

#### 类

##### `IDataAccessLayer`

数据访问层接口

**继承**: `ABC`

**方法**:

- `save_data(self, data: pd.DataFrame, classification: DataClassification, table_name: str = None, **kwargs)` → `bool` [data_access.py:46]
  - 保存数据
- `load_data(self, classification: DataClassification, table_name: str = None, filters: Dict = None, **kwargs)` → `pd.DataFrame` [data_access.py:52]
  - 加载数据
- `update_data(self, data: pd.DataFrame, classification: DataClassification, table_name: str = None, key_columns: List[str] = None, **kwargs)` → `bool` [data_access.py:58]
  - 更新数据
- `delete_data(self, classification: DataClassification, table_name: str = None, filters: Dict = None, **kwargs)` → `bool` [data_access.py:64]
  - 删除数据

##### `TDengineDataAccess`

TDengine数据访问器 - 高频时序数据专用

**继承**: `IDataAccessLayer`

**方法**:

- `__init__(self, monitoring_db: MonitoringDatabase)` → `None` [data_access.py:72]
  - 初始化TDengine数据访问器
- `save_data(self, data: pd.DataFrame, classification: DataClassification, table_name: str = None, **kwargs)` → `bool` [data_access.py:84]
  - 保存时序数据到TDengine，支持去重策略
- `load_data(self, classification: DataClassification, table_name: str = None, filters: Dict = None, **kwargs)` → `pd.DataFrame` [data_access.py:158]
  - 从TDengine加载时序数据
- `update_data(self, data: pd.DataFrame, classification: DataClassification, table_name: str = None, key_columns: List[str] = None, **kwargs)` → `bool` [data_access.py:205]
  - TDengine通常不支持更新操作，使用插入替代
- `delete_data(self, classification: DataClassification, table_name: str = None, filters: Dict = None, **kwargs)` → `bool` [data_access.py:211]
  - TDengine删除数据（谨慎使用）
- `_get_default_table_name(self, classification: DataClassification)` → `str` [data_access.py:217]
  - 根据数据分类获取默认表名
- `_apply_tdengine_deduplication(self, data: pd.DataFrame, table_name: str, strategy, classification: DataClassification)` → `Optional[pd.DataFrame]` [data_access.py:226]
  - 应用TDengine特定的去重策略
- `_handle_tdengine_latest_wins(self, data: pd.DataFrame, table_name: str, classification: DataClassification)` → `pd.DataFrame` [data_access.py:259]
  - TDengine最新覆盖策略：基于时间戳去重，保留最新记录
- `_handle_tdengine_first_wins(self, data: pd.DataFrame, table_name: str, classification: DataClassification)` → `pd.DataFrame` [data_access.py:292]
  - TDengine首次保留策略：查询已存在的数据，过滤重复
- `_handle_tdengine_merge(self, data: pd.DataFrame, table_name: str, classification: DataClassification)` → `pd.DataFrame` [data_access.py:349]
  - TDengine合并策略：时序数据通常使用最新覆盖
- `_handle_tdengine_reject(self, data: pd.DataFrame, table_name: str, classification: DataClassification)` → `Optional[pd.DataFrame]` [data_access.py:355]
  - TDengine拒绝重复策略：检查重复并拒绝
- `_preprocess_timeseries_data(self, data: pd.DataFrame, classification: DataClassification)` → `pd.DataFrame` [data_access.py:382]
  - 预处理时序数据
- `_postprocess_timeseries_data(self, data: pd.DataFrame, classification: DataClassification)` → `pd.DataFrame` [data_access.py:409]
  - 后处理时序数据
- `_insert_tick_data(self, cursor, data: pd.DataFrame, table_name: str)` → `bool` [data_access.py:422]
  - 插入Tick数据
- `_insert_minute_kline(self, cursor, data: pd.DataFrame, table_name: str)` → `bool` [data_access.py:451]
  - 插入分钟K线数据
- `_insert_generic_timeseries(self, cursor, data: pd.DataFrame, table_name: str)` → `bool` [data_access.py:483]
  - 插入通用时序数据
- `_build_timeseries_query(self, classification: DataClassification, table_name: str, filters: Dict = None, **kwargs)` → `str` [data_access.py:502]
  - 构建时序数据查询语句

##### `PostgreSQLDataAccess`

PostgreSQL数据访问器 - 历史数据仓库和分析

**继承**: `IDataAccessLayer`

**方法**:

- `__init__(self, monitoring_db: MonitoringDatabase)` → `None` [data_access.py:550]
  - 初始化PostgreSQL数据访问器
- `save_data(self, data: pd.DataFrame, classification: DataClassification, table_name: str = None, **kwargs)` → `bool` [data_access.py:562]
  - 保存数据到PostgreSQL
- `load_data(self, classification: DataClassification, table_name: str = None, filters: Dict = None, **kwargs)` → `pd.DataFrame` [data_access.py:618]
  - 从PostgreSQL加载数据
- `update_data(self, data: pd.DataFrame, classification: DataClassification, table_name: str = None, key_columns: List[str] = None, **kwargs)` → `bool` [data_access.py:665]
  - 更新PostgreSQL数据
- `delete_data(self, classification: DataClassification, table_name: str = None, filters: Dict = None, **kwargs)` → `bool` [data_access.py:716]
  - 删除PostgreSQL数据
- `_get_default_table_name(self, classification: DataClassification)` → `str` [data_access.py:769]
  - 根据数据分类获取默认表名
- `_get_default_key_columns(self, classification: DataClassification)` → `List[str]` [data_access.py:784]
  - 根据数据分类获取默认主键列
- `_preprocess_analytical_data(self, data: pd.DataFrame, classification: DataClassification)` → `pd.DataFrame` [data_access.py:800]
  - 预处理分析数据
- `_get_postgresql_engine(self, database_name: str)` → `None` [data_access.py:828]
  - 获取PostgreSQL SQLAlchemy引擎
- `_upsert_data_with_engine(self, data: pd.DataFrame, table_name: str, engine, classification: DataClassification)` → `None` [data_access.py:845]
  - 使用SQLAlchemy引擎执行UPSERT操作
- `_postprocess_analytical_data(self, data: pd.DataFrame, classification: DataClassification)` → `pd.DataFrame` [data_access.py:868]
  - 后处理分析数据
- `_upsert_data(self, data: pd.DataFrame, table_name: str, conn, classification: DataClassification)` → `None` [data_access.py:882]
  - PostgreSQL Upsert操作 - 使用ON CONFLICT实现
- `_execute_update(self, cursor, data: pd.DataFrame, table_name: str, key_columns: List[str])` → `bool` [data_access.py:938]
  - 执行更新操作
- `_build_analytical_query(self, classification: DataClassification, table_name: str, filters: Dict = None, **kwargs)` → `str` [data_access.py:974]
  - 构建分析数据查询语句
- `_build_delete_query(self, table_name: str, filters: Dict)` → `str` [data_access.py:1032]
  - 构建删除查询语句

##### `MySQLDataAccess`

MySQL数据访问器 - 元数据与参考数据仓库

**继承**: `IDataAccessLayer`

**方法**:

- `__init__(self, monitoring_db: MonitoringDatabase)` → `None` [data_access.py:1051]
  - 初始化MySQL数据访问器
- `save_data(self, data: pd.DataFrame, classification: DataClassification, table_name: str = None, **kwargs)` → `bool` [data_access.py:1063]
  - 保存数据到MySQL，支持UPSERT操作
- `load_data(self, classification: DataClassification, table_name: str = None, filters: Dict = None, **kwargs)` → `pd.DataFrame` [data_access.py:1102]
  - 从MySQL加载数据
- `update_data(self, data: pd.DataFrame, classification: DataClassification, table_name: str = None, key_columns: List[str] = None, **kwargs)` → `bool` [data_access.py:1127]
  - 更新MySQL数据
- `delete_data(self, classification: DataClassification, table_name: str = None, filters: Dict = None, **kwargs)` → `bool` [data_access.py:1132]
  - 删除MySQL数据
- `_get_default_table_name(self, classification: DataClassification)` → `str` [data_access.py:1138]
  - 根据数据分类获取默认表名
- `_mysql_upsert_data(self, data: pd.DataFrame, table_name: str, conn, classification: DataClassification)` → `int` [data_access.py:1152]
  - MySQL UPSERT操作 - 使用ON DUPLICATE KEY UPDATE实现
- `_get_mysql_key_columns(self, classification: DataClassification)` → `List[str]` [data_access.py:1228]
  - 根据数据分类获取MySQL主键列
- `_preprocess_reference_data(self, data: pd.DataFrame, classification: DataClassification)` → `pd.DataFrame` [data_access.py:1242]
  - 预处理参考数据
- `_build_reference_query(self, classification: DataClassification, table_name: str, filters: Dict = None, **kwargs)` → `str` [data_access.py:1254]
  - 构建参考数据查询语句

##### `RedisDataAccess`

Redis数据访问器 - 实时状态中心

**方法**:

- `__init__(self, monitoring_db: MonitoringDatabase)` → `None` [data_access.py:1288]
  - 初始化Redis数据访问器
- `_init_redis_connection(self)` → `None` [data_access.py:1300]
  - 初始化Redis连接
- `save_realtime_data(self, classification: DataClassification, key: str, data: Union[(Dict, pd.DataFrame)], expire: int = 300)` → `bool` [data_access.py:1319]
  - 保存实时数据到Redis
- `load_realtime_data(self, classification: DataClassification, key: str)` → `Optional[Any]` [data_access.py:1345]
  - 从Redis加载实时数据
- `cache_dataframe(self, key: str, df: pd.DataFrame, expire: int = 3600)` → `bool` [data_access.py:1377]
  - 缓存DataFrame到Redis

---

### data_access.__init__

**文件**: `data_access/__init__.py`

**说明**:

数据访问层模块

提供4种数据库的统一访问接口:
- TDengine: 高频时序数据
- PostgreSQL: 历史分析数据
- MySQL: 参考数据和元数据
- Redis: 实时热数据

创建日期: 2025-10-11
版本: 1.0.0

---

### data_access.mysql_access

**文件**: `data_access/mysql_access.py`

**说明**:

MySQL数据访问层

封装MySQL/MariaDB的所有CRUD操作。
专门处理参考数据和元数据(股票信息/交易日历/系统配置)。

创建日期: 2025-10-11
版本: 1.0.0

#### 类

##### `MySQLDataAccess`

MySQL/MariaDB数据访问类

提供参考数据和元数据的存储和查询接口:
- 表管理(CREATE/ALTER)
- 批量写入(executemany优化)
- ACID事务支持
- 复杂JOIN查询
- 索引管理

**方法**:

- `__init__(self)` → `None` [data_access/mysql_access.py:31]
  - 初始化MySQL连接
- `_get_connection(self)` → `None` [data_access/mysql_access.py:36]
  - 获取MySQL连接(懒加载)
- `_reconnect_if_needed(self)` → `None` [data_access/mysql_access.py:42]
  - 检查连接并在需要时重连
- `create_table(self, table_name: str, schema: Dict[(str, str)], primary_key: Optional[str] = None)` → `None` [data_access/mysql_access.py:51]
  - 创建表
- `create_index(self, table_name: str, index_name: str, columns: List[str], unique: bool = False)` → `None` [data_access/mysql_access.py:94]
  - 创建索引
- `insert_dataframe(self, table_name: str, df: pd.DataFrame, batch_size: int = 1000)` → `int` [data_access/mysql_access.py:130]
  - 批量插入DataFrame数据
- `upsert_dataframe(self, table_name: str, df: pd.DataFrame, update_columns: Optional[List[str]] = None, batch_size: int = 1000)` → `int` [data_access/mysql_access.py:184]
  - 批量Upsert (INSERT ... ON DUPLICATE KEY UPDATE)
- `query(self, table_name: str, columns: Optional[List[str]] = None, where: Optional[str] = None, order_by: Optional[str] = None, limit: Optional[int] = None)` → `pd.DataFrame` [data_access/mysql_access.py:250]
  - 通用查询
- `execute_sql(self, sql: str, params: Optional[Tuple] = None, fetch: bool = True)` → `Optional[pd.DataFrame]` [data_access/mysql_access.py:300]
  - 执行自定义SQL
- `delete(self, table_name: str, where: str)` → `int` [data_access/mysql_access.py:345]
  - 删除数据
- `get_table_info(self, table_name: str)` → `Dict[(str, Any)]` [data_access/mysql_access.py:378]
  - 获取表信息
- `close(self)` → `None` [data_access/mysql_access.py:419]
  - 关闭连接

---

### data_access.postgresql_access

**文件**: `data_access/postgresql_access.py`

**说明**:

PostgreSQL数据访问层

封装PostgreSQL+TimescaleDB的所有CRUD操作。
专门处理历史分析数据和衍生计算结果(日线/技术指标/回测结果)。

创建日期: 2025-10-11
版本: 1.0.0

#### 类

##### `PostgreSQLDataAccess`

PostgreSQL+TimescaleDB数据访问类

提供历史分析数据的存储和查询接口:
- 时序表(Hypertable)管理
- 批量写入(execute_values优化)
- 复杂时间范围查询
- JOIN查询支持
- 聚合和窗口函数

**方法**:

- `__init__(self)` → `None` [data_access/postgresql_access.py:32]
  - 初始化PostgreSQL连接池
- `_get_connection(self)` → `None` [data_access/postgresql_access.py:37]
  - 从连接池获取连接
- `_return_connection(self, conn)` → `None` [data_access/postgresql_access.py:43]
  - 归还连接到连接池
- `create_table(self, table_name: str, schema: Dict[(str, str)], primary_key: Optional[str] = None)` → `None` [data_access/postgresql_access.py:48]
  - 创建普通表
- `create_hypertable(self, table_name: str, time_column: str = "time", chunk_interval: str = "7 days")` → `None` [data_access/postgresql_access.py:94]
  - 将表转换为TimescaleDB时序表(Hypertable)
- `insert_dataframe(self, table_name: str, df: pd.DataFrame)` → `int` [data_access/postgresql_access.py:132]
  - 批量插入DataFrame数据 (使用execute_values优化)
- `upsert_dataframe(self, table_name: str, df: pd.DataFrame, conflict_columns: List[str], update_columns: Optional[List[str]] = None)` → `int` [data_access/postgresql_access.py:183]
  - 批量Upsert (INSERT ... ON CONFLICT UPDATE)
- `query(self, table_name: str, columns: Optional[List[str]] = None, where: Optional[str] = None, order_by: Optional[str] = None, limit: Optional[int] = None)` → `pd.DataFrame` [data_access/postgresql_access.py:251]
  - 通用查询
- `query_by_time_range(self, table_name: str, time_column: str, start_time: datetime, end_time: datetime, columns: Optional[List[str]] = None, filters: Optional[str] = None)` → `pd.DataFrame` [data_access/postgresql_access.py:303]
  - 按时间范围查询
- `execute_sql(self, sql: str, params: Optional[Tuple] = None)` → `pd.DataFrame` [data_access/postgresql_access.py:333]
  - 执行自定义SQL查询
- `delete(self, table_name: str, where: str)` → `int` [data_access/postgresql_access.py:368]
  - 删除数据
- `get_table_stats(self, table_name: str)` → `Dict[(str, Any)]` [data_access/postgresql_access.py:403]
  - 获取表统计信息
- `close_all(self)` → `None` [data_access/postgresql_access.py:439]
  - 关闭所有连接

---

### data_access.redis_access

**文件**: `data_access/redis_access.py`

**说明**:

Redis数据访问层

封装Redis的所有操作。
专门处理实时热数据(实时持仓/实时账户/订单队列)。

创建日期: 2025-10-11
版本: 1.0.0

#### 类

##### `RedisDataAccess`

Redis数据访问类

提供实时热数据的存储和查询接口:
- String操作 (简单键值对)
- Hash操作 (实时持仓/账户)
- List操作 (订单队列)
- Set操作 (标的集合)
- SortedSet操作 (排序队列)
- TTL过期管理

**方法**:

- `__init__(self)` → `None` [data_access/redis_access.py:32]
  - 初始化Redis连接
- `_get_connection(self)` → `None` [data_access/redis_access.py:37]
  - 获取Redis连接(懒加载)
- `set(self, key: str, value: Any, ttl: Optional[int] = None)` → `None` [data_access/redis_access.py:45]
  - 设置键值对
- `get(self, key: str)` → `Optional[Any]` [data_access/redis_access.py:68]
  - 获取键值
- `delete(self, *keys: str)` → `int` [data_access/redis_access.py:93]
  - 删除键
- `exists(self, key: str)` → `bool` [data_access/redis_access.py:109]
  - 检查键是否存在
- `expire(self, key: str, ttl: int)` → `bool` [data_access/redis_access.py:114]
  - 设置键的过期时间
- `hset(self, key: str, field: str, value: Any)` → `None` [data_access/redis_access.py:130]
  - 设置Hash字段
- `hget(self, key: str, field: str)` → `Optional[Any]` [data_access/redis_access.py:150]
  - 获取Hash字段值
- `hgetall(self, key: str)` → `Dict[(str, Any)]` [data_access/redis_access.py:172]
  - 获取Hash所有字段
- `hmset(self, key: str, mapping: Dict[(str, Any)])` → `None` [data_access/redis_access.py:199]
  - 批量设置Hash字段
- `hdel(self, key: str, *fields: str)` → `int` [data_access/redis_access.py:226]
  - 删除Hash字段
- `lpush(self, key: str, *values: Any)` → `int` [data_access/redis_access.py:233]
  - 从左侧推入列表
- `rpush(self, key: str, *values: Any)` → `int` [data_access/redis_access.py:259]
  - 从右侧推入列表
- `lpop(self, key: str)` → `Optional[Any]` [data_access/redis_access.py:272]
  - 从左侧弹出元素
- `rpop(self, key: str)` → `Optional[Any]` [data_access/redis_access.py:285]
  - 从右侧弹出元素
- `lrange(self, key: str, start: int = 0, end: int = ...)` → `List[Any]` [data_access/redis_access.py:298]
  - 获取列表范围元素
- `llen(self, key: str)` → `int` [data_access/redis_access.py:327]
  - 获取列表长度
- `sadd(self, key: str, *members: Any)` → `int` [data_access/redis_access.py:334]
  - 添加集合成员
- `smembers(self, key: str)` → `set` [data_access/redis_access.py:359]
  - 获取集合所有成员
- `srem(self, key: str, *members: Any)` → `int` [data_access/redis_access.py:373]
  - 删除集合成员
- `sismember(self, key: str, member: Any)` → `bool` [data_access/redis_access.py:386]
  - 检查成员是否在集合中
- `mget(self, *keys: str)` → `List[Optional[Any]]` [data_access/redis_access.py:397]
  - 批量获取键值
- `mset(self, mapping: Dict[(str, Any)])` → `None` [data_access/redis_access.py:414]
  - 批量设置键值
- `keys(self, pattern: str = "*")` → `List[str]` [data_access/redis_access.py:440]
  - 查找匹配模式的键
- `flushdb(self)` → `None` [data_access/redis_access.py:457]
  - 清空当前数据库 (谨慎使用!)
- `info(self)` → `Dict[(str, Any)]` [data_access/redis_access.py:462]
  - 获取Redis服务器信息
- `close(self)` → `None` [data_access/redis_access.py:467]
  - 关闭连接

---

### data_access.tdengine_access

**文件**: `data_access/tdengine_access.py`

**说明**:

TDengine数据访问层

封装TDengine WebSocket连接的所有CRUD操作。
专门处理高频时序数据(Tick/分钟线/盘口快照)的存储和查询。

创建日期: 2025-10-11
版本: 1.0.0

#### 类

##### `TDengineDataAccess`

TDengine数据访问类

提供高频时序数据的存储和查询接口:
- 超表(STable)管理
- 批量写入(自动按timestamp分区)
- 时间范围查询
- 聚合查询(OHLC等)

**方法**:

- `__init__(self)` → `None` [data_access/tdengine_access.py:29]
  - 初始化TDengine连接
- `_get_connection(self)` → `None` [data_access/tdengine_access.py:34]
  - 获取TDengine连接(懒加载)
- `create_stable(self, stable_name: str, schema: Dict[(str, str)], tags: Dict[(str, str)])` → `None` [data_access/tdengine_access.py:40]
  - 创建超表(STable)
- `create_table(self, table_name: str, stable_name: str, tag_values: Dict[(str, Any)])` → `None` [data_access/tdengine_access.py:72]
  - 创建子表(基于超表)
- `insert_dataframe(self, table_name: str, df: pd.DataFrame, timestamp_col: str = "ts")` → `None` [data_access/tdengine_access.py:100]
  - 批量插入DataFrame数据
- `query_by_time_range(self, table_name: str, start_time: datetime, end_time: datetime, columns: Optional[List[str]] = None, limit: Optional[int] = None)` → `pd.DataFrame` [data_access/tdengine_access.py:167]
  - 按时间范围查询数据
- `query_latest(self, table_name: str, limit: int = 100)` → `pd.DataFrame` [data_access/tdengine_access.py:232]
  - 查询最新N条数据
- `aggregate_to_kline(self, table_name: str, start_time: datetime, end_time: datetime, interval: str = "1m", price_col: str = "price", volume_col: str = "volume")` → `pd.DataFrame` [data_access/tdengine_access.py:267]
  - 聚合为K线数据
- `delete_by_time_range(self, table_name: str, start_time: datetime, end_time: datetime)` → `int` [data_access/tdengine_access.py:329]
  - 删除时间范围内的数据
- `get_table_info(self, table_name: str)` → `Dict[(str, Any)]` [data_access/tdengine_access.py:361]
  - 获取表信息(行数、时间范围、磁盘占用)
- `close(self)` → `None` [data_access/tdengine_access.py:398]
  - 关闭连接

---

### data_sources.tdx_importer

**文件**: `data_sources/tdx_importer.py`

**说明**:

TDX数据增量导入器 (TDX Incremental Importer)

功能说明:
- 从TDX本地文件增量导入数据到MyStocks数据库
- 通过5-tier数据分类自动路由到对应数据库
- 支持断点续传和增量更新
- 批量处理优化性能

数据路由策略:
- 日线/分钟线数据 → TDengine (时序数据库)
- 导入记录元数据 → MySQL (元数据库)

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 类

##### `ImportJob`

导入任务配置

**方法**:

- `__post_init__(self)` → `None` [data_sources/tdx_importer.py:48]

##### `TdxImporter`

TDX数据增量导入器

功能:
- 自动扫描TDX数据文件
- 增量导入到数据库
- 支持断点续传
- 进度跟踪和日志

**方法**:

- `__init__(self, unified_manager=None, data_path: str = None)` → `None` [data_sources/tdx_importer.py:64]
  - 初始化TDX导入器
- `import_market_daily(self, market: str = "sh", start_date: Optional[date] = None, end_date: Optional[date] = None, symbols: Optional[List[str]] = None, batch_size: int = 100)` → `Dict` [data_sources/tdx_importer.py:93]
  - 导入指定市场的日线数据
- `import_incremental(self, market: str = "sh", lookback_days: int = 7)` → `Dict` [data_sources/tdx_importer.py:172]
  - 增量导入（只导入最近N天的数据）
- `_save_to_database(self, symbol: str, data: pd.DataFrame, data_type: str, market: str)` → `None` [data_sources/tdx_importer.py:196]
  - 保存数据到数据库（通过5-tier数据分类路由）
- `get_import_progress(self, market: str)` → `Dict` [data_sources/tdx_importer.py:243]
  - 获取导入进度
- `_print_summary(self)` → `None` [data_sources/tdx_importer.py:280]
  - 打印导入统计摘要

---

### main

**文件**: `main.py`

**说明**:

主程序入口
演示统一数据接口的使用

#### 函数

##### `main()` → `None`

**位置**: [main.py:15]

主函数：演示统一数据接口的使用

---

### manager.unified_data_manager

**文件**: `manager/unified_data_manager.py`

**说明**:

统一数据管理器
作为系统的门户，提供简洁的API

作用：
- 统一数据管理器，系统的核心组件
- 作为系统的门户，提供简洁的API
- 协调不同数据源的使用
- 管理数据源实例的生命周期

功能：
- 提供数据源切换和比较功能
- 处理日期和股票代码的标准化
- 简化数据获取的过程
- 提供额外的功能，如数据源比较、代码和日期格式化等

#### 类

##### `UnifiedDataManager`

统一数据管理器：协调数据获取，提供高级功能

**方法**:

- `__init__(self)` → `None` [manager/unified_data_manager.py:35]
  - 初始化统一数据管理器
- `set_default_source(self, source_type: str)` → `None` [manager/unified_data_manager.py:40]
  - 设置默认数据源
- `get_source(self, source_type: Optional[str] = None)` → `IDataSource` [manager/unified_data_manager.py:50]
  - 获取数据源实例
- `get_stock_daily(self, symbol: str, start_date: Union[(str, datetime.date)], end_date: Union[(str, datetime.date, None)] = None, days: Optional[int] = None, source_type: Optional[str] = None)` → `pd.DataFrame` [manager/unified_data_manager.py:69]
  - 获取股票日线数据（统一接口）
- `get_index_daily(self, symbol: str, start_date: Union[(str, datetime.date)], end_date: Union[(str, datetime.date, None)] = None, days: Optional[int] = None, source_type: Optional[str] = None)` → `pd.DataFrame` [manager/unified_data_manager.py:96]
  - 获取指数日线数据（统一接口）
- `get_stock_basic(self, symbol: str, source_type: Optional[str] = None)` → `Dict` [manager/unified_data_manager.py:123]
  - 获取股票基本信息（统一接口）
- `get_index_components(self, symbol: str, source_type: Optional[str] = None)` → `List[str]` [manager/unified_data_manager.py:141]
  - 获取指数成分股（统一接口）
- `compare_data_sources(self, symbol: str, start_date: str, end_date: str)` → `None` [manager/unified_data_manager.py:159]
  - 比较两个数据源的数据
- `get_financial_data(self, symbol: str, period: str = "annual", source_type: Optional[str] = None)` → `pd.DataFrame` [manager/unified_data_manager.py:192]
  - 获取股票财务数据（统一接口）

---

### test_unified_manager

**文件**: `test_unified_manager.py`

**说明**:

统一数据管理器测试脚本
测试UnifiedDataManager使用Customer数据源的功能

#### 函数

##### `test_unified_data_manager_with_customer_source()` → `None`

**位置**: [test_unified_manager.py:16]

测试UnifiedDataManager使用Customer数据源

---

### test_unified_manager_financial

**文件**: `test_unified_manager_financial.py`

#### 函数

##### `test_unified_manager_with_financial()` → `None`

**位置**: [test_unified_manager_financial.py:9]

测试UnifiedDataManager使用FinancialDataSource

---

### test_us2_acceptance

**文件**: `test_us2_acceptance.py`

**说明**:

US2验收测试 - 配置驱动表结构管理

验证US2的完整功能:
- T024: 配置验证测试
- T025: US2安全模式验收测试

验收标准:
1. 可通过YAML配置自动创建所有表
2. 安全模式正确执行（添加列自动，删除/修改需确认）
3. 配置错误有明确提示

创建日期: 2025-10-12

#### 函数

##### `test_config_validation()` → `None`

**位置**: [test_us2_acceptance.py:35]

T024: 配置验证测试

##### `test_safe_mode()` → `None`

**位置**: [test_us2_acceptance.py:159]

T025: US2安全模式验收测试

##### `main()` → `None`

**位置**: [test_us2_acceptance.py:273]

主测试函数

---

### tests.integration.test_mysql_redis_integration

**文件**: `tests/integration/test_mysql_redis_integration.py`

**说明**:

MySQL/Redis集成测试

测试MySQL和Redis数据访问层的实际读写操作和性能。

创建日期: 2025-10-11
版本: 1.0.0

---

### tests.integration.test_operation_logging

**文件**: `tests/integration/test_operation_logging.py`

**说明**:

操作日志集成测试 (T032)

测试统一管理器的所有操作是否正确记录到监控数据库。

验证点:
1. SAVE操作 → 操作日志记录
2. LOAD操作 → 操作日志记录
3. 失败操作 → 失败日志记录
4. 操作统计 → 正确计数

创建日期: 2025-10-12

#### 类

##### `TestOperationLogging`

操作日志集成测试

**继承**: `unittest.TestCase`

**方法**:

- `setUpClass(cls)` → `None` [tests/integration/test_operation_logging.py:34]
  - 测试类初始化
- `test_01_save_operation_logging(self)` → `None` [tests/integration/test_operation_logging.py:47]
  - 测试1: SAVE操作日志记录
- `test_02_load_operation_logging(self)` → `None` [tests/integration/test_operation_logging.py:76]
  - 测试2: LOAD操作日志记录
- `test_03_failed_operation_logging(self)` → `None` [tests/integration/test_operation_logging.py:96]
  - 测试3: 失败操作日志记录
- `test_04_monitoring_statistics(self)` → `None` [tests/integration/test_operation_logging.py:120]
  - 测试4: 监控统计信息
- `test_05_batch_operation_logging(self)` → `None` [tests/integration/test_operation_logging.py:140]
  - 测试5: 批量操作日志记录
- `tearDownClass(cls)` → `None` [tests/integration/test_operation_logging.py:169]
  - 清理测试环境

---

### tests.integration.test_postgresql_integration

**文件**: `tests/integration/test_postgresql_integration.py`

**说明**:

PostgreSQL集成测试

测试PostgreSQL数据访问层的实际读写操作和性能。

创建日期: 2025-10-11
版本: 1.0.0

---

### tests.integration.test_tdengine_integration

**文件**: `tests/integration/test_tdengine_integration.py`

**说明**:

TDengine集成测试

测试TDengine数据访问层的实际读写操作和性能。

创建日期: 2025-10-11
版本: 1.0.0

---

### tests.integration.test_us1_acceptance

**文件**: `tests/integration/test_us1_acceptance.py`

**说明**:

US1端到端验收测试

验证MVP US1的所有验收标准:
1. 用户能够通过不超过3行代码完成数据保存和查询操作
2. 系统支持完整的34个数据分类的自动路由,路由正确率100%
3. 系统能够在2秒内完成10万条记录的批量保存操作
4. 实时数据从Redis缓存访问的响应时间不超过10毫秒
5. 时序数据查询响应时间不超过100毫秒
6. 数据库故障时自动排队,数据不丢失

创建日期: 2025-10-11
版本: 1.0.0

---

### tests.unit.test_mysql_table_creation

**文件**: `tests/unit/test_mysql_table_creation.py`

**说明**:

T023: MySQL表创建单元测试

验证ConfigDrivenTableManager能够正确创建MySQL表,
包括索引、约束、字符集等配置。

创建日期: 2025-10-11
版本: 1.0.0

#### 类

##### `TestMySQLTableCreation`

MySQL表创建测试类

**方法**:

- `setup_class(cls)` → `None` [tests/unit/test_mysql_table_creation.py:28]
  - 测试类初始化
- `test_01_mysql_connection(self)` → `None` [tests/unit/test_mysql_table_creation.py:33]
  - 测试1: MySQL连接测试
- `test_02_mysql_table_count(self)` → `None` [tests/unit/test_mysql_table_creation.py:51]
  - 测试2: 统计MySQL表定义数量
- `test_03_mysql_table_structure(self)` → `None` [tests/unit/test_mysql_table_creation.py:91]
  - 测试3: 验证MySQL表结构定义
- `test_04_create_mysql_tables(self)` → `None` [tests/unit/test_mysql_table_creation.py:136]
  - 测试4: 创建MySQL表
- `test_05_verify_table_exists(self)` → `None` [tests/unit/test_mysql_table_creation.py:171]
  - 测试5: 验证表是否存在
- `test_06_charset_and_collation(self)` → `None` [tests/unit/test_mysql_table_creation.py:195]
  - 测试6: 验证字符集和排序规则
- `test_07_auto_increment(self)` → `None` [tests/unit/test_mysql_table_creation.py:220]
  - 测试7: 验证自增主键

#### 函数

##### `run_tests()` → `None`

**位置**: [tests/unit/test_mysql_table_creation.py:245]

运行所有测试

---

### tests.unit.test_postgresql_table_creation

**文件**: `tests/unit/test_postgresql_table_creation.py`

**说明**:

T022: PostgreSQL表创建单元测试

验证ConfigDrivenTableManager能够正确创建PostgreSQL表,
包括TimescaleDB Hypertable、Chunk配置、压缩策略等。

创建日期: 2025-10-11
版本: 1.0.0

#### 类

##### `TestPostgreSQLTableCreation`

PostgreSQL表创建测试类

**方法**:

- `setup_class(cls)` → `None` [tests/unit/test_postgresql_table_creation.py:28]
  - 测试类初始化
- `test_01_postgresql_connection(self)` → `None` [tests/unit/test_postgresql_table_creation.py:33]
  - 测试1: PostgreSQL连接测试
- `test_02_timescaledb_extension(self)` → `None` [tests/unit/test_postgresql_table_creation.py:52]
  - 测试2: TimescaleDB扩展检查
- `test_03_postgresql_table_count(self)` → `None` [tests/unit/test_postgresql_table_creation.py:80]
  - 测试3: 统计PostgreSQL表定义数量
- `test_04_hypertable_structure(self)` → `None` [tests/unit/test_postgresql_table_creation.py:103]
  - 测试4: 验证Hypertable结构定义
- `test_05_create_postgresql_tables(self)` → `None` [tests/unit/test_postgresql_table_creation.py:140]
  - 测试5: 创建PostgreSQL表
- `test_06_verify_table_exists(self)` → `None` [tests/unit/test_postgresql_table_creation.py:176]
  - 测试6: 验证表是否存在
- `test_07_compression_policy(self)` → `None` [tests/unit/test_postgresql_table_creation.py:198]
  - 测试7: 验证压缩策略配置

#### 函数

##### `run_tests()` → `None`

**位置**: [tests/unit/test_postgresql_table_creation.py:223]

运行所有测试

---

### tests.unit.test_tdengine_table_creation

**文件**: `tests/unit/test_tdengine_table_creation.py`

**说明**:

T021: TDengine表创建单元测试

验证ConfigDrivenTableManager能够正确创建TDengine Super Tables,
包括标签(Tags)、压缩策略、保留策略等配置。

创建日期: 2025-10-11
版本: 1.0.0

#### 类

##### `TestTDengineTableCreation`

TDengine表创建测试类

**方法**:

- `setup_class(cls)` → `None` [tests/unit/test_tdengine_table_creation.py:28]
  - 测试类初始化
- `test_01_config_loaded(self)` → `None` [tests/unit/test_tdengine_table_creation.py:33]
  - 测试1: 配置文件加载成功
- `test_02_tdengine_connection(self)` → `None` [tests/unit/test_tdengine_table_creation.py:43]
  - 测试2: TDengine连接测试
- `test_03_tdengine_table_count(self)` → `None` [tests/unit/test_tdengine_table_creation.py:60]
  - 测试3: 统计TDengine表定义数量
- `test_04_super_table_structure(self)` → `None` [tests/unit/test_tdengine_table_creation.py:80]
  - 测试4: 验证Super Table结构定义
- `test_05_create_super_table(self)` → `None` [tests/unit/test_tdengine_table_creation.py:133]
  - 测试5: 创建Super Table
- `test_06_verify_table_exists(self)` → `None` [tests/unit/test_tdengine_table_creation.py:166]
  - 测试6: 验证表是否存在

#### 函数

##### `run_tests()` → `None`

**位置**: [tests/unit/test_tdengine_table_creation.py:189]

运行所有测试

---

### unified_manager

**文件**: `unified_manager.py`

**说明**:

MyStocks统一数据管理器 - 集成监控版本 (US1 + US3)

这是系统的核心入口,提供统一的数据保存和加载接口。
用户只需调用save_data_by_classification()和load_data_by_classification(),
系统自动根据数据分类路由到最优数据库。

新增功能 (US3):
- 所有操作自动记录到监控数据库
- 性能指标自动收集
- 慢查询自动告警
- 数据质量自动检查

创建日期: 2025-10-11
版本: 2.0.0 (MVP US1 + US3监控集成)

#### 类

##### `MyStocksUnifiedManager`

MyStocks统一数据管理器

**核心功能** (MVP US1):
1. 自动路由: 根据数据分类自动选择最优数据库
2. 统一接口: 2行代码完成保存/加载操作
3. 故障恢复: 数据库不可用时自动排队,数据不丢失
4. 批量操作: 支持10万条记录的高性能批量保存

**使用示例**:
    ```python
    manager = MyStocksUnifiedManager()

    # 保存Tick数据 → 自动路由到TDengine
    manager.save_data_by_classification(
        DataClassification.TICK_DATA,
        tick_df,
        table_name='tick_600000'
    )

    # 加载日线数据 → 自动路由到PostgreSQL
    kline_df = manager.load_data_by_classification(
        DataClassification.DAILY_KLINE,
        table_name='daily_kline',
        filters={'symbol': '600000.SH'}
    )
    ```

**方法**:

- `__init__(self, enable_monitoring: bool = True)` → `None` [unified_manager.py:78]
  - 初始化统一管理器
- `save_data_by_classification(self, classification: DataClassification, data: pd.DataFrame, table_name: str, **kwargs)` → `bool` [unified_manager.py:121]
  - 按分类保存数据 (核心方法 #1)
- `load_data_by_classification(self, classification: DataClassification, table_name: str, filters: Optional[Dict[(str, Any)]] = None, columns: Optional[List[str]] = None, limit: Optional[int] = None, **kwargs)` → `pd.DataFrame` [unified_manager.py:249]
  - 按分类加载数据 (核心方法 #2)
- `_save_to_redis(self, key: str, data: pd.DataFrame, ttl: Optional[int] = None)` → `None` [unified_manager.py:384]
  - 保存数据到Redis
- `_load_from_redis(self, key: str, filters: Optional[Dict[(str, Any)]] = None)` → `pd.DataFrame` [unified_manager.py:404]
  - 从Redis加载数据
- `_build_where_clause(self, filters: Dict[(str, Any)])` → `str` [unified_manager.py:430]
  - 构建WHERE子句
- `get_routing_info(self, classification: DataClassification)` → `Dict[(str, Any)]` [unified_manager.py:464]
  - 获取数据分类的路由信息
- `save_data_batch_with_strategy(self, classification: DataClassification, data: pd.DataFrame, table_name: str, strategy: BatchFailureStrategy = ..., **kwargs)` → `BatchOperationResult` [unified_manager.py:488]
  - 使用指定失败策略保存批量数据 (核心方法 #3)
- `get_monitoring_statistics(self)` → `Dict[(str, Any)]` [unified_manager.py:587]
  - 获取监控统计信息 (US3)
- `check_data_quality(self, classification: DataClassification, table_name: str, **kwargs)` → `Dict[(str, Any)]` [unified_manager.py:615]
  - 执行数据质量检查 (US3)
- `close_all_connections(self)` → `None` [unified_manager.py:691]
  - 关闭所有数据库连接

---

### web.backend.app.api.auth

**文件**: `web/backend/app/api/auth.py`

**说明**:

认证相关 API

#### 函数

##### `get_users_db()` → `None`

**位置**: [web/backend/app/api/auth.py:41]

获取用户数据库

##### `get_current_user(credentials: HTTPAuthorizationCredentials = Depends())` → `User`

**位置**: [web/backend/app/api/auth.py:45]

获取当前用户

##### `get_current_active_user(current_user: User = Depends())` → `User`

**位置**: [web/backend/app/api/auth.py:78]

获取当前活跃用户

##### `login_for_access_token(username: str = Form(), password: str = Form())` → `Dict[(str, Any)]`

**位置**: [web/backend/app/api/auth.py:89]

用户登录获取访问令牌
支持 OAuth2 标准的 form data 格式

**装饰器**: `@router.post`

##### `logout(current_user: User = Depends())` → `Dict[(str, Any)]`

**位置**: [web/backend/app/api/auth.py:125]

用户登出

**装饰器**: `@router.post`

##### `read_users_me(current_user: User = Depends())` → `User`

**位置**: [web/backend/app/api/auth.py:138]

获取当前用户信息

**装饰器**: `@router.get`

##### `refresh_token(current_user: User = Depends())` → `Dict[(str, Any)]`

**位置**: [web/backend/app/api/auth.py:147]

刷新访问令牌

**装饰器**: `@router.post`

##### `get_users(current_user: User = Depends())` → `Dict[(str, Any)]`

**位置**: [web/backend/app/api/auth.py:166]

获取用户列表（仅管理员）

**装饰器**: `@router.get`

##### `check_permission(user_role: str, required_role: str)` → `bool`

**位置**: [web/backend/app/api/auth.py:191]

检查用户权限

---

### web.backend.app.api.data

**文件**: `web/backend/app/api/data.py`

**说明**:

数据查询 API

#### 函数

##### `get_stocks_basic(limit: int = Query(), search: Optional[str] = Query(), industry: Optional[str] = Query(), market: Optional[str] = Query(), current_user: User = Depends())` → `Dict[(str, Any)]`

**位置**: [web/backend/app/api/data.py:16]

获取股票基本信息列表

**装饰器**: `@router.get`

##### `get_daily_kline(symbol: str = Query(), start_date: Optional[str] = Query(), end_date: Optional[str] = Query(), limit: int = Query(), current_user: User = Depends())` → `Dict[(str, Any)]`

**位置**: [web/backend/app/api/data.py:72]

获取股票日线数据

**装饰器**: `@router.get`

##### `get_market_overview(current_user: User = Depends())` → `Dict[(str, Any)]`

**位置**: [web/backend/app/api/data.py:154]

获取市场概览数据

**装饰器**: `@router.get`

##### `search_stocks(keyword: str = Query(), limit: int = Query(), current_user: User = Depends())` → `Dict[(str, Any)]`

**位置**: [web/backend/app/api/data.py:216]

股票搜索接口

**装饰器**: `@router.get`

##### `get_kline(symbol: str = Query(), start_date: Optional[str] = Query(), end_date: Optional[str] = Query(), limit: int = Query(), current_user: User = Depends())` → `Dict[(str, Any)]`

**位置**: [web/backend/app/api/data.py:280]

获取股票K线数据（stocks/daily的别名）

**装饰器**: `@router.get`

##### `get_financial_data(symbol: str = Query(), report_type: str = Query(), period: str = Query(), limit: int = Query(), current_user: User = Depends())` → `Dict[(str, Any)]`

**位置**: [web/backend/app/api/data.py:296]

获取股票财务数据

**报表类型**:
- balance: 资产负债表
- income: 利润表
- cashflow: 现金流量表

**数据源**: AkShare财务数据

**装饰器**: `@router.get`

---

### web.backend.app.api.tdx

**文件**: `web/backend/app/api/tdx.py`

**说明**:

TDX数据API路由

提供RESTful接口:
- GET /api/tdx/quote/{symbol} - 获取实时行情
- GET /api/tdx/kline - 获取历史K线(多周期)
- GET /api/tdx/index/quote/{symbol} - 获取指数行情
- GET /api/tdx/index/kline - 获取指数K线
- GET /api/tdx/health - 健康检查

所有接口均需JWT认证

#### 函数

##### `get_stock_quote(symbol: str, current_user: User = Depends(), service: TdxService = Depends())` → `None`

**位置**: [web/backend/app/api/tdx.py:38]

获取股票实时行情

**参数:**
- symbol: 6位数字股票代码(如: 600519)

**返回:**
- 实时行情数据,包含最新价、涨跌幅、五档行情等

**示例:**
```
GET /api/tdx/quote/600519
```

**认证:** 需要JWT令牌

**装饰器**: `@router.get`

##### `get_stock_kline(symbol: str = Query(), start_date: Optional[str] = Query(), end_date: Optional[str] = Query(), period: str = Query(), current_user: User = Depends(), service: TdxService = Depends())` → `None`

**位置**: [web/backend/app/api/tdx.py:92]

获取股票K线数据

**参数:**
- symbol: 6位数字股票代码(如: 600519)
- start_date: 开始日期(可选,默认为30天前)
- end_date: 结束日期(可选,默认为今天)
- period: K线周期
  - 1m: 1分钟
  - 5m: 5分钟
  - 15m: 15分钟
  - 30m: 30分钟
  - 1h: 1小时
  - 1d: 日线(默认)

**返回:**
- K线数据列表,包含开高低收成交量等

**示例:**
```
GET /api/tdx/kline?symbol=600519&period=5m&start_date=2025-10-01&end_date=2025-10-15
```

**认证:** 需要JWT令牌

**装饰器**: `@router.get`

##### `get_index_quote(symbol: str, current_user: User = Depends(), service: TdxService = Depends())` → `None`

**位置**: [web/backend/app/api/tdx.py:187]

获取指数实时行情

**参数:**
- symbol: 6位数字指数代码
  - 000001: 上证指数
  - 399001: 深证成指
  - 399006: 创业板指

**返回:**
- 指数实时点位、涨跌幅等数据

**示例:**
```
GET /api/tdx/index/quote/000001
```

**认证:** 需要JWT令牌

**装饰器**: `@router.get`

##### `get_index_kline(symbol: str = Query(), start_date: Optional[str] = Query(), end_date: Optional[str] = Query(), period: str = Query(), current_user: User = Depends(), service: TdxService = Depends())` → `None`

**位置**: [web/backend/app/api/tdx.py:244]

获取指数K线数据

**参数:**
- symbol: 6位数字指数代码
- start_date: 开始日期(可选,默认为90天前)
- end_date: 结束日期(可选,默认为今天)
- period: K线周期(同股票K线)

**返回:**
- 指数K线数据列表

**示例:**
```
GET /api/tdx/index/kline?symbol=000001&period=1d&start_date=2025-01-01
```

**认证:** 需要JWT令牌

**装饰器**: `@router.get`

##### `health_check(service: TdxService = Depends())` → `None`

**位置**: [web/backend/app/api/tdx.py:332]

TDX服务健康检查

**返回:**
- 服务状态和TDX连接信息

**示例:**
```
GET /api/tdx/health
```

**注意:** 此接口不需要认证

**装饰器**: `@router.get`

---

### web.backend.app.api.wencai

**文件**: `web/backend/app/api/wencai.py`

**说明**:

问财API路由

提供问财股票筛选功能的RESTful API端点

作者: MyStocks Backend Team
创建日期: 2025-10-17

#### 函数

##### `get_all_queries(db: Session = Depends())` → `WencaiQueryListResponse`

**位置**: [web/backend/app/api/wencai.py:50]

获取所有查询列表

返回所有预定义的问财查询配置（qs_1 ~ qs_9）

**装饰器**: `@router.get`

##### `get_query_by_name(query_name: str, db: Session = Depends())` → `WencaiQueryInfo`

**位置**: [web/backend/app/api/wencai.py:81]

获取指定查询信息

Args:
    query_name: 查询名称（如qs_1）

Returns:
    查询配置详情

**装饰器**: `@router.get`

##### `execute_query(request: WencaiQueryRequest, db: Session = Depends())` → `WencaiQueryResponse`

**位置**: [web/backend/app/api/wencai.py:122]

执行问财查询

从问财API获取数据，清理、去重后保存到MySQL

Args:
    request: 查询请求（包含query_name和pages）

Returns:
    查询执行结果统计

**装饰器**: `@router.post`

##### `get_query_results(query_name: str, limit: int = Query(), offset: int = Query(), db: Session = Depends())` → `WencaiResultsResponse`

**位置**: [web/backend/app/api/wencai.py:168]

获取查询结果

从数据库获取指定查询的最新结果

Args:
    query_name: 查询名称
    limit: 返回条数（1-1000）
    offset: 偏移量（用于分页）

Returns:
    查询结果列表

**装饰器**: `@router.get`

##### `refresh_query(query_name: str, background_tasks: BackgroundTasks, pages: int = Query(), db: Session = Depends())` → `WencaiRefreshResponse`

**位置**: [web/backend/app/api/wencai.py:214]

刷新查询数据（后台任务）

在后台异步执行数据刷新，立即返回任务状态

Args:
    query_name: 查询名称
    pages: 获取页数
    background_tasks: FastAPI后台任务管理器

Returns:
    任务状态响应

**装饰器**: `@router.post`

##### `get_query_history(query_name: str, days: int = Query(), db: Session = Depends())` → `WencaiHistoryResponse`

**位置**: [web/backend/app/api/wencai.py:276]

获取查询历史

统计指定天数内的查询数据情况

Args:
    query_name: 查询名称
    days: 查询天数（1-30）

Returns:
    历史统计数据

**装饰器**: `@router.get`

##### `execute_custom_query(request: WencaiCustomQueryRequest, db: Session = Depends())` → `WencaiCustomQueryResponse`

**位置**: [web/backend/app/api/wencai.py:319]

执行自定义查询

用户可以输入任意自然语言查询，直接获取结果

Args:
    request: 自定义查询请求（包含query_text和pages）

Returns:
    查询结果（不保存到数据库）

**装饰器**: `@router.post`

##### `health_check()` → `None`

**位置**: [web/backend/app/api/wencai.py:389]

健康检查

检查服务是否正常运行

Returns:
    健康状态

**装饰器**: `@router.get`

##### `_refresh_query_task(query_name: str, pages: int = 1)` → `None`

**位置**: [web/backend/app/api/wencai.py:409]

后台刷新任务

Args:
    query_name: 查询名称
    pages: 获取页数

---

### web.backend.app.core.security

**文件**: `web/backend/app/core/security.py`

**说明**:

安全认证和权限管理

#### 类

##### `Token`

JWT Token 模型

**继承**: `BaseModel`

##### `TokenData`

Token 数据模型

**继承**: `BaseModel`

##### `User`

用户模型

**继承**: `BaseModel`

##### `UserInDB`

数据库中的用户模型

**继承**: `User`

#### 函数

##### `verify_password(plain_password: str, hashed_password: str)` → `bool`

**位置**: [web/backend/app/core/security.py:43]

验证密码 - 直接使用 bcrypt，避免 passlib 兼容性问题

##### `get_password_hash(password: str)` → `str`

**位置**: [web/backend/app/core/security.py:54]

生成密码哈希 - 使用纯bcrypt

##### `create_access_token(data: Dict[(str, Any)], expires_delta: Optional[timedelta] = None)` → `str`

**位置**: [web/backend/app/core/security.py:60]

创建 JWT 访问令牌

##### `verify_token(token: str)` → `Optional[TokenData]`

**位置**: [web/backend/app/core/security.py:74]

验证 JWT 令牌

##### `authenticate_user(username: str, password: str)` → `Optional[UserInDB]`

**位置**: [web/backend/app/core/security.py:97]

验证用户身份

这里应该连接数据库查询用户信息
暂时使用模拟数据

##### `check_permission(user_role: str, required_role: str)` → `bool`

**位置**: [web/backend/app/core/security.py:136]

检查用户权限

##### `get_current_user(token: str = Depends())` → `User`

**位置**: [web/backend/app/core/security.py:145]

获取当前用户
依赖注入，用于路由保护

##### `get_current_active_user(current_user: User = Depends())` → `User`

**位置**: [web/backend/app/core/security.py:185]

获取当前活跃用户

---

### web.backend.app.main

**文件**: `web/backend/app/main.py`

**说明**:

FastAPI 主应用入口
MyStocks Web 管理界面后端服务

#### 函数

##### `log_requests(request: Request, call_next)` → `None`

**位置**: [web/backend/app/main.py:46]

**装饰器**: `@app.middleware`

##### `global_exception_handler(request: Request, exc: Exception)` → `None`

**位置**: [web/backend/app/main.py:73]

**装饰器**: `@app.exception_handler`

##### `health_check()` → `None`

**位置**: [web/backend/app/main.py:86]

系统健康检查

**装饰器**: `@app.get`

##### `root()` → `None`

**位置**: [web/backend/app/main.py:96]

根路径重定向到 API 文档

**装饰器**: `@app.get`

---

### web.backend.app.services.data_service

**文件**: `web/backend/app/services/data_service.py`

**说明**:

Data Service for Technical Analysis
股票数据服务 - 为技术指标计算提供OHLCV数据

Integrates with MyStocksUnifiedManager to load historical price data
Includes automatic data fetching via Akshare adapter when data is missing

#### 类

##### `StockDataNotFoundError`

股票数据未找到错误

**继承**: `Exception`

##### `InvalidDateRangeError`

无效日期范围错误

**继承**: `Exception`

##### `DataService`

数据服务

提供股票OHLCV数据加载功能,集成MyStocksUnifiedManager

**方法**:

- `__init__(self, auto_fetch: bool = True)` → `None` [web/backend/app/services/data_service.py:61]
  - 初始化数据服务
- `get_daily_ohlcv(self, symbol: str, start_date: datetime, end_date: datetime)` → `Tuple[(pd.DataFrame, Dict[(str, np.ndarray)])]` [web/backend/app/services/data_service.py:87]
  - 获取日线OHLCV数据
- `_fetch_and_save_from_akshare(self, symbol: str, start_date: datetime, end_date: datetime)` → `pd.DataFrame` [web/backend/app/services/data_service.py:156]
  - 从Akshare获取数据并保存到数据库
- `_load_from_unified_manager(self, symbol: str, start_date: datetime, end_date: datetime)` → `pd.DataFrame` [web/backend/app/services/data_service.py:226]
  - 从UnifiedManager加载数据
- `_generate_mock_data(self, symbol: str, start_date: datetime, end_date: datetime, base_price: float = 100.0)` → `pd.DataFrame` [web/backend/app/services/data_service.py:276]
  - 生成模拟数据 (用于开发测试)
- `_dataframe_to_ohlcv_arrays(self, df: pd.DataFrame)` → `Dict[(str, np.ndarray)]` [web/backend/app/services/data_service.py:337]
  - 将DataFrame转换为TA-Lib所需的NumPy数组格式
- `get_symbol_name(self, symbol: str)` → `str` [web/backend/app/services/data_service.py:355]
  - 获取股票名称
- `validate_symbol_format(self, symbol: str)` → `bool` [web/backend/app/services/data_service.py:384]
  - 验证股票代码格式
- `get_available_date_range(self, symbol: str)` → `Optional[Tuple[(datetime, datetime)]]` [web/backend/app/services/data_service.py:420]
  - 获取股票可用的数据日期范围

#### 函数

##### `get_data_service()` → `DataService`

**位置**: [web/backend/app/services/data_service.py:460]

获取数据服务单例

---

### web.backend.app.tasks.wencai_tasks

**文件**: `web/backend/app/tasks/wencai_tasks.py`

**说明**:

问财数据后台任务

使用Celery实现的后台任务：
  1. 单个查询刷新任务
  2. 定时刷新所有查询
  3. 清理旧数据任务

作者: MyStocks Backend Team
创建日期: 2025-10-17

#### 函数

##### `_get_safe_table_name(query_name: str)` → `str`

**位置**: [web/backend/app/tasks/wencai_tasks.py:30]

从白名单获取安全的表名，防止 SQL 注入

Args:
    query_name: 查询名称（如 'qs_1'）

Returns:
    安全的表名

Raises:
    ValueError: 如果 query_name 不在白名单中

##### `refresh_wencai_query(self, query_name: str, pages: int = 1)` → `Dict[(str, Any)]`

**位置**: [web/backend/app/tasks/wencai_tasks.py:55]

刷新单个问财查询（后台任务）

Args:
    query_name: 查询名称（如qs_1）
    pages: 获取页数

Returns:
    执行结果统计

**装饰器**: `@shared_task`

##### `scheduled_refresh_all_queries(pages: int = 1, active_only: bool = True)` → `Dict[(str, Any)]`

**位置**: [web/backend/app/tasks/wencai_tasks.py:120]

定时刷新所有查询（每日任务）

Args:
    pages: 每个查询获取的页数
    active_only: 是否只刷新启用的查询

Returns:
    批量执行结果统计

**装饰器**: `@shared_task`

##### `cleanup_old_wencai_data(days: int = 30, dry_run: bool = False)` → `Dict[(str, Any)]`

**位置**: [web/backend/app/tasks/wencai_tasks.py:208]

清理旧数据（定期维护任务）

删除指定天数之前的数据，释放存储空间

Args:
    days: 保留天数（删除N天前的数据）
    dry_run: 是否只模拟运行（不实际删除）

Returns:
    清理统计结果

**装饰器**: `@shared_task`

##### `get_wencai_stats()` → `Dict[(str, Any)]`

**位置**: [web/backend/app/tasks/wencai_tasks.py:326]

获取问财统计信息（监控任务）

统计所有查询的数据情况

Returns:
    统计信息

**装饰器**: `@shared_task`

##### `trigger_refresh_all()` → `None`

**位置**: [web/backend/app/tasks/wencai_tasks.py:422]

手动触发刷新所有查询

Returns:
    Celery AsyncResult

##### `trigger_cleanup(days: int = 30, dry_run: bool = False)` → `None`

**位置**: [web/backend/app/tasks/wencai_tasks.py:433]

手动触发清理任务

Args:
    days: 保留天数
    dry_run: 是否模拟运行

Returns:
    Celery AsyncResult

---
