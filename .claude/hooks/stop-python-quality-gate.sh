#!/usr/bin/env bash
#
# ============================================================================
# Claude Code Hook: Python Quality Gate (质量门禁)
# ============================================================================
#
# Event: Stop
# Purpose: 在 Claude 完成响应前，检查 Python 代码质量（语法、导入、类型、测试）
#
# 核心设计理念（基于 Reddit Case Study）:
#   这是"零错误容忍"策略的核心组件，与 PostToolUse file-edit-tracker 配合使用：
#   1. PostToolUse: 非阻塞记录编辑文件
#   2. Stop: 批量运行质量检查，若错误 ≥ 阈值则阻断 Claude 停止
#
#   目标: 确保代码质量，防止低质量代码流入生产环境
#
# 工作原理:
#   1. 读取 .claude/edit_log.jsonl，找出本会话编辑的所有文件
#   2. 按仓库分组（同一仓库的文件一起检查）
#   3. 针对每个受影响仓库运行 Python 质量检查：
#      - 关键模块导入验证（核心架构完整性）
#      - Python 语法检查（py_compile）
#      - 类型提示检查（mypy，可选）
#      - 快速测试（pytest，可选）
#   4. 收集所有错误
#   5. 如果错误 ≥ 阈值（默认 10），阻断 Stop 并要求 Claude 修复
#
# 退出码（符合 Claude 官方规范）:
#   0: 质量检查通过或错误 < 阈值（允许停止）
#   2: 质量检查失败且错误 ≥ 阈值（阻止停止，要求 Claude 修复）
#
# JSON 输出格式（使用官方推荐的 hookSpecificOutput 格式）:
#   {
#     "hookSpecificOutput": {
#       "hookEventName": "Stop",
#       "decision": "block",
#       "reason": "发现 12 个错误。请修复后再停止。",
#       "errorDetails": {
#         "critical_imports": 0,
#         "backend_syntax": 5,
#         "core_syntax": 2,
#         "type_hints_core": 3,
#         "quick_tests": 2
#       }
#     }
#   }
#
# 配置文件（.claude/build-checker-python.json）:
#   {
#     "errorThreshold": 10,
#     "repos": {
#       "/opt/claude/mystocks_spec": {
#         "qualityChecks": [
#           {
#             "name": "critical_imports",
#             "command": "python -c 'from src.core import ConfigDrivenTableManager; from web.backend.app.main import app'",
#             "critical": true,
#             "timeout": 15
#           }
#         ]
#       }
#     }
#   }
#
# 安装方法:
#   1. chmod +x stop-python-quality-gate.sh
#   2. 复制到 .claude/hooks/
#   3. 创建 .claude/build-checker-python.json 配置
#   4. 添加到 settings.json:
#      {
#        "hooks": {
#          "Stop": [
#            {
#              "hooks": [{
#                "type": "command",
#                "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/stop-python-quality-gate.sh"
#              }],
#              "timeout": 120
#            }
#          ]
#        }
#      }
#
# Timeout 建议: 120 秒（质量检查可能需要时间，根据项目大小调整到 180-240 秒）
#
# MyStocks 项目特定配置:
#   - 检查核心导入: from src.core import ConfigDrivenTableManager
#   - 检查后端导入: from web.backend.app.main import app
#   - 语法检查: web/backend/app/, src/core/, src/adapters/, src/data_access/
#   - 可选: mypy 类型检查，pytest 快速测试
#
# ============================================================================

set -euo pipefail

# ===== 配置 =====
EDIT_LOG_FILE="${CLAUDE_EDIT_LOG:-.claude/edit_log.jsonl}"
BUILD_CONFIG_FILE=".claude/build-checker-python.json"
DEFAULT_ERROR_THRESHOLD=10
DEBUG_MODE="${PYTHON_QG_DEBUG:-false}"
HOOK_TIMEOUT=120  # 单个检查的最大执行时间（秒）

# ===== 调试日志函数 =====
debug_log() {
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] $*" >&2
    fi
}

# ===== 错误输出函数 =====
error_log() {
    echo "[ERROR] $*" >&2
}

# ===== 读取 stdin JSON =====
INPUT_JSON=$(cat)
SESSION_ID=$(echo "$INPUT_JSON" | jq -r '.session_id // "unknown"')

debug_log "Python Quality Gate started for session: $SESSION_ID"

# ===== 检查编辑日志是否存在 =====
if [ ! -f "$EDIT_LOG_FILE" ]; then
    debug_log "No edit log found at $EDIT_LOG_FILE, skipping quality check"
    # 输出成功结果（允许停止）
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "Stop",
    "decision": "allow",
    "reason": "No files edited in this session"
  }
}
EOF
    exit 0
