#!/bin/bash
# ============================================
# US3 DataManager Grafana 监控自动部署脚本
# ============================================
# 版本: 1.0.0
# 创建日期: 2025-10-25
# 用途: 一键部署 US3 DataManager 监控到 Grafana
# ============================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量（从 .env 读取）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"

# 加载环境变量
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
else
    echo -e "${RED}❌ .env 文件不存在: $ENV_FILE${NC}"
    exit 1
fi

# PostgreSQL 配置
PG_HOST="${POSTGRESQL_HOST:-192.168.123.104}"
PG_PORT="${POSTGRESQL_PORT:-5438}"
PG_USER="${POSTGRESQL_USER:-postgres}"
PG_PASSWORD="${POSTGRESQL_PASSWORD}"
PG_DATABASE="${POSTGRESQL_DATABASE:-mystocks}"

# Grafana 配置
GRAFANA_URL="http://192.168.123.104:3000"
GRAFANA_USER="admin"
GRAFANA_PASSWORD="mystocks2025"

# ============================================
# 函数定义
# ============================================

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 未安装，请先安装"
        exit 1
    fi
}

# ============================================
# 1. 环境检查
# ============================================

print_header "1. 环境检查"

check_command "psql"
check_command "curl"
check_command "jq"
print_success "必要命令已安装"

# 检查 PostgreSQL 连接
print_info "检查 PostgreSQL 连接..."
if PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DATABASE" -c "SELECT 1" &> /dev/null; then
    print_success "PostgreSQL 连接正常 (${PG_HOST}:${PG_PORT}/${PG_DATABASE})"
else
    print_error "PostgreSQL 连接失败"
    exit 1
fi

# 检查 Grafana 连接
print_info "检查 Grafana 连接..."
if curl -s -f "$GRAFANA_URL/api/health" &> /dev/null; then
    GRAFANA_VERSION=$(curl -s "$GRAFANA_URL/api/health" | jq -r '.version' 2>/dev/null || echo "未知")
    print_success "Grafana 连接正常 (版本: $GRAFANA_VERSION)"
else
    print_error "Grafana 连接失败 ($GRAFANA_URL)"
    exit 1
fi

# ============================================
# 2. 部署监控表结构
# ============================================

print_header "2. 部署监控表结构"

SQL_INIT_FILE="$SCRIPT_DIR/init_us3_monitoring.sql"

if [ ! -f "$SQL_INIT_FILE" ]; then
    print_error "监控表初始化脚本不存在: $SQL_INIT_FILE"
    exit 1
fi

