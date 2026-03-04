#!/bin/bash
# MyStocks服务健康检查脚本
# 检查前端和后端服务的健康状态

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 配置参数
FRONTEND_URL="http://localhost:"
BACKEND_URL="http://localhost:/api/health"
TIMEOUT=10
RETRIES=3
RETRY_DELAY=2

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 健康检查函数
check_health() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}

    log_info "检查 $service_name 健康状态..."

    for attempt in $(seq 1 $RETRIES); do
        log_info "尝试 $attempt/$RETRIES: $url"

        # 使用curl进行健康检查
        local response
        local http_code

        response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
                      --max-time $TIMEOUT \
                      "$url" 2>/dev/null)

        http_code=$(echo "$response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')

        if [ "$http_code" = "$expected_status" ]; then
            log_info "$service_name 健康检查通过 (HTTP $http_code)"

            # 额外验证响应内容
            local response_body=$(echo "$response" | sed -e 's/HTTPSTATUS.*//')
            if echo "$response_body" | grep -q "DOCTYPE\|health\|status"; then
                log_info "$service_name 响应内容正常"
                return 0
            else
                log_warn "$service_name 响应内容异常"
            fi
        else
            log_warn "$service_name 健康检查失败 (HTTP $http_code)"
        fi

        # 如果不是最后一次尝试，等待后重试
        if [ $attempt -lt $RETRIES ]; then
            log_info "等待 ${RETRY_DELAY} 秒后重试..."
            sleep $RETRY_DELAY
        fi
    done

    log_error "$service_name 健康检查失败，已达到最大重试次数"
    return 1
}

# 进程状态检查函数
check_process() {
    local service_name=$1
    local process_pattern=$2

    log_info "检查 $service_name 进程状态..."

    if pgrep -f "$process_pattern" > /dev/null 2>&1; then
        log_info "$service_name 进程运行正常"
        return 0
    else
        log_error "$service_name 进程未运行"
        return 1
    fi
}

# 端口占用检查函数
check_port() {
    local port=$1
    local service_name=$2

    log_info "检查 $service_name 端口 $port 占用状态..."

    if lsof -i :$port > /dev/null 2>&1; then
        log_info "端口 $port ($service_name) 正常占用"
        return 0
    else
        log_error "端口 $port ($service_name) 未被占用"
        return 1
    fi
}

# 主检查流程
main() {
    local all_checks_passed=true

    echo "=========================================="
    log_info "开始 MyStocks 服务健康检查"
    echo "=========================================="

    # 1. 检查进程状态
    echo ""
    log_info "=== 进程状态检查 ==="

    if ! check_process "前端服务" "vite.*dev"; then
        all_checks_passed=false
    fi

    if ! check_process "后端服务" "uvicorn.*app.main"; then
        all_checks_passed=false
    fi

    # 2. 检查端口占用
    echo ""
    log_info "=== 端口占用检查 ==="

    if ! check_port 3001 "前端服务"; then
        all_checks_passed=false
    fi

    if ! check_port 8000 "后端服务"; then
        all_checks_passed=false
    fi

    # 3. 检查服务健康状态
    echo ""
    log_info "=== 服务健康检查 ==="

    if ! check_health "前端服务" "$FRONTEND_URL"; then
        all_checks_passed=false
    fi

    if ! check_health "后端服务" "$BACKEND_URL"; then
        all_checks_passed=false
    fi

    # 4. 生成检查报告
    echo ""
    echo "=========================================="

    if [ "$all_checks_passed" = true ]; then
        log_info "✅ 所有健康检查通过！"
        log_info "MyStocks服务运行正常，可以开始测试。"
        echo ""
        echo "📊 服务状态摘要:"
        echo "  • 前端服务: http://localhost: ✅"
        echo "  • 后端服务: http://localhost: ✅"
        echo "  • 健康检查: 通过 ✅"
        return 0
    else
        log_error "❌ 部分健康检查失败！"
        log_error "请检查服务状态并修复问题后再运行测试。"
        echo ""
        echo "🔧 故障排除建议:"
        echo "  1. 检查服务进程: pm2 list"
        echo "  2. 查看服务日志: pm2 logs"
        echo "  3. 重启服务: pm2 restart all"
        echo "  4. 检查端口占用: lsof -i :3001, lsof -i :8000"
        return 1
    fi
}

# 执行主函数
main "$@"