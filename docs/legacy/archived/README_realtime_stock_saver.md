# 沪深市场A股实时数据保存系统使用指南

**Note**: MySQL has been removed; use PostgreSQL. This legacy guide is kept for reference.

## 📋 概述

本系统按照db_manager工作原理设计，实现将customer接口中`stock.get_realtime_quotes()`获取的沪深市场A股最新状况数据保存到本地数据库的完整功能。

## 🏗️ 系统架构

系统基于MyStocks项目的db_manager模块构建，采用以下工作原理：

1. **环境变量驱动** - 从.env文件获取数据库连接配置
2. **统一数据库管理** - 通过DatabaseTableManager统一管理多种数据库
3. **自动DDL生成** - 根据DataFrame结构自动生成表结构
4. **完整监控记录** - 所有操作自动记录到监控数据库
5. **数据类型智能映射** - 自动分析数据类型并生成合适的SQL类型

## 📁 文件说明

| 文件名 | 功能说明 |
|--------|----------|
| `save_realtime_stock_data.py` | 基础版本，参数直接写在代码中 |
| `save_realtime_stock_data_v2.py` | 改进版本，支持配置文件 |
| `realtime_stock_config.env` | 配置文件，包含所有可调整参数 |
| `test_customer_realtime_data.py` | 测试脚本，用于验证数据结构 |

## 🔧 环境准备

### 1. 依赖安装

```bash
# 基础依赖
pip install pandas numpy sqlalchemy psycopg2-binary

# 数据源库
pip install efinance easyquotation

# 可选：性能优化库
pip install ujson numba
```

### 2. 数据库配置

在项目根目录创建`.env`文件：

```bash
# PostgreSQL配置（主数据库）
POSTGRESQL_HOST=192.168.123.104
POSTGRESQL_PORT=5432
POSTGRESQL_USER=your_user
POSTGRESQL_PASSWORD=your_password
POSTGRESQL_DATABASE=market_data

# 监控数据库配置（必需）
MONITOR_DB_URL=postgresql://user:password@host:port/db_monitor

REDIS_HOST=192.168.123.104
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

### 3. 数据库初始化

```bash
# 初始化监控数据库（首次使用）
python -m db_manager.init_db_monitor
```

## 🚀 使用方法

### 方法一：使用默认配置

```bash
# 使用默认配置运行
python save_realtime_stock_data_v2.py
```

### 方法二：使用自定义配置

```bash
# 1. 复制配置文件模板
cp realtime_stock_config.env my_config.env

# 2. 编辑配置文件
vim my_config.env

# 3. 使用自定义配置运行
python save_realtime_stock_data_v2.py --config my_config.env
```

### 方法三：直接修改参数

编辑`save_realtime_stock_data.py`文件中的参数：

```python
# 修改以下参数
TARGET_DATABASE_TYPE = DatabaseType.POSTGRESQL
TARGET_DATABASE_NAME = "your_database"
TARGET_TABLE_NAME = "your_table"
MARKET_SYMBOL = "hs"  # 'hs'=沪深, 'sh'=上海, 'sz'=深圳
```

## ⚙️ 配置参数详解

### 数据库配置

```bash
# 目标数据库类型：POSTGRESQL
TARGET_DATABASE_TYPE=POSTGRESQL

# 数据库名称（需要预先创建）
TARGET_DATABASE_NAME=market_data

# 表名称（自动创建）
TARGET_TABLE_NAME=realtime_stock_quotes
```

### 数据源配置

```bash
# 市场代码
# 'hs' = 沪深市场（推荐，数据最全）
# 'sh' = 上海市场
# 'sz' = 深圳市场
MARKET_SYMBOL=hs

# 数据源超时时间（秒）
DATA_SOURCE_TIMEOUT=30
```

### 表结构配置

```bash
# 主键列名（需要确保数据中包含此列）
# 常见列名：'股票代码', 'code', 'symbol'
PRIMARY_KEY_COLUMN=股票代码

# PostgreSQL不使用存储引擎/字符集参数（忽略即可）

# 是否添加时间戳列
ADD_TIMESTAMP_COLUMN=true
```

### 操作控制配置

```bash
# 是否删除已存在的表（谨慎使用！）
DROP_TABLE_IF_EXISTS=false

# 最大重试次数
MAX_RETRY_ATTEMPTS=3

