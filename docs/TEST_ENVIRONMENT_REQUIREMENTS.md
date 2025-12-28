# MyStocks 测试环境依赖需求文档

**文档版本**: 2.0  
**生成日期**: 2025-12-28  
**基于配置**: /opt/claude/mystocks_spec/.env  
**目的**: 为 Phase 6.2 测试覆盖率提升提供完整的环境依赖清单  

---

## 快速开始

### 1. 配置测试环境（5分钟）

```bash
# 1. 进入项目目录
cd /opt/claude/mystocks_phase6_monitoring

# 2. 检查环境
bash scripts/check_test_environment.sh

# 3. 初始化测试数据库（如果需要）
bash scripts/init_test_databases.sh

# 4. 加载环境变量
export $(cat .env.test | grep -v '^#' | xargs)

# 5. 运行测试
pytest tests/unit/ -v
```

---

## 1. 数据库依赖

### 1.1 生产环境数据库配置（已确认）

| 数据库 | 服务器地址 | 端口 | 用户 | 数据库 | 用途 |
|--------|-----------|------|------|--------|------|
| **TDengine** | 192.168.123.104 | 6030 | root | market_data | 高频时序数据 |
| **PostgreSQL** | 192.168.123.104 | 5438 ⚠️ | postgres | mystocks | 通用数据仓库 |
| **TimescaleDB** | 192.168.123.104 | 5438 | - | - | PostgreSQL扩展 |

**重要提示**:
- ✅ PostgreSQL使用端口 **5438**（非标准5432）
- ✅ 服务器地址: **192.168.123.104**
- ✅ 所有数据库已在生产环境运行

### 1.2 测试数据库配置

| 数据库 | 数据库名称 | 说明 |
|--------|----------|------|
| **TDengine** | market_data_test | 时序数据测试库 |
| **PostgreSQL** | mystocks_test | 通用数据测试库 |

---

## 2. 环境变量配置

### 2.1 P0 - 核心数据库配置（必须）

#### TDengine 测试配置
```bash
# 生产服务器配置（测试环境使用相同服务器，独立数据库）
TDENGINE_HOST=192.168.123.104
TDENGINE_PORT=6030
TDENGINE_USER=root
TDENGINE_PASSWORD=taosdata
TDENGINE_DATABASE=market_data_test        # ⚠️ 测试专用数据库
TDENGINE_REST_PORT=6041
```

#### PostgreSQL 测试配置
```bash
# 生产服务器配置（测试环境使用相同服务器，独立数据库）
POSTGRESQL_HOST=192.168.123.104
POSTGRESQL_PORT=5438                      # ⚠️ 非标准端口
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=c790414J
POSTGRESQL_DATABASE=mystocks_test           # ⚠️ 测试专用数据库
```

#### 监控数据库配置
```bash
# 使用PostgreSQL测试数据库
MONITOR_DB_HOST=192.168.123.104
MONITOR_DB_PORT=5438
MONITOR_DB_USER=postgres
MONITOR_DB_PASSWORD=c790414J
MONITOR_DB_DATABASE=mystocks_test
```

### 2.2 P1 - 连接池配置

```bash
# 数据库连接池
POOL_MIN_CONNECTIONS=2
POOL_MAX_CONNECTIONS=10
POOL_TIMEOUT=30
POOL_MAX_INACTIVE_CONNECTION_LIFETIME=3600
POOL_RECYCLE=3600

# 监控配置
ENABLE_POOL_MONITORING=true
MONITORING_INTERVAL=60
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10
```

### 2.3 P2 - 应用配置

```bash
# JWT认证
JWT_SECRET_KEY=ba08e97232f49b1b0e5f4e146c5e30b65f26c3b4f06637d08832733a7bb6a379
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# 缓存配置
CACHE_EXPIRE_SECONDS=300
LRU_CACHE_MAXSIZE=1000

# 数据验证
ENABLE_DATA_VALIDATION=true
MAX_RETRY_ATTEMPTS=3
DATA_SOURCE_TIMEOUT=30

# 测试模式
DEBUG_MODE=true
USE_MOCK_DATA=false
REAL_DATA_AVAILABLE=true
```

### 2.4 P3 - TDX数据源（可选）

```bash
# TDX配置（使用生产TDX服务器）
TDX_SERVER_HOST=192.168.123.104
TDX_SERVER_PORT=7709
TDX_MAX_RETRIES=3
TDX_RETRY_DELAY=1
TDX_API_TIMEOUT=10
TDX_MARKETS=sh,sz
```

