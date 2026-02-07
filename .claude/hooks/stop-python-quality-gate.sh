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
# 退出码和JSON输出（符合 Claude 官方规范）:
#   成功（允许停止）:
#     退出码: 0
#     JSON: {}
#
#   警告（错误数低于阈值，允许停止但提示）:
#     退出码: 0
#     JSON: {"systemMessage": "⚠️ 发现 N 个错误，低于阈值..."}
#
#   阻止停止（错误数 >= 阈值）:
#     退出码: 0  (不使用exit 2)
#     JSON: {"decision": "block", "reason": "❌ Python 质量检查失败: 发现 N 个错误..."}
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

# 检查输入是否为空
if [ -z "$INPUT_JSON" ]; then
    debug_log "Empty input received, allowing stop"
    echo '{}'
    exit 0
fi

# 验证 JSON 格式
if ! echo "$INPUT_JSON" | jq empty 2>/dev/null; then
    debug_log "Invalid JSON input, allowing stop"
    echo '{}'
    exit 0
fi

SESSION_ID=$(echo "$INPUT_JSON" | jq -r '.session_id // "unknown"' 2>/dev/null || echo "unknown")
STOP_HOOK_ACTIVE=$(echo "$INPUT_JSON" | jq -r '.stop_hook_active // false' 2>/dev/null || echo "false")

debug_log "Python Quality Gate started for session: $SESSION_ID"

# ===== 防止无限循环：如果已经触发过 Stop hook，跳过检查 =====
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
    debug_log "Stop hook already active, allowing stop to prevent loop"
    echo '{}'
    exit 0
fi

# ===== 检查编辑日志是否存在 =====
if [ ! -f "$EDIT_LOG_FILE" ]; then
    debug_log "No edit log found at $EDIT_LOG_FILE, skipping quality check"
    # 输出成功结果（允许停止）
    echo '{}'
    exit 0
fi

# ===== 处理多行 JSON 对象的编辑日志 =====
# 使用独立的 Python 脚本解析编辑日志
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARSE_SCRIPT="$SCRIPT_DIR/parse_edit_log.py"

if [ ! -f "$PARSE_SCRIPT" ]; then
    error_log "Parse script not found: $PARSE_SCRIPT"
    echo '{}'
    exit 0
fi

EDITED_FILES=$(python3 "$PARSE_SCRIPT" "$EDIT_LOG_FILE" "$SESSION_ID" 2>&1)

debug_log "Found repos: $EDITED_FILES"

if [ -z "$EDITED_FILES" ] || [ "$(echo "$EDITED_FILES" | wc -l)" -eq 0 ]; then
    debug_log "No files edited in this session, skipping quality check"
    echo '{}'
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

        # 动态替换 $PROJECT_ROOT 占位符为实际项目根目录
        PROJECT_ROOT=$(pwd)
        REPO_CONFIGS=$(echo "$BUILD_CONFIG" | jq -c --arg root "$PROJECT_ROOT" '
            .repos | to_entries | map(
                if .key == "$PROJECT_ROOT" then
                    .key = $root
                else
                    .
                end
            ) | from_entries
        ')
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

        # ===== 命令验证/白名单检查（Recommendation #1）=====
        # 允许的命令可执行文件（基于 build-checker-python.json 配置）
        ALLOWED_EXECUTABLES="python|python3|find|pytest|mypy|pylint|black|isort|bandit|radon"

        # 提取实际命令（移除可选的环境变量前缀，如 PYTHONPATH=.）
        ACTUAL_CMD="$CHECK_CMD"
        if [[ "$ACTUAL_CMD" =~ ^[A-Z_]+= ]]; then
            # 移除前导环境变量赋值（支持单个或多个，用空格分隔）
            ACTUAL_CMD=$(echo "$ACTUAL_CMD" | sed -E 's/^([A-Z_]+=\S+\s+)+//')
        fi

        # 提取第一个命令可执行文件名（处理管道、子shell等）
        FIRST_EXECUTABLE=$(echo "$ACTUAL_CMD" | sed -E 's/^[[:space:]]*//' | awk '{print $1}' | sed 's/.*\///')

        if ! echo "$FIRST_EXECUTABLE" | grep -qE "^($ALLOWED_EXECUTABLES)$"; then
            error_log "    [$CHECK_NAME] BLOCKED: Command '$FIRST_EXECUTABLE' not in allowlist"

            # 阻止 Stop 并返回详细原因
            jq -n \
              --arg reason "❌ 安全检查失败: 检查 '$CHECK_NAME' 使用了未授权的命令 '$FIRST_EXECUTABLE'。\n\n允许的命令: $(echo "$ALLOWED_EXECUTABLES" | tr '|' ', ')\n\n请更新 .claude/build-checker-python.json 配置或联系管理员。" \
              '{
                decision: "block",
                reason: $reason
              }'
            exit 0
        fi

        debug_log "    [$CHECK_NAME] Command validated: $FIRST_EXECUTABLE"

        # 运行检查（带超时）
        CHECK_OUTPUT=""
        if CHECK_OUTPUT=$(cd "$repo" && timeout "$CHECK_TIMEOUT" bash -c "$CHECK_CMD" 2>&1); then
            debug_log "    [$CHECK_NAME] ✓ Passed"
            CHECK_ERRORS["$CHECK_NAME"]=0
        else
            # 检查失败，解析错误
            if [ -n "$ERROR_PATTERNS" ]; then
                ERROR_COUNT=$(echo "$CHECK_OUTPUT" | grep -cE "$ERROR_PATTERNS" 2>/dev/null || echo 0)
                ERROR_COUNT=$(echo "$ERROR_COUNT" | tr -d '[:space:]' | sed 's/[^0-9]//g')
                [ -z "$ERROR_COUNT" ] && ERROR_COUNT=0
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
    echo '{}'
    exit 0
