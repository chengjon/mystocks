#!/usr/bin/env bash
#
# ============================================================================
# Claude Code Hook: File Location Validator (文件位置验证器)
# ============================================================================
#
# Event: PostToolUse
# Matcher: Write
# Purpose: 验证新文件位置是否符合项目目录结构规范，并提供建议
#
# 基于 reorganize-project-directory-structure 任务的整理经验创建
# 参考: docs/standards/FILE_ORGANIZATION_RULES.md v1.4
#
# 目录结构规范 (v1.4 - 2026-02):
#   src/          - 核心业务代码 (adapters/, core/, data_access/, db_manager/, interfaces/, monitoring/, storage/, utils/)
#   tests/        - 测试文件 (unit/, integration/, e2e/) [独立顶层目录]
#   scripts/      - 脚本工具 (dev/, runtime/, database/)
#   docs/         - 文档 (guides/, legacy/, api/, standards/, reports/)
#   architecture/ - 架构设计文档 [独立顶层目录]
#   config/       - 所有配置文件 (*.yaml, *.yml, *.ini, *.toml)
#   reports/      - 生成的分析报告
#   archived/     - 归档文件 [独立顶层目录]
#   data/         - 数据文件 [独立顶层目录]
#   .multi-cli-tasks/ - 多 CLI 协作工作目录 [dot-prefix]
#   web/          - Web 前后端 (frontend/, backend/, api/)
#   services/     - 微服务
#   openspec/     - OpenSpec 变更管理
#
# 根目录白名单 (v1.4):
#   - 项目入口/说明: README.md, AGENTS.md, CLAUDE.md, IFLOW.md, LICENSE
#   - Python 工具链: pyproject.toml, requirements*.txt, pytest.ini, mypy.ini, conftest.py, __init__.py
#   - Node/E2E 工具链: package.json, tsconfig*.json, vitest.config.*, playwright.config.*
#   - 兼容入口点: unified_manager.py
#   - Docker/部署: docker-compose*.yml, monitoring-stack.yml
#
# 工作原理:
#   1. 从 stdin 读取 tool_input.file_path
#   2. 根据文件类型和名称判断应该放在哪里
#   3. 如果位置不当，通过 hookSpecificOutput.additionalContext 提供建议
#   4. 非阻塞 (exit 0)，仅建议，不强制移动
#
# 退出码 (符合 Claude 官方规范):
#   0: 成功 (非阻塞)
#   1: 警告
#   2: 不使用
#
# ============================================================================

set -uo pipefail

# ===== 配置 =====
DEBUG_MODE="${FILE_LOCATION_VALIDATOR_DEBUG:-false}"
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"

# ===== 调试日志函数 =====
debug_log() {
    if [ "$DEBUG_MODE" = "true" ]; then
        echo "[DEBUG] $*" >&2
    fi
}

# ===== 根目录白名单 =====
ALLOWED_ROOT_FILES=(
    # 项目入口/说明
    "README.md" "AGENTS.md" "CLAUDE.md" "GEMINI.md" "IFLOW.md" "LICENSE"
    # Python 工具链
    "pyproject.toml" "requirements.txt" "requirements-dev.txt" "requirements-test.txt"
    "pytest.ini" "mypy.ini" "conftest.py" "setup.py" "setup.cfg" "__init__.py"
    # Node/E2E 工具链
    "package.json" "package-lock.json"
    "tsconfig.json" "tsconfig.node.json" "tsconfig.app.json"
    "vitest.config.ts" "vitest.config.js" "playwright.config.ts"
    # 兼容入口点 (src/ 重导出)
    "unified_manager.py"
    # Docker/部署
    "docker-compose.yml" "docker-compose.test.yml" "docker-compose.prod.yml"
    "monitoring-stack.yml"
    # 其他工具
    ".mcp.json" "opencode.json"
)

# ===== 允许的顶层目录 (v1.4: 9个核心目录) =====
ALLOWED_TOP_DIRS=(
    # 核心目录
    "src"           # 核心业务代码
    "tests"         # 测试文件 [独立顶层]
    "scripts"       # 脚本工具
    "docs"          # 文档
    "architecture"  # 架构设计文档 [独立顶层]
    "config"        # 配置文件
    "reports"       # 生成的报告
    "archived"      # 归档文件 [独立顶层]
    "data"          # 数据文件 [独立顶层]
    # 工具链/服务目录
    "web"           # Web 前后端
    "services"      # 微服务
    "openspec"      # OpenSpec 变更管理
    "gpu_api_system"  # GPU API 系统
    ".multi-cli-tasks"  # 多 CLI 协作工作目录
    "monitoring-stack"  # 监控栈
)