# 是否启用数据验证
ENABLE_DATA_VALIDATION=true
```

## 📊 数据流程

### 1. 数据获取流程

```
Customer适配器 → efinance.stock.get_realtime_quotes() → DataFrame
```

### 2. 数据处理流程

```
DataFrame → 数据类型分析 → 表结构生成 → DDL语句生成
```

### 3. 数据保存流程

```
表结构创建 → 数据验证 → 批量插入 → 操作日志记录
```

## 🔍 典型数据结构

从`stock.get_realtime_quotes()`获取的数据通常包含以下列：

| 列名 | 类型 | 说明 |
|------|------|------|
| 股票代码 | VARCHAR(20) | 主键，股票代码 |
| 股票名称 | VARCHAR(100) | 股票名称 |
| 最新价 | DECIMAL(15,4) | 当前价格 |
| 涨跌幅 | DECIMAL(8,4) | 涨跌幅度(%) |
| 涨跌额 | DECIMAL(10,4) | 涨跌金额 |
| 成交量 | BIGINT | 成交量 |
| 成交额 | DECIMAL(20,2) | 成交金额 |
| 换手率 | DECIMAL(8,4) | 换手率(%) |
| 市盈率 | DECIMAL(10,4) | 市盈率 |
| 市净率 | DECIMAL(10,4) | 市净率 |

## 📝 日志监控

### 日志文件位置

- 应用日志：`realtime_stock_saver.log`
- 系统日志：控制台输出

### 监控数据库表

系统自动在监控数据库中记录：

- `table_creation_log` - 表创建日志
- `table_operation_log` - 操作日志
- `table_validation_log` - 验证日志
- `column_definition_log` - 列定义日志

### 查询监控信息

```sql
-- 查看最近的操作记录
SELECT * FROM table_operation_log
ORDER BY operation_time DESC
LIMIT 10;

-- 查看数据保存统计
SELECT
    DATE(operation_time) as date,
    COUNT(*) as operations,
    SUM(CASE WHEN operation_status = 'success' THEN 1 ELSE 0 END) as success_count
FROM table_operation_log
WHERE operation_type = 'INSERT'
GROUP BY DATE(operation_time)
ORDER BY date DESC;
```

## 🛠️ 故障排除

### 常见问题

#### 1. 环境变量未配置

**错误信息：**
```
缺少必要的环境变量: ['MYSQL_HOST', 'MYSQL_USER']
```

**解决方案：**
检查`.env`文件是否存在且配置正确。

#### 2. 数据库连接失败

**错误信息：**
```
数据库连接测试失败
```

**解决方案：**
- 检查数据库服务是否启动
- 验证连接参数（主机、端口、用户名、密码）
- 确认数据库已创建

#### 3. efinance库不可用

**错误信息：**
```
efinance库不可用，无法获取实时数据
```

**解决方案：**
```bash
pip install efinance
```

#### 4. 主键列不存在

**错误信息：**
```
数据缺少主键列: 股票代码
```

**解决方案：**
检查数据结构，确认主键列名配置正确。常见列名包括：
- `股票代码`
- `code`
- `symbol`
- `ts_code`

### 调试模式

启用详细日志：

```bash
# 修改配置文件
LOG_LEVEL=DEBUG

# 或直接在代码中设置
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 定时任务

### 使用cron定时执行

```bash
# 编辑crontab
crontab -e

# 每5分钟执行一次
*/5 * * * * cd /path/to/mystocks && python save_realtime_stock_data_v2.py

# 每天上午9:30执行（开盘时间）
30 9 * * 1-5 cd /path/to/mystocks && python save_realtime_stock_data_v2.py
```

### 使用Windows任务计划程序

1. 打开任务计划程序
2. 创建基本任务
3. 设置触发器（每日/每小时等）
4. 操作设置为启动程序
5. 程序路径：`python.exe`
6. 参数：`save_realtime_stock_data_v2.py`
7. 起始位置：项目目录

## 📈 性能优化

### 1. 数据库优化

```sql
-- 为常用查询字段创建索引
CREATE INDEX idx_stock_code ON realtime_stock_quotes(股票代码);
CREATE INDEX idx_update_time ON realtime_stock_quotes(data_update_time);

-- 定期优化表
OPTIMIZE TABLE realtime_stock_quotes;
```

### 2. 应用优化

- 使用批量插入模式（已默认启用）
- 合理设置重试次数
- 启用数据验证避免脏数据

### 3. 监控优化

- 定期清理监控日志
- 设置日志轮转
- 监控磁盘空间使用

## 🔗 集成其他系统

### 与MyStocks v2.0系统集成

```python
from unified_manager import MyStocksUnifiedManager
from core import DataClassification

# 使用v2.0系统的统一管理器
manager = MyStocksUnifiedManager()

# 获取数据后自动路由保存
manager.save_data_by_classification(
    stock_data,
    DataClassification.REALTIME_POSITIONS
)
```

### API接口封装

可以将本系统封装为REST API：

```python
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/api/update_realtime_data')
def update_realtime_data():
    saver = RealtimeStockDataSaver()
    success = saver.run()
    return jsonify({'success': success})
```

## 📚 扩展开发

### 添加新的数据源

1. 在`adapters/`目录创建新适配器
2. 实现`IDataSource`接口
3. 修改`CustomerDataSource`类集成新数据源

### 支持新的数据库

1. 在`DatabaseType`枚举中添加新类型
2. 在`DatabaseTableManager`中添加连接逻辑
3. 实现对应的DDL生成方法

### 自定义数据处理

1. 继承`RealtimeStockDataSaver`类
2. 重写`get_realtime_stock_data`方法
3. 添加自定义的数据清洗逻辑

通过以上完整的使用指南，您可以轻松地部署和使用沪深市场A股实时数据保存系统。
