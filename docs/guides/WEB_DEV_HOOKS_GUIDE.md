# MyStocks Web开发Hook配置方案

**文档版本**: v1.0
**创建日期**: 2025-12-30
**目的**: 建立专门针对Web开发的Hook追踪系统，避免开发文档被移位

---

## 📊 设计方案

### 核心原则

1. **分离Web开发文档**: 将Web相关Hook追踪文件独立管理，避免与Python后端开发文档混淆
2. **集中日志管理**: 建立统一的Web开发日志记录机制
3. **智能文档分类**: 自动识别Web开发文档类型（TypeScript、VUE、React等）并建议正确位置
4. **避免误判**: 配置精确的白名单，避免误报Web开发文档

### 目录结构

```
.claude/
├── settings.json                              # 主配置
├── settings.local.json                        # 本地开发配置
├── skill-rules.json                        # Skill激活规则
├── build-checker-web.json                    # Web前端质量检查
├── web-dev-tracker-hooks/                    # Web开发Hook追踪
└── hooks/
    ├── file-tracker.sh                        # 文件编辑追踪（Web专用）
    ├── document-organizer.sh                   # 文档组织检查（Web专用）
    ├── whitelist-config.json                 # Web开发白名单配置
    └── web-file-tracker.sh                    # Web文件追踪脚本（新）
```

**Web文档目录**:
```
docs/
├── web-dev/                                   # Web开发文档专用
│   ├── tracing/                            # Hook追踪记录
│   ├── guidelines/                         # 开发指南
│   └── archived/                           # 归档的追踪记录
```

---

## 🎯 Web相关Hook功能

### 1. PostToolUse Hook: Web文件编辑追踪

**Hook名称**: `post-tool-use-web-file-tracker.sh`

**触发事件**: PostToolUse
**Matcher**: `Edit|Write` （仅追踪文件操作）
**Timeout**: 3秒
**Exit Code**: 0（非阻塞）

**功能**:
```
检测文件操作
    ↓
记录文件信息
  - file_path: 相对路径
  - absolute_path: 绝对路径
  - tool: Edit 或 Write
  - language: 文件类型检测
  - file_size: 文件大小
  - session_id: 会话UUID
  - timestamp: ISO8601时间戳
    ↓
分析文件类型
  ├── .ts → TypeScript
  ├── .tsx → React组件
  ├── .vue → Vue组件
  ├── .jsx → React组件
  ├── .css → 样式表
  ├── .html → HTML页面
  ├── .json → 配置文件
  └── .xml → 配置文件
    ↓
分类存储
  ├── docs/web-dev/tracing/          # 所有Web编辑记录
  ├── docs/web-dev/archived/          # 归档的追踪记录
  └── .claude/edit_log.jsonl        # 全局编辑日志
```

**分类规则**:
```json
{
  "file_categories": {
    ".ts": {
      "category": "TypeScript Source",
      "directory": "src/",
      "priority": "high"
    },
    ".tsx": {
      "category": "React Component",
      "directory": "web/frontend/src/components/",
      "priority": "high"
    },
    ".vue": {
      "category": "Vue Component",
      "directory": "web/frontend/src/components/",
      "priority": "high"
    },
    ".jsx": {
      "category": "React JSX",
      "directory": "web/frontend/src/",
      "priority": "medium"
    },
    ".css": {
      "category": "Stylesheet",
      "directory": "web/frontend/src/styles/",
      "priority": "low"
    },
    ".html": {
      "category": "HTML Page",
      "directory": "web/frontend/src/pages/",
      "priority": "high"
    },
    ".json": {
      "category": "Configuration",
      "directory": "config/",
      "priority": "low"
    },
    ".yaml": {
      "category": "Configuration",
      "directory": "config/",
      "priority": "low"
    }
  }
}
```

---

### 2. PostToolUse Hook: Web文档组织器

**Hook名称**: `post-tool-use-web-document-organizer.sh`

**触发事件**: PostToolUse
**Matcher**: `Write` （仅追踪Write操作，避免Read操作误报）
**Timeout**: 3秒
**Exit Code**: 0（非阻塞）