# ===== 子模块/前端排除规则 =====
EXCLUDED_DIR_KEYWORDS=("web" "css" "js" "frontend" "backend" "api" "services" "temp" "build" "dist" "node_modules" "gpu_api_system")

# ===== 读取 stdin JSON =====
INPUT_JSON=$(cat 2>/dev/null || true)
debug_log "File location validator started"

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

# ===== 提取必要字段 =====
TOOL_NAME=$(echo "$INPUT_JSON" | jq -r '.tool_name // "Unknown"' 2>/dev/null || echo "Unknown")
FILE_PATH=$(echo "$INPUT_JSON" | jq -r '.tool_input.file_path // empty' 2>/dev/null || echo "")

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

# ===== 转换为相对路径 =====
if [[ "$FILE_PATH" == "$PROJECT_ROOT"* ]]; then
    RELATIVE_PATH="${FILE_PATH#$PROJECT_ROOT/}"
else
    RELATIVE_PATH="$FILE_PATH"
fi

debug_log "Checking file: $RELATIVE_PATH"

# ===== 提取文件信息 =====
FILE_EXTENSION="${RELATIVE_PATH##*.}"
FILE_BASENAME=$(basename "$RELATIVE_PATH")
FILE_DIRNAME=$(dirname "$RELATIVE_PATH")
FILE_NAME_NO_EXT="${FILE_BASENAME%.*}"

# ===== 检查是否在排除目录 =====
RELATIVE_PATH_LOWER=$(echo "$RELATIVE_PATH" | tr '[:upper:]' '[:lower:]')
for keyword in "${EXCLUDED_DIR_KEYWORDS[@]}"; do
    keyword_lower=$(echo "$keyword" | tr '[:upper:]' '[:lower:]')
    if [[ "$RELATIVE_PATH_LOWER" == *"/$keyword_lower/"* ]] || [[ "$RELATIVE_PATH_LOWER" == "$keyword_lower/"* ]]; then
        debug_log "File in excluded directory: $keyword"
        # 子模块自治，不提供建议
        exit 0
    fi
done

# ===== 检查是否是隐藏文件/目录 =====
if [[ "$FILE_BASENAME" == .* ]]; then
    debug_log "Hidden file, skipping"
    exit 0
fi

# ===== 特殊文件名排除 (README 等永不移动) =====
README_VARIANTS=("README.md" "README" "readme.md" "readme" "Readme.md" "Readme")
for variant in "${README_VARIANTS[@]}"; do
    if [ "$FILE_BASENAME" = "$variant" ]; then
        debug_log "README file, never suggest moving"
        exit 0
    fi
done

# ===== 检查是否在根目录 =====
IS_IN_ROOT=false
if [ "$FILE_DIRNAME" = "." ] || [ "$FILE_DIRNAME" = "/" ] || [[ ! "$RELATIVE_PATH" =~ / ]]; then
    IS_IN_ROOT=true
fi

# ===== 分析文件类型并确定建议位置 =====
VIOLATION=""
SUGGESTION=""
FILE_CATEGORY=""

