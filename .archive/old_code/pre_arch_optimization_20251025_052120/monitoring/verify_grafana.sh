#!/bin/bash
#
# Grafana部署验证脚本
#
# 用法: ./verify_grafana.sh [NAS_IP]
#

GRAFANA_HOST="${1:-192.168.123.104}"
GRAFANA_PORT="3000"
ADMIN_USER="admin"
ADMIN_PASSWORD="mystocks2025"

echo "=========================================="
echo "Grafana部署验证"
echo "=========================================="
echo ""
echo "目标: http://${GRAFANA_HOST}:${GRAFANA_PORT}"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 测试1: 网络连通性
echo "测试1: 网络连通性..."
if ping -c 1 -W 2 ${GRAFANA_HOST} > /dev/null 2>&1; then
    echo -e "${GREEN}✓ NAS可访问${NC}"
else
    echo -e "${RED}✗ NAS不可访问 (${GRAFANA_HOST})${NC}"
    exit 1
fi
echo ""

# 测试2: 端口开放检查
echo "测试2: 端口开放检查..."
if nc -z -w 5 ${GRAFANA_HOST} ${GRAFANA_PORT} 2>/dev/null; then
    echo -e "${GREEN}✓ 端口${GRAFANA_PORT}已开放${NC}"
else
    echo -e "${RED}✗ 端口${GRAFANA_PORT}未开放或被防火墙阻止${NC}"
    echo "请检查:"
    echo "  1. Docker容器是否运行: docker ps | grep grafana"
    echo "  2. 端口映射是否正确: docker port mystocks-grafana"
    echo "  3. NAS防火墙设置"
    exit 1
fi
echo ""

# 测试3: HTTP健康检查
echo "测试3: HTTP健康检查..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://${GRAFANA_HOST}:${GRAFANA_PORT}/ 2>/dev/null)
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    echo -e "${GREEN}✓ Grafana HTTP响应正常 (HTTP ${HTTP_CODE})${NC}"
else
    echo -e "${RED}✗ Grafana HTTP响应异常 (HTTP ${HTTP_CODE})${NC}"
    echo "容器可能还在启动中，请稍等30秒后重试"
    exit 1
fi
echo ""

# 测试4: API健康状态
echo "测试4: API健康状态..."
HEALTH=$(curl -s http://${GRAFANA_HOST}:${GRAFANA_PORT}/api/health 2>/dev/null)
if echo "$HEALTH" | grep -q "ok"; then
    echo -e "${GREEN}✓ Grafana API健康 (database: ok)${NC}"
    echo "  详情: $HEALTH"
else
    echo -e "${YELLOW}⚠ 健康检查响应异常${NC}"
    echo "  响应: $HEALTH"
fi
echo ""

# 测试5: 登录测试
echo "测试5: 管理员登录测试..."
LOGIN_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "{\"user\":\"${ADMIN_USER}\",\"password\":\"${ADMIN_PASSWORD}\"}" \
  http://${GRAFANA_HOST}:${GRAFANA_PORT}/login 2>/dev/null)

if echo "$LOGIN_RESPONSE" | grep -q "Logged in"; then
    echo -e "${GREEN}✓ 管理员登录成功${NC}"
elif echo "$LOGIN_RESPONSE" | grep -q "Invalid"; then
    echo -e "${RED}✗ 登录失败: 用户名或密码错误${NC}"
    echo "  请检查: ${ADMIN_USER} / ${ADMIN_PASSWORD}"
else
    echo -e "${YELLOW}⚠ 登录测试未知响应${NC}"
    echo "  响应: $LOGIN_RESPONSE"
fi
echo ""

# 测试6: 数据源检查 (需要认证)
echo "测试6: 数据源配置检查..."
DATASOURCES=$(curl -s -u ${ADMIN_USER}:${ADMIN_PASSWORD} \
  http://${GRAFANA_HOST}:${GRAFANA_PORT}/api/datasources 2>/dev/null)

if echo "$DATASOURCES" | grep -q "MyStocks-Monitoring"; then
    echo -e "${GREEN}✓ 数据源'MyStocks-Monitoring'已配置${NC}"

    # 提取数据源详情
    DS_COUNT=$(echo "$DATASOURCES" | grep -o "\"name\"" | wc -l)
    echo "  已配置数据源数量: ${DS_COUNT}"
else
    echo -e "${YELLOW}⚠ 数据源未配置或名称不匹配${NC}"
    echo "  需要手动导入数据源配置"
    echo "  响应: $DATASOURCES"
fi
echo ""

# 测试7: Dashboard检查
echo "测试7: Dashboard配置检查..."
DASHBOARDS=$(curl -s -u ${ADMIN_USER}:${ADMIN_PASSWORD} \
  http://${GRAFANA_HOST}:${GRAFANA_PORT}/api/search?type=dash-db 2>/dev/null)

if echo "$DASHBOARDS" | grep -q "MyStocks"; then
    echo -e "${GREEN}✓ 监控面板已导入${NC}"

    # 提取dashboard数量
    DB_COUNT=$(echo "$DASHBOARDS" | grep -o "\"uid\"" | wc -l)
    echo "  已导入面板数量: ${DB_COUNT}"
else
    echo -e "${YELLOW}⚠ 监控面板未导入${NC}"
    echo "  需要手动导入Dashboard JSON配置"
fi
echo ""

# 总结
echo "=========================================="
echo "验证总结"
echo "=========================================="
echo ""
echo "访问信息:"
echo "  URL: http://${GRAFANA_HOST}:${GRAFANA_PORT}"
echo "  用户名: ${ADMIN_USER}"
echo "  密码: ${ADMIN_PASSWORD}"
echo ""
echo "下一步:"
echo "  1. 在浏览器打开上述URL"
echo "  2. 使用上述账号登录"
echo "  3. 检查数据源连接: Configuration → Data Sources"
echo "  4. 查看监控面板: Dashboards → Browse"
echo "  5. 生成监控数据: python test_monitoring_with_redis.py"
echo ""

# 提供快速访问命令
echo "快速访问命令:"
echo "  浏览器: xdg-open http://${GRAFANA_HOST}:${GRAFANA_PORT}"
echo "  或复制此链接: http://${GRAFANA_HOST}:${GRAFANA_PORT}"
echo ""
