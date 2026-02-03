# Claude Code Hooks 系统迁移指南

**版本**: 2.0 (Python/FastAPI)
**创建日期**: 2025-11-11
**目的**: 完整记录hooks系统,支持迁移到其他项目

---

## 目录

1. [系统概述](#系统概述)
2. [完整文件清单](#完整文件清单)
3. [Hooks详细说明](#hooks详细说明)
4. [配置文件详解](#配置文件详解)
5. [迁移步骤](#迁移步骤)
6. [自定义适配指南](#自定义适配指南)

---

## 系统概述

### 架构特点

- **7个hooks** 跨 **5个事件**: UserPromptSubmit, PostToolUse (3个), Stop, SessionStart, SessionEnd
- **遵循Claude官方规范**: Exit codes (0/1/2), JSON output (`hookSpecificOutput`), 合理timeout
- **非阻塞为主**: 除Stop hook外,所有hooks都是非阻塞(exit 0)
- **项目级日志**: 使用 `.claude/edit_log.jsonl` (非全局)
- **配置驱动**: 通过JSON配置文件控制行为

### 核心设计模式

1. **Reddit Case Study模式**: PostToolUse记录 → Stop批量检查
2. **Skill自动激活**: UserPromptSubmit根据关键词触发skill加载
3. **Context注入**: SessionStart通过stdout注入项目上下文
4. **智能分类**: 基于文件名/内容模式进行自动分类建议

---

## 完整文件清单

### 必需文件 (核心系统)

```
.claude/
├── settings.json                                      # 主配置文件 - hooks注册
├── skill-rules.json                                   # Skill激活规则配置
├── build-checker-python.json                          # Python质量检查配置
└── hooks/
    ├── user-prompt-submit-skill-activation.sh         # UserPromptSubmit hook
    ├── post-tool-use-file-edit-tracker.sh            # PostToolUse hook #1
    ├── post-tool-use-database-schema-validator.sh    # PostToolUse hook #2
    ├── post-tool-use-document-organizer.sh           # PostToolUse hook #3
    ├── stop-python-quality-gate.sh                   # Stop hook
    ├── session-start-task-master-injector.sh         # SessionStart hook
    └── session-end-cleanup.sh                        # SessionEnd hook
```

### 文档文件 (可选但推荐)

```
.claude/hooks/
├── README.md                                 # 用户指南
├── FILE_ORGANIZATION_GUIDE.md                # 文件组织快速指南
├── HOOKS_IMPROVEMENT_COMPLETION_REPORT.md    # 实施报告
├── HOOKS_TESTING_REPORT.md                   # 测试计划
└── DOCUMENT_ORGANIZER_COMPLETION.md          # Document Organizer完成报告
```

### 运行时文件 (自动生成)

```
.claude/
└── edit_log.jsonl                           # 文件编辑日志 (自动生成)
```

---

## Hooks详细说明

### 1. UserPromptSubmit Hook - Skill自动激活

**文件**: `user-prompt-submit-skill-activation.sh`
**大小**: 8,743 bytes
**Event**: UserPromptSubmit
**Timeout**: 5秒
**Exit Code**: 0 (非阻塞)

#### 功能
- 根据用户提示词自动激活相关skills
- 支持中英文双语关键词匹配
- 基于 `skill-rules.json` 配置的规则

#### 适用场景
- 用户输入包含特定关键词(如 "API", "接口", "database", "数据库")
- 用户编辑特定类型文件(如 `*.py`, `*.ts`)
- 自动加载最相关的skill文档到Claude上下文

#### 核心代码示例

```bash
#!/usr/bin/env bash
# Event: UserPromptSubmit
# Purpose: 根据关键词自动激活skills

set -euo pipefail

# 读取配置
SKILL_RULES_FILE="${CLAUDE_PROJECT_DIR}/.claude/skill-rules.json"
INPUT_JSON=$(cat)

# 提取用户提示词
USER_PROMPT=$(echo "$INPUT_JSON" | jq -r '.user_message // empty')

# 检查关键词匹配
ACTIVATED_SKILLS=()

# 遍历所有skills
for skill in $(jq -r '.skills | keys[]' "$SKILL_RULES_FILE"); do
    # 获取关键词列表
    keywords=$(jq -r ".skills[\"$skill\"].promptTriggers.keywords[]" "$SKILL_RULES_FILE")

    # 检查是否匹配
    for keyword in $keywords; do
        if echo "$USER_PROMPT" | grep -qiE "$keyword"; then
            ACTIVATED_SKILLS+=("$skill")
            break
        fi
    done
done

# 输出激活的skills
if [ ${#ACTIVATED_SKILLS[@]} -gt 0 ]; then
    SKILL_LIST=$(printf '%s\n' "${ACTIVATED_SKILLS[@]}" | jq -R . | jq -s .)

    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "activatedSkills": $SKILL_LIST
  }
}
EOF
fi

exit 0
```

#### 配置依赖
- `skill-rules.json` - 定义skill激活规则

---

### 2. PostToolUse Hook #1 - 文件编辑追踪器

**文件**: `post-tool-use-file-edit-tracker.sh`
**大小**: 5,104 bytes
**Event**: PostToolUse
**Matcher**: `Edit|Write`
**Timeout**: 3秒
**Exit Code**: 0 (非阻塞)

#### 功能
- 记录所有文件编辑到 `.claude/edit_log.jsonl`
- JSONL格式(每行一个JSON)
- 自动限制大小(最大10,000行)
- 为Stop hook提供批量检查输入

#### 适用场景
- 每次使用Edit或Write工具时自动记录
- 支持Stop hook进行批量代码质量检查
- 跟踪会话期间的所有文件修改

#### 核心代码示例

```bash
#!/usr/bin/env bash
# Event: PostToolUse
# Matcher: Edit|Write
# Purpose: 记录文件编辑到项目级日志

set -euo pipefail

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"
EDIT_LOG_FILE="${PROJECT_ROOT}/.claude/edit_log.jsonl"
MAX_LOG_LINES=10000

# 读取工具输入
INPUT_JSON=$(cat)
TOOL_NAME=$(echo "$INPUT_JSON" | jq -r '.tool_name // "Unknown"')
FILE_PATH=$(echo "$INPUT_JSON" | jq -r '.tool_input.file_path // empty')
SESSION_ID=$(echo "$INPUT_JSON" | jq -r '.session_id // "unknown"')

# 只记录Edit和Write操作
if [[ "$TOOL_NAME" != "Edit" && "$TOOL_NAME" != "Write" ]]; then
    exit 0
fi

# 如果没有文件路径,跳过
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# 确保日志目录存在
mkdir -p "$(dirname "$EDIT_LOG_FILE")"

# 转换为相对路径
if [[ "$FILE_PATH" == "$PROJECT_ROOT"* ]]; then
    RELATIVE_PATH="${FILE_PATH#$PROJECT_ROOT/}"
else
    RELATIVE_PATH="$FILE_PATH"
fi

# 创建日志条目
LOG_ENTRY=$(jq -n \
    --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg session "$SESSION_ID" \
    --arg file "$RELATIVE_PATH" \
    --arg tool "$TOOL_NAME" \
    '{
        timestamp: $timestamp,
        session_id: $session,
        file: $file,
        tool: $tool
    }')

# 追加到日志文件
echo "$LOG_ENTRY" >> "$EDIT_LOG_FILE"

# 限制日志大小
if [ -f "$EDIT_LOG_FILE" ]; then
    LINE_COUNT=$(wc -l < "$EDIT_LOG_FILE")

    if [ "$LINE_COUNT" -gt "$MAX_LOG_LINES" ]; then
        tail -n "$MAX_LOG_LINES" "$EDIT_LOG_FILE" > "${EDIT_LOG_FILE}.tmp"
        mv "${EDIT_LOG_FILE}.tmp" "$EDIT_LOG_FILE"
    fi
fi

exit 0
```

#### 日志格式示例

```jsonl
{"timestamp":"2025-11-11T10:30:00Z","session_id":"abc123","file":"src/core/manager.py","tool":"Edit"}
{"timestamp":"2025-11-11T10:35:00Z","session_id":"abc123","file":"tests/test_manager.py","tool":"Write"}
```

---

### 3. PostToolUse Hook #2 - 数据库架构验证器

**文件**: `post-tool-use-database-schema-validator.sh`
**大小**: 7,357 bytes
**Event**: PostToolUse
**Matcher**: `Edit|Write`
**Timeout**: 5秒
**Exit Code**: 0 (非阻塞,仅警告)

#### 功能
- 验证双数据库架构合规性 (TDengine vs PostgreSQL)
- 检测危险操作(如 `DROP STABLE`)
- 提供架构违规建议

#### 适用场景 (MyStocks特定)
- 编辑数据库相关文件时触发:
  - `table_config.yaml`
  - `*_adapter.py`
  - `database_manager.py`
  - `data_access/**/*.py`

#### 核心代码示例

```bash
#!/usr/bin/env bash
# Event: PostToolUse
# Matcher: Edit|Write
# Purpose: 验证数据库架构规则

set -euo pipefail

INPUT_JSON=$(cat)
FILE_PATH=$(echo "$INPUT_JSON" | jq -r '.tool_input.file_path // empty')
NEW_STRING=$(echo "$INPUT_JSON" | jq -r '.tool_input.new_string // .tool_input.content // empty')

# 只检查数据库相关文件
DATABASE_FILE_PATTERNS=(
    "table_config.yaml"
    "*_adapter.py"
    "database_manager.py"
    "data_access/"
)

IS_DATABASE_FILE=false
for pattern in "${DATABASE_FILE_PATTERNS[@]}"; do
    if [[ "$FILE_PATH" =~ $pattern ]]; then
        IS_DATABASE_FILE=true
        break
    fi
done

if [ "$IS_DATABASE_FILE" = "false" ]; then
    exit 0
fi

# 定义危险模式
declare -A DANGEROUS_PATTERNS=(
    ["tick.*PostgreSQL"]="⚠️ Tick数据应存储在TDengine超表中,不应使用PostgreSQL"
    ["tick_data.*postgres"]="⚠️ Tick数据应存储在TDengine超表中,不应使用PostgreSQL"
    ["minute.*PostgreSQL"]="⚠️ 分钟K线数据应存储在TDengine超表中,不应使用PostgreSQL"
    ["daily.*TDengine"]="⚠️ 日线数据通常存储在PostgreSQL,使用TDengine需要特殊理由"
    ["DROP.*STABLE"]="🚨 危险操作：删除TDengine超表！这将丢失所有时序数据！"
)

# 扫描代码中的危险模式
WARNINGS=""
WARNING_COUNT=0

for pattern in "${!DANGEROUS_PATTERNS[@]}"; do
    if echo "$NEW_STRING" | grep -qiE "$pattern"; then
        WARNING_MSG="${DANGEROUS_PATTERNS[$pattern]}"
        WARNINGS="${WARNINGS}${WARNING_MSG}\n"
        WARNING_COUNT=$((WARNING_COUNT + 1))
    fi
done

# 如果有警告,输出
if [ "$WARNING_COUNT" -gt 0 ]; then
    CONTEXT_MESSAGE="⚠️ DATABASE ARCHITECTURE WARNING

检测到 $WARNING_COUNT 个潜在的架构违规:

$WARNINGS

MyStocks 双数据库架构规则:
- TDengine: 高频时序数据 (tick, 分钟K线)
- PostgreSQL: 其他数据 (日线, 参考数据, 元数据)
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
```

#### 自定义适配
**修改危险模式**:
```bash
# 根据项目数据库架构定义规则
declare -A DANGEROUS_PATTERNS=(
    ["your_pattern"]="Your warning message"
)
```

**修改文件扫描范围**:
```bash
DATABASE_FILE_PATTERNS=(
    "config/database.yml"
    "models/*.py"
    "repositories/*.py"
)
```

---

### 4. PostToolUse Hook #3 - 文档组织器

**文件**: `post-tool-use-document-organizer.sh`
**大小**: 10,788 bytes
**Event**: PostToolUse
**Matcher**: `Write`
**Timeout**: 5秒
**Exit Code**: 0 (非阻塞)

#### 功能
- 验证新文档位置是否符合项目文件组织规则
- 智能推荐正确的文档位置
- 提供 `git mv` 命令建议

#### 适用场景
- 创建新的文档文件(`.md`, `.txt`, `.rst`, `.adoc`, `.org`)
- 自动检测根目录违规
- 建议正确的 `docs/` 子目录

#### 核心代码示例

```bash
#!/usr/bin/env bash
# Event: PostToolUse
# Matcher: Write
# Purpose: 验证文档位置

set -euo pipefail

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"
INPUT_JSON=$(cat)
FILE_PATH=$(echo "$INPUT_JSON" | jq -r '.tool_input.file_path // empty')
CONTENT=$(echo "$INPUT_JSON" | jq -r '.tool_input.content // empty')

# 允许在根目录的核心文件
ALLOWED_ROOT_FILES=(
    "README.md"
    "CLAUDE.md"
    "CHANGELOG.md"
    "requirements.txt"
    ".mcp.json"
)

# 转换为相对路径
if [[ "$FILE_PATH" == "$PROJECT_ROOT"* ]]; then
    RELATIVE_PATH="${FILE_PATH#$PROJECT_ROOT/}"
else
    RELATIVE_PATH="$FILE_PATH"
fi

FILE_EXTENSION="${RELATIVE_PATH##*.}"
FILE_BASENAME=$(basename "$RELATIVE_PATH")
FILE_DIRNAME=$(dirname "$RELATIVE_PATH")

# 只检查文档文件
DOC_EXTENSIONS=("md" "txt" "rst" "adoc" "org")
IS_DOC=false

for ext in "${DOC_EXTENSIONS[@]}"; do
    if [ "$FILE_EXTENSION" = "$ext" ]; then
        IS_DOC=true
        break
    fi
done

if [ "$IS_DOC" = "false" ]; then
    exit 0
fi

# 检查是否在根目录
IS_IN_ROOT=false
if [ "$FILE_DIRNAME" = "." ] || [ "$FILE_DIRNAME" = "/" ] || [[ ! "$RELATIVE_PATH" =~ / ]]; then
    IS_IN_ROOT=true
fi

VIOLATION=""
SUGGESTION=""

# 如果在根目录,检查是否允许
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

        # 智能推荐位置
        if [[ "$FILE_BASENAME" =~ ^(QUICKSTART|quickstart|tutorial|guide) ]]; then
            SUGGESTION="docs/guides/"
        elif [[ "$FILE_BASENAME" =~ ^(API|api) ]] || [[ "$CONTENT" =~ (API|endpoint|/api/) ]]; then
            SUGGESTION="docs/api/"
        elif [[ "$FILE_BASENAME" =~ (architecture|design|system) ]]; then
            SUGGESTION="docs/architecture/"
        elif [[ "$FILE_BASENAME" =~ (standard|规范|convention) ]]; then
            SUGGESTION="docs/standards/"
        else
            SUGGESTION="docs/guides/"
        fi
    fi
fi

# 如果有违规,输出建议
if [ -n "$VIOLATION" ]; then
    CONTEXT_MESSAGE="📁 DOCUMENT ORGANIZATION SUGGESTION

⚠️ $VIOLATION

当前位置: $RELATIVE_PATH
建议位置: $SUGGESTION$FILE_BASENAME

💡 推荐操作:
  1. 使用 'git mv' 移动文档到建议位置
     命令: git mv $RELATIVE_PATH $SUGGESTION$FILE_BASENAME

  2. 更新所有引用此文档的链接
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
```

#### 自定义适配
**修改允许的根目录文件**:
```bash
ALLOWED_ROOT_FILES=(
    "README.md"
    "LICENSE"
    "package.json"
    # 添加项目特定的根文件
)
```

**修改文档分类规则**:
```bash
# 根据文件名模式推荐位置
if [[ "$FILE_BASENAME" =~ ^(tutorial|guide) ]]; then
    SUGGESTION="docs/tutorials/"
elif [[ "$FILE_BASENAME" =~ ^(spec|specification) ]]; then
    SUGGESTION="docs/specifications/"
fi
```

---

### 5. Stop Hook - Python质量门禁

**文件**: `stop-python-quality-gate.sh`
**大小**: 10,807 bytes
**Event**: Stop
**Timeout**: 120秒
**Exit Code**: 2 (阻塞) 或 0 (允许)

#### 功能
- 批量检查编辑过的Python文件
- 验证关键导入
- 运行语法检查 (`python -m py_compile`)
- 错误数≥阈值时阻止停止

#### 适用场景
- Claude会话结束前自动运行
- 防止提交有错误的代码
- 可配置错误阈值(默认10)

#### 核心代码示例

```bash
#!/usr/bin/env bash
# Event: Stop
# Purpose: Python代码质量门禁

set -euo pipefail

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"
EDIT_LOG_FILE="${PROJECT_ROOT}/.claude/edit_log.jsonl"
CONFIG_FILE="${PROJECT_ROOT}/.claude/build-checker-python.json"

# 读取配置
ERROR_THRESHOLD=$(jq -r '.errorThreshold // 10' "$CONFIG_FILE")
QUALITY_CHECKS=$(jq -r '.repos[env.CLAUDE_PROJECT_DIR].qualityChecks[]' "$CONFIG_FILE")

# 读取编辑过的文件
EDITED_FILES=()
if [ -f "$EDIT_LOG_FILE" ]; then
    while IFS= read -r line; do
        file=$(echo "$line" | jq -r '.file')
        EDITED_FILES+=("$file")
    done < "$EDIT_LOG_FILE"
fi

# 运行质量检查
TOTAL_ERRORS=0
ERROR_DETAILS=""

# 检查1: 关键导入
echo "检查关键导入..."
if ! python -c "from src.core import ConfigDrivenTableManager" 2>/dev/null; then
    ERROR_DETAILS="${ERROR_DETAILS}❌ 关键导入失败: ConfigDrivenTableManager\n"
    TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
fi

# 检查2: 后端语法
echo "检查Python语法..."
for file in "${EDITED_FILES[@]}"; do
    if [[ "$file" =~ \.py$ ]] && [[ "$file" =~ web/backend/ ]]; then
        if ! python -m py_compile "$PROJECT_ROOT/$file" 2>/dev/null; then
            ERROR_DETAILS="${ERROR_DETAILS}❌ 语法错误: $file\n"
            TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
        fi
    fi
done

# 检查错误阈值
if [ "$TOTAL_ERRORS" -ge "$ERROR_THRESHOLD" ]; then
    REASON="发现 $TOTAL_ERRORS 个错误 (阈值: $ERROR_THRESHOLD)

错误详情:
$ERROR_DETAILS

请修复这些错误后再停止会话。"

    ESCAPED_REASON=$(echo "$REASON" | jq -Rs .)

    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "Stop",
    "decision": "block",
    "reason": $ESCAPED_REASON,
    "errorDetails": {
      "totalErrors": $TOTAL_ERRORS,
      "threshold": $ERROR_THRESHOLD
    }
  }
}
EOF

    exit 2  # 阻塞
else
    echo "质量检查通过 ($TOTAL_ERRORS 个错误 < $ERROR_THRESHOLD 阈值)"
    exit 0  # 允许
fi
```

#### 配置依赖
- `build-checker-python.json` - 定义质量检查和阈值

---

### 6. SessionStart Hook - Task Master上下文注入

**文件**: `session-start-task-master-injector.sh`
**大小**: 9,065 bytes
**Event**: SessionStart
**Timeout**: 5秒
**Exit Code**: 0 (非阻塞)

#### 功能
- 会话开始时注入Task Master任务上下文
- 显示进行中的任务详情
- 列出高优先级待办任务
- 防止Claude上下文丢失

#### 适用场景
- 每次启动新Claude Code会话
- 自动恢复项目任务上下文
- 需要Task Master系统支持

#### 核心代码示例

```bash
#!/usr/bin/env bash
# Event: SessionStart
# Purpose: 注入Task Master上下文

set -euo pipefail

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"
TASKS_FILE="${PROJECT_ROOT}/.taskmaster/tasks/tasks.json"
MAX_OUTPUT_LINES=100

# 检查Task Master是否初始化
if [ ! -f "$TASKS_FILE" ]; then
    cat <<EOF
📋 Task Master 尚未初始化

建议运行: task-master init
参考文档: .taskmaster/CLAUDE.md
EOF
    exit 0
fi

# 读取任务数据
TASKS=$(cat "$TASKS_FILE")

# 提取进行中的任务
IN_PROGRESS_TASKS=$(echo "$TASKS" | jq -r '
    .tasks[]
    | select(.status == "in-progress")
    | "## Task \(.id): \(.title)\n\n**状态**: \(.status)\n**优先级**: \(.priority // "medium")\n\n**描述**: \(.description)\n\n**详情**: \(.details // "无")\n\n---"
')

# 提取高优先级待办任务(前3个)
PENDING_TASKS=$(echo "$TASKS" | jq -r '
    .tasks[]
    | select(.status == "pending" and .priority == "high")
    | "- Task \(.id): \(.title)"
' | head -n 3)

# 构建输出
OUTPUT="📋 TASK MASTER CONTEXT

### 进行中的任务

$IN_PROGRESS_TASKS

### 高优先级待办任务 (前3个)

$PENDING_TASKS

---
💡 使用 'task-master next' 获取下一个任务
"

# 限制输出行数
echo "$OUTPUT" | head -n "$MAX_OUTPUT_LINES"

exit 0
```

#### 项目依赖
- 需要Task Master系统: `.taskmaster/tasks/tasks.json`
- 可选: 如果没有Task Master,可以注释掉或适配其他项目管理工具

---

### 7. SessionEnd Hook - 会话清理

**文件**: `session-end-cleanup.sh`
**大小**: 3,651 bytes
**Event**: SessionEnd
**Timeout**: 5秒
**Exit Code**: 0 (非阻塞)

#### 功能
- 清理当前会话的编辑日志
- 截断日志文件到5,000行
- 保持会话隔离

#### 适用场景
- 每次Claude Code会话结束时自动运行
- 防止日志文件无限增长
- 保持项目整洁

#### 核心代码示例

```bash
#!/usr/bin/env bash
# Event: SessionEnd
# Purpose: 清理会话日志

set -euo pipefail

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"
EDIT_LOG_FILE="${PROJECT_ROOT}/.claude/edit_log.jsonl"
MAX_LOG_LINES=5000

INPUT_JSON=$(cat)
SESSION_ID=$(echo "$INPUT_JSON" | jq -r '.session_id // "unknown"')

# 如果日志文件不存在,退出
if [ ! -f "$EDIT_LOG_FILE" ]; then
    exit 0
fi

# 清理当前会话的记录
if TMP_FILE=$(mktemp); then
    jq --arg sid "$SESSION_ID" 'select(.session_id != $sid)' "$EDIT_LOG_FILE" > "$TMP_FILE"

    if [ -s "$TMP_FILE" ]; then
        mv "$TMP_FILE" "$EDIT_LOG_FILE"
    else
        rm -f "$TMP_FILE"
    fi
fi

# 截断日志文件
if [ -f "$EDIT_LOG_FILE" ]; then
    LINE_COUNT=$(wc -l < "$EDIT_LOG_FILE")

    if [ "$LINE_COUNT" -gt "$MAX_LOG_LINES" ]; then
        if TMP_FILE=$(mktemp); then
            tail -n "$MAX_LOG_LINES" "$EDIT_LOG_FILE" > "$TMP_FILE"
            mv "$TMP_FILE" "$EDIT_LOG_FILE"
        fi
    fi
fi

exit 0
```

---

## 配置文件详解

### 1. settings.json - 主配置文件

**路径**: `.claude/settings.json`
**用途**: 注册所有hooks到Claude Code

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [{
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/user-prompt-submit-skill-activation.sh"
        }],
        "timeout": 5
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-file-edit-tracker.sh"
        }],
        "timeout": 3
      },
      {
        "matcher": "Edit|Write",
        "hooks": [{
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-database-schema-validator.sh"
        }],
        "timeout": 5
      },
      {
        "matcher": "Write",
        "hooks": [{
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-document-organizer.sh"
        }],
        "timeout": 5
      }
    ],
    "Stop": [
      {
        "hooks": [{
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/stop-python-quality-gate.sh"
        }],
        "timeout": 120
      }
    ],
    "SessionStart": [
      {
        "hooks": [{
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start-task-master-injector.sh"
        }],
        "timeout": 5
      }
    ],
    "SessionEnd": [
      {
        "hooks": [{
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-end-cleanup.sh"
        }],
        "timeout": 5
      }
    ]
  }
}
```

**关键字段说明**:
- `matcher`: 过滤工具名称 (如 `Edit|Write`)
- `timeout`: 超时时间(秒)
- `command`: Hook脚本路径 (使用 `$CLAUDE_PROJECT_DIR` 环境变量)

---

### 2. skill-rules.json - Skill激活规则

**路径**: `.claude/skill-rules.json`
**用途**: 定义UserPromptSubmit hook的skill激活规则

**完整文件** (338行): 见 `.claude/skill-rules.json`

**核心结构**:
```json
{
  "version": "2.0",
  "description": "Skill activation triggers",
  "skills": {
    "backend-dev-guidelines": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "high",
      "description": "Backend development patterns",
      "promptTriggers": {
        "keywords": ["backend", "后端", "API", "接口"],
        "intentPatterns": [
          "(create|add|implement).*?(route|endpoint|API)"
        ]
      },
      "fileTriggers": {
        "pathPatterns": ["web/backend/app/**/*.py"],
        "contentPatterns": ["APIRouter", "FastAPI"]
      }
    },
    "database-architecture-guidelines": {
      "type": "domain",
      "enforcement": "warn",
      "priority": "critical",
      "description": "Database architecture rules",
      "promptTriggers": {
        "keywords": ["database", "数据库", "TDengine", "PostgreSQL"]
      },
      "fileTriggers": {
        "pathPatterns": ["src/data_access/**/*.py", "config/table_config.yaml"]
      }
    }
  }
}
```

**自定义适配**:
1. 修改 `skills` 对象,添加/删除/修改skill定义
2. 更新 `keywords` 数组,匹配项目特定关键词
3. 更新 `pathPatterns`,匹配项目文件结构
4. 调整 `priority`: `critical` > `high` > `medium` > `low`

---

### 3. build-checker-python.json - Python质量检查配置

**路径**: `.claude/build-checker-python.json`
**用途**: 配置Stop hook的质量检查规则

```json
{
  "version": "2.0",
  "description": "Python quality checks for Stop hook",
  "errorThreshold": 10,
  "repos": {
    "/opt/claude/mystocks_spec": {
      "qualityChecks": [
        {
          "name": "critical_imports",
          "description": "验证关键导入",
          "command": "python -c 'from src.core import ConfigDrivenTableManager'",
          "critical": true,
          "timeout": 5
        },
        {
          "name": "backend_syntax",
          "description": "后端语法检查",
          "command": "find web/backend/app -name '*.py' -exec python -m py_compile {} \\;",
          "critical": false,
          "timeout": 30
        }
      ]
    }
  }
}
```

**自定义适配**:
1. 修改 `errorThreshold` 调整容错度
2. 更新 `repos` 键为新项目路径
3. 添加/修改 `qualityChecks` 数组:
   - `name`: 检查名称
   - `command`: 执行的检查命令
   - `critical`: 是否为关键检查
   - `timeout`: 单个检查超时(秒)

**示例 - 添加mypy类型检查**:
```json
{
  "name": "mypy_check",
  "description": "类型检查",
  "command": "mypy src/ --ignore-missing-imports",
  "critical": false,
  "timeout": 60
}
```

---

## 迁移步骤

### 最小迁移 (核心功能)

#### 步骤1: 复制必需文件

```bash
# 创建目标项目的.claude目录
cd /path/to/new-project
mkdir -p .claude/hooks

