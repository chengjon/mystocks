#!/bin/bash
# ===========================================
# Worker CLI 进度监控脚本
# ===========================================
# 用途: 非侵入式监控所有Worker CLI的工作进度
# 数据来源: README.md文件 + Git提交历史
# 运行频率: 每2小时自动运行一次
# ===========================================

set -euo pipefail

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Worktree配置 (格式: "路径:CLI名称:优先级")
WORKTREES=(
  "/opt/claude/mystocks_phase3_frontend:CLI-1:Round 1"
  "/opt/claude/mystocks_phase6_api_contract:CLI-2:Round 1 (最高优先级)"
  "/opt/claude/mystocks_phase6_monitoring:CLI-5:Round 1"
  "/opt/claude/mystocks_phase6_quality:CLI-6:Round 1 (贯穿始终)"
)

# Round 2 worktrees (将在Day 15添加)
ROUND2_WORKTREES=(
  "/opt/claude/mystocks_phase4_complete:CLI-3:Round 2"
  "/opt/claude/mystocks_phase5_ai_screening:CLI-4:Round 2"
)

# 时间阈值 (秒)
YELLOW_ALERT_THRESHOLD=$((24 * 3600))  # 24小时
RED_ALERT_THRESHOLD=$((48 * 3600))      # 48小时

# 当前时间戳
CURRENT_TIME=$(date +%s)

# 报告文件
REPORT_FILE="/tmp/mystocks_progress_$(date +%Y%m%d_%H%M%S).txt"

echo "==========================================="
echo "  Worker CLI 进度监控"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "==========================================="
echo ""

# 检查单个worktree的进度
check_worktree() {
  local worktree_path="$1"
  local cli_name="$2"
  local priority="$3"

  echo "-------------------------------------------"
  echo "## $cli_name ($priority)"
  echo "   路径: $worktree_path"

  # 检查worktree是否存在
  if [ ! -d "$worktree_path" ]; then
    echo -e "   ${RED}⚠️ 状态: 未创建${NC}"
    return
  fi

  # 检查README更新时间
  if [ -f "$worktree_path/README.md" ]; then
    readme_mtime=$(stat -c %Y "$worktree_path/README.md" 2>/dev/null || echo 0)
    time_diff=$((CURRENT_TIME - readme_mtime))

    last_update=$(stat -c %y "$worktree_path/README.md" | cut -d'.' -f1)
    echo "   📄 README更新: $last_update"

    # 时间预警
    if [ $time_diff -gt $RED_ALERT_THRESHOLD ]; then
      echo -e "   ${RED}🔴 红色预警: README超过48小时未更新!${NC}"
    elif [ $time_diff -gt $YELLOW_ALERT_THRESHOLD ]; then
      echo -e "   ${YELLOW}🟡 黄色预警: README超过24小时未更新${NC}"
    else
      echo -e "   ${GREEN}✅ 状态: 活跃${NC}"
    fi

    # 提取进度信息
    if grep -q "## 进度更新" "$worktree_path/README.md"; then
      echo "   📊 进度摘要:"
      sed -n '/## 进度更新/,/^##/p' "$worktree_path/README.md" | head -n 10 | sed 's/^/      /'
    else
      echo "   ℹ️  进度信息: 尚未开始记录进度"
    fi
  else
    echo -e "   ${RED}⚠️ README不存在${NC}"
  fi

  # 检查Git提交
  if [ -d "$worktree_path/.git" ]; then
    cd "$worktree_path" || return

    # 最近一次提交
    last_commit=$(git log -1 --format="%h - %s (%ar)" 2>/dev/null || echo "无提交记录")
    echo "   🔧 最后提交: $last_commit"

    # 提交统计
    commit_count=$(git rev-list --count HEAD 2>/dev/null || echo 0)
    echo "   📈 总提交数: $commit_count"

    # 未提交的修改
    if git diff --quiet && git diff --cached --quiet; then
      echo -e "   ${GREEN}✔ 工作区: 干净${NC}"
    else
      modified_count=$(git status --short | wc -l)
      echo -e "   ${YELLOW}⚠ 工作区: 有$modified_count个修改未提交${NC}"
    fi

    cd - > /dev/null || return
  fi

  echo ""
}

# 主监控逻辑
echo "=== Round 1 Worker CLIs ==="
echo ""

for item in "${WORKTREES[@]}"; do
  IFS=':' read -r worktree cli_name priority <<< "$item"
  check_worktree "$worktree" "$cli_name" "$priority"
done

# 检查Round 2是否应该启动（根据当前日期判断）
echo "-------------------------------------------"
echo "## Round 2 Worker CLIs"
echo "   启动条件: CLI-2 (API契约) 完成"
echo ""

for item in "${ROUND2_WORKTREES[@]}"; do
  IFS=':' read -r worktree cli_name priority <<< "$item"

  if [ -d "$worktree" ]; then
    check_worktree "$worktree" "$cli_name" "$priority"
  else
    echo "   $cli_name: ⏳ 等待Round 1完成"
    echo ""
  fi
done

echo "==========================================="
echo "  监控完成"
echo "==========================================="
echo ""

# 生成简化报告
{
  echo "# MyStocks Multi-CLI Progress Report"
  echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
  echo ""
  echo "## Summary"

  active_count=0
  warning_count=0
  alert_count=0

  for item in "${WORKTREES[@]}"; do
    IFS=':' read -r worktree cli_name priority <<< "$item"

    if [ -f "$worktree/README.md" ]; then
      readme_mtime=$(stat -c %Y "$worktree/README.md" 2>/dev/null || echo 0)
      time_diff=$((CURRENT_TIME - readme_mtime))

      if [ $time_diff -gt $RED_ALERT_THRESHOLD ]; then
        alert_count=$((alert_count + 1))
      elif [ $time_diff -gt $YELLOW_ALERT_THRESHOLD ]; then
        warning_count=$((warning_count + 1))
      else
        active_count=$((active_count + 1))
      fi
    fi
  done

  echo "- Active CLIs (< 24h): $active_count"
  echo "- Warning CLIs (24-48h): $warning_count"
  echo "- Alert CLIs (> 48h): $alert_count"

} > "$REPORT_FILE"

echo "📊 详细报告已保存: $REPORT_FILE"
echo ""

# 如果有预警，返回非零退出码（可用于告警集成）
if [ $warning_count -gt 0 ] || [ $alert_count -gt 0 ]; then
  exit 1
fi

exit 0
