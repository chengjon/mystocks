#!/usr/bin/env bash
#
# ============================================================================
# Claude Code Hook: Document Organizer (文档组织器)
# ============================================================================
#
# Event: PostToolUse
# Matcher: Write
# Purpose: 自动验证新文档位置是否符合项目文件组织规则,并提供建议
#
# MyStocks 文件组织哲学:
#   - 根目录只允许5个核心文件 (README, CLAUDE, CHANGELOG, requirements.txt, .mcp.json)
#   - 所有其他文件必须按功能分类到子目录
#   - 文档文件必须放在 docs/ 的正确子目录中
#
# 文档分类规则:
#   docs/guides/        - 用户和开发者指南 (QUICKSTART.md, IFLOW.md, 教程)
#   docs/archived/      - 已废弃文档 (保留历史参考,顶部标注废弃)
#   docs/architecture/  - 架构设计文档 (系统设计、技术架构)
#   docs/api/          - API 文档 (API 参考、端点文档、SDK 指南)
#   docs/standards/    - 标准和规范 (编码标准、流程文档、规范)
#
# 工作原理:
#   1. 从 stdin 读取 tool_input.file_path 和 tool_input.content
#   2. 检测是否创建了新的文档文件 (.md, .txt, .rst 等)
#   3. 验证文档位置是否符合文件组织规则
#   4. 如果位置不当,通过 hookSpecificOutput.additionalContext 提供建议
#   5. 非阻塞 (exit 0),仅建议,不强制移动
#
# 退出码 (符合 Claude 官方规范):
#   0: 成功 (非阻塞),建议通过 additionalContext 注入
#   1: 警告 (显示 stderr 但继续)
#   2: 不使用 (文档位置建议不应阻塞工作流)
#
# JSON 输出格式 (使用官方推荐的 hookSpecificOutput.additionalContext):
#   {
#     "hookSpecificOutput": {
#       "hookEventName": "PostToolUse",
#       "additionalContext": "📁 DOCUMENT ORGANIZATION SUGGESTION\n\n..."
#     }
#   }
#
# 安装方法:
#   1. chmod +x post-tool-use-document-organizer.sh
#   2. 复制到 .claude/hooks/
#   3. 添加到 settings.json:
#      {
#        "hooks": {
#          "PostToolUse": [
#            {
#              "matcher": "Write",
#              "hooks": [{
#                "type": "command",
#                "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-document-organizer.sh"
#              }],
#              "timeout": 5
#            }
#          ]
#        }
#      }
#
# Timeout 建议: 5 秒 (快速路径检查)
#
# MyStocks 项目特定规则:
#   - 根目录只允许5个核心文件
#   - 所有文档必须在 docs/ 子目录中
#   - 配置文件必须在 config/
#   - 脚本文件必须在 scripts/ 的正确子目录
#
# 自动更新索引:
#   - 检测到新文档时,建议更新相关索引文件
#   - 例如: 新建 API 文档 → 建议更新 docs/api/README.md
#
# ============================================================================

set -euo pipefail

# ===== 配置 =====
DEBUG_MODE="${DOC_ORGANIZER_DEBUG:-false}"
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"

# 允许在根目录的5个核心文件
ALLOWED_ROOT_FILES=(
    "README.md"
    "CLAUDE.md"
    "CHANGELOG.md"
    "requirements.txt"
    ".mcp.json"
)

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
debug_log "Document organizer started"

# ===== 验证 stdin 不为空 =====
if [ -z "$INPUT_JSON" ]; then
    debug_log "Empty stdin, skipping"
    exit 0
fi

# ===== 验证 JSON 有效性 =====
if ! echo "$INPUT_JSON" | jq empty 2>/dev/null; then
    debug_log "Invalid JSON received, skipping"
    exit 0
fi

# ===== 提取必要字段（使用安全的 jq 调用） =====
TOOL_NAME=$(echo "$INPUT_JSON" | jq -r '.tool_name // "Unknown"' 2>/dev/null || echo "Unknown")
FILE_PATH=$(echo "$INPUT_JSON" | jq -r '.tool_input.file_path // empty' 2>/dev/null || echo "")
CONTENT=$(echo "$INPUT_JSON" | jq -r '.tool_input.content // empty' 2>/dev/null || echo "")
SESSION_ID=$(echo "$INPUT_JSON" | jq -r '.session_id // "unknown"' 2>/dev/null || echo "unknown")

# ===== 如果不是 Write 工具,跳过 =====
if [ "$TOOL_NAME" != "Write" ]; then
    debug_log "Tool $TOOL_NAME is not Write, skipping"
    exit 0
fi

# ===== 如果没有文件路径,跳过 =====
if [ -z "$FILE_PATH" ]; then
    debug_log "No file_path found, skipping"
    exit 0
fi