# 复制核心配置文件
cp /path/to/mystocks/.claude/settings.json .claude/
cp /path/to/mystocks/.claude/skill-rules.json .claude/
cp /path/to/mystocks/.claude/build-checker-python.json .claude/

# 复制所有hook脚本
cp /path/to/mystocks/.claude/hooks/*.sh .claude/hooks/

# 添加执行权限
chmod +x .claude/hooks/*.sh
```

#### 步骤2: 修改settings.json路径

如果项目路径不同,需要更新环境变量或使用相对路径:

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/user-prompt-submit-skill-activation.sh"
      }]
    }]
  }
}
```

`$CLAUDE_PROJECT_DIR` 会自动解析为当前项目根目录。

#### 步骤3: 适配配置文件

**修改 build-checker-python.json**:
```json
{
  "repos": {
    "/path/to/new-project": {  // 更新为新项目路径
      "qualityChecks": [
        // 根据新项目调整检查命令
      ]
    }
  }
}
```

**修改 skill-rules.json**:
```json
{
  "skills": {
    "backend-dev-guidelines": {
      "fileTriggers": {
        "pathPatterns": [
          "src/**/*.py",          // 更新为新项目路径
          "api/**/*.py"
        ]
      }
    }
  }
}
```

#### 步骤4: 禁用项目特定hooks (可选)

如果不需要某些hooks,可以从 `settings.json` 中删除:

**删除Database Validator** (如果项目不是双数据库架构):
```json
{
  "PostToolUse": [
    // 删除这个hook注册
    // {
    //   "matcher": "Edit|Write",
    //   "hooks": [{
    //     "command": "...database-schema-validator.sh"
    //   }]
    // }
  ]
}
```

**删除Task Master Injector** (如果项目没有Task Master):
```json
{
  "SessionStart": [
    // 删除这个hook注册或修改为其他上下文注入
  ]
}
```

#### 步骤5: 测试hooks

```bash
# 启动Claude Code
cd /path/to/new-project
claude

