#!/bin/bash
# E2E测试运行脚本
# 提供统一的端到端测试执行入口
#
# 使用方法:
#   ./scripts/tests/run-e2e-tests.sh [选项]
#
# 选项:
#   --browser BROWSER    指定浏览器 (chromium|firefox|webkit) [默认: chromium]
#   --shard SHARD        测试分片 (N/M格式) [可选]
#   --project PROJECT    指定测试项目 [可选]
#   --grep PATTERN       只运行匹配的测试 [可选]
#   --headless          无头模式运行 [默认: false]
#   --headed            有头模式运行
#   --debug             调试模式
#   --report            生成HTML报告 [默认: true]
#   --trace             启用trace收集 [默认: on-first-retry]
#   --video             启用视频录制 [默认: retain-on-failure]
#   --screenshot        启用截图 [默认: only-on-failure]
#   --env ENV           测试环境 (dev|staging|prod) [默认: dev]
#   --parallel          并行执行测试 [默认: true]
#   --workers WORKERS   并行工作进程数 [默认: CPU核心数]
#   --timeout TIMEOUT   测试超时时间(秒) [默认: 30]
#   --verbose           详细输出
#   --ci               CI模式 (优化输出和性能)
#   --help             显示帮助信息
#
# 作者: Claude Code
# 创建时间: 2025-11-14

set -e

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/web/frontend"
BACKEND_DIR="$PROJECT_ROOT/web/backend"

# 默认配置
BROWSER="chromium"
HEADLESS_DEFAULT=false
REPORT=true
TRACE="on-first-retry"
VIDEO="retain-on-failure"
SCREENSHOT="only-on-failure"
ENV="dev"
PARALLEL=true
VERBOSE=false
CI=false
TIMEOUT=30

# 输出颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
E2E测试运行脚本

使用方法:
    $0 [选项]

选项:
    测试配置:
      --browser BROWSER    指定浏览器 (chromium|firefox|webkit) [默认: chromium]
      --shard SHARD        测试分片 (N/M格式) [可选]
      --project PROJECT    指定测试项目 [可选]
      --grep PATTERN       只运行匹配的测试 [可选]
      --env ENV           测试环境 (dev|staging|prod) [默认: dev]

    执行模式:
      --headless          无头模式运行 [默认: false]
      --headed            有头模式运行
      --debug             调试模式
      --parallel          并行执行测试 [默认: true]
      --workers WORKERS   并行工作进程数 [默认: CPU核心数]
      --timeout TIMEOUT   测试超时时间(秒) [默认: 30]

    报告和调试:
      --report            生成HTML报告 [默认: true]
      --no-report         不生成HTML报告
      --trace LEVEL       trace收集级别 (off|on-first-retry|retain-on-failure) [默认: on-first-retry]
      --video MODE        视频录制模式 (off|on|first-retry|retain-on-failure) [默认: retain-on-failure]
      --screenshot MODE   截图模式 (off|on|only-on-failure) [默认: only-on-failure]

    输出控制:
      --verbose           详细输出
      --ci               CI模式 (优化输出和性能)
      --help             显示此帮助信息

示例:
    # 运行所有测试
    $0

    # 只运行登录测试
    $0 --grep "登录"

    # 运行Firefox测试并启用调试
    $0 --browser firefox --debug --headed

    # CI环境运行 (无头模式，详细日志)
    $0 --headless --ci --verbose --trace retain-on-failure

    # 并行运行多浏览器测试
    $0 --parallel --workers 4

