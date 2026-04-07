# MyStocks 故障排除快速手册

> **使用说明**:
> 本文件是运维排障 quick reference，适合快速查阅，不是当前运行基线、当前服务地址或仓库共享规则的唯一事实来源。
> 若涉及环境一致性、当前端口、服务编排或测试/发布门禁，请优先阅读 `architecture/STANDARDS.md`；若涉及运维执行流程或协作约束，再结合根目录 `AGENTS.md` 与 `docs/operations/README.md`。
>
> 文内 `curl` 地址、单命令诊断流程与局部脚本示例应视为排障样例；若与当次运行环境不符，应以实际进程和当前治理文档为准。

> **文档版本**: v1.0  
> **更新日期**: 2026-01-14  
> **用途**: 快速诊断和解决常见问题

---

## 📋 快速索引

| 问题类型 | 症状 | 解决方案 |
|----------|------|----------|
| [服务启动失败](#1-服务启动问题) | 进程无法启动 | 检查端口、依赖、日志 |
| [数据库连接失败](#2-数据库问题) | 无法连接数据库 | 检查服务状态、凭据、网络 |
| [API 请求超时](#3-api-问题) | 请求无响应 | 检查性能、负载、网络 |
| [前端页面异常](#4-前端问题) | 页面加载失败 | 检查构建、资源、浏览器 |
| [CI/CD 失败](#5-cicd-问题) | 流水线失败 | 查看日志、检查环境 |
| [性能问题](#6-性能问题) | 系统响应慢 | 分析瓶颈、优化资源 |

---

## 1. 服务启动问题

### 1.1 后端服务无法启动

```bash
# 症状：uvicorn 进程启动失败

# 诊断步骤
echo "=== 1. 检查端口占用 ==="
lsof -i :8020

echo ""
echo "=== 2. 检查 Python 错误 ==="
cd web/backend
python -m uvicorn app.main:app --reload --log-level debug 2>&1 | head -50

echo ""
echo "=== 3. 检查依赖 ==="
pip list | grep -E "(fastapi|uvicorn|pydantic)"

echo ""
echo "=== 4. 检查配置文件 ==="
python -c "from app.core.config import settings; print(settings.dict())"
```

**常见错误与解决方案**

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `Address already in use` | 端口被占用 | `kill $(lsof -t -i:8020)` 或使用其他端口 |
| `ModuleNotFoundError` | 依赖缺失 | `pip install -r requirements.txt` |
| `ImportError` | 导入路径错误 | 检查 `PYTHONPATH` 设置 |
| `DatabaseError` | 数据库连接失败 | 先启动数据库服务 |

### 1.2 前端服务无法启动

```bash
# 症状：Vite 开发服务器启动失败

# 诊断步骤
echo "=== 1. 检查 Node 版本 ==="
node --version

echo ""
echo "=== 2. 检查依赖安装 ==="
cd web/frontend
ls -la node_modules | head -5

echo ""
echo "=== 3. 尝试重新安装 ==="
rm -rf node_modules package-lock.json
npm install

echo ""
echo "=== 4. 检查端口占用 ==="
lsof -i :3000

echo ""
echo "=== 5. 运行开发服务器（查看详细错误） ==="
npm run dev -- --debug
```

### 1.3 Docker 容器启动失败

```bash
# 症状：容器启动后立即退出

echo "=== 1. 查看容器日志 ==="
docker-compose logs --tail=100

echo ""
echo "=== 2. 检查容器状态 ==="
docker-compose ps

echo ""
echo "=== 3. 单独运行容器 ==="
docker-compose run --rm backend python -c "import app.main; print('OK')"

echo ""
echo "=== 4. 检查资源限制 ==="
docker stats
```

---

## 2. 数据库问题

### 2.1 PostgreSQL 连接失败

```bash
# 症状：psycopg2.OperationalError

echo "=== 1. 检查 PostgreSQL 服务状态 ==="
systemctl status postgresql || docker-compose ps | grep postgres

echo ""
echo "=== 2. 测试连接 ==="
PGPASSWORD=$POSTGRESQL_PASSWORD psql \
  -h $POSTGRESQL_HOST \
  -p $POSTGRESQL_PORT \
  -U $POSTGRESQL_USER \
  -d $POSTGRESQL_DATABASE \
  -c "SELECT 1"

echo ""
echo "=== 3. 检查网络连通性 ==="
nc -zv $POSTGRESQL_HOST $POSTGRESQL_PORT

echo ""
echo "=== 4. 检查连接池状态 ==="
PGPASSWORD=$POSTGRESQL_PASSWORD psql \
  -h $POSTGRESQL_HOST \
  -p $POSTGRESQL_PORT \
  -U $POSTGRESQL_USER \
  -d $POSTGRESQL_DATABASE \
  -c "SELECT count(*) FROM pg_stat_activity;"
```

**快速修复命令**

```bash
# 重启 PostgreSQL
sudo systemctl restart postgresql

# 或 Docker 方式
docker-compose restart postgres
```

### 2.2 TDengine 连接失败

```bash
# 症状：taos 连接超时

echo "=== 1. 检查 TDengine 服务状态 ==="
systemctl status taosd || docker-compose ps | grep tdengine

echo ""
echo "=== 2. 测试连接 ==="
taos -h $TDENGINE_HOST -P $TDENGINE_PORT -u $TDENGINE_USER -p $TDENGINE_PASSWORD -c "SELECT 1"

echo ""
echo "=== 3. 检查端口监听 ==="
netstat -tlnp | grep 6030

echo ""
echo "=== 4. 查看 TDengine 日志 ==="
tail -50 /var/log/taos/taosd.log
```

### 2.3 数据库连接池耗尽

```bash
# 症状：could not obtain connection from the pool

echo "=== 1. 检查活跃连接 ==="
PGPASSWORD=$POSTGRESQL_PASSWORD psql \
  -h $POSTGRESQL_HOST \
  -p $POSTGRESQL_PORT \
  -U $POSTGRESQL_USER \
  -d $POSTGRESQL_DATABASE \
  -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"

echo ""
echo "=== 2. 检查最大连接数 ==="
PGPASSWORD=$POSTGRESQL_PASSWORD psql \
  -h $POSTGRESQL_HOST \
  -p $POSTGRESQL_PORT \
  -U $POSTGRESQL_USER \
  -d $POSTGRESQL_DATABASE \
  -c "SHOW max_connections;"

echo ""
echo "=== 3. 查找泄漏的连接 ==="
PGPASSWORD=$POSTGRESQL_PASSWORD psql \
  -h $POSTGRESQL_HOST \
  -p $POSTGRESQL_PORT \
  -U $POSTGRESQL_USER \
  -d $POSTGRESQL_DATABASE \
  -c "SELECT pid, usename, application_name, state, query_start FROM pg_stat_activity WHERE state = 'idle' AND state_change < NOW() - INTERVAL '10 minutes';"
```

---

## 3. API 问题

### 3.1 API 请求超时

```bash
# 症状：请求等待超过 30s

echo "=== 1. 测试 API 响应时间 ==="
curl -w "\nTime: %{time_total}s\n" -s http://localhost:8020/health

echo ""
echo "=== 2. 检查慢查询日志 ==="
PGPASSWORD=$POSTGRESQL_PASSWORD psql \
  -h $POSTGRESQL_HOST \
  -p $POSTGRESQL_PORT \
  -U $POSTGRESQL_USER \
  -d $POSTGRESQL_DATABASE \
  -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE state != 'idle' ORDER BY duration DESC LIMIT 5;"

echo ""
echo "=== 3. 检查 API 日志 ==="
tail -100 /var/log/mystocks/api.log | grep -E "(ERROR|WARNING|timeout)"
```

### 3.2 API 返回 500 错误

```bash
# 症状：Internal Server Error

echo "=== 1. 查看详细错误 ==="
curl -s http://localhost:8020/health
echo ""

# 开启调试模式
DEBUG=1 python -m uvicorn app.main:app --reload

echo ""
echo "=== 2. 检查 Python 异常 ==="
tail -50 /var/log/mystocks/error.log

echo ""
echo "=== 3. 检查数据库查询 ==="
# 在请求时查看活跃查询
PGPASSWORD=$POSTGRESQL_PASSWORD psql \
  -h $POSTGRESQL_HOST \
  -p $POSTGRESQL_PORT \
  -U $POSTGRESQL_USER \
  -d $POSTGRESQL_DATABASE \
  -c "SELECT * FROM pg_stat_activity WHERE state = 'active' LIMIT 5;"
```

### 3.3 Swagger UI 无法访问

```bash
# 症状：/docs 返回 404 或空白

echo "=== 1. 检查路由注册 ==="
curl http://localhost:8020/openapi.json | python3 -m json.tool | head -20

echo ""
echo "=== 2. 检查 CORS 配置 ==="
curl -s -I http://localhost:8020/docs | grep -i cors

echo ""
echo "=== 3. 检查静态文件 ==="
ls -la web/backend/app/static/
```

---

## 4. 前端问题

### 4.1 页面加载缓慢

```bash
# 症状：首次加载超过 10s

echo "=== 1. 检查网络 ==="
curl -w "DNS: %{time_namelookup}s, Connect: %{time_connect}s, SSL: %{time_appconnect}s, Total: %{time_total}s\n" -s http://localhost:3000 > /dev/null

echo ""
echo "=== 2. 检查浏览器控制台 ==="
# 在浏览器 DevTools > Console 中查看错误

echo ""
echo "=== 3. 检查资源大小 ==="
du -sh web/frontend/dist/

echo ""
echo "=== 4. 清除缓存重新构建 ==="
cd web/frontend
rm -rf dist
npm run build
npm run preview
```

### 4.2 构建失败

```bash
# 症状：npm run build 失败

echo "=== 1. 检查 TypeScript 错误 ==="
npm run type-check 2>&1 | head -50

echo ""
echo "=== 2. 检查 ESLint 错误 ==="
npm run lint 2>&1 | head -50

echo ""
echo "=== 3. 重新安装依赖 ==="
rm -rf node_modules package-lock.json
npm install

echo ""
echo "=== 4. 检查资源限制 ==="
# Node.js 内存限制
node --max-old-space-size=4096 build.js
```

### 4.3 WebSocket 连接失败

```javascript
// 在浏览器控制台执行
const ws = new WebSocket('ws://localhost:8020/ws');
ws.onopen = () => console.log('Connected!');
ws.onerror = (e) => console.error('Error:', e);
ws.onclose = (e) => console.log('Closed:', e.code, e.reason);

// 检查连接状态
console.log('WebSocket readyState:', ws.readyState);
```

---

## 5. CI/CD 问题

### 5.1 GitHub Actions 失败

```bash
# 症状：流水线检查不通过

echo "=== 1. 查看工作流日志 ==="
# 在 GitHub Actions 页面查看详细日志

echo ""
echo "=== 2. 本地重现问题 ==="
# 运行失败的步骤
./scripts/ci/code_quality_check.sh

echo ""
echo "=== 3. 检查依赖版本 ==="
pip freeze | grep -E "(fastapi|uvicorn|pytest)"
npm list --depth=0
```

### 5.2 测试失败

```bash
# 症状：pytest 测试不通过

echo "=== 1. 运行单个测试 ==="
pytest tests/ -v --tb=short 2>&1 | head -100

echo ""
echo "=== 2. 检查测试数据 ==="
# 确认测试数据库配置正确
python -c "from app.db import engine; engine.connect()"

echo ""
echo "=== 3. 检查测试覆盖率 ==="
pytest --cov=src --cov-report=term-missing

echo ""
echo "=== 4. 跳过慢测试快速验证 ==="
pytest tests/ -v --ignore=tests/performance/ -x
```

### 5.3 Docker 构建失败

```bash
# 症状：Docker 构建中途失败

echo "=== 1. 查看构建日志 ==="
docker build -t mystocks-backend . --progress=plain 2>&1 | tail -100

echo ""
echo "=== 2. 检查 Dockerfile ==="
cat web/backend/Dockerfile

echo ""
echo "=== 3. 单独测试构建步骤 ==="
docker run -it python:3.12-slim bash
# 在容器内手动执行构建步骤
```

---

## 6. 性能问题

### 6.1 CPU 使用率过高

```bash
# 症状：CPU 持续 80%+

echo "=== 1. 查看进程 CPU 使用 ==="
top -c

echo ""
echo "=== 2. 查看 Python 进程线程 ==="
ps aux | grep python | head -10

echo ""
echo "=== 3. 检查慢 API 端点 ==="
curl -s http://localhost:8020/api/v1/slow-endpoint -w "\nTime: %{time_total}s\n"

echo ""
echo "=== 4. 检查数据库慢查询 ==="
PGPASSWORD=$POSTGRESQL_PASSWORD psql \
  -h $POSTGRESQL_HOST \
  -p $POSTGRESQL_PORT \
  -U $POSTGRESQL_USER \
  -d $POSTGRESQL_DATABASE \
  -c "SELECT pid, now() - query_start AS duration, query FROM pg_stat_activity WHERE state != 'idle' AND now() - query_start > '5 seconds' ORDER BY duration DESC LIMIT 5;"
```

### 6.2 内存不足

```bash
# 症状：OutOfMemoryError 或系统变慢

echo "=== 1. 查看内存使用 ==="
free -h

echo ""
echo "=== 2. 查看进程内存 ==="
ps aux --sort=-%mem | head -10

echo ""
echo "=== 3. Python 内存泄漏检查 ==="
python -c "
import tracemalloc
tracemalloc.start()
# 触发可疑代码
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
"

echo ""
echo "=== 4. 增加内存限制 ==="
# 在 .env 中
PYTHONMEMORYLIMIT=4G
UVICORN_WORKERS=2
```

### 6.3 数据库性能问题

```bash
# 症状：查询响应慢

echo "=== 1. 检查查询执行计划 ==="
PGPASSWORD=$POSTGRESQL_PASSWORD psql \
  -h $POSTGRESQL_HOST \
  -p $POSTGRESQL_PORT \
  -U $POSTGRESQL_USER \
  -d $POSTGRESQL_DATABASE \
  -c "EXPLAIN ANALYZE SELECT * FROM your_table WHERE condition;"

echo ""
echo "=== 2. 检查缺失的索引 ==="
PGPASSWORD=$POSTGRESQL_PASSWORD psql \
  -h $POSTGRESQL_HOST \
  -p $POSTGRESQL_PORT \
  -U $POSTGRESQL_USER \
  -d $POSTGRESQL_DATABASE \
  -c "SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;"

echo ""
echo "=== 3. 检查表膨胀 ==="
PGPASSWORD=$POSTGRESQL_PASSWORD psql \
  -h $POSTGRESQL_HOST \
  -p $POSTGRESQL_PORT \
  -U $POSTGRESQL_USER \
  -d $POSTGRESQL_DATABASE \
  -c "SELECT schemaname, tablename, dead_tuple_ratio FROM pg_stat_user_tables ORDER BY dead_tuple_ratio DESC LIMIT 10;"
```

---

## 🔧 常用修复命令速查

```bash
# =====================
# 快速修复命令
# =====================

# 重启后端服务
sudo systemctl restart mystocks-api
# 或
docker-compose restart backend

# 重启前端服务
docker-compose restart frontend

# 重启数据库
sudo systemctl restart postgresql
docker-compose restart postgres

# 清除缓存
redis-cli FLUSHALL

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
cd web/frontend && npm install

# 清除 Python 缓存
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete

# 检查配置
python -c "from app.core.config import settings; print(settings.dict())"

# 检查数据库连接
python -c "from app.db import engine; engine.connect(); print('DB OK')"

# 查看日志
tail -f /var/log/mystocks/api.log
tail -f /var/log/mystocks/error.log
```

---

## 📞 紧急联系方式

| 问题类型 | 联系渠道 |
|----------|----------|
| 生产故障 | 值班电话：xxx-xxxx-xxxx |
| 安全问题 | security@mystocks.example.com |
| 一般咨询 | dev-team@mystocks.example.com |

---

## 📋 问题报告模板

```markdown
## 问题描述
- 发生时间：
- 影响范围：
- 期望行为：
- 实际行为：

## 环境信息
- 操作系统：
- Python 版本：
- Node.js 版本：
- Docker 版本：

## 重现步骤
1. 步骤 1
2. 步骤 2
3. 步骤 3

## 错误日志
```
粘贴错误日志
```

## 已尝试的解决方案
1. 尝试 1 - 结果
2. 尝试 2 - 结果
```

---

*最后更新: 2026-01-14*
