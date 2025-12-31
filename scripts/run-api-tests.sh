#!/bin/bash

# API 契约测试执行脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."

    if ! command -v node &> /dev/null; then
        print_error "Node.js 未安装"
        exit 1
    fi

    if ! command -v npx &> /dev/null; then
        print_error "npx 未安装"
        exit 1
    fi

    print_info "依赖检查通过"
}

# 检查后端服务
check_backend() {
    print_info "检查后端服务..."

    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_warn "后端服务未启动或无法访问"
        print_warn "请先启动后端服务: cd web/backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
        read -p "是否继续测试? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_info "后端服务运行正常"
    fi
}

# 显示帮助信息
show_help() {
    cat << EOF
API 契约测试执行脚本

用法: ./run-api-tests.sh [选项]

选项:
  all                 运行所有API测试
  auth                运行认证API测试
  market              运行市场数据API测试
  technical           运行技术指标API测试
  wencai              运行问财API测试
  strategy            运行策略API测试
  backtest            运行回测API测试
  system              运行系统API测试
  cache               运行缓存API测试
  report              生成测试报告
  help                显示此帮助信息

环境变量:
  API_BASE_URL        API基础URL (默认: http://localhost:8000)

示例:
  ./run-api-tests.sh all
  ./run-api-tests.sh auth
  API_BASE_URL=http://localhost:8001 ./run-api-tests.sh all
EOF
}

# 运行测试
run_tests() {
    local test_file=$1
    local test_name=$2

    print_info "运行 ${test_name} 测试..."
    print_info "测试文件: ${test_file}"

    if [ ! -f "$test_file" ]; then
        print_error "测试文件不存在: ${test_file}"
        return 1
    fi

    npx playwright test "$test_file" --reporter=list --reporter=json --reporter=html

    if [ $? -eq 0 ]; then
        print_info "${test_name} 测试通过"
    else
        print_error "${test_name} 测试失败"
        return 1
    fi
}

# 主逻辑
case "$1" in
    all)
        check_dependencies
        check_backend
        print_info "运行所有API测试..."
        npx playwright test tests/api/ --reporter=list --reporter=json --reporter=html
        print_info "测试报告已生成到 playwright-report/"
        ;;
    auth)
        check_dependencies
        check_backend
        run_tests "tests/api/auth.spec.ts" "认证API"
        ;;
    market)
        check_dependencies
        check_backend
        run_tests "tests/api/market.spec.ts" "市场数据API"
        ;;
    technical)
        check_dependencies
        check_backend
        run_tests "tests/api/technical.spec.ts" "技术指标API"
        ;;
    wencai)
        check_dependencies
        check_backend
        run_tests "tests/api/wencai.spec.ts" "问财API"
        ;;
    strategy)
        check_dependencies
        check_backend
        run_tests "tests/api/strategy.spec.ts" "策略API"
        ;;
    backtest)
        check_dependencies
        check_backend
        run_tests "tests/api/backtest.spec.ts" "回测API"
        ;;
    system)
        check_dependencies
        check_backend
        run_tests "tests/api/system.spec.ts" "系统API"
        ;;
    cache)
        check_dependencies
        check_backend
        run_tests "tests/api/cache.spec.ts" "缓存API"
        ;;
    report)
        print_info "打开测试报告..."
        npx playwright show-report
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        show_help
        ;;
    *)
        print_error "未知选项: $1"
        show_help
        exit 1
        ;;
esac