### 2.5 测试专用配置

```bash
# 测试端口（避免与生产冲突）
BACKEND_PORT=8888                           # 生产使用8000
METRICS_PORT=9091                           # 生产使用9090

# 测试日志
LOG_LEVEL=DEBUG                             # 测试环境使用DEBUG
LOG_FILE=/tmp/mystocks_test.log

# 测试限制（放宽限制以便测试）
API_RATE_LIMIT=1000                         # 生产限制为100
```

---

## 3. Python包依赖

### 3.1 数据库驱动（必须）

| 包名 | 用途 | 状态 |
|------|------|------|
| **psycopg2-binary** | PostgreSQL驱动 | ✅ 已安装 |
| **taosws** | TDengine WebSocket驱动 | ✅ 需要安装 |
| **sqlalchemy** | ORM框架 | ✅ 已安装 |
| **python-dotenv** | 环境变量加载 | ✅ 已安装 |

### 3.2 测试框架（必须）

| 包名 | 用途 | 状态 |
|------|------|------|
| **pytest** | 测试框架 | ✅ 已安装 |
| **pytest-cov** | 覆盖率工具 | ✅ 已安装 |
| **pytest-mock** | Mock工具 | ✅ 已安装 |

### 3.3 Mock工具（可选，用于纯Mock测试）

| 包名 | 用途 |
|------|------|
| **responses** | Mock HTTP请求 |
| **freezegun** | Mock时间 |

---

## 4. 数据库初始化

### 4.1 TDengine 测试数据库

```sql
-- 创建测试数据库
CREATE DATABASE IF NOT EXISTS market_data_test;

-- 创建超表（时序数据）
USE market_data_test;

CREATE STABLE IF NOT EXISTS tick_data (
    ts TIMESTAMP,
    price FLOAT,
    volume BIGINT,
    amount DOUBLE,
    bid_price FLOAT,
    ask_price FLOAT
) TAGS (
    symbol BINARY(20),
    exchange BINARY(10)
);

CREATE STABLE IF NOT EXISTS minute_kline (
    ts TIMESTAMP,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT,
    amount DOUBLE,
    turnover DOUBLE
) TAGS (
    symbol BINARY(20),
    exchange BINARY(10)
);
```

### 4.2 PostgreSQL 测试数据库

```sql
-- 创建测试数据库
CREATE DATABASE mystocks_test;

-- 启用TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 日线数据表（Hypertable）
CREATE TABLE IF NOT EXISTS daily_kline (
    symbol VARCHAR(20),
    date DATE,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    amount DECIMAL(20,2),
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (symbol, date)
);

SELECT create_hypertable('daily_kline', 'date', if_not_exists => TRUE);

-- 股票基本信息表（Hypertable）
CREATE TABLE IF NOT EXISTS stock_basic_info (
    symbol VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100),
    industry VARCHAR(100),
    market VARCHAR(20),
    list_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

SELECT create_hypertable('stock_basic_info', 'created_at', if_not_exists => TRUE);
```

### 4.3 监控表

```sql
-- 操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    operation_id VARCHAR(50) PRIMARY KEY,
    operation_type VARCHAR(50),
    classification VARCHAR(100),
    target_database VARCHAR(20),
    table_name VARCHAR(100),
    record_count INTEGER,
    operation_status VARCHAR(20),
    error_message TEXT,
    execution_time_ms INTEGER,
    user_agent VARCHAR(200),
    client_ip VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 性能指标表（Hypertable）
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100),
    metric_value DOUBLE,
    metadata JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

SELECT create_hypertable('performance_metrics', 'timestamp', if_not_exists => TRUE);

-- 警报表
CREATE TABLE IF NOT EXISTS alert_records (
    alert_id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50),
    severity VARCHAR(20),
    message TEXT,
    details JSONB,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);
```

---

## 5. 测试环境配置选项

### 5.1 方案A: 使用生产服务器（推荐）

**适用场景**: 集成测试，E2E测试

**优点**:
- ✅ 使用真实生产环境数据库
- ✅ 数据已就绪，无需额外初始化
- ✅ 与生产环境配置一致

**缺点**:
- ⚠️ 依赖网络连接到 192.168.123.104
- ⚠️ 测试数据可能影响生产监控数据

