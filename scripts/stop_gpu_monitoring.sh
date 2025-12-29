#!/bin/bash

# GPU监控仪表板停止脚本
# Stop Script for GPU Monitoring Dashboard

set -e

echo "🛑 停止GPU监控仪表板..."

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查PID文件
if [ -f "logs/gpu-api.pid" ]; then
    BACKEND_PID=$(cat logs/gpu-api.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        echo "停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        echo -e "${GREEN}✅ 后端服务已停止${NC}"
    else
        echo -e "${YELLOW}⚠️  后端服务未运行${NC}"
    fi
    rm logs/gpu-api.pid
else
    echo -e "${YELLOW}⚠️  后端PID文件不存在${NC}"
fi

if [ -f "logs/gpu-frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/gpu-frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        echo -e "${GREEN}✅ 前端服务已停止${NC}"
    else
        echo -e "${YELLOW}⚠️  前端服务未运行${NC}"
    fi
    rm logs/gpu-frontend.pid
else
    echo -e "${YELLOW}⚠️  前端PID文件不存在${NC}"
fi

# 清理可能的僵尸进程
echo ""
echo "清理僵尸进程..."
pkill -f "uvicorn.*gpu_monitoring_routes" 2>/dev/null || true
pkill -f "npm.*run.*dev" 2>/dev/null || true

echo -e "${GREEN}✅ 清理完成${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ GPU监控仪表板已停止${NC}"
echo -e "${GREEN}========================================${NC}"