# 测试UserPromptSubmit hook
# 输入包含关键词的提示词,检查skill是否激活

# 测试PostToolUse hook
# 编辑一个文件,检查是否记录到edit_log.jsonl

# 测试Stop hook
# 尝试停止会话,检查质量门禁是否工作
```

---

### 完整迁移 (包含文档)

除了上述步骤,还需要复制文档文件:

```bash
# 复制文档文件
cp /path/to/mystocks/.claude/hooks/README.md .claude/hooks/
cp /path/to/mystocks/.claude/hooks/FILE_ORGANIZATION_GUIDE.md .claude/hooks/
cp /path/to/mystocks/.claude/hooks/HOOKS_IMPROVEMENT_COMPLETION_REPORT.md .claude/hooks/
```

---

## 自定义适配指南

### 适配场景1: 非Python项目 (如TypeScript/Node.js)

#### 修改Stop Hook

将 `stop-python-quality-gate.sh` 适配为TypeScript检查:

```bash
#!/usr/bin/env bash
# 修改后的Stop hook for TypeScript

# 检查TypeScript编译
echo "检查TypeScript编译..."
if ! npx tsc --noEmit 2>/dev/null; then
    ERROR_DETAILS="${ERROR_DETAILS}❌ TypeScript编译错误\n"
    TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
