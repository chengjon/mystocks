# MyStocks 基础设施检查手册

> **使用说明**:
> 本文件是基础设施检查清单，适合巡检参考，不是当前环境拓扑、统一服务地址或仓库共享规则的唯一事实来源。
> 若涉及当前运行基线、PM2/Docker 主线、审批门禁或服务访问地址，请优先阅读 `architecture/STANDARDS.md`；若涉及运维执行流程或协作约束，再结合根目录 `AGENTS.md` 与 `docs/operations/README.md`。
>
> 文内端口、脚本、检查阈值如未重新核实，应视为巡检样例或历史快照，而不是自动生效的当前标准。

> **文档版本**: v1.0  
> **更新日期**: 2026-01-14  
> **适用范围**: 开发环境、测试环境、生产环境

---

## 📋 目录

1. [环境检查清单](#1-环境检查清单)
2. [数据库检查](#2-数据库检查)
3. [服务状态检查](#3-服务状态检查)
4. [依赖服务检查](#4-依赖服务检查)
5. [网络连通性检查](#5-网络连通性检查)
6. [监控与告警检查](#6-监控与告警检查)
7. [快速健康检查脚本](#7-快速健康检查脚本)

---

## 1. 环境检查清单

### 1.1 系统要求验证

```bash
#!/bin/bash
# 检查系统要求

echo "=== 系统版本检查 ==="
echo "OS: $(uname -a)"
echo "Kernel: $(uname -r)"

echo ""
echo "=== Python 版本检查 ==="
python3 --version
pip --version

echo ""
echo "=== Node.js 版本检查 ==="
node --version
npm --version

echo ""
echo "=== Git 版本检查 ==="
git --version
```

### 1.2 验证标准

| 组件 | 最低版本 | 推荐版本 | 状态 |
|------|----------|----------|------|
| Python | 3.8+ | 3.12+ | ☐ |
| Node.js | 16+ | 20+ | ☐ |
| Git | 2.30+ | 2.40+ | ☐ |
| Docker | 20.0+ | 24.0+ | ☐ |
| Docker Compose | 2.0+ | 2.20+ | ☐ |

### 1.3 环境变量检查

```bash
# 检查必需的环境变量
echo "=== 环境变量检查 ==="

# TDengine 配置
echo "TDENGINE_HOST: ${TDENGINE_HOST:-未设置}"
echo "TDENGINE_PORT: ${TDENGINE_PORT:-未设置}"

# PostgreSQL 配置
echo "POSTGRESQL_HOST: ${POSTGRESQL_HOST:-未设置}"
echo "POSTGRESQL_PORT: ${POSTGRESQL_PORT:-未设置}"

# 缓存配置
echo "REDIS_HOST: ${REDIS_HOST:-未设置}"
echo "REDIS_PORT: ${REDIS_PORT:-未设置}"
```

### 1.4 必需环境变量清单

```bash
# .env 文件模板

# TDengine 高频时序数据库（必需）
TDENGINE_HOST=localhost
TDENGINE_PORT=6030
TDENGINE_USER=root
TDENGINE_PASSWORD=your-tdengine-password
TDENGINE_DATABASE=market_data

# PostgreSQL 主数据库（必需）
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5438
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your_password
POSTGRESQL_DATABASE=mystocks

# 监控数据库
MONITOR_DB_URL=postgresql://postgres:password@localhost:5438/mystocks

# 应用层缓存配置
CACHE_EXPIRE_SECONDS=300
LRU_CACHE_MAXSIZE=1000

# API 安全密钥
JWT_SECRET_KEY=your-secret-key
```

---

## 2. 数据库检查

### 2.1 PostgreSQL 检查

```bash
#!/bin/bash
# PostgreSQL 健康检查脚本

echo "=== PostgreSQL 连接测试 ==="

# 测试连接
PGPASSWORD=$POSTGRESQL_PASSWORD psql -h $POSTGRESQL_HOST -p $POSTGRESQL_PORT -U $POSTGRESQL_USER -d $POSTGRESQL_DATABASE -c "SELECT 1 as test;"

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL 连接成功"
else
    echo "❌ PostgreSQL 连接失败"
fi

echo ""
echo "=== PostgreSQL 版本 ==="
PGPASSWORD=$POSTGRESQL_PASSWORD psql -h $POSTGRESQL_HOST -p $POSTGRESQL_PORT -U $POSTGRESQL_USER -d $POSTGRESQL_DATABASE -c "SELECT version();"

echo ""
echo "=== 数据库大小 ==="
PGPASSWORD=$POSTGRESQL_PASSWORD psql -h $POSTGRESQL_HOST -p $POSTGRESQL_PORT -U $POSTGRESQL_USER -d $POSTGRESQL_DATABASE -c "SELECT pg_size_pretty(pg_database_size('$POSTGRESQL_DATABASE'));"

echo ""
echo "=== 连接数统计 ==="
PGPASSWORD=$POSTGRESQL_PASSWORD psql -h $POSTGRESQL_HOST -p $POSTGRESQL_PORT -U $POSTGRESQL_USER -d $POSTGRESQL_DATABASE -c "SELECT count(*) FROM pg_stat_activity;"
```

### 2.2 TDengine 检查

```bash
#!/bin/bash
# TDengine 健康检查脚本

echo "=== TDengine 连接测试 ==="

# 测试连接
taos -h $TDENGINE_HOST -P $TDENGINE_PORT -u $TDENGINE_USER -p $TDENGINE_PASSWORD -c "SELECT 1;" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ TDengine 连接成功"
else
    echo "❌ TDengine 连接失败"
fi

echo ""
echo "=== TDengine 版本 ==="
taos -h $TDENGINE_HOST -P $TDENGINE_PORT -u $TDENGINE_USER -p $TDENGINE_PASSWORD -c "SHOW VERTICLES;" 2>/dev/null | head -5

echo ""
echo "=== 数据库列表 ==="
taos -h $TDENGINE_HOST -P $TDENGINE_PORT -u $TDENGINE_USER -p $TDENGINE_PASSWORD -c "SHOW DATABASES;" 2>/dev/null

echo ""
echo "=== 市场数据表 ==="
taos -h $TDENGINE_HOST -P $TDENGINE_PORT -u $TDENGINE_USER -p $TDENGINE_PASSWORD -c "USE market_data; SHOW TABLES;" 2>/dev/null
```

### 2.3 数据库检查清单

| 检查项 | 命令 | 预期结果 | 状态 |
|--------|------|----------|------|
| PostgreSQL 连接 | `psql -c "SELECT 1"` | 返回 1 | ☐ |
| PostgreSQL 版本 | `psql -c "SELECT version()"` | 版本号显示 | ☐ |
| TDengine 连接 | `taos -c "SELECT 1"` | 返回 1 | ☐ |
| TDengine 版本 | `taos -c "SHOW VERTICLES"` | 正常显示 | ☐ |
| 表结构验证 | `psql -c "\dt"` | 列出所有表 | ☐ |
| 索引状态 | `psql -c "\di"` | 列出所有索引 | ☐ |
| 活跃连接 | `psql -c "SELECT count(*) FROM pg_stat_activity"` | 正常数值 | ☐ |

---

## 3. 服务状态检查

### 3.1 后端服务检查

```bash
#!/bin/bash
# 后端服务健康检查

echo "=== 后端服务健康检查 ==="

# 检查进程
if ps aux | grep -v grep | grep "uvicorn" > /dev/null; then
    echo "✅ uvicorn 进程运行中"
    ps aux | grep -v grep | grep uvicorn
else
    echo "❌ uvicorn 进程未运行"
fi

echo ""
echo "=== API 健康端点 ==="
curl -s http://localhost:8020/health | python3 -m json.tool

echo ""
echo "=== API 响应时间 ==="
curl -w "\nTotal time: %{time_total}s\n" -s http://localhost:8020/health -o /dev/null

echo ""
echo "=== 数据库连接状态 ==="
curl -s http://localhost:8020/api/v1/db-status | python3 -m json.tool
```

### 3.2 前端服务检查

```bash
#!/bin/bash
# 前端服务健康检查

echo "=== 前端服务健康检查 ==="

# 检查进程
if ps aux | grep -v grep | grep "vite" > /dev/null; then
    echo "✅ vite 开发服务器运行中"
else
    echo "❌ vite 进程未运行"
fi

echo ""
echo "=== 前端响应测试 ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
echo ""

echo ""
echo "=== 构建产物检查 ==="
if [ -d "web/frontend/dist" ]; then
    echo "✅ 构建产物存在"
    ls -la web/frontend/dist | head -10
else
    "❌ 构建产物不存在，需要运行 npm run build"
fi
```

### 3.3 GPU API 服务检查

```bash
#!/bin/bash
# GPU API 服务健康检查

echo "=== GPU 服务状态 ==="

# 检查进程
if ps aux | grep -v grep | grep "gpu_api_server" > /dev/null; then
    echo "✅ GPU API 服务器运行中"
else
    echo "⚠️ GPU API 服务器未运行（如果未配置 GPU 可忽略）"
fi

echo ""
echo "=== GPU 状态端点 ==="
curl -s http://localhost:8001/gpu/status 2>/dev/null | python3 -m json.tool || echo "端点不可用"

echo ""
echo "=== WSL2 GPU 初始化状态 ==="
if [ -f "gpu_api_system/wsl2_gpu_init.py" ]; then
    python3 gpu_api_system/wsl2_gpu_init.py --check 2>/dev/null || echo "检查脚本执行失败"
fi
```

### 3.4 服务检查清单

| 服务 | 检查方法 | 预期结果 | 状态 |
|------|----------|----------|------|
| 后端 API | `curl localhost:8020/health` | 返回 healthy | ☐ |
| 前端 Web | `curl localhost:3000` | 返回 200 | ☐ |
| API 文档 | `curl localhost:8020/docs` | 返回 Swagger UI | ☐ |
| WebSocket | `curl localhost:8020/ws` | 正常连接 | ☐ |
| GPU 服务 | `curl localhost:8001/gpu/status` | 返回 GPU 状态 | ☐ |

---

## 4. 依赖服务检查

### 4.1 Redis 检查

```bash
#!/bin/bash
# Redis 健康检查

echo "=== Redis 连接测试 ==="

# 检查连接
redis-cli -h $REDIS_HOST -p $REDIS_PORT ping

if [ $? -eq 0 ]; then
    echo "✅ Redis 连接成功"
else
    echo "❌ Redis 连接失败"
fi

echo ""
echo "=== Redis 信息 ==="
redis-cli -h $REDIS_HOST -p $REDIS_PORT info

echo ""
echo "=== 内存使用 ==="
redis-cli -h $REDIS_HOST -p $REDIS_PORT info memory | grep used_memory_human
```

### 4.2 Docker 服务检查

```bash
#!/bin/bash
# Docker 服务健康检查

echo "=== Docker 版本 ==="
docker --version
docker compose version

echo ""
echo "=== Docker 进程状态 ==="
systemctl status docker --no-pager

echo ""
echo "=== 运行中的容器 ==="
docker ps -a

echo ""
echo "=== 容器资源使用 ==="
docker stats --no-stream

echo ""
echo "=== Docker 镜像 ==="
docker images | head -10
```

### 4.3 依赖服务检查清单

| 服务 | 检查命令 | 预期结果 | 状态 |
|------|----------|----------|------|
| Redis | `redis-cli ping` | 返回 PONG | ☐ |
| Docker | `docker --version` | 显示版本 | ☐ |
| Docker Compose | `docker compose version` | 显示版本 | ☐ |
| 容器运行 | `docker ps` | 列出容器 | ☐ |

---

## 5. 网络连通性检查

### 5.1 端口监听检查

```bash
#!/bin/bash
# 端口监听检查

echo "=== 监听端口检查 ==="

echo "--- Python 后端 (8000) ---"
netstat -tlnp 2>/dev/null | grep 8000 || ss -tlnp | grep 8000

echo ""
echo "--- 前端 (3000) ---"
netstat -tlnp 2>/dev/null | grep 3000 || ss -tlnp | grep 3000

echo ""
echo "--- PostgreSQL (5438) ---"
netstat -tlnp 2>/dev/null | grep 5438 || ss -tlnp | grep 5438

echo ""
echo "--- TDengine (6030) ---"
netstat -tlnp 2>/dev/null | grep 6030 || ss -tlnp | grep 6030

echo ""
echo "--- Redis (6379) ---"
netstat -tlnp 2>/dev/null | grep 6379 || ss -tlnp | grep 6379
```

### 5.2 连通性测试

```bash
#!/bin/bash
# 网络连通性测试

echo "=== 本地回环测试 ==="
ping -c 1 127.0.0.1

echo ""
echo "=== 数据库连接测试 ==="
timeout 5 bash -c 'cat < /dev/null > /dev/tcp/'$POSTGRESQL_HOST'/'$POSTGRESQL_PORT'' && echo "✅ PostgreSQL 可达" || echo "❌ PostgreSQL 不可达"
timeout 5 bash -c 'cat < /dev/null > /dev/tcp/'$TDENGINE_HOST'/'$TDENGINE_PORT'' && echo "✅ TDengine 可达" || echo "❌ TDengine 不可达"

echo ""
echo "=== DNS 解析测试 ==="
nslookup $POSTGRESQL_HOST 2>/dev/null || echo "DNS 解析失败"
```

### 5.3 网络检查清单

| 检查项 | 命令 | 预期结果 | 状态 |
|--------|------|----------|------|
| 后端端口 | `netstat \| grep 8000` | 监听中 | ☐ |
| 前端端口 | `netstat \| grep 3000` | 监听中 | ☐ |
| PostgreSQL 端口 | `netstat \| grep 5438` | 监听中 | ☐ |
| TDengine 端口 | `netstat \| grep 6030` | 监听中 | ☐ |
| 本地连接 | `ping 127.0.0.1` | 正常 | ☐ |

---

## 6. 监控与告警检查

### 6.1 Prometheus 检查

```bash
#!/bin/bash
# Prometheus 健康检查

echo "=== Prometheus 状态 ==="
curl -s http://localhost:9090/api/v1/status/runtimeinfo | python3 -m json.tool

echo ""
echo "=== Prometheus 目标 ==="
curl -s http://localhost:9090/api/v1/targets | python3 -m json.tool | grep -E "(health|targets)"

echo ""
echo "=== Prometheus 告警规则 ==="
curl -s http://localhost:9090/api/v1/alerts | python3 -m json.tool
```

### 6.2 Grafana 检查

```bash
#!/bin/bash
# Grafana 健康检查

echo "=== Grafana 状态 ==="
curl -s http://localhost:3020/api/health | python3 -m json.tool

echo ""
echo "=== Grafana 数据源 ==="
curl -s -u admin:admin http://localhost:3020/api/datasources | python3 -m json.tool

echo ""
echo "=== Grafana 仪表板 ==="
curl -s -u admin:admin http://localhost:3020/api/search | python3 -m json.tool
```

### 6.3 监控检查清单

| 组件 | 检查方法 | 预期结果 | 状态 |
|------|----------|----------|------|
| Prometheus | `curl localhost:9090/api/v1/status` | 正常响应 | ☐ |
| Grafana | `curl localhost:3020/api/health` | 返回 ok | ☐ |
| 告警规则 | `curl localhost:9090/api/v1/alerts` | 无活跃告警 | ☐ |
| 数据源 | `curl Grafana/api/datasources` | 已配置 | ☐ |

---

## 7. 快速健康检查脚本

### 7.1 一键检查脚本

```bash
#!/bin/bash
# 一键基础设施健康检查

set -e

echo "=========================================="
echo "    MyStocks 基础设施健康检查"
echo "    $(date)"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
}

check_warn() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

echo "=== 1. 环境变量检查 ==="
if [ -n "$TDENGINE_HOST" ]; then
    check_pass "TDENGINE_HOST 已设置: $TDENGINE_HOST"
else
    check_fail "TDENGINE_HOST 未设置"
fi

if [ -n "$POSTGRESQL_HOST" ]; then
    check_pass "POSTGRESQL_HOST 已设置: $POSTGRESQL_HOST"
else
    check_fail "POSTGRESQL_HOST 未设置"
fi

echo ""
echo "=== 2. Python 环境 ==="
if python3 --version | grep -q "3.1"; then
    check_pass "Python 版本: $(python3 --version)"
else
    check_fail "Python 版本不符合要求"
fi

echo ""
echo "=== 3. PostgreSQL 连接 ==="
if PGPASSWORD=$POSTGRESQL_PASSWORD psql -h $POSTGRESQL_HOST -p $POSTGRESQL_PORT -U $POSTGRESQL_USER -d $POSTGRESQL_DATABASE -c "SELECT 1" > /dev/null 2>&1; then
    check_pass "PostgreSQL 连接成功"
else
    check_fail "PostgreSQL 连接失败"
fi

echo ""
echo "=== 4. TDengine 连接 ==="
if taos -h $TDENGINE_HOST -P $TDENGINE_PORT -u $TDENGINE_USER -p $TDENGINE_PASSWORD -c "SELECT 1" > /dev/null 2>&1; then
    check_pass "TDengine 连接成功"
else
    check_warn "TDengine 连接失败（如果未配置可忽略）"
fi

echo ""
echo "=== 5. 后端服务 ==="
if curl -s http://localhost:8020/health > /dev/null 2>&1; then
    check_pass "后端 API 运行正常"
else
    check_fail "后端 API 无响应"
fi

echo ""
echo "=== 6. 前端服务 ==="
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
    check_pass "前端服务响应正常"
else
    check_warn "前端服务无响应"
fi

echo ""
echo "=========================================="
echo "    检查完成"
echo "=========================================="
```

### 7.2 保存为可执行脚本

```bash
# 保存脚本
cat > scripts/check_infrastructure.sh << 'EOF'
#!/bin/bash
# MyStocks 基础设施健康检查脚本
# 用法: ./scripts/check_infrastructure.sh
EOF

chmod +x scripts/check_infrastructure.sh
```

### 7.3 使用方法

```bash
# 运行完整检查
./scripts/check_infrastructure.sh

# 运行详细检查
bash -x ./scripts/check_infrastructure.sh

# 定期检查（添加到 crontab）
# 0 */1 * * * /path/to/scripts/check_infrastructure.sh >> /var/log/infrastructure_check.log
```

---

## 📋 完整检查清单

| 类别 | 检查项 | 命令 | 状态 |
|------|--------|------|------|
| **环境** | Python 版本 | `python3 --version` | ☐ |
| | Node.js 版本 | `node --version` | ☐ |
| | 环境变量 | `env \| grep -E "(TDENGINE\|POSTGRESQL)"` | ☐ |
| **数据库** | PostgreSQL 连接 | `psql -c "SELECT 1"` | ☐ |
| | TDengine 连接 | `taos -c "SELECT 1"` | ☐ |
| | 表结构验证 | `psql -c "\dt"` | ☐ |
| **服务** | 后端 API | `curl localhost:8020/health` | ☐ |
| | 前端 Web | `curl localhost:3000` | ☐ |
| | GPU 服务 | `curl localhost:8001/gpu/status` | ☐ |
| **依赖** | Redis | `redis-cli ping` | ☐ |
| | Docker | `docker --version` | ☐ |
| **网络** | 端口监听 | `netstat -tlnp` | ☐ |
| | 连通性 | `ping -c 1 host` | ☐ |
| **监控** | Prometheus | `curl localhost:9090/api/v1/status` | ☐ |
| | Grafana | `curl localhost:3020/api/health` | ☐ |

---

## 🔧 故障处理流程

### 常见问题处理

| 问题 | 可能原因 | 解决方法 |
|------|----------|----------|
| PostgreSQL 连接失败 | 服务未启动 | `systemctl start postgresql` |
| TDengine 连接失败 | 服务未启动 | `systemctl start taosd` |
| 后端 API 无响应 | 进程崩溃 | 重启服务 |
| 前端无响应 | Nginx 未启动 | `systemctl start nginx` |
| 端口未监听 | 进程未运行 | 检查进程状态 |

---

*最后更新: 2026-01-14*
