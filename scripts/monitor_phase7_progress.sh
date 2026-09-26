#!/bin/bash

###############################################################################
# Phase 7 多CLI并行开发 - 自动化进度监控脚本
#
# 功能:
#   - 每小时检查所有Worker CLI的TASK-REPORT.md
#   - 每2小时生成汇总进度报告
#   - 检测阻塞问题并立即告警
#   - 生成Main CLI决策所需的简洁报告
#
# 使用方式:
#   bash scripts/monitor_phase7_progress.sh [--check-only]
#
# 作者: Main CLI (Manager)
# 版本: v1.0
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
LATEST_REPORT="${REPORT_DIR}/latest_progress.txt"
HOURLY_REPORT="${REPORT_DIR}/hourly_${DATE_ONLY}.txt"

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
# 函数: 检查单个Worker CLI的进度
###############################################################################
check_worker_progress() {
    local worker_name=$1
    local worktree_path=$2
    local task_report="${worktree_path}/TASK-REPORT.md"

    # 检查TASK-REPORT.md是否存在
    if [[ ! -f "${task_report}" ]]; then
        log "${YELLOW}WARN" "${worker_name}: TASK-REPORT.md 尚未创建"
        echo "${worker_name}|NOT_STARTED|0|0|TASK-REPORT.md尚未创建"
        return 0
    fi

    # 提取关键信息
    local current_stage=$(grep -E "^当前阶段:" "${task_report}" | sed 's/当前阶段: //' || echo "未知")
    local current_task=$(grep -E "^当前任务:" "${task_report}" | sed 's/当前任务: //' || echo "未知")
    local progress=$(grep -E "^总体进度:" "${task_report}" | sed 's/总体进度: //' || echo "0%")
    local last_update=$(grep -E "^最后更新:" "${task_report}" | sed 's/最后更新: //' || echo "未知")
    local blocking_issues=$(grep -E "🔴 阻塞级" "${task_report}" | wc -l)

    # 检查是否有阻塞问题
    if [[ ${blocking_issues} -gt 0 ]]; then
        log "${RED}ALERT" "${worker_name}: 发现 ${blocking_issues} 个阻塞问题！"
        echo "${worker_name}|BLOCKED|${current_stage}|${progress}|${current_task}|有${blocking_issues}个阻塞问题"
    else
        log "${GREEN}INFO" "${worker_name}: 阶段${current_stage} - ${progress} - ${current_task}"
        echo "${worker_name}|IN_PROGRESS|${current_stage}|${progress}|${current_task}|最后更新: ${last_update}"
    fi
}