fi

# 检查ESLint
echo "检查ESLint..."
if ! npx eslint src/ 2>/dev/null; then
    ERROR_DETAILS="${ERROR_DETAILS}❌ ESLint检查失败\n"
    TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
fi

# 运行测试
echo "运行单元测试..."
if ! npm test 2>/dev/null; then
    ERROR_DETAILS="${ERROR_DETAILS}❌ 单元测试失败\n"
    TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
fi
```

#### 修改build-checker配置

创建 `build-checker-typescript.json`:
```json
{
  "version": "1.0",
  "errorThreshold": 5,
  "repos": {
    "/path/to/ts-project": {
      "qualityChecks": [
        {
          "name": "typescript_compile",
          "command": "npx tsc --noEmit",
          "critical": true
        },
        {
          "name": "eslint",
          "command": "npx eslint src/",
          "critical": false
        },
        {
          "name": "unit_tests",
          "command": "npm test",
          "critical": true
        }
      ]
    }
  }
}
```

---

### 适配场景2: 单数据库项目

如果项目只有一个数据库,可以:

**选项1: 删除Database Validator Hook**
```json
// settings.json - 删除database-schema-validator注册
{
  "PostToolUse": [
    // 删除这个hook
  ]
}
```

**选项2: 改为通用SQL检查**

修改 `post-tool-use-database-schema-validator.sh`:
```bash
# 检查危险SQL操作
declare -A DANGEROUS_PATTERNS=(
    ["DROP TABLE"]="⚠️ 危险操作: DROP TABLE"
    ["TRUNCATE"]="⚠️ 危险操作: TRUNCATE"
    ["DELETE FROM.*WHERE 1=1"]="⚠️ 危险操作: 无条件DELETE"
    ["UPDATE.*SET.*WHERE 1=1"]="⚠️ 危险操作: 无条件UPDATE"
)
```

---

### 适配场景3: 没有Task Master的项目

#### 选项1: 删除SessionStart Hook

```json
// settings.json
{
  "SessionStart": []  // 清空
}
```

#### 选项2: 改为Git Context注入

修改 `session-start-task-master-injector.sh`:
```bash
#!/usr/bin/env bash
# 注入Git最近提交和分支信息

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"