# ===== 转换为相对路径 (如果是绝对路径) =====
if [[ "$FILE_PATH" == "$PROJECT_ROOT"* ]]; then
    RELATIVE_PATH="${FILE_PATH#$PROJECT_ROOT/}"
else
    RELATIVE_PATH="$FILE_PATH"
fi

debug_log "Checking file: $RELATIVE_PATH"

# ===== 检测文件类型 =====
FILE_EXTENSION="${RELATIVE_PATH##*.}"
FILE_BASENAME=$(basename "$RELATIVE_PATH")
FILE_DIRNAME=$(dirname "$RELATIVE_PATH")

# ===== 只检查文档文件 =====
DOC_EXTENSIONS=("md" "txt" "rst" "adoc" "org")
IS_DOC=false

for ext in "${DOC_EXTENSIONS[@]}"; do
    if [ "$FILE_EXTENSION" = "$ext" ]; then
        IS_DOC=true
        break
    fi
done

if [ "$IS_DOC" = "false" ]; then
    debug_log "File is not a document, skipping"
    exit 0
fi

debug_log "Detected document file: $FILE_BASENAME"

# ===== 检查是否在根目录 =====
IS_IN_ROOT=false
if [ "$FILE_DIRNAME" = "." ] || [ "$FILE_DIRNAME" = "/" ] || [[ ! "$RELATIVE_PATH" =~ / ]]; then
    IS_IN_ROOT=true
fi

# ===== 如果在根目录,检查是否是允许的核心文件 =====
VIOLATION=""
SUGGESTION=""

if [ "$IS_IN_ROOT" = "true" ]; then
    IS_ALLOWED=false
    for allowed in "${ALLOWED_ROOT_FILES[@]}"; do
        if [ "$FILE_BASENAME" = "$allowed" ]; then
            IS_ALLOWED=true
            break
        fi
    done

    if [ "$IS_ALLOWED" = "false" ]; then
        VIOLATION="📁 文档文件不应放在根目录"

        # 根据文件名推测应该放在哪里
        if [[ "$FILE_BASENAME" =~ ^(QUICKSTART|quickstart|tutorial|guide|getting.?started|how.?to) ]]; then
            SUGGESTION="docs/guides/"
        elif [[ "$FILE_BASENAME" =~ ^(API|api|endpoint|swagger|openapi) ]] || [[ "$CONTENT" =~ (API|endpoint|/api/|swagger|openapi) ]]; then
            SUGGESTION="docs/api/"
        elif [[ "$FILE_BASENAME" =~ (architecture|design|system|database|schema) ]] || [[ "$CONTENT" =~ (架构|architecture|设计|design) ]]; then
            SUGGESTION="docs/architecture/"
        elif [[ "$FILE_BASENAME" =~ (standard|规范|convention|guideline|best.?practice) ]] || [[ "$CONTENT" =~ (标准|规范|standard|convention) ]]; then
            SUGGESTION="docs/standards/"
        elif [[ "$FILE_BASENAME" =~ (deprecated|archived|old|legacy|废弃) ]] || [[ "$CONTENT" =~ (已废弃|deprecated|archived) ]]; then
            SUGGESTION="docs/archived/"
        else
            # 默认放在 guides
            SUGGESTION="docs/guides/"
        fi
    fi
fi

# ===== 如果已经在 docs/ 下,检查是否在正确的子目录 =====
if [[ "$RELATIVE_PATH" =~ ^docs/ ]]; then
    # 检查是否直接在 docs/ 根目录
    if [[ "$FILE_DIRNAME" = "docs" ]]; then
        VIOLATION="📁 文档不应直接放在 docs/ 根目录"

        # 推测正确子目录
        if [[ "$FILE_BASENAME" =~ ^(QUICKSTART|quickstart|tutorial|guide) ]]; then
            SUGGESTION="docs/guides/"
        elif [[ "$FILE_BASENAME" =~ ^(API|api) ]]; then
            SUGGESTION="docs/api/"
        elif [[ "$FILE_BASENAME" =~ (architecture|design) ]]; then
            SUGGESTION="docs/architecture/"
        elif [[ "$FILE_BASENAME" =~ (standard|规范|convention) ]]; then
            SUGGESTION="docs/standards/"
        else
            SUGGESTION="docs/guides/"
        fi
    else
        # 已经在子目录,验证是否正确
        SUBDIR=$(echo "$FILE_DIRNAME" | cut -d'/' -f2)

        # 验证子目录是否有效
        VALID_SUBDIRS=("guides" "archived" "architecture" "api" "standards")
        IS_VALID_SUBDIR=false

        for valid in "${VALID_SUBDIRS[@]}"; do
            if [ "$SUBDIR" = "$valid" ]; then
                IS_VALID_SUBDIR=true
                break
            fi
        done

        if [ "$IS_VALID_SUBDIR" = "false" ]; then
            VIOLATION="📁 无效的 docs/ 子目录: $SUBDIR"
            SUGGESTION="docs/guides/ (或 api/, architecture/, standards/, archived/)"
        fi
    fi
