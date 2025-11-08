#!/usr/bin/env bash
#
# ============================================================================
# Claude Code Hook: Build Checker (Quality Gate)
# ============================================================================
#
# Event: Stop
# Purpose: 在 Claude 完成响应前，检查所有受影响仓库的构建状态
#
# Reddit 案例核心设计:
#   这是"零错误容忍"策略的核心组件，与 PostToolUse file-edit-tracker 配合使用：
#   1. PostToolUse: 非阻塞记录编辑文件
#   2. Stop: 批量运行构建，若错误 ≥5 则阻断 Claude 停止
#
#   结果: Reddit 团队 6 个月零错误记录（0 TypeScript 编译错误流入生产）
#
# 工作原理:
#   1. 读取 ~/.claude/edit_log.jsonl，找出本会话编辑的所有文件
#   2. 按仓库分组（同一仓库的文件一起构建）
#   3. 针对每个受影响仓库运行构建命令
#   4. 收集所有错误（TypeScript 错误、ESLint 错误等）
#   5. 如果错误 ≥ 阈值（默认 5），阻断 Stop 并建议 Claude 修复
#
# 退出码:
#   0: 构建成功或错误 < 阈值（允许停止）
#   2: 构建失败且错误 ≥ 阈值（阻止停止，要求 Claude 修复）
#
# JSON 输出格式（阻断时）:
#   {
#     "decision": "block",
#     "reason": "Found 7 TypeScript errors in 3 files. Run /build-and-fix or review manually."
#   }
#
# 配置文件（.claude/build-checker.json）:
#   {
#     "errorThreshold": 5,
#     "repos": {
#       "/home/user/project": {
#         "buildCommand": "pnpm build",
#         "testCommand": "pnpm test",  // 可选
#         "skipPatterns": ["*.test.ts", "*.spec.ts"]  // 可选
#       }
#     }
#   }
#
# 安装方法:
#   1. chmod +x stop-build-checker.sh
#   2. 复制到 .claude/hooks/
#   3. 创建 .claude/build-checker.json 配置
#   4. 添加到 settings.json:
#      {
#        "hooks": {
#          "Stop": [
#            {
#              "hooks": [{
#                "type": "command",
#                "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/stop-build-checker.sh"
#              }],
#              "timeout": 120
#            }
#          ]
#        }
#      }
#
# Timeout 建议: 120 秒（构建可能需要时间，根据项目大小调整）
#
# 配合使用:
#   - PostToolUse hook: post-tool-use-file-edit-tracker.sh
#   - Slash command: /build-and-fix（当错误 ≥5 时调用 build-error-resolver agent）
#
# ============================================================================

set -euo pipefail

# ===== 配置 =====
EDIT_LOG_FILE="${CLAUDE_EDIT_LOG:-$HOME/.claude/edit_log.jsonl}"
BUILD_CONFIG_FILE=".claude/build-checker.json"
DEFAULT_ERROR_THRESHOLD=5
DEBUG_MODE="${BUILD_CHECKER_DEBUG:-false}"

# ===== 调试日志函数 =====
debug_log() {
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] $*" >&2
    fi
}

# ===== 读取 stdin JSON（虽然 Stop 事件没有太多有用字段）=====
INPUT_JSON=$(cat)
SESSION_ID=$(echo "$INPUT_JSON" | jq -r '.session_id // "unknown"')

debug_log "Build checker started for session: $SESSION_ID"

# ===== 检查编辑日志是否存在 =====
if [ ! -f "$EDIT_LOG_FILE" ]; then
    debug_log "No edit log found at $EDIT_LOG_FILE, skipping build check"
    exit 0
fi

# ===== 提取本会话的编辑记录 =====
EDITED_FILES=$(jq -r --arg sid "$SESSION_ID" 'select(.session_id == $sid) | .repo' "$EDIT_LOG_FILE" 2>/dev/null || echo "")

if [ -z "$EDITED_FILES" ]; then
    debug_log "No files edited in this session, skipping build check"
    exit 0
fi

# ===== 获取受影响的仓库列表（去重）=====
AFFECTED_REPOS=$(echo "$EDITED_FILES" | sort -u)
REPO_COUNT=$(echo "$AFFECTED_REPOS" | wc -l)

debug_log "Found $REPO_COUNT affected repositories"

# ===== 读取构建配置 =====
ERROR_THRESHOLD=$DEFAULT_ERROR_THRESHOLD
REPO_CONFIGS="{}"

