# 基础设施功能

**类别**: infrastructure
**模块数**: 42
**类数**: 71
**函数数**: 258
**代码行数**: 11743

## 概述


基础设施模块提供底层数据库连接管理、表结构定义、配置管理等基础服务。
这些模块确保系统的稳定运行和数据持久化。

**关键特性**:
- 多数据库连接管理（TDengine, PostgreSQL, MySQL, Redis）
- 配置驱动的表结构管理
- 数据库连接池
- ORM 模型定义
- 数据迁移工具

**设计模式**: Singleton Pattern, Connection Pool, Repository Pattern


## 模块列表

### config.__init__

**文件**: `config/__init__.py`

---

### core.config_driven_table_manager

**文件**: `core/config_driven_table_manager.py`

**说明**:

配置驱动的表管理器

根据table_config.yaml自动创建和管理数据库表结构,支持安全模式和版本管理。

创建日期: 2025-10-11
版本: 1.0.0

#### 类

##### `ConfigDrivenTableManager`

配置驱动的表管理器

功能:
1. 从YAML配置文件读取表结构定义
2. 根据配置自动创建表 (TDengine Super Table, TimescaleDB Hypertable, MySQL表)
3. 验证表结构与配置一致性
4. 安全模式: 自动添加列,删除/修改需确认

**方法**:

- `__init__(self, config_path: str = "config/table_config.yaml")` → `None` [core/config_driven_table_manager.py:34]
  - 初始化配置驱动表管理器
- `_load_config(self)` → `Dict[(str, Any)]` [core/config_driven_table_manager.py:48]
  - 加载并验证YAML配置文件
- `initialize_all_tables(self)` → `Dict[(str, Any)]` [core/config_driven_table_manager.py:69]
  - 根据配置初始化所有表
- `_create_table(self, table_def: Dict[(str, Any)])` → `bool` [core/config_driven_table_manager.py:107]
  - 创建单个表
- `_table_exists(self, db_type: str, table_name: str, database_name: Optional[str] = None)` → `bool` [core/config_driven_table_manager.py:138]
  - 检查表是否存在
- `_create_tdengine_super_table(self, table_def: Dict[(str, Any)])` → `bool` [core/config_driven_table_manager.py:183]
  - 创建TDengine Super Table
- `_create_postgresql_table(self, table_def: Dict[(str, Any)])` → `bool` [core/config_driven_table_manager.py:238]
  - 创建PostgreSQL表 (支持TimescaleDB)
- `_create_mysql_table(self, table_def: Dict[(str, Any)])` → `bool` [core/config_driven_table_manager.py:357]
  - 创建MySQL表
- `validate_all_table_structures(self)` → `Dict[(str, Any)]` [core/config_driven_table_manager.py:447]
  - 验证所有表结构与配置一致性
- `_validate_table_structure(self, table_def: Dict[(str, Any)])` → `bool` [core/config_driven_table_manager.py:478]
  - 验证单个表结构
- `safe_add_column(self, table_name: str, column_def: Dict[(str, Any)])` → `bool` [core/config_driven_table_manager.py:495]
  - 安全模式: 自动添加列
- `confirm_dangerous_operation(self, operation_type: str, table_name: str, details: str)` → `bool` [core/config_driven_table_manager.py:514]
  - 确认危险操作 (删除列/修改列)
- `get_table_count_by_database(self)` → `Dict[(str, int)]` [core/config_driven_table_manager.py:532]
  - 获取每个数据库的表数量统计
- `get_classification_mapping(self)` → `Dict[(str, str)]` [core/config_driven_table_manager.py:547]
  - 获取数据分类到表名的映射

---

### core.config_loader

**文件**: `core/config_loader.py`

**说明**:

YAML配置加载器

使用PyYAML解析配置文件,Pydantic V2进行类型验证。
支持环境变量替换。

创建日期: 2025-10-11
版本: 1.0.0

#### 类

##### `ConfigLoader`

YAML配置加载器

**方法**:

- `load_config(config_path: str)` → `Dict[(str, Any)]` [core/config_loader.py:21]
  - 加载YAML配置文件

---

### db_manager.__init__

**文件**: `db_manager/__init__.py`

---

### db_manager.connection_manager

**文件**: `db_manager/connection_manager.py`

**说明**:

数据库连接管理器

管理4种数据库(TDengine/PostgreSQL/MySQL/Redis)的连接池和连接生命周期。
所有连接参数从环境变量读取,确保安全性。

创建日期: 2025-10-11
版本: 1.0.0

#### 类

##### `DatabaseConnectionManager`

数据库连接管理器基础类

管理4种数据库的连接池,提供统一的连接获取接口

**方法**:

- `__init__(self)` → `None` [db_manager/connection_manager.py:26]
  - 初始化连接管理器,验证必需的环境变量
- `_validate_env_variables(self)` → `None` [db_manager/connection_manager.py:31]
  - 验证必需的环境变量是否存在
- `get_tdengine_connection(self)` → `None` [db_manager/connection_manager.py:65]
  - 获取TDengine WebSocket连接
- `get_postgresql_connection(self)` → `None` [db_manager/connection_manager.py:104]
  - 获取PostgreSQL连接池
- `_return_postgresql_connection(self, conn)` → `None` [db_manager/connection_manager.py:142]
  - 归还PostgreSQL连接到连接池
- `get_mysql_connection(self)` → `None` [db_manager/connection_manager.py:152]
  - 获取MySQL连接池
- `get_redis_connection(self)` → `None` [db_manager/connection_manager.py:190]
  - 获取Redis连接池
- `close_all_connections(self)` → `None` [db_manager/connection_manager.py:235]
  - 关闭所有数据库连接
- `test_all_connections(self)` → `Dict[(str, bool)]` [db_manager/connection_manager.py:252]
  - 测试所有数据库连接

#### 函数

##### `get_connection_manager()` → `DatabaseConnectionManager`

**位置**: [db_manager/connection_manager.py:304]

获取全局连接管理器实例 (单例模式)

---

### db_manager.database_manager

**文件**: `db_manager/database_manager.py`

**说明**:

# 功能：数据库管理器，负责连接管理、表创建和结构验证
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025

#### 类

##### `DatabaseType`

**继承**: `Enum`

##### `TableCreationLog`

**继承**: `Base`

##### `ColumnDefinitionLog`

**继承**: `Base`

##### `TableOperationLog`

**继承**: `Base`

##### `TableValidationLog`

**继承**: `Base`

##### `DatabaseTableManager`

**方法**:

- `__init__(self)` → `None` [db_manager/database_manager.py:138]
- `get_connection(self, db_type: DatabaseType, db_name: str, **kwargs)` → `None` [db_manager/database_manager.py:182]
  - 获取数据库连接
- `_log_operation(self, table_name: str, db_type: DatabaseType, db_name: str, operation_type: str, operation_details: Dict, ddl_command: str = "", status: str = "success", error_message: str = "")` → `None` [db_manager/database_manager.py:269]
  - 记录操作日志到监控数据库
- `create_table(self, db_type: DatabaseType, db_name: str, table_name: str, columns: List[Dict], **kwargs)` → `bool` [db_manager/database_manager.py:287]
  - 在指定数据库中创建表
- `alter_table(self, db_type: DatabaseType, db_name: str, table_name: str, alterations: List[Dict], **kwargs)` → `bool` [db_manager/database_manager.py:379]
  - 修改表结构
- `drop_table(self, db_type: DatabaseType, db_name: str, table_name: str, **kwargs)` → `bool` [db_manager/database_manager.py:431]
  - 删除表
- `validate_table_structure(self, db_type: DatabaseType, db_name: str, table_name: str, expected_columns: List[Dict], **kwargs)` → `Dict` [db_manager/database_manager.py:496]
  - 验证表结构是否符合预期
- `batch_create_tables(self, config_file: str)` → `None` [db_manager/database_manager.py:574]
  - 通过配置文件table_config.yaml批量创建表,若yaml格式修改，这个函数也要改
- `_generate_alter_ddl(self, db_type: DatabaseType, table_name: str, alterations: List[Dict])` → `str` [db_manager/database_manager.py:600]
  - 生成ALTER TABLE语句
- `_generate_column_definition(self, col_def: Dict)` → `str` [db_manager/database_manager.py:620]
  - 生成列定义字符串
