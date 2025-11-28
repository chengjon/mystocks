#!/bin/bash

# MyStocks 自动化测试一键执行脚本
# 整合 PM2 + tmux + lnav 的完整测试流程
# 作者: MyStocks Testing Team
# 创建日期: 2025-11-26
# 版本: 1.0.0

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="/opt/claude/mystocks_spec"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="${PROJECT_ROOT}/tests/logs"
REPORT_DIR="${PROJECT_ROOT}/tests/reports"

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

log_debug() {
    if [[ "${DEBUG:-0}" == "1" ]]; then
        echo -e "${CYAN}[DEBUG]${NC} $1"
    fi
}

# 检查必需工具
check_prerequisites() {
    log_info "🔍 检查必需工具..."

    # 检查PM2
    if ! command -v pm2 &> /dev/null; then
        log_error "PM2 未安装，请先安装 PM2"
        exit 1
    fi
    log_info "✅ PM2: $(pm2 --version)"

    # 检查tmux
    if ! command -v tmux &> /dev/null; then
        log_error "tmux 未安装，请先安装 tmux"
        exit 1
    fi
    log_info "✅ tmux: $(tmux -V)"

    # 检查lnav
    if ! command -v lnav &> /dev/null; then
        log_error "lnav 未安装，请先安装 lnav"
        exit 1
    fi
    log_info "✅ lnav: $(lnav --version)"

    # 检查Node.js和npm
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装，请先安装 Node.js"
        exit 1
    fi
    log_info "✅ Node.js: $(node --version)"

    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装，请先安装 Python3"
        exit 1
    fi
    log_info "✅ Python3: $(python3 --version)"

    # 检查Playwright
    if ! command -v npx &> /dev/null; then
        log_error "npm/npx 未安装，请先安装 npm"
        exit 1
    fi

    log_info "✅ 所有工具检查完成"
}

# 创建必要目录
create_directories() {
    log_info "📁 创建必要目录..."

    mkdir -p "${LOG_DIR}"
    mkdir -p "${REPORT_DIR}"
    mkdir -p "${PROJECT_ROOT}/logs"
    mkdir -p "${PROJECT_ROOT}/logs/archive"

    log_info "✅ 目录创建完成"
}

# 清理旧进程
cleanup_old_processes() {
    log_info "🧹 清理旧进程和会话..."

    # 停止所有PM2进程
    if pm2 list | grep -q "online\|stopping"; then
        log_info "停止现有PM2进程..."
        pm2 stop all || true
        pm2 delete all || true
    fi

    # 清理tmux会话
    if tmux has-session -t mystocks-test 2>/dev/null; then
        log_info "删除现有tmux会话..."
        tmux kill-session -t mystocks-test || true
    fi

    # 清理旧日志文件
    find "${PROJECT_ROOT}/logs" -name "*.log" -mtime +7 -delete 2>/dev/null || true

    log_info "✅ 清理完成"
}

# 启动tmux会话
start_tmux_session() {
    log_info "🖥️ 启动tmux测试会话..."

    # 创建新的tmux会话
    tmux new-session -d -s mystocks-test

    # 加载配置文件
    if [[ -f "${PROJECT_ROOT}/scripts/tmux/mystocks-test.conf" ]]; then
        tmux source-file "${PROJECT_ROOT}/scripts/tmux/mystocks-test.conf"
        log_info "✅ tmux配置加载完成"
    else
        log_warn "tmux配置文件不存在，使用默认配置"
        # 创建默认窗格
        tmux split-window -h
        tmux split-window -v
        tmux split-window -v
    fi

    log_info "✅ tmux会话启动完成"
}

