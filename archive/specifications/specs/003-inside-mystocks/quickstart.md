# 快速开始指南 (Quickstart Guide)

**Feature**: 股票数据扩展功能集成
**Version**: 1.0.0
**Date**: 2025-10-14

本指南帮助您快速搭建开发环境并启动股票数据扩展功能。

---

## 目录

1. [环境要求](#1-环境要求)
2. [快速启动](#2-快速启动)
3. [数据库初始化](#3-数据库初始化)
4. [后端服务启动](#4-后端服务启动)
5. [前端开发服务器](#5-前端开发服务器)
6. [验证安装](#6-验证安装)
7. [常见问题](#7-常见问题)

---

## 1. 环境要求

### 1.1 必需软件

| 软件 | 版本 | 用途 |
|-----|------|------|
| **Python** | 3.12+ | 后端服务 |
| **Node.js** | 18.x+ | 前端构建 |
| **PostgreSQL** | 14.x+ | 主数据库 |
| **TimescaleDB** | 2.11+ | 时序数据扩展 |
| **MySQL/MariaDB** | 8.0+ | 参考数据库 |
| **Redis** | 7.0+ | 缓存服务 |
| **TDengine** | 3.0+ (可选) | 高频数据 |

### 1.2 Python依赖

```bash
# 核心依赖
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pandas==2.1.3
numpy==1.26.2
TA-Lib==0.4.28
akshare==1.12.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pymysql==1.1.0
redis==5.0.1
structlog==23.2.0

# 新增依赖 (用于TQLEX接口)
requests==2.31.0
```

### 1.3 前端依赖

```bash
# 核心依赖
vue@3.3.8
vue-router@4.2.5
pinia@2.1.7
element-plus@2.4.3
axios@1.6.2
klinecharts@9.6.0  # EXISTING
echarts@5.4.3       # 用于资金流向图表
```

---

## 2. 快速启动

### 2.1 克隆项目（如果还没有）

```bash
# 项目应该已经在 /opt/claude/mystocks_spec
cd /opt/claude/mystocks_spec
```

### 2.2 安装Python依赖

```bash
# 创建虚拟环境 (推荐)
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 如果没有requirements.txt,手动安装核心依赖
pip install fastapi uvicorn pandas numpy TA-Lib akshare sqlalchemy psycopg2-binary pymysql redis structlog requests
```

**注意**: TA-Lib需要先安装系统库

```bash
# Ubuntu/Debian
sudo apt-get install -y ta-lib

# macOS
brew install ta-lib

# CentOS/RHEL
yum install -y ta-lib-devel
```

### 2.3 安装前端依赖

```bash
cd web/frontend
npm install
# 或使用淘宝镜像加速
npm install --registry=https://registry.npmmirror.com
```

---

## 3. 数据库初始化

### 3.1 配置环境变量

创建 `.env` 文件（项目根目录）:

```bash
# PostgreSQL配置 (主数据库)
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your_password
POSTGRESQL_DATABASE=mystocks

# MySQL配置 (参考数据库)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=mystocks_ref

# Redis配置 (缓存)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# TDengine配置 (可选,用于高频数据)
TDENGINE_HOST=localhost
TDENGINE_PORT=6041
TDENGINE_USER=root
TDENGINE_PASSWORD=taosdata
TDENGINE_DATABASE=mystocks_market

# TQLEX接口配置 (通达信)
TQLEX_TOKEN=your_tqlex_token_here
TQLEX_BASE_URL=http://excalc.icfqs.com:7616/TQLEX

# 监控数据库配置
MONITOR_DB_URL=postgresql://postgres:your_password@localhost:5432/mystocks_monitor
```

### 3.2 初始化PostgreSQL数据库

```bash
# 登录PostgreSQL
psql -U postgres

# 创建数据库
CREATE DATABASE mystocks;
CREATE DATABASE mystocks_monitor;

# 启用TimescaleDB扩展
\c mystocks
CREATE EXTENSION IF NOT EXISTS timescaledb;

\c mystocks_monitor
CREATE EXTENSION IF NOT EXISTS timescaledb;

# 退出
\q
```

### 3.3 初始化MySQL数据库

```bash
# 登录MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE mystocks_ref CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 创建用户并授权 (可选)
CREATE USER 'mystocks'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON mystocks_ref.* TO 'mystocks'@'localhost';
FLUSH PRIVILEGES;

# 退出
EXIT;
```

### 3.4 运行数据库迁移脚本

```bash
# 返回项目根目录
cd /opt/claude/mystocks_spec

# 初始化完整系统 (包括所有数据库表)
python -c "from unified_manager import MyStocksUnifiedManager; manager = MyStocksUnifiedManager(); manager.initialize_system()"

# 验证表结构
python -c "from core import ConfigDrivenTableManager; mgr = ConfigDrivenTableManager(); mgr.validate_all_table_structures()"
```

**预期输出**:
```
✅ PostgreSQL连接成功
✅ MySQL连接成功
✅ Redis连接成功
✅ 创建表: stock_fund_flow
✅ 创建表: etf_spot_data
✅ 创建表: chip_race_data
✅ 创建表: stock_lhb_detail
✅ 创建表: strategy_signals
✅ 创建表: backtest_trades
✅ 创建表: backtest_results
✅ 创建表: strategy_configs
✅ 创建表: dividend_data
✅ 系统初始化完成
```

---

## 4. 后端服务启动

### 4.1 启动FastAPI开发服务器

```bash
# 返回项目根目录
cd /opt/claude/mystocks_spec

# 启动后端服务 (带自动重载)
cd web/backend
uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload
```

**预期输出**:
```
INFO:     Uvicorn running on http://0.0.0.0:8888 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 4.2 验证API服务

在浏览器访问:
- **Swagger UI**: http://localhost:8888/docs
- **ReDoc**: http://localhost:8888/redoc
- **健康检查**: http://localhost:8888/api/health

**测试API端点**:

```bash
# 测试健康检查
curl http://localhost:8888/api/health

# 预期响应
{"status":"healthy","timestamp":"2024-10-14T10:30:00Z"}

# 获取指标注册表 (EXISTING API)
curl http://localhost:8888/api/indicators/registry

# 预期响应: 包含161个TA-Lib指标的元数据
```

---

## 5. 前端开发服务器

### 5.1 启动Vue开发服务器

**新开一个终端**:

```bash
cd /opt/claude/mystocks_spec/web/frontend

# 启动前端开发服务器
npm run dev
```

**预期输出**:
```
VITE v4.5.0  ready in 1234 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
➜  press h to show help
```

### 5.2 访问前端应用

在浏览器访问: **http://localhost:5173**

**登录凭据** (默认):
```
用户名: admin
密码: admin123
```

---

## 6. 验证安装

### 6.1 后端功能验证

#### 测试1: 技术指标计算 (EXISTING功能)

```bash
curl -X POST "http://localhost:8888/api/indicators/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "600519.SH",
    "start_date": "2024-01-01",
    "end_date": "2024-10-14",
    "indicators": [
      {"abbreviation": "SMA", "parameters": {"timeperiod": 20}}
    ],
    "use_cache": false
  }'
```

**预期**: 返回贵州茅台的20日均线数据

#### 测试2: 资金流向数据 (NEW功能)

```bash
curl -X GET "http://localhost:8888/api/market/fund-flow?symbol=600519.SH&timeframe=1"
```

**预期**: 返回贵州茅台的今日资金流向数据

#### 测试3: 策略列表 (NEW功能)

```bash
curl -X GET "http://localhost:8888/api/strategies/list"
```

**预期**: 返回10个预定义策略的列表

### 6.2 前端功能验证

访问前端应用后,依次检查以下页面:

1. **仪表盘 (Dashboard)** ✅ EXISTING
   - 路径: http://localhost:5173/dashboard
   - 功能: 系统概览

2. **市场行情 (Market)** 🆕 NEW
   - 路径: http://localhost:5173/market
   - 功能: 个股资金流向、ETF列表、竞价抢筹、龙虎榜

3. **技术分析 (Technical Analysis)** ✅ EXISTING + ENHANCE
   - 路径: http://localhost:5173/technical
   - 功能: K线图 + 161个技术指标叠加显示

4. **策略管理 (Strategy Management)** 🆕 NEW
   - 路径: http://localhost:5173/strategy
   - 功能: 策略列表、参数配置、回测运行

5. **回测分析 (Backtest Analysis)** 🆕 NEW
   - 路径: http://localhost:5173/backtest
   - 功能: 回测结果、权益曲线、交易明细

### 6.3 数据库验证

#### 检查PostgreSQL表

```bash
psql -U postgres -d mystocks -c "\dt"
```

**预期输出** (应包含新创建的表):
```
           List of relations
 Schema |        Name        | Type  |  Owner
--------+--------------------+-------+----------
 public | stock_fund_flow    | table | postgres
 public | etf_spot_data      | table | postgres
 public | chip_race_data     | table | postgres
 public | stock_lhb_detail   | table | postgres
 public | strategy_signals   | table | postgres
 public | backtest_trades    | table | postgres
 public | backtest_results   | table | postgres
 public | daily_kline        | table | postgres  (EXISTING)
```

#### 检查MySQL表

```bash
mysql -u root -p mystocks_ref -e "SHOW TABLES;"
```

**预期输出**:
```
+----------------------+
| Tables_in_mystocks_ref |
+----------------------+
| strategy_configs     |
| dividend_data        |
| symbols              |  (EXISTING)
+----------------------+
```

#### 检查TimescaleDB hypertable

```bash
psql -U postgres -d mystocks -c "SELECT * FROM timescaledb_information.hypertables;"
```

**预期**: 应列出所有7个hypertable

---

## 7. 常见问题

### Q1: TA-Lib安装失败

**症状**: `pip install TA-Lib` 报错

**解决方案**:

```bash
# Ubuntu/Debian
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install TA-Lib

# macOS (使用Homebrew)
brew install ta-lib
pip install TA-Lib

# Windows
# 下载预编译wheel: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
pip install TA_Lib‑0.4.28‑cp312‑cp312‑win_amd64.whl
```

### Q2: PostgreSQL连接失败

**症状**: `FATAL: password authentication failed for user "postgres"`

**解决方案**:

1. 检查 `.env` 文件中的密码是否正确
2. 检查 `pg_hba.conf` 配置:
   ```bash
   sudo nano /etc/postgresql/14/main/pg_hba.conf
   # 确保有以下行
   local   all             all                                     md5
   host    all             all             127.0.0.1/32            md5
   ```
3. 重启PostgreSQL: `sudo systemctl restart postgresql`

### Q3: TimescaleDB扩展未安装

**症状**: `ERROR: could not open extension control file`

**解决方案**:

```bash
# Ubuntu/Debian
sudo apt-get install timescaledb-2-postgresql-14

# 添加扩展
sudo timescaledb-tune

# 重启PostgreSQL
sudo systemctl restart postgresql
```

### Q4: 前端npm install卡住

**症状**: npm install长时间无响应

**解决方案**:

```bash
# 使用淘宝镜像
npm config set registry https://registry.npmmirror.com

# 清除缓存
npm cache clean --force

# 重新安装
rm -rf node_modules package-lock.json
npm install
```

### Q5: Akshare数据获取失败

**症状**: 接口返回 "获取数据失败"

**解决方案**:

1. **检查网络连接**: 确保能访问东方财富网
2. **检查Akshare版本**: `pip show akshare` (建议 >= 1.12.0)
3. **更新Akshare**: `pip install --upgrade akshare`
4. **检查代理设置**: 如使用代理,在 `.env` 中配置:
   ```bash
   HTTP_PROXY=http://proxy.example.com:8080
   HTTPS_PROXY=http://proxy.example.com:8080
   ```

### Q6: TQLEX接口401错误

**症状**: 竞价抢筹数据返回401 Unauthorized

**解决方案**:

1. 检查 `.env` 中的 `TQLEX_TOKEN` 是否正确
2. 联系TQLEX服务商获取有效token
3. 如果没有TQLEX token,可以暂时跳过竞价抢筹功能

---

## 8. 下一步

### 8.1 开发流程

1. **后端开发**:
   ```bash
   cd web/backend
   # 创建新的API端点
   vim app/api/market_data.py
   # 启动开发服务器 (自动重载)
   uvicorn app.main:app --reload
   ```

2. **前端开发**:
   ```bash
   cd web/frontend
   # 创建新的Vue组件
   vim src/views/MarketData/FundFlowPanel.vue
   # 启动开发服务器 (热更新)
   npm run dev
   ```

3. **数据库Schema变更**:
   ```bash
   # 编辑table_config.yaml
   vim table_config.yaml
   # 运行迁移
   python -c "from core import ConfigDrivenTableManager; mgr = ConfigDrivenTableManager(); mgr.validate_all_table_structures()"
   ```

### 8.2 推荐学习资源

- **FastAPI文档**: https://fastapi.tiangolo.com/zh/
- **Vue 3文档**: https://cn.vuejs.org/
- **Element Plus文档**: https://element-plus.org/zh-CN/
- **KLineCharts文档**: https://klinecharts.com/
- **TA-Lib文档**: https://ta-lib.github.io/ta-lib-python/
- **Akshare文档**: https://akshare.akfamily.xyz/
- **TimescaleDB文档**: https://docs.timescale.com/

### 8.3 生产环境部署

生产环境部署指南请参考:
- `deployment/docker-compose.yml` - Docker容器化部署
- `deployment/nginx.conf` - Nginx反向代理配置
- `deployment/systemd/` - Systemd服务配置

---

## 联系和支持

- **项目仓库**: https://github.com/yourusername/mystocks
- **问题反馈**: https://github.com/yourusername/mystocks/issues
- **文档**: https://docs.mystocks.com

---

**版本**: 1.0.0
**最后更新**: 2025-10-14
**状态**: ✅ Phase 1 Design Complete
