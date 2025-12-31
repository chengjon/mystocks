#!/bin/bash

# 自动化测试日志分析脚本
# 在测试执行期间自动分析日志

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志文件
LOG_DIR="logs"
TEST_LOG="${LOG_DIR}/test_analysis.log"
ERROR_LOG="${LOG_DIR}/errors.log"
PERFORMANCE_LOG="${LOG_DIR}/performance.log"
SUMMARY_LOG="${LOG_DIR}/summary.log"

# 统计变量
TOTAL_ERRORS=0
TOTAL_WARNINGS=0
TOTAL_API_CALLS=0
SLOW_REQUESTS=0

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 初始化日志目录
init_logs() {
    mkdir -p "$LOG_DIR"

    # 清空日志文件
    > "$TEST_LOG"
    > "$ERROR_LOG"
    > "$PERFORMANCE_LOG"
    > "$SUMMARY_LOG"

    print_info "日志目录初始化完成"
}

# 分析错误日志
analyze_errors() {
    print_info "分析错误日志..."

    local error_count=$(grep -r -E "ERROR|CRITICAL|FATAL|Exception|Traceback" "$LOG_DIR"/*.log 2>/dev/null | wc -l)
    local critical_count=$(grep -r -E "CRITICAL|FATAL" "$LOG_DIR"/*.log 2>/dev/null | wc -l)

    TOTAL_ERRORS=$error_count

    echo "=== 错误分析 ===" >> "$SUMMARY_LOG"
    echo "总错误数: $error_count" >> "$SUMMARY_LOG"
    echo "严重错误数: $critical_count" >> "$SUMMARY_LOG"
    echo "" >> "$SUMMARY_LOG"

    # 按模块统计错误
    print_info "按模块统计错误..."
    echo "=== 按模块统计 ===" >> "$SUMMARY_LOG"

    for log_file in "$LOG_DIR"/*.log; do
        if [ -f "$log_file" ]; then
            local module_name=$(basename "$log_file" .log)
            local module_errors=$(grep -E "ERROR|CRITICAL|FATAL" "$log_file" 2>/dev/null | wc -l)

            if [ $module_errors -gt 0 ]; then
                echo "$module_name: $module_errors 个错误" >> "$SUMMARY_LOG"
            fi
        fi
    done

    echo "" >> "$SUMMARY_LOG"

    # 提取错误详情
    grep -r -E "ERROR|CRITICAL|FATAL|Exception|Traceback" "$LOG_DIR"/*.log 2>/dev/null > "$ERROR_LOG" || true

    print_info "错误分析完成，发现 $error_count 个错误"
}

# 分析性能日志
analyze_performance() {
    print_info "分析性能日志..."

    # 提取响应时间
    grep -r -E "response_time|duration|elapsed" "$LOG_DIR"/*.log 2>/dev/null > "$PERFORMANCE_LOG" || true

    # 统计API调用
    TOTAL_API_CALLS=$(grep -r -E "GET|POST|PUT|DELETE" "$LOG_DIR"/*.log 2>/dev/null | wc -l)

    # 统计慢请求 (> 1s)
    SLOW_REQUESTS=$(grep -r -E "(response_time|duration|elapsed).*[0-9]{4,}ms|response_time.*[1-9]\d{3,}ms" "$LOG_DIR"/*.log 2>/dev/null | wc -l)

    echo "=== 性能分析 ===" >> "$SUMMARY_LOG"
    echo "API调用总数: $TOTAL_API_CALLS" >> "$SUMMARY_LOG"
    echo "慢请求数 (>1s): $SLOW_REQUESTS" >> "$SUMMARY_LOG"
    echo "" >> "$SUMMARY_LOG"

    # 计算平均响应时间
    local avg_time=$(grep -oE '[0-9]+ms' "$PERFORMANCE_LOG" 2>/dev/null | sed 's/ms//' | awk '{sum+=$1; count++} END {if(count>0) print sum/count else print 0}')

    echo "平均响应时间: ${avg_time}ms" >> "$SUMMARY_LOG"
    echo "" >> "$SUMMARY_LOG"

    print_info "性能分析完成，平均响应时间: ${avg_time}ms"
}

# 分析测试覆盖率
analyze_coverage() {
    print_info "分析测试覆盖率..."

    local tested_apis=$(grep -r -oE '/api/[a-zA-Z0-9_/]+' "$LOG_DIR"/api*.log 2>/dev/null | sort -u | wc -l)
    local total_apis=209

    local coverage=$((tested_apis * 100 / total_apis))

    echo "=== 测试覆盖率 ===" >> "$SUMMARY_LOG"
    echo "已测试API数: $tested_apis" >> "$SUMMARY_LOG"
    echo "总API数: $total_apis" >> "$SUMMARY_LOG"
    echo "覆盖率: ${coverage}%" >> "$SUMMARY_LOG"
    echo "" >> "$SUMMARY_LOG"

    print_info "测试覆盖率: ${coverage}%"
}

# 生成报告
generate_report() {
    print_info "生成分析报告..."

    echo "========================================" >> "$SUMMARY_LOG"
    echo "自动化测试日志分析报告" >> "$SUMMARY_LOG"
    echo "========================================" >> "$SUMMARY_LOG"
    echo "生成时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$SUMMARY_LOG"
    echo "" >> "$SUMMARY_LOG"

    cat "$SUMMARY_LOG"

    # 打印到控制台
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}自动化测试日志分析报告${NC}"
    echo -e "${BLUE}========================================${NC}"
    cat "$SUMMARY_LOG"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# 显示帮助信息
show_help() {
    cat << EOF
自动化测试日志分析脚本

用法: ./analyze-test-logs.sh [选项]

选项:
  analyze             分析日志并生成报告
  errors              仅分析错误
  performance         仅分析性能
  coverage            仅分析覆盖率
  report              生成完整报告
  clear               清空日志文件
  help                显示此帮助信息

示例:
  ./analyze-test-logs.sh analyze
  ./analyze-test-logs.sh errors
  ./analyze-test-logs.sh report
EOF
}

# 主逻辑
case "$1" in
    analyze)
        init_logs
        analyze_errors
        analyze_performance
        analyze_coverage
        generate_report
        ;;
    errors)
        init_logs
        analyze_errors
        ;;
    performance)
        init_logs
        analyze_performance
        ;;
    coverage)
        init_logs
        analyze_coverage
        ;;
    report)
        generate_report
        ;;
    clear)
        print_info "清空日志文件..."
        rm -rf "$LOG_DIR"/*.log
        print_info "日志文件已清空"
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
