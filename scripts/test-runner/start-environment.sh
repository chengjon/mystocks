#!/bin/bash
# MyStocks环境标准化启动脚本
# 确保测试环境的一致性和可重现性

set -e  # 遇到错误立即退出

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 配置参数
FRONTEND_PORT=3001
BACKEND_PORT=8000
MAX_WAIT_TIME=60
HEALTH_CHECK_INTERVAL=5

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 清理函数
cleanup() {
    log_info "执行清理操作..."

    # 停止PM2服务
    if command -v pm2 &> /dev/null; then
        log_info "停止PM2服务..."
        pm2 delete all 2>/dev/null || true
    fi

    # 杀死残留进程
    log_info "清理残留进程..."
    pkill -f "vite.*dev" 2>/dev/null || true
    pkill -f "uvicorn.*app.main" 2>/dev/null || true

    # 清理临时文件
    log_info "清理临时日志文件..."
    rm -f /tmp/pm2-*.log 2>/dev/null || true

    # 等待端口释放
    log_info "等待端口释放..."
    for port in $FRONTEND_PORT $BACKEND_PORT; do
        local count=0
        while lsof -i :$port >/dev/null 2>&1 && [ $count -lt 10 ]; do
            sleep 1
            count=$((count + 1))
        done
        if lsof -i :$port >/dev/null 2>&1; then
            log_warn "端口 $port 可能仍被占用"
        fi
    done

    log_success "清理完成"
}

# 环境验证函数
validate_environment() {
    log_info "验证运行环境..."

    # 检查Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装"
        exit 1
    fi

    local node_version=$(node -v | sed 's/v//')
    log_info "Node.js 版本: $node_version"

    # 检查npm
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装"
        exit 1
    fi

    local npm_version=$(npm -v)
    log_info "npm 版本: $npm_version"

    # 检查Python
    if ! command -v python &> /dev/null; then
        log_error "Python 未安装"
        exit 1
    fi

    local python_version=$(python --version 2>&1 | awk '{print $2}')
    log_info "Python 版本: $python_version"

    # 检查PM2
    if ! command -v pm2 &> /dev/null; then
        log_error "PM2 未安装，请运行: npm install -g pm2"
        exit 1
    fi

    local pm2_version=$(pm2 -v)
    log_info "PM2 版本: $pm2_version"

    # 检查端口是否被占用
    for port in $FRONTEND_PORT $BACKEND_PORT; do
        if lsof -i :$port >/dev/null 2>&1; then
            log_error "端口 $port 已被占用"
            lsof -i :$port
            exit 1
        fi
    done

    log_success "环境验证通过"
}

# 启动服务函数
start_services() {
    log_info "启动MyStocks服务..."

    cd "$PROJECT_ROOT"

    # 检查ecosystem.config.js是否存在
    if [ ! -f "ecosystem.config.js" ]; then
        log_error "ecosystem.config.js 文件不存在"
        exit 1
    fi

    # 使用PM2启动服务
    log_info "使用PM2启动服务..."
    if pm2 start ecosystem.config.js; then
        log_success "PM2服务启动命令执行成功"
    else
        log_error "PM2服务启动失败"
        exit 1
    fi

    # 等待服务启动
    log_info "等待服务启动..."
    sleep 5
}

# 健康检查函数
wait_for_services() {
    log_info "执行服务健康检查..."

    local start_time=$(date +%s)

    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))

        if [ $elapsed -gt $MAX_WAIT_TIME ]; then
            log_error "服务启动超时 ($MAX_WAIT_TIME 秒)"
            pm2 list
            pm2 logs --lines 20
            exit 1
        fi

        log_info "检查服务状态 (已等待 ${elapsed}s)..."

        # 检查前端服务
        local frontend_ok=false
        if curl -s --max-time 5 "http://localhost:$FRONTEND_PORT" >/dev/null 2>&1; then
            frontend_ok=true
            log_success "前端服务已就绪"
        fi

        # 检查后端服务
        local backend_ok=false
        if curl -s --max-time 5 "http://localhost:$BACKEND_PORT/api/health" >/dev/null 2>&1; then
            backend_ok=true
            log_success "后端服务已就绪"
        fi

        # 如果所有服务都就绪，退出循环
        if [ "$frontend_ok" = true ] && [ "$backend_ok" = true ]; then
            break
        fi

        # 显示当前状态
        pm2 jlist | jq -r '.[] | "\(.name): \(.pm2_env.status)"' 2>/dev/null || pm2 list

        log_info "等待 ${HEALTH_CHECK_INTERVAL} 秒后重新检查..."
        sleep $HEALTH_CHECK_INTERVAL
    done

    log_success "所有服务启动完成！"
}