fi

# ===== 处理多行 JSON 对象的编辑日志 =====
# 编辑日志包含多行 JSON 对象，使用 Python 进行处理
EDITED_FILES=$(python3 << PYTHON_EOF
import json
import sys

session_id = "$SESSION_ID"
repos = set()

try:
    with open("$EDIT_LOG_FILE", 'r', encoding='utf-8') as f:
        content = f.read()
        # 处理多行 JSON 对象
        objects = []
        current_obj = ""
        brace_count = 0

        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue

            current_obj += line + "\n"
            brace_count += line.count('{') - line.count('}')

            if brace_count == 0 and current_obj.strip():
                try:
                    obj = json.loads(current_obj)
                    if obj.get('session_id') == session_id:
                        repo = obj.get('repo')
                        if repo:
                            repos.add(repo)
                    current_obj = ""
                except json.JSONDecodeError:
                    current_obj = ""

        # 输出找到的仓库（按行分隔）
        for repo in sorted(repos):
            print(repo)
except Exception as e:
    sys.stderr.write(f"Error parsing edit log: {e}\n")
PYTHON_EOF
)

debug_log "Found repos: $EDITED_FILES"

if [ -z "$EDITED_FILES" ] || [ "$(echo "$EDITED_FILES" | wc -l)" -eq 0 ]; then
    debug_log "No files edited in this session, skipping quality check"
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "Stop",
    "decision": "allow",
    "reason": "No files edited in this session"
  }
}
EOF
    exit 0
fi

# ===== 获取受影响的仓库列表（已自动去重）=====
AFFECTED_REPOS="$EDITED_FILES"
REPO_COUNT=$(echo "$AFFECTED_REPOS" | grep -v '^$' | wc -l)

debug_log "Found $REPO_COUNT affected repositories"

# ===== 读取质量检查配置 =====
ERROR_THRESHOLD=$DEFAULT_ERROR_THRESHOLD
REPO_CONFIGS="{}"

if [ -f "$BUILD_CONFIG_FILE" ]; then
    debug_log "Loading quality check configuration from $BUILD_CONFIG_FILE"
    BUILD_CONFIG=$(cat "$BUILD_CONFIG_FILE")

    if ! echo "$BUILD_CONFIG" | jq empty 2>/dev/null; then
        error_log "$BUILD_CONFIG_FILE contains invalid JSON, using defaults"
    else
        ERROR_THRESHOLD=$(echo "$BUILD_CONFIG" | jq -r '.errorThreshold // 10')
        REPO_CONFIGS=$(echo "$BUILD_CONFIG" | jq -c '.repos // {}')
    fi
else
    debug_log "No quality check configuration found, using default settings"
fi

debug_log "Error threshold: $ERROR_THRESHOLD"

# ===== 运行质量检查并收集错误 =====
TOTAL_ERRORS=0
declare -A CHECK_ERRORS  # 关联数组存储每个检查的错误数
ERROR_SUMMARY=""

