# Vue + FastAPI 架构适配的部署实施指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## 📋 概述

本文档为基于Vue.js + FastAPI架构的MyStocks项目提供完整的部署实施指导，结合mystocks_spec项目的成熟经验，针对Vue.js前端和FastAPI后端的架构特点进行专门优化。

**适用架构**: Vue.js (前端) + FastAPI (后端)
**参考项目**: mystocks_spec (主分支)
**文档版本**: v1.0
**创建时间**: 2025-11-16

---

## 🏗️ 部署架构对比

### mystocks_spec vs Vue+FastAPI部署架构

| 部署组件 | mystocks_spec架构 | Vue+FastAPI架构 | 迁移策略 |
|---------|------------------|----------------|----------|
| **前端框架** | NiceGUI (Python生成) | Vue.js 3 + TypeScript | 完全重构前端部署 |
| **后端框架** | FastAPI | FastAPI | 保持核心后端架构 |
| **构建工具** | 自动构建 | Vite + Webpack | 现代化前端构建 |
| **容器化** | 单容器部署 | 分离前后端容器 | 微服务化部署 |
| **CI/CD** | Python集成 | Vue+FastAPI CI/CD | 分离构建流水线 |
| **监控系统** | Python内置 | Vue.js + FastAPI监控 | 完整监控适配 |

### 共享底层架构（100%兼容）

```
部署基础设施
├── AI策略引擎 (完全复用)
│   ├── 动量策略 (mystocks_spec/ai_strategy_analyzer.py)
│   ├── 均值回归策略
│   └── ML基础策略
├── GPU加速系统 (完全复用)
│   ├── RAPIDS (cuDF/cuML)
│   ├── GPU API服务
│   └── 三级缓存系统
├── 监控系统 (完全复用)
│   ├── AIAlertManager
│   ├── AIRealtimeMonitor
│   └── 智能告警系统
└── 数据存储层 (完全复用)
    ├── PostgreSQL (通用数据)
    └── TDengine (时序数据)
```

---

## 🚀 部署实施路线图

### Phase 1: 环境准备与基础架构 (Week 1)
**目标**: 搭建Vue.js + FastAPI部署环境

#### 1.1 开发环境准备
```bash
# 创建项目结构
mkdir vue-mystocks
cd vue-mystocks
mkdir -p backend frontend shared scripts

# 后端环境准备
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install fastapi uvicorn pydantic python-multipart

# 前端环境准备
cd ../frontend
npm init -y
npm install vue@3 vue-router@4 pinia element-plus axios
npm install -D vite @vitejs/plugin-vue typescript @types/node
```

#### 1.2 项目配置文件
```yaml
# docker-compose.yml
version: '3.8'

services:
  # Vue.js前端服务
  vue-frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "8080:80"
    environment:
      - VUE_APP_API_BASE_URL=http://localhost:8000
    depends_on:
      - fastapi-backend
    networks:
      - mystocks-network

  # FastAPI后端服务
  fastapi-backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ENV=production
      - DATABASE_URL=postgresql://admin:password@postgresql:5432/mystocks
      - GPU_ENABLED=true
    volumes:
      - ./shared:/app/shared
    depends_on:
      - postgresql
      - tdengine
      - redis
    networks:
      - mystocks-network

  # PostgreSQL数据库
  postgresql:
    image: postgres:17
    environment:
      - POSTGRES_DB=mystocks
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - mystocks-network

  # TDengine时序数据库
  tdengine:
    image: tdengine/tdengine:3.3.2.0
    ports:
      - "6030:6030"
      - "6041:6041"
      - "6043:6043"
    volumes:
      - tdengine_data:/var/lib/taos
    environment:
      - TAOS_FQDN=tdengine
    networks:
      - mystocks-network

  # Redis缓存
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - mystocks-network

  # GPU加速服务（可选）
  gpu-acceleration:
    image: rapidsai/rapidsai:23.12-cuda11.8-devel-ubuntu20.04-py3.11
    environment:
      - CUDA_VISIBLE_DEVICES=0
    volumes:
      - ./shared:/app/shared
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    networks:
      - mystocks-network

volumes:
  postgres_data:
  tdengine_data:
  redis_data:

networks:
  mystocks-network:
    driver: bridge
```

#### 1.3 后端Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### 1.4 前端Dockerfile
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS build

WORKDIR /app

# 复制package文件
COPY package*.json ./
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产环境
FROM nginx:alpine

# 复制构建结果
COPY --from=build /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Phase 2: 后端部署配置 (Week 2)
**目标**: 完善FastAPI后端部署配置