**配置**: 使用 `.env.test`（已生成）

```bash
# .env.test
TDENGINE_HOST=192.168.123.104
TDENGINE_PORT=6030
TDENGINE_DATABASE=market_data_test
POSTGRESQL_HOST=192.168.123.104
POSTGRESQL_PORT=5438
POSTGRESQL_DATABASE=mystocks_test
```

**步骤**:
```bash
# 1. 检查环境
bash scripts/check_test_environment.sh

# 2. 初始化测试数据库
bash scripts/init_test_databases.sh

# 3. 加载环境变量
export $(cat .env.test | grep -v '^#' | xargs)

# 4. 运行测试
pytest tests/unit/ -v --cov=src
```

---

### 5.2 方案B: 使用Docker（环境隔离）

**适用场景**: 完全隔离的测试环境

**优点**:
- ✅ 完全隔离，不影响生产
- ✅ 本地运行，无需网络
- ✅ 易于清理和重置

**缺点**:
- ❌ 需要安装Docker
- ❌ 需要导入测试数据

**配置**: 使用 `docker-compose.test.yml`（已生成）

```bash
# 启动容器
docker-compose -f docker-compose.test.yml up -d

# 等待数据库启动
sleep 10

# 更新 .env.test 使用 localhost
# TDENGINE_HOST=localhost
# POSTGRESQL_HOST=localhost
```

---

### 5.3 方案C: 纯Mock（最小配置）

**适用场景**: 单元测试，无数据库依赖

**优点**:
- ✅ 无需数据库
- ✅ 测试速度快
- ✅ 完全隔离

**缺点**:
- ❌ 无法测试真实数据库交互
- ❌ 需要维护Mock

**配置**:

```bash
# .env.mock
MOCK_DATABASE_CONNECTIONS=true
USE_MOCK_DATA=true
DEBUG_MODE=true
```

**运行**:
```bash
pytest tests/unit/ -v -m mock_only
```

---

## 6. 模块数据库依赖清单

### 6.1 核心模块

| 模块 | TDengine | PostgreSQL | 说明 |
|------|----------|------------|------|
| `src/data_access/tdengine_access.py` | ✅ 必需 | ❌ | TDengine访问层 |
| `src/data_access/postgresql_access.py` | ❌ | ✅ 必需 | PostgreSQL访问层 |
| `src/storage/database/database_manager.py` | ✅ 必需 | ✅ 必需 | 数据库管理器 |
| `src/storage/database/connection_manager.py` | ✅ 必需 | ✅ 必需 | 连接管理 |
| `src/core/data_manager.py` | ✅ 必需 | ✅ 必需 | 数据管理器 |
| `src/monitoring/monitoring_database.py` | ❌ | ✅ 必需 | 监控数据库 |

### 6.2 适配器模块

| 模块 | 数据库依赖 | 说明 |
|------|-----------|------|
| `src/adapters/tdx_adapter.py` | ❌ | TDX数据源（无数据库） |
| `src/adapters/akshare_adapter.py` | ❌ | AkShare数据源（无数据库） |
| `src/adapters/financial_adapter.py` | ❌ | 财经数据源（无数据库） |

### 6.3 GPU模块

| 模块 | TDengine | PostgreSQL | GPU |
|------|----------|------------|------|
| `src/gpu/acceleration/*.py` | ✅ 可选 | ✅ 必需 | ✅ 必需 |

---

## 7. 环境检查脚本

### 7.1 使用说明

```bash
# 运行环境检查
bash scripts/check_test_environment.sh
```

**输出示例**:
```
==========================================
  MyStocks 测试环境检查
==========================================

[1/5] 检查环境变量...
✅ 环境变量已设置
   ✅ 存在: TDENGINE_HOST
   ✅ 存在: TDENGINE_PORT
   ✅ 存在: POSTGRESQL_HOST
   ...

[2/5] 检查Docker...
✅ Docker 已安装: 24.0.7

[3/5] 检查Python包...
✅ 已安装: psycopg2-binary (2.9.9)
✅ 已安装: pytest (8.4.2)
...

[4/5] 检查数据库连接...
✅ TDengine 连接成功 (192.168.123.104:6030)
✅ PostgreSQL 连接成功 (192.168.123.104:5438)

[5/5] 检查Docker容器状态...
⚠️  TDengine 容器未运行
⚠️  PostgreSQL 容器未运行

==========================================
  检查完成
==========================================

✅ 环境就绪，可以开始测试
```

