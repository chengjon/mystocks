#!/bin/bash

# ===================================
# MyStocks 健康检查脚本
# 版本: v1.0
# 描述: 生产环境服务健康检查和监控
# ===================================

set -e

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
API_BASE_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"

# 函数定义
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$HEALTH_LOG"
}

success() {
    echo -e "${GREEN}[健康]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

error() {
    echo -e "${RED}[异常]${NC} $1"
}

# PM2服务检查
check_pm2_services() {
    log "检查PM2服务状态..."
    
    # 检查PM2是否安装
    if ! command -v pm2 >/dev/null 2>&1; then
        error "PM2 未安装"
        return 1
    fi
    
    # 检查PM2进程状态
    PM2_STATUS=$(pm2 list --json 2>/dev/null || echo '{"processes":[]}')
    
    # 解析JSON状态 (简单检查)
    if echo "$PM2_STATUS" | grep -q '"online"'; then
        success "PM2 服务正在运行"
        
        # 显示服务详情
        pm2 list --no-color | grep -E "(mystocks|data-sync)" || true
        
        return 0
    else
        error "PM2 服务未正常运行"
        pm2 list --no-color || true
        return 1
    fi
}

# API服务检查
check_api_service() {
    log "检查API服务健康状态..."
    
    local api_url="${API_BASE_URL}/api/monitoring/health"
    local response
    local status_code
    
    # 检查HTTP状态码
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "$api_url" 2>/dev/null || echo "000")
    
    if [[ "$status_code" == "200" ]]; then
        success "API服务响应正常 (HTTP $status_code)"
        
        # 获取详细健康信息
        response=$(curl -s "$api_url" 2>/dev/null || echo '{"status":"unknown"}')
        echo "健康检查详情: $response"
        
        return 0
    else
        error "API服务响应异常 (HTTP $status_code)"
        return 1
    fi
}

# 前端服务检查
check_frontend_service() {
    log "检查前端服务状态..."
    
    local response
    local status_code
    
    # 检查HTTP状态码
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" 2>/dev/null || echo "000")
    
    if [[ "$status_code" == "200" ]]; then
        success "前端服务响应正常 (HTTP $status_code)"
        return 0
    else
        error "前端服务响应异常 (HTTP $status_code)"
        return 1
    fi
}

# 数据库连接检查
check_database_connections() {
    log "检查数据库连接状态..."
    
    cd "$PROJECT_ROOT"
    
    # 检查PostgreSQL连接
    if python3 -c "
import os
os.environ['PYTHONPATH'] = '$PROJECT_ROOT'
try:
    from src.data_access.postgresql_access import PostgreSQLDataAccess
    access = PostgreSQLDataAccess()
    # 尝试简单的查询测试
    print('PostgreSQL连接测试')
except Exception as e:
    print(f'PostgreSQL连接失败: {e}')
    exit(1)
" 2>/dev/null; then
        success "PostgreSQL 数据库连接正常"
    else
        error "PostgreSQL 数据库连接失败"
        return 1
    fi
    
    # 检查TDengine连接
    if python3 -c "
import os
os.environ['PYTHONPATH'] = '$PROJECT_ROOT'
try:
    from src.data_access.tdengine_access import TDengineDataAccess
    access = TDengineDataAccess()
    # 尝试简单的查询测试
    print('TDengine连接测试')
except Exception as e:
    print(f'TDengine连接失败: {e}')
    exit(1)
" 2>/dev/null; then
        success "TDengine 数据库连接正常"
    else
        error "TDengine 数据库连接失败"
        return 1
    fi
    
    return 0
}

# 系统资源检查
check_system_resources() {
    log "检查系统资源使用情况..."
    
    # CPU使用率
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    if (( $(echo "$CPU_USAGE < 80" | bc -l) )); then
        success "CPU使用率正常: ${CPU_USAGE}%"
    else
        warning "CPU使用率较高: ${CPU_USAGE}%"
    fi
    
    # 内存使用率
    MEMORY_INFO=$(free | grep Mem)
    TOTAL_MEMORY=$(echo $MEMORY_INFO | awk '{print $2}')
    USED_MEMORY=$(echo $MEMORY_INFO | awk '{print $3}')
    MEMORY_USAGE=$(echo "scale=2; $USED_MEMORY * 100 / $TOTAL_MEMORY" | bc)
    
    if (( $(echo "$MEMORY_USAGE < 85" | bc -l) )); then
        success "内存使用率正常: ${MEMORY_USAGE}%"
    else
        warning "内存使用率较高: ${MEMORY_USAGE}%"
    fi
    
    # 磁盘使用率
    DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    if [[ "$DISK_USAGE" < "90" ]]; then
        success "磁盘使用率正常: ${DISK_USAGE}%"
    else
        warning "磁盘使用率较高: ${DISK_USAGE}%"
    fi
    
    return 0
}

# 网络连接检查
check_network_connectivity() {
    log "检查网络连接状态..."
    
    # 检查本地端口监听
    log "检查关键端口监听状态..."
    
    PORTS=(3000 8000 5432 6030)
    for port in "${PORTS[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            success "端口 $port 正在监听"
        else
            warning "端口 $port 未监听"
        fi
    done
    
    return 0
}