# 函数：根据文件类型获取建议位置 (v1.4 规范)
get_suggested_location() {
    local filename="$1"
    local ext="$2"
    local name_no_ext="$3"

    # ===== 脚本文件 (.py) =====
    if [ "$ext" = "py" ]; then
        # 测试文件 → tests/ (v1.4: 独立顶层目录)
        if [[ "$filename" =~ ^test_ ]] || [[ "$filename" =~ _test\.py$ ]]; then
            FILE_CATEGORY="测试文件"
            echo "tests/unit/ 或 tests/integration/"
            return
        fi
        # 运行时脚本
        if [[ "$filename" =~ ^(run_|save_|monitor_|start_) ]]; then
            FILE_CATEGORY="运行时脚本"
            echo "scripts/runtime/"
            return
        fi
        # 数据库脚本
        if [[ "$filename" =~ ^(check_|verify_|create_|init_|migrate_) ]]; then
            FILE_CATEGORY="数据库脚本"
            echo "scripts/database/"
            return
        fi
        # 部署脚本
        if [[ "$filename" =~ ^(deploy_|build_|setup_) ]]; then
            FILE_CATEGORY="部署脚本"
            echo "scripts/dev/ (或 config/docker/ 如果是 Docker 相关)"
            return
        fi
        # 开发工具
        if [[ "$filename" =~ ^(validate_|analyze_|generate_|convert_|fix_) ]]; then
            FILE_CATEGORY="开发工具脚本"
            echo "scripts/dev/"
            return
        fi
        # 演示脚本
        if [[ "$filename" =~ _demo\.py$ ]] || [[ "$filename" =~ Demo\.py$ ]]; then
            FILE_CATEGORY="演示脚本"
            echo "scripts/runtime/ 或 scripts/dev/"
            return
        fi
        # 默认 Python 脚本
        FILE_CATEGORY="Python 脚本"
        echo "scripts/dev/ (或根据功能选择 scripts/runtime/, scripts/database/)"
        return
    fi

    # ===== 配置文件 =====
    if [[ "$ext" =~ ^(yaml|yml|ini|toml|conf|cfg)$ ]]; then
        FILE_CATEGORY="配置文件"
        echo "config/"
        return
    fi
    if [[ "$filename" =~ docker-compose ]]; then
        FILE_CATEGORY="Docker 配置"
        echo "config/ (或根目录如果常用)"
        return
    fi
    if [[ "$filename" =~ ^(pytest|mypy|ruff|black|isort)\. ]]; then
        FILE_CATEGORY="Python 工具配置"
        echo "config/ 或根目录 (允许)"
        return
    fi

    # ===== 文档文件 =====
    if [[ "$ext" =~ ^(md|rst|txt|adoc|org)$ ]]; then
        # 根据内容/名称判断
        if [[ "$filename" =~ ^(QUICKSTART|quickstart|tutorial|guide|getting.?started|how.?to|IFLOW) ]]; then
            FILE_CATEGORY="指南文档"
            echo "docs/guides/"
            return
        fi
        if [[ "$filename" =~ ^(API|api|endpoint|swagger|openapi) ]]; then
            FILE_CATEGORY="API 文档"
            echo "docs/api/"
            return
        fi
        # v1.4: 架构文档在独立顶层目录 architecture/
        if [[ "$filename" =~ (architecture|design|system|database|schema|ADR) ]]; then
            FILE_CATEGORY="架构文档"
            echo "architecture/"
            return
        fi
        if [[ "$filename" =~ (standard|规范|convention|guideline|best.?practice|RULES) ]]; then
            FILE_CATEGORY="标准规范"
            echo "docs/standards/"
            return
        fi
        if [[ "$filename" =~ (report|REPORT|summary|SUMMARY|assessment|ASSESSMENT) ]]; then
            FILE_CATEGORY="报告文档"
            echo "docs/reports/ 或 reports/"
            return
        fi
        # v1.4: 归档文件在独立顶层目录 archived/
        if [[ "$filename" =~ (deprecated|archived|old|legacy|废弃|旧版) ]]; then
            FILE_CATEGORY="归档文档"
            echo "archived/ 或 docs/legacy/"
            return
        fi
        if [[ "$filename" =~ ^(TASK|PLAN|TODO) ]]; then
            FILE_CATEGORY="计划文档"
            echo "docs/plans/ 或 openspec/"
            return
        fi
        if [[ "$filename" =~ ^(REVIEW|review|审查) ]]; then
            FILE_CATEGORY="审查文档"
            echo "docs/reviews/"
            return
        fi
        # 默认文档
        FILE_CATEGORY="文档"
        echo "docs/guides/ (根据内容选择正确的 docs/ 子目录)"
        return
    fi

    # ===== 报告/数据文件 =====
    if [[ "$ext" =~ ^(json|csv|xml)$ ]]; then
        if [[ "$filename" =~ [0-9]{8}_[0-9]{6} ]] || [[ "$filename" =~ (report|analysis|result|assessment) ]]; then
            FILE_CATEGORY="报告/数据文件"
            echo "reports/"
            return
        fi
        # v1.4: 数据文件在独立顶层目录 data/
        if [[ "$filename" =~ (data|dataset|seed) ]]; then
            FILE_CATEGORY="数据文件"
            echo "data/"
            return
        fi
    fi

    # ===== TypeScript/JavaScript =====
    if [[ "$ext" =~ ^(ts|tsx|js|jsx|mjs|cjs)$ ]]; then
        if [[ "$filename" =~ ^test_ ]] || [[ "$filename" =~ \.test\. ]] || [[ "$filename" =~ \.spec\. ]]; then
            FILE_CATEGORY="测试文件"
            echo "tests/e2e/ 或 web/frontend/tests/"
            return
        fi
        if [[ "$filename" =~ \.config\. ]]; then
            FILE_CATEGORY="配置文件"
            echo "config/ 或根目录 (工具配置)"
            return
        fi
        # 其他 TS/JS 文件通常在 web/ 内
        FILE_CATEGORY="前端源码"
        echo "web/frontend/src/ (前端模块自治)"
        return
    fi

    # ===== Vue 组件 =====
    if [ "$ext" = "vue" ]; then
        FILE_CATEGORY="Vue 组件"
        echo "web/frontend/src/ (前端模块自治)"
        return
    fi

    # ===== SQL 文件 =====
    if [ "$ext" = "sql" ]; then
        FILE_CATEGORY="SQL 脚本"
        echo "scripts/database/"
        return
    fi

    # ===== Shell 脚本 =====
    if [ "$ext" = "sh" ]; then
        FILE_CATEGORY="Shell 脚本"
        echo "scripts/dev/ 或 scripts/runtime/"
        return
    fi

    # ===== 默认 =====
    FILE_CATEGORY="未知类型"
    echo "根据文件用途选择合适的目录 (参考 docs/standards/FILE_ORGANIZATION_RULES.md)"
}