###############################################################################
# 函数: 生成进度报告
###############################################################################
generate_progress_report() {
    local report_file=$1
    local is_summary=${2:-false}

    {
        echo "════════════════════════════════════════════════════════════════"
        echo "        Phase 7 多CLI并行开发 - 进度监控报告"
        echo "════════════════════════════════════════════════════════════════"
        echo ""
        echo "生成时间: ${TIMESTAMP}"
        echo "报告类型: $(${is_summary} && echo "汇总报告" || echo "实时报告")"
        echo ""

        # 检查所有Worker CLI
        echo "────────────────────────────────────────────────────────────────"
        echo "📊 Worker CLI 进度总览"
        echo "────────────────────────────────────────────────────────────────"
        echo ""

        local total_progress=0
        local worker_count=0
        local blocked_workers=()

        for worktree in "${WORKTREES[@]}"; do
            IFS=':' read -r name path <<< "${worktree}"
            local worker_info=$(check_worker_progress "${name}" "${path}")
            IFS='|' read -r status_name status stage progress task message <<< "${worker_info}"

            # 计算总进度（用于汇总报告）
            if ${is_summary}; then
                # 提取进度百分比
                local progress_num=$(echo "${progress}" | grep -oE '[0-9]+' || echo "0")
                total_progress=$((total_progress + progress_num))
                worker_count=$((worker_count + 1))
            fi

            # 显示Worker状态
            case "${status}" in
                "NOT_STARTED")
                    echo -e "${YELLOW}⏳ ${status_name}${NC}: ${message}"
                    ;;
                "BLOCKED")
                    echo -e "${RED}🔴 ${status_name}${NC}: 阶段${stage} - ${message}"
                    blocked_workers+=("${status_name}")
                    ;;
                "IN_PROGRESS")
                    echo -e "${GREEN}✅ ${status_name}${NC}: 阶段${stage} - ${progress} - ${task}"
                    ;;
            esac
            echo ""
        done

        # 汇总报告附加信息
        if ${is_summary}; then
            local avg_progress=$((total_progress / worker_count))
            echo "────────────────────────────────────────────────────────────────"
            echo "📈 整体进度统计"
            echo "────────────────────────────────────────────────────────────────"
            echo ""
            echo "平均进度: ${avg_progress}%"
            echo "活跃Worker: ${worker_count}个"
            echo "阻塞Worker: ${#blocked_workers[@]}个"

            if [[ ${#blocked_workers[@]} -gt 0 ]]; then
                echo ""
                echo -e "${RED}⚠️  需要主CLI介入的Worker: ${blocked_workers[*]}${NC}"
            else
                echo ""
                echo -e "${GREEN}✅ 所有Worker正常执行中${NC}"
            fi
            echo ""
        fi

        # 最近更新日志（从TASK-REPORT.md提取）
        echo "────────────────────────────────────────────────────────────────"
        echo "📝 最近更新日志"
        echo "────────────────────────────────────────────────────────────────"
        echo ""

        for worktree in "${WORKTREES[@]}"; do
            IFS=':' read -r name path <<< "${worktree}"
            local task_report="${path}/TASK-REPORT.md"

            if [[ -f "${task_report}" ]]; then
                echo "【${name}】"
                # 提取最后3条更新日志
                grep -A 2 "^- " "${task_report}" | tail -6 | sed 's/^--$//'
                echo ""
            fi
        done

        echo "════════════════════════════════════════════════════════════════"
        echo "报告结束 | Main CLI (Manager) | Phase 7 多CLI并行开发"
        echo "════════════════════════════════════════════════════════════════"

    } | tee "${report_file}"
}

###############################################################################
# 函数: 主监控流程
###############################################################################
main() {
    local check_only=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --check-only)
                check_only=true
                shift
                ;;
            *)
                echo "未知参数: $1"
                echo "使用方式: $0 [--check-only]"
                exit 1
                ;;
        esac
    done

    log "${BLUE}INFO" "═══════════════════════════════════════"
    log "${BLUE}INFO" "Phase 7 进度监控开始"
    log "${BLUE}INFO" "═══════════════════════════════════════"

    # 生成实时报告
    log "${BLUE}INFO" "生成实时进度报告..."
    generate_progress_report "${LATEST_REPORT}" false

    # 如果不是check-only模式，生成汇总报告
    if ! ${check_only}; then
        log "${BLUE}INFO" "生成汇总进度报告..."
        generate_progress_report "${HOURLY_REPORT}" true

        # 显示摘要
        echo ""
        log "${GREEN}SUCCESS" "进度监控完成"
        echo ""
        echo "📄 报告位置:"
        echo "   - 实时报告: ${LATEST_REPORT}"
        echo "   - 汇总报告: ${HOURLY_REPORT}"
        echo ""

        # 检查是否有阻塞问题
        local blocking_count=$(grep -c "🔴" "${LATEST_REPORT}" || echo "0")
        if [[ ${blocking_count} -gt 0 ]]; then
            log "${RED}ALERT" "发现 ${blocking_count} 个阻塞问题，需要主CLI立即介入！"
            exit 1
        fi
    fi

    log "${BLUE}INFO" "═══════════════════════════════════════"
    log "${BLUE}INFO" "Phase 7 进度监控结束"
    log "${BLUE}INFO" "═══════════════════════════════════════"
}

# 执行主流程
main "$@"
