#!/bin/bash

# GPU监控 - 完整启动脚本（Grafana集成）
# Complete GPU Monitoring Startup Script with Grafana Integration

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         GPU Monitoring - Complete Startup           ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
MODE=${1:-all}  # all | api | exporter | grafana
GPU_API_PORT=8000
GPU_EXPORTER_PORT=9100
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

echo "启动模式: $MODE"
echo ""

# 检查依赖
echo "🔍 检查依赖..."

# Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python3已安装${NC}"

# Node.js
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js未安装${NC}"
fi

# Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker未安装${NC}"
    echo "Docker仅用于Grafana/Prometheus，可选"
fi

# NVIDIA GPU
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✅ 检测到NVIDIA GPU${NC}"
    nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
else
    echo -e "${YELLOW}⚠️  未检测到NVIDIA GPU${NC}"
fi

# 检查Python包
echo ""
echo "📦 检查Python包..."

PACKAGES=("fastapi" "uvicorn" "pynvml" "psutil" "sqlalchemy" "pydantic" "prometheus_client")
for pkg in "${PACKAGES[@]}"; do
    if python3 -c "import $pkg" 2>/dev/null; then
        echo -e "${GREEN}✅ $pkg${NC}"
    else
        echo -e "${RED}❌ $pkg 未安装${NC}"
    fi
done

# 检查端口
echo ""
echo "🔌 检查端口..."

check_port() {
    if netstat -tuln 2>/dev/null | grep -q ":$1 "; then
        echo -e "${YELLOW}⚠️  端口$1已被占用${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ 端口$1可用${NC}"
    return 0
}

check_port $GPU_API_PORT
check_port $GPU_EXPORTER_PORT
check_port $PROMETHEUS_PORT
check_port $GRAFANA_PORT

# 创建日志目录
mkdir -p logs

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                     启动服务                             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 根据模式启动服务
case "$MODE" in
    all)
        echo -e "${BLUE}🚀 启动所有服务...${NC}"
        echo ""
        start_gpu_api=true
        start_exporter=true
        start_grafana_prometheus=true
        ;;

    api)
        echo -e "${BLUE}🚀 仅启动GPU API服务...${NC}"
        echo ""
        start_gpu_api=true
        ;;

    exporter)
        echo -e "${BLUE}🚀 仅启动GPU Metrics Exporter...${NC}"
        echo ""
        start_exporter=true
        ;;

    grafana)
        echo -e "${BLUE}🚀 仅启动Grafana和Prometheus...${NC}"
        echo ""
        start_grafana_prometheus=true
        ;;

    *)
        echo -e "${RED}❌ 未知模式: $MODE${NC}"
        echo "用法: $0 [all|api|exporter|grafana]"
        echo ""
        echo "  all       - 启动所有服务（默认）"
        echo "  api       - 仅启动GPU API"
        echo "  exporter  - 仅启动GPU Metrics Exporter"
        echo "  grafana   - 仅启动Grafana和Prometheus"
        exit 1
        ;;
esac

# 启动GPU API
if [ "$start_gpu_api" = true ]; then
    echo "📊 启动GPU API服务..."

    nohup uvicorn src.api.gpu_monitoring_routes:app \
        --host 0.0.0.0 \
        --port $GPU_API_PORT \
        --log-level info \
        > logs/gpu-api.log 2>&1 &

    GPU_API_PID=$!
    echo $GPU_API_PID > logs/gpu-api.pid
    echo -e "${GREEN}✅ GPU API已启动 (PID: $GPU_API_PID, 端口: $GPU_API_PORT)${NC}"
fi

# 启动GPU Metrics Exporter
if [ "$start_exporter" = true ]; then
    echo ""
    echo "📈 启动GPU Metrics Exporter..."

    nohup python3 -u << 'PYTHON_EXPORTER_EOF' > logs/gpu-exporter.log 2>&1 &
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.gpu_monitoring.prometheus_exporter import GPUMetricsExporter

try:
    exporter = GPUMetricsExporter()
    exporter.start(port=$GPU_EXPORTER_PORT, interval=10)
except KeyboardInterrupt:
    print("\nExporter stopped")
PYTHON_EXPORTER_EOF

    GPU_EXPORTER_PID=$!
    echo $GPU_EXPORTER_PID > logs/gpu-exporter.pid
    echo -e "${GREEN}✅ GPU Exporter已启动 (PID: $GPU_EXPORTER_PID, 端口: $GPU_EXPORTER_PORT)${NC}"
fi

