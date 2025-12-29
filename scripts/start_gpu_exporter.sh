#!/bin/bash

# GPU监控 - Prometheus Exporter启动脚本
# Start script for GPU Metrics Prometheus Exporter

set -e

echo "=========================================="
echo "  GPU Metrics Prometheus Exporter"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 默认配置
PORT=${GPU_EXPORTER_PORT:-9110}
INTERVAL=${GPU_EXPORTER_INTERVAL:-10}

echo "配置信息:"
echo "  端口: $PORT"
echo "  更新间隔: ${INTERVAL}秒"
echo ""

# 检查依赖
echo "检查依赖..."

if ! python3 -c "import prometheus_client" 2>/dev/null; then
    echo -e "${RED}❌ prometheus_client未安装${NC}"
    echo "请运行: pip install prometheus_client"
    exit 1
fi
echo -e "${GREEN}✅ prometheus_client已安装${NC}"

if ! python3 -c "from src.gpu_monitoring.gpu_monitor_service import GPUMonitoringService" 2>/dev/null; then
    echo -e "${RED}❌ GPU监控模块未找到${NC}"
    echo "请确保src/gpu_monitoring/目录存在"
    exit 1
fi
echo -e "${GREEN}✅ GPU监控模块已找到${NC}"

echo ""
echo "检查端口 $PORT..."
if netstat -tuln 2>/dev/null | grep -q ":$PORT "; then
    echo -e "${YELLOW}⚠️  端口$PORT已被占用${NC}"
    echo "请检查是否已有进程在运行，或修改GPU_EXPORTER_PORT环境变量"
    exit 1
fi
echo -e "${GREEN}✅ 端口$PORT可用${NC}"

# 创建日志目录
mkdir -p logs

# 启动exporter
echo ""
echo -e "${GREEN}🚀 启动GPU Metrics Exporter...${NC}"
echo ""
echo "访问地址:"
echo "  Metrics: http://localhost:$PORT/metrics"
echo "  Health: http://localhost:$PORT/health"
echo ""

# 创建临时Python脚本
cat > /tmp/gpu_exporter_launcher.py << EOF
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, '/opt/claude/mystocks_phase6_monitoring')

from src.gpu_monitoring.prometheus_exporter import GPUMetricsExporter

# 创建exporter实例
exporter = GPUMetricsExporter()

# 启动exporter
try:
    exporter.start(port=${PORT}, interval=${INTERVAL})
except KeyboardInterrupt:
    print("\n🛑 Shutting down GPU Metrics Exporter")
    exporter.running = False
EOF

# 使用nohup启动
nohup python3 -u /tmp/gpu_exporter_launcher.py > logs/gpu-exporter.log 2>&1 &

EXPORTER_PID=$!
echo "GPU Metrics Exporter已启动 (PID: $EXPORTER_PID)"
echo "日志文件: logs/gpu-exporter.log"

# 保存PID
echo $EXPORTER_PID > logs/gpu-exporter.pid

# 等待服务启动
echo "等待服务启动..."
sleep 3

# 检查服务是否启动成功
if curl -s http://localhost:$PORT/metrics > /dev/null; then
    echo -e "${GREEN}✅ GPU Metrics Exporter启动成功${NC}"
    echo ""
    echo "测试metrics端点..."
    curl -s http://localhost:$PORT/metrics | grep "^gpu_" | head -20
else
    echo -e "${RED}❌ GPU Metrics Exporter启动失败${NC}"
    echo "请检查日志: logs/gpu-exporter.log"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ GPU Metrics Exporter运行中${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📊 Prometheus配置:"
echo ""
echo "在prometheus.yml中添加以下配置:"
echo ""
echo "scrape_configs:"
echo "  - job_name: 'gpu-metrics'"
echo "    scrape_interval: 10s"
echo "    static_configs:"
echo "      - targets: ['localhost:$PORT']"
echo ""
echo "📝 查看日志:"
echo "   tail -f logs/gpu-exporter.log"
echo ""
echo "🛑 停止服务:"
echo "   ./scripts/stop_gpu_exporter.sh"
echo ""
echo -e "${GREEN}========================================${NC}"