cd "$PROJECT_ROOT" || exit 0

cat <<EOF
📋 GIT CONTEXT

### 当前分支
$(git branch --show-current 2>/dev/null || echo "未知")

### 最近5次提交
$(git log --oneline -5 2>/dev/null || echo "无Git历史")

### 未提交的更改
$(git status --short 2>/dev/null || echo "无更改")
EOF

exit 0
```

---

### 适配场景4: 自定义文档组织规则

修改 `post-tool-use-document-organizer.sh`:

```bash
# 自定义允许的根文件
ALLOWED_ROOT_FILES=(
    "README.md"
    "LICENSE"
    "package.json"        # Node.js项目
    "Cargo.toml"          # Rust项目
    "setup.py"            # Python包
)

# 自定义文档分类
if [[ "$FILE_BASENAME" =~ ^(tutorial|guide) ]]; then
    SUGGESTION="docs/tutorials/"
elif [[ "$FILE_BASENAME" =~ ^(RFC|proposal) ]]; then
    SUGGESTION="docs/rfcs/"
elif [[ "$FILE_BASENAME" =~ ^(release|changelog) ]]; then
    SUGGESTION="docs/releases/"
fi
```

---

### 适配场景5: 修改Skill激活规则

在 `skill-rules.json` 中添加新的skill或修改现有skill:

```json
{
  "skills": {
    "rust-dev-guidelines": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "high",
      "description": "Rust development patterns",
      "promptTriggers": {
        "keywords": ["rust", "cargo", "trait", "lifetime"],
        "intentPatterns": [
          "(create|implement|add).*?(struct|trait|module)"
        ]
      },
      "fileTriggers": {
        "pathPatterns": ["src/**/*.rs", "tests/**/*.rs"],
        "contentPatterns": [
          "pub struct",
          "impl.*for",
          "fn.*->.*Result"
        ]
      }
    }
  }
}
```

---

## 常见问题和解决方案

### Q1: Hook没有执行

**可能原因**:
1. 权限问题: `chmod +x .claude/hooks/*.sh`
2. 路径错误: 检查 `settings.json` 中的 `command` 路径
3. 语法错误: 运行 `bash -n hook-file.sh` 检查语法

**调试方法**:
```bash
# 启用调试模式
export HOOK_NAME_DEBUG=true

# 手动运行hook
echo '{"user_message":"test","session_id":"test"}' | \
    .claude/hooks/user-prompt-submit-skill-activation.sh
```

### Q2: Stop Hook太严格

修改 `build-checker-python.json`:
```json
{
  "errorThreshold": 20  // 增加阈值
}
```

或临时禁用:
```json
{
  "Stop": []  // 清空Stop hooks
}
```

### Q3: 编辑日志过大

检查 `edit_log.jsonl` 大小:
```bash
wc -l .claude/edit_log.jsonl
```

手动清理:
```bash
tail -n 1000 .claude/edit_log.jsonl > .claude/edit_log.jsonl.tmp
mv .claude/edit_log.jsonl.tmp .claude/edit_log.jsonl
```

或修改 `session-end-cleanup.sh` 中的 `MAX_LOG_LINES`。

### Q4: Skill没有自动激活

检查 `skill-rules.json`:
1. 关键词是否匹配
2. 文件路径模式是否正确
3. Regex语法是否有误

手动测试关键词匹配:
```bash
echo "创建一个新的API接口" | grep -qiE "(API|接口)" && echo "匹配"
```

---

## 版本历史

- **v2.0** (2025-11-11): Python/FastAPI架构,7个hooks
  - 迁移自TypeScript/Node.js架构
  - 新增: Database Validator, Document Organizer
  - 更新: Skill Rules (双语支持)

- **v1.0** (2025-11之前): TypeScript/Node.js架构
  - 6个hooks
  - Stop hook使用 `npm build`

---

## 支持和维护

### 报告问题
1. 启用调试模式: `export HOOK_NAME_DEBUG=true`
2. 检查hook输出和stderr
3. 验证配置文件JSON语法: `jq . config.json`

### 获取帮助
- Claude官方文档: https://docs.claude.com/en/docs/claude-code/hooks
- 项目README: `.claude/hooks/README.md`
- 完成报告: `.claude/hooks/HOOKS_IMPROVEMENT_COMPLETION_REPORT.md`

---

**创建日期**: 2025-11-11
**维护者**: Claude Code Assistant
**最后更新**: 2025-11-11
**文档版本**: 1.0
