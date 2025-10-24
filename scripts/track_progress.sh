#!/bin/bash
# 架构优化进度跟踪工具
# 用途: 自动统计tasks.md的任务完成情况

TASKS_FILE="specs/002-arch-optimization/tasks.md"
REPORT_DIR="specs/002-arch-optimization/progress"

# 创建报告目录
mkdir -p "$REPORT_DIR"

# 生成时间戳
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
DATE=$(date +"%Y%m%d")

echo "========================================"
echo "架构优化进度报告"
echo "生成时间: $TIMESTAMP"
echo "========================================"
echo ""

# 统计总任务数
TOTAL_TASKS=$(grep -c "^- \[ \]" "$TASKS_FILE")
COMPLETED_TASKS=$(grep -c "^- \[x\]" "$TASKS_FILE")
PENDING_TASKS=$((TOTAL_TASKS - COMPLETED_TASKS))
COMPLETION_RATE=$(echo "scale=2; $COMPLETED_TASKS * 100 / $TOTAL_TASKS" | bc)

echo "📊 总体进度"
echo "----------------------------------------"
echo "总任务数:     $TOTAL_TASKS"
echo "已完成:       $COMPLETED_TASKS"
echo "待完成:       $PENDING_TASKS"
echo "完成率:       ${COMPLETION_RATE}%"
echo ""

# 绘制进度条
PROGRESS_BAR_LENGTH=40
FILLED_LENGTH=$(echo "scale=0; $COMPLETED_TASKS * $PROGRESS_BAR_LENGTH / $TOTAL_TASKS" | bc)
BAR=$(printf '█%.0s' $(seq 1 $FILLED_LENGTH))
EMPTY=$(printf '░%.0s' $(seq 1 $((PROGRESS_BAR_LENGTH - FILLED_LENGTH))))
echo "进度条: [$BAR$EMPTY] ${COMPLETION_RATE}%"
echo ""

# 按阶段统计
echo "📋 各阶段进度"
echo "----------------------------------------"

phases=(
    "Phase 1: Setup"
    "Phase 2: Foundational"
    "Phase 3: User Story 1"
    "Phase 4: User Story 2"
    "Phase 5: User Story 3"
    "Phase 6: User Story 4"
    "Phase 7: User Story 5"
    "Phase 8: User Story 6"
    "Phase 9: User Story 7"
    "Phase 10: User Story 8"
    "Phase 11: User Story 9"
    "Phase 12: Polish"
)

for phase in "${phases[@]}"; do
    # 提取阶段标题的下一部分，直到下一个##或文件结尾
    phase_section=$(awk "/## $phase/,/^## /" "$TASKS_FILE")

    phase_total=$(echo "$phase_section" | grep -c "^- \[")
    phase_completed=$(echo "$phase_section" | grep -c "^- \[x\]")

    if [ "$phase_total" -gt 0 ]; then
        phase_rate=$(echo "scale=1; $phase_completed * 100 / $phase_total" | bc)
        printf "%-28s: %2d/%2d (%.1f%%)\n" "$phase" "$phase_completed" "$phase_total" "$phase_rate"
    fi
done
echo ""

# 识别当前阶段（第一个有未完成任务的阶段）
echo "🎯 当前焦点"
echo "----------------------------------------"

current_phase=""
for phase in "${phases[@]}"; do
    phase_section=$(awk "/## $phase/,/^## /" "$TASKS_FILE")
    phase_pending=$(echo "$phase_section" | grep -c "^- \[ \]")

    if [ "$phase_pending" -gt 0 ]; then
        current_phase="$phase"
        break
    fi
done

if [ -n "$current_phase" ]; then
    echo "当前阶段: $current_phase"

    # 显示当前阶段的前5个未完成任务
    echo ""
    echo "待完成任务（前5个）:"
    awk "/## $current_phase/,/^## /" "$TASKS_FILE" | grep "^- \[ \]" | head -5 | sed 's/^/  /'
else
    echo "🎉 所有任务已完成！"
fi
echo ""

# 计算预计完成时间
if [ "$PENDING_TASKS" -gt 0 ]; then
    # 假设平均每个任务0.5天
    ESTIMATED_DAYS=$(echo "scale=1; $PENDING_TASKS * 0.5" | bc)
    echo "📅 预计剩余时间"
    echo "----------------------------------------"
    echo "预计还需: ${ESTIMATED_DAYS} 个工作日"

    # 计算预计完成日期（仅工作日）
    COMPLETION_DATE=$(date -d "+${ESTIMATED_DAYS%.*} days" +"%Y-%m-%d")
    echo "预计完成: $COMPLETION_DATE"
    echo ""
fi

# 生成JSON报告
cat > "$REPORT_DIR/progress_${DATE}.json" << EOF
{
  "timestamp": "$TIMESTAMP",
  "total_tasks": $TOTAL_TASKS,
  "completed_tasks": $COMPLETED_TASKS,
  "pending_tasks": $PENDING_TASKS,
  "completion_rate": $COMPLETION_RATE,
  "current_phase": "$current_phase",
  "estimated_days_remaining": ${ESTIMATED_DAYS:-0}
}
EOF

echo "📄 报告已保存到: $REPORT_DIR/progress_${DATE}.json"
echo ""

# 可选: 生成趋势图（需要之前的报告）
if [ $(ls -1 "$REPORT_DIR"/progress_*.json 2>/dev/null | wc -l) -gt 1 ]; then
    echo "📈 进度趋势（最近7天）"
    echo "----------------------------------------"

    for report in $(ls -t "$REPORT_DIR"/progress_*.json | head -7); do
        report_date=$(basename "$report" .json | sed 's/progress_//')
        report_rate=$(jq -r '.completion_rate' "$report" 2>/dev/null)

        if [ -n "$report_rate" ]; then
            printf "%s: %.1f%%\n" "$report_date" "$report_rate"
        fi
    done
    echo ""
fi

echo "========================================"
echo "提示: 使用以下命令更新任务状态"
echo "  vim $TASKS_FILE"
echo "  # 将 [ ] 改为 [x] 标记任务完成"
echo "========================================"
