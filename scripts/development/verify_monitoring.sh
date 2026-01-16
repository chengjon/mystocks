#!/bin/bash

# 监控系统验证脚本
# 验证Grafana数据源、Dashboard、Loki和Tempo功能

echo "=================================="
echo "MyStocks 监控系统验证"
echo "=================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试函数
test_service() {
    local name=$1
    local url=$2
    local auth=$3

    echo -n "Testing $name... "
    if [ -z "$auth" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url" --user "$auth")
    fi

    if [ "$response" = "200" ] || [ "$response" = "204" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $response)"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $response)"
        return 1
    fi
}

echo "1. 服务健康检查"
echo "----------------------------------------"
test_service "Prometheus" "http://localhost:9090/-/ready"
test_service "Grafana" "http://localhost:3000/api/health"
test_service "Loki" "http://localhost:3100/ready"
test_service "Tempo" "http://localhost:3200/ready"
test_service "Node Exporter" "http://localhost:9100/metrics"
echo ""

echo "2. Grafana数据源验证"
echo "----------------------------------------"
echo "Checking Prometheus datasource..."
ds_result=$(curl -s 'http://localhost:3000/api/datasources' --user admin:admin 2>&1)

if echo "$ds_result" | grep -q "Prometheus"; then
    echo -e "${GREEN}✅ Prometheus datasource found${NC}"
else
    echo -e "${RED}❌ Prometheus datasource NOT found${NC}"
    echo "Response: $ds_result"
fi

if echo "$ds_result" | grep -q "Loki"; then
    echo -e "${GREEN}✅ Loki datasource found${NC}"
else
    echo -e "${RED}❌ Loki datasource NOT found${NC}"
fi

if echo "$ds_result" | grep -q "Tempo"; then
    echo -e "${GREEN}✅ Tempo datasource found${NC}"
else
    echo -e "${YELLOW}⚠️  Tempo datasource NOT found (optional)${NC}"
fi
echo ""

echo "3. Grafana Dashboard验证"
echo "----------------------------------------"
echo "Checking for provisioned dashboards..."

dashboard_list=$(curl -s 'http://localhost:3000/api/search' --user admin:admin 2>&1)

if echo "$dashboard_list" | grep -q "GPU"; then
    echo -e "${GREEN}✅ GPU监控Dashboard已加载${NC}"
else
    echo -e "${YELLOW}⚠️  GPU监控Dashboard未自动加载 (需手动导入)${NC}"
fi

if echo "$dashboard_list" | grep -q "API.*performance" || echo "$dashboard_list" | grep -q "API性能"; then
    echo -e "${GREEN}✅ API性能Dashboard已加载${NC}"
else
    echo -e "${YELLOW}⚠️  API性能Dashboard未自动加载 (需手动导入)${NC}"
fi

if echo "$dashboard_list" | grep -q "系统资源" || echo "$dashboard_list" | grep -q "System"; then
    echo -e "${GREEN}✅ 系统资源Dashboard已加载${NC}"
else
    echo -e "${YELLOW}⚠️  系统资源Dashboard未自动加载 (需手动导入)${NC}"
fi

if echo "$dashboard_list" | grep -q "MyStocks"; then
    echo -e "${GREEN}✅ MyStocks健康Dashboard已加载${NC}"
else
    echo -e "${RED}❌ MyStocks健康Dashboard未加载${NC}"
fi
echo ""

echo "4. Prometheus指标抓取验证"
echo "----------------------------------------"
echo "Checking scraped targets..."
targets=$(curl -s http://localhost:9090/api/v1/targets)

backend_status=$(echo "$targets" | grep -o '"job":"mystocks-backend"' | wc -l)
node_exporter_status=$(echo "$targets" | grep -o '"job":"node"' | wc -l)

if [ "$backend_status" -gt 0 ]; then
    echo -e "${GREEN}✅ MyStocks后端目标已配置${NC}"
else
    echo -e "${RED}❌ MyStocks后端目标未配置${NC}"
fi

if [ "$node_exporter_status" -gt 0 ]; then
    echo -e "${GREEN}✅ Node Exporter目标已配置${NC}"
else
    echo -e "${RED}❌ Node Exporter目标未配置${NC}"
fi

# 检查目标状态
up_targets=$(echo "$targets" | grep -o '"health":"up"' | wc -l)
total_targets=$(echo "$targets" | grep -o '"health":' | wc -l)

echo "目标状态: $up_targets/$total_targets UP"
echo ""

echo "5. Tempo追踪功能测试"
echo "----------------------------------------"
echo "Testing Tempo search API..."
tempo_search=$(curl -s http://localhost:3200/api/search 2>&1)

if echo "$tempo_search" | grep -q "traces"; then
    echo -e "${GREEN}✅ Tempo搜索API正常${NC}"
    echo "当前追踪数: $(echo "$tempo_search" | grep -o '"totalJobs":[0-9]*' | grep -o '[0-9]*')"
else
    echo -e "${RED}❌ Tempo搜索API异常${NC}"
    echo "Response: $tempo_search"
fi
echo ""

echo "6. Dashboard文件验证"
echo "----------------------------------------"
dashboard_dir="/opt/claude/mystocks_spec/monitoring-stack/provisioning/dashboards"

if [ -f "$dashboard_dir/gpu-monitoring-dashboard.json" ]; then
    echo -e "${GREEN}✅ GPU监控Dashboard文件存在${NC}"
else
    echo -e "${RED}❌ GPU监控Dashboard文件不存在${NC}"
fi

if [ -f "$dashboard_dir/api-performance-dashboard.json" ]; then
    echo -e "${GREEN}✅ API性能Dashboard文件存在${NC}"
else
    echo -e "${RED}❌ API性能Dashboard文件不存在${NC}"
fi

if [ -f "$dashboard_dir/system-resource-dashboard.json" ]; then
    echo -e "${GREEN}✅ 系统资源Dashboard文件存在${NC}"
else
    echo -e "${RED}❌ 系统资源Dashboard文件不存在${NC}"
fi
echo ""

echo "=================================="
echo "验证完成"
echo "=================================="
echo ""
echo "访问地址:"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana:   http://localhost:3000 (admin/admin)"
echo "  - Loki:      http://localhost:3100"
echo "  - Tempo:     http://localhost:3200"
echo ""
echo "手动导入Dashboard (如需):"
echo "  1. 访问 http://localhost:3000"
echo "  2. 登录 (admin/admin)"
echo "  3. 进入 Dashboards -> Import"
echo "  4. 上传以下JSON文件:"
echo "     - $dashboard_dir/gpu-monitoring-dashboard.json"
echo "     - $dashboard_dir/api-performance-dashboard.json"
echo "     - $dashboard_dir/system-resource-dashboard.json"
echo ""
