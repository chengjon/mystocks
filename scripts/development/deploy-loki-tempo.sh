#!/bin/bash

set -e

echo "=========================================="
echo "MyStocks Loki & Tempo 部署脚本"
echo "=========================================="

WORK_DIR="/opt/claude/mystocks_phase6_monitoring/monitoring-stack"
cd "$WORK_DIR"

echo "1. 检查必要的目录..."
mkdir -p config data/loki data/tempo data/prometheus data/grafana provisioning

echo "2. 检查配置文件..."
if [ ! -f config/loki-config.yaml ]; then
    echo "错误: config/loki-config.yaml 不存在"
    exit 1
fi

if [ ! -f config/tempo-config.yaml ]; then
    echo "错误: config/tempo-config.yaml 不存在"
    exit 1
fi

echo "3. 检查 Docker 镜像..."
LOKI_EXISTS=$(docker images -q grafana/loki:latest)
TEMPO_EXISTS=$(docker images -q grafana/tempo:latest)

if [ -z "$LOKI_EXISTS" ]; then
    echo "错误: grafana/loki:latest 镜像不存在"
    echo "请先运行以下命令下载镜像:"
    echo "  docker_pull_acc grafana/loki:latest"
    exit 1
fi

if [ -z "$TEMPO_EXISTS" ]; then
    echo "错误: grafana/tempo:latest 镜像不存在"
    echo "请先运行以下命令下载镜像:"
    echo "  docker_pull_acc grafana/tempo:latest"
    exit 1
fi

echo "4. 停止现有容器（如果存在）..."
docker stop mystocks-loki mystocks-tempo 2>/dev/null || true
docker rm mystocks-loki mystocks-tempo 2>/dev/null || true

echo "5. 启动 Loki..."
docker run -d \
  --name mystocks-loki \
  --network mystocks-monitoring \
  -p 3100:3100 \
  -p 9096:9096 \
  -v $(pwd)/config/loki-config.yaml:/etc/loki/local-config.yaml:ro \
  -v $(pwd)/data/loki:/tmp/loki \
  --restart unless-stopped \
  grafana/loki:latest \
  -config.file=/etc/loki/local-config.yaml

echo "6. 启动 Tempo..."
docker run -d \
  --name mystocks-tempo \
  --network mystocks-monitoring \
  -p 3200:3200 \
  -p 4317:4317 \
  -p 4318:4318 \
  -v $(pwd)/config/tempo-config.yaml:/etc/tempo-config.yaml:ro \
  -v $(pwd)/data/tempo:/tmp/tempo \
  --restart unless-stopped \
  grafana/tempo:latest \
  -config.file=/etc/tempo-config.yaml

echo "7. 等待服务启动..."
sleep 5

echo "8. 验证服务状态..."
LOKI_STATUS=$(docker ps --filter "name=mystocks-loki" --format "{{.Status}}")
TEMPO_STATUS=$(docker ps --filter "name=mystocks-tempo" --format "{{.Status}}")

echo ""
echo "=========================================="
echo "部署完成！"
echo "=========================================="
echo ""
echo "服务状态:"
echo "  Loki:   $LOKI_STATUS"
echo "  Tempo:  $TEMPO_STATUS"
echo ""
echo "访问地址:"
echo "  Loki:   http://localhost:3100"
echo "  Tempo:  http://localhost:3200"
echo "  Grafana: http://localhost:3000"
echo ""
echo "下一步: 在 Grafana 中添加 Loki 和 Tempo 数据源"
echo ""