#### 2.1 生产环境配置
```python
# backend/app/core/config.py
from pydantic import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # 基础配置
    app_name: str = "MyStocks AI Platform"
    app_version: str = "1.0.0"
    debug: bool = False

    # 数据库配置
    database_url: str = os.getenv("DATABASE_URL", "postgresql://admin:password@localhost:5432/mystocks")
    tdengine_url: str = os.getenv("TDENGINE_URL", "taos://localhost:6030")

    # API配置
    api_prefix: str = "/api/v1"
    allowed_origins: list = [
        "http://localhost:8080",
        "http://localhost:3000",
        "http://localhost:5173",
        "https://yourdomain.com"
    ]

    # GPU加速配置
    gpu_enabled: bool = os.getenv("GPU_ENABLED", "false").lower() == "true"

    # 缓存配置
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # 日志配置
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # 安全配置
    secret_key: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-this")
    access_token_expire_minutes: int = 60 * 24 * 7  # 7天

    class Config:
        env_file = ".env"

settings = Settings()
```

#### 2.2 后端启动脚本
```bash
# backend/start.sh
#!/bin/bash

# 启动FastAPI应用
echo "🚀 启动MyStocks FastAPI后端..."

# 等待数据库就绪
echo "⏳ 等待数据库就绪..."
python -c "
import time
import psycopg2
from urllib.parse import urlparse

def wait_for_db():
    db_url = '$DATABASE_URL'
    parsed = urlparse(db_url)
    for i in range(30):
        try:
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path[1:]
            )
            conn.close()
            print('✅ 数据库连接成功')
            return True
        except Exception as e:
            print(f'⏳ 等待数据库... ({i+1}/30)')
            time.sleep(2)
    return False

if not wait_for_db():
    print('❌ 数据库连接失败')
    exit(1)
"

# 启动应用
if [ "$ENV" = "development" ]; then
    echo "🔧 开发模式启动"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
else
    echo "🚀 生产模式启动"
    gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120
fi
```

#### 2.3 后端健康检查
```python
# backend/app/api/endpoints/health.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import time
import logging
from datetime import datetime

router = APIRouter(prefix="/api/v1/health", tags=["health"])

@router.get("/")
async def health_check() -> Dict[str, Any]:
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "MyStocks FastAPI Backend",
        "version": "1.0.0"
    }

@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """就绪检查端点"""
    # 检查关键服务是否可用
    checks = {
        "database": await check_database_connection(),
        "redis": await check_redis_connection(),
        "gpu": await check_gpu_availability()
    }

    all_healthy = all(check.get("status") == "healthy" for check in checks.values())

    return {
        "status": "ready" if all_healthy else "not_ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }

@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """存活检查端点"""
    # 检查服务基本功能
    start_time = time.time()

    # 模拟简单操作
    try:
        # 这里可以添加一些轻量级的检查操作
        result = {"status": "healthy", "response_time": time.time() - start_time}
    except Exception as e:
        result = {"status": "unhealthy", "error": str(e)}

    return {
        "status": result["status"],
        "timestamp": datetime.utcnow().isoformat(),
        "response_time": result.get("response_time", 0)
    }

async def check_database_connection() -> Dict[str, Any]:
    """检查数据库连接"""
    try:
        # 实际的数据库连接检查逻辑
        # 这里简化处理，实际应连接数据库执行简单查询
        return {"status": "healthy", "message": "Database connection OK"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_redis_connection() -> Dict[str, Any]:
    """检查Redis连接"""
    try:
        # 实际的Redis连接检查逻辑
        return {"status": "healthy", "message": "Redis connection OK"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_gpu_availability() -> Dict[str, Any]:
    """检查GPU可用性"""
    try:
        if os.getenv("GPU_ENABLED", "false").lower() == "true":
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                return {
                    "status": "healthy",
                    "message": f"GPU available: {len(gpus)} devices found",
                    "gpu_count": len(gpus)
                }
        else:
            return {"status": "disabled", "message": "GPU acceleration disabled"}
    except ImportError:
        return {"status": "unavailable", "message": "GPU libraries not installed"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### Phase 3: 前端部署配置 (Week 3)
**目标**: 完善Vue.js前端部署配置

#### 3.1 前端构建配置
```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@views': resolve(__dirname, 'src/views'),
      '@stores': resolve(__dirname, 'src/stores'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@services': resolve(__dirname, 'src/services')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          'element-plus': ['element-plus'],
          'vue-router': ['vue-router'],
          'pinia': ['pinia'],
          'axios': ['axios']
        }
      }
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@use "@/styles/variables.scss" as *;`
      }
    }
  }
})
```

