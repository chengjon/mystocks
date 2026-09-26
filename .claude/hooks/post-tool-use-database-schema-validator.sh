#!/usr/bin/env bash
#
# ============================================================================
# Claude Code Hook: Database Schema Validator (MyStocks-Specific)
# ============================================================================
#
# Event: PostToolUse
# Matcher: Edit|Write
# Purpose: 验证数据库架构变更是否符合 MyStocks 双数据库架构规范
#
# MyStocks 双数据库架构规范:
#   TDengine: 高频时序数据（tick 数据、分钟K线）
#   - 超表: tick_data, minute_data
#   - 特点: 极致压缩（20:1），超高写入性能
#
#   PostgreSQL: 所有其他数据（日线、参考数据、元数据、交易数据、衍生数据）
#   - TimescaleDB 混合表: daily_bars, technical_indicators
#   - 标准表: stocks, portfolios, strategies, alerts
#
# 验证规则:
#   ❌ tick 数据不应存储在 PostgreSQL
#   ❌ 分钟K线数据不应存储在 PostgreSQL
#   ❌ 日线数据不应存储在 TDengine（除非特殊需求）
#   ❌ 参考数据不应存储在 TDengine
#   ⚠️ 新建超表需要明确理由
#   ⚠️ 删除超表需要特别警告
#
# 工作原理:
#   1. 从 stdin 读取 tool_input.file_path 和 tool_input.new_string
#   2. 检测是否编辑了数据库相关文件（table_config.yaml, *_adapter.py, database_manager.py）
#   3. 扫描代码中的危险模式（tick 数据写入 PostgreSQL 等）
#   4. 通过 hookSpecificOutput.additionalContext 注入警告给 Claude
#   5. 非阻塞（exit 0），仅警告，不阻止操作
#
# 退出码（符合 Claude 官方规范）:
#   0: 成功（非阻塞），警告通过 additionalContext 注入
#   1: 一般错误（显示 stderr 但继续）
#   2: 阻止（不推荐使用，除非严重架构违规）
#
# JSON 输出格式（使用官方推荐的 hookSpecificOutput.additionalContext）:
#   {
#     "hookSpecificOutput": {
#       "hookEventName": "PostToolUse",
#       "additionalContext": "🔍 DATABASE ARCHITECTURE VALIDATION\n\n⚠️ 检测到潜在架构问题:\n..."
#     }
#   }
#
# 安装方法:
#   1. chmod +x post-tool-use-database-schema-validator.sh
#   2. 复制到 .claude/hooks/
#   3. 添加到 settings.json:
#      {
#        "hooks": {
#          "PostToolUse": [
#            {
#              "matcher": "Edit|Write",
#              "hooks": [{
#                "type": "command",
#                "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-database-schema-validator.sh"
#              }],
#              "timeout": 5
#            }
#          ]
#        }
#      }
#
# Timeout 建议: 5 秒（快速模式匹配）
#
# MyStocks 项目特定规则:
#   - 任何 tick_ 或 minute_ 相关代码应使用 TDengine
#   - 任何 daily_ 相关代码应使用 PostgreSQL
#   - 新建超表应有明确注释说明理由
#
# ============================================================================

set -uo pipefail

# ===== 配置 =====
DEBUG_MODE="${DB_VALIDATOR_DEBUG:-false}"

# ===== 调试日志函数 =====
debug_log() {
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] $*" >&2
    fi
}

# ===== 错误处理函数 =====
error_exit() {
    echo "Error: $*" >&2
    exit 1
}

# ===== 读取 stdin JSON =====
INPUT_JSON=$(cat 2>/dev/null || true)
debug_log "Database validator started"

# ===== 验证 stdin 不为空 =====
if [ -z "$INPUT_JSON" ]; then
    debug_log "Empty stdin, skipping validation"
    exit 0
fi

# ===== 验证 JSON 有效性 =====
if ! echo "$INPUT_JSON" | jq empty 2>/dev/null; then
    debug_log "Invalid JSON received, skipping validation"
    exit 0
fi

# ===== 提取必要字段（使用安全的 jq 调用） =====
TOOL_NAME=$(echo "$INPUT_JSON" | jq -r '.tool_name // "Unknown"' 2>/dev/null || echo "Unknown")
FILE_PATH=$(echo "$INPUT_JSON" | jq -r '.tool_input.file_path // empty' 2>/dev/null || echo "")
NEW_STRING=$(echo "$INPUT_JSON" | jq -r '.tool_input.new_string // empty' 2>/dev/null || echo "")
SESSION_ID=$(echo "$INPUT_JSON" | jq -r '.session_id // "unknown"' 2>/dev/null || echo "unknown")