fi

# ===== 检测是否需要更新索引文件 =====
INDEX_UPDATE_SUGGESTIONS=""

if [[ "$RELATIVE_PATH" =~ ^docs/api/ ]]; then
    INDEX_UPDATE_SUGGESTIONS="\n💡 建议更新: docs/api/README.md (添加新 API 文档链接)"
elif [[ "$RELATIVE_PATH" =~ ^docs/architecture/ ]]; then
    INDEX_UPDATE_SUGGESTIONS="\n💡 建议更新: docs/architecture/README.md (如果存在)"
elif [[ "$RELATIVE_PATH" =~ ^docs/standards/ ]]; then
    INDEX_UPDATE_SUGGESTIONS="\n💡 建议更新: docs/standards/README.md (添加新规范文档)"
fi

# ===== 如果没有违规,正常退出 =====
if [ -z "$VIOLATION" ]; then
    debug_log "Document location is correct"

    # 即使位置正确,如果有索引更新建议,也提示
    if [ -n "$INDEX_UPDATE_SUGGESTIONS" ]; then
        CONTEXT_MESSAGE="📁 DOCUMENT ORGANIZATION

✅ 文档位置正确: $RELATIVE_PATH
$INDEX_UPDATE_SUGGESTIONS
"
        ESCAPED_CONTEXT=$(echo "$CONTEXT_MESSAGE" | jq -Rs .)

        cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": $ESCAPED_CONTEXT
  }
}
EOF
    fi

    exit 0
fi

# ===== 检查是否需要自动修复位置问题 =====
# 如果文件已经在建议的位置,说明已经被正确放置,无需进一步操作
SUGGESTED_FULL_PATH="$SUGGESTION$FILE_BASENAME"
if [ -f "$SUGGESTED_FULL_PATH" ]; then
    debug_log "File already exists at suggested location: $SUGGESTED_FULL_PATH"

    # 输出一个信息性消息,说明文档已经在正确位置
    CONTEXT_MESSAGE="📁 DOCUMENT ORGANIZATION

✅ 文档已在正确位置: $SUGGESTED_FULL_PATH

此 hook 检测到文档已经被放置在组织规则要求的位置,无需进一步操作。
"
    ESCAPED_CONTEXT=$(echo "$CONTEXT_MESSAGE" | jq -Rs .)

    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": $ESCAPED_CONTEXT
  }
}
EOF

    exit 0
fi

# ===== 构建建议消息 (注入给 Claude) =====
CONTEXT_MESSAGE="📁 DOCUMENT ORGANIZATION SUGGESTION

⚠️ $VIOLATION

当前位置: $RELATIVE_PATH
建议位置: $SUGGESTION$FILE_BASENAME

📖 MyStocks 文件组织规则:

根目录规则:
  只允许5个核心文件: README.md, CLAUDE.md, CHANGELOG.md, requirements.txt, .mcp.json
  所有其他文件必须组织到子目录

文档分类规则:
  docs/guides/       - 用户指南、教程 (QUICKSTART.md, IFLOW.md)
  docs/api/          - API 文档 (端点文档、SDK 指南、OpenAPI 规范)
  docs/architecture/ - 架构设计文档 (系统设计、数据库架构)
  docs/standards/    - 标准和规范 (编码标准、流程文档)
  docs/archived/     - 已废弃文档 (历史参考,顶部标注废弃)

💡 推荐操作:
  1. 确认源文件位置，然后使用 'git mv' 移动文档到建议位置 (保留历史)

     如果文件已在 git 中：
       git mv $RELATIVE_PATH $SUGGESTION$FILE_BASENAME

     如果文件是新文件（未追踪）：
       git add $SUGGESTION$FILE_BASENAME
       git rm --cached $RELATIVE_PATH 2>/dev/null || true

  2. 更新所有引用此文档的链接

  3. 如果创建了新的 API/架构/标准文档,考虑更新相关索引文件$INDEX_UPDATE_SUGGESTIONS

参考: docs/standards/FILE_ORGANIZATION_RULES.md (完整规则)
      .claude/hooks/FILE_ORGANIZATION_GUIDE.md (快速指南)

⚠️ 注意: 请确保先检查源文件是否存在再执行 'git mv' 命令。
"

# ===== 输出 JSON (通过 additionalContext 注入给 Claude) =====
ESCAPED_CONTEXT=$(echo "$CONTEXT_MESSAGE" | jq -Rs .)

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": $ESCAPED_CONTEXT
  }
}
EOF

debug_log "Document organization suggestion sent to Claude"

# 非阻塞成功退出
exit 0
