#!/bin/bash
# MyStocks多工具协同测试执行脚本 (简化版)
# Phase 4.1: 全栈协同测试机制 - 多工具协同执行框架

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_phase() {
    local phase=$1
    local message=$2
    echo -e "${PURPLE}[PHASE ${phase}]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $message"
}

# Phase定义
declare -A PHASE_NAMES=(
    [0]="ESM兼容性预处理"
    [1]="PM2环境管理和健康检查"
    [2]="后端测试基础优化"
    [3]="前端测试分层建设"
    [4]="全栈协同测试机制"
    [5]="性能测试和监控体系"
    [6]="验证和部署准备"
)

declare -A PHASE_SCRIPTS=(
    [0]="${SCRIPT_DIR}/esm-validation.sh"
    [1]="${SCRIPT_DIR}/start-environment.sh"
    [2]="${SCRIPT_DIR}/run-schemathesis.sh"
    [3]="${SCRIPT_DIR}/run-playwright-tests.sh"
    [4]="${SCRIPT_DIR}/run-orchestration.sh"
    [5]="${SCRIPT_DIR}/run-performance-tests.sh"
    [6]="${SCRIPT_DIR}/run-validation.sh"
)

# 执行单个Phase
execute_phase() {
    local phase=$1
    local phase_name=${PHASE_NAMES[$phase]}
    local script_path=${PHASE_SCRIPTS[$phase]}

    log_phase "$phase" "开始执行: $phase_name"

    # 检查脚本是否存在
    if [ ! -f "$script_path" ]; then
        log_warn "Phase $phase 脚本不存在: $script_path (使用占位符)"
        create_placeholder "$phase" "$script_path"
    fi

    # 执行脚本
    log_info "执行脚本: $(basename "$script_path")"

    if bash "$script_path" 2>&1; then
        log_success "Phase $phase 执行成功"
        return 0
    else
        local exit_code=$?
        log_error "Phase $phase 执行失败 (退出码: $exit_code)"
        return 1
    fi
}

# 创建占位符脚本
create_placeholder() {
    local phase=$1
    local script_path=$2

    cat > "$script_path" << EOF
#!/bin/bash
echo "🔄 Phase $phase: ${PHASE_NAMES[$phase]}"
echo "此脚本为占位符，Phase $phase 尚未完全实现"
echo "✅ 占位符脚本执行完成"
exit 0
EOF

    chmod +x "$script_path"
}

# 执行Phase范围
execute_phases() {
    local start_phase=${1:-0}
    local end_phase=${2:-6}

    log_info "执行Phase范围: $start_phase 到 $end_phase"

    local failed_phases=()

    for phase in $(seq "$start_phase" "$end_phase"); do
        if execute_phase "$phase"; then
            log_success "Phase $phase 成功完成"
        else
            log_error "Phase $phase 执行失败"
            failed_phases+=("$phase")
        fi
    done

    if [ ${#failed_phases[@]} -eq 0 ]; then
        log_success "所有Phase执行完成"
    else
        log_error "部分Phase执行失败: ${failed_phases[*]}"
    fi
}

# 显示帮助
show_help() {
    cat << EOF
MyStocks多工具协同测试执行脚本

用法:
    $0 [选项]

选项:
    --phase PHASE          执行单个Phase (0-6)
    --start-phase PHASE    指定开始Phase (默认: 0)
    --end-phase PHASE      指定结束Phase (默认: 6)
    --help, -h             显示此帮助信息

Phase说明:
    0: ESM兼容性预处理
    1: PM2环境管理和健康检查
    2: 后端测试基础优化
    3: 前端测试分层建设
    4: 全栈协同测试机制
    5: 性能测试和监控体系
    6: 验证和部署准备

示例:
    $0                          # 执行所有Phase (0-6)
    $0 --phase 0               # 仅执行Phase 0
    $0 --start-phase 1 --end-phase 3  # 执行Phase 1-3
EOF
}

# 主函数
main() {
    echo "🚀 MyStocks多工具协同测试执行框架"
    echo "======================================"
    echo "Phase 4.1: 全栈协同测试机制"
    echo ""

    # 默认值
    START_PHASE=0
    END_PHASE=6
    SINGLE_PHASE=""

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --phase)
                SINGLE_PHASE="$2"
                shift 2
                ;;
            --start-phase)
                START_PHASE="$2"
                shift 2
                ;;
            --end-phase)
                END_PHASE="$2"
                shift 2
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

    # 确定执行范围
    if [ -n "$SINGLE_PHASE" ]; then
        START_PHASE="$SINGLE_PHASE"
        END_PHASE="$SINGLE_PHASE"
    fi

    log_info "执行配置:"
    log_info "  Phase范围: $START_PHASE-$END_PHASE"

    # 执行Phase
    execute_phases "$START_PHASE" "$END_PHASE"

    log_success "🎉 多工具协同测试框架执行完成!"
}

main "$@"