**功能**:
```
检测到Write操作
    ↓
检查文件扩展名
  ├── .md/.rst → docs/web-dev/guides/
  ├── .yaml/.yml → config/
  ├── .json → config/
  └── .txt → docs/
    ↓
检查文件路径和内容
  ├── 检测文档类型
  ├── 分析标题和结构
  └── 提取元数据
    ↓
建议正确位置
  ├── API文档 → docs/api/
  ├── 前端架构文档 → docs/architecture/
  ├── 开发教程 → docs/tutorials/
  └── 部署文档 → docs/deployment/
    ↓
验证文件位置
  └── 提供Git mv命令建议
```

**文档分类规则**:
```json
{
  "document_categories": {
    "api_docs": {
      "patterns": ["^docs/api/.*\\.(md|rst)$"],
      "target": "docs/api/",
      "description": "API文档"
    },
    "guides": {
      "patterns": ["docs/(tutorials|guides)/.*\\.md$"],
      "target": "docs/web-dev/guides/",
      "description": "开发指南文档"
    },
    "architecture": {
      "patterns": ["docs/architecture/.*\\.md$"],
      "target": "docs/architecture/",
      "description": "架构文档"
    },
    "deployment": {
      "patterns": ["docs/deployment/.*\\.md$"],
      "target": "docs/deployment/",
      "description": "部署文档"
    },
    "standards": {
      "patterns": ["docs/(standard|规范|convention).*$"],
      "target": "docs/standards/",
      "description": "标准文档"
    }
  }
}
```

---

### 3. PostToolUse Hook: Web代码质量检查

**Hook名称**: `post-tool-use-web-code-quality-check.sh`

**触发事件**: PostToolUse
**Matcher**: `Read` （读取文件内容）
**Timeout**: 5秒
**Exit Code**: 0（非阻塞，仅警告）

**功能**:
```
检测到Read操作（文件内容）
    ↓
检查文件扩展名
  ├── .ts/.tsx → TypeScript文件
  ├── .vue → Vue组件
  └── .js → JavaScript文件
    ↓
代码质量检查
  ├── ESLint检查（Web前端）
  ├── TSLint检查（TypeScript）
  ├── Stylelint检查（CSS）
  ├── ESLint Plugin（React Hooks）
  └── 空间复杂性检查
    ↓
生成检查结果
  - 错误数量
  - 警告数量
  - 建议
```

**代码质量规则**:
```json
{
  "eslint_rules": {
    "@typescript-eslint/no-explicit-any": "warn",
    "@typescript-eslint/explicit-module-boundary-types": "error",
    "react-hooks/rules-of-hooks": "warn",
    "no-console": "off",
    "react/jsx-uses-react": "error"
  },
  "tslint_rules": {
    "no-any": "error",
    "no-console": "off",
    "no-unused-vars": "warn"
  },
  "linters": {
    "eslint": {
      "command": "cd web/frontend && eslint \"{\\\"extends\\\": [\\\"standard\\\",\\\"plugin:react-hooks\\\"]}\" $(dirname \"$file\")"
    },
    "tslint": {
      "command": "tsc --noEmit $(dirname \"$file\")"
    }
  }
}
```

---

### 4. Stop Hook: 前端质量门禁

**Hook名称**: `stop-web-quality-gate.sh`

**触发事件**: Stop
**Matcher**: `-`（所有工具）
**Timeout**: 120秒
**Exit Code**: 2（阻塞 - 质量检查未通过）
**Exit Code**: 0（允许 - 质量检查通过）

**功能**:
```
会话停止前检查
    ↓
检查Web前端文件
  ├── 扫描 web/frontend/src/
  ├── 检查是否有TypeScript编译错误
  ├── 检查ESLint错误
  └── 检查TSLint错误
    ↓
统计错误
  ├─ TypeScript错误数（0个）
  ├─ ESLint错误数（0个）
  └─ TSLint错误数（0个）
    ↓
比较阈值
  ├─ 错误数 = 0 → 允许停止（exit 0）
  ├─ 警告数 ≤ 5 → 允许停止（exit 0）
  ├─ 警告数 > 10 → 阻止并警告（exit 0）
  └─ 错误数 > 0 → 阻止（exit 2）
    ↓
输出JSON结果
  {
    "hookSpecificOutput": {
      "decision": "allow" | "block",
      "errorDetails": "TypeScript编译错误: 3个\nESLint错误: 2个\nTSLint错误: 1个",
      "webOnly": true
    }
  }
```