# 启动PM2服务
start_pm2_services() {
    log_info "🚀 启动PM2服务..."

    cd "${PROJECT_ROOT}"

    # 启动所有服务
    pm2 start pm2.config.js

    # 等待服务启动
    log_info "等待服务启动..."
    sleep 15

    # 检查服务状态
    local failed_services=()
    while IFS= read -r service; do
        if [[ $(pm2 jlist | jq -r ".[] | select(.name == \"$service\") | .pm2_env.status") != "online" ]]; then
            failed_services+=("$service")
        fi
    done < <(pm2 jlist | jq -r '.[].name')

    if [[ ${#failed_services[@]} -gt 0 ]]; then
        log_error "以下服务启动失败: ${failed_services[*]}"
        pm2 logs
        return 1
    fi

    # 验证服务可用性
    log_info "验证服务可用性..."

    # 检查前端服务
    local frontend_status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3001" || echo "000")
    if [[ "$frontend_status" != "200" ]]; then
        log_error "前端服务不可用 (状态码: $frontend_status)"
        return 1
    fi

    # 检查后端服务
    local backend_status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/health" || echo "000")
    if [[ "$backend_status" != "200" ]]; then
        log_error "后端服务不可用 (状态码: $backend_status)"
        return 1
    fi

    log_info "✅ 所有服务启动成功"
    return 0
}

# 启动日志监控
start_log_monitoring() {
    log_info "📊 启动日志监控..."

    # 在tmux会话中启动lnav
    tmux send-keys -t mystocks-test:0.2 "cd ${PROJECT_ROOT}" C-m
    tmux send-keys -t mystocks-test:0.2 "echo '🔍 启动日志聚合监控...'" C-m

    # 启动lnav监控所有日志文件
    tmux send-keys -t mystocks-test:0.2 "lnav logs/*.log ${LOG_DIR}/playwright-*.log ${LOG_DIR}/e2e-*.log" C-m

    log_info "✅ 日志监控启动完成"
}

# 运行测试
run_tests() {
    local test_type="${1:-all}"
    log_info "🧪 运行测试: $test_type"

    # 在tmux会话中运行测试
    tmux send-keys -t mystocks-test:0.1 "cd ${PROJECT_ROOT}/tests" C-m
    tmux send-keys -t mystocks-test:0.1 "echo '🧪 开始执行测试用例...'" C-m

    local test_command=""
    local log_file="${LOG_DIR}/playwright-${test_type}-${TIMESTAMP}.log"

    case "$test_type" in
        "all")
            test_command="npx playwright test --reporter=json --reporter=html --reporter=${log_file}"
            ;;
        "auth")
            test_command="npx playwright test tests/e2e/login.spec.js --reporter=json --reporter=${log_file}"
            ;;
        "api")
            test_command="npx playwright test tests/e2e/real-api-endpoints.spec.js --reporter=json --reporter=${log_file}"
            ;;
        "usability")
            test_command="npx playwright test tests/e2e/mystocks-comprehensive-e2e.spec.js --reporter=json --reporter=${log_file}"
            ;;
        "quick")
            test_command="npx playwright test --grep \"@fast\" --reporter=json --reporter=${log_file}"
            ;;
        *)
            log_error "未知的测试类型: $test_type"
            log_info "可用类型: all, auth, api, usability, quick"
            return 1
            ;;
    esac

    # 执行测试命令
    tmux send-keys -t mystocks-test:0.1 "$test_command" C-m

    log_info "✅ 测试启动完成，正在执行..."

    # 等待测试完成
    if [[ "$test_type" == "quick" ]]; then
        sleep 30
    elif [[ "$test_type" == "all" ]]; then
        sleep 180
    else
        sleep 120
    fi

    log_info "📊 测试执行中，请查看tmux会话实时进度"
}

# 生成测试报告
generate_report() {
    log_info "📄 生成测试报告..."

    # 移动报告到报告目录
    if [[ -d "${PROJECT_ROOT}/playwright-report" ]]; then
        mv "${PROJECT_ROOT}/playwright-report" "${REPORT_DIR}/report-${TIMESTAMP}"
        log_info "✅ HTML报告已生成: ${REPORT_DIR}/report-${TIMESTAMP}/index.html"
    fi

    # 生成JSON报告摘要
    cd "${PROJECT_ROOT}/tests"

    # 创建报告摘要
    {
        echo "{"
        echo "  \"timestamp\": \"$(date -Iseconds)\","
        echo "  \"test_type\": \"$1\","
        echo "  \"environment\": \"test\","
        echo "  \"frontend_url\": \"http://localhost:3001\","
        echo "  \"backend_url\": \"http://localhost:8000\","
        echo "  \"report_directory\": \"${REPORT_DIR}/report-${TIMESTAMP}\","
        echo "  \"log_directory\": \"${LOG_DIR}\""
        echo "}"
    } > "${REPORT_DIR}/summary-${TIMESTAMP}.json"

    log_info "✅ 报告生成完成"
}