# ===== 检查根目录违规 =====
if [ "$IS_IN_ROOT" = "true" ]; then
    # 检查是否在白名单中
    IS_ALLOWED=false
    for allowed in "${ALLOWED_ROOT_FILES[@]}"; do
        if [ "$FILE_BASENAME" = "$allowed" ]; then
            IS_ALLOWED=true
            break
        fi
    done

    if [ "$IS_ALLOWED" = "false" ]; then
        VIOLATION="文件不应放在根目录"
        SUGGESTION=$(get_suggested_location "$FILE_BASENAME" "$FILE_EXTENSION" "$FILE_NAME_NO_EXT")
    fi
fi

# ===== 检查顶层目录违规 =====
if [ "$IS_IN_ROOT" = "false" ]; then
    TOP_DIR=$(echo "$RELATIVE_PATH" | cut -d'/' -f1)

    IS_VALID_DIR=false
    # 检查是否在允许的目录列表中
    for allowed in "${ALLOWED_TOP_DIRS[@]}"; do
        if [ "$TOP_DIR" = "$allowed" ]; then
            IS_VALID_DIR=true
            break
        fi
    done

    # 检查是否是隐藏目录
    if [[ "$TOP_DIR" == .* ]]; then
        IS_VALID_DIR=true
    fi

    if [ "$IS_VALID_DIR" = "false" ]; then
        # 不在允许的顶层目录中
        SUGGESTION=$(get_suggested_location "$FILE_BASENAME" "$FILE_EXTENSION" "$FILE_NAME_NO_EXT")
        if [ -z "$VIOLATION" ]; then
            VIOLATION="顶层目录 '$TOP_DIR' 不在标准目录列表中"
        fi
    fi
fi

# ===== 检查特定位置的合理性 =====
# 如果文件已经在某个目录中，检查是否在正确的位置
if [ -z "$VIOLATION" ] && [ "$IS_IN_ROOT" = "false" ]; then
    # 检查配置文件是否在 config/
    if [[ "$FILE_EXTENSION" =~ ^(yaml|yml|ini|toml)$ ]] && [[ ! "$RELATIVE_PATH" =~ ^config/ ]] && [[ ! "$RELATIVE_PATH" =~ ^web/ ]] && [[ ! "$RELATIVE_PATH" =~ ^services/ ]]; then
        VIOLATION="配置文件应该在 config/ 目录"
        SUGGESTION="config/"
        FILE_CATEGORY="配置文件"
    fi

    # v1.4: 检查测试文件是否在 tests/ (独立顶层目录)
    if [[ "$FILE_BASENAME" =~ ^test_ ]] && [ "$FILE_EXTENSION" = "py" ]; then
        if [[ ! "$RELATIVE_PATH" =~ ^tests/ ]]; then
            VIOLATION="测试文件应该在 tests/ 目录 (v1.4 独立顶层目录)"
            SUGGESTION="tests/unit/ 或 tests/integration/"
            FILE_CATEGORY="测试文件"
        fi
    fi

    # 检查文档是否在 docs/ 或 architecture/ (v1.4)
    if [[ "$FILE_EXTENSION" =~ ^(md|rst)$ ]] && [[ ! "$RELATIVE_PATH" =~ ^docs/ ]] && [[ ! "$RELATIVE_PATH" =~ ^architecture/ ]] && [[ ! "$RELATIVE_PATH" =~ ^web/ ]] && [[ ! "$RELATIVE_PATH" =~ ^services/ ]]; then
        if [[ ! "$FILE_BASENAME" =~ ^(README|CHANGELOG) ]]; then
            # v1.4: 架构文档应该在 architecture/
            if [[ "$FILE_BASENAME" =~ (architecture|design|system|database|schema|ADR) ]]; then
                VIOLATION="架构文档应该在 architecture/ 目录 (v1.4 独立顶层目录)"
                SUGGESTION="architecture/"
                FILE_CATEGORY="架构文档"
            else
                VIOLATION="文档文件应该在 docs/ 目录"
                SUGGESTION=$(get_suggested_location "$FILE_BASENAME" "$FILE_EXTENSION" "$FILE_NAME_NO_EXT")
                FILE_CATEGORY="文档"
            fi
        fi
    fi
