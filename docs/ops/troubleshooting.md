# 排障指南

> **版本**: 1.0 | **更新日期**: 2026-07-12
> **维护者**: 运维
> **合并来源**: `operations/TROUBLESHOOTING.md` + `operations/TROUBLESHOOTING_QUICK_REFERENCE.md`

---

## 快速诊断

### 系统健康检查

```bash
# 检查后端服务
curl http://localhost:8020/health

# 检查前端服务
curl http://localhost:3020

# 检查数据库连接
python3 -c "from app.db import engine; engine.connect(); print('DB OK')"
```

### 预期响应

```json
{
  "status": "healthy",
  "services": {
    "database": "up",
    "cache": "up",
    "api": "up"
  }
}
```

---

## 问题索引

| 问题类型 | 症状 | 定位 |
|----------|------|------|
| [服务启动失败](#服务启动问题) | 进程无法启动 | 检查端口、依赖、日志 |
| [数据库连接失败](#数据库问题) | 无法连接数据库 | 检查服务状态、凭据、网络 |
| [API 请求超时](#api-问题) | 请求无响应 | 检查性能、负载、网络 |
| [前端页面异常](#前端问题) | 页面加载失败 | 检查构建、资源、浏览器 |
| [CI/CD 失败](#cicd-问题) | 流水线失败 | 查看日志、检查环境 |
| [性能问题](#性能问题) | 系统响应慢 | 分析瓶颈、优化资源 |

---

## 服务启动问题

### 后端服务无法启动

```bash
# 1. 检查端口占用
lsof -i :8020

# 2. 检查 Python 错误
cd web/backend
python -m uvicorn app.main:app --reload --log-level debug 2>&1 | head -50

# 3. 检查依赖
pip list | grep -E "(fastapi|uvicorn|pydantic)"

# 4. 检查配置文件
python -c "from app.core.config import settings; print(settings.dict())"
```

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `Address already in use` | 端口被占用 | `kill $(lsof -t -i:8020)` 或使用备用端口 8021 |
| `ModuleNotFoundError` | 依赖缺失 | `pip install -r requirements.txt` |
| `ImportError` | 导入路径错误 | 检查 `PYTHONPATH` 设置 |
| `DatabaseError` | 数据库连接失败 | 先启动数据库服务 |

### 前端服务无法启动

```bash
# 1. 检查 Node 版本
node --version

# 2. 检查依赖安装
cd web/frontend && ls -la node_modules | head -5

# 3. 重新安装
rm -rf node_modules package-lock.json && npm install

# 4. 检查端口占用
lsof -i :3020
```

### Docker 容器启动失败

```bash
# 查看容器日志
docker-compose logs --tail=100

# 检查容器状态
docker-compose ps

# 单独运行容器测试
docker-compose run --rm backend python -c "import app.main; print('OK')"

# 检查资源限制
docker stats
```

---

## 数据库问题

### PostgreSQL 连接失败

**错误**: `could not connect to server: Connection refused`

```bash
# 检查服务状态
sudo systemctl status postgresql || docker-compose ps | grep postgres

# 测试连接
psql -h localhost -U mystocks -d mystocks

# 检查端口
netstat -tlnp | grep 5432

# 检查连接池状态
PGPASSWORD=$POSTGRESQL_PASSWORD psql -h $POSTGRESQL_HOST -p $POSTGRESQL_PORT \
  -U $POSTGRESQL_USER -d $POSTGRESQL_DATABASE \
  -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"
```

### TDengine 连接失败

**错误**: `Unable to establish connection to TDengine`

```bash
# 检查服务状态
systemctl status taosd || docker-compose ps | grep tdengine

# 测试连接
taos -h localhost -P 6030 -u root -p your-tdengine-password

# 检查端口
netstat -tlnp | grep 6030

# 查看日志
tail -50 /var/log/taos/taosd.log
```

### 数据库连接池耗尽

**错误**: `could not obtain connection from the pool`

```bash
# 检查活跃连接
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';

# 检查最大连接数
SHOW max_connections;

# 查找泄漏连接（idle > 10 分钟）
SELECT pid, usename, application_name, state, query_start
FROM pg_stat_activity
WHERE state = 'idle' AND state_change < NOW() - INTERVAL '10 minutes';
```

**修复**:
```bash
# 调整连接池配置（.env）
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
```

---

## API 问题

### 请求超时

```bash
# 测试响应时间
curl -w "\nTime: %{time_total}s\n" -s http://localhost:8020/health

# 检查慢查询
PGPASSWORD=$POSTGRESQL_PASSWORD psql -h $POSTGRESQL_HOST -p $POSTGRESQL_PORT \
  -U $POSTGRESQL_USER -d $POSTGRESQL_DATABASE \
  -c "SELECT pid, now() - query_start AS duration, query
      FROM pg_stat_activity
      WHERE state != 'idle'
      ORDER BY duration DESC LIMIT 5;"
```

### API 返回 500 错误

```bash
# 开启调试模式
DEBUG=1 python -m uvicorn app.main:app --reload

# 查看错误日志
tail -50 /var/log/mystocks/error.log
```

### Swagger UI 无法访问

```bash
# 检查路由注册
curl http://localhost:8020/openapi.json | python3 -m json.tool | head -20

# 检查 CORS 配置
curl -s -I http://localhost:8020/docs | grep -i cors
```

### 登录 / Token 问题

| 症状 | 错误码 | 解决方案 |
|------|--------|----------|
| 用户名或密码错误 | 1001 | 重置密码: `python3 scripts/reset_password.py --username admin` |
| Token 过期 | 1002 | 延长过期时间: `.env` 中 `JWT_ACCESS_TOKEN_EXPIRE_MINUTES=7200` |
| 服务维护中 | 9003 | 等待维护完成或联系管理员 |
| 数据不更新 | — | `python3 scripts/update_market_data.py --force` |

---

## 前端问题

### 页面加载缓慢

```bash
# 检查网络耗时
curl -w "DNS:%{time_namelookup}s Connect:%{time_connect}s Total:%{time_total}s\n" \
  -s http://localhost:3020 > /dev/null

# 清除缓存重新构建
cd web/frontend && rm -rf dist && npm run build && npm run preview

# 检查资源大小
du -sh web/frontend/dist/
```

### 构建失败

```bash
# TypeScript 错误
npm run type-check 2>&1 | head -50

# ESLint 错误
npm run lint 2>&1 | head -50

# Node 内存限制
node --max-old-space-size=4096 build.js
```

### WebSocket 连接失败

```javascript
// 浏览器控制台
const ws = new WebSocket('ws://localhost:8020/ws');
ws.onopen = () => console.log('Connected!');
ws.onerror = (e) => console.error('Error:', e);
ws.onclose = (e) => console.log('Closed:', e.code, e.reason);
```

---

## CI/CD 问题

### GitHub Actions 失败

```bash
# 本地重现
./scripts/ci/code_quality_check.sh

# 检查依赖版本
pip freeze | grep -E "(fastapi|uvicorn|pytest)"
npm list --depth=0
```

### 测试失败

```bash
# 运行单个测试
pytest tests/ -v --tb=short 2>&1 | head -100

# 检查测试覆盖率
pytest --cov=src --cov-report=term-missing

# 跳过慢测试快速验证
pytest tests/ -v --ignore=tests/performance/ -x
```

### Docker 构建失败

```bash
# 查看详细构建日志
docker build -t mystocks-backend . --progress=plain 2>&1 | tail -100

# 单独测试构建步骤
docker run -it python:3.12-slim bash
```

---

## 性能问题

### CPU 使用率过高

```bash
# 查看进程 CPU
top -c

# 检查慢 API 端点
curl -s http://localhost:8020/api/v1/slow-endpoint -w "\nTime: %{time_total}s\n"

# 检查数据库慢查询（>5s）
PGPASSWORD=$POSTGRESQL_PASSWORD psql -h $POSTGRESQL_HOST -p $POSTGRESQL_PORT \
  -U $POSTGRESQL_USER -d $POSTGRESQL_DATABASE \
  -c "SELECT pid, now() - query_start AS duration, query
      FROM pg_stat_activity
      WHERE state != 'idle' AND now() - query_start > '5 seconds'
      ORDER BY duration DESC LIMIT 5;"
```

### 内存不足

```bash
# 查看内存使用
free -h

# 查看进程内存
ps aux --sort=-%mem | head -10

# Python 内存泄漏检查
python -c "
import tracemalloc
tracemalloc.start()
snapshot = tracemalloc.take_snapshot()
for stat in snapshot.statistics('lineno')[:10]:
    print(stat)
"

# 增加 .env 配置
# UVICORN_WORKERS=2
```

### 数据库性能问题

```bash
# 查询执行计划
EXPLAIN ANALYZE SELECT * FROM your_table WHERE condition;

# 检查缺失索引
SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;

# 检查表膨胀
SELECT schemaname, tablename, dead_tuple_ratio
FROM pg_stat_user_tables
ORDER BY dead_tuple_ratio DESC LIMIT 10;
```

---

## 日志查看

```bash
# API 日志
tail -f /var/log/mystocks/api.log
tail -n 100 /var/log/mystocks/api.log
grep -i error /var/log/mystocks/api.log
grep "<request_id>" /var/log/mystocks/api.log

# 数据库日志
tail -f /var/log/postgresql/postgresql.log
tail -f /var/log/taos/taosd.log

# Nginx 日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## 常用修复命令速查

```bash
# 重启后端
sudo systemctl restart mystocks-api
# 或
docker-compose restart backend

# 重启前端
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
```

---

## 问题报告模板

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
粘贴错误日志

## 已尝试的解决方案
1. 尝试 1 - 结果
2. 尝试 2 - 结果
```

---

## 相关文档

- [运维手册主页](index.md)
- [部署指南](deployment.md)
- [监控指南](monitoring.md)
- [API 错误码](../api/error-codes.md)
