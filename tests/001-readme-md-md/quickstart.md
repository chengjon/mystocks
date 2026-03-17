# MyStocks Quick Start Guide

**创建人**: Claude (自动生成)
**版本**: 1.0.0
**创建日期**: 2025-10-11

## 1. 环境准备

### 1.1 数据库安装

#### TDengine 3.0+ (高频时序数据)

```bash
# Ubuntu/Debian
wget https://www.taosdata.com/assets-download/3.0/TDengine-server-3.0.5.0-Linux-x64.deb
sudo dpkg -i TDengine-server-3.0.5.0-Linux-x64.deb

# 启动服务
sudo systemctl start taosd
sudo systemctl enable taosd

# 验证安装
taos
# 在taos shell中: SHOW DATABASES;
```

#### PostgreSQL 14+ with TimescaleDB 2.x (历史分析)

```bash
# 安装PostgreSQL 14
sudo apt-get install postgresql-14

# 安装TimescaleDB扩展
sudo add-apt-repository ppa:timescale/timescaledb-ppa
sudo apt-get update
sudo apt-get install timescaledb-2-postgresql-14

# 配置TimescaleDB
sudo timescaledb-tune
sudo systemctl restart postgresql

# 创建数据库
sudo -u postgres psql
CREATE DATABASE mystocks;
\c mystocks
CREATE EXTENSION IF NOT EXISTS timescaledb;

# 创建监控数据库
CREATE DATABASE mystocks_monitor;
```

#### MySQL 8.0+ / MariaDB 10.6+ (参考数据)

```bash
# 安装MySQL 8.0
sudo apt-get install mysql-server-8.0

# 或安装MariaDB 10.6
sudo apt-get install mariadb-server-10.6

# 创建数据库
mysql -u root -p
CREATE DATABASE mystocks_reference CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### Redis 6.0+ (实时缓存)

```bash
# 安装Redis
sudo apt-get install redis-server

# 配置持久化 (编辑 /etc/redis/redis.conf)
appendonly yes
appendfsync everysec

# 重启服务
sudo systemctl restart redis-server
```

---

### 1.2 Python环境

```bash
# 创建虚拟环境 (Python 3.8+)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 升级pip
pip install --upgrade pip

# 安装依赖
cd /path/to/mystocks_spec
pip install -r requirements.txt
```

**requirements.txt**:
```txt
# 核心依赖
pandas>=2.0.0
numpy>=1.24.0
pyyaml>=6.0

# 数据库驱动
taospy>=2.7.0              # TDengine
psycopg2-binary>=2.9.5     # PostgreSQL
pymysql>=1.0.2             # MySQL
redis>=4.5.0               # Redis

# 数据源
akshare>=1.11.0
baostock>=0.9.0
tushare>=1.3.0
efinance>=0.5.0

# 类型验证
pydantic>=2.0.0
pandera>=0.17.0

# 工具
python-dotenv>=1.0.0
schedule>=1.2.0

# 开发工具
pytest>=7.4.0
mypy>=1.5.0
```

---

### 1.3 配置文件

#### 创建 `.env` 文件

```bash
cp .env.example .env
vi .env  # 或使用你喜欢的编辑器
```

**`.env` 内容**:
```env
# TDengine配置
TDENGINE_HOST=localhost
TDENGINE_PORT=6041
TDENGINE_USER=root
TDENGINE_PASSWORD=your-tdengine-password
TDENGINE_DATABASE=market_data

# PostgreSQL配置
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your_password
POSTGRESQL_DATABASE=mystocks

# MySQL配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=mystocks_reference

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_APP_CACHE_DB=1
REDIS_MONITORING_DB=0
REDIS_CELERY_BROKER_DB=0
REDIS_CELERY_RESULT_DB=1

# 监控数据库配置
MONITOR_DB_URL=postgresql://postgres:your_password@localhost:5432/mystocks_monitor
```

---

## 2. 系统初始化

### 2.1 初始化数据库表

```python
from core import ConfigDrivenTableManager

# 读取table_config.yaml并自动创建所有表
manager = ConfigDrivenTableManager()
result = manager.initialize_all_tables()

print(f"✅ 创建 {result['tables_created']} 个表")
print(f"⏭️ 跳过 {result['tables_skipped']} 个表 (已存在)")

if result['errors']:
    print(f"❌ 错误: {result['errors']}")
```

### 2.2 验证系统健康状态

```python
from unified_manager import MyStocksUnifiedManager

