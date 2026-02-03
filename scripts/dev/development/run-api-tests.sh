#!/bin/bash

# Playwright API 自动化测试运行脚本
# 用于自动化测试 FastAPI 后端的所有接口

set -o pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
BASE_URL="${BASE_URL:-http://localhost:8000}"
API_TOKEN="${API_TOKEN:-}"
TEST_DIR="/opt/claude/mystocks_spec/web/frontend/tests"
TEST_FILE="api-automation.spec.js"
REPORT_DIR="/opt/claude/mystocks_spec/docs/reports/test-results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 检查环境依赖环境
check_env() {
    print_message "${BLUE}" "🔍 检查环境依赖..."

    local missing_deps=0

    if ! command -v curl &> /dev/null; then
        print_message "${RED}" "❌ 未找到 curl"
        missing_deps=1
    fi

    if ! command -v python3 &> /dev/null; then
        print_message "${RED}" "❌ 未找到 python3"
        missing_deps=1
    fi

    if [ $missing_deps -eq 1 ]; then
        return 1
    fi

    print_message "${GREEN}" "✅ 环境检查通过"
    return 0
}

# 检查后端服务
check_backend() {
    print_message "${BLUE}" "🔍 检查后端服务状态..."

    if curl -s -f "${BASE_URL}/health" > /dev/null 2>&1; then
        print_message "${GREEN}" "✅ 后端服务运行正常"
        return 0
    else
        print_message "${RED}" "❌ 后端服务未响应或不可用 (${BASE_URL}/health)"
        print_message "${YELLOW}" "请确保后端服务已启动并使用 REAL 数据源。"
        return 1
    fi
}

# 检查 Playwright 安装
check_playwright() {
    print_message "${BLUE}" "🔍 检查 Playwright 安装..."

    if ! command -v npx &> /dev/null; then
        print_message "${RED}" "❌ 未找到 npx 命令"
        print_message "${YELLOW}" "请先安装 Node.js 和 npm"
        return 1
    fi

    if [ ! -f "${TEST_DIR}/${TEST_FILE}" ]; then
        print_message "${RED}" "❌ 未找到测试文件: ${TEST_DIR}/${TEST_FILE}"
        return 1
    fi

    print_message "${GREEN}" "✅ Playwright 检查通过"
    return 0
}

# 创建报告目录
create_report_dir() {
    if [ ! -d "${REPORT_DIR}" ]; then
        mkdir -p "${REPORT_DIR}"
        print_message "${GREEN}" "✅ 创建报告目录: ${REPORT_DIR}"
    fi
}

# 运行 Playwright 测试
run_tests() {
    print_message "${BLUE}" "🚀 开始运行 API 自动化测试..."
    echo ""

    local output_file="${REPORT_DIR}/api-test-report-${TIMESTAMP}.txt"

    cd /opt/claude/mystocks_spec/web/frontend

    # 运行测试并保存输出
    # 使用 PIPESTATUS 获取管道中第一个命令的退出状态
    BASE_URL="${BASE_URL}" API_TOKEN="${API_TOKEN}" npx playwright test "${TEST_FILE}" \
        --reporter=list \
        --reporter=json \
        2>&1 | tee "${output_file}"

    local exit_code=${PIPESTATUS[0]}

    echo ""
    if [ ${exit_code} -eq 0 ]; then
        print_message "${GREEN}" "✅ 测试套件执行成功"
    else
        print_message "${YELLOW}" "⚠️  测试套件执行完成，但存在失败用例 (Exit Code: ${exit_code})"
    fi

    print_message "${BLUE}" "📄 报告已保存到:"
    echo "  - 文本报告: ${output_file}"
    echo "  - 测试结果: web/frontend/playwright-report/"

    return ${exit_code}
}

# 主函数
main() {
    print_message "${BLUE}" "══════════════════════════════════════════"
    print_message "${BLUE}" "   Playwright API 自动化测试 (REAL Data)"
    print_message "${BLUE}" "══════════════════════════════════════════"
    echo ""
    print_message "${YELLOW}" "配置信息:"
    echo "  - 后端地址: ${BASE_URL}"
    if [ -n "${API_TOKEN}" ]; then
        echo "  - 认证令牌: ${API_TOKEN:0:15}..."
    else
        echo "  - 认证令牌: (未设置)"
    fi
    echo "  - 测试目录: ${TEST_DIR}"
    echo "  - 报告目录: ${REPORT_DIR}"
    echo ""

    # 检查依赖
    check_env || exit 1
    check_backend || exit 1
    check_playwright || exit 1
    create_report_dir

    # 运行测试
    run_tests
    local test_exit_code=$?

    echo ""
    print_message "${BLUE}" "══════════════════════════════════════════"

    # 始终返回测试的退出码，除非我们希望 CI 忽略它
    return ${test_exit_code}
}

# 显示帮助信息
show_help() {
    cat << EOF
使用方法:
  $0 [选项]

选项:
  -h, --help          显示此帮助信息
  -u, --url URL       指定后端服务URL (默认: http://localhost:8000)
  -t, --token TOKEN   指定认证令牌

示例:
  $0                              # 使用默认配置运行测试
  $0 -u http://localhost:8001     # 指定不同的后端地址
  $0 -t "Bearer my-token"         # 指定认证令牌

环境变量:
  BASE_URL          后端服务地址 (默认: http://localhost:8000)
  API_TOKEN         认证令牌 (用于需要登录的接口)

注意: 本项目全面使用 REAL 数据，请确保后端已正确配置数据源。
EOF
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -u|--url)
            BASE_URL="$2"
            shift 2
            ;;
        -t|--token)
            API_TOKEN="$2"
            shift 2
            ;;
        *)
            print_message "${RED}" "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

# 运行主函数
main