fi

# ===== 如果没有违规,正常退出 =====
if [ -z "$VIOLATION" ]; then
    debug_log "File location is correct"
    exit 0
fi

# ===== 构建建议消息 (v1.4 规范) =====
CONTEXT_MESSAGE="📁 FILE LOCATION VALIDATION (v1.4)

⚠️ $VIOLATION

当前位置: $RELATIVE_PATH
文件类型: ${FILE_CATEGORY:-未知}
建议位置: $SUGGESTION

📖 MyStocks 目录结构规范 (v1.4):

9 个核心顶层目录:
  src/          - 核心业务代码 (adapters/, core/, data_access/, interfaces/, monitoring/, storage/, utils/)
  tests/        - 测试文件 [独立顶层] (unit/, integration/, e2e/)
  scripts/      - 脚本工具
    ├── runtime/    - 运行时脚本 (run_*, save_*, monitor_*, *_demo.py)
    ├── database/   - 数据库脚本 (check_*, verify_*, create_*, init_*, migrate_*)
    └── dev/        - 开发工具 (validate_*, analyze_*, generate_*)
  docs/         - 文档
    ├── guides/     - 用户指南 (QUICKSTART, tutorial, how-to)
    ├── api/        - API 文档 (endpoint, swagger, openapi)
    ├── standards/  - 标准规范 (RULES, conventions)
    ├── reports/    - 报告文档 (assessment, summary)
    └── legacy/     - 历史文档 (archived, deprecated)
  architecture/ - 架构设计文档 [独立顶层] (design, system, ADR, DATABASE_*)
  config/       - 所有配置文件 (*.yaml, *.yml, *.ini, *.toml)
  reports/      - 生成的分析报告 (带时间戳的 json/txt)
  archived/     - 归档文件 [独立顶层]
  data/         - 数据文件 [独立顶层]

工具链/服务目录:
  web/          - Web 前后端 [子模块自治]
  services/     - 微服务 [子模块自治]
  openspec/     - OpenSpec 变更管理
  .multi-cli-tasks/ - 多 CLI 协作工作目录 [dot-prefix]

根目录 allowlist (允许的文件):
  项目入口: README.md, AGENTS.md, CLAUDE.md, GEMINI.md, IFLOW.md, LICENSE
  Python: pyproject.toml, requirements*.txt, pytest.ini, mypy.ini, conftest.py, __init__.py
  Node: package.json, tsconfig*.json, vitest.config.*, playwright.config.*
  兼容入口: unified_manager.py

💡 推荐操作:
  1. 使用 'git mv' 移动文件到建议位置 (保留历史)
     git mv $RELATIVE_PATH $SUGGESTION$FILE_BASENAME

  2. 更新所有引用此文件的链接

参考: docs/standards/FILE_ORGANIZATION_RULES.md (v1.4)
      .claude/hooks/FILE_ORGANIZATION_GUIDE.md
"

# ===== 输出 JSON =====
ESCAPED_CONTEXT=$(echo "$CONTEXT_MESSAGE" | jq -Rs .)

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": $ESCAPED_CONTEXT
  }
}
EOF

debug_log "File location suggestion sent to Claude"

# 非阻塞成功退出
exit 0