环境变量:
    PLAYWRIGHT_BASE_URL   基础URL [默认: http://localhost:5173]
    PLAYWRIGHT_API_URL    API URL [默认: http://localhost:8000]
    PLAYWRIGHT_TIMEOUT    测试超时 [默认: 30000ms]

EOF
}

# 检查依赖
check_dependencies() {
    local missing_deps=()

    if ! command -v node &> /dev/null; then
        missing_deps+=("node")
    fi

    if ! command -v npm &> /dev/null; then
        missing_deps+=("npm")
    fi

    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "缺少必要的依赖: ${missing_deps[*]}"
        exit 1
    fi

    # 检查Playwright是否安装
    if [ ! -d "$FRONTEND_DIR/node_modules/@playwright/test" ]; then
        log_warning "Playwright未安装，正在安装..."
        cd "$FRONTEND_DIR"
        npm install @playwright/test@1.48.1
        npx playwright install --with-deps
    fi

    log_success "依赖检查通过"
}

# 检查服务状态
check_services() {
    local base_url="${PLAYWRIGHT_BASE_URL:-http://localhost:5173}"
    local api_url="${PLAYWRIGHT_API_URL:-http://localhost:8000}"

    # 检查前端服务
    if ! curl -f "$base_url" &> /dev/null; then
        log_error "前端服务未运行: $base_url"
        log_info "请启动前端服务或运行: ./scripts/tests/manage-test-env.sh start"
        exit 1
    fi

    # 检查后端API
    if ! curl -f "$api_url/health" &> /dev/null; then
        log_error "后端API未运行: $api_url"
        log_info "请启动后端服务或运行: ./scripts/tests/manage-test-env.sh start"
        exit 1
    fi

    log_success "服务状态检查通过"
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --browser)
                BROWSER="$2"
                shift 2
                ;;
            --shard)
                SHARD="$2"
                shift 2
                ;;
            --project)
                PROJECT="$2"
                shift 2
                ;;
            --grep)
                GREP="$2"
                shift 2
                ;;
            --env)
                ENV="$2"
                shift 2
                ;;
            --headless)
                HEADLESS_DEFAULT=true
                shift
                ;;
            --headed)
                HEADLESS_DEFAULT=false
                shift
                ;;
            --debug)
                DEBUG=true
                HEADLESS_DEFAULT=false
                shift
                ;;
            --parallel)
                PARALLEL=true
                shift
                ;;
            --no-parallel)
                PARALLEL=false
                shift
                ;;
            --workers)
                WORKERS="$2"
                shift 2
                ;;
            --timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            --report)
                REPORT=true
                shift
                ;;
            --no-report)
                REPORT=false
                shift
                ;;
            --trace)
                TRACE="$2"
                shift 2
                ;;
            --video)
                VIDEO="$2"
                shift 2
                ;;
            --screenshot)
                SCREENSHOT="$2"
                shift 2
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --ci)
                CI=true
                HEADLESS_DEFAULT=true
                PARALLEL=true
                TRACE="retain-on-failure"
                VIDEO="retain-on-failure"
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # 验证参数
    case $BROWSER in
        chromium|firefox|webkit|edge)
            ;;
        *)
            log_error "不支持的浏览器: $BROWSER"
            log_info "支持的浏览器: chromium, firefox, webkit, edge"
            exit 1
            ;;
    esac

    case $ENV in
        dev|staging|prod)
            ;;
        *)
            log_error "不支持的环境: $ENV"
            log_info "支持的环境: dev, staging, prod"
            exit 1
            ;;
    esac
}

# 设置环境变量
setup_environment() {
    # 默认环境变量
    export PLAYWRIGHT_BASE_URL="${PLAYWRIGHT_BASE_URL:-http://localhost:5173}"
    export PLAYWRIGHT_API_URL="${PLAYWRIGHT_API_URL:-http://localhost:8000}"
    export PLAYWRIGHT_TIMEOUT="${PLAYWRIGHT_TIMEOUT:-$((TIMEOUT * 1000))}"
    export NODE_ENV="test"
    export USE_MOCK_DATA="true"

    # 根据环境设置特定变量
    case $ENV in
        dev)
            export PLAYWRIGHT_BASE_URL="http://localhost:5173"
            export PLAYWRIGHT_API_URL="http://localhost:8000"
            ;;
        staging)
            export PLAYWRIGHT_BASE_URL="https://staging.mystocks.company.com"
            export PLAYWRIGHT_API_URL="https://staging-api.mystocks.company.com"
            ;;
        prod)
            export PLAYWRIGHT_BASE_URL="https://mystocks.company.com"
            export PLAYWRIGHT_API_URL="https://api.mystocks.company.com"
            ;;
    esac
}

