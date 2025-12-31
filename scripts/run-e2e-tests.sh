#!/bin/bash
# E2E测试执行脚本
# 运行所有E2E测试或指定模块的测试

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    echo "E2E测试执行脚本"
    echo ""
    echo "用法: $0 [选项] [模块]"
    echo ""
    echo "选项:"
    echo "  -h, --help           显示帮助信息"
    echo "  -u, --ui             使用UI模式运行测试"
    echo "  -d, --debug          使用调试模式运行测试"
    echo "  -H, --headed         使用有头模式运行测试"
    echo "  -w, --workers N      设置worker数量"
    echo ""
    echo "模块:"
    echo "  all                 运行所有E2E测试 (默认)"
    echo "  auth                认证测试"
    echo "  dashboard           仪表板测试"
    echo "  stocks              股票列表测试"
    echo "  strategy            策略管理测试"
    echo "  backtest            回测分析测试"
    echo "  technical           技术分析测试"
    echo "  monitor             系统监控测试"
    echo "  monitoring          监控中心测试"
    echo "  tasks               任务管理测试"
    echo ""
    echo "示例:"
    echo "  $0 all              # 运行所有E2E测试"
    echo "  $0 auth             # 运行认证测试"
    echo "  $0 -u dashboard     # UI模式运行仪表板测试"
    echo "  $0 -d stocks        # 调试模式运行股票列表测试"
}

# 默认参数
MODE=""
WORKERS=""
MODULE="all"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -u|--ui)
            MODE="--ui"
            shift
            ;;
        -d|--debug)
            MODE="--debug"
            shift
            ;;
        -H|--headed)
            MODE="--headed"
            shift
            ;;
        -w|--workers)
            WORKERS="--workers $2"
            shift 2
            ;;
        all|auth|dashboard|stocks|strategy|backtest|technical|monitor|monitoring|tasks)
            MODULE=$1
            shift
            ;;
        *)
            print_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 进入项目根目录
cd "$(dirname "$0")/.."
print_info "工作目录: $(pwd)"

# 检查前端是否运行
print_info "检查前端服务..."
if ! curl -s http://localhost:3000 > /dev/null; then
    print_warning "前端服务未运行，请先启动前端："
    echo "  cd web/frontend && npm run dev"
    exit 1
fi
print_success "前端服务运行中"

# 检查后端是否运行
print_info "检查后端服务..."
if ! curl -s http://localhost:8000/health > /dev/null; then
    print_warning "后端服务未运行，请先启动后端："
    echo "  python3 simple_auth_server.py"
    exit 1
fi
print_success "后端服务运行中"

# 构建测试命令
BASE_CMD="npx playwright test e2e"

# 根据模块选择测试文件
case $MODULE in
    all)
        TEST_FILES="tests/e2e/"
        ;;
    auth)
        TEST_FILES="tests/e2e/auth.spec.ts"
        ;;
    dashboard)
        TEST_FILES="tests/e2e/dashboard.spec.ts"
        ;;
    stocks)
        TEST_FILES="tests/e2e/stocks.spec.ts"
        ;;
    strategy)
        TEST_FILES="tests/e2e/strategy-management.spec.ts"
        ;;
    backtest)
        TEST_FILES="tests/e2e/backtest-analysis.spec.ts"
        ;;
    technical)
        TEST_FILES="tests/e2e/technical-analysis.spec.ts"
        ;;
    monitor)
        TEST_FILES="tests/e2e/monitor.spec.ts"
        ;;
    monitoring)
        TEST_FILES="tests/e2e/monitoring-dashboard.spec.ts"
        ;;
    tasks)
        TEST_FILES="tests/e2e/task-management.spec.ts"
        ;;
esac

# 执行测试
print_info "运行E2E测试: $MODULE"
echo "命令: npx playwright test $TEST_FILES $MODE $WORKERS"
echo ""

# 运行测试
if eval npx playwright test "$TEST_FILES" $MODE $WORKERS; then
    print_success "E2E测试完成"

    # 显示测试报告位置
    if [ "$MODE" != "--ui" ] && [ "$MODE" != "--debug" ]; then
        print_info "测试报告: playwright-report/index.html"
    fi
else
    print_error "E2E测试失败"
    exit 1
fi
