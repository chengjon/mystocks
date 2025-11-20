#!/bin/bash

# 无Docker E2E测试启动脚本
# 为Vue 3 + FastAPI架构优化的端到端测试执行器
# 
# 功能:
# 1. 环境检查和准备
# 2. 依赖安装验证
# 3. 测试服务启动管理
# 4. E2E测试执行
# 5. 结果报告生成
# 
# 作者: Claude Code
# 生成时间: 2025-11-14

set -e  # 遇到错误立即退出

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="$PROJECT_ROOT/test-results/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/test_execution_$TIMESTAMP.log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置参数
SKIP_ENV_CHECK=false
SKIP_DEPENDENCIES=false
SKIP_FRONTEND_INSTALL=false
SKIP_BACKEND_INSTALL=false
SKIP_PLAYWRIGHT_INSTALL=false
SKIP_FRONTEND_SERVER=false
SKIP_BACKEND_SERVER=false
PARALLEL_WORKERS=1
BROWSERS="chromium"
TEST_PATTERN=""
HEADLESS=true
VERBOSE=false
GENERATE_REPORT=true
CLEANUP=true

# 创建日志目录
mkdir -p "$LOG_DIR"

# 日志函数
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() {
    log "INFO" "${BLUE}$*${NC}"
}

log_success() {
    log "SUCCESS" "${GREEN}$*${NC}"
}

log_warning() {
    log "WARNING" "${YELLOW}$*${NC}"
}

log_error() {
    log "ERROR" "${RED}$*${NC}"
}

log_debug() {
    if [[ "$VERBOSE" == "true" ]]; then
        log "DEBUG" "${PURPLE}$*${NC}"
    fi
}

# 显示帮助信息
show_help() {
    cat << EOF
MyStocks 无Docker E2E测试启动脚本

用法: $0 [选项]

环境控制选项:
  --skip-env-check           跳过环境检查
  --skip-dependencies        跳过依赖安装检查
  --skip-frontend-install    跳过前端依赖安装
  --skip-backend-install     跳过后端依赖安装
  --skip-playwright-install  跳过Playwright浏览器安装

服务控制选项:
  --skip-frontend-server     跳过前端服务器启动
  --skip-backend-server      跳过后端服务器启动

测试执行选项:
  --workers NUM              并行工作进程数 (默认: 1)
  --browsers BROWSERS        浏览器列表，用逗号分隔 (默认: chromium)
                             可选值: chromium,firefox,webkit
  --pattern PATTERN          测试文件匹配模式 (默认: 所有测试)
  --headed                   非无头模式运行测试
  --verbose                  显示详细输出
  --no-report                不生成测试报告
  --no-cleanup               测试完成后不清理进程

帮助选项:
  --help, -h                 显示此帮助信息

示例:
  $0                                    # 运行所有测试
  $0 --pattern auth.spec.ts            # 只运行认证测试
  $0 --workers 3 --browsers chromium,firefox  # 多进程多浏览器测试
  $0 --headed --verbose                # 可视化调试模式

环境变量:
  PLAYWRIGHT_BASE_URL        前端URL (默认: http://localhost:5173)
  PLAYWRIGHT_API_URL         后端API URL (默认: http://localhost:8000)
  PLAYWRIGHT_TIMEOUT         测试超时时间 (默认: 30000)

EOF
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-env-check)
                SKIP_ENV_CHECK=true
                shift
                ;;
            --skip-dependencies)
                SKIP_DEPENDENCIES=true
                shift
                ;;
            --skip-frontend-install)
                SKIP_FRONTEND_INSTALL=true
                shift
                ;;
            --skip-backend-install)
                SKIP_BACKEND_INSTALL=true
                shift
                ;;
            --skip-playwright-install)
                SKIP_PLAYWRIGHT_INSTALL=true
                shift
                ;;
            --skip-frontend-server)
                SKIP_FRONTEND_SERVER=true
                shift
                ;;
            --skip-backend-server)
                SKIP_BACKEND_SERVER=true
                shift
                ;;
            --workers)
                PARALLEL_WORKERS="$2"
                shift 2
                ;;
            --browsers)
                BROWSERS="$2"
                shift 2
                ;;
            --pattern)
                TEST_PATTERN="$2"
                shift 2
                ;;
            --headed)
                HEADLESS=false
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --no-report)
                GENERATE_REPORT=false
                shift
                ;;
            --no-cleanup)
                CLEANUP=false
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 检查系统要求
check_system_requirements() {
    log_info "检查系统要求..."
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装"
        return 1
    fi
    
    NODE_VERSION=$(node --version)
    log_success "Node.js: $NODE_VERSION"
    
    # 检查npm
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装"
        return 1
    fi
    
    NPM_VERSION=$(npm --version)
    log_success "npm: $NPM_VERSION"
    
    # 检查Python3
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        return 1
    fi
    
    PYTHON_VERSION=$(python3 --version)
    log_success "$PYTHON_VERSION"
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 未安装"
        return 1
    fi
    
    return 0
}

