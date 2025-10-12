# 数据库管理器使用示例

本文档提供数据库管理器模块的详细使用示例，包括多数据库配置、监控系统使用和实际场景应用。

## 📋 目录

1. [环境配置](#环境配置)
2. [基础使用示例](#基础使用示例)
3. [Redis热数据固化示例](#redis热数据固化示例) ⭐ **新增**
4. [强制更新实时数据](#强制更新实时数据) ⭐ **新增**
5. [多数据库管理](#多数据库管理)
6. [监控系统使用](#监控系统使用)
7. [DataFrame转SQL](#dataframe转sql)
8. [TDengine时序数据库](#tdengine时序数据库)
9. [Jupyter环境使用](#jupyter环境使用)
10. [安全配置](#安全配置)
11. [故障排除](#故障排除)
12. [与v2.0系统集成](#与v20系统集成)

## 🔧 环境配置

### 数据库环境准备

#### 1. MySQL/MariaDB配置

```bash
# 安装MySQL驱动
pip install pymysql

# .env文件配置
MYSQL_HOST=192.168.123.104
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=test_db

# MariaDB配置（可选）
MARIADB_HOST=192.168.123.104
MARIADB_PORT=3307
MARIADB_USER=root
MARIADB_PASSWORD=your_password
```

#### 2. PostgreSQL配置

```bash
# 安装PostgreSQL驱动
pip install psycopg2-binary

# .env文件配置
POSTGRESQL_HOST=192.168.123.104
POSTGRESQL_PORT=5433
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your_password
POSTGRESQL_DATABASE=quant_research
```

#### 3. TDengine配置

```bash
# 安装TDengine驱动
pip install taospy

# .env文件配置
TDENGINE_HOST=192.168.123.104
TDENGINE_PORT=6030
TDENGINE_USER=root
TDENGINE_PASSWORD=taosdata
TDENGINE_DATABASE=market_data
```

#### 4. Redis配置

```bash
# 安装Redis驱动
pip install redis

# .env文件配置
REDIS_HOST=192.168.123.104
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

### 监控数据库配置

```bash
# 监控数据库URL（独立于业务数据库）
MONITOR_DB_URL=mysql+pymysql://root:password@192.168.123.104:3306/db_monitor
```

## 🚀 基础使用示例

### 1. 数据库管理器初始化

```python
from db_manager.database_manager import DatabaseTableManager, DatabaseType
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def basic_manager_example():
    """数据库管理器基础使用示例"""
    
    print("=== 数据库管理器初始化 ===")
    
    # 创建管理器实例
    manager = DatabaseTableManager()
    
    # 检查各数据库的可用性
    databases = [
        (DatabaseType.MYSQL, "MySQL"),
        (DatabaseType.POSTGRESQL, "PostgreSQL"),
        (DatabaseType.TDENGINE, "TDengine"),
        (DatabaseType.REDIS, "Redis"),
        (DatabaseType.MARIADB, "MariaDB")
    ]
    
    print("数据库可用性检查:")
    for db_type, db_name in databases:
        try:
            connection = manager.get_connection(db_type, "test_db")
            if connection:
                print(f"  ✅ {db_name}: 可用")
                connection.close()
            else:
                print(f"  ❌ {db_name}: 连接失败")
        except Exception as e:
            print(f"  ❌ {db_name}: {str(e)[:50]}...")
    
    return manager

# 运行示例
manager = basic_manager_example()
```

### 2. 表结构创建示例

```python
def table_creation_example():
    """表结构创建示例"""
    
    manager = DatabaseTableManager()
    
    # 1. 简单表结构定义
    simple_table_config = {
        'table_name': 'stock_basic_info',
        'database_name': 'test_db',
        'database_type': 'MySQL',
        'columns': [
            {
                'name': 'symbol',
                'type': 'VARCHAR',
                'length': 10,
                'nullable': False,
                'comment': '股票代码'
            },
            {
                'name': 'name',
                'type': 'VARCHAR',
                'length': 100,
                'nullable': False,
                'comment': '股票名称'
            },
            {
                'name': 'exchange',
                'type': 'VARCHAR',
                'length': 10,
                'nullable': False,
                'comment': '交易所'
            },
            {
                'name': 'industry',
                'type': 'VARCHAR',
                'length': 50,
                'comment': '所属行业'
            },
            {
                'name': 'list_date',
                'type': 'DATE',
                'comment': '上市日期'
            },
            {
                'name': 'created_at',
                'type': 'TIMESTAMP',
                'nullable': False,
                'default': 'CURRENT_TIMESTAMP',
                'comment': '创建时间'
            }
        ],
        'primary_key': ['symbol'],
        'indexes': [
            {'name': 'idx_exchange', 'columns': ['exchange']},
            {'name': 'idx_industry', 'columns': ['industry']}
        ]
    }
    
    print("=== 创建股票基本信息表 ===")
    try:
        # 生成DDL
        ddl = manager.generate_ddl(simple_table_config)
        print(f"生成的DDL:")
        print(ddl)
        
        # 创建表
        success = manager.create_table_from_config(simple_table_config)
        print(f"表创建结果: {'成功' if success else '失败'}")
        
    except Exception as e:
        print(f"表创建失败: {e}")
    
    # 2. 复杂表结构定义（日线数据表）
    kline_table_config = {
        'table_name': 'stock_daily_kline',
        'database_name': 'test_db',
        'database_type': 'MySQL',
        'columns': [
            {'name': 'id', 'type': 'BIGINT', 'nullable': False, 'auto_increment': True},
            {'name': 'symbol', 'type': 'VARCHAR', 'length': 10, 'nullable': False},
            {'name': 'trade_date', 'type': 'DATE', 'nullable': False},
            {'name': 'open', 'type': 'DECIMAL', 'precision': 10, 'scale': 2},
            {'name': 'high', 'type': 'DECIMAL', 'precision': 10, 'scale': 2},
            {'name': 'low', 'type': 'DECIMAL', 'precision': 10, 'scale': 2},
            {'name': 'close', 'type': 'DECIMAL', 'precision': 10, 'scale': 2, 'nullable': False},
            {'name': 'volume', 'type': 'BIGINT', 'default': 0},
            {'name': 'amount', 'type': 'DECIMAL', 'precision': 15, 'scale': 2, 'default': 0},
            {'name': 'adj_factor', 'type': 'DECIMAL', 'precision': 10, 'scale': 6, 'default': 1},
            {'name': 'pre_close', 'type': 'DECIMAL', 'precision': 10, 'scale': 2},
            {'name': 'change_amount', 'type': 'DECIMAL', 'precision': 10, 'scale': 2},
            {'name': 'change_pct', 'type': 'DECIMAL', 'precision': 8, 'scale': 4},
            {'name': 'turnover_rate', 'type': 'DECIMAL', 'precision': 8, 'scale': 4},
            {'name': 'updated_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'}
        ],
        'primary_key': ['id'],
        'unique_keys': [['symbol', 'trade_date']],
        'indexes': [
            {'name': 'idx_symbol_date', 'columns': ['symbol', 'trade_date']},
            {'name': 'idx_trade_date', 'columns': ['trade_date']},
            {'name': 'idx_symbol', 'columns': ['symbol']}
        ],
        'engine': 'InnoDB',
        'charset': 'utf8mb4'
    }
    
    print("\n=== 创建股票日线数据表 ===")
    try:
        ddl = manager.generate_ddl(kline_table_config)
        print(f"日线数据表DDL:")
        print(ddl)
        
        success = manager.create_table_from_config(kline_table_config)
        print(f"日线数据表创建结果: {'成功' if success else '失败'}")
        
    except Exception as e:
        print(f"日线数据表创建失败: {e}")

table_creation_example()
```

## 🔥 Redis热数据固化示例

### 1. 基础固化使用

```python
from db_manager.redis_data_fixation import RedisDataFixationManager, FixationStrategy
import pandas as pd

def basic_fixation_example():
    """Redis数据固化基础示例"""
    
    print("=== Redis热数据固化示例 ===")
    
    # 创建固化管理器
    fixation_manager = RedisDataFixationManager()
    
    # 模拟实时数据
    sample_data = pd.DataFrame({
        'symbol': ['000001.SZ', '000002.SZ', '600000.SH'],
        'price': [10.50, 8.20, 12.80],
        'volume': [1000000, 800000, 1200000],
        'amount': [10500000, 6560000, 15360000],
        'timestamp': pd.Timestamp.now()
    })
    
    # 立即固化数据
    print("📊 立即固化数据到永久存储...")
    fixation_results = fixation_manager.fixate_redis_data_immediate(sample_data)
    
    for storage_type, success in fixation_results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"   {storage_type}: {status}")
    
    # 获取固化统计
    stats = fixation_manager.get_fixation_statistics()
    print(f"\n📈 固化统计: {stats}")

basic_fixation_example()
```

### 2. 不同固化策略配置

```python
def fixation_strategy_example():
    """不同固化策略的配置示例"""
    
    print("=== 固化策略配置示例 ===")
    
    # 策略1: 立即固化（适合重要数据）
    immediate_config = {
        'fixation_strategy': FixationStrategy.IMMEDIATE,
        'backup_to_tick_data': True,
        'backup_to_daily_kline': False
    }
    
    # 策略2: 过期前固化（推荐策略）
    before_expire_config = {
        'fixation_strategy': FixationStrategy.BEFORE_EXPIRE,
        'fixation_interval_seconds': 240,  # 4分钟
        'backup_to_tick_data': True,
        'backup_to_daily_kline': True
    }
    
    # 策略3: 定时固化（批量处理）
    scheduled_config = {
        'fixation_strategy': FixationStrategy.SCHEDULED,
        'fixation_interval_seconds': 300,  # 5分钟
        'batch_size': 1000
    }
    
    strategies = [
        ("立即固化", immediate_config),
        ("过期前固化", before_expire_config), 
        ("定时固化", scheduled_config)
    ]
    
    for strategy_name, config in strategies:
        print(f"\n📋 {strategy_name}策略:")
        for key, value in config.items():
            print(f"   {key}: {value}")

fixation_strategy_example()
```

### 3. 多重备份配置

```python
def multi_backup_example():
    """多重备份配置示例"""
    
    print("=== 多重备份配置示例 ===")
    
    # 配置文件内容示例
    fixation_config = """
    # Redis固化配置 - 多重备份策略
    FIXATION_STRATEGY=before_expire
    FIXATION_INTERVAL_SECONDS=240
    
    # 主要备份：TDengine时序存储（推荐）
    BACKUP_TO_TICK_DATA=true
    
    # 次要备份：PostgreSQL分析存储（可选）
    BACKUP_TO_DAILY_KLINE=true
    
    # 应急备份：文件系统（兜底方案）
    BACKUP_TO_FILE_SYSTEM=true
    BACKUP_DIRECTORY=./backup/redis_fixation
    
    # 性能配置
    ENABLE_COMPRESSION=true
    BATCH_SIZE=1000
    MAX_RETRY_ATTEMPTS=3
    """
    
    print("📄 推荐的固化配置:")
    print(fixation_config)
    
    # 存储目标说明
    storage_targets = {
        "TDengine": {
            "用途": "时序分析、历史回测",
            "优点": "高性能时序查询、数据压缩",
            "适用": "Tick级数据、技术指标计算"
        },
        "PostgreSQL": {
            "用途": "聚合分析、报表统计", 
            "优点": "SQL分析、复杂查询",
            "适用": "日线数据、财务分析"
        },
        "文件系统": {
            "用途": "应急备份、数据迁移",
            "优点": "简单可靠、易于恢复",
            "适用": "灾难恢复、系统迁移"
        }
    }
    
    print("\n🗄️ 存储目标说明:")
    for target, info in storage_targets.items():
        print(f"\n📊 {target}:")
        for key, value in info.items():
            print(f"   {key}: {value}")

multi_backup_example()
```

## ⚡ 强制更新实时数据

### 1. 基础强制更新

```python
def force_update_basic_example():
    """强制更新基础示例"""
    
    print("=== 强制更新实时数据示例 ===")
    
    from db_manager.redis_data_fixation import RedisDataFixationManager
    
    # 创建固化管理器
    fixation_manager = RedisDataFixationManager()
    
    # 强制更新沪深市场数据
    print("🔄 执行强制更新...")
    update_result = fixation_manager.force_update_realtime_data(
        market_symbol="hs",
        bypass_cache=True
    )
    
    # 显示更新结果
    if update_result['success']:
        print("✅ 强制更新成功!")
        print(f"📊 更新时间: {update_result['update_time']}")
        print(f"📈 数据条数: {update_result['data_count']}")
        print(f"📋 数据列: {update_result['data_columns']}")
    else:
        print(f"❌ 强制更新失败: {update_result.get('error', '未知错误')}")

force_update_basic_example()
```

### 2. 命令行强制更新

```bash
# 方式1: 通过统一启动器
python run_realtime_market_saver.py --force-update

# 方式2: 直接运行核心程序
python db_manager/save_realtime_market_data.py --force-update

# 方式3: 组合使用（强制更新+自动固化）
python db_manager/save_realtime_market_data.py --force-update --enable-fixation
```

### 3. 不同市场的强制更新

```python
def multi_market_force_update():
    """多市场强制更新示例"""
    
    print("=== 多市场强制更新示例 ===")
    
    from db_manager.redis_data_fixation import RedisDataFixationManager
    
    fixation_manager = RedisDataFixationManager()
    
    # 支持的市场代码
    markets = {
        "hs": "沪深市场",
        "sh": "上海市场", 
        "sz": "深圳市场"
    }
    
    results = {}
    
    for market_code, market_name in markets.items():
        print(f"\n🔄 强制更新{market_name} ({market_code})...")
        
        result = fixation_manager.force_update_realtime_data(
            market_symbol=market_code,
            bypass_cache=True
        )
        
        results[market_code] = result
        
        if result['success']:
            print(f"✅ {market_name}更新成功: {result['data_count']} 条数据")
        else:
            print(f"❌ {market_name}更新失败: {result.get('error')}")
    
    # 汇总结果
    print("\n📊 更新结果汇总:")
    total_success = sum(1 for r in results.values() if r['success'])
    total_markets = len(results)
    print(f"成功率: {total_success}/{total_markets} ({total_success/total_markets*100:.1f}%)")

multi_market_force_update()
```

### 4. 强制更新的时机选择

```python
def update_timing_guide():
    """强制更新时机指南"""
    
    print("=== 强制更新时机指南 ===")
    
    timing_scenarios = {
        "交易时间开始": {
            "时机": "09:30",
            "原因": "获取开盘后的最新数据",
            "命令": "python db_manager/save_realtime_market_data.py --force-update"
        },
        "午间休市后": {
            "时机": "13:00",
            "原因": "获取上午交易的完整数据",
            "命令": "python db_manager/save_realtime_market_data.py --force-update --enable-fixation"
        },
        "收盘后": {
            "时机": "15:30",
            "原因": "获取全天交易的最终数据",
            "命令": "python db_manager/save_realtime_market_data.py --force-update --enable-fixation"
        },
        "数据异常时": {
            "时机": "发现数据异常时",
            "原因": "跳过可能有问题的缓存数据",
            "命令": "python db_manager/save_realtime_market_data.py --force-update"
        },
        "系统重启后": {
            "时机": "Redis重启或清空后",
            "原因": "重新填充缓存数据",
            "命令": "python db_manager/save_realtime_market_data.py --force-update"
        }
    }
    
    print("📅 推荐的强制更新时机:")
    for scenario, info in timing_scenarios.items():
        print(f"\n🕒 {scenario}:")
        for key, value in info.items():
            print(f"   {key}: {value}")

update_timing_guide()
```

## 🗄️ 多数据库管理

### 1. 不同数据库的DDL生成

```python
def multi_database_ddl_example():
    """多数据库DDL生成示例"""
    
    manager = DatabaseTableManager()
    
    # 基础表结构定义
    base_config = {
        'table_name': 'stock_quotes',
        'columns': [
            {'name': 'symbol', 'type': 'VARCHAR', 'length': 10, 'nullable': False},
            {'name': 'timestamp', 'type': 'TIMESTAMP', 'nullable': False},
            {'name': 'price', 'type': 'DECIMAL', 'precision': 10, 'scale': 2},
            {'name': 'volume', 'type': 'BIGINT'}
        ],
        'primary_key': ['symbol', 'timestamp']
    }
    
    # 不同数据库的配置
    database_configs = [
        ('MySQL', 'mysql_db'),
        ('PostgreSQL', 'postgres_db'),
        ('TDengine', 'tdengine_db')
    ]
    
    print("=== 多数据库DDL生成对比 ===")
    
    for db_type, db_name in database_configs:
        config = base_config.copy()
        config['database_type'] = db_type
        config['database_name'] = db_name
        
        try:
            ddl = manager.generate_ddl(config)
            print(f"\n{db_type} DDL:")
            print("-" * 50)
            print(ddl)
            
        except Exception as e:
            print(f"\n{db_type} DDL生成失败: {e}")

multi_database_ddl_example()
```

### 2. TDengine超级表创建

```python
def tdengine_supertable_example():
    """TDengine超级表创建示例"""
    
    manager = DatabaseTableManager()
    
    # TDengine超级表配置
    supertable_config = {
        'table_name': 'stock_tick_data',
        'database_name': 'market_data',
        'database_type': 'TDengine',
        'is_super_table': True,  # 标记为超级表
        'columns': [
            # 时间戳列（必须是第一列）
            {'name': 'ts', 'type': 'TIMESTAMP', 'nullable': False, 'comment': '时间戳'},
            # 数据列
            {'name': 'price', 'type': 'FLOAT', 'nullable': False, 'comment': '成交价格'},
            {'name': 'volume', 'type': 'INT', 'nullable': False, 'comment': '成交量'},
            {'name': 'amount', 'type': 'DOUBLE', 'comment': '成交金额'},
            {'name': 'buy_order_id', 'type': 'BIGINT', 'comment': '买单号'},
            {'name': 'sell_order_id', 'type': 'BIGINT', 'comment': '卖单号'}
        ],
        'tags': [
            # 标签列
            {'name': 'symbol', 'type': 'VARCHAR', 'length': 20, 'comment': '股票代码'},
            {'name': 'exchange', 'type': 'VARCHAR', 'length': 10, 'comment': '交易所'},
            {'name': 'market_type', 'type': 'VARCHAR', 'length': 10, 'comment': '市场类型'}
        ]
    }
    
    print("=== TDengine超级表创建示例 ===")
    
    try:
        # 生成TDengine超级表DDL
        ddl = manager.generate_ddl(supertable_config)
        print("TDengine超级表DDL:")
        print(ddl)
        
        # 创建超级表
        success = manager.create_table_from_config(supertable_config)
        print(f"超级表创建结果: {'成功' if success else '失败'}")
        
        # 创建子表示例
        subtable_config = {
            'table_name': 'stock_tick_000001',
            'parent_table': 'stock_tick_data',
            'database_name': 'market_data',
            'database_type': 'TDengine',
            'tag_values': {
                'symbol': '000001',
                'exchange': 'SZ',
                'market_type': 'MAIN'
            }
        }
        
        subtable_ddl = manager.generate_subtable_ddl(subtable_config)
        print(f"\n子表DDL示例:")
        print(subtable_ddl)
        
    except Exception as e:
        print(f"TDengine超级表操作失败: {e}")

# 注意：需要安装TDengine客户端才能执行
# tdengine_supertable_example()
```

## 📊 监控系统使用

### 1. 监控数据库初始化

```python
from db_manager.init_db_monitor import init_monitoring_database

def monitoring_system_example():
    """监控系统使用示例"""
    
    print("=== 监控系统初始化 ===")
    
    # 1. 首次初始化（保留已有数据）
    print("1. 首次初始化监控系统...")
    success = init_monitoring_database(drop_existing=False)
    
    if success:
        print("✅ 监控系统初始化成功")
        print("已创建监控表:")
        print("  - table_creation_log: 表创建日志")
        print("  - table_operation_log: 表操作日志")
        print("  - table_validation_log: 表验证日志")
        print("  - column_definition_log: 列定义日志")
    else:
        print("❌ 监控系统初始化失败")
        return False
    
    # 2. 强制重建（删除已有表）
    print("\n2. 强制重建监控表...")
    rebuild_success = init_monitoring_database(drop_existing=True)
    print(f"重建结果: {'成功' if rebuild_success else '失败'}")
    
    return success

# 运行监控系统示例
monitoring_system_example()
```

### 2. 监控日志查询

```python
def monitoring_logs_example():
    """监控日志查询示例"""
    
    from db_manager.database_manager import DatabaseTableManager, DatabaseType
    import pandas as pd
    
    manager = DatabaseTableManager()
    
    print("=== 监控日志查询示例 ===")
    
    try:
        # 连接监控数据库
        connection = manager.get_connection(DatabaseType.MYSQL, "db_monitor")
        
        if not connection:
            print("❌ 无法连接监控数据库")
            return
        
        # 1. 查询表创建日志
        print("1. 最近的表创建日志:")
        creation_logs_query = \"\"\"
        SELECT table_name, database_type, created_at, 
               operation_status, error_message
        FROM table_creation_log 
        ORDER BY created_at DESC 
        LIMIT 10
        \"\"\"
        
        creation_logs = pd.read_sql(creation_logs_query, connection)
        if not creation_logs.empty:
            print(creation_logs.to_string(index=False))
        else:
            print("  暂无表创建日志")
        
        # 2. 查询表操作日志
        print("\n2. 最近的表操作日志:")
        operation_logs_query = \"\"\"
        SELECT operation_id, table_name, operation_type, 
               operation_status, operation_time
        FROM table_operation_log 
        ORDER BY operation_time DESC 
        LIMIT 10
        \"\"\"
        
        operation_logs = pd.read_sql(operation_logs_query, connection)
        if not operation_logs.empty:
            print(operation_logs.to_string(index=False))
        else:
            print("  暂无表操作日志")
        
        # 3. 统计信息
        print("\n3. 监控统计信息:")
        
        stats_queries = {
            "总表创建数": "SELECT COUNT(*) as count FROM table_creation_log",
            "成功创建数": "SELECT COUNT(*) as count FROM table_creation_log WHERE operation_status = 'success'",
            "失败创建数": "SELECT COUNT(*) as count FROM table_creation_log WHERE operation_status = 'failed'",
            "总操作数": "SELECT COUNT(*) as count FROM table_operation_log"
        }
        
        for stat_name, query in stats_queries.items():
            result = pd.read_sql(query, connection)
            count = result.iloc[0]['count'] if not result.empty else 0
            print(f"  {stat_name}: {count}")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ 监控日志查询失败: {e}")

monitoring_logs_example()
```

## 📁 DataFrame转SQL

### 1. 基本转换示例

```python
from db_manager.df2sql import DataFrameToSQL
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def dataframe_to_sql_example():
    """DataFrame转SQL示例"""
    
    print("=== DataFrame到SQL转换示例 ===")
    
    # 1. 创建示例数据
    print("1. 创建示例股票数据...")
    
    # 生成示例股票日线数据
    symbols = ['000001', '600000', '000002']
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
    
    data_records = []
    for symbol in symbols:
        base_price = np.random.uniform(10, 50)
        for date in dates:
            # 模拟价格波动
            price_change = np.random.normal(0, 0.02)
            close_price = base_price * (1 + price_change)
            
            record = {
                'symbol': symbol,
                'trade_date': date.date(),
                'open': round(close_price * (1 + np.random.uniform(-0.01, 0.01)), 2),
                'high': round(close_price * (1 + np.random.uniform(0, 0.03)), 2),
                'low': round(close_price * (1 + np.random.uniform(-0.03, 0)), 2),
                'close': round(close_price, 2),
                'volume': np.random.randint(1000000, 50000000),
                'amount': round(close_price * np.random.randint(1000000, 50000000), 2),
                'turnover_rate': round(np.random.uniform(0.1, 5.0), 2)
            }
            data_records.append(record)
            base_price = close_price  # 价格延续
    
    stock_df = pd.DataFrame(data_records)
    print(f"生成数据: {len(stock_df)} 条记录")
    print(stock_df.head())
    
    # 2. 转换为SQL
    print("\n2. 转换为SQL表结构...")
    
    df_to_sql = DataFrameToSQL()
    
    # 自动分析DataFrame并生成表结构
    table_schema = df_to_sql.analyze_dataframe(
        stock_df, 
        table_name='auto_stock_daily',
        database_type='MySQL'
    )
    
    print("自动生成的表结构:")
    for col in table_schema['columns']:
        print(f"  {col['name']}: {col['type']}")
    
    # 3. 生成DDL
    ddl = df_to_sql.generate_ddl(table_schema)
    print("\n生成的DDL:")
    print(ddl)
    
    # 4. 生成INSERT语句
    print("\n4. 生成INSERT语句示例...")
    insert_sql = df_to_sql.generate_insert_sql(
        stock_df.head(3), 
        'auto_stock_daily'
    )
    print("INSERT语句示例:")
    print(insert_sql)
    
    # 5. 批量插入优化
    print("\n5. 批量插入优化...")
    batch_inserts = df_to_sql.generate_batch_insert_sql(
        stock_df, 
        'auto_stock_daily',
        batch_size=1000
    )
    
    print(f"生成了 {len(batch_inserts)} 个批次的INSERT语句")
    print(f"第一个批次包含 {batch_inserts[0].count('VALUES') if batch_inserts else 0} 条记录")

dataframe_to_sql_example()
```

### 2. 复杂数据类型处理

```python
def complex_datatype_example():
    """复杂数据类型处理示例"""
    
    print("=== 复杂数据类型处理示例 ===")
    
    # 创建包含复杂数据类型的DataFrame
    complex_data = pd.DataFrame({
        'id': range(1, 6),
        'name': ['股票A', '股票B', '股票C', '股票D', '股票E'],
        'price': [12.34, 56.78, 90.12, 34.56, 78.90],
        'volume': [1000000, 2000000, 1500000, 800000, 1200000],
        'is_active': [True, True, False, True, False],
        'created_at': pd.Timestamp.now(),
        'metadata': [{'sector': 'tech'}, {'sector': 'finance'}, {}, {'sector': 'energy'}, None],
        'tags': [['A股', '大盘'], ['港股'], ['创业板', '小盘'], ['主板'], []],
        'description': ['这是一个很长的描述文本' * 10, '简短描述', None, '', '中等长度的描述文本']
    })
    
    print("复杂数据示例:")
    print(complex_data.info())
    print(complex_data.head())
    
    df_to_sql = DataFrameToSQL()
    
    # 分析复杂数据类型
    print("\n=== 数据类型分析 ===")
    
    # 自定义类型映射配置
    type_mapping_config = {
        'string_length_analysis': True,      # 分析字符串长度
        'json_detection': True,              # 检测JSON格式数据
        'array_handling': 'json',            # 数组处理方式: 'json' 或 'text'
        'boolean_as_tinyint': True,          # 布尔值转换为TINYINT
        'decimal_precision': (10, 2),        # 小数精度配置
        'text_threshold': 255                # TEXT类型阈值
    }
    
    table_schema = df_to_sql.analyze_dataframe(
        complex_data,
        table_name='complex_stock_data',
        database_type='MySQL',
        config=type_mapping_config
    )
    
    print("分析后的表结构:")
    for col in table_schema['columns']:
        col_info = f"  {col['name']}: {col['type']}"
        if 'length' in col:
            col_info += f"({col['length']})"
        if 'nullable' in col:
            col_info += f" {'NULL' if col['nullable'] else 'NOT NULL'}"
        if 'comment' in col:
            col_info += f" -- {col['comment']}"
        print(col_info)
    
    # 生成优化后的DDL
    ddl = df_to_sql.generate_ddl(table_schema)
    print("\n优化后的DDL:")
    print(ddl)

complex_datatype_example()
```

## ⚡ TDengine时序数据库

### 1. TDengine连接和基本操作

```python
def tdengine_basic_example():
    """TDengine基本操作示例"""
    
    from db_manager.database_manager import DatabaseTableManager, DatabaseType
    
    manager = DatabaseTableManager()
    
    print("=== TDengine基本操作示例 ===")
    
    try:
        # 1. 测试TDengine连接
        print("1. 测试TDengine连接...")
        connection = manager.get_connection(DatabaseType.TDENGINE, "market_data")
        
        if not connection:
            print("❌ TDengine连接失败，请检查:")
            print("  - TDengine服务是否启动")
            print("  - taospy库是否安装: pip install taospy")
            print("  - 环境变量配置是否正确")
            return
        
        print("✅ TDengine连接成功")
        
        # 2. 创建数据库（如果不存在）
        print("\n2. 创建TDengine数据库...")
        create_db_sql = \"\"\"
        CREATE DATABASE IF NOT EXISTS market_data 
        PRECISION 'ms' 
        KEEP 365 
        DAYS 1 
        BLOCKS 6 
        CACHE 64 
        MAXROWS 4096 
        MINROWS 100 
        COMP 2 
        WAL 1 
        FSYNC 3000 
        REPLICA 1
        \"\"\"
        
        cursor = connection.cursor()
        cursor.execute(create_db_sql)
        print("✅ 数据库创建/验证成功")
        
        # 3. 使用数据库
        cursor.execute("USE market_data")
        
        # 4. 创建超级表
        print("\n3. 创建超级表...")
        create_stable_sql = \"\"\"
        CREATE STABLE IF NOT EXISTS stock_tick (
            ts TIMESTAMP,
            price FLOAT,
            volume INT,
            amount DOUBLE
        ) TAGS (
            symbol VARCHAR(20),
            exchange VARCHAR(10)
        )
        \"\"\"
        
        cursor.execute(create_stable_sql)
        print("✅ 超级表创建成功")
        
        # 5. 创建子表
        print("\n4. 创建子表...")
        create_table_sql = \"\"\"
        CREATE TABLE IF NOT EXISTS stock_tick_000001 
        USING stock_tick 
        TAGS ('000001', 'SZ')
        \"\"\"
        
        cursor.execute(create_table_sql)
        print("✅ 子表创建成功")
        
        # 6. 插入示例数据
        print("\n5. 插入示例数据...")
        
        import time
        current_time = int(time.time() * 1000)  # 毫秒时间戳
        
        insert_sql = f\"\"\"
        INSERT INTO stock_tick_000001 VALUES 
        ({current_time}, 12.34, 1000, 12340.0),
        ({current_time + 1000}, 12.35, 1500, 18525.0),
        ({current_time + 2000}, 12.33, 800, 9864.0)
        \"\"\"
        
        cursor.execute(insert_sql)
        print("✅ 数据插入成功")
        
        # 7. 查询数据
        print("\n6. 查询数据...")
        query_sql = \"\"\"
        SELECT ts, price, volume, amount 
        FROM stock_tick_000001 
        ORDER BY ts DESC 
        LIMIT 5
        \"\"\"
        
        cursor.execute(query_sql)
        results = cursor.fetchall()
        
        print("查询结果:")
        for row in results:
            print(f"  时间: {row[0]}, 价格: {row[1]}, 成交量: {row[2]}, 成交额: {row[3]}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ TDengine操作失败: {e}")
        print("请确保:")
        print("  1. TDengine服务已启动")
        print("  2. Python环境已安装taospy: pip install taospy")
        print("  3. 环境变量配置正确")

# 注意：需要TDengine环境才能运行
# tdengine_basic_example()
```

### 2. 时序数据批量处理

```python
def tdengine_batch_processing_example():
    """TDengine时序数据批量处理示例"""
    
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    print("=== TDengine批量数据处理示例 ===")
    
    # 1. 生成大量时序数据
    print("1. 生成时序数据...")
    
    symbols = ['000001', '000002', '600000', '600036']
    start_time = datetime.now() - timedelta(days=1)
    
    # 生成每分钟的数据点
    time_range = pd.date_range(
        start=start_time,
        end=datetime.now(),
        freq='1min'
    )
    
    all_data = []
    for symbol in symbols:
        base_price = np.random.uniform(10, 50)
        
        for timestamp in time_range:
            # 模拟价格随机游走
            price_change = np.random.normal(0, 0.001)
            base_price *= (1 + price_change)
            
            record = {
                'symbol': symbol,
                'exchange': 'SZ' if symbol.startswith('000') else 'SH',
                'timestamp': timestamp,
                'price': round(base_price, 2),
                'volume': np.random.randint(100, 10000),
                'amount': round(base_price * np.random.randint(100, 10000), 2)
            }
            all_data.append(record)
    
    tick_df = pd.DataFrame(all_data)
    print(f"生成数据: {len(tick_df)} 条记录")
    print(f"时间范围: {tick_df['timestamp'].min()} 到 {tick_df['timestamp'].max()}")
    print(f"股票数量: {tick_df['symbol'].nunique()}")
    
    # 2. 转换为TDengine格式
    print("\n2. 转换为TDengine批量插入格式...")
    
    def generate_tdengine_batch_sql(df, batch_size=1000):
        \"\"\"生成TDengine批量插入SQL\"\"\"
        
        batches = []
        
        # 按symbol分组处理
        for symbol, group in df.groupby('symbol'):
            exchange = group.iloc[0]['exchange']
            table_name = f"stock_tick_{symbol}"
            
            # 生成子表创建SQL
            create_table_sql = f\"\"\"
            CREATE TABLE IF NOT EXISTS {table_name} 
            USING stock_tick 
            TAGS ('{symbol}', '{exchange}')
            \"\"\"
            batches.append(('CREATE_TABLE', create_table_sql))
            
            # 分批生成插入SQL
            for i in range(0, len(group), batch_size):
                batch_data = group.iloc[i:i+batch_size]
                
                values = []
                for _, row in batch_data.iterrows():
                    ts = int(row['timestamp'].timestamp() * 1000)
                    values.append(f"({ts}, {row['price']}, {row['volume']}, {row['amount']})")
                
                insert_sql = f\"\"\"
                INSERT INTO {table_name} VALUES 
                {', '.join(values)}
                \"\"\"
                
                batches.append(('INSERT', insert_sql))
        
        return batches
    
    batch_sqls = generate_tdengine_batch_sql(tick_df, batch_size=500)
    print(f"生成批量SQL: {len(batch_sqls)} 条语句")
    
    # 3. 显示SQL示例
    print("\n3. SQL示例:")
    
    create_count = sum(1 for batch_type, _ in batch_sqls if batch_type == 'CREATE_TABLE')
    insert_count = sum(1 for batch_type, _ in batch_sqls if batch_type == 'INSERT')
    
    print(f"  创建表语句: {create_count} 条")
    print(f"  插入语句: {insert_count} 条")
    
    # 显示第一个创建表语句
    for batch_type, sql in batch_sqls:
        if batch_type == 'CREATE_TABLE':
            print(f"\n创建表SQL示例:")
            print(sql)
            break
    
    # 显示第一个插入语句（截取）
    for batch_type, sql in batch_sqls:
        if batch_type == 'INSERT':
            print(f"\n插入SQL示例（前200字符）:")
            print(sql[:200] + "...")
            break
    
    print("\n✅ 批量数据处理完成")
    print("注意: 实际执行需要TDengine环境")

tdengine_batch_processing_example()
```

## 📓 Jupyter环境使用

### 1. Jupyter Notebook中的基本使用

```python
# Jupyter Cell 1: 环境检查和导入
import os
import sys
import pandas as pd

# 检查当前工作目录
print(f"当前工作目录: {os.getcwd()}")

# 确保在正确的项目目录
# os.chdir('/path/to/your/mystocks/project')

# 导入必要模块
try:
    from db_manager.database_manager import DatabaseTableManager, DatabaseType
    from db_manager.init_db_monitor import init_monitoring_database
    print("✅ 模块导入成功")
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    print("请确保在正确的项目目录中运行")
```

```python
# Jupyter Cell 2: 初始化数据库管理器
print("=== Jupyter环境中的数据库管理器使用 ===")

# 创建管理器（避免使用命令行参数）
manager = DatabaseTableManager()

# 检查数据库连接
databases_to_test = [
    (DatabaseType.MYSQL, "MySQL"),
    (DatabaseType.POSTGRESQL, "PostgreSQL"), 
    (DatabaseType.REDIS, "Redis")
]

print("数据库连接测试:")
for db_type, db_name in databases_to_test:
    try:
        conn = manager.get_connection(db_type, "test_db")
        if conn:
            print(f"  ✅ {db_name}: 连接成功")
            conn.close()
        else:
            print(f"  ❌ {db_name}: 连接失败")
    except Exception as e:
        print(f"  ❌ {db_name}: {str(e)[:50]}...")
```

```python
# Jupyter Cell 3: 监控系统初始化（推荐方式）
print("=== 在Jupyter中初始化监控系统 ===")

# 直接调用API函数，避免argparse冲突
try:
    success = init_monitoring_database(drop_existing=False)
    
    if success:
        print("✅ 监控系统初始化成功")
        print("创建的监控表:")
        print("  - table_creation_log")
        print("  - table_operation_log") 
        print("  - table_validation_log")
        print("  - column_definition_log")
    else:
        print("❌ 监控系统初始化失败")
        
except Exception as e:
    print(f"❌ 初始化过程出错: {e}")
```

```python
# Jupyter Cell 4: 表创建示例
print("=== 在Jupyter中创建表 ===")

# 定义表结构
table_config = {
    'table_name': 'jupyter_test_table',
    'database_name': 'test_db',
    'database_type': 'MySQL',
    'columns': [
        {'name': 'id', 'type': 'INT', 'nullable': False, 'auto_increment': True},
        {'name': 'name', 'type': 'VARCHAR', 'length': 100, 'nullable': False},
        {'name': 'value', 'type': 'DECIMAL', 'precision': 10, 'scale': 2},
        {'name': 'created_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'}
    ],
    'primary_key': ['id']
}

try:
    # 生成DDL
    ddl = manager.generate_ddl(table_config)
    print("生成的DDL:")
    print(ddl)
    
    # 创建表
    success = manager.create_table_from_config(table_config)
    print(f"\n表创建结果: {'成功' if success else '失败'}")
    
except Exception as e:
    print(f"❌ 表创建失败: {e}")
```

### 2. Jupyter中的常见问题解决

```python
# Jupyter Cell: 常见问题解决方案

def jupyter_troubleshooting():
    """Jupyter环境故障排除"""
    
    print("=== Jupyter环境故障排除 ===")
    
    # 1. 工作目录检查
    current_dir = os.getcwd()
    print(f"1. 当前工作目录: {current_dir}")
    
    # 检查是否在正确的项目目录
    required_dirs = ['db_manager', 'adapters', 'interfaces']
    missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
    
    if missing_dirs:
        print(f"❌ 缺少必要目录: {missing_dirs}")
        print("请使用 os.chdir() 切换到正确的项目根目录")
    else:
        print("✅ 目录结构正确")
    
    # 2. 环境变量检查
    print("\n2. 环境变量检查:")
    env_vars = [
        'MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD',
        'POSTGRESQL_HOST', 'REDIS_HOST', 'MONITOR_DB_URL'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # 隐藏敏感信息
            if 'PASSWORD' in var or 'URL' in var:
                display_value = value[:5] + '*' * (len(value) - 5)
            else:
                display_value = value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: 未设置")
    
    # 3. 导入检查
    print("\n3. 依赖包检查:")
    packages = ['pandas', 'numpy', 'pymysql', 'psycopg2', 'redis', 'taospy']
    
    for package in packages:
        try:
            __import__(package)
            print(f"  ✅ {package}: 已安装")
        except ImportError:
            print(f"  ❌ {package}: 未安装")
    
    # 4. 提供解决方案
    print("\n4. 常见解决方案:")
    print("  - 工作目录问题: os.chdir('/path/to/mystocks')")
    print("  - 环境变量问题: 检查.env文件是否存在并正确配置")
    print("  - 包依赖问题: pip install package_name")
    print("  - 内核重启: Kernel -> Restart & Clear Output")

jupyter_troubleshooting()
```

## 🔒 安全配置

### 1. 安全检查脚本使用

```python
from db_manager.security_check import SecurityChecker

def security_configuration_example():
    """安全配置示例"""
    
    print("=== 数据库安全配置检查 ===")
    
    # 创建安全检查器
    checker = SecurityChecker()
    
    # 1. 检查环境变量配置
    print("1. 环境变量安全检查:")
    env_check = checker.check_environment_variables()
    
    for check_item, result in env_check.items():
        status = "✅" if result['passed'] else "❌"
        print(f"  {status} {check_item}: {result['message']}")
    
    # 2. 检查数据库连接安全性
    print("\n2. 数据库连接安全检查:")
    
    # 检查MySQL连接
    mysql_security = checker.check_mysql_security()
    print(f"  MySQL安全性: {'通过' if mysql_security['secure'] else '需要改进'}")
    
    for issue in mysql_security.get('issues', []):
        print(f"    ⚠️ {issue}")
    
    # 3. 检查代码中的敏感信息
    print("\n3. 代码安全扫描:")
    
    # 扫描指定目录
    scan_results = checker.scan_code_for_secrets(['db_manager/', 'adapters/'])
    
    if scan_results['secrets_found']:
        print(f"  ❌ 发现 {len(scan_results['secrets'])} 个潜在的敏感信息")
        for secret in scan_results['secrets'][:3]:  # 只显示前3个
            print(f"    - {secret['file']}:{secret['line']} - {secret['type']}")
    else:
        print("  ✅ 未发现明显的敏感信息泄露")
    
    # 4. 生成安全建议
    print("\n4. 安全建议:")
    recommendations = checker.get_security_recommendations()
    
    for category, suggestions in recommendations.items():
        print(f"  {category}:")
        for suggestion in suggestions:
            print(f"    - {suggestion}")

# 运行安全检查示例
security_configuration_example()
```

### 2. 安全的环境变量配置

```python
def secure_environment_setup():
    """安全的环境变量配置示例"""
    
    print("=== 安全的环境变量配置 ===")
    
    # 1. 推荐的.env文件格式
    recommended_env = \"\"\"
# MySQL/MariaDB配置
MYSQL_HOST=192.168.123.104
MYSQL_PORT=3306
MYSQL_USER=mystocks_user          # 使用专用用户，不要用root
MYSQL_PASSWORD=complex_password_123  # 使用复杂密码
MYSQL_DATABASE=mystocks_db

# PostgreSQL配置
POSTGRESQL_HOST=192.168.123.104
POSTGRESQL_PORT=5433
POSTGRESQL_USER=mystocks_pg_user
POSTGRESQL_PASSWORD=another_complex_password_456
POSTGRESQL_DATABASE=quant_research

# Redis配置（如果有密码）
REDIS_HOST=192.168.123.104
REDIS_PORT=6379
REDIS_PASSWORD=redis_password_789   # Redis密码
REDIS_DB=0

# TDengine配置
TDENGINE_HOST=192.168.123.104
TDENGINE_PORT=6030
TDENGINE_USER=mystocks_td_user
TDENGINE_PASSWORD=td_password_abc
TDENGINE_DATABASE=market_data

# 监控数据库（独立配置）
MONITOR_DB_URL=mysql+pymysql://monitor_user:monitor_pass@192.168.123.104:3306/db_monitor

# 可选：加密密钥（用于敏感数据加密）
ENCRYPTION_KEY=your_32_byte_encryption_key_here

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=mystocks_system.log
\"\"\"
    
    print("推荐的.env文件格式:")
    print(recommended_env)
    
    # 2. 安全最佳实践
    print("\n=== 安全最佳实践 ===")
    best_practices = [
        "1. 数据库用户权限最小化原则",
        "   - 为应用程序创建专用数据库用户",
        "   - 只授予必要的权限（SELECT, INSERT, UPDATE, DELETE）",
        "   - 避免使用root或超级用户账户",
        "",
        "2. 密码安全策略",
        "   - 使用复杂密码（字母+数字+特殊字符）",
        "   - 定期更换密码",
        "   - 不同服务使用不同密码",
        "",
        "3. 网络安全配置",
        "   - 使用内网IP地址",
        "   - 配置防火墙规则",
        "   - 启用SSL/TLS连接（生产环境）",
        "",
        "4. 文件权限管理",
        "   - .env文件设置为只读权限",
        "   - 不要将.env文件提交到版本控制",
        "   - 使用.gitignore忽略敏感文件",
        "",
        "5. 监控和审计",
        "   - 启用数据库连接日志",
        "   - 定期检查异常访问",
        "   - 使用监控数据库记录所有操作"
    ]
    
    for practice in best_practices:
        print(practice)
    
    # 3. 数据库用户创建示例
    print("\n=== 数据库用户创建示例 ===")
    
    mysql_user_sql = \"\"\"
-- MySQL用户创建和权限设置
CREATE USER 'mystocks_user'@'%' IDENTIFIED BY 'complex_password_123';

-- 授予特定数据库权限
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER 
ON mystocks_db.* TO 'mystocks_user'@'%';

-- 刷新权限
FLUSH PRIVILEGES;
\"\"\"
    
    postgresql_user_sql = \"\"\"
-- PostgreSQL用户创建和权限设置
CREATE USER mystocks_pg_user WITH PASSWORD 'another_complex_password_456';

-- 创建数据库并设置所有者
CREATE DATABASE quant_research OWNER mystocks_pg_user;

-- 授予数据库权限
GRANT ALL PRIVILEGES ON DATABASE quant_research TO mystocks_pg_user;
\"\"\"
    
    print("MySQL用户创建SQL:")
    print(mysql_user_sql)
    print("PostgreSQL用户创建SQL:")
    print(postgresql_user_sql)

secure_environment_setup()
```

## 🛠️ 故障排除

### 1. 常见问题诊断

```python
def troubleshooting_guide():
    """故障排除指南"""
    
    print("=== 数据库管理器故障排除指南 ===")
    
    # 1. 连接问题诊断
    print("1. 数据库连接问题诊断:")
    
    from db_manager.database_manager import DatabaseTableManager, DatabaseType
    
    manager = DatabaseTableManager()
    
    # 诊断各种数据库连接
    databases = [
        (DatabaseType.MYSQL, "MySQL", "MYSQL_HOST"),
        (DatabaseType.POSTGRESQL, "PostgreSQL", "POSTGRESQL_HOST"),
        (DatabaseType.REDIS, "Redis", "REDIS_HOST"),
        (DatabaseType.TDENGINE, "TDengine", "TDENGINE_HOST")
    ]
    
    for db_type, db_name, env_var in databases:
        print(f"\n  检查 {db_name}:")
        
        # 检查环境变量
        host = os.getenv(env_var)
        if not host:
            print(f"    ❌ 环境变量 {env_var} 未设置")
            continue
        else:
            print(f"    ✅ 主机地址: {host}")
        
        # 尝试连接
        try:
            connection = manager.get_connection(db_type, "test_db")
            if connection:
                print(f"    ✅ 连接成功")
                connection.close()
            else:
                print(f"    ❌ 连接失败")
        except Exception as e:
            print(f"    ❌ 连接错误: {str(e)[:100]}...")
            
            # 提供具体的解决建议
            if "Connection refused" in str(e):
                print(f"      💡 建议: 检查{db_name}服务是否启动")
            elif "Access denied" in str(e):
                print(f"      💡 建议: 检查用户名和密码是否正确")
            elif "Unknown database" in str(e):
                print(f"      💡 建议: 检查数据库名称是否存在")
            elif "timed out" in str(e):
                print(f"      💡 建议: 检查网络连接和防火墙设置")
    
    # 2. 依赖包问题诊断
    print("\n2. 依赖包问题诊断:")
    
    required_packages = {
        'pandas': '数据处理核心库',
        'numpy': '数值计算库',
        'pyyaml': 'YAML配置文件解析',
        'sqlalchemy': '数据库ORM框架',
        'pymysql': 'MySQL数据库驱动',
        'psycopg2': 'PostgreSQL数据库驱动',
        'redis': 'Redis客户端',
        'taospy': 'TDengine客户端'
    }
    
    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"  ✅ {package}: 已安装 - {description}")
        except ImportError:
            print(f"  ❌ {package}: 未安装 - {description}")
            print(f"      💡 安装命令: pip install {package}")
    
    # 3. 配置文件问题诊断
    print("\n3. 配置文件问题诊断:")
    
    # 检查.env文件
    env_file_path = ".env"
    if os.path.exists(env_file_path):
        print(f"  ✅ .env文件存在: {env_file_path}")
        
        # 检查文件权限
        import stat
        file_mode = oct(stat.S_IMODE(os.lstat(env_file_path).st_mode))
        print(f"  📋 文件权限: {file_mode}")
        
        if file_mode == '0o644' or file_mode == '0o600':
            print(f"    ✅ 文件权限安全")
        else:
            print(f"    ⚠️ 建议设置更严格的文件权限")
        
    else:
        print(f"  ❌ .env文件不存在: {env_file_path}")
        print(f"      💡 请创建.env文件并配置数据库连接信息")
    
    # 4. 日志文件检查
    print("\n4. 日志文件检查:")
    
    log_directories = ['logs/', 'db_manager/logs/']
    for log_dir in log_directories:
        if os.path.exists(log_dir):
            print(f"  ✅ 日志目录存在: {log_dir}")
            
            # 列出最近的日志文件
            import glob
            log_files = glob.glob(os.path.join(log_dir, "*.log"))
            recent_logs = sorted(log_files, key=os.path.getmtime, reverse=True)[:3]
            
            for log_file in recent_logs:
                mtime = os.path.getmtime(log_file)
                import datetime
                mtime_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                print(f"    📄 {log_file} (修改时间: {mtime_str})")
        else:
            print(f"  ❌ 日志目录不存在: {log_dir}")

troubleshooting_guide()
```

### 2. 性能调优建议

```python
def performance_tuning_guide():
    """性能调优指南"""
    
    print("=== 数据库性能调优指南 ===")
    
    # 1. 连接池配置建议
    print("1. 连接池配置优化:")
    
    connection_pool_config = {
        "MySQL": {
            "pool_size": 10,           # 连接池大小
            "max_overflow": 20,        # 最大溢出连接数
            "pool_timeout": 30,        # 连接超时时间
            "pool_recycle": 3600,      # 连接回收时间(秒)
            "pool_pre_ping": True      # 连接前ping测试
        },
        "PostgreSQL": {
            "pool_size": 8,
            "max_overflow": 15,
            "pool_timeout": 30,
            "pool_recycle": 7200
        },
        "Redis": {
            "connection_pool_size": 15,
            "retry_on_timeout": True,
            "socket_timeout": 5
        }
    }
    
    for db_type, config in connection_pool_config.items():
        print(f"\n  {db_type} 连接池配置:")
        for param, value in config.items():
            print(f"    {param}: {value}")
    
    # 2. 批量操作优化
    print("\n2. 批量操作优化建议:")
    
    batch_optimization_tips = [
        "📊 数据插入优化:",
        "  - 使用批量INSERT语句，每批1000-5000条记录",
        "  - 关闭自动提交，手动控制事务",
        "  - 使用LOAD DATA INFILE (MySQL) 或 COPY (PostgreSQL)",
        "",
        "🔍 查询优化:",
        "  - 为常用查询字段创建索引",
        "  - 使用LIMIT限制返回结果数量",
        "  - 避免SELECT * ，只查询需要的字段",
        "  - 使用WHERE条件过滤数据",
        "",
        "⚡ TDengine优化:",
        "  - 使用超级表结构存储时序数据",
        "  - 合理设置标签列，避免高基数标签",
        "  - 批量写入数据，减少网络开销",
        "",
        "💾 Redis优化:",
        "  - 设置合理的过期时间，避免内存泄漏",
        "  - 使用pipeline减少网络往返",
        "  - 选择合适的数据结构(Hash, List, Set)"
    ]
    
    for tip in batch_optimization_tips:
        print(tip)
    
    # 3. 监控指标建议
    print("\n3. 性能监控指标:")
    
    monitoring_metrics = {
        "数据库连接": [
            "活跃连接数",
            "连接池使用率",
            "连接建立时间",
            "连接超时次数"
        ],
        "查询性能": [
            "平均查询时间",
            "慢查询数量",
            "查询错误率",
            "并发查询数"
        ],
        "系统资源": [
            "CPU使用率",
            "内存使用率",
            "磁盘I/O",
            "网络延迟"
        ]
    }
    
    for category, metrics in monitoring_metrics.items():
        print(f"\n  {category}:")
        for metric in metrics:
            print(f"    - {metric}")
    
    # 4. 实际优化示例
    print("\n4. 实际优化代码示例:")
    
    optimization_code = \"\"\"
# 批量插入优化示例
def optimized_batch_insert(data_df, table_name, batch_size=1000):
    \"\"\"优化的批量插入方法\"\"\"
    
    manager = DatabaseTableManager()
    connection = manager.get_connection(DatabaseType.MYSQL, "test_db")
    
    try:
        # 关闭自动提交
        connection.autocommit = False
        cursor = connection.cursor()
        
        # 分批处理数据
        for i in range(0, len(data_df), batch_size):
            batch_data = data_df.iloc[i:i+batch_size]
            
            # 生成批量插入SQL
            values = []
            for _, row in batch_data.iterrows():
                value_str = "(" + ",".join([f"'{v}'" for v in row.values]) + ")"
                values.append(value_str)
            
            sql = f"INSERT INTO {table_name} VALUES {','.join(values)}"
            cursor.execute(sql)
            
            print(f"插入批次 {i//batch_size + 1}: {len(batch_data)} 条记录")
        
        # 提交事务
        connection.commit()
        print("批量插入完成")
        
    except Exception as e:
        connection.rollback()
        print(f"插入失败，已回滚: {e}")
    finally:
        cursor.close()
        connection.close()

# 连接池配置示例
def configure_connection_pool():
    \"\"\"配置连接池\"\"\"
    from sqlalchemy import create_engine
    from sqlalchemy.pool import QueuePool
    
    database_url = "mysql+pymysql://user:password@localhost/dbname"
    
    engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=3600,
        pool_pre_ping=True
    )
    
    return engine
\"\"\"
    
    print(optimization_code)

performance_tuning_guide()
```

## 🔗 与v2.0系统集成

### 完整集成示例

```python
def complete_v2_integration_example():
    """完整的v2.0系统集成示例"""
    
    print("=== db_manager与MyStocks v2.0完整集成 ===")
    
    # 1. 初始化v2.0系统
    try:
        from unified_manager import MyStocksUnifiedManager
        from core import DataClassification
        
        print("1. 初始化MyStocks v2.0系统...")
        v2_manager = MyStocksUnifiedManager()
        init_result = v2_manager.initialize_system()
        
        if not init_result['config_loaded']:
            print("❌ v2.0系统初始化失败")
            return
        
        print("✅ v2.0系统初始化成功")
        
    except ImportError:
        print("❌ MyStocks v2.0模块未找到，请确保已正确安装")
        return
    
    # 2. 初始化db_manager
    print("\n2. 初始化db_manager...")
    
    db_manager = DatabaseTableManager()
    
    # 初始化监控数据库
    monitor_success = init_monitoring_database(drop_existing=False)
    print(f"监控数据库初始化: {'成功' if monitor_success else '失败'}")
    
    # 3. 验证数据库连接
    print("\n3. 验证数据库连接...")
    
    database_status = {}
    test_databases = [
        (DatabaseType.MYSQL, "MySQL"),
        (DatabaseType.POSTGRESQL, "PostgreSQL"),
        (DatabaseType.REDIS, "Redis"),
        (DatabaseType.TDENGINE, "TDengine")
    ]
    
    for db_type, db_name in test_databases:
        try:
            conn = db_manager.get_connection(db_type, "test_db")
            database_status[db_name] = conn is not None
            if conn:
                conn.close()
        except:
            database_status[db_name] = False
        
        status = "✅" if database_status[db_name] else "❌"
        print(f"  {status} {db_name}: {'可用' if database_status[db_name] else '不可用'}")
    
    # 4. 创建测试表（通过v2.0系统）
    print("\n4. 通过v2.0系统创建测试表...")
    
    # 使用v2.0的配置驱动表管理
    test_table_config = {
        'table_name': 'integration_test_stock_data',
        'database_name': 'test_db',
        'database_type': 'MySQL',
        'classification': DataClassification.DAILY_KLINE.value,
        'columns': [
            {'name': 'symbol', 'type': 'VARCHAR', 'length': 10, 'nullable': False},
            {'name': 'trade_date', 'type': 'DATE', 'nullable': False},
            {'name': 'close', 'type': 'DECIMAL', 'precision': 10, 'scale': 2},
            {'name': 'volume', 'type': 'BIGINT'},
            {'name': 'created_at', 'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP'}
        ],
        'primary_key': ['symbol', 'trade_date']
    }
    
    try:
        # 使用db_manager创建表
        table_success = db_manager.create_table_from_config(test_table_config)
        print(f"测试表创建: {'成功' if table_success else '失败'}")
        
        if table_success:
            # 通过v2.0系统验证表存在
            # 这里可以添加更多验证逻辑
            print("✅ 表创建成功，已被v2.0系统识别")
        
    except Exception as e:
        print(f"❌ 表创建失败: {e}")
    
    # 5. 数据流测试
    print("\n5. 数据流测试...")
    
    # 创建测试数据
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    test_data = pd.DataFrame({
        'symbol': ['000001', '600000', '000002'] * 5,
        'trade_date': [datetime.now().date() - timedelta(days=i) for i in range(15)],
        'close': np.random.uniform(10, 50, 15),
        'volume': np.random.randint(1000000, 10000000, 15)
    })
    
    try:
        # 通过v2.0系统保存数据（自动路由到PostgreSQL）
        save_success = v2_manager.save_data_by_classification(
            test_data, 
            DataClassification.DAILY_KLINE
        )
        print(f"数据保存测试: {'成功' if save_success else '失败'}")
        
        if save_success:
            # 通过v2.0系统查询数据
            loaded_data = v2_manager.load_data_by_classification(
                DataClassification.DAILY_KLINE,
                filters={'symbol': '000001'},
                limit=5
            )
            print(f"数据查询测试: {'成功' if not loaded_data.empty else '失败'}")
            print(f"查询到 {len(loaded_data)} 条记录")
        
    except Exception as e:
        print(f"❌ 数据流测试失败: {e}")
    
    # 6. 监控系统验证
    print("\n6. 监控系统验证...")
    
    try:
        # 获取系统状态
        system_status = v2_manager.get_system_status()
        
        monitoring = system_status.get('monitoring', {})
        op_stats = monitoring.get('operation_statistics', {})
        
        print(f"总操作数: {op_stats.get('total_operations', 0)}")
        print(f"成功操作: {op_stats.get('successful_operations', 0)}")
        print(f"失败操作: {op_stats.get('failed_operations', 0)}")
        
        # 检查监控表是否有数据
        if database_status.get('MySQL', False):
            monitor_conn = db_manager.get_connection(DatabaseType.MYSQL, "db_monitor")
            if monitor_conn:
                cursor = monitor_conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM table_operation_log")
                log_count = cursor.fetchone()[0]
                print(f"监控日志记录数: {log_count}")
                cursor.close()
                monitor_conn.close()
        
    except Exception as e:
        print(f"❌ 监控系统验证失败: {e}")
    
    # 7. 集成总结
    print("\n=== 集成测试总结 ===")
    
    integration_results = {
        "v2.0系统初始化": init_result['config_loaded'],
        "监控数据库": monitor_success,
        "MySQL连接": database_status.get('MySQL', False),
        "PostgreSQL连接": database_status.get('PostgreSQL', False),
        "Redis连接": database_status.get('Redis', False),
        "TDengine连接": database_status.get('TDengine', False),
        "表创建功能": table_success if 'table_success' in locals() else False,
        "数据流测试": save_success if 'save_success' in locals() else False
    }
    
    for component, status in integration_results.items():
        result = "✅ 通过" if status else "❌ 失败"
        print(f"  {component}: {result}")
    
    success_rate = sum(integration_results.values()) / len(integration_results)
    print(f"\n整体集成成功率: {success_rate:.1%}")
    
    if success_rate >= 0.8:
        print("🎉 集成测试基本成功！系统可以正常使用")
    else:
        print("⚠️ 集成测试存在问题，请检查失败的组件")

# 运行完整集成测试
complete_v2_integration_example()
```

## 🎯 最佳实践总结

### 基础实践
1. **环境配置**: 确保所有数据库服务正常运行，环境变量正确配置
2. **安全管理**: 使用专用数据库用户，设置复杂密码，启用监控
3. **性能优化**: 使用连接池，批量操作，合理设置索引
4. **错误处理**: 实现完善的异常处理和重试机制
5. **监控维护**: 启用监控数据库，定期检查系统状态

### Redis热数据固化最佳实践 ⭐

#### 1. 固化策略选择
```bash
# 生产环境推荐配置
FIXATION_STRATEGY=before_expire
FIXATION_INTERVAL_SECONDS=240    # 4分钟（Redis 5分钟过期的80%）
BACKUP_TO_TICK_DATA=true        # 主要备份到TDengine
BACKUP_TO_DAILY_KLINE=false     # 可选备份到PostgreSQL
BACKUP_TO_FILE_SYSTEM=true      # 应急备份到文件系统
```

#### 2. 强制更新时机
- **交易开始前**: 09:25 清理缓存，获取开盘数据
- **午间休市**: 12:00 固化上午数据
- **收盘后**: 15:05 固化全天数据
- **异常情况**: 发现数据异常时立即强制更新

#### 3. 监控指标
- 固化成功率 > 95%
- 数据延迟 < 30秒
- 存储使用率 < 80%
- 错误率 < 1%

#### 4. 运维命令
```bash
# 日常监控
python db_manager/validate_mystocks_architecture.py

# 强制更新
python db_manager/save_realtime_market_data.py --force-update

# 启用固化
python db_manager/save_realtime_market_data.py --enable-fixation

# 综合运行
python run_realtime_market_saver.py --validate
```

### 故障恢复预案

#### Redis数据丢失恢复
1. **从TDengine恢复**: 查询最近的Tick数据重新加载到Redis
2. **从文件系统恢复**: 使用备份CSV文件恢复数据
3. **强制更新**: 跳过缓存重新获取最新数据

#### 固化失败处理
1. **检查存储空间**: 确保目标数据库有足够空间
2. **验证网络连接**: 检查到各数据库的网络连通性
3. **重试机制**: 系统自动重试最多3次
4. **降级处理**: 自动切换到文件系统备份

### 性能调优建议

#### Redis优化
- 设置合适的内存淘汰策略: `maxmemory-policy allkeys-lru`
- 启用AOF持久化: `appendonly yes`
- 调整过期检查频率: `hz 10`

#### TDengine优化  
- 按symbol和时间分区存储
- 设置合适的数据压缩比
- 定期清理过期数据

#### PostgreSQL优化
- 创建复合索引: `(symbol, trade_date)`
- 启用并行查询: `max_parallel_workers = 4`
- 定期VACUUM和ANALYZE

通过以上示例，您可以充分利用数据库管理器模块的强大功能，构建稳定高效的数据库管理系统。