fi

if [ "$TOTAL_ERRORS" -lt "$ERROR_THRESHOLD" ]; then
    # 错误数低于阈值，警告但不阻断
    debug_log "⚠ Found $TOTAL_ERRORS errors, below threshold ($ERROR_THRESHOLD)"

    # 构建错误详情 JSON 数组
    ERROR_DETAILS_ARRAY="[]"
    for check_name in "${!CHECK_ERRORS[@]}"; do
        error_count="${CHECK_ERRORS[$check_name]}"
        error_count=$(echo "$error_count" | tr -d '[:space:]' | grep -E '^[0-9]+$' || echo 0)
        [ -z "$error_count" ] && error_count=0
        ERROR_DETAILS_ARRAY=$(echo "$ERROR_DETAILS_ARRAY" | jq --arg name "$check_name" --argjson count "$error_count" '. += [{name: $name, errors: $count}]')
    done

    # 使用 jq 生成有效的 JSON（不阻断）
    jq -n \
      --arg msg "⚠️ 发现 $TOTAL_ERRORS 个错误，低于阈值 ($ERROR_THRESHOLD)。建议修复后再继续。" \
      '{
        systemMessage: $msg
      }'
    exit 0
fi

# ===== 错误 ≥ 阈值，阻断 Stop =====
debug_log "✗ Found $TOTAL_ERRORS errors (threshold: $ERROR_THRESHOLD), blocking stop"

    # 构建错误详情 JSON 数组
    ERROR_DETAILS_ARRAY="[]"
    for check_name in "${!CHECK_ERRORS[@]}"; do
        error_count="${CHECK_ERRORS[$check_name]}"
        error_count=$(echo "$error_count" | tr -d '[:space:]' | grep -E '^[0-9]+$' || echo 0)
        [ -z "$error_count" ] && error_count=0
        ERROR_DETAILS_ARRAY=$(echo "$ERROR_DETAILS_ARRAY" | jq --arg name "$check_name" --argjson count "$error_count" '. += [{name: $name, errors: $count}]')
    done

# 构建原因字符串
REASON="❌ Python 质量检查失败: 发现 $TOTAL_ERRORS 个错误（阈值: $ERROR_THRESHOLD）

请修复以下错误后再停止：

$(echo -e "$ERROR_SUMMARY" | head -c 800)"

# 使用 jq 生成有效的 JSON（decision: "block" + reason）
jq -n \
  --arg reason "$REASON" \
  '{
    decision: "block",
    reason: $reason
  }'

# 退出码 0（Stop hook 使用 JSON decision 字段控制是否阻止）
exit 0