# 检查端口可用性
check_port_available() {
    local port=$1
    local service_name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warning "$service_name 端口 $port 已被占用"
        return 1
    else
        log_success "$service_name 端口 $port 可用"
        return 0
    fi
}

# 安装前端依赖
install_frontend_dependencies() {
    if [[ "$SKIP_FRONTEND_INSTALL" == "true" ]]; then
        log_info "跳过前端依赖安装"
        return 0
    fi
    
    log_info "安装前端依赖..."
    
    local frontend_dir="$PROJECT_ROOT/web/frontend"
    
    if [[ ! -d "$frontend_dir" ]]; then
        log_error "前端目录不存在: $frontend_dir"
        return 1
    fi
    
    cd "$frontend_dir"
    
    if [[ ! -f "package.json" ]]; then
        log_error "package.json 文件不存在"
        return 1
    fi
    
    # 安装依赖
    log_info "执行 npm install..."
    if ! npm install --silent; then
        log_error "前端依赖安装失败"
        return 1
    fi
    
    log_success "前端依赖安装完成"
    return 0
}

# 安装后端依赖
install_backend_dependencies() {
    if [[ "$SKIP_BACKEND_INSTALL" == "true" ]]; then
        log_info "跳过后端依赖安装"
        return 0
    fi
    
    log_info "安装后端依赖..."
    
    local backend_dir="$PROJECT_ROOT/web/backend"
    
    if [[ ! -d "$backend_dir" ]]; then
        log_error "后端目录不存在: $backend_dir"
        return 1
    fi
    
    cd "$backend_dir"
    
    if [[ ! -f "requirements.txt" ]]; then
        log_error "requirements.txt 文件不存在"
        return 1
    fi
    
    # 安装依赖
    log_info "执行 pip3 install -r requirements.txt..."
    if ! pip3 install -r requirements.txt --quiet; then
        log_error "后端依赖安装失败"
        return 1
    fi
    
    log_success "后端依赖安装完成"
    return 0
}

# 安装Playwright浏览器
install_playwright_browsers() {
    if [[ "$SKIP_PLAYWRIGHT_INSTALL" == "true" ]]; then
        log_info "跳过Playwright浏览器安装"
        return 0
    fi
    
    log_info "安装Playwright浏览器..."
    
    cd "$PROJECT_ROOT"
    
    # 安装Playwright浏览器
    log_info "安装Playwright浏览器: $BROWSERS"
    if ! npx playwright install $BROWSERS --with-deps; then
        log_error "Playwright浏览器安装失败"
        return 1
    fi
    
    log_success "Playwright浏览器安装完成"
    return 0
}