---

## 8. 审批清单

### 环境配置审批

- [x] **数据库选择**: [x] 生产服务器 / [ ] Docker / [ ] 本地
- [x] **测试数据库**: [x] market_data_test / mystocks_test
- [x] **环境配置**: [x] .env.test 已创建
- [x] **检查脚本**: [x] check_test_environment.sh 已创建
- [x] **初始化脚本**: [x] init_test_databases.sh 已创建

### 测试目标审批

- [ ] **覆盖率目标**: [ ] 80% / [ ] 60% / [ ] 40%
- [ ] **测试范围**: [ ] 全部模块 / [ ] 核心模块 / [ ] 关键路径
- [ ] **测试类型**: [ ] 单元测试 / [ ] 集成测试 / [ ] E2E测试

### 待审批事项

#### 请选择测试策略：

**选项A**: 使用生产服务器（推荐）
- [ ] 同意使用 192.168.123.104 作为测试数据库服务器
- [ ] 同意创建 market_data_test 和 mystocks_test 测试数据库
- [ ] 需要初始化测试数据（运行 init_test_databases.sh）

**选项B**: 使用Docker（环境隔离）
- [ ] 需要安装Docker和Docker Compose
- [ ] 需要导入测试数据到容器

**选项C**: 纯Mock（单元测试）
- [ ] 仅运行单元测试，不连接真实数据库

---

## 9. 下一步行动（待审批后）

### 9.1 立即执行（5分钟）

1. **加载环境变量**
   ```bash
   export $(cat .env.test | grep -v '^#' | xargs)
   ```

2. **运行环境检查**
   ```bash
   bash scripts/check_test_environment.sh
   ```

3. **修复任何问题**
   - [ ] 环境变量缺失？
   - [ ] 数据库连接失败？
   - [ ] Python包缺失？

### 9.2 初始化测试数据库（10分钟）

1. **初始化数据库**
   ```bash
   bash scripts/init_test_databases.sh
   ```

2. **验证数据库**
   ```bash
   # TDengine
   taos -h 192.168.123.104 -P 6030 -u root -p taosdata -s "USE market_data_test;"

   # PostgreSQL
   PGPASSWORD=c790414J psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks_test -c "\dt"
   ```

### 9.3 开始测试（持续）

1. **运行现有测试**
   ```bash
   pytest tests/unit/ -v --cov=src --cov-report=term-missing
   ```

2. **分析覆盖率**
   ```bash
   # 生成覆盖率报告
   pytest --cov=src --cov-report=html
   open htmlcov/index.html
   ```

3. **提升覆盖率**
   - 分析低覆盖率模块
   - 编写测试用例
   - 验证覆盖率提升

---

## 10. 常见问题

### Q1: 数据库连接失败？

**原因**:
- 网络不可达 192.168.123.104
- 端口配置错误（PostgreSQL使用5438，非5432）

**解决**:
```bash
# 检查网络连通性
ping 192.168.123.104

# 检查端口开放
telnet 192.168.123.104 6030    # TDengine
telnet 192.168.123.104 5438    # PostgreSQL
```

### Q2: TDengine 连接超时？

**原因**: TDengine WebSocket端口配置错误

**解决**:
```bash
# 确认使用正确的端口
TDENGINE_PORT=6030              # WebSocket端口
TDENGINE_REST_PORT=6041          # REST API端口
```

### Q3: PostgreSQL 驱动未安装？

**解决**:
```bash
pip install psycopg2-binary sqlalchemy python-dotenv
```

### Q4: TDengine 驱动未安装？

**解决**:
```bash
pip install taosws
```

---

## 11. 联系方式

**问题反馈**:
- 环境配置问题: 请联系DevOps团队
- 数据库访问问题: 请检查 192.168.123.104 服务器
- 测试编写问题: 请联系开发团队

---

## 12. 文件清单

本次生成的文件：

| 文件 | 说明 |
|------|------|
| `.env.test` | 测试环境配置（基于生产配置） |
| `docker-compose.test.yml` | Docker测试环境（可选） |
| `scripts/check_test_environment.sh` | 环境检查脚本 |
| `scripts/init_test_databases.sh` | 数据库初始化脚本 |

---

**文档版本**: 2.0  
**最后更新**: 2025-12-28  
**状态**: 待审批
