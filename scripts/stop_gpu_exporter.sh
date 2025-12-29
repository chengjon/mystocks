#!/bin/bash

# GPU监控 - Prometheus Exporter停止脚本
# Stop script for GPU Metrics Prometheus Exporter

set -e

echo "🛑 停止GPU Metrics Exporter..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查PID文件
if [ -f "logs/gpu-exporter.pid" ]; then
    EXPORTER_PID=$(cat logs/gpu-exporter.pid)
    if ps -p $EXPORTER_PID > /dev/null; then
        echo "停止GPU Metrics Exporter (PID: $EXPORTER_PID)..."
        kill $EXPORTER_PID
        echo -e "${GREEN}✅ GPU Metrics Exporter已停止${NC}"
    else
        echo -e "${YELLOW}⚠️  GPU Metrics Exporter未运行${NC}"
    fi
    rm logs/gpu-exporter.pid
else
    echo -e "${YELLOW}⚠️  Exporter PID文件不存在${NC}"
fi

# 清理可能的僵尸进程
echo ""
echo "清理僵尸进程..."
pkill -f "python3.*prometheus_exporter" 2>/dev/null || true

echo -e "${GREEN}✅ 清理完成${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ GPU Metrics Exporter已停止${NC}"
echo -e "${GREEN}========================================${NC}"
