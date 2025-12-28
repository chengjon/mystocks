# MyStocks 部署指南

## 目录

- [环境要求](#环境要求)
- [Docker 部署](#docker-部署)
- [Kubernetes 部署](#kubernetes-部署)
- [手动部署](#手动部署)
- [配置说明](#配置说明)
- [验证部署](#验证部署)

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

- Python 3.11+
- PostgreSQL 15+
- TDengine 3.0+
- Redis 7.0+
- Nginx 1.20+

---

## Docker 部署

### 1. 安装 Docker

```bash
# Ubuntu
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker

# 添加用户到 docker 组
sudo usermod -aG docker $USER
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置
vim .env
```

### 3. 使用 Docker Compose 启动

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f api

# 停止所有服务
docker-compose down
```

### 4. Docker Compose 配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
      - tdengine
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: mystocks
      POSTGRES_USER: ${POSTGRES_USER:-mystocks}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  tdengine:
    image: tdengine/tdengine:3.0.0.0
    ports:
      - "6030:6030"
      - "6041:6041"
    volumes:
      - tdengine_data:/var/lib/taos
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
  tdengine_data:
  redis_data:
```

---

## Kubernetes 部署

### 1. 创建 Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: mystocks
```

```bash
kubectl apply -f k8s/namespace.yaml
```

### 2. 创建 ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mystocks-config
  namespace: mystocks
data:
  DATABASE_URL: "postgresql://mystocks:password@postgres:5432/mystocks"
  REDIS_URL: "redis://redis:6379/0"
  TDENGINE_URL: "taos://root:taosdata@tdengine:6030"
```

### 3. 创建 Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mystocks-api
  namespace: mystocks
spec:
  replicas: 2
  selector:
    matchLabels:
      app: mystocks-api
  template:
    metadata:
      labels:
        app: mystocks-api
    spec:
      containers:
      - name: api
        image: mystocks/api:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: mystocks-config
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 4. 创建 Service

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: mystocks-api
  namespace: mystocks
spec:
  selector:
    app: mystocks-api
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

### 5. 部署到 K8s

```bash
# 应用所有配置
kubectl apply -f k8s/

# 查看部署状态
kubectl get pods -n mystocks

# 查看日志
kubectl logs -f deployment/mystocks-api -n mystocks

# 扩缩容
kubectl scale deployment mystocks-api -n mystocks --replicas=3
```

---

## 手动部署

### 1. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装 Python 依赖
pip install -r requirements.txt

# 安装数据库驱动
pip install psycopg2-binary taospy
```

### 2. 配置数据库

```bash
# 初始化 PostgreSQL
psql -U postgres -c "CREATE DATABASE mystocks;"
psql -U postgres -c "CREATE USER mystocks WITH PASSWORD 'password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE mystocks TO mystocks;"

# 初始化 TDengine
taos -c "CREATE DATABASE IF NOT EXISTS mystocks;"
```

### 3. 初始化表结构

```bash
python scripts/database/init_tables.py
```

### 4. 启动服务

```bash
# 开发环境
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 生产环境
python -m gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 --access-logfile logs/access.log
```

### 5. 配置 Nginx

```nginx
# /etc/nginx/sites-available/mystocks
server {
    listen 80;
    server_name mystocks.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /app/static/;
    }
}

sudo ln -s /etc/nginx/sites-available/mystocks /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

---

## 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DATABASE_URL | PostgreSQL 连接字符串 | - |
| POSTGRES_HOST | PostgreSQL 主机 | localhost |
| POSTGRES_PORT | PostgreSQL 端口 | 5432 |
| POSTGRES_USER | PostgreSQL 用户 | mystocks |
| POSTGRES_PASSWORD | PostgreSQL 密码 | - |
| TDENGINE_URL | TDengine 连接字符串 | - |
| REDIS_URL | Redis 连接字符串 | - |
| JWT_SECRET_KEY | JWT 密钥 | - |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | Token 过期时间 | 7200 |
| LOG_LEVEL | 日志级别 | INFO |

### 生产环境配置

```bash
# .env.production
POSTGRES_HOST=10.0.0.10
POSTGRES_PORT=5432
POSTGRES_USER=mystocks
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=mystocks

TDENGINE_URL=taos://root:secure_password@10.0.0.20:6030

REDIS_URL=redis://:password@10.0.0.30:6379/0

JWT_SECRET_KEY=your-secure-random-key-here

LOG_LEVEL=WARNING
```

---

## 验证部署

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

预期响应:
```json
{
  "status": "healthy",
  "services": {
    "database": "up",
    "cache": "up",
    "tdengine": "up"
  }
}
```

### 2. API 测试

```bash
# 测试登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# 测试获取 K 线数据
curl "http://localhost:8000/api/v1/market/kline?symbol=000001.SZ&start_date=2025-01-01&end_date=2025-01-31"
```

### 3. 性能测试

```bash
# 使用 ab 进行压力测试
ab -n 1000 -c 10 http://localhost:8000/health
```

### 4. 查看监控指标

```bash
# Prometheus 指标
curl http://localhost:8000/metrics
```

---

## 故障排除

### 常见问题

1. **数据库连接失败**: 检查网络和防火墙设置
2. **端口被占用**: 使用 `lsof -i :8000` 检查
3. **内存不足**: 增加服务器资源或优化配置

详细故障排查请参阅 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
