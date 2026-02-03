#!/bin/bash

###############################################################################
# MyStocks Web 端自动化测试启动脚本
#
# 使用方法:
#   ./scripts/tests/run-playwright-tests.sh              # 运行所有测试
#   ./scripts/tests/run-playwright-tests.sh --debug      # 调试模式
#   ./scripts/tests/run-playwright-tests.sh --ui         # UI 模式
#   ./scripts/tests/run-playwright-tests.sh --headed     # 显示浏览器
#   ./scripts/tests/run-playwright-tests.sh --report     # 查看报告
###############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/web/frontend"
BACKEND_DIR="$PROJECT_ROOT/web/backend"

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

# 检查前置条件
check_prerequisites() {
    log_info "检查前置条件..."

    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装，请先安装 Node.js"
        exit 1
    fi
    log_success "Node.js 已安装: $(node --version)"

    # 检查 npm
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装，请先安装 npm"
        exit 1
    fi
    log_success "npm 已安装: $(npm --version)"

    # 检查 Python
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        log_error "Python 未安装，请先安装 Python"
        exit 1
    fi
    log_success "Python 已安装"
}

# 安装依赖
install_dependencies() {
    log_info "安装依赖..."

    # 前端依赖
    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
        log_info "安装前端依赖..."
        cd "$FRONTEND_DIR"
        npm install
        log_success "前端依赖安装完成"
    fi

    # Playwright 依赖
    log_info "安装 Playwright..."
    cd "$PROJECT_ROOT"
    npx playwright install
    log_success "Playwright 安装完成"
}

# 运行测试
run_tests() {
    local mode=$1
    local test_file="tests/e2e/login.spec.js"

    cd "$PROJECT_ROOT"

    case $mode in
        "debug")
            log_info "以调试模式运行测试..."
            npx playwright test --debug --config=playwright.config.web.ts "$test_file"
            ;;
        "ui")
            log_info "以 UI 模式运行测试..."
            npx playwright test --ui --config=playwright.config.web.ts "$test_file"
            ;;
        "headed")
            log_info "以显示浏览器模式运行测试..."
            npx playwright test --headed --config=playwright.config.web.ts "$test_file"
            ;;
        "report")
            log_info "查看测试报告..."
            npx playwright show-report playwright-report
            ;;
        "chrome")
            log_info "仅在 Chrome 中运行测试..."
            npx playwright test --project=chromium --config=playwright.config.web.ts "$test_file"
            ;;
        "firefox")
            log_info "仅在 Firefox 中运行测试..."
            npx playwright test --project=firefox --config=playwright.config.web.ts "$test_file"
            ;;
        "webkit")
            log_info "仅在 Safari 中运行测试..."
            npx playwright test --project=webkit --config=playwright.config.web.ts "$test_file"
            ;;
        *)
            log_info "运行所有测试..."
            npx playwright test --config=playwright.config.web.ts "$test_file"
            ;;
    esac
}

# 显示帮助信息
show_help() {
    cat << EOF
${BLUE}MyStocks Web 端自动化测试脚本${NC}

用法:
  $0 [选项]

选项:
  --help       显示此帮助信息
  --debug      以调试模式运行测试
  --ui         以 UI 模式运行测试
  --headed     显示浏览器窗口运行测试
  --report     查看测试报告
  --chrome     仅在 Chrome 浏览器中运行
  --firefox    仅在 Firefox 浏览器中运行
  --webkit     仅在 Safari 浏览器中运行

示例:
  # 运行所有测试
  $0

  # 调试模式
  $0 --debug

  # UI 模式（推荐用于开发）
  $0 --ui

  # 仅在 Chrome 中运行
  $0 --chrome

  # 查看测试报告
  $0 --report

EOF
}

# 主函数
main() {
    local mode=""

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help)
                show_help
                exit 0
                ;;
            --debug)
                mode="debug"
                shift
                ;;
            --ui)
                mode="ui"
                shift
                ;;
            --headed)
                mode="headed"
                shift
                ;;
            --report)
                mode="report"
                shift
                ;;
            --chrome)
                mode="chrome"
                shift
                ;;
            --firefox)
                mode="firefox"
                shift
                ;;
            --webkit)
                mode="webkit"
                shift
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done

    log_info "开始 MyStocks Web 端自动化测试流程..."
    log_info "项目根目录: $PROJECT_ROOT"

    # 检查前置条件
    check_prerequisites

    # 安装依赖
    install_dependencies

    # 运行测试
    if run_tests "$mode"; then
        log_success "测试完成！"
        exit 0
    else
        log_error "测试失败！"
        exit 1
    fi
}

# 运行主函数
main "$@"
