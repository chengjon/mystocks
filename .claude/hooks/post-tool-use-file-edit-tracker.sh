#!/usr/bin/env bash
#
# ============================================================================
# Claude Code Hook: File Edit Tracker
# ============================================================================
#
# Event: PostToolUse
# Matcher: Edit|Write
# Purpose: 记录所有文件编辑操作，供后续 Stop hook（构建检查器）使用
#
# Reddit 案例设计理念:
#   不要在每次编辑后立即运行构建（会产生噪声），而是：
#   1. PostToolUse: 非阻塞记录编辑文件到日志
#   2. Stop: 批量运行构建，检测所有错误
#
#   优点：允许临时代码破坏，减少构建次数，只在完成时做质量门禁
#
# 工作原理:
#   1. 从 stdin 读取 tool_input.file_path 和 tool_response
#   2. 记录到 ~/.claude/edit_log.jsonl（JSONL 格式，每行一个 JSON）
#   3. 记录信息：时间戳、文件路径、工具名称、会话 ID、仓库路径
#   4. 非阻塞（exit 0），不干扰工作流
#
# 退出码:
#   0: 成功（非阻塞）
#   1: 警告（显示 stderr 但继续）
#   2: 阻止（一般不使用，除非严重错误）
#
# 日志格式 (.claude/edit_log.jsonl):
#   {"timestamp":"2025-11-07T10:30:45Z","file_path":"src/index.py","tool":"Edit","session_id":"abc123","repo":"/opt/claude/mystocks_spec"}
#
# 清理策略:
#   日志文件自动保留最后 10000 条记录
#   SessionEnd hook 会在会话结束时清理当前会话的日志
#
# 安装方法:
#   1. chmod +x post-tool-use-file-edit-tracker.sh
#   2. 复制到 .claude/hooks/
#   3. 添加到 settings.json:
#      {
#        "hooks": {
#          "PostToolUse": [
#            {
#              "matcher": "Edit|Write",
#              "hooks": [{
#                "type": "command",
#                "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-file-edit-tracker.sh"
#              }],
#              "timeout": 3
#            }
#          ]
#        }
#      }
#
# Timeout 建议: 3 秒（只是记录，应该很快）
#
# 配合使用:
#   - Stop hook: stop-build-checker.sh（读取此日志并运行构建）
#
# ============================================================================

set -euo pipefail

# ===== 配置 =====
# 使用项目级日志文件（而不是全局 ~/.claude/）
EDIT_LOG_FILE="${CLAUDE_EDIT_LOG:-.claude/edit_log.jsonl}"
DEBUG_MODE="${EDIT_TRACKER_DEBUG:-false}"

# ===== 调试日志函数 =====
debug_log() {
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] $*" >&2
    fi
}

# ===== 确保日志目录存在 =====
mkdir -p "$(dirname "$EDIT_LOG_FILE")"

# ===== 读取 stdin JSON =====
INPUT_JSON=$(cat)
debug_log "Received input JSON"

# ===== 提取必要字段 =====
TOOL_NAME=$(echo "$INPUT_JSON" | jq -r '.tool_name // "Unknown"')
FILE_PATH=$(echo "$INPUT_JSON" | jq -r '.tool_input.file_path // empty')
SESSION_ID=$(echo "$INPUT_JSON" | jq -r '.session_id // "unknown"')
CWD=$(echo "$INPUT_JSON" | jq -r '.cwd // "unknown"')

# ===== 如果没有文件路径，跳过（可能是其他类型的工具）=====
if [ -z "$FILE_PATH" ]; then
    debug_log "No file_path found, skipping tracking"
    exit 0
fi

# ===== 只跟踪 Edit 和 Write 工具 =====
if [ "$TOOL_NAME" != "Edit" ] && [ "$TOOL_NAME" != "Write" ]; then
    debug_log "Tool $TOOL_NAME is not Edit or Write, skipping"
    exit 0
fi

# ===== 检查工具是否成功 =====
SUCCESS=$(echo "$INPUT_JSON" | jq -r '.tool_response.success // true')
if [ "$SUCCESS" != "true" ]; then
    debug_log "Tool execution failed, skipping tracking"
    exit 0
fi

# ===== 获取时间戳 =====
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# ===== 解析仓库路径（项目根目录）=====
# 如果文件路径是相对路径，基于 cwd 计算绝对路径
if [[ "$FILE_PATH" != /* ]]; then
    ABSOLUTE_PATH="$CWD/$FILE_PATH"
else
    ABSOLUTE_PATH="$FILE_PATH"
fi

# 尝试找到 git 仓库根目录
REPO_ROOT="$CWD"
if command -v git &> /dev/null; then
    if DETECTED_REPO=$(cd "$(dirname "$ABSOLUTE_PATH")" 2>/dev/null && git rev-parse --show-toplevel 2>/dev/null); then
        REPO_ROOT="$DETECTED_REPO"
    fi
fi

debug_log "Tracking edit: $FILE_PATH in repo $REPO_ROOT"

# ===== 构建日志条目 =====
LOG_ENTRY=$(jq -n \
    --arg ts "$TIMESTAMP" \
    --arg fp "$FILE_PATH" \
    --arg tool "$TOOL_NAME" \
    --arg sid "$SESSION_ID" \
    --arg repo "$REPO_ROOT" \
    --arg abs "$ABSOLUTE_PATH" \
    '{
        timestamp: $ts,
        file_path: $fp,
        absolute_path: $abs,
        tool: $tool,
        session_id: $sid,
        repo: $repo
    }')

# ===== 写入日志文件（追加）=====
echo "$LOG_ENTRY" >> "$EDIT_LOG_FILE"

# ===== 限制日志文件大小（保留最后 10000 条）=====
if [ -f "$EDIT_LOG_FILE" ]; then
    LINE_COUNT=$(wc -l < "$EDIT_LOG_FILE")
    if [ "$LINE_COUNT" -gt 10000 ]; then
        debug_log "Log file has $LINE_COUNT lines, trimming to last 10000"
        tail -n 10000 "$EDIT_LOG_FILE" > "$EDIT_LOG_FILE.tmp"
        mv "$EDIT_LOG_FILE.tmp" "$EDIT_LOG_FILE"
    fi
fi

debug_log "Successfully logged edit to $EDIT_LOG_FILE"

# 非阻塞成功退出
exit 0