---

## 🔧 配置文件

### settings.json 主配置

```json
{
  "version": "2.0",
  "description": "MyStocks Web Development Hooks配置",
  "web_dev_hooks": {
    "file_tracker": {
      "enabled": true,
      "timeout": 3
    },
    "document_organizer": {
      "enabled": true,
      "timeout": 3
    },
    "code_quality_check": {
      "enabled": true,
      "timeout": 5
    }
  },
  "stop_hooks": {
    "web_quality_gate": {
      "enabled": true,
      "timeout": 120
    }
  },
  "file_categories": {
    ".ts": {
      "category": "TypeScript Source",
      "directory": "src/",
      "priority": "high"
    },
    ".tsx": {
      "category": "React Component",
      "directory": "web/frontend/src/components/",
      "priority": "high"
    },
    ".vue": {
      "category": "Vue Component",
      "directory": "web/frontend/src/components/",
      "priority": "high"
    },
    ".jsx": {
      "web/frontend/src/": "React JSX",
      "priority": "medium"
    },
    ".css": {
      "web/frontend/src/styles/",
      "priority": "low"
    },
    ".html": {
      "web/frontend/src/pages/",
      "priority": "high"
    },
    ".json": {
      "config/",
      "priority": "low"
    },
    ".yaml": {
      "config/",
      "priority": "low"
    }
  },
  "document_categories": {
    "api_docs": {
      "patterns": ["^docs/api/.*\\.(md|rst)$"],
      "target": "docs/api/"
    },
    "guides": {
      "patterns": ["docs/(tutorials|guides)/.*\\.md$"],
      "target": "docs/web-dev/guides/"
    },
    "architecture": {
      "patterns": ["docs/architecture/.*\\.md$"],
      "target": "docs/architecture/"
    },
    "deployment": {
      "patterns": ["docs/deployment/.*\\.md$"],
      "target": "docs/deployment/"
    }
  },
  "whitelist": {
    "web_dev_allowed_dirs": [
      "web/frontend/src/",
      "web/backend/app/",
      "config/",
      "docs/",
      "web/",
      "docs/guides/"
      "docs/api/",
      "docs/architecture/",
      "docs/standards/"
    ],
    "web_dev_allowed_files": [
      "README.md",
      "package.json",
      "tsconfig.json",
      "vite.config.ts",
      "docker-compose.yml"
    ]
  }
}
```

---

## 📁 Web开发Hook脚本

### 1. web-dev-file-tracker.sh

