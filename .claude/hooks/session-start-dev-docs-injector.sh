#!/usr/bin/env bash
#
# ============================================================================
# Claude Code Hook: Dev Docs Context Injector
# ============================================================================
#
# Event: SessionStart
# Purpose: 在新会话启动或恢复时，注入 Dev Docs 的上下文摘要
#
# Reddit 案例设计理念:
#   Claude 的自动压缩会导致上下文丢失，跨会话时"失忆"。
#   解决方案: Dev Docs 三文档系统 (plan.md + context.md + tasks.md)
#   在 SessionStart 时自动注入 context.md 摘要，使 Claude 能够"继续"之前的工作。
#
# 工作原理:
#   1. 检测会话启动类型（startup, resume, clear, compact）
#   2. 查找活动任务目录（.claude/dev/active/*/context.md）
#   3. 读取 context.md 并提取摘要（前 50 行 或 < 200 行）
#   4. 输出摘要到 stdout（SessionStart 的 stdout 会被注入到 Claude！）
#   5. Claude 收到上下文后可以继续之前的任务
#
# 退出码:
#   0: 成功（stdout 会被注入到 Claude 上下文！特例！）
#   1: 警告（显示 stderr 但继续）
#   2: 一般不用于 SessionStart（阻止错误会被忽略）
#
# SessionStart 特有功能:
#   - stdout 会被注入到 Claude
#   - 可以写入 CLAUDE_ENV_FILE 持久化环境变量
#
# Dev Docs 三文档结构:
#   .claude/dev/active/<task-name>/
#   ├── plan.md          # 战略目标和架构决策
#   ├── context.md       # 关键文件、依赖、注意事项（< 200 行）
#   └── tasks.md         # 任务清单（已完成/进行中/待办）
#
# 安装方法:
#   1. chmod +x session-start-dev-docs-injector.sh
#   2. 复制到 .claude/hooks/
#   3. 添加到 settings.json:
#      {
#        "hooks": {
#          "SessionStart": [
#            {
#              "hooks": [{
#                "type": "command",
#                "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start-dev-docs-injector.sh"
#              }],
#              "timeout": 5
#            }
#          ]
#        }
#      }
#
# Timeout 建议: 5 秒（快速读取文件）
#
# 配合使用:
#   - PreCompact hook: pre-compact-dev-docs-snapshot.sh（压缩前保存）
#   - Stop hook: stop-dev-docs-updater.sh（停止前更新）
#   - Slash command: /dev-docs, /dev-docs-update
#
# ============================================================================

set -euo pipefail

# ===== 配置 =====
DEV_DOCS_DIR=".claude/dev/active"
CONTEXT_SUMMARY_LINES=50  # 只注入前 50 行摘要（避免占用太多 tokens）
DEBUG_MODE="${DEV_DOCS_DEBUG:-false}"

# ===== 调试日志函数 =====
debug_log() {
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] $*" >&2
    fi
}

# ===== 读取 stdin JSON =====
INPUT_JSON=$(cat)
SESSION_ID=$(echo "$INPUT_JSON" | jq -r '.session_id // "unknown"')
SOURCE=$(echo "$INPUT_JSON" | jq -r '.source // "unknown"')

debug_log "Dev Docs injector started"
debug_log "Session ID: $SESSION_ID"
debug_log "Source: $SOURCE"

# ===== 检查 Dev Docs 目录是否存在 =====
if [ ! -d "$DEV_DOCS_DIR" ]; then
    debug_log "No Dev Docs directory found at $DEV_DOCS_DIR, skipping injection"
    exit 0
fi

# ===== 查找活动任务（最近修改的 context.md）=====
ACTIVE_TASK=""
CONTEXT_FILE=""

# 查找所有 context.md 文件，按修改时间排序
if [ -d "$DEV_DOCS_DIR" ]; then
    while IFS= read -r file; do
        if [ -f "$file" ]; then
            CONTEXT_FILE="$file"
            ACTIVE_TASK=$(dirname "$file" | xargs basename)
            break
        fi
    done < <(find "$DEV_DOCS_DIR" -name "context.md" -type f -printf '%T@ %p\n' 2>/dev/null | sort -rn | cut -d' ' -f2-)
fi

if [ -z "$CONTEXT_FILE" ]; then
    debug_log "No active task found (no context.md files)"
    exit 0
fi

debug_log "Found active task: $ACTIVE_TASK"
debug_log "Context file: $CONTEXT_FILE"

# ===== 读取 context.md 摘要 =====
if [ ! -f "$CONTEXT_FILE" ]; then
    debug_log "Context file not found: $CONTEXT_FILE"
    exit 0
fi

# 提取前 N 行作为摘要
CONTEXT_SUMMARY=$(head -n "$CONTEXT_SUMMARY_LINES" "$CONTEXT_FILE")
LINE_COUNT=$(wc -l < "$CONTEXT_FILE")

debug_log "Read $LINE_COUNT lines from context.md, using first $CONTEXT_SUMMARY_LINES"

# ===== 构建注入消息 =====
INJECTION_MESSAGE="
═══════════════════════════════════════════════════════════════
 Resuming Task: $ACTIVE_TASK
═══════════════════════════════════════════════════════════════

The following context was saved from previous sessions.
Please review before proceeding.

Context summary (from $CONTEXT_FILE):

$CONTEXT_SUMMARY

"

if [ "$LINE_COUNT" -gt "$CONTEXT_SUMMARY_LINES" ]; then
    INJECTION_MESSAGE="${INJECTION_MESSAGE}
... (showing first $CONTEXT_SUMMARY_LINES of $LINE_COUNT lines)

For full context, see: $CONTEXT_FILE
"
fi

INJECTION_MESSAGE="${INJECTION_MESSAGE}
═══════════════════════════════════════════════════════════════
"

# ===== 输出到 stdout（会被注入到 Claude 上下文）=====
echo "$INJECTION_MESSAGE"

# ===== （可选）设置环境变量（如果提供了 CLAUDE_ENV_FILE）=====
if [ -n "${CLAUDE_ENV_FILE:-}" ] && [ -f "${CLAUDE_ENV_FILE}" ]; then
    debug_log "CLAUDE_ENV_FILE detected: $CLAUDE_ENV_FILE"

    # 检查是否有任务特定的环境变量
    TASK_ENV_FILE="$(dirname "$CONTEXT_FILE")/env.sh"
    if [ -f "$TASK_ENV_FILE" ]; then
        debug_log "Loading task-specific environment from $TASK_ENV_FILE"
        cat "$TASK_ENV_FILE" >> "$CLAUDE_ENV_FILE"
    fi
fi

debug_log "Context injection completed"

exit 0