#### 3.2 前端环境配置
```json
// frontend/.env.production
VUE_APP_API_BASE_URL=https://api.yourdomain.com
VUE_APP_ENV=production
VUE_APP_VERSION=1.0.0
VUE_APP_ENABLE_GPU_ACCELERATION=true
VUE_APP_MONITORING_INTERVAL=5000
```

#### 3.3 前端部署脚本
```bash
# frontend/deploy.sh
#!/bin/bash

echo "🚀 开始部署Vue.js前端..."

# 检查Node.js版本
NODE_VERSION=$(node --version)
echo "Node.js版本: $NODE_VERSION"

# 安装依赖
echo "📦 安装前端依赖..."
npm ci --only=production

# 构建应用
echo "🏗️ 构建前端应用..."
npm run build

# 检查构建结果
if [ $? -eq 0 ]; then
    echo "✅ 前端构建成功"

    # 复制到Nginx目录
    if [ -d "/usr/share/nginx/html" ]; then
        echo "🔄 复制构建结果到Nginx..."
        cp -r dist/* /usr/share/nginx/html/
        echo "✅ 部署完成"
    else
        echo "⚠️ Nginx目录不存在，跳过复制"
        echo "构建结果在 ./dist 目录"
    fi
else
    echo "❌ 前端构建失败"
    exit 1
fi
```

#### 3.4 Nginx配置
```nginx
# frontend/nginx.conf
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # 基本配置
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss;

    server {
        listen 80;
        server_name localhost;

        # 前端静态文件
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
            expires 1m;
        }

        # API代理
        location /api/ {
            proxy_pass http://fastapi-backend:8000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # 超时设置
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # 健康检查
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

### Phase 4: CI/CD 集成 (Week 4)
**目标**: 实现完整的CI/CD流水线

#### 4.1 GitHub Actions 工作流
```yaml
# .github/workflows/deploy.yml
name: Deploy Vue + FastAPI Application

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.12]
        node-version: [18.x]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install Python dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run Python tests
      run: |
        cd backend
        pytest tests/ --cov=app/ --cov-report=xml

    - name: Set up Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}

    - name: Install Node.js dependencies
      run: |
        cd frontend
        npm ci

    - name: Run Node.js tests
      run: |
        cd frontend
        npm run test:unit

    - name: Run linting
      run: |
        cd frontend
        npm run lint

  build-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18.x'

    - name: Build frontend
      run: |
        cd frontend
        npm ci
        npm run build

    - name: Upload frontend artifacts
      uses: actions/upload-artifact@v3
      with:
        name: frontend-build
        path: frontend/dist

  build-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Build backend Docker image
      run: |
        docker build -t ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-backend:latest ./backend

    - name: Log in to registry
      run: echo "${{ secrets.GITHUB_TOKEN }}" | docker login ${{ env.REGISTRY }} -u ${{ github.actor }} --password-stdin

    - name: Push backend image
      run: docker push ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-backend:latest

  deploy:
    needs: [build-frontend, build-backend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
    - uses: actions/checkout@v4

    - name: Download frontend build
      uses: actions/download-artifact@v3
      with:
        name: frontend-build
        path: frontend/dist

    - name: Deploy to production
      run: |
        # 这里添加实际的部署命令
        echo "Deploying to production..."
        # docker-compose up -d
```

#### 4.2 部署验证脚本
```bash
# scripts/deployment-validation.sh
#!/bin/bash

echo "🔍 验证部署状态..."

# 检查服务是否运行
echo "⏳ 检查服务状态..."

# 检查后端API
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$BACKEND_STATUS" = "200" ]; then
    echo "✅ 后端服务运行正常 (HTTP $BACKEND_STATUS)"
else
    echo "❌ 后端服务异常 (HTTP $BACKEND_STATUS)"
fi

# 检查前端页面
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ 前端服务运行正常 (HTTP $FRONTEND_STATUS)"
else
    echo "❌ 前端服务异常 (HTTP $FRONTEND_STATUS)"
fi

# 检查API连通性
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health/)
if [ "$API_STATUS" = "200" ]; then
    echo "✅ API连通性正常 (HTTP $API_STATUS)"
else
    echo "❌ API连通性异常 (HTTP $API_STATUS)"
fi