- `_generate_tdengine_ddl(self, table_name: str, columns: List[Dict], tags: List[Dict], **kwargs)` → `str` [db_manager/database_manager.py:648]
  - 生成TDengine的DDL语句
- `_generate_postgresql_ddl(self, table_name: str, columns: List[Dict], **kwargs)` → `str` [db_manager/database_manager.py:686]
  - 生成PostgreSQL的DDL语句
- `_generate_mysql_ddl(self, table_name: str, columns: List[Dict], **kwargs)` → `str` [db_manager/database_manager.py:728]
  - 生成MySQL的DDL语句
- `_initialize_redis_structure(self, conn, key_prefix: str, columns: List[Dict])` → `None` [db_manager/database_manager.py:780]
  - 初始化Redis数据结构
- `get_table_info(self, db_type: DatabaseType, db_name: str, table_name: str, **kwargs)` → `Optional[Dict]` [db_manager/database_manager.py:801]
  - 获取表结构信息
- `close_all_connections(self)` → `None` [db_manager/database_manager.py:876]
  - 关闭所有数据库连接

---

### db_manager.db_utils

**文件**: `db_manager/db_utils.py`

**说明**:

安全的数据库管理工具函数
避免在代码中硬编码敏感信息，统一从环境变量读取

#### 函数

##### `create_databases_safely()` → `None`

**位置**: [db_manager/db_utils.py:10]

安全地创建所需的数据库
所有连接参数从环境变量中读取

##### `get_database_config(db_type)` → `None`

**位置**: [db_manager/db_utils.py:73]

安全地获取数据库配置
:param db_type: 数据库类型 ('mysql', 'postgresql', 'tdengine', 'redis', 'mariadb')
:return: 数据库配置字典或None

---

### db_manager.df2sql

**文件**: `db_manager/df2sql.py`

**说明**:

Created on Mon May 15 10:01:46 2023
@author: CHENGJUN
update: 2025-09-12

功能介绍：这是用来把dataframe保存到mysql的必备转化工具，可根据dataframe生成SQL建表命令
          这个版本是更新过的，它支持设置primary_key和字符集utf8mb4

修改日期：2025-09-12
修改内容：增加了对大整数的支持，自动选择INT或BIGINT类型

#### 函数

##### `create_sql_cmd(df, table_name, primary_key=None)` → `None`

**位置**: [db_manager/df2sql.py:18]

---

### db_manager.execute_example

**文件**: `db_manager/execute_example.py`

---

### db_manager.execute_example_mysql_only

**文件**: `db_manager/execute_example_mysql_only.py`

---

### db_manager.fix_database_connections

**文件**: `db_manager/fix_database_connections.py`

**说明**:

数据库连接修复工具
用于解决MyStocks项目中的数据库连接问题

#### 函数

##### `check_database_connections()` → `None`

**位置**: [db_manager/fix_database_connections.py:27]

检查所有数据库连接配置

##### `fix_postgresql_hypertable()` → `None`

**位置**: [db_manager/fix_database_connections.py:49]

修复PostgreSQL中的hypertable问题

##### `fix_tdengine_database()` → `None`

**位置**: [db_manager/fix_database_connections.py:85]

修复TDengine数据库指定问题

##### `create_databases()` → `None`

**位置**: [db_manager/fix_database_connections.py:104]

创建所需的数据库

##### `validate_connections()` → `None`

**位置**: [db_manager/fix_database_connections.py:185]

验证所有数据库连接

##### `main()` → `None`

**位置**: [db_manager/fix_database_connections.py:226]

主函数

---

### db_manager.fixed_example

**文件**: `db_manager/fixed_example.py`

**说明**:

修复后的数据库管理示例
只使用可用的数据库库进行测试

#### 函数

##### `test_database_manager_import()` → `None`

**位置**: [db_manager/fixed_example.py:15]

测试DatabaseTableManager导入

##### `create_simple_mysql_example()` → `None`

**位置**: [db_manager/fixed_example.py:27]

创建简单的MySQL示例（仅生成DDL，不连接数据库）

##### `test_yaml_config_loading()` → `None`

**位置**: [db_manager/fixed_example.py:50]

测试YAML配置文件加载

##### `main()` → `None`

**位置**: [db_manager/fixed_example.py:75]

---

### db_manager.init_db_monitor

**文件**: `db_manager/init_db_monitor.py`

#### 函数

##### `find_env_file(default_path="mystocks/.env")` → `None`

**位置**: [db_manager/init_db_monitor.py:28]

智能查找环境变量文件，支持多种工作目录

Args:
    default_path (str): 默认相对路径

Returns:
    str: 找到的环境文件绝对路径

Raises:
    FileNotFoundError: 如果所有路径都找不到文件

##### `load_env_config(env_file=None)` → `None`

**位置**: [db_manager/init_db_monitor.py:100]

从环境变量文件加载配置

##### `get_sql_commands(drop_existing=False, charset="utf8mb4", collation="utf8mb4_unicode_ci")` → `None`

**位置**: [db_manager/init_db_monitor.py:166]

生成SQL命令，支持删除已有表选项

##### `create_database_and_tables(drop_existing=False)` → `None`

**位置**: [db_manager/init_db_monitor.py:255]

创建数据库和表结构

##### `init_monitoring_database(drop_existing=False)` → `None`

**位置**: [db_manager/init_db_monitor.py:357]

初始化监控数据库（专用于 Jupyter 环境调用）

Args:
    drop_existing (bool): 是否删除已存在的表

Returns:
    bool: 初始化是否成功

Examples:
    # 在 Jupyter 中使用
    success = init_monitoring_database()

    # 删除已存在的表并重建
    success = init_monitoring_database(drop_existing=True)

##### `extract_table_name(sql_cmd)` → `None`

**位置**: [db_manager/init_db_monitor.py:394]

从 CREATE TABLE 命令中提取表名

---

### db_manager.redis_data_fixation

**文件**: `db_manager/redis_data_fixation.py`

**说明**:

Redis热数据固化和强制更新扩展模块
解决Redis 5分钟过期数据的持久化和强制刷新问题

功能特性：
1. 自动固化Redis热数据到永久存储
2. 支持强制更新（跳过缓存）
3. 数据备份和恢复机制
4. 灵活的固化策略配置

作者: MyStocks项目组
日期: 2025-09-21

#### 类

##### `FixationStrategy`

数据固化策略

**继承**: `Enum`

##### `RedisDataFixationManager`

Redis热数据固化管理器

**方法**:

- `__init__(self, unified_manager: MyStocksUnifiedManager = None)` → `None` [db_manager/redis_data_fixation.py:42]
  - 初始化Redis数据固化管理器
- `force_update_realtime_data(self, market_symbol: str = "hs", bypass_cache: bool = True)` → `Dict[(str, Any)]` [db_manager/redis_data_fixation.py:65]
  - 强制更新实时数据（不读缓存）
- `_clear_redis_cache(self, market_symbol: str)` → `bool` [db_manager/redis_data_fixation.py:127]
  - 清除Redis缓存
- `fixate_redis_data_immediate(self, data: pd.DataFrame)` → `Dict[(str, bool)]` [db_manager/redis_data_fixation.py:156]
  - 立即固化Redis数据到永久存储
- `_aggregate_to_daily_format(self, realtime_data: pd.DataFrame)` → `Optional[pd.DataFrame]` [db_manager/redis_data_fixation.py:229]
  - 将实时数据聚合为日线格式
- `start_scheduled_fixation(self, interval_seconds: int = None)` → `None` [db_manager/redis_data_fixation.py:276]
  - 启动定时固化任务
- `get_fixation_statistics(self)` → `Dict[(str, Any)]` [db_manager/redis_data_fixation.py:291]
  - 获取固化统计信息

#### 函数

##### `main()` → `None`

**位置**: [db_manager/redis_data_fixation.py:319]

演示Redis热数据固化和强制更新功能

---

### db_manager.save_realtime_market_data

**文件**: `db_manager/save_realtime_market_data.py`

**说明**:

沪深市场A股实时数据保存系统 - efinance版本
严格按照MyStocks系统的统一接口规范和数据分类策略实现

