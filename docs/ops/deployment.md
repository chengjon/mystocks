# 部署指南

> **版本**: 1.0 | **更新日期**: 2026-07-12
> **维护者**: 运维
> **合并来源**: `operations/deployment/DEPLOYMENT.md` + `operations/deployment/PORT_CONFIGURATION.md` + `operations/deployment-guide.md`
> **详细源码备份**: 各源文件原位保留重定向头

---

## 环境要求

### 最低配置

| 组件 | CPU | 内存 | 存储 |
|------|-----|------|------|
| API 服务 | 2 核 | 4 GB | 20 GB |
| PostgreSQL | 1 核 | 2 GB | 50 GB |
| TDengine | 1 核 | 2 GB | 100 GB |
| Redis | 1 核 | 1 GB | 10 GB |

### 推荐配置

| 组件 | CPU | 内存 | 存储 |
|------|-----|------|------|
| API 服务 | 4 核 | 8 GB | 50 GB |
| PostgreSQL | 4 核 | 8 GB | 200 GB |
| TDengine | 4 核 | 8 GB | 500 GB |
| Redis | 2 核 | 4 GB | 50 GB |

### 软件依赖

- Python 3.12+
- PostgreSQL 17+ / TimescaleDB
- TDengine 3.3+
- Redis 7.0+
- Nginx 1.20+

---

## 端口配置

> 端口通过 `.env` 注入，禁止硬编码。

| 系统 | 变量 | 默认 | 备用 |
|------|------|------|------|
| 前端 ArtDeco | `FRONTEND_PORT` | 3020 | 3021 |
| 后端 ArtDeco | `BACKEND_PORT` | 8020 | 8021 |
| 前端 Quant Matrix Pro | `QM_FRONTEND_PORT` | 3030 | — |
| 后端 Quant Matrix Pro | `QM_BACKEND_PORT` | 8030 | — |

允许操作范围：前端 3020-3029，后端 8020-8029。

---

## Docker 部署

### 1. 安装 Docker

```bash
sudo apt-get update && sudo apt-get install -y docker.io docker-compose
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

### 2. 配置环境变量

```bash
cp .env.example .env
vim .env   # 填入数据库密码、JWT_SECRET_KEY 等
```

### 3. 启动服务

```bash
docker-compose up -d            # 启动全部服务
docker-compose ps               # 查看状态
docker-compose logs -f api      # 查看 API 日志
docker-compose down             # 停止
```

### Docker Compose 服务清单

| 服务 | 内部端口 | 说明 |
|------|---------|------|
| api | 8020 | FastAPI 后端 |
| postgres | 5432 | PostgreSQL + TimescaleDB |
| tdengine | 6030/6041 | TDengine 时序库 |
| redis | 6379 | Redis 缓存 |
| nginx | 80/443 | Nginx 反向代理 |

---

## Kubernetes 部署

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

kubectl get pods -n mystocks
kubectl logs -f deployment/mystocks-api -n mystocks
kubectl scale deployment mystocks-api -n mystocks --replicas=3
```

详见 [operations/deployment/DEPLOYMENT.md](../operations/deployment/DEPLOYMENT.md) K8s 章节完整 yaml。

---

## 手动部署

### 1. 安装依赖

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install psycopg2-binary taospy
```

### 2. 配置数据库

```bash
psql -U postgres -c "CREATE DATABASE mystocks;"
psql -U postgres -c "CREATE USER mystocks WITH PASSWORD 'password';"
taos -c "CREATE DATABASE IF NOT EXISTS mystocks;"
python scripts/database/init_tables.py
```

### 3. 启动服务

```bash
# 开发
python -m uvicorn web.backend.app.main:app --host 0.0.0.0 --port 8020 --reload

# 生产
python -m gunicorn web.backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8020 --access-logfile var/log/access.log
```

### 4. Nginx 配置

```nginx
server {
    listen 80;
    server_name mystocks.example.com;
    location / {
        proxy_pass http://127.0.0.1:8020;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 环境变量参考

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DATABASE_URL | PostgreSQL 连接字符串 | — |
| POSTGRES_HOST | PostgreSQL 主机 | localhost |
| POSTGRES_PORT | PostgreSQL 端口 | 5432 |
| TDENGINE_URL | TDengine 连接字符串 | — |
| REDIS_URL | Redis 连接字符串 | — |
| JWT_SECRET_KEY | JWT 密钥 | — |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | Token 过期时间 | 7200 |
| LOG_LEVEL | 日志级别 | INFO |

---

## 验证部署

```bash
# 健康检查
curl http://localhost:8020/health
# 预期: {"status":"healthy","services":{"database":"up","cache":"up","tdengine":"up"}}

# API 测试
curl -X POST http://localhost:8020/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

curl "http://localhost:8020/api/v1/market/kline?symbol=000001.SZ"

# 性能压测
ab -n 1000 -c 10 http://localhost:8020/health

# Prometheus 指标
curl http://localhost:8020/metrics
```

---

## 故障排除

| 症状 | 排查 |
|------|------|
| 数据库连接失败 | 检查网络、防火墙、`DATABASE_URL` |
| 端口被占用 | `lsof -i :8020` → `kill -9 <PID>` |
| 前端白屏 | `cd web/frontend && npm run build` → 检查控制台 |
| 内存不足 | 增加资源或降低 `gunicorn -w` 数 |
| Docker 权限 | `sudo usermod -aG docker $USER` 后重新登录 |

详细排障手册：[troubleshooting.md](troubleshooting.md)

---

## 相关文档

- [运维手册主页](index.md)
- [监控指南](monitoring.md)
- [排障指南](troubleshooting.md)
- [备份恢复](../operations/BACKUP_GUIDE.md)
- [CI/CD 架构](../operations/ci-cd/ARCHITECTURE.md)