# ===== 如果没有文件路径或新内容，跳过 =====
if [ -z "$FILE_PATH" ] || [ -z "$NEW_STRING" ]; then
    debug_log "No file_path or new_string found, skipping validation"
    exit 0
fi

# ===== 只检查数据库相关文件 =====
RELEVANT_FILE=false
if [[ "$FILE_PATH" == *"table_config.yaml"* ]] || \
   [[ "$FILE_PATH" == *"adapter.py"* ]] || \
   [[ "$FILE_PATH" == *"database_manager.py"* ]] || \
   [[ "$FILE_PATH" == *"data_access"* ]] || \
   [[ "$FILE_PATH" == *"unified_manager.py"* ]]; then
    RELEVANT_FILE=true
fi

if [ "$RELEVANT_FILE" = "false" ]; then
    debug_log "File $FILE_PATH not database-related, skipping"
    exit 0
fi

debug_log "Validating database changes in: $FILE_PATH"

# ===== 定义危险模式（使用关联数组）=====
declare -A DANGEROUS_PATTERNS=(
    ["tick.*PostgreSQL"]="⚠️ Tick数据应存储在TDengine超表中，不应使用PostgreSQL"
    ["tick_data.*postgres"]="⚠️ Tick数据应存储在TDengine超表中，不应使用PostgreSQL"
    ["minute.*PostgreSQL"]="⚠️ 分钟K线数据应存储在TDengine超表中，不应使用PostgreSQL"
    ["minute_data.*postgres"]="⚠️ 分钟K线数据应存储在TDengine超表中，不应使用PostgreSQL"
    ["daily.*TDengine"]="⚠️ 日线数据通常存储在PostgreSQL，使用TDengine需要特殊理由"
    ["daily_bars.*tdengine"]="⚠️ 日线数据通常存储在PostgreSQL，使用TDengine需要特殊理由"
    ["stocks.*TDengine"]="⚠️ 参考数据（股票列表）应存储在PostgreSQL，不应使用TDengine"
    ["portfolios.*TDengine"]="⚠️ 交易数据（组合）应存储在PostgreSQL，不应使用TDengine"
    ["DROP.*STABLE"]="🚨 危险操作：删除TDengine超表！这将丢失所有时序数据！"
    ["CREATE.*STABLE.*tick"]="ℹ️ 创建新的Tick超表，请确保有明确理由并在注释中说明"
    ["CREATE.*STABLE.*minute"]="ℹ️ 创建新的分钟K线超表，请确保有明确理由并在注释中说明"
)

# ===== 扫描新代码中的危险模式 =====
WARNINGS=""
WARNING_COUNT=0

for pattern in "${!DANGEROUS_PATTERNS[@]}"; do
    if echo "$NEW_STRING" | grep -qiE "$pattern"; then
        WARNING_MSG="${DANGEROUS_PATTERNS[$pattern]}"
        WARNINGS="${WARNINGS}${WARNING_MSG}\n"
        WARNINGS="${WARNINGS}  检测到模式: $pattern\n"
        WARNINGS="${WARNINGS}  位置: $FILE_PATH\n\n"
        WARNING_COUNT=$((WARNING_COUNT + 1))
        debug_log "Found dangerous pattern: $pattern"
    fi
done

# ===== 如果没有警告，正常退出 =====
if [ "$WARNING_COUNT" -eq 0 ]; then
    debug_log "No database architecture issues detected"
    exit 0
fi

# ===== 构建警告消息（注入给 Claude）=====
CONTEXT_MESSAGE="🔍 DATABASE ARCHITECTURE VALIDATION

检测到 $WARNING_COUNT 个潜在的数据库架构问题:

$WARNINGS

📖 MyStocks 双数据库架构规范:
  - TDengine: Tick数据、分钟K线（超表: tick_data, minute_data）
  - PostgreSQL: 日线数据、参考数据、元数据、交易数据（标准表 + TimescaleDB混合表）

💡 建议:
  1. 检查数据分类是否正确
  2. 确认使用的数据库符合架构规范
  3. 如有特殊需求，请在注释中明确说明理由

参考: docs/standards/FILE_ORGANIZATION_RULES.md
      CLAUDE.md (MyStocks 架构说明)
"

# ===== 输出 JSON（通过 additionalContext 注入给 Claude）=====
# 转义特殊字符
ESCAPED_CONTEXT=$(echo "$CONTEXT_MESSAGE" | jq -Rs .)

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": $ESCAPED_CONTEXT
  }
}
EOF

debug_log "Database validation warnings sent to Claude"

# 非阻塞成功退出
exit 0