核心设计理念：
1. 使用efinance的ef.stock.get_realtime_quotes()获取沪深A股实时数据
2. 使用统一管理器 (MyStocksUnifiedManager) - 隐藏底层数据库差异
3. 正确的数据分类 - 实时行情数据保存为REALTIME_POSITIONS (Redis) + DAILY_KLINE (PostgreSQL)
4. 自动路由保存 - 系统自动选择最优数据库存储
5. 完整监控集成 - 所有操作自动记录到监控数据库

数据分类策略：
- ef.stock.get_realtime_quotes() 获取的实时行情快照：
  * REALTIME_POSITIONS → Redis (热数据，快速访问)
  * DAILY_KLINE → PostgreSQL+TimescaleDB (持久化存储，分析查询)
- 双重保存确保数据的实时性和持久性

作者: MyStocks项目组
日期: 2025-09-23
修正: 使用efinance接口并保存到PostgreSQL

#### 类

##### `RealtimeMarketDataSaver`

沪深市场A股实时数据保存器 - 按照MyStocks统一接口规范实现

**方法**:

- `__init__(self, config_file: str = "realtime_market_config.env")` → `None` [db_manager/save_realtime_market_data.py:45]
  - 初始化数据保存器
- `_setup_logging(self)` → `None` [db_manager/save_realtime_market_data.py:57]
  - 配置日志系统
- `_load_config(self)` → `None` [db_manager/save_realtime_market_data.py:73]
  - 加载配置参数
- `initialize_unified_manager(self)` → `bool` [db_manager/save_realtime_market_data.py:119]
  - 初始化MyStocks统一管理器
- `initialize_data_source(self)` → `bool` [db_manager/save_realtime_market_data.py:151]
  - 初始化数据源适配器
- `get_realtime_market_data(self)` → `Optional[pd.DataFrame]` [db_manager/save_realtime_market_data.py:169]
  - 使用efinance获取沪深市场A股实时数据
- `_validate_market_data(self, data: pd.DataFrame)` → `bool` [db_manager/save_realtime_market_data.py:210]
  - 验证市场数据的基本结构
- `save_data_using_unified_interface(self, data: pd.DataFrame)` → `Dict[(str, bool)]` [db_manager/save_realtime_market_data.py:237]
  - 使用MyStocks统一接口保存数据
- `_prepare_daily_data(self, market_data: pd.DataFrame)` → `Optional[pd.DataFrame]` [db_manager/save_realtime_market_data.py:330]
  - 将实时市场数据转换为日线数据格式（用于PostgreSQL存储）
- `_prepare_tick_data(self, market_data: pd.DataFrame)` → `Optional[pd.DataFrame]` [db_manager/save_realtime_market_data.py:413]
  - 将市场数据转换为Tick数据格式（用于TDengine存储）
- `run(self)` → `bool` [db_manager/save_realtime_market_data.py:463]
  - 执行完整的数据获取和保存流程

#### 函数

##### `main()` → `None`

**位置**: [db_manager/save_realtime_market_data.py:538]

主函数

---

### db_manager.save_realtime_market_data_simple

**文件**: `db_manager/save_realtime_market_data_simple.py`

**说明**:

沪深市场A股实时数据保存系统 - 简化版
专注于实时数据获取和Redis存储，避免复杂的数据库依赖

核心功能：
1. 从efinance获取沪深A股实时数据
2. 保存到Redis热数据存储（5分钟过期）
3. 可选：导出到CSV文件作为备份
4. 支持强制更新（跳过缓存）

作者: MyStocks项目组
日期: 2025-09-21
版本: 简化版 v1.0

#### 类

##### `SimpleRealtimeDataSaver`

简化版实时数据保存器 - 只使用Redis和CSV

**方法**:

- `__init__(self, config_file: str = None)` → `None` [db_manager/save_realtime_market_data_simple.py:32]
  - 初始化简化版数据保存器
- `_setup_logging(self)` → `None` [db_manager/save_realtime_market_data_simple.py:53]
  - 配置日志系统
- `_load_config(self)` → `None` [db_manager/save_realtime_market_data_simple.py:68]
  - 加载配置参数
- `initialize_redis(self)` → `bool` [db_manager/save_realtime_market_data_simple.py:115]
  - 初始化Redis连接
- `get_realtime_market_data(self)` → `Optional[pd.DataFrame]` [db_manager/save_realtime_market_data_simple.py:139]
  - 获取实时市场数据
- `_validate_market_data(self, data: pd.DataFrame)` → `bool` [db_manager/save_realtime_market_data_simple.py:193]
  - 验证市场数据的基本结构
- `save_to_redis(self, data: pd.DataFrame)` → `bool` [db_manager/save_realtime_market_data_simple.py:218]
  - 保存数据到Redis
- `save_to_csv(self, data: pd.DataFrame)` → `bool` [db_manager/save_realtime_market_data_simple.py:254]
  - 保存数据到CSV文件
- `force_update(self)` → `Dict[(str, Any)]` [db_manager/save_realtime_market_data_simple.py:279]
  - 强制更新（清除缓存并获取最新数据）
- `save_data(self, data: pd.DataFrame)` → `Dict[(str, bool)]` [db_manager/save_realtime_market_data_simple.py:324]
  - 保存数据到所有配置的目标
- `run(self, force_update: bool = False)` → `bool` [db_manager/save_realtime_market_data_simple.py:336]
  - 执行完整的数据获取和保存流程

#### 函数

##### `main()` → `None`

**位置**: [db_manager/save_realtime_market_data_simple.py:394]

主函数

---

### db_manager.security_check

**文件**: `db_manager/security_check.py`

**说明**:

数据库安全检查脚本
检查代码中是否存在硬编码的敏感信息

#### 类

##### `SecurityChecker`

数据库安全检查器

**方法**:

- `__init__(self, project_root: str)` → `None` [db_manager/security_check.py:15]
- `is_excluded_file(self, file_path: str)` → `bool` [db_manager/security_check.py:54]
  - 检查文件是否应该被排除
- `is_safe_line(self, line: str)` → `bool` [db_manager/security_check.py:61]
  - 检查是否是安全的代码行
- `scan_file(self, file_path: str)` → `List[Dict]` [db_manager/security_check.py:68]
  - 扫描单个文件
- `scan_directory(self, directory: str = None)` → `List[Dict]` [db_manager/security_check.py:109]
  - 扫描目录中的所有Python文件
- `generate_report(self, issues: List[Dict])` → `str` [db_manager/security_check.py:135]
  - 生成安全检查报告

#### 函数

##### `main()` → `None`

**位置**: [db_manager/security_check.py:171]

主函数

---

### db_manager.test_database_menu

**文件**: `db_manager/test_database_menu.py`

**说明**:

数据库测试工具 - 交互式菜单版本
整合了路径查找、配置检查、连通性测试功能

#### 类

##### `DatabaseTestTool`

数据库测试工具类

**方法**:

- `__init__(self)` → `None` [db_manager/test_database_menu.py:17]
  - 初始化测试工具
- `find_env_file(self)` → `bool` [db_manager/test_database_menu.py:32]
  - 查找.env文件路径
- `load_config(self)` → `Dict[(str, Any)]` [db_manager/test_database_menu.py:81]
  - 从环境变量加载数据库配置
- `test_config_integrity(self)` → `bool` [db_manager/test_database_menu.py:125]
  - 测试数据库配置完整性
- `check_database_drivers(self)` → `bool` [db_manager/test_database_menu.py:175]
  - 检查数据库驱动安装情况
- `_check_tdengine_drivers(self)` → `list` [db_manager/test_database_menu.py:243]
  - 检测 TDengine 的各种连接方式
- `test_database_connectivity(self)` → `bool` [db_manager/test_database_menu.py:322]
  - 测试数据库连通性
- `_test_mysql_monitor_simple(self, config: Dict[(str, Any)], create_engine, text)` → `bool` [db_manager/test_database_menu.py:434]
  - 简化版MySQL监控数据库测试
- `_test_mysql_simple(self, config: Dict[(str, Any)], pymysql)` → `bool` [db_manager/test_database_menu.py:449]
  - 简化版MySQL连接测试
- `_test_redis_simple(self, config: Dict[(str, Any)], redis_lib)` → `bool` [db_manager/test_database_menu.py:475]
  - 简化版Redis连接测试