```bash
#!/usr/bin/env bash
set -euo pipefail

# Web开发文件追踪Hook
# 版本: 1.0
# 用途: 自动追踪所有Web开发相关文件的编辑操作

# 配置
CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
WEB_DEV_DIR="docs/web-dev"
WEB_DEV_LOG="${WEB_DEV_DIR}/tracing/web-edit-tracker.jsonl"

# 日志函数
web_log() {
    echo "[WebDev Tracker] $(date +%Y-%m-%dT%H:%M:%SZ): $*" >&2
}

# 读取输入JSON
INPUT_JSON=$(cat)

# 验证JSON格式
if ! echo "$INPUT_JSON" | jq empty 2>/dev/null; then
    web_log "Invalid JSON input"
    exit 0
fi

# 提取文件信息
FILE_PATH=$(echo "$INPUT_JSON" | jq -r '.tool_input.file_path // empty')
TOOL_NAME=$(echo "$INPUT_JSON" | jq -r '.tool_name // "Unknown"')
SESSION_ID=$(echo "$INPUT_JSON" | jq -r '.session_id // "unknown"')
CWD=$(echo "$INPUT_JSON" | jq -r '.cwd // "unknown"')

web_log "File operation detected"
web_log "  File: $FILE_PATH"
web_log "  Tool: $TOOL_NAME"
web_log "  Session: $SESSION_ID"

# 检查文件是否存在
if [ ! -z "$FILE_PATH" ]; then
    # 获取文件信息
    if [ -f "$FILE_PATH" ]; then
        ABSOLUTE_PATH=$(cd "$(dirname "$FILE_PATH")" && pwd)/$(basename "$FILE_PATH")
        FILE_SIZE=$(stat -f "$FILE_PATH" | awk '{print $5}')
    else
        ABSOLUTE_PATH="unknown"
        FILE_SIZE="unknown"
    fi

    # 检测文件扩展名
    FILE_EXTENSION="${FILE_PATH##*.}"

    # Web文件类型检测
    case "$FILE_EXTENSION" in
        .ts|tsx)
            FILE_TYPE="TypeScript"
            FILE_LANGUAGE="TypeScript"
            FILE_DIR="src/"
            PRIORITY="high"
            ;;
        .vue)
            FILE_TYPE="Vue Component"
            FILE_LANGUAGE="Vue"
            FILE_DIR="web/frontend/src/components/"
            PRIORITY="high"
            ;;
        .jsx)
            FILE_TYPE="React JSX"
            FILE_LANGUAGE="JavaScript"
            FILE_DIR="web/frontend/src/"
            PRIORITY="medium"
            ;;
        .css)
            FILE_TYPE="Stylesheet"
            FILE_LANGUAGE="CSS"
            FILE_DIR="web/frontend/src/styles/"
            PRIORITY="low"
            ;;
        .html)
            FILE_TYPE="HTML Page"
            FILE_LANGUAGE="HTML"
            FILE_DIR="web/frontend/src/pages/"
            PRIORITY="high"
            ;;
        .json)
            FILE_TYPE="Configuration"
            FILE_LANGUAGE="JSON"
            FILE_DIR="config/"
            PRIORITY="low"
            ;;
        .yaml|yml)
            FILE_TYPE="Configuration"
            FILE_LANGUAGE: YAML"
            FILE_DIR="config/"
            PRIORITY="low"
            ;;
        *)
            FILE_TYPE="Unknown"
            FILE_LANGUAGE="Unknown"
            FILE_DIR="unknown"
            PRIORITY="low"
            ;;
    esac

    web_log "  Type: $FILE_TYPE ($FILE_LANGUAGE)"
    web_log "  Dir: $FILE_DIR (priority: $PRIORITY)"
    web_log "  Size: $FILE_SIZE"

    # 自动分类并记录
    TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    # 创建Web追踪目录
    mkdir -p "$WEB_DEV_LOG"

    # 记录到Web专用日志
    cat >> "$WEB_DEV_LOG" <<EOF
{"timestamp": "$TIMESTAMP", "file_path": "$FILE_PATH", "absolute_path": "$ABSOLUTE_PATH", "tool": "$TOOL_NAME", "session_id": "$SESSION_ID", "type": "$FILE_TYPE", "language": "$FILE_LANGUAGE", "priority": "$priority", "size": "$FILE_SIZE"}
EOF

    web_log "  Recorded to: $WEB_DEV_LOG"

    # 同步到全局日志（保持向后兼容）
    mkdir -p "$(dirname ".claude/edit_log.jsonl")"
    cat >> ".claude/edit_log.jsonl" <<EOF
{"timestamp": "$TIMESTAMP", "file_path": "$FILE_PATH", "absolute_path": "$else: [ "$ABSOLUTE_PATH" ]", "session_id": "$SESSION_ID", "type": "$FILE_TYPE", "language": "$FILE_LANGUAGE", "priority": "$priority"}
EOF

    web_log "  Synced to .claude/edit_log.jsonl"

else
    web_log "  Empty file_path, skipping"
fi

# 返回成功
exit 0
```

---

### 2. post-tool-use-web-document-organizer.sh