mgr = MyStocksUnifiedManager()
health = mgr.get_system_health()

print(f"系统状态: {health['overall_status']}")
for db_name, db_status in health['databases'].items():
    print(f"  {db_name}: {db_status['status']}")
```

---

## 3. 基础使用示例

### 3.1 保存日线数据

```python
import pandas as pd
from core import DataClassification
from unified_manager import MyStocksUnifiedManager

# 准备日线数据
daily_data = pd.DataFrame({
    'symbol': ['600000.SH', '000001.SZ'],
    'trade_date': pd.to_datetime(['2025-10-11', '2025-10-11'], utc=True),
    'interval_type': ['D', 'D'],
    'open': [10.50, 15.30],
    'high': [10.80, 15.60],
    'low': [10.30, 15.20],
    'close': [10.65, 15.45],
    'volume': [1000000, 2000000],
    'amount': [10650000.0, 30900000.0]
})

# 保存数据 (自动路由到PostgreSQL)
mgr = MyStocksUnifiedManager()
result = mgr.save_data_by_classification(
    data=daily_data,
    classification=DataClassification.DAILY_KLINE
)

print(f"✅ 成功保存 {result['records_saved']} 条记录")
print(f"📊 目标数据库: {result['target_database']}")
print(f"⏱️ 执行耗时: {result['execution_time_ms']:.2f}ms")
```

### 3.2 查询股票信息

```python
# 查询上交所活跃股票
stocks = mgr.load_data_by_classification(
    classification=DataClassification.SYMBOLS_INFO,
    filters={
        'exchange': 'SSE',
        'status': 'ACTIVE'
    },
    order_by=['market_cap DESC'],
    limit=10
)

print(stocks[['symbol', 'name', 'market_cap']])
```

### 3.3 使用数据源适配器

```python
from adapters import AkshareAdapter

# 获取实时行情
adapter = AkshareAdapter()
quotes = adapter.get_realtime_quotes(['600000.SH', '000001.SZ'])

# 保存到系统 (自动路由到Redis)
mgr.save_data_by_classification(
    data=quotes,
    classification=DataClassification.REALTIME_POSITIONS
)
```

---

## 4. 监控和告警

### 4.1 查询操作统计

```python
from monitoring import MonitoringDatabase
from datetime import datetime, timedelta

monitor = MonitoringDatabase('postgresql://localhost/mystocks_monitor')

# 查询近期失败的操作
failures = monitor.get_recent_failures(hours=24, limit=10)
for op in failures:
    print(f"❌ {op['operation_time']}: {op['error_message']}")
```

### 4.2 查询数据质量报告

```python
from monitoring import DataQualityMonitor

quality_monitor = DataQualityMonitor()

# 检查日线数据完整性
report = quality_monitor.check_data_completeness(
    classification=DataClassification.DAILY_KLINE,
    expected_count=1000,
    actual_count=995
)

print(f"完整性率: {report['completeness_rate']:.2f}%")
print(f"缺失记录: {report['missing_count']}")
print(f"检查结果: {report['check_result']}")
```

---

## 5. 常见问题

### Q1: 数据库连接失败

**问题**: `DatabaseUnavailableException: PostgreSQL connection failed`

**解决**:
1. 检查数据库服务是否启动: `sudo systemctl status postgresql`
2. 检查 `.env` 文件中的连接参数
3. 验证数据库用户权限

### Q2: table_config.yaml 配置错误

**问题**: `ConfigurationException: Classification 'DAILY_KLINE' not configured`

**解决**:
1. 确保 `table_config.yaml` 文件存在
2. 检查对应数据分类的表定义是否完整
3. 运行 `python -c "from core import ConfigLoader; ConfigLoader.load_config('table_config.yaml')"`

### Q3: Redis使用0号数据库冲突

**问题**: Redis 0号数据库被其他程序占用

**解决**:
在 `.env` 中按角色设置 Redis DB，例如 `REDIS_APP_CACHE_DB=1`、`REDIS_MONITORING_DB=0`、`REDIS_CELERY_BROKER_DB=0`、`REDIS_CELERY_RESULT_DB=1`

---

## 6. 下一步

- 阅读 [data-model.md](data-model.md) 了解完整的数据模型设计
- 查看 [contracts/unified_manager_api.md](contracts/unified_manager_api.md) 了解API详细用法
- 查看 [research.md](research.md) 了解技术决策和架构设计

---

**文档版本**: 1.0.0
**最后更新**: 2025-10-11