- `_test_tdengine_multi(self, config: Dict[(str, Any)], methods: Dict[(str, Any)])` → `bool` [db_manager/test_database_menu.py:499]
  - 多种连接方式测试TDengine，只要有一种成功即可
- `_test_tdengine_websocket(self, config: Dict[(str, Any)], taosws)` → `bool` [db_manager/test_database_menu.py:549]
  - 测试TDengine WebSocket连接
- `_test_tdengine_rest(self, config: Dict[(str, Any)], taosrest)` → `bool` [db_manager/test_database_menu.py:569]
  - 测试TDengine REST连接
- `_test_tdengine_native(self, config: Dict[(str, Any)], taos)` → `bool` [db_manager/test_database_menu.py:594]
  - 测试TDengine原生连接
- `_print_config_summary(self, successful: int)` → `None` [db_manager/test_database_menu.py:619]
  - 打印配置测试总结
- `run_all_tests(self)` → `None` [db_manager/test_database_menu.py:641]
  - 运行所有测试

#### 函数

##### `show_menu()` → `None`

**位置**: [db_manager/test_database_menu.py:673]

显示主菜单

##### `main()` → `None`

**位置**: [db_manager/test_database_menu.py:688]

主函数

---

### db_manager.test_jupyter_compatibility

**文件**: `db_manager/test_jupyter_compatibility.py`

**说明**:

测试 Jupyter 环境兼容性

#### 函数

##### `test_jupyter_api()` → `None`

**位置**: [db_manager/test_jupyter_compatibility.py:15]

测试 Jupyter API 调用

---

### db_manager.test_multi_directory

**文件**: `db_manager/test_multi_directory.py`

**说明**:

模拟不同工作目录下运行的测试

#### 函数

##### `test_from_directory(test_dir)` → `None`

**位置**: [db_manager/test_multi_directory.py:18]

从指定目录测试初始化

##### `main()` → `None`

**位置**: [db_manager/test_multi_directory.py:51]

主测试函数

---

### db_manager.test_simple

**文件**: `db_manager/test_simple.py`

**说明**:

简化的数据库连接测试脚本
用于验证TDengine导入问题是否已解决

#### 函数

##### `test_taos_import()` → `None`

**位置**: [db_manager/test_simple.py:14]

测试TDengine导入

##### `test_other_databases()` → `None`

**位置**: [db_manager/test_simple.py:30]

测试其他数据库库的导入

##### `test_conditional_import()` → `None`

**位置**: [db_manager/test_simple.py:55]

测试条件导入机制

---

### db_manager.test_tdengine

**文件**: `db_manager/test_tdengine.py`

**说明**:

TDengine连接测试脚本
包含条件导入和错误处理机制

#### 函数

##### `test_tdengine_import()` → `None`

**位置**: [db_manager/test_tdengine.py:15]

测试TDengine导入和连接

##### `test_tdengine_connection(taos_module, module_name)` → `None`

**位置**: [db_manager/test_tdengine.py:44]

测试TDengine数据库连接

##### `main()` → `None`

**位置**: [db_manager/test_tdengine.py:132]

主函数

---

### db_manager.validate_mystocks_architecture

**文件**: `db_manager/validate_mystocks_architecture.py`

**说明**:

MyStocks统一接口验证脚本
验证实时市场数据保存系统是否符合MyStocks架构设计

验证内容：
1. 统一管理器初始化
2. 数据分类路由正确性
3. 自动数据库选择
4. 监控系统集成
5. 与系统架构的一致性

作者: MyStocks项目组
日期: 2025-09-21

#### 函数

##### `setup_logging()` → `None`

**位置**: [db_manager/validate_mystocks_architecture.py:31]

配置日志系统

##### `test_data_classification_strategy()` → `None`

**位置**: [db_manager/validate_mystocks_architecture.py:40]

测试数据分类策略

##### `test_unified_manager_initialization()` → `None`

**位置**: [db_manager/validate_mystocks_architecture.py:79]

测试统一管理器初始化

##### `test_data_source_integration()` → `None`

**位置**: [db_manager/validate_mystocks_architecture.py:129]

测试数据源集成

##### `test_unified_interface_save(unified_manager, sample_data)` → `None`

**位置**: [db_manager/validate_mystocks_architecture.py:165]

测试统一接口保存功能

##### `test_architecture_consistency()` → `None`

**位置**: [db_manager/validate_mystocks_architecture.py:229]

测试架构一致性

##### `main()` → `None`

**位置**: [db_manager/validate_mystocks_architecture.py:272]

主函数

---

### scripts.analysis.models

**文件**: `scripts/analysis/models.py`

**说明**:

数据模型定义 - MyStocks Function Classification Manual

定义所有代码分析和手册生成使用的数据结构。

作者: MyStocks Team
日期: 2025-10-19

#### 类

##### `CategoryEnum`

功能类别枚举

**继承**: `Enum`

##### `SeverityEnum`

严重性级别枚举

**继承**: `Enum`

##### `PriorityEnum`

优先级枚举

**继承**: `Enum`

##### `ParameterMetadata`

函数参数元数据

##### `FunctionMetadata`

函数元数据

##### `ClassMetadata`

类元数据

##### `ModuleMetadata`

模块元数据

##### `CodeBlock`

代码块（用于相似性比较）

##### `DuplicationCase`

代码重复案例

##### `Dependency`

模块依赖关系

##### `OptimizationOpportunity`

优化机会

##### `MergeRecommendation`

合并建议

##### `DataFlow`

数据流

##### `ArchitectureIssue`

架构问题

##### `ManualMetadata`

手册元数据

##### `ModuleInventory`

模块清单

**方法**:

- `get_modules_by_category(self, category: CategoryEnum)` → `List[ModuleMetadata]` [scripts/analysis/models.py:216]
  - 按类别获取模块列表
- `get_module_by_path(self, file_path: str)` → `Optional[ModuleMetadata]` [scripts/analysis/models.py:220]
  - 根据文件路径获取模块
- `get_total_functions(self)` → `int` [scripts/analysis/models.py:227]
  - 获取总函数数量
- `get_total_classes(self)` → `int` [scripts/analysis/models.py:236]
  - 获取总类数量

##### `DuplicationIndex`

重复索引

**方法**:

- `add_duplication(self, dup: DuplicationCase)` → `None` [scripts/analysis/models.py:253]
  - 添加重复案例并自动分类
- `get_by_severity(self, severity: SeverityEnum)` → `List[DuplicationCase]` [scripts/analysis/models.py:267]
  - 按严重性获取重复案例

##### `OptimizationRoadmap`

优化路线图

**方法**:

- `add_opportunity(self, opp: OptimizationOpportunity)` → `None` [scripts/analysis/models.py:290]
  - 添加优化机会并自动分类
- `get_by_priority(self, priority: PriorityEnum)` → `List[OptimizationOpportunity]` [scripts/analysis/models.py:301]
  - 按优先级获取优化机会
- `get_quick_wins(self)` → `List[OptimizationOpportunity]` [scripts/analysis/models.py:305]
  - 获取快速胜利项（高优先级 + 低工作量）

##### `ConsolidationGuide`

合并指南

**方法**:

- `add_recommendation(self, rec: MergeRecommendation)` → `None` [scripts/analysis/models.py:321]
  - 添加合并建议
- `get_by_risk_level(self, risk_level: str)` → `List[MergeRecommendation]` [scripts/analysis/models.py:325]
  - 按风险级别获取建议
- `get_high_impact(self)` → `List[MergeRecommendation]` [scripts/analysis/models.py:329]
  - 获取高影响合并建议（合并 3+ 模块）

#### 函数

##### `severity_from_similarity(token_sim: float, ast_sim: float)` → `SeverityEnum`

**位置**: [scripts/analysis/models.py:336]

根据相似度计算严重性级别

##### `categorize_module_by_path(file_path: str)` → `CategoryEnum`

**位置**: [scripts/analysis/models.py:348]

根据文件路径推断模块类别（初步分类）

##### `estimate_complexity(function_ast)` → `int`

**位置**: [scripts/analysis/models.py:385]

估算函数圈复杂度

简化版本：计算决策点数量（if, for, while, try, except, and, or）

---

### test_config_driven_table_manager

**文件**: `test_config_driven_table_manager.py`

**说明**:

测试ConfigDrivenTableManager

验证US2 (T020) 的核心功能:
1. 配置文件加载正确
2. 表结构统计准确
3. 分类映射完整
4. 安全模式工作正常

创建日期: 2025-10-12

#### 函数

##### `test_config_loading()` → `None`

**位置**: [test_config_driven_table_manager.py:30]

测试1: 配置文件加载

##### `test_table_statistics(manager)` → `None`

**位置**: [test_config_driven_table_manager.py:48]

测试2: 表统计功能

##### `test_classification_mapping(manager)` → `None`

**位置**: [test_config_driven_table_manager.py:79]

测试3: 数据分类映射

##### `test_safe_mode(manager)` → `None`

**位置**: [test_config_driven_table_manager.py:124]

测试4: 安全模式功能

##### `test_config_validation(manager)` → `None`

**位置**: [test_config_driven_table_manager.py:153]

测试5: 配置内容验证

##### `main()` → `None`

**位置**: [test_config_driven_table_manager.py:185]

主测试函数

---

### tests.acceptance.test_us2_config_driven

**文件**: `tests/acceptance/test_us2_config_driven.py`

**说明**:

T025: US2配置驱动表结构管理验收测试

验证配置驱动表结构管理的6个核心场景：
1. 添加新表定义 → 自动创建
2. 添加新列 → 自动添加
3. 删除/修改列 → 需要确认
4. 配置语法错误 → 明确错误信息
5. 不支持的数据库类型 → 错误提示
6. 表名冲突 → 冲突错误

创建日期: 2025-10-11
版本: 1.0.0

#### 类

##### `TestUS2ConfigDriven`

US2验收测试类

**方法**:

- `setup_class(cls)` → `None` [tests/acceptance/test_us2_config_driven.py:37]
  - 测试类初始化
- `teardown_class(cls)` → `None` [tests/acceptance/test_us2_config_driven.py:47]
  - 测试类清理
- `_check_database_availability(cls)` → `None` [tests/acceptance/test_us2_config_driven.py:54]
  - 检查数据库可用性
- `test_scenario_1_add_new_table_auto_create(self)` → `None` [tests/acceptance/test_us2_config_driven.py:97]
  - 场景1: 添加新表定义 → 自动创建
- `test_scenario_2_add_new_column_auto_add(self)` → `None` [tests/acceptance/test_us2_config_driven.py:225]
  - 场景2: 添加新列 → 自动添加
- `test_scenario_3_delete_column_needs_confirmation(self)` → `None` [tests/acceptance/test_us2_config_driven.py:244]
  - 场景3: 删除/修改列 → 需要确认
- `test_scenario_4_config_syntax_error_clear_message(self)` → `None` [tests/acceptance/test_us2_config_driven.py:274]
  - 场景4: 配置语法错误 → 明确错误信息
- `test_scenario_5_unsupported_database_type_error(self)` → `None` [tests/acceptance/test_us2_config_driven.py:339]
  - 场景5: 不支持的数据库类型 → 错误提示
- `test_scenario_6_table_name_conflict_error(self)` → `None` [tests/acceptance/test_us2_config_driven.py:409]
  - 场景6: 表名冲突 → 冲突错误
- `test_integration_summary(self)` → `None` [tests/acceptance/test_us2_config_driven.py:493]
  - 集成测试总结

#### 函数

##### `run_tests()` → `None`

**位置**: [tests/acceptance/test_us2_config_driven.py:538]

运行所有验收测试

---

### tests.unit.test_config_validation

**文件**: `tests/unit/test_config_validation.py`

**说明**:

T024: 配置验证单元测试

验证table_config.yaml配置文件的完整性和正确性,
包括配置结构、数据分类覆盖、冲突检测等。

创建日期: 2025-10-11
版本: 1.0.0

#### 类

##### `TestConfigValidation`

配置验证测试类

**方法**:

- `setup_class(cls)` → `None` [tests/unit/test_config_validation.py:28]
  - 测试类初始化
- `test_01_config_structure(self)` → `None` [tests/unit/test_config_validation.py:33]
  - 测试1: 验证配置文件结构
- `test_02_database_config(self)` → `None` [tests/unit/test_config_validation.py:48]
  - 测试2: 验证数据库配置
- `test_03_table_count(self)` → `None` [tests/unit/test_config_validation.py:69]
  - 测试3: 验证表数量
- `test_04_classification_coverage(self)` → `None` [tests/unit/test_config_validation.py:91]
  - 测试4: 验证数据分类覆盖
- `test_05_table_name_uniqueness(self)` → `None` [tests/unit/test_config_validation.py:124]
  - 测试5: 验证表名唯一性
- `test_06_required_columns(self)` → `None` [tests/unit/test_config_validation.py:143]
  - 测试6: 验证必需列
- `test_07_index_definition(self)` → `None` [tests/unit/test_config_validation.py:168]
  - 测试7: 验证索引定义
- `test_08_compression_config(self)` → `None` [tests/unit/test_config_validation.py:201]
  - 测试8: 验证压缩配置
- `test_09_retention_policy(self)` → `None` [tests/unit/test_config_validation.py:226]
  - 测试9: 验证保留策略
- `test_10_maintenance_config(self)` → `None` [tests/unit/test_config_validation.py:254]
  - 测试10: 验证维护配置

#### 函数

##### `run_tests()` → `None`

**位置**: [tests/unit/test_config_validation.py:281]

运行所有测试

---

### utils.tdx_server_config

**文件**: `utils/tdx_server_config.py`

**说明**:

# 功能：TDX服务器配置模块，管理通达信服务器列表和连接参数
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025

#### 类

##### `TdxServerConfig`

TDX服务器配置管理器

功能:
- 解析connect.cfg文件提取服务器列表
- 支持主服务器配置(PrimaryHost)
- 支持随机服务器选择(负载均衡)
- 支持故障转移(fallback到备用服务器)

示例:
    >>> config = TdxServerConfig('/path/to/connect.cfg')
    >>> primary_host, primary_port = config.get_primary_server()
    >>> all_servers = config.get_all_servers()
    >>> random_server = config.get_random_server()

**方法**:

- `__init__(self, config_file: str = None)` → `None` [utils/tdx_server_config.py:37]
  - 初始化TDX服务器配置管理器
- `_load_config(self)` → `None` [utils/tdx_server_config.py:59]
  - 加载并解析connect.cfg文件
- `get_primary_server(self)` → `Tuple[(str, int)]` [utils/tdx_server_config.py:136]
  - 获取主服务器(根据PrimaryHost配置)
- `get_random_server(self)` → `Tuple[(str, int)]` [utils/tdx_server_config.py:154]
  - 随机选择一个服务器(负载均衡)
- `get_all_servers(self)` → `List[Tuple[(str, int, str)]]` [utils/tdx_server_config.py:171]
  - 获取所有可用服务器列表
- `get_server_by_index(self, index: int)` → `Optional[Tuple[(str, int)]]` [utils/tdx_server_config.py:185]
  - 根据索引获取服务器
- `get_failover_servers(self, max_count: int = 3)` → `List[Tuple[(str, int)]]` [utils/tdx_server_config.py:200]
  - 获取故障转移服务器列表(主服务器+备用服务器)
- `get_server_count(self)` → `int` [utils/tdx_server_config.py:249]
  - 获取可用服务器总数
- `__str__(self)` → `None` [utils/tdx_server_config.py:253]
  - 字符串表示

#### 函数

##### `get_global_config()` → `TdxServerConfig`

**位置**: [utils/tdx_server_config.py:267]

获取全局TDX服务器配置单例

Returns:
    TdxServerConfig单例实例

示例:
    >>> config = get_global_config()
    >>> host, port = config.get_primary_server()

---

### web.backend.app.api.market

**文件**: `web/backend/app/api/market.py`

**说明**:

市场数据API路由

提供RESTful接口:
- GET /api/market/fund-flow - 查询资金流向
- POST /api/market/fund-flow/refresh - 刷新资金流向数据
- GET /api/market/etf/list - 查询ETF列表
- POST /api/market/etf/refresh - 刷新ETF数据
- GET /api/market/chip-race - 查询竞价抢筹
- POST /api/market/chip-race/refresh - 刷新抢筹数据
- GET /api/market/lhb - 查询龙虎榜
- POST /api/market/lhb/refresh - 刷新龙虎榜数据