# 构建Playwright命令
build_playwright_command() {
    local cmd="npx playwright test"

    # 浏览器配置
    if [ -n "$PROJECT" ]; then
        cmd="$cmd --project=$PROJECT"
    else
        cmd="$cmd --project=$BROWSER"
    fi

    # 分片配置
    if [ -n "$SHARD" ]; then
        cmd="$cmd --shard=$SHARD"
    fi

    # 测试过滤
    if [ -n "$GREP" ]; then
        cmd="$cmd --grep=\"$GREP\""
    fi

    # 报告配置
    if [ "$REPORT" = true ]; then
        cmd="$cmd --reporter=html,json,junit"
    else
        cmd="$cmd --reporter=dot"
    fi

    # Trace配置
    cmd="$cmd --trace=$TRACE"

    # 视频配置
    cmd="$cmd --video=$VIDEO"

    # 截图配置
    cmd="$cmd --screenshot=$SCREENSHOT"

    # 并行配置
    if [ "$PARALLEL" = true ]; then
        local workers="${WORKERS:-$(nproc)}"
        cmd="$cmd --workers=$workers"
    fi

    # 调试配置
    if [ "$DEBUG" = true ]; then
        cmd="$cmd --debug"
        HEADLESS_DEFAULT=false
    fi

    # 超时配置
    cmd="$cmd --timeout=$((TIMEOUT * 1000))"

    # 输出目录
    cmd="$cmd --output=test-results/"

    echo "$cmd"
}

# 运行测试
run_tests() {
    cd "$FRONTEND_DIR"

    log_info "开始运行E2E测试..."
    log_info "配置信息:"
    log_info "  浏览器: $BROWSER"
    log_info "  环境: $ENV"
    log_info "  基础URL: $PLAYWRIGHT_BASE_URL"
    log_info "  API URL: $PLAYWRIGHT_API_URL"
    log_info "  超时: ${TIMEOUT}秒"
    log_info "  并行: $PARALLEL"
    log_info "  无头模式: $HEADLESS_DEFAULT"

    if [ -n "$SHARD" ]; then
        log_info "  分片: $SHARD"
    fi

    if [ -n "$GREP" ]; then
        log_info "  测试过滤: $GREP"
    fi

    # 构建命令
    local playwright_cmd=$(build_playwright_command)

    if [ "$VERBOSE" = true ]; then
        log_info "执行命令: $playwright_cmd"
    fi

    # 设置无头模式
    export HEADLESS="$HEADLESS_DEFAULT"

    # 执行测试
    if [ "$VERBOSE" = true ]; then
        eval "$playwright_cmd"
    else
        eval "$playwright_cmd" 2>&1 | tee /tmp/playwright-output.log
    fi

    local exit_code=$?

    # 生成报告
    if [ "$REPORT" = true ] && [ -f "playwright-report/index.html" ]; then
        log_success "HTML报告已生成: playwright-report/index.html"

        if [ "$CI" = true ]; then
            # CI环境中上传报告的逻辑
            log_info "在CI环境中，报告应该通过artifacts上传"
        fi
    fi

    # 显示结果摘要
    if [ -f "test-results/results.json" ]; then
        log_info "测试结果摘要:"
        if command -v jq &> /dev/null; then
            local total=$(jq '.stats.expected' test-results/results.json 2>/dev/null || echo "N/A")
            local passed=$(jq '.stats.expected' test-results/results.json 2>/dev/null || echo "N/A")
            local failed=$(jq '.stats.unexpected' test-results/results.json 2>/dev/null || echo "N/A")
            local duration=$(jq '.stats.duration' test-results/results.json 2>/dev/null || echo "N/A")

            log_info "  总计: $total"
            log_info "  通过: $passed"
            log_info "  失败: $failed"
            log_info "  耗时: ${duration}ms"
        else
            log_info "请安装jq以查看详细结果: sudo apt-get install jq"
        fi
    fi

    return $exit_code
}

# 主函数
main() {
    # 解析参数
    parse_args "$@"

    # 设置环境
    setup_environment

    # 检查环境
    check_dependencies

    # 检查服务（仅在非CI模式下）
    if [ "$CI" != true ]; then
        check_services
    fi

    # 运行测试
    if run_tests; then
        log_success "所有测试通过!"
        exit 0
    else
        log_error "有测试失败"
        exit 1
    fi
}

# 执行主函数
main "$@"
