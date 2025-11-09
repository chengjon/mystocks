#!/bin/bash
#
# Grafana自动部署脚本 - 部署到NAS
#
# 用法: ./deploy_grafana_to_nas.sh
#
# 作者: MyStocks Development Team
# 日期: 2025-10-12

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置变量
NAS_IP="192.168.123.104"
NAS_USER="admin"
NAS_BASE_DIR="/volume1/docker/mystocks-grafana"
GRAFANA_PORT="3000"
ADMIN_USER="admin"
ADMIN_PASSWORD="mystocks2025"

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Grafana自动部署脚本${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# 步骤1: 检查配置文件
echo -e "${YELLOW}[1/6] 检查配置文件...${NC}"
if [ ! -f "grafana-datasource.yml" ]; then
    echo -e "${RED}错误: grafana-datasource.yml 不存在${NC}"
    exit 1
fi
if [ ! -f "grafana-dashboard-provider.yml" ]; then
    echo -e "${RED}错误: grafana-dashboard-provider.yml 不存在${NC}"
    exit 1
fi
if [ ! -f "grafana_dashboard.json" ]; then
    echo -e "${RED}错误: grafana_dashboard.json 不存在${NC}"
    exit 1
fi
if [ ! -f "docker-compose-grafana.yml" ]; then
    echo -e "${RED}错误: docker-compose-grafana.yml 不存在${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 所有配置文件已就绪${NC}"
echo ""

# 步骤2: 测试NAS连接
echo -e "${YELLOW}[2/6] 测试NAS连接...${NC}"
if ! ping -c 1 -W 2 ${NAS_IP} > /dev/null 2>&1; then
    echo -e "${RED}错误: 无法连接到NAS (${NAS_IP})${NC}"
    echo "请检查:"
    echo "  1. NAS是否开机"
    echo "  2. IP地址是否正确"
    echo "  3. 网络连接是否正常"
    exit 1
fi
echo -e "${GREEN}✓ NAS连接正常${NC}"
echo ""

# 步骤3: 在NAS上创建目录
echo -e "${YELLOW}[3/6] 在NAS上创建目录...${NC}"
echo "请输入NAS的${NAS_USER}用户密码:"
ssh ${NAS_USER}@${NAS_IP} "
    mkdir -p ${NAS_BASE_DIR}/{data,config/provisioning/{datasources,dashboards}}
    chmod 755 ${NAS_BASE_DIR}
    chmod 777 ${NAS_BASE_DIR}/data
" || {
    echo -e "${RED}错误: 无法在NAS上创建目录${NC}"
    echo "请检查SSH访问权限"
    exit 1
}
echo -e "${GREEN}✓ 目录创建完成${NC}"
echo ""

# 步骤4: 上传配置文件
echo -e "${YELLOW}[4/6] 上传配置文件到NAS...${NC}"
scp grafana-datasource.yml ${NAS_USER}@${NAS_IP}:${NAS_BASE_DIR}/config/provisioning/datasources/ || exit 1
echo "  ✓ grafana-datasource.yml"

scp grafana-dashboard-provider.yml ${NAS_USER}@${NAS_IP}:${NAS_BASE_DIR}/config/provisioning/dashboards/ || exit 1
echo "  ✓ grafana-dashboard-provider.yml"

scp grafana_dashboard.json ${NAS_USER}@${NAS_IP}:${NAS_BASE_DIR}/config/provisioning/dashboards/ || exit 1
echo "  ✓ grafana_dashboard.json"

scp docker-compose-grafana.yml ${NAS_USER}@${NAS_IP}:${NAS_BASE_DIR}/docker-compose.yml || exit 1
echo "  ✓ docker-compose.yml"

echo -e "${GREEN}✓ 配置文件上传完成${NC}"
echo ""

# 步骤5: 启动Grafana容器
echo -e "${YELLOW}[5/6] 启动Grafana容器...${NC}"
ssh ${NAS_USER}@${NAS_IP} "
    cd ${NAS_BASE_DIR}

    # 检查是否已存在容器
    if docker ps -a | grep -q mystocks-grafana; then
        echo '  停止并删除已存在的容器...'
        docker stop mystocks-grafana 2>/dev/null || true
        docker rm mystocks-grafana 2>/dev/null || true
    fi

    # 启动容器
    echo '  拉取Grafana镜像...'
    docker pull grafana/grafana:latest

    echo '  启动容器...'
    docker-compose up -d

    # 等待容器启动
    echo '  等待容器启动...'
    sleep 10

    # 检查容器状态
    if docker ps | grep -q mystocks-grafana; then
        echo '  ✓ 容器启动成功'
    else
        echo '  ✗ 容器启动失败'
        docker logs mystocks-grafana
        exit 1
    fi
" || {
    echo -e "${RED}错误: 容器启动失败${NC}"
    exit 1
}
echo -e "${GREEN}✓ Grafana容器启动成功${NC}"
echo ""

# 步骤6: 验证部署
echo -e "${YELLOW}[6/6] 验证部署...${NC}"
sleep 5  # 等待Grafana完全启动

# 检查健康状态
if curl -s -o /dev/null -w "%{http_code}" http://${NAS_IP}:${GRAFANA_PORT}/api/health | grep -q "200"; then
    echo -e "${GREEN}✓ Grafana健康检查通过${NC}"
else
    echo -e "${YELLOW}⚠ Grafana可能还在启动中...${NC}"
fi
echo ""

# 完成
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "访问信息:"
echo "  URL: http://${NAS_IP}:${GRAFANA_PORT}"
echo "  用户名: ${ADMIN_USER}"
echo "  密码: ${ADMIN_PASSWORD}"
echo ""
echo "下一步:"
echo "  1. 在浏览器打开 http://${NAS_IP}:${GRAFANA_PORT}"
echo "  2. 使用 admin / mystocks2025 登录"
echo "  3. 验证数据源连接: Configuration → Data Sources"
echo "  4. 查看监控面板: Dashboards → MyStocks"
echo "  5. 修改管理员密码 (强烈建议)"
echo ""
echo "生成监控数据:"
echo "  cd /mnt/wd_mycode/mystocks_spec"
echo "  python test_monitoring_with_redis.py"
echo ""
echo -e "${GREEN}🎉 部署成功!${NC}"
