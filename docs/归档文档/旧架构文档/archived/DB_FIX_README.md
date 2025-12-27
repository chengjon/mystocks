# MyStocks 数据库问题修复指南

## 问题分析

在运行 MyStocks 系统时，可能会遇到以下数据库相关错误：

1. **TDengine 错误**: `Database not specified`
2. **PostgreSQL 错误**: `function create_hypertable(unknown, unknown) does not exist`
3. **MySQL 错误**: 连接或权限问题

## 解决方案

### 1. TDengine 问题修复

**错误信息**:
```
ERROR:DatabaseTableManager:Failed to create table tick_data: [0x2616]: Database not specified
```

**解决方案**:
运行修复脚本会自动处理此问题，为TDengine添加默认数据库名称。

### 2. PostgreSQL TimescaleDB 问题修复

**错误信息**:
```
ERROR:DatabaseTableManager:Failed to create table daily_kline: function create_hypertable(unknown, unknown) does not exist
```

**解决方案**:

1. **安装 TimescaleDB 扩展**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install timescaledb-2-postgresql-17

   # CentOS/RHEL
   sudo yum install timescaledb-2-postgresql-17

   # 或者从源码安装
   git clone https://github.com/timescale/timescaledb.git
   cd timescaledb
   ./bootstrap -DREGRESS_CHECKS=OFF
   cd build && make
   sudo make install
   ```

2. **启用扩展**:
   ```sql
   -- 连接到PostgreSQL
   psql -U your_username -d your_database

   -- 启用TimescaleDB扩展
   CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
   ```

3. **配置 PostgreSQL**:
   编辑 `postgresql.conf` 文件，添加:
   ```
   shared_preload_libraries = 'timescaledb'
   ```

4. **重启 PostgreSQL 服务**:
   ```bash
   sudo systemctl restart postgresql
   ```

### 3. 数据库配置检查

确保环境变量正确设置：

```bash
# TDengine 配置
export TDENGINE_HOST=localhost
export TDENGINE_PORT=6041
export TDENGINE_USER=root
export TDENGINE_PASSWORD=taosdata

# PostgreSQL 配置
export POSTGRESQL_HOST=localhost
export POSTGRESQL_PORT=5432
export POSTGRESQL_USER=postgres
export POSTGRESQL_PASSWORD=your_password

# MySQL 配置
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password

# Redis 配置
export REDIS_HOST=localhost
export REDIS_PORT=6379
```

### 4. 运行修复脚本

```bash
cd /path/to/mystocks
python db_manager/fix_database_connections.py
```

## 验证修复结果

运行以下命令验证数据库连接：

```bash
python db_manager/validate_mystocks_architecture.py
```

## 简化运行模式

如果只需要基本功能，可以使用简化版运行模式：

```bash
python db_manager/save_realtime_market_data_simple.py
```

这个模式只需要Redis和CSV文件支持，不需要复杂的数据库配置。

## 常见问题解答

### Q: 如何检查TimescaleDB是否安装成功？
A: 运行以下SQL查询：
```sql
SELECT extname FROM pg_extension WHERE extname = 'timescaledb';
```

### Q: 如果无法安装TimescaleDB怎么办？
A: 可以使用简化版运行模式，该模式不依赖TimescaleDB。

### Q: 如何手动创建数据库？
A: 使用以下命令：
```sql
-- MySQL
CREATE DATABASE IF NOT EXISTS market_data;
CREATE DATABASE IF NOT EXISTS quant_research;

-- PostgreSQL
CREATE DATABASE quant_research;
```

## 联系支持

如果以上方法都无法解决问题，请联系项目维护者或在GitHub上提交issue。
