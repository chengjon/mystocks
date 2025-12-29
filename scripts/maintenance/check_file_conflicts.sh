#!/bin/bash
# 检查Git Worktree文件冲突
# 使用方法：bash scripts/maintenance/check_file_conflicts.sh

echo "=== Git Worktree文件冲突检测 ==="
echo ""

OWNERSHIP_FILE="/opt/claude/mystocks_spec/.FILE_OWNERSHIP"
CONFLICTS_FOUND=0

for cli_path in /opt/claude/mystocks_phase*/; do
  if [ -d "$cli_path" ]; then
    cli_name=$(basename "$cli_path")
    echo "## 检查 $cli_name"

    cd "$cli_path"

    # 检查已修改但未提交的文件
    git diff --name-only | while read file; do
      # 跳过已删除的文件
      [ ! -f "$file" ] && continue

      # 检查文件所有权
      owner=$(grep "^$file:" "$OWNERSHIP_FILE" 2>/dev/null | cut -d: -f2 | cut -d: -f1)

      if [ -z "$owner" ]; then
        # 未知所有权，默认归主CLI
        owner="main"
      fi

      # 如果文件不属于当前CLI
      if [ "$owner" != "$cli_name" ] && [ "$owner" != "main+clis" ]; then
        echo "  ⚠️  潜在冲突: $file"
        echo "     拥有者: $owner"
        echo "     修改者: $cli_name"
        CONFLICTS_FOUND=$((CONFLICTS_FOUND + 1))
      fi
    done

    echo ""
  fi
done

if [ $CONFLICTS_FOUND -eq 0 ]; then
  echo "✅ 未发现文件冲突"
  exit 0
else
  echo "🚨 发现 $CONFLICTS_FOUND 个潜在文件冲突"
  echo ""
  echo "建议："
  echo "1. 查看文件所有权映射: cat /opt/claude/mystocks_spec/.FILE_OWNERSHIP"
  echo "2. 与文件拥有者CLI协调"
  echo "3. 或通过主CLI申请修改权限"
  exit 1
fi