# 服务状态检查
check_service_status() {
    log_info "🔍 检查服务状态..."

    # 检查PM2进程状态
    log_info "PM2进程状态:"
    pm2 status | grep -E "(online|stopping|errored)" || true

    # 检查端口占用
    log_info "端口占用状态:"
    ss -tuln | grep -E ":(3001|8000)" || true

    # 检查服务健康状态
    local frontend_health=$(curl -s http://localhost:3001/health 2>/dev/null | head -c 100 || echo "Unreachable")
    local backend_health=$(curl -s http://localhost:8000/health 2>/dev/null || echo "Unreachable")

    log_info "前端健康检查: $frontend_health"
    log_info "后端健康检查: $backend_health"
}

# 停止服务
stop_services() {
    log_info "🛑 停止服务..."

    # 保存最终日志快照
    if command -v lnav &> /dev/null; then
        log_info "保存日志快照..."
        lnav -w "${LOG_DIR}/lnav-snapshot-${TIMESTAMP}.log" logs/*.log ${LOG_DIR}/*.log &>/dev/null || true
    fi

    # 停止PM2服务
    pm2 stop all

    # 清理tmux会话
    if tmux has-session -t mystocks-test 2>/dev/null; then
        tmux detach -s mystocks-test
        # 保留会话以便后续查看
        log_info "tmux会话已保留，可通过 'tmux attach -t mystocks-test' 重新连接"
    fi

    log_info "✅ 服务停止完成"
}

# 显示最终状态
show_final_status() {
    log_info "📈 显示最终状态..."

    echo ""
    log_info "=== MyStocks 测试执行完成 ==="
    echo ""
    log_info "📊 测试报告:"
    if [[ -d "${REPORT_DIR}/report-${TIMESTAMP}" ]]; then
        log_info "  HTML报告: ${REPORT_DIR}/report-${TIMESTAMP}/index.html"
    fi
    if [[ -f "${REPORT_DIR}/summary-${TIMESTAMP}.json" ]]; then
        log_info "  摘要报告: ${REPORT_DIR}/summary-${TIMESTAMP}.json"
    fi
    echo ""
    log_info "📁 日志文件:"
    log_info "  测试日志: ${LOG_DIR}/"
    log_info "  服务日志: ${PROJECT_ROOT}/logs/"
    echo ""
    log_info "🔧 快捷命令:"
    log_info "  查看PM2状态: pm2 status"
    log_info "  重连tmux会话: tmux attach -t mystocks-test"
    log_info "  查看HTML报告: open ${REPORT_DIR}/report-${TIMESTAMP}/index.html"
    echo ""
}

# 主函数
main() {
    local test_type="${1:-all}"
    local action="${2:-run}"

    log_info "🚀 MyStocks 自动化测试脚本启动..."
    log_info "测试类型: $test_type"
    log_info "执行动作: $action"

    case "$action" in
        "check")
            check_prerequisites
            check_service_status
            ;;
        "start")
            check_prerequisites
            create_directories
            cleanup_old_processes
            start_tmux_session
            start_pm2_services
            start_log_monitoring
            ;;
        "test")
            start_tmux_session
            start_pm2_services
            start_log_monitoring
            run_tests "$test_type"
            generate_report "$test_type"
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 5
            main "$test_type" "start"
            ;;
        "full")
            cleanup_old_processes
            check_prerequisites
            create_directories
            start_tmux_session
            start_pm2_services
            start_log_monitoring
            run_tests "$test_type"
            generate_report "$test_type"
            stop_services
            show_final_status
            ;;
        *)
            echo "用法: $0 <test_type> <action>"
            echo ""
            echo "测试类型:"
            echo "  all       - 运行所有测试 (默认)"
            echo "  auth      - 用户认证测试"
            echo "  api       - API接口测试"
            echo "  usability - 可用性测试"
            echo "  quick     - 快速测试"
            echo ""
            echo "执行动作:"
            echo "  check     - 检查环境和工具"
            echo "  start     - 启动服务环境"
            echo "  test      - 运行测试"
            echo "  stop      - 停止服务"
            echo "  restart   - 重启服务"
            echo "  full      - 完整测试流程"
            echo ""
            echo "示例:"
            echo "  $0 auth test      # 运行认证测试"
            echo "  $0 all full       # 完整测试流程"
            echo "  $0 api restart    # 重启API服务"
            exit 1
            ;;
    esac
}

# 错误处理
trap 'log_error "脚本执行失败，退出码: $?"' ERR

# 执行主函数
main "$@"