#### 函数

##### `get_fund_flow(symbol: str = Query(), timeframe: str = Query(), start_date: Optional[date] = Query(), end_date: Optional[date] = Query(), service: MarketDataService = Depends())` → `None`

**位置**: [web/backend/app/api/market.py:38]

查询个股资金流向历史数据

**参数说明:**
- symbol: 股票代码 (如: 600519.SH)
- timeframe: 1=今日, 3=3日, 5=5日, 10=10日
- start_date/end_date: 时间范围筛选

**返回:** 资金流向列表

**装饰器**: `@router.get`

##### `refresh_fund_flow(symbol: str = Query(), timeframe: str = Query(), service: MarketDataService = Depends())` → `None`

**位置**: [web/backend/app/api/market.py:63]

从数据源刷新资金流向数据并保存到数据库

**数据源:** 东方财富网 (via akshare)

**装饰器**: `@router.post`

##### `get_etf_list(symbol: Optional[str] = Query(), keyword: Optional[str] = Query(), limit: int = Query(), service: MarketDataService = Depends())` → `None`

**位置**: [web/backend/app/api/market.py:84]

查询ETF实时行情数据

**查询方式:**
- 指定symbol: 返回单个ETF数据
- 指定keyword: 模糊搜索名称/代码
- 不指定条件: 返回全市场ETF(按涨跌幅排序)

**返回:** ETF数据列表

**装饰器**: `@router.get`

##### `refresh_etf_data(service: MarketDataService = Depends())` → `None`

**位置**: [web/backend/app/api/market.py:108]

刷新全市场ETF实时数据

**数据源:** 东方财富网 (via akshare)
**更新频率:** 建议每5分钟调用一次

**装饰器**: `@router.post`

##### `get_chip_race(race_type: str = Query(), trade_date: Optional[date] = Query(), min_race_amount: Optional[float] = Query(), limit: int = Query(), service: MarketDataService = Depends())` → `None`

**位置**: [web/backend/app/api/market.py:128]

查询竞价抢筹数据

**类型说明:**
- open: 早盘抢筹(集合竞价)
- end: 尾盘抢筹(收盘竞价)

**返回:** 按抢筹金额倒序排列

**装饰器**: `@router.get`

##### `refresh_chip_race(race_type: str = Query(), trade_date: Optional[str] = Query(), service: MarketDataService = Depends())` → `None`

**位置**: [web/backend/app/api/market.py:152]

刷新竞价抢筹数据

**数据源:** 通达信TQLEX
**更新时机:**
- open: 9:30之后
- end: 15:05之后

**装饰器**: `@router.post`

##### `get_lhb_detail(symbol: Optional[str] = Query(), start_date: Optional[date] = Query(), end_date: Optional[date] = Query(), min_net_amount: Optional[float] = Query(), limit: int = Query(), service: MarketDataService = Depends())` → `None`

**位置**: [web/backend/app/api/market.py:176]

查询龙虎榜详细数据

**筛选条件:**
- symbol: 查询指定股票的历史龙虎榜记录
- start_date/end_date: 时间范围
- min_net_amount: 净买入额下限(元)

**返回:** 按日期倒序排列

**装饰器**: `@router.get`

##### `refresh_lhb_detail(trade_date: str = Query(), service: MarketDataService = Depends())` → `None`

**位置**: [web/backend/app/api/market.py:202]

刷新指定日期的龙虎榜数据

**数据源:** 东方财富网 (via akshare)
**更新时机:** 每日20:00之后
**说明:** 龙虎榜数据次日公布

**装饰器**: `@router.post`

##### `get_market_quotes(symbols: Optional[str] = Query())` → `None`

**位置**: [web/backend/app/api/market.py:224]

获取实时市场行情数据

**参数**:
- symbols: 股票代码列表（可选）。不指定则返回热门股票行情

**数据源**: TDX实时行情
**返回**: 实时行情列表

**装饰器**: `@router.get`

##### `get_stock_list(limit: int = Query(), search: Optional[str] = Query(), industry: Optional[str] = Query(), market: Optional[str] = Query())` → `None`

**位置**: [web/backend/app/api/market.py:272]

获取股票基本信息列表

**查询条件**:
- search: 关键词搜索（代码或名称）
- industry: 按行业筛选
- market: 按市场筛选（SH/SZ）
- limit: 返回数量限制

**数据源**: MySQL stock_info表
**返回**: 股票列表

**装饰器**: `@router.get`

##### `health_check()` → `None`

**位置**: [web/backend/app/api/market.py:346]

API健康检查

**装饰器**: `@router.get`

---

### web.backend.app.api.system

**文件**: `web/backend/app/api/system.py`

**说明**:

系统管理API端点
提供系统设置、数据库连接测试、运行日志查询等功能

#### 类

##### `ConnectionTestRequest`

数据库连接测试请求

**继承**: `BaseModel`

##### `ConnectionTestResponse`

数据库连接测试响应

**继承**: `BaseModel`

##### `SystemLog`

系统日志模型

**继承**: `BaseModel`

##### `LogQueryResponse`

日志查询响应

**继承**: `BaseModel`

#### 函数

##### `system_health()` → `None`

**位置**: [web/backend/app/api/system.py:21]

系统健康检查端点

返回:
- 数据库连接状态
- 系统运行时间
- 服务状态

**装饰器**: `@router.get`

##### `get_datasources()` → `None`

**位置**: [web/backend/app/api/system.py:69]

获取已配置的数据源列表

返回所有可用的数据源配置信息

**装饰器**: `@router.get`

##### `test_database_connection(request: ConnectionTestRequest)` → `None`

**位置**: [web/backend/app/api/system.py:133]

测试数据库连接

支持的数据库类型:
- mysql: MySQL/MariaDB
- postgresql: PostgreSQL
- tdengine: TDengine
- redis: Redis

**装饰器**: `@router.post`

##### `get_system_logs_from_db(filter_errors: bool = False, limit: int = 100, offset: int = 0, level: Optional[str] = None, category: Optional[str] = None)` → `List[SystemLog]`

**位置**: [web/backend/app/api/system.py:407]

从PostgreSQL监控数据库获取系统日志

Args:
    filter_errors: 是否只返回有问题的日志 (WARNING, ERROR, CRITICAL)
    limit: 返回条数限制
    offset: 偏移量
    level: 日志级别筛选
    category: 日志分类筛选

Returns:
    系统日志列表

##### `get_mock_system_logs(filter_errors: bool = False, limit: int = 100)` → `List[SystemLog]`

**位置**: [web/backend/app/api/system.py:512]

生成模拟的系统日志（用于演示和数据库不可用时的备用）

##### `get_system_logs(filter_errors: bool = Query(), limit: int = Query(), offset: int = Query(), level: Optional[str] = Query(), category: Optional[str] = Query())` → `None`

**位置**: [web/backend/app/api/system.py:626]

获取系统运行日志

参数:
- filter_errors: 是否只显示有问题的日志 (WARNING/ERROR/CRITICAL)
- limit: 返回条数限制 (1-1000)
- offset: 偏移量，用于分页
- level: 日志级别筛选
- category: 日志分类筛选

返回:
- 系统运行日志列表，包含时间戳、级别、分类、操作、消息等信息

示例:
- GET /api/system/logs - 获取所有日志
- GET /api/system/logs?filter_errors=true - 只获取有问题的日志
- GET /api/system/logs?level=ERROR - 只获取ERROR级别日志
- GET /api/system/logs?category=database - 只获取数据库相关日志

**装饰器**: `@router.get`

##### `get_logs_summary()` → `None`

**位置**: [web/backend/app/api/system.py:683]

获取日志统计摘要

返回:
- 总日志数
- 各级别日志数量
- 各分类日志数量
- 最近错误数

**装饰器**: `@router.get`

---

### web.backend.app.core.config

**文件**: `web/backend/app/core/config.py`

**说明**:

应用配置管理

#### 类

##### `Settings`

应用配置

**继承**: `BaseSettings`

#### 函数

##### `get_mysql_connection_string()` → `str`

**位置**: [web/backend/app/core/config.py:84]

##### `get_postgresql_connection_string()` → `str`

**位置**: [web/backend/app/core/config.py:90]

