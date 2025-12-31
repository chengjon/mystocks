#!/bin/bash

###############################################################################
# Phase 7 增强版进度监控脚本
#
# 功能:
#   - 基于文件修改时间监控Worker CLI活跃度
#   - 检测TASK-REPORT.md（如果存在）
#   - 统计各worktree的代码行数变化
#   - 生成实时活跃度报告
#
# 使用方式:
#   bash scripts/monitor_phase7_progress_enhanced.sh
#
# 作者: Main CLI (Manager)
# 版本: v2.0 (enhanced)
# 创建时间: 2025-12-30
###############################################################################

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目路径配置
MAIN_PROJECT="/opt/claude/mystocks_spec"
WORKTREES=(
    "backend:/opt/claude/mystocks_phase7_backend"
    "test:/opt/claude/mystocks_phase7_test"
    "frontend:/opt/claude/mystocks_phase7_frontend"
)

# 时间戳
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
DATE_ONLY=$(date +"%Y-%m-%d")

# 报告目录
REPORT_DIR="${MAIN_PROJECT}/reports/phase7_monitoring"
mkdir -p "${REPORT_DIR}"

# 最新报告路径
LATEST_REPORT="${REPORT_DIR}/latest_progress_enhanced.txt"

###############################################################################
# 函数: 打印带时间戳的日志
###############################################################################
log() {
    local level=$1
    shift
    local message="$*"
    echo -e "${TIMESTAMP} [${level}] ${message}"
}

###############################################################################
# 函数: 检查Worker CLI的文件活跃度
###############################################################################
check_worker_activity() {
    local worker_name=$1
    local worktree_path=$2

    # 统计最近修改的文件数量（过去2小时）
    local recent_python=$(find "${worktree_path}" -type f -name "*.py" -mmin -120 2>/dev/null | wc -l)
    local recent_ts=$(find "${worktree_path}" -type f \( -name "*.ts" -o -name "*.vue" \) -mmin -120 2>/dev/null | wc -l)
    local recent_sh=$(find "${worktree_path}" -type f -name "*.sh" -mmin -120 2>/dev/null | wc -l)
    local total_recent=$((recent_python + recent_ts + recent_sh))

    # 检查TASK-REPORT.md
    local task_report="${worktree_path}/TASK-REPORT.md"
    local has_report="❌"
    if [[ -f "${task_report}" ]]; then
        has_report="✅"
    fi

    # 判断活跃度
    local activity_level="🔴 闲置"
    if [[ ${total_recent} -gt 20 ]]; then
        activity_level="🟢 高度活跃"
    elif [[ ${total_recent} -gt 5 ]]; then
        activity_level="🟡 活跃"
    elif [[ ${total_recent} -gt 0 ]]; then
        activity_level="🟠 轻度活跃"
    fi

    # 输出结果
    echo "${worker_name}|${activity_level}|${total_recent}|${recent_python}|${recent_ts}|${recent_sh}|${has_report}"
}

###############################################################################
# 函数: 显示最近修改的文件示例
###############################################################################
show_recent_files() {
    local worktree_path=$1
    local limit=$2

    echo "最近修改的文件示例（过去2小时）:"
    find "${worktree_path}" -type f \( -name "*.py" -o -name "*.ts" -o -name "*.vue" -o -name "*.sh" \) -mmin -120 -printf "%T+ %p\n" 2>/dev/null | sort -r | head -${limit} | while read -r timestamp filepath; do
        local relative_path="${filepath#${worktree_path}/}"
        echo "  📄 ${relative_path}"
    done
}

###############################################################################
# 函数: 生成活跃度报告
###############################################################################
generate_activity_report() {
    local report_file=$1

    {
        echo "════════════════════════════════════════════════════════════════"
        echo "        Phase 7 多CLI并行开发 - 增强版活跃度监控报告"
        echo "════════════════════════════════════════════════════════════════"
        echo ""
        echo "生成时间: ${TIMESTAMP}"
        echo "监控方式: 基于文件修改时间（不依赖TASK-REPORT.md）"
        echo "活跃阈值: 过去2小时内修改的文件"
        echo ""

        # 检查所有Worker CLI
        echo "────────────────────────────────────────────────────────────────"
        echo "📊 Worker CLI 活跃度总览"
        echo "────────────────────────────────────────────────────────────────"
        echo ""

        local total_active=0
        local total_workers=0

        for worktree in "${WORKTREES[@]}"; do
            IFS=':' read -r name path <<< "${worktree}"
            local worker_info=$(check_worker_activity "${name}" "${path}")
            IFS='|' read -r worker_name activity_level total_recent py_files ts_files sh_files has_report <<< "${worker_info}"

            # 统计活跃Worker数量
            if [[ ${total_recent} -gt 0 ]]; then
                total_active=$((total_active + 1))
            fi
            total_workers=$((total_workers + 1))

            # 显示Worker状态
            echo -e "${worker_name} CLI:"
            echo "  活跃度: ${activity_level}"
            echo "  进度报告: ${has_report} TASK-REPORT.md"
            echo "  最近修改: ${total_recent}个文件 (py:${py_files}, ts:${ts_files}, sh:${sh_files})"
            echo ""
        done

        # 汇总统计
        echo "────────────────────────────────────────────────────────────────"
        echo "📈 活跃度统计"
        echo "────────────────────────────────────────────────────────────────"
        echo ""
        echo "活跃Worker: ${total_active}/${total_workers}"
        local activity_rate=$((total_active * 100 / total_workers))
        echo "活跃率: ${activity_rate}%"
        echo ""

        # 详细文件列表
        for worktree in "${WORKTREES[@]}"; do
            IFS=':' read -r name path <<< "${worktree}"
            echo "────────────────────────────────────────────────────────────────"
            echo "【${name} CLI】详细活动"
            echo "────────────────────────────────────────────────────────────────"
            echo ""
            show_recent_files "${path}" 10
            echo ""
        done

        echo "════════════════════════════════════════════════════════════════"
        echo "报告结束 | Main CLI (Manager) | Phase 7 增强版监控"
        echo "════════════════════════════════════════════════════════════════"

    } | tee "${report_file}"
}

###############################################################################
# 函数: 主监控流程
###############################################################################
main() {
    log "${BLUE}INFO" "═══════════════════════════════════════"
    log "${BLUE}INFO" "Phase 7 增强版进度监控开始"
    log "${BLUE}INFO" "═══════════════════════════════════════"

    # 生成活跃度报告
    log "${BLUE}INFO" "生成基于文件修改时间的活跃度报告..."
    generate_activity_report "${LATEST_REPORT}"

    # 显示摘要
    echo ""
    log "${GREEN}SUCCESS" "增强版监控完成"
    echo ""
    echo "📄 报告位置: ${LATEST_REPORT}"
    echo ""

    log "${BLUE}INFO" "═══════════════════════════════════════"
    log "${BLUE}INFO" "Phase 7 增强版进度监控结束"
    log "${BLUE}INFO" "═══════════════════════════════════════"
}

# 执行主流程
main "$@"