# 启动前端服务器
start_frontend_server() {
    if [[ "$SKIP_FRONTEND_SERVER" == "true" ]]; then
        log_info "跳过前端服务器启动"
        return 0
    fi
    
    log_info "启动前端开发服务器..."
    
    local frontend_dir="$PROJECT_ROOT/web/frontend"
    
    if [[ ! -d "$frontend_dir" ]]; then
        log_error "前端目录不存在"
        return 1
    fi
    
    # 检查端口
    if ! check_port_available 5173 "前端"; then
        log_error "前端端口 5173 被占用，无法启动前端服务器"
        return 1
    fi
    
    cd "$frontend_dir"
    
    # 启动开发服务器（后台进程）
    export NODE_ENV=test
    export PLAYWRIGHT_BASE_URL=http://localhost:5173
    
    nohup npm run dev > "$LOG_DIR/frontend_$TIMESTAMP.log" 2>&1 &
    FRONTEND_PID=$!
    
    echo $FRONTEND_PID > "$PROJECT_ROOT/.test_frontend_pid"
    
    # 等待服务器启动
    log_info "等待前端服务器启动..."
    for i in {1..30}; do
        if curl -s http://localhost:5173 >/dev/null 2>&1; then
            log_success "前端服务器启动成功 (PID: $FRONTEND_PID)"
            return 0
        fi
        sleep 2
    done
    
    log_error "前端服务器启动超时"
    return 1
}

# 启动后端服务器
start_backend_server() {
    if [[ "$SKIP_BACKEND_SERVER" == "true" ]]; then
        log_info "跳过后端服务器启动"
        return 0
    fi
    
    log_info "启动后端API服务器..."
    
    local backend_dir="$PROJECT_ROOT/web/backend"
    
    if [[ ! -d "$backend_dir" ]]; then
        log_error "后端目录不存在"
        return 1
    fi
    
    # 检查端口
    if ! check_port_available 8000 "后端"; then
        log_error "后端端口 8000 被占用，无法启动后端服务器"
        return 1
    fi
    
    cd "$backend_dir"
    
    # 启动API服务器（后台进程）
    export TESTING=1
    export USE_MOCK_DATA=1
    export PLAYWRIGHT_API_URL=http://localhost:8000
    
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$LOG_DIR/backend_$TIMESTAMP.log" 2>&1 &
    BACKEND_PID=$!
    
    echo $BACKEND_PID > "$PROJECT_ROOT/.test_backend_pid"
    
    # 等待服务器启动
    log_info "等待后端服务器启动..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/docs >/dev/null 2>&1; then
            log_success "后端服务器启动成功 (PID: $BACKEND_PID)"
            return 0
        fi
        sleep 2
    done
    
    log_error "后端服务器启动超时"
    return 1
}

# 停止测试服务器
stop_test_servers() {
    if [[ "$CLEANUP" == "false" ]]; then
        log_info "跳过服务器清理"
        return 0
    fi
    
    log_info "停止测试服务器..."
    
    # 停止前端服务器
    if [[ -f "$PROJECT_ROOT/.test_frontend_pid" ]]; then
        local frontend_pid=$(cat "$PROJECT_ROOT/.test_frontend_pid")
        if kill -0 $frontend_pid 2>/dev/null; then
            kill $frontend_pid
            log_success "前端服务器已停止 (PID: $frontend_pid)"
        fi
        rm -f "$PROJECT_ROOT/.test_frontend_pid"
    fi
    
    # 停止后端服务器
    if [[ -f "$PROJECT_ROOT/.test_backend_pid" ]]; then
        local backend_pid=$(cat "$PROJECT_ROOT/.test_backend_pid")
        if kill -0 $backend_pid 2>/dev/null; then
            kill $backend_pid
            log_success "后端服务器已停止 (PID: $backend_pid)"
        fi
        rm -f "$PROJECT_ROOT/.test_backend_pid"
    fi
    
    # 强制清理任何残留进程
    pkill -f "npm run dev" 2>/dev/null || true
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
}

