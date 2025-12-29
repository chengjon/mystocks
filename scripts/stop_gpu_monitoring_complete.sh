#!/bin/bash

# GPU监控 - 完整停止脚本
# Complete GPU Monitoring Stop Script

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║         GPU Monitoring - Stop All Services            ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

MODE=${1:-all}

echo "停止模式: $MODE"
echo ""

# 停止GPU API
if [ "$MODE" = "all" ] || [ "$MODE" = "api" ]; then
    if [ -f "logs/gpu-api.pid" ]; then
        API_PID=$(cat logs/gpu-api.pid)
        if ps -p $API_PID > /dev/null 2>&1; then
            echo "🛑 停止GPU API服务 (PID: $API_PID)..."
            kill $API_PID
            echo -e "${GREEN}✅ GPU API已停止${NC}"
        else
            echo -e "${YELLOW}⚠️  GPU API未运行${NC}"
        fi
        rm logs/gpu-api.pid
    fi
fi

# 停止GPU Exporter
if [ "$MODE" = "all" ] || [ "$MODE" = "exporter" ]; then
    if [ -f "logs/gpu-exporter.pid" ]; then
        EXPORTER_PID=$(cat logs/gpu-exporter.pid)
        if ps -p $EXPORTER_PID > /dev/null 2>&1; then
            echo "🛑 停止GPU Exporter (PID: $EXPORTER_PID)..."
            kill $EXPORTER_PID
            echo -e "${GREEN}✅ GPU Exporter已停止${NC}"
        else
            echo -e "${YELLOW}⚠️  GPU Exporter未运行${NC}"
        fi
        rm logs/gpu-exporter.pid
    fi
fi

# 停止Grafana和Prometheus (Docker)
if [ "$MODE" = "all" ] || [ "$MODE" = "grafana" ]; then
    if command -v docker &> /dev/null; then
        if [ -f "docker-compose.yml" ] || [ -f "monitoring-stack.yml" ]; then
            COMPOSE_FILE=$(find . -maxdepth 1 -name "*monitoring*.yml" | head -1)
            echo "🛑 停止Grafana和Prometheus..."
            docker-compose -f $COMPOSE_FILE stop prometheus grafana
            echo -e "${GREEN}✅ Grafana和Prometheus已停止${NC}"
        fi
    fi
fi

# 清理僵尸进程
echo ""
echo "🧹 清理僵尸进程..."

if [ "$MODE" = "all" ] || [ "$MODE" = "api" ]; then
    pkill -f "uvicorn.*gpu_monitoring_routes" 2>/dev/null || true
fi

if [ "$MODE" = "all" ] || [ "$MODE" = "exporter" ]; then
    pkill -f "python3.*prometheus_exporter" 2>/dev/null || true
fi

echo -e "${GREEN}✅ 清理完成${NC}"

# 显示最终状态
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║                   服务状态                              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# 检查服务状态
if [ "$MODE" = "all" ] || [ "$MODE" = "api" ]; then
    if ps aux | grep -v grep | grep -q "uvicorn.*gpu_monitoring_routes"; then
        echo -e "${RED}❌ GPU API仍在运行${NC}"
    else
        echo -e "${GREEN}✅ GPU API已停止${NC}"
    fi
fi

if [ "$MODE" = "all" ] || [ "$MODE" = "exporter" ]; then
    if ps aux | grep -v grep | grep -q "python3.*prometheus_exporter"; then
        echo -e "${RED}❌ GPU Exporter仍在运行${NC}"
    else
        echo -e "${GREEN}✅ GPU Exporter已停止${NC}"
    fi
fi

if [ "$MODE" = "all" ] || [ "$MODE" = "grafana" ]; then
    if command -v docker &> /dev/null; then
        PROMETHEUS_RUNNING=$(docker ps --filter "name=prometheus" --format "{{.Names}}" | wc -l)
        GRAFANA_RUNNING=$(docker ps --filter "name=grafana" --format "{{.Names}}" | wc -l)

        if [ $PROMETHEUS_RUNNING -gt 0 ]; then
            echo -e "${YELLOW}⚠️  Prometheus仍在运行 ($PROMETHEUS_RUNNING个容器）${NC}"
        else
            echo -e "${GREEN}✅ Prometheus已停止${NC}"
        fi

        if [ $GRAFANA_RUNNING -gt 0 ]; then
            echo -e "${YELLOW}⚠️  Grafana仍在运行 ($GRAFANA_RUNNING个容器）${NC}"
        else
            echo -e "${GREEN}✅ Grafana已停止${NC}"
        fi
    fi
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║               ✅ 停止完成！                              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "💡 提示:"
echo "  - 重新启动: ./scripts/start_gpu_monitoring_complete.sh"
echo "  - 查看日志: tail -f logs/*.log"
echo ""