while IFS= read -r repo; do
    if [ -z "$repo" ] || [ ! -d "$repo" ]; then
        continue
    fi

    debug_log "Checking repository: $repo"

    # 获取该仓库的质量检查配置
    QUALITY_CHECKS=$(echo "$REPO_CONFIGS" | jq -c --arg repo "$repo" '.[$repo].qualityChecks // []')

    if [ "$QUALITY_CHECKS" = "[]" ]; then
        debug_log "  No quality checks configured for $repo, skipping"
        continue
    fi

    # 遍历所有质量检查
    CHECK_COUNT=$(echo "$QUALITY_CHECKS" | jq 'length')
    debug_log "  Running $CHECK_COUNT quality checks"

    for i in $(seq 0 $((CHECK_COUNT - 1))); do
        CHECK=$(echo "$QUALITY_CHECKS" | jq -c ".[$i]")

        CHECK_NAME=$(echo "$CHECK" | jq -r '.name')
        CHECK_CMD=$(echo "$CHECK" | jq -r '.command')
        CHECK_CRITICAL=$(echo "$CHECK" | jq -r '.critical // false')
        CHECK_TIMEOUT=$(echo "$CHECK" | jq -r '.timeout // 30')
        ERROR_PATTERNS=$(echo "$CHECK" | jq -r '.errorPatterns // [] | join("|")')

        debug_log "    [$CHECK_NAME] Running: $CHECK_CMD"

        # 运行检查（带超时）
        CHECK_OUTPUT=""
        if CHECK_OUTPUT=$(cd "$repo" && timeout "$CHECK_TIMEOUT" bash -c "$CHECK_CMD" 2>&1); then
            debug_log "    [$CHECK_NAME] ✓ Passed"
            CHECK_ERRORS["$CHECK_NAME"]=0
        else
            # 检查失败，解析错误
            if [ -n "$ERROR_PATTERNS" ]; then
                ERROR_COUNT=$(echo "$CHECK_OUTPUT" | grep -cE "$ERROR_PATTERNS" || echo 0)
            else
                # 默认：任何输出都算1个错误
                if [ -n "$CHECK_OUTPUT" ]; then
                    ERROR_COUNT=1
                else
                    ERROR_COUNT=0
                fi
            fi

            CHECK_ERRORS["$CHECK_NAME"]=$ERROR_COUNT

            if [ "$CHECK_CRITICAL" = "true" ] && [ "$ERROR_COUNT" -gt 0 ]; then
                # 关键检查失败，立即增加错误计数
                TOTAL_ERRORS=$((TOTAL_ERRORS + ERROR_COUNT))
                debug_log "    [$CHECK_NAME] ✗ CRITICAL FAILED with $ERROR_COUNT errors"

                # 提取前 5 行错误消息
                ERROR_PREVIEW=$(echo "$CHECK_OUTPUT" | head -n 5)
                ERROR_SUMMARY="${ERROR_SUMMARY}[$CHECK_NAME - CRITICAL] $ERROR_COUNT errors:\n$ERROR_PREVIEW\n\n"
            elif [ "$ERROR_COUNT" -gt 0 ]; then
                # 非关键检查失败，记录但不增加计数（或根据需求调整）
                TOTAL_ERRORS=$((TOTAL_ERRORS + ERROR_COUNT))
                debug_log "    [$CHECK_NAME] ⚠ Failed with $ERROR_COUNT errors (non-critical)"

                ERROR_PREVIEW=$(echo "$CHECK_OUTPUT" | head -n 3)
                ERROR_SUMMARY="${ERROR_SUMMARY}[$CHECK_NAME] $ERROR_COUNT errors:\n$ERROR_PREVIEW\n\n"
            fi
        fi
    done
done <<< "$AFFECTED_REPOS"

# ===== 决策：是否阻断 Stop =====
if [ "$TOTAL_ERRORS" -eq 0 ]; then
    debug_log "✓ All quality checks passed, allowing stop"
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "Stop",
    "decision": "allow",
    "reason": "✅ 所有质量检查通过！"
  }
}
EOF
    exit 0
fi

if [ "$TOTAL_ERRORS" -lt "$ERROR_THRESHOLD" ]; then
    # 错误数低于阈值，警告但不阻断
    debug_log "⚠ Found $TOTAL_ERRORS errors, below threshold ($ERROR_THRESHOLD)"

    # 构建错误详情 JSON
    ERROR_DETAILS="{"
    for check_name in "${!CHECK_ERRORS[@]}"; do
        ERROR_DETAILS="$ERROR_DETAILS\"$check_name\": ${CHECK_ERRORS[$check_name]},"
    done
    ERROR_DETAILS="${ERROR_DETAILS%,}}"  # 移除最后的逗号

    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "Stop",
    "decision": "allow",
    "reason": "⚠️ 发现 $TOTAL_ERRORS 个错误，低于阈值 ($ERROR_THRESHOLD)。建议修复后再继续。",
    "errorDetails": $ERROR_DETAILS
  }
}
EOF
    exit 0
fi

# ===== 错误 ≥ 阈值，阻断 Stop =====
debug_log "✗ Found $TOTAL_ERRORS errors (threshold: $ERROR_THRESHOLD), blocking stop"

# 构建错误详情 JSON
ERROR_DETAILS="{"
for check_name in "${!CHECK_ERRORS[@]}"; do
    ERROR_DETAILS="$ERROR_DETAILS\"$check_name\": ${CHECK_ERRORS[$check_name]},"
done
ERROR_DETAILS="${ERROR_DETAILS%,}}"

# 构建原因字符串（转义换行符和引号）
REASON="❌ Python 质量检查失败: 发现 $TOTAL_ERRORS 个错误（阈值: $ERROR_THRESHOLD）\n\n"
REASON="${REASON}请修复以下错误后再停止：\n\n"
REASON="${REASON}$(echo -e "$ERROR_SUMMARY" | sed 's/"/\\"/g' | tr '\n' '\\' | sed 's/\\/\\n/g')"

# 输出 JSON（阻断 Stop）
cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "Stop",
    "decision": "block",
    "reason": "$(echo -e "$REASON" | sed 's/"/\\"/g' | head -c 1000)",
    "errorDetails": $ERROR_DETAILS,
    "suggestion": "使用 Task Master 创建修复任务: task-master add-task --prompt='修复质量检查错误'"
  }
}
EOF

# 退出码 2 = 阻止停止
exit 2
