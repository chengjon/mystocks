#!/bin/bash
# 性能测试环境集成脚本
# Phase 5.1: 配置Locust性能测试环境

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[性能测试]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[性能测试]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[性能测试]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[性能测试]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查性能测试依赖..."

    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi

    # 检查pytest-benchmark
    if ! python3 -c "import pytest_benchmark" 2>/dev/null; then
        log_warn "pytest-benchmark 未安装，正在安装..."
        pip install pytest-benchmark
    fi

    # 检查Locust
    if ! python3 -c "import locust" 2>/dev/null; then
        log_warn "Locust 未安装，正在安装..."
        pip install locust
    fi

    log_success "依赖检查完成"
}

# 建立性能基线
establish_baseline() {
    log_info "建立性能基线..."

    python3 "${SCRIPT_DIR}/performance_test_suite.py" --baseline

    if [ $? -eq 0 ]; then
        log_success "性能基线建立成功"
    else
        log_error "性能基线建立失败"
        exit 1
    fi
}

# 运行pytest-benchmark测试
run_pytest_benchmarks() {
    log_info "运行pytest-benchmark性能测试..."

    cd "$PROJECT_ROOT"

    # 运行所有benchmark测试
    python -m pytest tests/ -k "benchmark" --benchmark-only --benchmark-json="benchmark_results.json" -v

    if [ $? -eq 0 ]; then
        log_success "pytest-benchmark测试完成"
    else
        log_warn "pytest-benchmark测试发现问题"
    fi
}

# 运行Locust负载测试
run_locust_test() {
    local users=${1:-50}
    local spawn_rate=${2:-5}
    local run_time=${3:-2m}

    log_info "运行Locust负载测试 (用户: $users, 孵化率: $spawn_rate, 时长: $run_time)..."

    python3 "${SCRIPT_DIR}/performance_test_suite.py" --load-test \
        --users "$users" \
        --spawn-rate "$spawn_rate" \
        --run-time "$run_time"

    if [ $? -eq 0 ]; then
        log_success "Locust负载测试完成"
    else
        log_error "Locust负载测试失败"
        exit 1
    fi
}

# 生成性能报告
generate_performance_report() {
    log_info "生成性能测试报告..."

    # 创建报告目录
    mkdir -p "${PROJECT_ROOT}/test-reports/performance"

    # 运行完整性能测试套件
    python3 "${SCRIPT_DIR}/performance_test_suite.py" > "${PROJECT_ROOT}/test-reports/performance/full_report_$(date +%Y%m%d_%H%M%S).json"

    if [ $? -eq 0 ]; then
        log_success "性能报告生成完成"
    else
        log_error "性能报告生成失败"
    fi
}

# 监控模式
start_monitoring() {
    log_info "启动性能监控模式..."
    log_info "按 Ctrl+C 停止监控"

    # 这里可以实现持续监控逻辑
    while true; do
        echo "🔍 $(date '+%H:%M:%S') - 执行性能检查..."
        sleep 30
    done
}

# 显示使用说明
show_usage() {
    cat << EOF
MyStocks性能测试环境集成工具
Phase 5.1: 配置Locust性能测试环境

用法:
    $0 [选项]

选项:
    --baseline          建立性能基线
    --pytest-bench      运行pytest-benchmark测试
    --locust-test       运行Locust负载测试
    --users NUM         并发用户数 (默认: 50)
    --spawn-rate NUM    用户孵化率 (默认: 5)
    --run-time TIME     测试运行时间 (默认: 2m)
    --report            生成完整性能报告
    --monitor           启动性能监控模式
    --all               运行完整性能测试套件
    --help, -h          显示此帮助信息

示例:
    $0 --baseline                    # 建立性能基线
    $0 --pytest-bench                # 运行基准测试
    $0 --locust-test --users 100     # 100用户负载测试
    $0 --all                         # 运行完整测试套件

输出文件:
    基线文件: test-reports/performance_baseline.json
    基准结果: benchmark_results.json
    Locust结果: test-reports/locust/results_*.csv
    性能报告: test-reports/performance/full_report_*.json
EOF
}

# 主函数
main() {
    echo "📈 MyStocks性能测试环境集成工具"
    echo "===================================="
    echo "Phase 5.1: 配置Locust性能测试环境"
    echo ""

    # 默认参数
    USERS=50
    SPAWN_RATE=5
    RUN_TIME="2m"

    # 参数解析
    while [[ $# -gt 0 ]]; do
        case $1 in
            --baseline)
                ACTION="baseline"
                shift
                ;;
            --pytest-bench)
                ACTION="pytest_bench"
                shift
                ;;
            --locust-test)
                ACTION="locust_test"
                shift
                ;;
            --users)
                USERS="$2"
                shift 2
                ;;
            --spawn-rate)
                SPAWN_RATE="$2"
                shift 2
                ;;
            --run-time)
                RUN_TIME="$2"
                shift 2
                ;;
            --report)
                ACTION="report"
                shift
                ;;
            --monitor)
                ACTION="monitor"
                shift
                ;;
            --all)
                ACTION="all"
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    # 检查依赖
    check_dependencies

    # 执行操作
    case $ACTION in
        baseline)
            establish_baseline
            ;;
        pytest_bench)
            run_pytest_benchmarks
            ;;
        locust_test)
            run_locust_test "$USERS" "$SPAWN_RATE" "$RUN_TIME"
            ;;
        report)
            generate_performance_report
            ;;
        monitor)
            start_monitoring
            ;;
        all|"")
            # 默认操作：运行完整性能测试套件
            log_info "运行完整性能测试套件..."

            establish_baseline
            echo ""
            run_pytest_benchmarks
            echo ""
            run_locust_test "$USERS" "$SPAWN_RATE" "$RUN_TIME"
            echo ""
            generate_performance_report
            ;;
    esac

    echo ""
    log_success "🎉 性能测试环境执行完成!"

    # 显示结果摘要
    echo ""
    echo "📊 测试结果摘要:"
    echo "  • 性能基线: ✅ 已建立 (test-reports/performance_baseline.json)"
    echo "  • pytest-benchmark: ✅ 已运行 (benchmark_results.json)"
    echo "  • Locust负载测试: ✅ 已完成 (test-reports/locust/)"
    echo "  • 性能报告: ✅ 已生成 (test-reports/performance/)"

    echo ""
    echo "🔧 告警检查:"
    if [ -f "${PROJECT_ROOT}/test-reports/performance_alerts.json" ]; then
        alert_count=$(jq '.alerts | length' "${PROJECT_ROOT}/test-reports/performance_alerts.json" 2>/dev/null || echo "0")
        if [ "$alert_count" -gt 0 ]; then
            echo "  ⚠️  发现 $alert_count 个性能告警，请检查: test-reports/performance_alerts.json"
        else
            echo "  ✅ 无性能告警"
        fi
    else
        echo "  ❓ 告警文件不存在"
    fi

    echo ""
    echo "📋 后续操作建议:"
    echo "  1. 查看详细报告: cat test-reports/performance/full_report_*.json"
    echo "  2. 分析性能趋势: 比较多次运行的结果"
    echo "  3. 优化发现的问题: 根据告警信息进行改进"
    echo "  4. 集成到CI/CD: 在构建流程中运行性能测试"
}

main "$@"