if [ -f "$BUILD_CONFIG_FILE" ]; then
    debug_log "Loading build configuration from $BUILD_CONFIG_FILE"
    BUILD_CONFIG=$(cat "$BUILD_CONFIG_FILE")

    if ! echo "$BUILD_CONFIG" | jq empty 2>/dev/null; then
        echo "Warning: $BUILD_CONFIG_FILE contains invalid JSON, using defaults" >&2
    else
        ERROR_THRESHOLD=$(echo "$BUILD_CONFIG" | jq -r '.errorThreshold // 5')
        REPO_CONFIGS=$(echo "$BUILD_CONFIG" | jq -r '.repos // {}')
    fi
else
    debug_log "No build configuration found, using default settings"
fi

debug_log "Error threshold: $ERROR_THRESHOLD"

# ===== 运行构建并收集错误 =====
TOTAL_ERRORS=0
ERROR_SUMMARY=""

while IFS= read -r repo; do
    if [ -z "$repo" ] || [ ! -d "$repo" ]; then
        continue
    fi

    debug_log "Checking repository: $repo"

    # 获取该仓库的构建命令
    BUILD_CMD=$(echo "$REPO_CONFIGS" | jq -r --arg repo "$repo" '.[$repo].buildCommand // empty')

    if [ -z "$BUILD_CMD" ]; then
        # 尝试检测构建命令
        if [ -f "$repo/package.json" ]; then
            if jq -e '.scripts.build' "$repo/package.json" &>/dev/null; then
                BUILD_CMD="npm run build"
            elif jq -e '.scripts.compile' "$repo/package.json" &>/dev/null; then
                BUILD_CMD="npm run compile"
            fi
        elif [ -f "$repo/tsconfig.json" ]; then
            BUILD_CMD="tsc --noEmit"
        fi
    fi

    if [ -z "$BUILD_CMD" ]; then
        debug_log "  No build command found for $repo, skipping"
        continue
    fi

    debug_log "  Running: $BUILD_CMD"

    # 运行构建（捕获输出）
    if BUILD_OUTPUT=$(cd "$repo" && eval "$BUILD_CMD" 2>&1); then
        debug_log "  ✓ Build succeeded"
    else
        # 构建失败，解析错误
        ERROR_COUNT=$(echo "$BUILD_OUTPUT" | grep -c "error TS" || echo 0)

        if [ "$ERROR_COUNT" -eq 0 ]; then
            # 尝试其他错误模式
            ERROR_COUNT=$(echo "$BUILD_OUTPUT" | grep -ciE "(error|failed)" || echo 0)
        fi

        TOTAL_ERRORS=$((TOTAL_ERRORS + ERROR_COUNT))
        debug_log "  ✗ Build failed with $ERROR_COUNT errors"

        # 提取前 3 个错误消息
        ERROR_PREVIEW=$(echo "$BUILD_OUTPUT" | grep -m 3 "error" || echo "")
        ERROR_SUMMARY="${ERROR_SUMMARY}Repo: $repo ($ERROR_COUNT errors)\n$ERROR_PREVIEW\n\n"
    fi
done <<< "$AFFECTED_REPOS"

# ===== 决策：是否阻断 Stop =====
if [ "$TOTAL_ERRORS" -eq 0 ]; then
    debug_log "✓ All builds passed, allowing stop"
    exit 0
fi

if [ "$TOTAL_ERRORS" -lt "$ERROR_THRESHOLD" ]; then
    # 错误数低于阈值，警告但不阻断
    echo "Warning: Found $TOTAL_ERRORS error(s), but below threshold ($ERROR_THRESHOLD). Consider reviewing before proceeding." >&2
    exit 0
fi

# ===== 错误 ≥ 阈值，阻断 Stop =====
debug_log "✗ Found $TOTAL_ERRORS errors (threshold: $ERROR_THRESHOLD), blocking stop"

REASON="Build check failed: Found $TOTAL_ERRORS error(s) across $REPO_COUNT repository(ies)."

if [ "$TOTAL_ERRORS" -ge 5 ]; then
    REASON="$REASON Consider running /build-and-fix to invoke the build-error-resolver agent."
fi

REASON="$REASON\n\nError summary:\n$ERROR_SUMMARY"

# 输出 JSON（阻断 Stop）
cat <<EOF
{
  "decision": "block",
  "reason": "$(echo -e "$REASON" | sed 's/"/\\"/g' | tr '\n' ' ')"
}
EOF

exit 2