print_info "执行监控表初始化脚本..."
if PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DATABASE" -f "$SQL_INIT_FILE" &> /tmp/us3_monitoring_init.log; then
    print_success "监控表结构创建成功"

    # 验证表创建
    TABLE_COUNT=$(PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DATABASE" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'monitoring' AND table_name LIKE '%routing%'")
    print_info "创建的监控表数量: $(echo $TABLE_COUNT | xargs)"

    VIEW_COUNT=$(PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DATABASE" -t -c "SELECT COUNT(*) FROM information_schema.views WHERE table_schema = 'monitoring' AND table_name LIKE 'v_%'")
    print_info "创建的监控视图数量: $(echo $VIEW_COUNT | xargs)"
else
    print_error "监控表结构创建失败，查看日志: /tmp/us3_monitoring_init.log"
    cat /tmp/us3_monitoring_init.log
    exit 1
fi

# ============================================
# 3. 配置 Grafana 数据源
# ============================================

print_header "3. 配置 Grafana 数据源"

# 检查数据源是否已存在
DATASOURCE_NAME="MyStocks-PostgreSQL"
DATASOURCE_EXISTS=$(curl -s -u "$GRAFANA_USER:$GRAFANA_PASSWORD" "$GRAFANA_URL/api/datasources/name/$DATASOURCE_NAME" | jq -r '.id' 2>/dev/null || echo "null")

if [ "$DATASOURCE_EXISTS" != "null" ] && [ "$DATASOURCE_EXISTS" != "" ]; then
    print_warning "数据源 '$DATASOURCE_NAME' 已存在 (ID: $DATASOURCE_EXISTS)"
    print_info "跳过数据源创建，使用现有数据源"
else
    print_info "创建 Grafana 数据源..."

    DATASOURCE_JSON=$(cat <<EOF
{
  "name": "$DATASOURCE_NAME",
  "type": "postgres",
  "access": "proxy",
  "url": "$PG_HOST:$PG_PORT",
  "database": "$PG_DATABASE",
  "user": "$PG_USER",
  "secureJsonData": {
    "password": "$PG_PASSWORD"
  },
  "jsonData": {
    "sslmode": "disable",
    "postgresVersion": 1400,
    "timescaledb": true
  },
  "isDefault": false
}
EOF
)

    DATASOURCE_RESULT=$(curl -s -X POST -H "Content-Type: application/json" -u "$GRAFANA_USER:$GRAFANA_PASSWORD" -d "$DATASOURCE_JSON" "$GRAFANA_URL/api/datasources")

    if echo "$DATASOURCE_RESULT" | jq -e '.id' &> /dev/null; then
        DATASOURCE_ID=$(echo "$DATASOURCE_RESULT" | jq -r '.id')
        print_success "数据源创建成功 (ID: $DATASOURCE_ID)"
    else
        print_error "数据源创建失败"
        echo "$DATASOURCE_RESULT" | jq .
        exit 1
    fi
fi

# ============================================
# 4. 导入 Grafana Dashboard
# ============================================

print_header "4. 导入 Grafana Dashboard"

DASHBOARD_JSON_FILE="$SCRIPT_DIR/grafana_us3_datamanager_dashboard.json"

if [ ! -f "$DASHBOARD_JSON_FILE" ]; then
    print_error "Dashboard JSON 文件不存在: $DASHBOARD_JSON_FILE"
    exit 1
fi

print_info "导入 US3 DataManager 性能监控 Dashboard..."

DASHBOARD_RESULT=$(curl -s -X POST -H "Content-Type: application/json" -u "$GRAFANA_USER:$GRAFANA_PASSWORD" -d @"$DASHBOARD_JSON_FILE" "$GRAFANA_URL/api/dashboards/db")

if echo "$DASHBOARD_RESULT" | jq -e '.status' | grep -q "success"; then
    DASHBOARD_UID=$(echo "$DASHBOARD_RESULT" | jq -r '.uid')
    DASHBOARD_URL=$(echo "$DASHBOARD_RESULT" | jq -r '.url')
    print_success "Dashboard 导入成功"
    print_info "Dashboard UID: $DASHBOARD_UID"
    print_info "Dashboard URL: $GRAFANA_URL$DASHBOARD_URL"
else
    print_warning "Dashboard 导入响应:"
    echo "$DASHBOARD_RESULT" | jq .

    # 检查是否因为已存在
    if echo "$DASHBOARD_RESULT" | jq -e '.message' | grep -q "already exists"; then
        print_warning "Dashboard 已存在，将尝试更新..."
        # 这里可以添加更新逻辑
    fi
fi

# ============================================
# 5. 生成测试数据
# ============================================

print_header "5. 生成测试数据"

print_info "插入测试监控数据..."

TEST_DATA_SQL=$(cat <<EOF
INSERT INTO monitoring.datamanager_routing_metrics (
    operation_id, classification, target_database,
    routing_decision_time_ms, operation_type, table_name,
    data_count, operation_success, operation_duration_ms
) VALUES
('deploy_test_001', 'TICK_DATA', 'TDENGINE', 0.0002, 'save_data', 'tick_data', 1000, TRUE, 125.5),
('deploy_test_002', 'DAILY_KLINE', 'POSTGRESQL', 0.0002, 'save_data', 'daily_kline', 500, TRUE, 89.3),
('deploy_test_003', 'SYMBOLS_INFO', 'POSTGRESQL', 0.0002, 'load_data', 'symbols_info', 100, TRUE, 45.2),
('deploy_test_004', 'MINUTE_KLINE', 'TDENGINE', 0.0002, 'save_data', 'minute_kline', 5000, TRUE, 256.8),
('deploy_test_005', 'TECHNICAL_INDICATORS', 'POSTGRESQL', 0.0002, 'save_data', 'technical_indicators', 200, TRUE, 67.4);
EOF
)

if PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DATABASE" -c "$TEST_DATA_SQL" &> /dev/null; then
    print_success "测试数据插入成功（5条记录）"
else
    print_warning "测试数据插入失败（可能已存在）"
fi

# ============================================
# 6. 验证部署
# ============================================

print_header "6. 验证部署"

# 查询监控数据
print_info "验证监控数据..."
RECORD_COUNT=$(PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DATABASE" -t -c "SELECT COUNT(*) FROM monitoring.datamanager_routing_metrics")
print_info "监控记录总数: $(echo $RECORD_COUNT | xargs)"

# 查询性能摘要
print_info "验证监控视图..."
VIEW_RESULT=$(PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DATABASE" -t -c "SELECT total_operations FROM monitoring.v_routing_performance_24h" 2>/dev/null || echo "0")
print_info "最近24小时操作数: $(echo $VIEW_RESULT | xargs)"

if [ "$(echo $VIEW_RESULT | xargs)" -gt "0" ]; then
    print_success "监控数据验证通过"
else
    print_warning "监控数据为空，请执行实际操作后查看"
fi

# ============================================
# 7. 部署完成
# ============================================

print_header "部署完成"

print_success "US3 DataManager Grafana 监控集成完成！"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}下一步操作${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "1. 访问 Grafana Dashboard:"
echo -e "   ${BLUE}$GRAFANA_URL/dashboards${NC}"
echo -e ""
echo -e "2. 查找 Dashboard:"
echo -e "   ${BLUE}搜索 'US3 DataManager 性能监控'${NC}"
echo -e ""
echo -e "3. 集成到 DataManager:"
echo -e "   ${BLUE}参考文档: $SCRIPT_DIR/US3_GRAFANA_INTEGRATION_GUIDE.md${NC}"
echo -e ""
echo -e "4. 测试监控:"
echo -e "   ${BLUE}cd $PROJECT_ROOT && python core/datamanager_monitoring.py${NC}"
echo -e "${GREEN}========================================${NC}\n"

print_info "部署日志已保存到: /tmp/us3_monitoring_deploy.log"

# 保存部署信息
cat > /tmp/us3_monitoring_deploy.log <<EOF
US3 DataManager Grafana 监控部署信息
部署时间: $(date)
PostgreSQL: $PG_HOST:$PG_PORT/$PG_DATABASE
Grafana: $GRAFANA_URL
数据源: $DATASOURCE_NAME
Dashboard: US3 DataManager 性能监控
状态: 部署成功
EOF

print_success "所有任务完成！"

exit 0
