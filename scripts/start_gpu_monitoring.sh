#!/bin/bash

# GPU监控仪表板启动脚本
# Quick Start Script for GPU Monitoring Dashboard

set -e

echo "🚀 启动GPU监控仪表板..."

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python3已安装${NC}"

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js未安装，前端无法启动${NC}"
    echo "请先安装Node.js: https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}✅ Node.js已安装${NC}"

# 检查GPU
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✅ 检测到NVIDIA GPU${NC}"
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
else
    echo -e "${YELLOW}⚠️  未检测到NVIDIA GPU，将使用模拟数据${NC}"
fi

# 检查PostgreSQL
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠️  PostgreSQL客户端未安装${NC}"
    echo "请确保PostgreSQL服务器正在运行"
else
    echo -e "${GREEN}✅ PostgreSQL客户端已安装${NC}"
fi

# 检查环境变量
if [ -z "$POSTGRESQL_HOST" ]; then
    echo -e "${YELLOW}⚠️  POSTGRESQL_HOST未设置，使用默认值localhost${NC}"
    export POSTGRESQL_HOST="localhost"
fi

if [ -z "$POSTGRESQL_PORT" ]; then
    echo -e "${YELLOW}⚠️  POSTGRESQL_PORT未设置，使用默认值5432${NC}"
    export POSTGRESQL_PORT="5432"
fi

if [ -z "$POSTGRESQL_USER" ]; then
    echo -e "${YELLOW}⚠️  POSTGRESQL_USER未设置，使用默认值postgres${NC}"
    export POSTGRESQL_USER="postgres"
fi

if [ -z "$POSTGRESQL_PASSWORD" ]; then
    echo -e "${YELLOW}⚠️  POSTGRESQL_PASSWORD未设置${NC}"
    echo "请设置环境变量: export POSTGRESQL_PASSWORD=your_password"
    exit 1
fi

if [ -z "$POSTGRESQL_DATABASE" ]; then
    echo -e "${YELLOW}⚠️  POSTGRESQL_DATABASE未设置，使用默认值mystocks${NC}"
    export POSTGRESQL_DATABASE="mystocks"
fi

echo -e "${GREEN}✅ 数据库配置检查通过${NC}"
echo "  Host: $POSTGRESQL_HOST:$POSTGRESQL_PORT"
echo "  User: $POSTGRESQL_USER"
echo "  Database: $POSTGRESQL_DATABASE"

# 检查后端依赖
echo ""
echo "📦 检查后端依赖..."
PYTHON_DEPS=("fastapi" "uvicorn" "pynvml" "psutil" "sqlalchemy" "pydantic" "cupy" "numpy")

for dep in "${PYTHON_DEPS[@]}"; do
    if python3 -c "import $dep" 2>/dev/null; then
        echo -e "${GREEN}✅ $dep${NC}"
    else
        echo -e "${RED}❌ $dep 未安装${NC}"
        echo "请运行: pip install $dep"
        exit 1
    fi
done

# 检查前端依赖
echo ""
echo "📦 检查前端依赖..."
cd web/frontend

if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

FRONTEND_DEPS=("vue" "element-plus" "echarts" "axios")

for dep in "${FRONTEND_DEPS[@]}"; do
    if [ -d "node_modules/$dep" ]; then
        echo -e "${GREEN}✅ $dep${NC}"
    else
        echo -e "${RED}❌ $dep 未安装${NC}"
        echo "请运行: npm install"
        exit 1
    fi
done

cd ../..

# 创建日志目录
mkdir -p logs

# 启动后端服务
echo ""
echo "🚀 启动后端服务..."
nohup uvicorn src.api.gpu_monitoring_routes:app \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info \
    > logs/gpu-api.log 2>&1 &

BACKEND_PID=$!
echo "后端服务已启动 (PID: $BACKEND_PID)"
echo "日志文件: logs/gpu-api.log"

# 等待后端启动
echo "等待后端服务启动..."
sleep 5

# 检查后端是否启动成功
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ 后端服务启动成功${NC}"
else
    echo -e "${RED}❌ 后端服务启动失败${NC}"
    echo "请检查日志: logs/gpu-api.log"
    exit 1
fi

# 启动前端服务
echo ""
echo "🚀 启动前端服务..."
cd web/frontend

nohup npm run dev > ../../logs/gpu-frontend.log 2>&1 &

FRONTEND_PID=$!
cd ../..

echo "前端服务已启动 (PID: $FRONTEND_PID)"
echo "日志文件: logs/gpu-frontend.log"

# 保存PID
echo $BACKEND_PID > logs/gpu-api.pid
echo $FRONTEND_PID > logs/gpu-frontend.pid

# 等待前端启动
echo "等待前端服务启动..."
sleep 10

# 显示访问信息
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ GPU监控仪表板启动成功！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📊 访问地址:"
echo "   前端: http://localhost:5173/gpu-monitoring"
echo "   后端API: http://localhost:8000/api/gpu"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "📝 日志文件:"
echo "   后端: logs/gpu-api.log"
echo "   前端: logs/gpu-frontend.log"
echo ""
echo "🛑 停止服务:"
echo "   ./stop_gpu_monitoring.sh"
echo ""
echo "📖 快速开始文档:"
echo "   docs/GPU_MONITORING_QUICK_START.md"
echo ""
echo -e "${GREEN}========================================${NC}"

# 测试API
echo ""
echo "🧪 测试API端点..."
echo ""
echo "测试: GET /api/gpu/metrics/0"
curl -s http://localhost:8000/api/gpu/metrics/0 | python3 -m json.tool | head -20
echo ""
echo "测试: GET /api/gpu/performance"
curl -s http://localhost:8000/api/gpu/performance | python3 -m json.tool
echo ""
