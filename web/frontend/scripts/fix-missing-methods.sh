#!/bin/bash

# 修复TypeScript错误 - 添加缺失的辅助方法

FRONTEND_DIR="/opt/claude/mystocks_spec/web/frontend"
VIEWS_DIR="$FRONTEND_DIR/src/views"

echo "=== 修复缺失的辅助方法 ==="

# AlertRulesManagement.vue - 添加getNotificationLevelType方法
echo "修复 AlertRulesManagement.vue..."
if ! grep -q "getNotificationLevelType" "$VIEWS_DIR/monitoring/AlertRulesManagement.vue"; then
  sed -i '/const getNotificationLevelClass/i\
\
const getNotificationLevelType = (level?: string): '"'"'success'"'"' | '"'"'warning'"'"' | '"'"'danger'"'"' | '"'"'info'"'"' => {\
  if (!level) return '"'"'info'"'"'\
  const levelLower = level.toLowerCase()\
  if (levelLower.includes('"'"'high'"'"') || levelLower.includes('"'"'critical'"'"')) {\
    return '"'"'danger'"'"'\
  }\
  if (levelLower.includes('"'"'medium'"'"')) {\
    return '"'"'warning'"'"'\
  }\
  return '"'"'success'"'"'\
}' "$VIEWS_DIR/monitoring/AlertRulesManagement.vue"
fi

echo "✓ 辅助方法添加完成"