```bash
#!/usr/bin/env bash
set -euo pipefail

# Web文档组织器Hook
# 版本: 1.0
# 用途: 自动建议Web文档的存放位置

# 配置
CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
WEB_DEV_DIR="docs/web-dev"
WEB_DEV_LOG="$WEB_DEV_LOG/organizer.log"

# 白名单 - 这些文件不会被移动
ALLOWED_ROOT_FILES=(
    "README.md"
    "package.json"
    "tsconfig.json"
    "vite.config.ts"
    "docker-compose.yml"
    ".pre-commit-config.yaml"
    ".gitignore"
)

# 文档分类映射
DOC_MAP=(
    "docs/api/GUIDE.md -> $WEB_DEV_DIR/api/"
    "docs/architecture/ARCHITECTURE.md -> $WEB_DEV_DIR/architecture/"
    "docs/deployment/DEPLOYMENT.md -> $WEB_DEV_DIR/deployment/"
    "docs/(tutorials|guides)/GUIDE.md -> $WEB_DEV_DIR/guides/"
    "docs/(标准|规范|convention).+md -> $WEB_DEV_DIR/standards/"
)

# 文档类型映射
DOC_TYPE_MAP=(
    ".md" -> "Markdown文档"
    ".rst" -> "reStructuredText文档"
    ".txt" -> "纯文文档"
    ".json" -> "JSON配置"
    ".yaml" -> "YAML配置"
    ".yml" -> "YAML配置"
    ".html" -> "HTML页面"
    "css" -> "CSS样式表"
)

# 日志函数
web_org_log() {
    echo "[Web Organizer] $(date +%Y-%m-%dT%H:%M:%SZ): $*" >&2
}

# 读取输入JSON
INPUT_JSON=$(cat)

# 验证JSON格式
if ! echo "$INPUT_JSON" | jq empty 2>/dev/null; then
    web_org_log "Invalid JSON input"
    exit 0
fi

# 提取信息
FILE_PATH=$(echo "$INPUT_JSON" | jq -r '.tool_input.file_path // empty')
CONTENT=$(echo "$INPUT_JSON" | jq -r '.tool_input.content // empty')

if [ -z "$FILE_PATH" ]; then
    web_org_log "Empty file_path, skipping"
    exit 0
fi

# 检查是否在白名单中
for allowed in "${ALLOWED_ROOT_FILES[@]}"; do
    if [ "$(basename "$FILE_PATH")" == "$allowed" ]; then
        web_org_log "File in whitelist, skipping"
        exit 0
    fi
done

# 检测文件扩展名
FILE_EXT="${FILE_EXT##*.}"

# 检查文档类型
for doc_type in "${!DOC_TYPE_MAP[@]}"; do
    EXTENSION="${doc_type%% ->*}"
    if [ "$FILE_EXT" == "$EXTENSION" ]; then
        TYPE="${DOC_TYPE##*}"
        break
    fi
done

if [ -z "$TYPE" ]; then
    TYPE="Unknown"
fi

# 检查文件路径
if [[ "$FILE_PATH" =~ ^docs/api/ ]]; then
    RECOMMENDATION="$WEB_DEV_DIR/api/"
elif [[ "$FILE_PATH" =~ ^docs/.*guide/.* ]]; then
    RECOMMENDATION="$WEB_DEV_DIR/guides/"
elif [[ "$FILE_PATH" =~ ^docs/architecture/.* ]]; then
    RECOMMENDATION="$WEB_DEV_DIR/architecture/"
elif [[ "$FILE_PATH" =~ ^docs/deployment/ ]]; then
    RECOMMENDATION="$WEB_DEV_DIR/deployment/"
elif [[ "$FILE_PATH" =~ ^docs/(标准|规范|convention) ]]; then
    RECOMMENDATION="$WEB_DEV_DIR/standards/"
elif [[ "$FILE_PATH" =~ ^docs/.*guide.*/ ]]; then
    RECOMMENDATION="$WEB_DEV_DIR/guides/"
else
    RECOMMENDATION=""
fi

# 如果有推荐位置，输出建议
if [ -n "$RECOMMENDATION" ]; then
    # 提取相对路径
    if [[ "$FILE_PATH" == /* ]]; then
        RELATIVE_PATH="${FILE_PATH#*}"
    fi

    # 创建Web开发文档建议文档
    WEB_DEV_GUIDE="docs/web-dev/GUIDE.md"

    # 如果文档不存在，创建它
    if [ ! -f "$WEB_DEV_GUIDE" ]; then
        mkdir -p "$(dirname "$WEB_DEV_GUIDE")"
        cat > "$WEB_DEV_GUIDE" << 'EOF'
# MyStocks Web开发Hook追踪器使用指南

## 📚 文档分类规则

### API文档
```bash
# API文档应存放在这里
docs/api/
├── 以下文档路径符合API文档规则：
docs/api/CLAUDE_AGENTS_GUIDE.md
docs/api/AGENTS_QUICK_REFERENCE.md
docs/api/WEB_PAGES_API_MAPPING.md
docs/api/AGENTS_AUDIT_REPORT.md
```

### 开发指南
```bash
# 开发指南应存放在这里
docs/web-dev/guides/
├── 以下文档路径符合开发指南规则：
docs/guides/WEB_AUTOMATION_TEST_PLAN.md
docs/guides/WEB_AUTOMATION_TEST_QUICK_REFERENCE.md
docs/guides/WEB_AUTOMATION_TEST_PLAN.md
docs/guides/WEB_AUTOMATION_TEST_QUICK_REFERENCE.md
```

### 部署文档
```bash
# 部署文档应存放在这里
docs/deployment/
├── 以下文档路径符合部署文档规则:
docs/deployment/DEPLOYMENT.md
docs/deployment/WEB_AUTOMATION_DEPLOYMENT.md
docs/deployment/APIFOX_INTEGRATION_COMPLETE.md
```

### 架构文档
```bash
# 架构文档应存放在这里
docs/architecture/
├── 以下文档路径符合架构文档规则:
docs/architecture/ARCHITECTURE.md
docs/ARCHITECTURE_REVIEW_SUMMARY.md
docs/architecture/DATA_SOURCE_ARCHITECTURE.md
docs/architecture/API_ARCHITECTURE.md
docs/architecture/DATABASE_ARCHITECTURE.md
```

---

## 🔗 自动化流程

### 1. Hook安装命令

```bash
# 创建Web开发Hook目录
mkdir -p .claude/web-dev-hooks