# 检查数据库连接
DB_CHECK=$(docker exec -it vue-mystocks-postgresql-1 pg_isready -h localhost -U admin 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ 数据库连接正常"
else
    echo "❌ 数据库连接异常"
fi

# 检查GPU状态（如果有）
if command -v nvidia-smi &> /dev/null; then
    GPU_COUNT=$(nvidia-smi --query-gpu=name --format=csv,noheader,nounits | wc -l)
    if [ "$GPU_COUNT" -gt 0 ]; then
        echo "✅ GPU设备可用 ($GPU_COUNT 个)"
    else
        echo "⚠️ 未检测到GPU设备"
    fi
fi

echo "✅ 部署验证完成"
```

### Phase 5: 监控与运维 (Week 5)
**目标**: 建立完整的监控和运维体系

#### 5.1 应用性能监控
```python
# backend/app/middleware/performance.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import Callable

class PerformanceMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""

    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("performance")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        # 记录性能指标
        self.logger.info(
            f"REQUEST - {request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Time: {process_time:.3f}s "
            f"- IP: {request.client.host}"
        )

        # 这里可以添加到Prometheus等监控系统
        if hasattr(request.state, 'metrics'):
            request.state.metrics.add_request_time(process_time)

        return response

# 在main.py中使用
from app.middleware.performance import PerformanceMiddleware

app.add_middleware(PerformanceMiddleware)
```

#### 5.2 日志配置
```python
# backend/app/core/logging_config.py
import logging
from pythonjsonlogger import jsonlogger
import os
from datetime import datetime

def setup_logging():
    """配置日志系统"""

    # 获取日志级别
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    level = getattr(logging, log_level)

    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 创建JSON格式的日志处理器
    if os.getenv('JSON_LOGS', 'false').lower() == 'true':
        json_handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s',
            rename_fields={
                'timestamp': '@timestamp',
                'level': 'level',
                'name': 'logger',
            }
        )
        json_handler.setFormatter(formatter)
        root_logger.addHandler(json_handler)
    else:
        # 普通格式日志
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # 配置特定模块的日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # 文件日志
    if os.getenv('LOG_TO_FILE', 'false').lower() == 'true':
        file_handler = logging.FileHandler('app.log')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

# 使用示例
if __name__ != "__main__":
    setup_logging()
```

---

## 🚀 部署操作指南

### 1. 本地开发环境部署
```bash
# 克隆项目
git clone <repository-url>
cd vue-mystocks

# 启动开发环境
docker-compose up -d

# 或者分别启动
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

cd frontend
npm run dev
```

### 2. 生产环境部署
```bash
# 构建生产镜像
docker-compose -f docker-compose.prod.yml build

# 启动生产环境
docker-compose -f docker-compose.prod.yml up -d

# 验证部署
./scripts/deployment-validation.sh
```

### 3. 蓝绿部署策略
```bash
# 蓝绿部署脚本
./scripts/blue-green-deploy.sh
```

### 4. 回滚策略
```bash
# 回滚到上一个版本
./scripts/rollback.sh
```

---

## 🔧 故障排查

### 1. 常见问题及解决方案

#### 问题1: 前端无法连接后端API
**症状**: 前端显示"网络错误"或"API连接失败"
**解决方案**:
```bash
# 检查后端服务状态
docker-compose logs fastapi-backend

# 检查网络连接
docker-compose exec vue-frontend ping fastapi-backend

# 检查API端点
curl http://localhost:8000/health
```

#### 问题2: GPU加速不可用
**症状**: GPU相关功能报错或性能未提升
**解决方案**:
```bash
# 检查GPU驱动
nvidia-smi

# 检查CUDA安装
nvcc --version

# 检查RAPIDS库
docker-compose exec fastapi-backend python -c "import cudf; print(cudf.__version__)"
```

#### 问题3: 数据库连接失败
**症状**: 应用启动失败，报数据库连接错误
**解决方案**:
```bash
# 检查数据库服务
docker-compose logs postgresql

# 检查数据库状态
docker-compose exec postgresql pg_isready

# 检查网络连接
docker-compose exec fastapi-backend ping postgresql
```

### 2. 监控命令
```bash
# 查看所有服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 查看资源使用
docker stats

# 查看应用健康状态
curl http://localhost:8000/api/v1/health
curl http://localhost:8080/health
```

---

## 📊 性能优化

### 1. 前端优化
- 启用Gzip压缩
- 使用CDN加速静态资源
- 实现代码分割和懒加载
- 优化图片和资源大小

### 2. 后端优化
- 使用连接池
- 实现缓存策略
- 优化数据库查询
- 启用GPU加速

### 3. 部署优化
- 使用多阶段构建
- 实现健康检查
- 配置资源限制
- 设置自动扩缩容

---

## 🛡️ 安全配置

### 1. 容器安全
- 使用非root用户运行
- 最小化镜像大小
- 定期更新基础镜像
- 扫描镜像漏洞

### 2. API安全
- 实现身份验证
- 设置请求限制
- 使用HTTPS
- 验证输入数据

### 3. 网络安全
- 配置网络策略
- 限制端口暴露
- 使用VPN访问
- 实现防火墙规则

---

**文档版本**: v1.0
**更新时间**: 2025-11-16
**维护者**: MyStocks开发团队
