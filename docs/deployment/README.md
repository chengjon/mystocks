# MyStocks 部署指南 - 双数据库架构

**版本**: 3.0.0
**更新日期**: 2025-10-25
**架构**: TDengine + PostgreSQL 双数据库

---

## 目录

1. [系统要求](#系统要求)
2. [数据库安装](#数据库安装)
3. [环境配置](#环境配置)
4. [系统初始化](#系统初始化)
5. [服务启动](#服务启动)
6. [验证测试](#验证测试)
7. [故障排查](#故障排查)

---

## 系统要求

### 硬件要求

| 组件 | 最小配置 | 推荐配置 |
|------|---------|---------|
| CPU | 4核 | 8核+ |
| 内存 | 8GB | 16GB+ |
| 磁盘 | 100GB SSD | 500GB+ SSD |
| 网络 | 100Mbps | 1Gbps |

### 软件要求

- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Windows 10+ (WSL2)
- **Python**: 3.8 - 3.12
- **Node.js**: 16.x+ (前端开发)
- **Git**: 2.x+

---

## 数据库安装

### 1. 安装 TDengine

**用途**: 高频时序数据存储（tick数据、分钟K线、深度数据）

#### Ubuntu/Debian

```bash
# 1. 下载TDengine安装包
wget https://www.taosdata.com/assets-download/3.0/TDengine-server-3.3.6.13-Linux-x64.tar.gz

# 2. 解压并安装
tar -xzf TDengine-server-3.3.6.13-Linux-x64.tar.gz
cd TDengine-server-3.3.6.13
sudo ./install.sh

# 3. 启动TDengine服务
sudo systemctl start taosd
sudo systemctl enable taosd

# 4. 验证安装
taos
# 在taos shell中执行:
# > SELECT server_version();
# > quit
```

#### Windows (WSL2推荐)

使用WSL2运行Ubuntu并按照上述Ubuntu步骤安装。

#### 配置TDengine

编辑配置文件 `/etc/taos/taos.cfg`：

```ini
# 数据存储目录
dataDir /var/lib/taos

# 日志目录
logDir /var/log/taos

# 监听端口
serverPort 6030

# 最大连接数
maxShellConns 5000

# 压缩设置（极致压缩）
comp 2

# 数据保留天数（高频数据保留90天）
keep 90
```

重启服务使配置生效：
```bash
sudo systemctl restart taosd
```

---

### 2. 安装 PostgreSQL + TimescaleDB

**用途**: 通用数据存储（日线数据、参考数据、衍生数据、交易数据、元数据）

#### Ubuntu/Debian

```bash
# 1. 添加PostgreSQL官方仓库
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update

# 2. 安装PostgreSQL 14
sudo apt-get install -y postgresql-14 postgresql-contrib-14

# 3. 添加TimescaleDB仓库
sudo add-apt-repository ppa:timescale/timescaledb-ppa
sudo apt-get update

# 4. 安装TimescaleDB扩展
sudo apt-get install -y timescaledb-2-postgresql-14

# 5. 配置TimescaleDB
sudo timescaledb-tune --quiet --yes

# 6. 重启PostgreSQL
sudo systemctl restart postgresql

# 7. 验证安装
sudo -u postgres psql -c "SELECT version();"
```

#### 创建数据库和用户

```bash
# 切换到postgres用户
sudo -u postgres psql

# 在psql中执行以下命令:
```

```sql
-- 创建mystocks用户
CREATE USER mystocks_user WITH PASSWORD 'your_secure_password';

-- 创建mystocks业务数据库
CREATE DATABASE mystocks OWNER mystocks_user;

-- 创建监控数据库
CREATE DATABASE mystocks_monitoring OWNER mystocks_user;

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE mystocks TO mystocks_user;
GRANT ALL PRIVILEGES ON DATABASE mystocks_monitoring TO mystocks_user;

-- 退出
\q
```

#### 启用TimescaleDB扩展

```bash
# 在mystocks数据库中启用TimescaleDB
sudo -u postgres psql -d mystocks -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"

# 验证扩展
sudo -u postgres psql -d mystocks -c "\dx"
```

---

## 环境配置

### 1. 克隆项目

```bash
cd /opt/claude
git clone <your-repo-url> mystocks_spec
cd mystocks_spec
git checkout 002-arch-optimization
```

### 2. 创建Python虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装Python依赖

```bash
# 安装核心依赖（双数据库架构）
pip install pandas numpy pyyaml psycopg2-binary taospy akshare

# 安装完整依赖（包含Web服务）
pip install -r requirements.txt
```

### 4. 配置环境变量

复制并编辑 `.env` 文件：

```bash
cp .env.example .env
nano .env  # 或使用其他编辑器
```

**关键配置项**：

```bash
# ========== TDengine配置 ==========
TDENGINE_HOST=192.168.123.104  # TDengine服务器地址
TDENGINE_PORT=6030
TDENGINE_USER=root
TDENGINE_PASSWORD=taosdata
TDENGINE_DATABASE=market_data

# ========== PostgreSQL配置 ==========
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_USER=mystocks_user
POSTGRESQL_PASSWORD=your_secure_password  # 修改为实际密码
POSTGRESQL_DATABASE=mystocks

# ========== 监控数据库配置 ==========
MONITOR_DB_URL=postgresql://mystocks_user:your_secure_password@localhost:5432/mystocks_monitoring
```

---

## 系统初始化

### 1. 初始化TDengine数据库

```bash
# 连接到TDengine
taos -h 192.168.123.104 -P 6030 -u root -p taosdata

# 创建数据库（在taos shell中执行）
CREATE DATABASE IF NOT EXISTS market_data
    KEEP 90
    DAYS 10
    BLOCKS 6
    COMP 2;

# 切换到market_data数据库
USE market_data;

# 创建超表（示例）
CREATE STABLE IF NOT EXISTS tick_data (
    ts TIMESTAMP,
    price DOUBLE,
    volume BIGINT,
    amount DOUBLE
) TAGS (symbol BINARY(20));

CREATE STABLE IF NOT EXISTS minute_data (
    ts TIMESTAMP,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    volume BIGINT
) TAGS (symbol BINARY(20));

# 退出
quit
```

### 2. 初始化PostgreSQL表结构

```bash
# 使用系统初始化脚本
python -c "from unified_manager import MyStocksUnifiedManager; mgr = MyStocksUnifiedManager(); mgr.initialize_system()"

# 或使用配置驱动管理器
python -c "from core import ConfigDrivenTableManager; mgr = ConfigDrivenTableManager(); mgr.batch_create_tables('table_config.yaml')"
```

### 3. 验证表结构

```bash
# 验证PostgreSQL表
python -c "from core import ConfigDrivenTableManager; mgr = ConfigDrivenTableManager(); mgr.validate_all_table_structures()"

# 检查TDengine超表
taos -h 192.168.123.104 -P 6030 -u root -p taosdata -s "USE market_data; SHOW STABLES;"
```

---

## 服务启动

### 1. 启动后端服务（FastAPI）

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动FastAPI服务
cd web/backend
uvicorn main:app --host 0.0.0.0 --port 8888 --reload

# 或使用生产模式（使用gunicorn）
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8888
```

访问API文档：http://localhost:8888/docs

### 2. 启动前端服务（Vue3）

```bash
# 安装前端依赖
cd web/frontend
npm install

# 开发模式启动
npm run dev

# 生产模式构建
npm run build
```

访问前端页面：http://localhost:5173

### 3. 使用Docker Compose（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 验证测试

### 1. 数据库连接测试

```bash
# 测试TDengine连接
python3 << 'EOF'
import taos
try:
    conn = taos.connect(
        host='192.168.123.104',
        port=6030,
        user='root',
        password='taosdata',
        database='market_data'
    )
    result = conn.query("SELECT server_version()")
    print(f"✅ TDengine连接成功: {result.fetch_all()[0][0]}")
    conn.close()
except Exception as e:
    print(f"❌ TDengine连接失败: {e}")
EOF

# 测试PostgreSQL连接
python3 << 'EOF'
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        user='mystocks_user',
        password='your_secure_password',
        database='mystocks'
    )
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print(f"✅ PostgreSQL连接成功: {cur.fetchone()[0][:50]}...")
    conn.close()
except Exception as e:
    print(f"❌ PostgreSQL连接失败: {e}")
EOF
```

### 2. 系统功能测试

```bash
# 运行系统演示
python system_demo.py

# 运行综合测试
python test_comprehensive.py

# 测试统一管理器
python test_unified_manager.py
```

### 3. 数据路由测试

```bash
python3 << 'EOF'
from unified_manager import MyStocksUnifiedManager
from core import DataClassification, DataStorageStrategy
import pandas as pd

# 验证路由规则
print("=== 数据路由验证 ===")
print(f"TICK_DATA → {DataStorageStrategy.get_target_database(DataClassification.TICK_DATA).value}")
print(f"DAILY_KLINE → {DataStorageStrategy.get_target_database(DataClassification.DAILY_KLINE).value}")
print(f"SYMBOLS_INFO → {DataStorageStrategy.get_target_database(DataClassification.SYMBOLS_INFO).value}")

# 测试数据保存
manager = MyStocksUnifiedManager()
test_data = pd.DataFrame({
    'symbol': ['TEST001'],
    'timestamp': [pd.Timestamp.now()],
    'value': [123.45]
})

# 保存到TDengine
print("\n=== 测试TDengine保存 ===")
result = manager.save_data_by_classification(
    DataClassification.TICK_DATA,
    test_data,
    'test_tick_data'
)
print(f"TDengine保存: {'成功' if result else '失败'}")

# 保存到PostgreSQL
print("\n=== 测试PostgreSQL保存 ===")
result = manager.save_data_by_classification(
    DataClassification.DAILY_KLINE,
    test_data,
    'test_daily_kline'
)
print(f"PostgreSQL保存: {'成功' if result else '失败'}")
EOF
```

---

## 故障排查

### 常见问题

#### 1. TDengine连接失败

**错误**: `WebSocket protocol error: Handshake not finished`

**解决方案**:
```bash
# 检查TDengine服务状态
sudo systemctl status taosd

# 重启TDengine服务
sudo systemctl restart taosd

# 检查防火墙
sudo ufw allow 6030/tcp

# 检查配置文件
cat /etc/taos/taos.cfg | grep serverPort
```

#### 2. PostgreSQL连接失败

**错误**: `psycopg2.OperationalError: could not connect to server`

**解决方案**:
```bash
# 检查PostgreSQL服务状态
sudo systemctl status postgresql

# 检查监听地址
sudo -u postgres psql -c "SHOW listen_addresses;"

# 修改postgresql.conf（如需远程连接）
sudo nano /etc/postgresql/14/main/postgresql.conf
# 修改: listen_addresses = '*'

# 修改pg_hba.conf（添加访问控制）
sudo nano /etc/postgresql/14/main/pg_hba.conf
# 添加: host all all 0.0.0.0/0 md5

# 重启PostgreSQL
sudo systemctl restart postgresql
```

#### 3. Python依赖安装失败

**错误**: `error: Failed building wheel for psycopg2-binary`

**解决方案**:
```bash
# Ubuntu/Debian
sudo apt-get install -y python3-dev libpq-dev

# CentOS/RHEL
sudo yum install -y python3-devel postgresql-devel

# 重新安装
pip install psycopg2-binary
```

#### 4. TimescaleDB扩展创建失败

**错误**: `ERROR: could not open extension control file`

**解决方案**:
```bash
# 重新安装TimescaleDB
sudo apt-get install --reinstall timescaledb-2-postgresql-14

# 重新运行tune
sudo timescaledb-tune --quiet --yes

# 重启PostgreSQL
sudo systemctl restart postgresql
```

---

## 性能优化建议

### TDengine优化

```ini
# /etc/taos/taos.cfg

# 增加缓存大小
cache 32

# 增加写入缓冲
blocks 8

# 启用极致压缩
comp 2

# 调整数据保留期
keep 90
```

### PostgreSQL + TimescaleDB优化

```sql
-- 设置合适的chunk_time_interval
SELECT set_chunk_time_interval('daily_kline', INTERVAL '7 days');

-- 启用自动压缩（30天后）
SELECT add_compression_policy('daily_kline', INTERVAL '30 days');

-- 创建索引
CREATE INDEX idx_daily_kline_symbol_time ON daily_kline(symbol, trade_date DESC);

-- 调整内存参数
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET work_mem = '50MB';
```

---

## 监控和维护

### 数据库监控

```bash
# 查看TDengine数据库大小
taos -h 192.168.123.104 -s "SHOW DATABASES;"

# 查看PostgreSQL数据库大小
psql -U mystocks_user -d mystocks -c "SELECT pg_size_pretty(pg_database_size('mystocks'));"

# 查看表大小
psql -U mystocks_user -d mystocks -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;"
```

### 日志查看

```bash
# TDengine日志
tail -f /var/log/taos/taoslog*

# PostgreSQL日志
tail -f /var/log/postgresql/postgresql-14-main.log

# 应用日志
tail -f mystocks_system.log
```

---

## 备份和恢复

### TDengine备份

```bash
# 备份数据库
taosdump -h 192.168.123.104 -o /backup/tdengine/market_data

# 恢复数据库
taosdump -h 192.168.123.104 -i /backup/tdengine/market_data
```

### PostgreSQL备份

```bash
# 备份数据库
pg_dump -U mystocks_user -d mystocks -F c -f /backup/postgresql/mystocks_$(date +%Y%m%d).dump

# 恢复数据库
pg_restore -U mystocks_user -d mystocks /backup/postgresql/mystocks_20251025.dump
```

---

## 安全建议

1. **修改默认密码**: 更改TDengine root密码和PostgreSQL用户密码
2. **启用SSL**: 为生产环境启用数据库SSL连接
3. **限制访问**: 使用防火墙限制数据库端口访问
4. **定期备份**: 设置自动备份任务
5. **监控告警**: 配置数据库监控和告警通知

---

## 附录

### A. 端口列表

| 服务 | 端口 | 用途 |
|-----|------|------|
| TDengine | 6030 | TDengine服务端口 |
| PostgreSQL | 5432 | PostgreSQL服务端口 |
| FastAPI | 8888 | 后端API服务 |
| Vue Frontend | 5173 | 前端开发服务器 |

### B. 目录结构

```
/opt/claude/mystocks_spec/
├── core.py                    # 核心数据分类和路由
├── unified_manager.py         # 统一管理器
├── data_access.py             # 数据访问层
├── table_config.yaml          # 表配置文件
├── .env                       # 环境变量配置
├── web/
│   ├── backend/              # FastAPI后端
│   └── frontend/             # Vue3前端
├── docs/                      # 文档目录
└── tests/                     # 测试文件
```

### C. 参考链接

- [TDengine官方文档](https://docs.taosdata.com/)
- [PostgreSQL官方文档](https://www.postgresql.org/docs/)
- [TimescaleDB官方文档](https://docs.timescale.com/)
- [MyStocks项目文档](../DATASOURCE_AND_DATABASE_ARCHITECTURE.md)

---

**文档维护**: 如有问题或建议，请联系项目组
**最后更新**: 2025-10-25