##### `get_tdengine_connection_string()` → `str`

**位置**: [web/backend/app/core/config.py:93]

##### `get_redis_connection_string()` → `str`

**位置**: [web/backend/app/core/config.py:96]

---

### web.backend.app.core.database

**文件**: `web/backend/app/core/database.py`

**说明**:

数据库连接管理
复用现有 MyStocks 数据库连接

#### 类

##### `DatabaseService`

数据库服务类

**方法**:

- `__init__(self)` → `None` [web/backend/app/core/database.py:156]
- `query_stocks_basic(self, limit: int = 100)` → `pd.DataFrame` [web/backend/app/core/database.py:162]
  - 查询股票基本信息
- `query_daily_kline(self, symbol: str, start_date: str, end_date: str)` → `pd.DataFrame` [web/backend/app/core/database.py:181]
  - 查询日线数据
- `get_cache_data(self, key: str)` → `Optional[Any]` [web/backend/app/core/database.py:212]
  - 获取缓存数据
- `set_cache_data(self, key: str, data: Any, ttl: int = None)` → `bool` [web/backend/app/core/database.py:228]
  - 设置缓存数据

#### 函数

##### `get_mysql_engine()` → `None`

**位置**: [web/backend/app/core/database.py:28]

获取 MySQL 数据库引擎

##### `get_postgresql_engine()` → `None`

**位置**: [web/backend/app/core/database.py:42]

获取 PostgreSQL 数据库引擎

##### `get_tdengine_engine()` → `None`

**位置**: [web/backend/app/core/database.py:56]

获取 TDengine 数据库引擎

##### `get_mysql_session()` → `Session`

**位置**: [web/backend/app/core/database.py:75]

获取 MySQL 会话

##### `get_postgresql_session()` → `Session`

**位置**: [web/backend/app/core/database.py:82]

获取 PostgreSQL 会话

##### `get_redis_client()` → `None`

**位置**: [web/backend/app/core/database.py:89]

获取 Redis 客户端

##### `close_all_connections()` → `None`

**位置**: [web/backend/app/core/database.py:111]

关闭所有数据库连接

##### `get_db()` → `Session`

**位置**: [web/backend/app/core/database.py:248]

获取数据库会话（用于FastAPI依赖注入）

---

### web.backend.app.models.__init__

**文件**: `web/backend/app/models/__init__.py`

---

### web.backend.app.models.indicator_config

**文件**: `web/backend/app/models/indicator_config.py`

**说明**:

SQLAlchemy Model for Indicator Configurations
指标配置的数据库模型

#### 类

##### `IndicatorConfiguration`

用户指标配置表

对应 table_config.yaml 中的 indicator_configurations 表

**继承**: `Base`

**方法**:

- `__repr__(self)` → `None` [web/backend/app/models/indicator_config.py:71]
- `to_dict(self)` → `None` [web/backend/app/models/indicator_config.py:77]
  - 转换为字典格式

---

### web.backend.app.models.market_data

**文件**: `web/backend/app/models/market_data.py`

**说明**:

市场数据模型 (SQLAlchemy ORM)

包含4个核心实体:
- FundFlow: 个股资金流向
- ETFData: ETF基金数据
- ChipRaceData: 竞价抢筹数据
- LongHuBangData: 龙虎榜数据

#### 类

##### `FundFlow`

个股资金流向表

**继承**: `Base`

**方法**:

- `to_dict(self)` → `None` [web/backend/app/models/market_data.py:39]
  - 转换为字典

##### `ETFData`

ETF实时数据表

**继承**: `Base`

**方法**:

- `to_dict(self)` → `None` [web/backend/app/models/market_data.py:83]
  - 转换为字典

##### `ChipRaceData`

竞价抢筹数据表

**继承**: `Base`

**方法**:

- `to_dict(self)` → `None` [web/backend/app/models/market_data.py:131]
  - 转换为字典

##### `LongHuBangData`

龙虎榜详细数据表

**继承**: `Base`

**方法**:

- `to_dict(self)` → `None` [web/backend/app/models/market_data.py:174]
  - 转换为字典

---

### web.backend.app.models.task

**文件**: `web/backend/app/models/task.py`

**说明**:

任务管理数据模型
定义任务的数据结构和状态

#### 类

##### `TaskType`

任务类型枚举

**继承**: `str`, `Enum`

##### `TaskStatus`

任务状态枚举

**继承**: `str`, `Enum`

##### `TaskPriority`

任务优先级

**继承**: `int`, `Enum`

##### `TaskSchedule`

任务调度配置

**继承**: `BaseModel`

##### `TaskConfig`

任务配置

**继承**: `BaseModel`

##### `TaskExecution`

任务执行记录

**继承**: `BaseModel`

##### `TaskStatistics`

任务统计信息

**继承**: `BaseModel`

##### `TaskResponse`

任务响应模型

**继承**: `BaseModel`

---

### web.backend.app.models.wencai_data

**文件**: `web/backend/app/models/wencai_data.py`

**说明**:

问财数据ORM模型

定义问财查询和结果的数据库模型

作者: MyStocks Backend Team
创建日期: 2025-10-17

#### 类

##### `WencaiQuery`

问财查询定义表

存储预定义的查询语句配置

**继承**: `Base`

**方法**:

- `__repr__(self)` → `None` [web/backend/app/models/wencai_data.py:58]
- `to_dict(self)` → `None` [web/backend/app/models/wencai_data.py:61]
  - 转换为字典

##### `WencaiResultBase`

问财查询结果基类（抽象类）

用于动态创建查询结果表（wencai_qs_1 ~ wencai_qs_9）
注意：实际的结果表会根据问财API返回的数据动态创建，
      因为不同查询返回的字段不同

共同字段：
- id: 主键
- fetch_time: 数据获取时间
- 取数区间: 查询时间范围
- 其他字段: 根据问财API返回动态添加

**方法**:

- `__tablename__(cls)` → `None` [web/backend/app/models/wencai_data.py:90]
  - 动态表名
- `__table_args__(cls)` → `None` [web/backend/app/models/wencai_data.py:100]
  - 表配置

---

### web.backend.app.schemas.indicator_response

**文件**: `web/backend/app/schemas/indicator_response.py`

**说明**:

Pydantic Response Schemas for Indicator API
定义指标计算API的响应数据模型

#### 类

##### `IndicatorValueOutput`

单个指标的输出值

Example:
    {
        "output_name": "sma",
        "values": [10.5, 11.2, 10.8, ...],
        "display_name": "SMA(20)"
    }

**继承**: `BaseModel`

##### `IndicatorResult`

单个指标的计算结果

Example:
    {
        "abbreviation": "SMA",
        "parameters": {"timeperiod": 20},
        "outputs": [
            {
                "output_name": "sma",
                "values": [10.5, 11.2, ...],
                "display_name": "SMA(20)"
            }
        ],
        "panel_type": "overlay",
        "reference_lines": null,
        "error": null
    }

**继承**: `BaseModel`

##### `OHLCVData`

OHLCV K线数据

Example:
    {
        "dates": ["2024-01-01", "2024-01-02", ...],
        "open": [10.5, 10.8, ...],
        "high": [11.0, 11.5, ...],
        "low": [10.2, 10.5, ...],
        "close": [10.8, 11.2, ...],
        "volume": [1000000, 1200000, ...],
        "turnover": [10800000, 12544000, ...]
    }

**继承**: `BaseModel`

##### `IndicatorCalculateResponse`

指标计算响应

Example:
    {
        "symbol": "600519.SH",
        "symbol_name": "贵州茅台",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "ohlcv": {
            "dates": [...],
            "open": [...],
            ...
        },
        "indicators": [
            {
                "abbreviation": "SMA",
                "parameters": {"timeperiod": 20},
                "outputs": [...],
                "panel_type": "overlay",
                "reference_lines": null,
                "error": null
            }
        ],
        "calculation_time_ms": 15.5,
        "cached": false
    }

**继承**: `BaseModel`

##### `IndicatorMetadata`

指标元数据