# 生成状态报告函数
generate_report() {
    log_info "生成启动状态报告..."

    echo ""
    echo "=========================================="
    echo "🏥 MyStocks 服务启动状态报告"
    echo "=========================================="

    # PM2服务状态
    echo ""
    echo "📊 PM2 服务状态:"
    pm2 jlist | jq -r '.[] | "  • \(.name): \(.pm2_env.status) (PID: \(.pid))"' 2>/dev/null || echo "  PM2状态获取失败"

    # 端口状态
    echo ""
    echo "🔌 端口占用状态:"
    for port in $FRONTEND_PORT $BACKEND_PORT; do
        if lsof -i :$port >/dev/null 2>&1; then
            local process=$(lsof -i :$port | tail -1 | awk '{print $1}')
            echo "  ✅ 端口 $port: 正常占用 ($process)"
        else
            echo "  ❌ 端口 $port: 未占用"
        fi
    done

    # 服务健康状态
    echo ""
    echo "💚 服务健康状态:"
    if curl -s --max-time 3 "http://localhost:$FRONTEND_PORT" >/dev/null 2>&1; then
        echo "  ✅ 前端服务: http://localhost:$FRONTEND_PORT"
    else
        echo "  ❌ 前端服务: 无响应"
    fi

    if curl -s --max-time 3 "http://localhost:$BACKEND_PORT/api/health" >/dev/null 2>&1; then
        echo "  ✅ 后端服务: http://localhost:$BACKEND_PORT"
    else
        echo "  ❌ 后端服务: 无响应"
    fi

    # 环境信息
    echo ""
    echo "🖥️  环境信息:"
    echo "  • Node.js: $(node -v 2>/dev/null || echo 'N/A')"
    echo "  • npm: $(npm -v 2>/dev/null || echo 'N/A')"
    echo "  • Python: $(python --version 2>&1 | awk '{print $2}' || echo 'N/A')"
    echo "  • PM2: $(pm2 -v 2>/dev/null || echo 'N/A')"

    echo ""
    echo "🎯 下一步操作建议:"
    echo "  1. 运行健康检查: ./scripts/test-runner/health-check.sh"
    echo "  2. 执行ESM验证: ./scripts/test-runner/esm-validation.sh"
    echo "  3. 开始测试: npm run test (或相应测试命令)"
    echo ""
    echo "📋 查看日志:"
    echo "  • PM2日志: pm2 logs"
    echo "  • 前端日志: tail -f /tmp/pm2-mystocks-frontend.log"
    echo "  • 后端日志: tail -f /tmp/pm2-mystocks-backend.log"
    echo ""
    echo "=========================================="
}

# 主函数
main() {
    echo "🚀 MyStocks 环境标准化启动脚本"
    echo "======================================"

    # 参数处理
    case "${1:-}" in
        "cleanup")
            cleanup
            exit 0
            ;;
        "status")
            generate_report
            exit 0
            ;;
        "help"|"-h"|"--help")
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  cleanup    仅执行清理操作"
            echo "  status     显示当前服务状态"
            echo "  help       显示此帮助信息"
            echo ""
            echo "无参数时执行完整的启动流程"
            exit 0
            ;;
    esac

    # 执行启动流程
    cleanup
    validate_environment
    start_services
    wait_for_services
    generate_report

    log_success "🎉 MyStocks 环境启动完成！"
    log_info "可以开始测试工作了。"
}

# 错误处理
trap 'log_error "脚本执行失败，退出码: $?"' ERR

# 执行主函数
main "$@"