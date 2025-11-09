# Contract: 数据库连接验证契约

**Feature**: 系统规范化改进
**Branch**: 006-0-md-1
**Date**: 2025-10-16
**Type**: Database Validation

## 目的

定义4个数据库(MySQL, PostgreSQL, TDengine, Redis)的连接验证标准和契约，为修复Web页面数据显示问题提供诊断依据。

## 数据库连接参数

### 1. MySQL (参考数据和元数据)

**配置参数**:
```python
MYSQL_HOST=192.168.123.104
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=[从.env读取]
MYSQL_DATABASE=quant_research
```

**关键表清单**:
- `stock_info` - 股票基本信息
- `constituents` - 指数成分股
- `contracts` - 合约信息
- `data_sources` - 数据源配置
- `indicator_configurations` - 指标配置

**健康检查SQL**:
```sql
-- 1. 版本检查
SELECT VERSION();

-- 2. 数据库检查
SHOW DATABASES LIKE 'quant_research';

-- 3. 表检查
SHOW TABLES;

-- 4. 数据量检查
SELECT COUNT(*) FROM stock_info;
SELECT COUNT(*) FROM data_sources;
```

### 2. PostgreSQL (衍生数据和监控)

**配置参数**:
```python
POSTGRESQL_HOST=192.168.123.104
POSTGRESQL_PORT=5438  # 非标准端口
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=[从.env读取]
POSTGRESQL_DATABASE=mystocks
```

**关键表清单** (mystocks数据库):
- `daily_kline` - 历史日K线
- `realtime_market_quotes` - 实时市场行情
- `technical_indicators` - 技术指标
- `operation_logs` - 操作日志
- `operation_logs_2025_10` - 分区表

**关键表清单** (mystocks_monitoring数据库):
- 监控数据库包含8个监控相关表

**健康检查SQL**:
```sql
-- 1. 版本检查
SELECT version();

-- 2. 数据库检查
SELECT datname FROM pg_database WHERE datname IN ('mystocks', 'mystocks_monitoring');

-- 3. 表检查
SELECT table_name FROM information_schema.tables WHERE table_schema='public';

-- 4. 数据量检查
SELECT COUNT(*) FROM daily_kline;
SELECT COUNT(*) FROM realtime_market_quotes;

-- 5. 监控数据库检查
\c mystocks_monitoring
SELECT table_name FROM information_schema.tables WHERE table_schema='public';
```

### 3. TDengine (时序市场数据)

**配置参数**:
```python
TDENGINE_HOST=192.168.123.104
TDENGINE_PORT=6030
TDENGINE_USER=root
TDENGINE_PASSWORD=taosdata
TDENGINE_DATABASE=market_data
```

**关键超级表清单** (预期):
- tick数据相关超级表
- 分钟K线超级表
- 实时行情超级表

**健康检查SQL**:
```sql
-- 1. 版本检查
SELECT server_version();

-- 2. 数据库检查
SHOW DATABASES LIKE 'market_data';

-- 3. 超级表检查
USE market_data;
SHOW STABLES;

-- 4. 数据量检查
SELECT COUNT(*) FROM stable_name;
```

**已知问题**:
- ❌ `SELECT server_version()` 返回None，需要修复
- ⚠️ 连接成功但查询异常，可能数据库未初始化

### 4. Redis (实时缓存)

**配置参数**:
```python
REDIS_HOST=192.168.123.104
REDIS_PORT=6379
REDIS_PASSWORD=  # 空密码
REDIS_DB=1  # 使用DB1
```

**健康检查命令**:
```bash
# 1. 连接测试
redis-cli -h 192.168.123.104 -p 6379 -n 1 PING

# 2. 版本检查
redis-cli -h 192.168.123.104 -p 6379 INFO server | grep redis_version

# 3. 内存检查
redis-cli -h 192.168.123.104 -p 6379 INFO memory | grep used_memory_human

# 4. 键数量检查
redis-cli -h 192.168.123.104 -p 6379 -n 1 DBSIZE

# 5. 键列表检查
redis-cli -h 192.168.123.104 -p 6379 -n 1 KEYS "stock:*"
```