# 运行E2E测试
run_e2e_tests() {
    log_info "开始运行E2E测试..."
    
    cd "$PROJECT_ROOT"
    
    # 创建测试结果目录
    mkdir -p test-results/{screenshots,videos,traces,reports}
    
    # 设置环境变量
    export PLAYWRIGHT_BASE_URL=${PLAYWRIGHT_BASE_URL:-http://localhost:5173}
    export PLAYWRIGHT_API_URL=${PLAYWRIGHT_API_URL:-http://localhost:8000}
    export PLAYWRIGHT_TIMEOUT=${PLAYWRIGHT_TIMEOUT:-30000}
    
    # 构建测试命令
    local test_cmd="npx playwright test"
    
    # 添加测试模式
    if [[ -n "$TEST_PATTERN" ]]; then
        test_cmd="$test_cmd $TEST_PATTERN"
    else
        test_cmd="$test_cmd tests/e2e/specs/"
    fi
    
    # 添加并行度
    test_cmd="$test_cmd --workers=$PARALLEL_WORKERS"
    
    # 添加浏览器
    test_cmd="$test_cmd --project=$BROWSERS"
    
    # 添加输出选项
    test_cmd="$test_cmd --output=test-results"
    test_cmd="$test_cmd --reporter=html,json,junit"
    
    # 添加其他选项
    if [[ "$HEADLESS" == "false" ]]; then
        test_cmd="$test_cmd --headed"
    fi
    
    if [[ "$VERBOSE" == "true" ]]; then
        test_cmd="$test_cmd --verbose"
    fi
    
    log_info "执行测试命令: $test_cmd"
    
    # 执行测试
    if eval $test_cmd; then
        log_success "E2E测试执行成功"
        return 0
    else
        log_error "E2E测试执行失败"
        return 1
    fi
}

# 生成测试报告
generate_test_report() {
    if [[ "$GENERATE_REPORT" == "false" ]]; then
        log_info "跳过测试报告生成"
        return 0
    fi
    
    log_info "生成测试报告..."
    
    local report_dir="$PROJECT_ROOT/test-results/reports"
    local report_file="$report_dir/test_execution_report_$TIMESTAMP.md"
    
    mkdir -p "$report_dir"
    
    # 创建Markdown报告
    cat > "$report_file" << EOF
# E2E测试执行报告

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**项目**: MyStocks
**执行模式**: 无Docker测试环境

## 测试配置

- **并行进程数**: $PARALLEL_WORKERS
- **浏览器**: $BROWSERS
- **测试模式**: ${TEST_PATTERN:-所有测试}
- **无头模式**: $HEADLESS
- **详细输出**: $VERBOSE

## 环境信息

- **前端URL**: ${PLAYWRIGHT_BASE_URL:-http://localhost:5173}
- **后端URL**: ${PLAYWRIGHT_API_URL:-http://localhost:8000}
- **超时设置**: ${PLAYWRIGHT_TIMEOUT:-30000}ms

## 文件输出

- **截图目录**: test-results/screenshots/
- **视频目录**: test-results/videos/
- **追踪目录**: test-results/traces/
- **HTML报告**: test-results/index.html
- **JSON报告**: test-results/results.json
- **JUnit报告**: test-results/junit.xml

## 执行日志

详细执行日志请查看: $LOG_FILE

EOF
    
    log_success "测试报告已生成: $report_file"
    
    # 如果安装了HTML报告查看器，显示结果
    if [[ -f "$PROJECT_ROOT/test-results/index.html" ]]; then
        log_info "HTML测试报告: $PROJECT_ROOT/test-results/index.html"
    fi
}

# 清理函数
cleanup() {
    log_info "执行清理..."
    stop_test_servers
    
    # 清理临时文件
    rm -f "$PROJECT_ROOT/.test_frontend_pid"
    rm -f "$PROJECT_ROOT/.test_backend_pid"
    
    log_success "清理完成"
}

# 信号处理
trap cleanup EXIT INT TERM

# 主函数
main() {
    local start_time=$(date +%s)
    
    log_info "MyStocks 无Docker E2E测试启动"
    log_info "项目根目录: $PROJECT_ROOT"
    log_info "日志文件: $LOG_FILE"
    echo
    
    # 解析参数
    parse_args "$@"
    
    # 环境检查
    if [[ "$SKIP_ENV_CHECK" != "true" ]]; then
        log_info "=== 步骤 1: 环境检查 ==="
        if ! check_system_requirements; then
            log_error "环境检查失败"
            exit 1
        fi
        echo
    fi
    
    # 依赖检查和安装
    if [[ "$SKIP_DEPENDENCIES" != "true" ]]; then
        log_info "=== 步骤 2: 依赖安装 ==="
        if ! install_frontend_dependencies; then
            log_error "前端依赖安装失败"
            exit 1
        fi
        
        if ! install_backend_dependencies; then
            log_error "后端依赖安装失败"
            exit 1
        fi
        
        if ! install_playwright_browsers; then
            log_error "Playwright浏览器安装失败"
            exit 1
        fi
        echo
    fi
    
    # 启动服务
    log_info "=== 步骤 3: 启动测试服务 ==="
    if ! start_frontend_server; then
        log_error "前端服务器启动失败"
        exit 1
    fi
    
    if ! start_backend_server; then
        log_error "后端服务器启动失败"
        exit 1
    fi
    echo
    
    # 等待服务稳定
    log_info "=== 步骤 4: 等待服务稳定 ==="
    sleep 5
    echo
    
    # 运行测试
    log_info "=== 步骤 5: 运行E2E测试 ==="
    local test_success=true
    if ! run_e2e_tests; then
        test_success=false
    fi
    echo
    
    # 生成报告
    log_info "=== 步骤 6: 生成测试报告 ==="
    generate_test_report
    echo
    
    # 计算执行时间
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local minutes=$((duration / 60))
    local seconds=$((duration % 60))
    
    log_info "=== 执行完成 ==="
    log_info "总执行时间: ${minutes}分${seconds}秒"
    
    # 返回适当的退出码
    if [[ "$test_success" == "true" ]]; then
        log_success "测试执行成功"
        exit 0
    else
        log_error "测试执行失败"
        exit 1
    fi
}

# 显示启动横幅
show_banner() {
    cat << EOF
${CYAN}
╔══════════════════════════════════════════════════════════════╗
║                   MyStocks E2E 测试系统                       ║
║                   无Docker测试环境                            ║
╠══════════════════════════════════════════════════════════════╣
║  🎭  Playwright E2E 测试                                      ║
║  🔧  无Docker依赖                                            ║
║  ⚡  快速启动                                                ║
║  📊  详细报告                                                ║
╚══════════════════════════════════════════════════════════════╝
${NC}
EOF
}

# 显示启动信息
show_startup_info() {
    log_info "启动参数:"
    log_info "  跳过环境检查: $SKIP_ENV_CHECK"
    log_info "  跳过依赖安装: $SKIP_DEPENDENCIES"
    log_info "  跳过前端安装: $SKIP_FRONTEND_INSTALL"
    log_info "  跳过后端安装: $SKIP_BACKEND_INSTALL"
    log_info "  跳过Playwright安装: $SKIP_PLAYWRIGHT_INSTALL"
    log_info "  跳过前端服务器: $SKIP_FRONTEND_SERVER"
    log_info "  跳过后端服务器: $SKIP_BACKEND_SERVER"
    log_info "  并行进程数: $PARALLEL_WORKERS"
    log_info "  浏览器: $BROWSERS"
    log_info "  测试模式: ${TEST_PATTERN:-所有测试}"
    log_info "  无头模式: $HEADLESS"
    log_info "  详细输出: $VERBOSE"
    log_info "  生成报告: $GENERATE_REPORT"
    log_info "  清理进程: $CLEANUP"
    echo
}

# 执行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    show_banner
    show_startup_info
    main "$@"
fi