Example:
    {
        "abbreviation": "SMA",
        "full_name": "Simple Moving Average",
        "chinese_name": "简单移动平均线",
        "category": "trend",
        "description": "计算收盘价的算术平均值",
        "panel_type": "overlay",
        "parameters": [
            {
                "name": "timeperiod",
                "type": "int",
                "default": 20,
                "min": 2,
                "max": 200,
                "description": "周期"
            }
        ],
        "outputs": [
            {
                "name": "sma",
                "description": "SMA值"
            }
        ],
        "reference_lines": null,
        "min_data_points_formula": "timeperiod"
    }

**继承**: `BaseModel`

##### `IndicatorRegistryResponse`

指标注册表响应

Example:
    {
        "total_count": 161,
        "categories": {
            "trend": 15,
            "momentum": 20,
            "volatility": 10,
            "volume": 8,
            "candlestick": 61
        },
        "indicators": [
            {...},
            {...}
        ]
    }

**继承**: `BaseModel`

##### `IndicatorConfigResponse`

指标配置响应

Example:
    {
        "id": 1,
        "user_id": 123,
        "name": "我的常用配置",
        "indicators": [
            {"abbreviation": "MA", "parameters": {"timeperiod": 20}},
            {"abbreviation": "RSI", "parameters": {"timeperiod": 14}}
        ],
        "created_at": "2024-01-01T10:00:00",
        "updated_at": "2024-01-02T15:30:00",
        "last_used_at": "2024-01-03T09:00:00"
    }

**继承**: `BaseModel`

##### `IndicatorConfigListResponse`

指标配置列表响应

Example:
    {
        "total_count": 5,
        "configs": [
            {...},
            {...}
        ]
    }

**继承**: `BaseModel`

##### `ErrorDetail`

错误详情

Example:
    {
        "error_code": "INSUFFICIENT_DATA",
        "error_message": "指标 SMA(200) 需要至少 200 个数据点",
        "details": {
            "indicator": "SMA",
            "required_points": 200,
            "actual_points": 150
        }
    }

**继承**: `BaseModel`

##### `APIResponse`

通用API响应包装器

Example:
    {
        "success": true,
        "data": {...},
        "error": null,
        "timestamp": "2024-01-01T10:00:00"
    }

**继承**: `BaseModel`

---

### web.backend.app.services.market_data_service

**文件**: `web/backend/app/services/market_data_service.py`

**说明**:

市场数据服务 (MarketDataService)

业务逻辑层,负责:
1. 数据获取: 调用adapters获取外部数据
2. 数据存储: 保存到PostgreSQL+TimescaleDB
3. 数据查询: 从数据库读取历史数据
4. 数据刷新: 定时更新最新数据

复用组件:
- akshare_extension: ETF/资金流向/龙虎榜数据
- tqlex_adapter: 竞价抢筹数据

#### 类

##### `MarketDataService`

市场数据服务

**方法**:

- `__init__(self)` → `None` [web/backend/app/services/market_data_service.py:32]
  - 初始化数据库连接
- `_build_db_url(self)` → `str` [web/backend/app/services/market_data_service.py:48]
  - 从环境变量构建数据库URL
- `fetch_and_save_fund_flow(self, symbol: str, timeframe: str = "1")` → `Dict[(str, Any)]` [web/backend/app/services/market_data_service.py:60]
  - 获取并保存资金流向数据
- `query_fund_flow(self, symbol: str, timeframe: str = "1", start_date: Optional[date] = None, end_date: Optional[date] = None)` → `List[FundFlow]` [web/backend/app/services/market_data_service.py:125]
  - 查询资金流向历史数据
- `fetch_and_save_etf_spot(self)` → `Dict[(str, Any)]` [web/backend/app/services/market_data_service.py:165]
  - 获取并保存ETF实时数据(全市场)
- `query_etf_spot(self, symbol: Optional[str] = None, keyword: Optional[str] = None, limit: int = 50)` → `List[ETFData]` [web/backend/app/services/market_data_service.py:250]
  - 查询ETF数据
- `fetch_and_save_chip_race(self, race_type: str = "open", trade_date: Optional[str] = None)` → `Dict[(str, Any)]` [web/backend/app/services/market_data_service.py:291]
  - 获取并保存竞价抢筹数据
- `query_chip_race(self, race_type: str = "open", trade_date: Optional[date] = None, min_race_amount: Optional[float] = None, limit: int = 100)` → `List[ChipRaceData]` [web/backend/app/services/market_data_service.py:363]
  - 查询竞价抢筹数据
- `fetch_and_save_lhb_detail(self, trade_date: str)` → `Dict[(str, Any)]` [web/backend/app/services/market_data_service.py:403]
  - 获取并保存龙虎榜数据
- `query_lhb_detail(self, symbol: Optional[str] = None, start_date: Optional[date] = None, end_date: Optional[date] = None, min_net_amount: Optional[float] = None, limit: int = 100)` → `List[LongHuBangData]` [web/backend/app/services/market_data_service.py:463]
  - 查询龙虎榜数据

#### 函数

##### `get_market_data_service()` → `MarketDataService`

**位置**: [web/backend/app/services/market_data_service.py:510]

获取市场数据服务单例

---

### web.backend.app.services.wencai_service

**文件**: `web/backend/app/services/wencai_service.py`

**说明**:

问财数据服务

业务逻辑层：
  1. 数据获取和清理
  2. 去重和存储
  3. 查询结果管理
  4. 历史数据统计

作者: MyStocks Backend Team
创建日期: 2025-10-17

#### 类

##### `WencaiService`

问财数据服务

提供问财数据的完整业务逻辑

**方法**:

- `__init__(self, db: Session = None)` → `None` [web/backend/app/services/wencai_service.py:54]
  - 初始化服务
- `_get_safe_table_name(query_name: str)` → `str` [web/backend/app/services/wencai_service.py:71]
  - 从白名单获取安全的表名，防止 SQL 注入
- `get_all_queries(self)` → `List[Dict[(str, Any)]]` [web/backend/app/services/wencai_service.py:89]
  - 获取所有查询列表
- `get_query_by_name(self, query_name: str)` → `Optional[Dict[(str, Any)]]` [web/backend/app/services/wencai_service.py:103]
  - 根据名称获取查询
- `fetch_and_save(self, query_name: str, pages: int = 1)` → `Dict[(str, Any)]` [web/backend/app/services/wencai_service.py:122]
  - 获取并保存查询结果（核心方法）
- `_save_to_database(self, data: pd.DataFrame, query_name: str)` → `Dict[(str, Any)]` [web/backend/app/services/wencai_service.py:201]
  - 保存数据到MySQL并去重
- `get_query_results(self, query_name: str, limit: int = 100, offset: int = 0)` → `Dict[(str, Any)]` [web/backend/app/services/wencai_service.py:287]
  - 获取查询结果
- `get_query_history(self, query_name: str, days: int = 7)` → `Dict[(str, Any)]` [web/backend/app/services/wencai_service.py:354]
  - 获取查询历史统计
- `close(self)` → `None` [web/backend/app/services/wencai_service.py:430]
  - 关闭资源

#### 函数

##### `get_wencai_service(db: Session = None)` → `WencaiService`

**位置**: [web/backend/app/services/wencai_service.py:438]

获取WencaiService实例

Args:
    db: 数据库会话

Returns:
    WencaiService实例

---

### web.backend.celeryconfig_wencai

**文件**: `web/backend/celeryconfig_wencai.py`

**说明**:

问财功能Celery配置示例

将以下配置添加到现有的celeryconfig.py文件中

作者: MyStocks Backend Team
创建日期: 2025-10-17

---

### web.backend.setup_database

**文件**: `web/backend/setup_database.py`

**说明**:

MyStocks数据库初始化脚本
功能:
1. 验证TimescaleDB扩展
2. 创建所有PostgreSQL表
3. 创建所有MySQL表

#### 类

##### `DatabaseSetup`

**方法**:

- `__init__(self)` → `None` [web/backend/setup_database.py:22]
- `verify_timescaledb(self)` → `None` [web/backend/setup_database.py:42]
  - 验证TimescaleDB扩展是否已安装
- `create_postgresql_tables(self)` → `None` [web/backend/setup_database.py:85]
  - 创建PostgreSQL表
- `create_mysql_tables(self)` → `None` [web/backend/setup_database.py:168]
  - 创建MySQL表
- `run(self)` → `None` [web/backend/setup_database.py:223]
  - 执行完整的数据库设置流程

---