# 启动Grafana和Prometheus
if [ "$start_grafana_prometheus" = true ]; then
    echo ""
    echo "📝 启动Grafana和Prometheus..."

    if command -v docker &> /dev/null; then
        # 使用Docker启动
        if [ -f "docker-compose.yml" ] || [ -f "monitoring-stack.yml" ]; then
            COMPOSE_FILE=$(find . -maxdepth 1 -name "*monitoring*.yml" | head -1)
            echo "使用: $COMPOSE_FILE"
            docker-compose -f $COMPOSE_FILE up -d prometheus grafana
            echo -e "${GREEN}✅ Grafana和Prometheus已启动${NC}"
        else
            echo -e "${YELLOW}⚠️  未找到docker-compose文件${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Docker未安装，跳过Grafana/Prometheus${NC}"
        echo "请手动启动或安装Docker"
    fi
fi

# 等待服务启动
echo ""
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                   服务状态                              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 检查GPU API
if [ "$start_gpu_api" = true ]; then
    if curl -s http://localhost:$GPU_API_PORT/health > /dev/null; then
        echo -e "${GREEN}✅ GPU API: http://localhost:$GPU_API_PORT${NC}"
        echo -e "   健康检查: ${GREEN}OK${NC}"
    else
        echo -e "${RED}❌ GPU API: 启动失败${NC}"
    fi
fi

# 检查GPU Exporter
if [ "$start_exporter" = true ]; then
    if curl -s http://localhost:$GPU_EXPORTER_PORT/metrics > /dev/null; then
        echo -e "${GREEN}✅ GPU Exporter: http://localhost:$GPU_EXPORTER_PORT/metrics${NC}"
        echo -e "   Metrics: ${GREEN}OK${NC}"
    else
        echo -e "${RED}❌ GPU Exporter: 启动失败${NC}"
    fi
fi

# 检查Prometheus
if [ "$start_grafana_prometheus" = true ]; then
    if curl -s http://localhost:$PROMETHEUS_PORT/-/healthy > /dev/null; then
        echo -e "${GREEN}✅ Prometheus: http://localhost:$PROMETHEUS_PORT${NC}"
        echo -e "   健康检查: ${GREEN}OK${NC}"
    else
        echo -e "${YELLOW}⚠️  Prometheus: 未运行${NC}"
    fi
fi

# 检查Grafana
if [ "$start_grafana_prometheus" = true ]; then
    if curl -s http://localhost:$GRAFANA_PORT/api/health > /dev/null; then
        echo -e "${GREEN}✅ Grafana: http://localhost:$GRAFANA_PORT${NC}"
        echo -e "   登录: admin/admin${NC}"
    else
        echo -e "${YELLOW}⚠️  Grafana: 未运行${NC}"
    fi
fi

# 显示访问信息
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                   访问地址                             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

if [ "$start_gpu_api" = true ]; then
    echo "📊 GPU监控仪表板（独立）:"
    echo "   前端: http://localhost:5173/gpu-monitoring"
    echo "   API: http://localhost:$GPU_API_PORT/api/gpu"
    echo "   文档: http://localhost:$GPU_API_PORT/docs"
    echo ""
fi

if [ "$start_exporter" = true ]; then
    echo "📈 Prometheus Metrics:"
    echo "   Exporter: http://localhost:$GPU_EXPORTER_PORT/metrics"
    echo "   Prometheus: http://localhost:$PROMETHEUS_PORT/graph"
    echo ""
fi

if [ "$start_grafana_prometheus" = true ]; then
    echo "📝 Grafana Dashboard:"
    echo "   Grafana: http://localhost:$GRAFANA_PORT"
    echo "   Dashboard: http://localhost:$GRAFANA_PORT/d/gpu-monitoring/gpu-monitoring"
    echo "   登录: admin / admin"
    echo ""
fi

echo "📝 日志文件:"
echo "   GPU API: logs/gpu-api.log"
echo "   Exporter: logs/gpu-exporter.log"
if [ -f "monitoring-stack.yml" ]; then
    echo "   Grafana: docker-compose logs grafana"
    echo "   Prometheus: docker-compose logs prometheus"
fi

echo ""
echo "🛑 停止服务:"
echo "   ./scripts/stop_gpu_monitoring_complete.sh"
echo ""

echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║               ✅ 启动完成！                              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "💡 提示:"
echo "  - 使用 'all' 模式启动所有服务"
echo "  - 导入Dashboard: 配置文件位于 config/monitoring/dashboards/gpu-monitoring.json"
echo "  - 查看文档: docs/GPU_MONITORING_GRAFANA_INTEGRATION.md"
echo ""