**Python检查**:
```python
import redis

r = redis.Redis(host='192.168.123.104', port=6379, db=1)
r.ping()  # 返回True表示成功
info = r.info()
print(f"Redis版本: {info['redis_version']}")
print(f"键数量: {r.dbsize()}")
```

## 连接失败错误码和处理方案

### MySQL错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 2003 | Can't connect to MySQL server | 检查服务是否启动: `systemctl status mysql` |
| 1045 | Access denied | 检查用户名/密码 |
| 1049 | Unknown database | 数据库不存在，需要创建 |
| 1146 | Table doesn't exist | 表未创建，运行初始化脚本 |

### PostgreSQL错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| Connection refused | 连接被拒绝 | 检查服务: `systemctl status postgresql` |
| FATAL: password authentication failed | 密码错误 | 检查.env配置 |
| FATAL: database does not exist | 数据库不存在 | 创建数据库: `createdb mystocks` |
| could not translate host name | 主机名解析失败 | 检查HOST配置，使用IP地址 |

### TDengine错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| Connection refused | 连接被拒绝 | 检查服务: `systemctl status taosd` |
| Authentication failure | 认证失败 | 检查用户名/密码 |
| Database not exist | 数据库不存在 | 创建: `CREATE DATABASE market_data` |
| Invalid SQL | SQL语法错误 | 检查TDengine SQL语法差异 |

### Redis错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| Connection refused | 连接被拒绝 | 检查服务: `systemctl status redis` |
| NOAUTH | 需要密码认证 | 提供密码参数 |
| Invalid DB index | DB索引无效 | 检查REDIS_DB配置(0-15) |

## 修复验证清单

### 验证工具

**自动化脚本**: `utils/check_db_health.py`

```bash
# 运行数据库健康检查
python utils/check_db_health.py

# 预期输出
============================================================
MyStocks 数据库健康检查
============================================================
✅ MySQL: 通过
✅ PostgreSQL: 通过
✅ TDengine: 通过
✅ Redis: 通过

总计: 4/4 个数据库连接成功
通过率: 100%
```

### 手动验证

**MySQL**:
```bash
mysql -h 192.168.123.104 -u root -p -D quant_research -e "SELECT VERSION(); SHOW TABLES;"
```

**PostgreSQL**:
```bash
psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks -c "SELECT version(); \dt"
```

**TDengine**:
```bash
taos -h 192.168.123.104 -u root -p taosdata -s "SHOW DATABASES; USE market_data; SHOW STABLES;"
```

**Redis**:
```bash
redis-cli -h 192.168.123.104 -p 6379 -n 1 PING
```

## 修复优先级

### P1 (立即修复)

1. **TDengine连接异常** ❌
   - 当前状态: 连接成功但查询失败
   - 影响: TDX实时行情功能完全不可用
   - 修复: 检查数据库初始化，修复health check脚本

2. **config.py硬编码密码** ⚠️
   - 当前状态: 明文密码 "c790414J"
   - 影响: 安全风险，配置不统一
   - 修复: 改为从.env读取

### P2 (重要)

3. **PostgreSQL非标准端口** ⚠️
   - 当前状态: 5438而非5432
   - 影响: 可能导致混淆
   - 修复: 文档说明或统一为标准端口

4. **Redis无数据** ℹ️
   - 当前状态: 键数量为0
   - 影响: 缓存功能未启用
   - 修复: 确认是否需要预热缓存

## 验收标准

### 必须满足 (SC-009-NEW)

- [ ] MySQL连接测试通过 ✅ (已完成)
- [ ] PostgreSQL连接测试通过 ✅ (已完成)
- [ ] TDengine连接测试通过 ❌ (需修复)
- [ ] Redis连接测试通过 ✅ (已完成)
- [ ] `check_db_health.py` 100%通过率

### 建议满足

- [ ] config.py从.env读取密码
- [ ] 所有关键表存在且可访问
- [ ] 数据量检查返回合理结果
- [ ] 监控数据库(mystocks_monitoring)正常

---

**创建人**: Claude
**版本**: 1.0.0
**批准日期**: 待定
**最后修订**: 2025-10-16
**本次修订内容**: 基于R5研究结果创建数据库验证契约
