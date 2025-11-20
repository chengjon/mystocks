#!/bin/bash

# ===================================
# MyStocks 健康检查脚本 v2.2 - 简化版
# 版本: v2.2
# 描述: 生产环境服务健康检查和监控（简化版）
# ===================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_ROOT="/opt/claude/mystocks_spec"
LOG_DIR="/opt/mystocks/logs"
HEALTH_LOG="${LOG_DIR}/health_check.log"
API_BASE_URL="http://localhost:8888"
FRONTEND_URL="http://localhost:3000"
PG_HOST="localhost"
PG_PORT="5438"

# 确保日志目录存在
mkdir -p "$LOG_DIR"

# 函数定义
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$HEALTH_LOG"
}

success() {
    echo -e "${GREEN}[健康]${NC} $1" | tee -a "$HEALTH_LOG"
}

warning() {
    echo -e "${YELLOW}[警告]${NC} $1" | tee -a "$HEALTH_LOG"
}

error() {
    echo -e "${RED}[异常]${NC} $1" | tee -a "$HEALTH_LOG"
}

# 检查基础服务
check_basic_services() {
    log "检查基础服务..."
    
    # 检查前端服务
    if curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" 2>/dev/null | grep -q "200"; then
        success "前端服务正常"
    else
        warning "前端服务异常"
    fi
    
    # 检查PostgreSQL
    if pg_isready -h "$PG_HOST" -p "$PG_PORT" >/dev/null 2>&1; then
        success "PostgreSQL连接正常"
    else
        error "PostgreSQL连接失败"
    fi
    
    # 检查TDengine端口
    if nc -z localhost 6030 >/dev/null 2>&1; then
        success "TDengine端口可访问"
    else
        warning "TDengine端口不可访问"
    fi
    
    # 检查API服务
    for api_endpoint in "/api/health" "/api/docs"; do
        if curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL$api_endpoint" 2>/dev/null | grep -q "200"; then
            success "API端点正常: $api_endpoint"
        else
            warning "API端点异常: $api_endpoint"
        fi
    done
}

# 生成报告
generate_report() {
    log "生成简化报告..."
    
    local report_file="${LOG_DIR}/health_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "MyStocks 简化健康检查报告"
        echo "检查时间: $(date)"
        echo "=========================================="
        echo ""
        
        echo "前端服务: $(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" 2>/dev/null || echo '不可用')"
        echo "PostgreSQL: $(pg_isready -h localhost -p $PG_PORT 2>/dev/null && echo '正常' || echo '异常')"
        echo "TDengine: $(nc -z localhost 6030 2>/dev/null && echo '可访问' || echo '不可访问')"
        echo "API文档: $(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/api/docs" 2>/dev/null || echo '不可用')"
        echo "API健康: $(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/api/health" 2>/dev/null || echo '不可用')"
        
    } > "$report_file"
    
    success "报告已生成: $report_file"
}

# 主函数
main() {
    log "开始MyStocks简化健康检查..."
    
    check_basic_services
    generate_report
    
    log "检查完成"
}

# 执行主函数
main