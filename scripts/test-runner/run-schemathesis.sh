#!/bin/bash
# Schemathesis API契约测试执行脚本
# 集成到CI/CD流水线

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 配置参数
BACKEND_URL="http://localhost:8000"
SCHEMATHESIS_OPTIONS="--checks all --validate-schema true --hypothesis-max-examples 50"
REPORT_DIR="${PROJECT_ROOT}/test-reports/schemathesis"
TIMEOUT=300  # 5分钟超时

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

# 创建报告目录
setup_reports() {
    log_info "创建报告目录..."
    mkdir -p "$REPORT_DIR"

    # 生成报告文件名（带时间戳）
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    export SCHEMATHESIS_REPORT="${REPORT_DIR}/schemathesis_report_${TIMESTAMP}.json"
    export SCHEMATHESIS_HTML="${REPORT_DIR}/schemathesis_report_${TIMESTAMP}.html"

    log_success "报告目录创建完成"
}

# 检查后端服务状态
check_backend() {
    log_info "检查后端服务状态..."

    # 等待后端服务启动
    local attempts=0
    local max_attempts=30  # 30次尝试，约30秒

    while [ $attempts -lt $max_attempts ]; do
        if curl -s --max-time 5 "${BACKEND_URL}/docs" > /dev/null 2>&1; then
            log_success "后端服务已就绪"
            return 0
        fi

        attempts=$((attempts + 1))
        log_info "等待后端服务启动... (${attempts}/${max_attempts})"
        sleep 1
    done

    log_error "后端服务启动超时"
    return 1
}

# 执行Schemathesis测试
run_schemathesis() {
    log_info "开始执行Schemathesis API契约测试..."

    # 设置Python路径
    export PYTHONPATH="${PROJECT_ROOT}:${PROJECT_ROOT}/web/backend:$PYTHONPATH"

    # 切换到后端目录
    cd "${PROJECT_ROOT}/web/backend"

    # 执行Schemathesis测试
    log_info "执行命令: schemathesis run ${BACKEND_URL}/openapi.json $SCHEMATHESIS_OPTIONS --report ${SCHEMATHESIS_REPORT}"

    # 设置超时并执行
    timeout $TIMEOUT schemathesis run \
        "${BACKEND_URL}/openapi.json" \
        $SCHEMATHESIS_OPTIONS \
        --report "${SCHEMATHESIS_REPORT}" \
        --output "${SCHEMATHESIS_HTML}"

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        log_success "Schemathesis测试执行成功"
        return 0
    elif [ $exit_code -eq 124 ]; then
        log_warn "Schemathesis测试执行超时"
        return 1
    else
        log_error "Schemathesis测试执行失败 (退出码: $exit_code)"
        return 1
    fi
}

# 分析测试结果
analyze_results() {
    log_info "分析测试结果..."

    if [ ! -f "$SCHEMATHESIS_REPORT" ]; then
        log_error "测试报告文件不存在: $SCHEMATHESIS_REPORT"
        return 1
    fi

    # 解析JSON报告
    local total_tests=$(jq -r '.total // 0' "$SCHEMATHESIS_REPORT" 2>/dev/null || echo "0")
    local passed_tests=$(jq -r '.passed // 0' "$SCHEMATHESIS_REPORT" 2>/dev/null || echo "0")
    local failed_tests=$(jq -r '.failed // 0' "$SCHEMATHESIS_REPORT" 2>/dev/null || echo "0")
    local errors_count=$(jq -r '.errors // 0' "$SCHEMATHESIS_REPORT" 2>/dev/null || echo "0")

    # 计算成功率
    local success_rate=0
    if [ "$total_tests" -gt 0 ]; then
        success_rate=$((passed_tests * 100 / total_tests))
    fi

    # 输出结果摘要
    echo ""
    echo "=========================================="
    echo "📊 Schemathesis测试结果摘要"
    echo "=========================================="
    echo "总测试数:     $total_tests"
    echo "通过测试:     $passed_tests"
    echo "失败测试:     $failed_tests"
    echo "错误数量:     $errors_count"
    echo "成功率:       ${success_rate}%"
    echo "报告文件:     $SCHEMATHESIS_REPORT"
    echo "HTML报告:     $SCHEMATHESIS_HTML"
    echo ""

    # 评估结果
    if [ "$success_rate" -ge 90 ]; then
        log_success "✅ API契约测试通过 (成功率: ${success_rate}%)"
        return 0
    elif [ "$success_rate" -ge 75 ]; then
        log_warn "⚠️ API契约测试基本通过 (成功率: ${success_rate}%)"
        return 0
    else
        log_error "❌ API契约测试失败 (成功率: ${success_rate}%)"
        return 1
    fi
}

# 生成状态ful测试报告
run_stateful_tests() {
    log_info "执行状态ful契约测试..."

    # 设置Python路径
    export PYTHONPATH="${PROJECT_ROOT}:${PROJECT_ROOT}/web/backend:$PYTHONPATH"

    # 切换到项目根目录
    cd "$PROJECT_ROOT"

    # 执行状态ful测试
    python -m pytest tests/contract/test_api_contract_schemathesis.py::TestAPIStatefulContract \
        -v --tb=short --maxfail=3 \
        --junitxml="${REPORT_DIR}/stateful_tests_${TIMESTAMP}.xml"

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        log_success "状态ful测试执行成功"
        return 0
    else
        log_warn "状态ful测试发现问题"
        return 1
    fi
}

# 清理函数
cleanup() {
    log_info "清理临时文件..."
    # 可以在这里添加清理逻辑
}

# 主函数
main() {
    local start_time=$(date +%s)

    echo "🔗 Schemathesis API契约测试执行脚本"
    echo "======================================"

    # 参数处理
    case "${1:-}" in
        "setup")
            setup_reports
            exit 0
            ;;
        "check-backend")
            check_backend
            exit $?
            ;;
        "stateful-only")
            run_stateful_tests
            exit $?
            ;;
        "help"|"-h"|"--help")
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  setup          仅执行报告目录设置"
            echo "  check-backend  仅检查后端服务状态"
            echo "  stateful-only  仅执行状态ful测试"
            echo "  help           显示此帮助信息"
            echo ""
            echo "无参数时执行完整的测试流程"
            exit 0
            ;;
    esac

    # 执行完整测试流程
    local exit_code=0

    # 1. 设置报告目录
    if ! setup_reports; then
        exit_code=1
    fi

    # 2. 检查后端服务
    if ! check_backend; then
        exit_code=1
    fi

    # 3. 执行Schemathesis测试
    if [ $exit_code -eq 0 ]; then
        if ! run_schemathesis; then
            exit_code=1
        fi
    fi

    # 4. 执行状态ful测试
    if [ $exit_code -eq 0 ]; then
        if ! run_stateful_tests; then
            exit_code=1
        fi
    fi

    # 5. 分析结果
    if [ $exit_code -eq 0 ]; then
        if ! analyze_results; then
            exit_code=1
        fi
    fi

    # 计算执行时间
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo ""
    echo "=========================================="
    if [ $exit_code -eq 0 ]; then
        log_success "🎉 Schemathesis测试执行完成 (耗时: ${duration}s)"
    else
        log_error "❌ Schemathesis测试执行失败 (耗时: ${duration}s)"
    fi
    echo "=========================================="

    cleanup
    exit $exit_code
}

# 错误处理
trap 'log_error "脚本执行失败，退出码: $?"' ERR

# 执行主函数
main "$@"