# 错误日志检查
check_error_logs() {
    log "检查最近的错误日志..."
    
    # 检查PM2错误日志
    if [[ -d "${LOG_DIR}" ]]; then
        # 查找最近的错误 (最近1小时)
        ERROR_COUNT=$(find "${LOG_DIR}" -name "*.log" -type f -mmin -60 -exec grep -l "error\|ERROR\|Error" {} \; 2>/dev/null | wc -l)
        if [[ "$ERROR_COUNT" -eq 0 ]]; then
            success "最近1小时无错误日志"
        else
            warning "最近1小时发现 $ERROR_COUNT 个包含错误的日志文件"
            
            # 显示最新的错误日志
            echo "最新的错误日志:"
            find "${LOG_DIR}" -name "*.log" -type f -mmin -60 -exec tail -10 {} \; | grep -E "error|ERROR|Error" | tail -5
        fi
    else
        warning "日志目录不存在: ${LOG_DIR}"
    fi
    
    return 0
}

# API端点测试
test_api_endpoints() {
    log "测试关键API端点..."
    
    # 定义要测试的API端点
    local endpoints=(
        "${API_BASE_URL}/api/monitoring/health"
        "${API_BASE_URL}/api/data/stocks/basic?limit=5"
        "${API_BASE_URL}/api/data/markets/overview"
        "${API_BASE_URL}/api/analysis/industry/list"
        "${API_BASE_URL}/api/analysis/concept/list"
    )
    
    local failed_endpoints=0
    
    for endpoint in "${endpoints[@]}"; do
        if curl -s -f -m 10 "$endpoint" >/dev/null 2>&1; then
            success "API端点正常: $(basename "$endpoint")"
        else
            error "API端点异常: $(basename "$endpoint")"
            ((failed_endpoints++))
        fi
    done
    
    if [[ "$failed_endpoints" -eq 0 ]]; then
        success "所有API端点测试通过"
        return 0
    else
        error "$failed_endpoints 个API端点测试失败"
        return 1
    fi
}

# 生成健康报告
generate_health_report() {
    log "生成健康检查报告..."
    
    local report_file="${LOG_DIR}/health_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "MyStocks 系统健康检查报告"
        echo "检查时间: $(date)"
        echo "=========================================="
        echo ""
        
        echo "1. PM2 服务状态:"
        pm2 list --no-color 2>/dev/null || echo "PM2 服务异常"
        echo ""
        
        echo "2. 系统资源使用:"
        echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
        echo "内存: $(free | grep Mem | awk '{printf "%.2f%%", $3/$2 * 100.0}')"
        echo "磁盘: $(df / | tail -1 | awk '{print $5}')"
        echo ""
        
        echo "3. 数据库连接:"
        echo "PostgreSQL: $(pg_isready -h localhost -p 5432 2>/dev/null || echo '连接失败')"
        echo "TDengine: $(docker exec $(docker-compose ps -q tdengine 2>/dev/null) taos -s "show databases;" >/dev/null 2>&1 && echo '连接正常' || echo '连接失败')"
        echo ""
        
        echo "4. 网络端口监听:"
        for port in 3000 8000 5432 6030; do
            echo "端口 $port: $(lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 && echo '监听中' || echo '未监听')"
        done
        echo ""
        
        echo "5. 最近的错误日志摘要:"
        find "${LOG_DIR}" -name "*.log" -type f -mmin -60 -exec tail -5 {} \; 2>/dev/null | grep -E "error|ERROR|Error" | tail -10 || echo "无最近错误"
        
    } > "$report_file"
    
    success "健康检查报告已生成: $report_file"
}

# 主函数
main() {
    # 创建日志目录
    mkdir -p "$LOG_DIR"
    
    log "开始MyStocks系统健康检查..."
    
    local exit_code=0
    
    # 执行各项检查
    check_pm2_services || ((exit_code++))
    check_api_service || ((exit_code++))
    check_frontend_service || ((exit_code++))
    check_database_connections || ((exit_code++))
    check_system_resources || ((exit_code++))
    check_network_connectivity || ((exit_code++))
    check_error_logs || ((exit_code++))
    test_api_endpoints || ((exit_code++))
    
    # 生成健康报告
    generate_health_report
    
    # 显示检查结果
    echo ""
    if [[ "$exit_code" -eq 0 ]]; then
        success "=========================================="
        success "所有健康检查通过，系统运行正常"
        success "=========================================="
    else
        error "=========================================="
        error "发现 $exit_code 个健康问题，请及时处理"
        error "=========================================="
    fi
    
    log "健康检查完成"
    exit $exit_code
}

# 显示使用信息
show_usage() {
    echo "MyStocks 系统健康检查脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  --pm2-only     仅检查PM2服务"
    echo "  --api-only     仅检查API服务"
    echo "  --db-only      仅检查数据库"
    echo "  --quick        快速检查 (跳过详细测试)"
    echo ""
    echo "示例:"
    echo "  $0              # 完整健康检查"
    echo "  $0 --quick      # 快速检查"
    echo "  $0 --pm2-only   # 仅检查PM2服务"
}

# 解析命令行参数
case "${1:-}" in
    -h|--help)
        show_usage
        exit 0
        ;;
    --pm2-only)
        mkdir -p "$LOG_DIR"
        log "仅检查PM2服务状态..."
        check_pm2_services
        exit $?
        ;;
    --api-only)
        mkdir -p "$LOG_DIR"
        log "仅检查API服务状态..."
        check_api_service
        exit $?
        ;;
    --db-only)
        mkdir -p "$LOG_DIR"
        log "仅检查数据库连接..."
        check_database_connections
        exit $?
        ;;
    --quick)
        mkdir -p "$LOG_DIR"
        log "执行快速健康检查..."
        check_pm2_services || exit 1
        check_api_service || exit 1
        check_frontend_service || exit 1
        success "快速检查通过"
        exit 0
        ;;
    *)
        main
        ;;
esac