# 复制Web专用Hook脚本
cp scripts/maintenance/file_cleanup.sh .claude/web-dev-hooks/file-cleanup.sh
cp scripts/maintenance/organize-files.sh .claude/web-dev-hooks/document-organizer.sh

# 添加执行权限
chmod +x .claude/web-dev-hooks/*.sh

# 验证Hook脚本
ls -la .claude/web-dev-hooks/
```

### 2. 配置注册

编辑 `.claude/settings.json`，添加Web开发Hook配置

```json
{
  "version": "2.0",
  "description": "MyStocks Web Development System - Hooks",
  "web_dev_hooks": {
    "enabled": true,
    "file_tracker": {
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/web-dev-hooks/file-tracker.sh"
      }],
      "timeout": 3
    },
    "document_organizer": {
      "matcher": "Write",
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/web-dev-hooks/document-organizer.sh"
      }],
      "timeout": 3
    }
  }
}
```

### 3. 测试Hook

```bash
# 测试文件编辑追踪
echo '{"tool_name":"Write","tool_input":{"file_path":"docs/api/test.md","content":"# Test"},"session_id":"test-123","cwd":"/opt/claude/mystocks_spec"}' \
  | .claude/web-dev-hooks/file-tracker.sh

# 预期结果：
{
  "timestamp": "2025-12-30T06:30:00Z",
  "file_path": "docs/api/test.md",
  "file_path": "/opt/claude/mystocks_spec/docs/api/test.md",
  "tool": "Write",
  "session_id": "test-123",
  "cwd": "/opt/claude/mystocks_spec",
  "type": "Markdown文档",
  "language": "Markdown",
  "priority": "high",
  "size": "30B"
}
```

---

## 📝 快速参考卡片

| 功能 | Hook | 触发时机 | Timeout | 阻塞 |
|------|------|---------|---------|
| Web文件编辑追踪 | Web Tracker | PostToolUse | 3s | ❌ |
| Web文档组织器 | Organizer | PostToolUse | 3s | ❌ |
| Web代码质量检查 | Code Quality | PostToolUse | 5s | ❌ |
| Web前端质量门禁 | Quality Gate | Stop | 120s | ✅ |
| Web上下文注入 | Context | SessionStart | 5s | ❌ |
| Web会话清理 | Cleanup | SessionEnd | 5s | ❌ |
| Skill激活 | UserPromptSubmit | 5s | ❌ |

---

## 🔧 自动化Hook脚本

### post-tool-use-web-file-tracker.sh

```bash
#!/usr/bin/env bash
set -euo pipefail

# Web开发文件追踪Hook
# 自动追踪Web开发文件的编辑操作

# 配置
CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
WEB_DEV_LOG="docs/web-dev/tracing/web-edit-tracker.jsonl"

# Web文档分类
CATEGORIES=(
    "src/frontend/src/components|React组件|high"
    "src/backend/app|FastAPI应用|high"
    "config/|配置文件|medium"
    "docs/api/|API文档|high"
    "docs/(guide|教程)/|开发指南|high"
    "docs/architecture/|架构文档|high"
    "docs/deployment/|部署文档|high"
)

# 检查并记录文件操作
FILE_PATH=$(echo "$INPUT_JSON" | jq -r '.tool_input.file_path // empty')
FILE_EXT="${FILE_PATH##*.}"

if [ -f "$FILE_PATH" ]; then
    ABSOLUTE_PATH=$(cd "$(dirname "$FILE_PATH")" && pwd)/$(basename "$FILE_PATH")
    FILE_SIZE=$(stat -f "$FILE_PATH" | awk '{print $5}')
    TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ')

    # Web开发文件类型识别
    case "$FILE_EXT" in
        .ts|.tsx|.vue)
            FILE_TYPE="Web源码"
            CATEGORY="high"
            ;;
        .css|.scss)
            FILE_TYPE="样式表"
            CATEGORY="medium"
            ;;
        .html)
            FILE_TYPE="HTML页面"
            CATEGORY="high"
            ;;
        .json)
            FILE_TYPE="配置文件"
            CATEGORY="medium"
            ;;
        .yaml|yml)
            FILE_TYPE="配置文件"
            CATEGORY="medium"
            ;;
        .md|rst|txt)
            FILE_TYPE="文档"
            CATEGORY="medium"
            ;;
        *)
            FILE_TYPE="未知"
            CATEGORY="low"
            ;;
    esac

    # 记录到Web开发日志
    mkdir -p "$(dirname "$WEB_DEV_LOG/tracing")"
    cat >> "$WEB_DEV_LOG/tracing/web-edit-tracker.jsonl" << EOF
{
  "timestamp": "$TIMESTAMP",
  "file_path": "$FILE_PATH",
  "absolute_path": "$ABSOLUTE_PATH",
  "tool": "$(echo "$INPUT_JSON" | jq -r '.tool_name // "Unknown"')",
  "session_id": "$(echo "$INPUT_JSON" | jq -r '.session_id // "unknown"')",
  "cwd": "$(echo "$INPUT_JSON" | jq -r '.cwd // "unknown"')",
  "type": "$FILE_TYPE",
  "category": "$CATEGORY",
  "size": "$FILE_SIZE"
}
EOF

    # 同步到全局日志（如果需要）
    mkdir -p "$(dirname ".claude/edit_log.jsonl")"
    if [ -f ".claude/edit_log.jsonl" ]; then
        cat >> ".claude/edit_log.jsonl" << EOF
{
  "timestamp": "$TIMESTAMP",
  "file_path": "$FILE_PATH",
  "absolute_path": "$ABSOLUTE_PATH",
  "tool": "$(echo "$INPUT_JSON" | jq -r '.tool_name // "Unknown"')",
  "session_id": "$(echo "$INPUT_JSON" | jq -r '.session_id // "unknown"')",
  "cwd": "$(echo "$INPUT_JSON" | jq -r '.cwd // "unknown"')",
  "type": "$FILE_TYPE",
  "category": "$CATEGORY",
  "size": "$FILE_SIZE"
}
EOF
        echo "Web tracking sync successful"
    else
        echo "Global edit log not found, skipping sync"
    fi
else
    echo "Empty file_path, skipping"
fi

exit 0
EOF
