# Web Development Hooks Guide

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


**Version**: 1.0
**Date**: 2025-12-30
**Purpose**: Configure hooks for Web development to prevent file displacement and enforce organization rules

---

## Overview

The Web Development Hooks system provides specialized file tracking, validation, and quality assurance for web development files (TypeScript, Vue, React, CSS, HTML, JavaScript) in the MyStocks project. This prevents web-specific files from being incorrectly moved or deleted by general-purpose hooks.

---

## Hook Scripts

### Stop Closeout Reporting

仓库当前额外启用了一个通用 Stop closeout reporter：`.claude/hooks/stop-graphiti-task-closeout.sh`。

用途：
- 监听 assistant 最终收尾语句中的完成态表达；
- 在明确完成时，把标准化任务总结写入 Graphiti；
- 为后续审计保留 `episode_uuid`、`group_id`、去重键和失败记录。

行为约束：
- 只在命中完成短语且未命中否定短语时触发；
- 写入走共享 CLI 合同 `scripts/runtime/coordctl.py graphiti remember`；
- 失败不阻塞 Stop，审计信息落在 `.claude/graphiti-closeout-state.json`。

配置入口：
- 默认读取 `config/hooks/graphiti-closeout.json`；
- 可配置 `actor_cli`、`group_id_template`、完成短语、否定短语、验证关键字；
- 环境变量 `GRAPHITI_CLOSEOUT_ACTOR_CLI`、`GRAPHITI_CLOSEOUT_GROUP_ID`、`GRAPHITI_CLOSEOUT_CONFIG` 可覆盖默认配置。

版本控制口径：
- 关键 closeout hook 资产应纳入 Git 管理，包括：
  - `.claude/settings.json`
  - `.claude/hooks/stop-graphiti-task-closeout.sh`
  - `.claude/hooks/record_graphiti_closeout.py`
  - `.claude/hooks/README.md`
  - `config/hooks/graphiti-closeout.json`
- 本地运行态文件继续保持不入库，例如：
  - `.claude/graphiti-closeout-state.json`
  - `.claude/edit_log.jsonl`

巡检命令：
- `python scripts/runtime/inspect_graphiti_closeout_state.py`
- `python scripts/runtime/inspect_graphiti_closeout_state.py --output json`
- `python scripts/runtime/inspect_graphiti_closeout_state.py --limit 10`

巡检输出会汇总：
- 已处理去重键数量；
- closeout 成功/失败数量；
- 最近失败项的 session、完成短语、错误原因；
- 最近成功项的 session、`episode_uuid`、`group_id`。

端到端演练：
- `python scripts/runtime/smoke_graphiti_closeout_hook.py`
- 该脚本会构造临时 transcript、临时配置和 fake Graphiti CLI，调用真实 `stop-graphiti-task-closeout.sh`，再读取本地 state 做汇总。
- hook wrapper 默认仍是异步；仅在测试或演练时通过 `GRAPHITI_CLOSEOUT_SYNC=1` 切到同步执行。

真实 Graphiti 联调：
- 可直接复用仓库现有 CLI：
  `python scripts/runtime/smoke_graphiti_cli.py --actor-cli <actor> --group-id <group_id> --name "<name>" --body "<body>" --query "<query>"`
- 建议为每次联调使用唯一 `group_id`，例如 `mystocks_spec_closeout_live_<timestamp>`。
- 成功口径：
  - `remember_server_status=ok`
  - `remember_ingest_status=completed`
  - `search_server_status=ok`
  - `search_outcome=hit`
- 2026-04-22 的一次实测样例已验证通过，返回：
  - `episode_uuid=1d4ff976-6b2e-4067-aa5b-21eac1c1e4b6`
  - `group_id=mystocks_spec_closeout_live_20260422142710`
  - `search_summary=nodes hit=3, facts hit=2`

正式 live 验收：
- `python scripts/runtime/run_graphiti_closeout_live_validation.py --output json`
- 可追加 `--report-file docs/reports/hooks/<your-report>.md` 自动落盘验收报告。
- 该脚本会：
  - 构造真实 Stop 事件输入；
  - 调用真实 `stop-graphiti-task-closeout.sh`；
  - 走真实 `coordctl.py graphiti remember`；
  - 再走真实 `coordctl.py graphiti search` 回查；
  - 输出本地 state 与 Graphiti search 的双向验证结果。

推荐接入时机：
- 新增或修改 closeout hook 行为后，合并前至少运行一次正式 live 验收；
- 调整 `group_id_template`、完成短语或 Graphiti CLI 合同时，必须重跑正式 live 验收；
- 重要发布前，如本次迭代涉及 hooks / memory / automation 治理，建议再次执行。

`group_id` 命名规范：
- fake smoke：`smoke_{project_name}_closeouts`
- 临时真实联调：`mystocks_spec_closeout_live_<timestamp>`
- 正式 Stop-hook 真实验收：`mystocks_spec_closeout_hook_live_<timestamp>`
- 验收记录归档：`mystocks_spec_closeout_validation`

命名原则：
- 前缀固定表达用途，不混用；
- `<timestamp>` 使用 `YYYYMMDDHHMMSS`；
- 验收归档组应稳定，便于后续集中检索；
- 单次临时联调组应唯一，避免搜索结果互相污染。

### 1. Web-Dev File Tracker Hook

**File**: `.claude/hooks/post-tool-use-web-dev-file-tracker.sh`

**Purpose**: Track all web development file edits and write runtime logs to `var/log/web-dev/tracing/`

**Trigger**: PostToolUse (Edit|Write)

**Features**:
- Logs all web file edits with timestamps
- Classifies files by type (TypeScript, Vue, React, CSS, HTML)
- Tracks session metadata (tool, timestamp, changes)
- Separates web dev logs from Python backend logs

**Log Location**: `var/log/web-dev/tracing/web-edit-tracker.jsonl`

**Example Log Entry**:
```json
{
  "timestamp": "2025-12-30T15:30:45Z",
  "file_path": "web/frontend/src/components/StockChart.vue",
  "relative_path": "web/frontend/src/components/StockChart.vue",
  "file_type": "Vue Component",
  "web_subdir": "components/",
  "tool_name": "Edit",
  "session_id": "session-123",
  "cwd": "/opt/claude/mystocks_spec"
}
```

---

### 2. Web-Dev Document Organizer Hook

**File**: `.claude/hooks/post-tool-use-web-dev-document-organizer.sh`

**Purpose**: Validate web documentation location and prevent organization violations

**Trigger**: PostToolUse (Write)

**Features**:
- Validates `.md` files are in correct locations
- Prevents moving web development docs to archive
- Checks whitelist before organizing files
- Enforces web-specific file classification rules

**Whitelist**: `.claude/web-dev-whitelist.json`

**Protected Files**:
- All files in `docs/guides/hooks/`
- All files in `web/` directory
- Root configuration files (package.json, tsconfig.json, etc.)

---

### 3. Web-Dev Quality Gate Hook

**File**: `.claude/hooks/stop-web-dev-quality-gate.sh`

**Purpose**: Enforce web development quality standards before session end

**Trigger**: Stop

**Timeout**: 60 seconds

**Quality Checks**:
1. **TypeScript Compilation** - `tsc --noEmit`
2. **ESLint** - JavaScript/TypeScript linting
3. **React Prop Types** - Type checking
4. **Vue Template Validation** - Template linting
5. **CSS/SCSS Linting** - Style validation
6. **Build Verification** - `npm run build` (optional)

**Exit Codes**:
- `0` - Pass (all quality checks passed)
- `1` - Error (non-critical failures)
- `2` - Block (stop session)

**Error Threshold**: 10 errors before blocking

---

## Configuration Files

### Web Dev Whitelist

**File**: `.claude/web-dev-whitelist.json`

**Purpose**: Exclude web-specific files and directories from general hooks

**Allowed Root Files**:
- `package.json`
- `tsconfig.json`
- `playwright.*.ts`
- `ecosystem.config.js`
- `pm2.config.js`
- `.env`
- `.env.production`
- `.env.example`

**Allowed Directories**:
- `web/`
- `web/backend/`
- `web/frontend/`
- `config/`
- `docs/guides/hooks/`

---

### Web Dev File Categories

**File**: `.claude/web-dev-file-categories.json`

**Purpose**: Define web file classification and target directories

**Categories**:
```json
{
  "typescript": {
    "category": "TypeScript Source",
    "directory": "web/",
    "priority": "high",
    "extensions": [".ts", ".tsx"]
  },
  "vue": {
    "category": "Vue Component",
    "directory": "web/frontend/src/components/",
    "priority": "high",
    "extensions": [".vue"]
  },
  "react": {
    "category": "React Component",
    "directory": "web/frontend/src/components/",
    "priority": "high",
    "extensions": [".tsx", ".jsx"]
  },
  "css": {
    "category": "Stylesheet",
    "directory": "web/frontend/src/styles/",
    "priority": "low",
    "extensions": [".css", ".scss", ".sass", ".less"]
  },
  "html": {
    "category": "HTML Page",
    "directory": "web/src/pages/",
    "priority": "medium",
    "extensions": [".html", ".htm"]
  },
  "config": {
    "category": "Configuration",
    "directory": "config/",
    "priority": "low",
    "extensions": [".json", ".yml", ".yaml", ".toml"]
  },
  "documentation": {
    "category": "Documentation",
    "directory": "docs/guides/hooks/",
    "priority": "high",
    "extensions": [".md"]
  }
}
```

---

## File Organization Rules

### Root Directory (Protected)
These files should remain in root directory:
```yaml
root_protected:
  - package.json
  - tsconfig.json
  - playwright.config.ts
  - playwright.config.simple.ts
  - playwright.grafana.config.ts
  - ecosystem.config.js
  - pm2.config.js
  - ecosystem.production.config.js
  - ecosystem.grpc.config.js
  - ecosystem.production.grpc.json
  - .env
  - .env.production
  - .env.example
  - docker-compose.test.yml
  - pyproject.toml
```

### Web Directory Structure
```yaml
web_frontend:
  root: "web/frontend/src/"
  components: "web/frontend/src/components/"
  pages: "web/frontend/src/pages/"
  styles: "web/frontend/src/styles/"
  assets: "web/frontend/src/assets/"
  utils: "web/frontend/src/utils/"
  api: "web/frontend/src/api/"

web_backend:
  root: "web/backend/src/"
  api: "web/backend/api/"
  routes: "web/backend/src/routes/"
  services: "web/backend/src/services/"
  middleware: "web/backend/src/middleware/"
```

### Documentation Structure
```yaml
web_dev_docs:
  root: "docs/guides/hooks/"
  guides: "docs/guides/hooks/"
  api: "docs/api/"
  tutorials: "docs/guides/hooks/"
  deployment: "docs/operations/"
  tracing: "var/log/web-dev/tracing/"
  archived: "archive/docs/"
```

---

## Installation

### 1. Create Directory Structure
```bash
mkdir -p docs/guides/hooks
mkdir -p var/log/web-dev/tracing
mkdir -p .claude/hooks
```

### 2. Create Hook Scripts
Copy the hook scripts to `.claude/hooks/`:
- `post-tool-use-web-dev-file-tracker.sh`
- `post-tool-use-web-dev-document-organizer.sh`
- `stop-web-dev-quality-gate.sh`

### 3. Create Configuration Files
Copy configuration files to `.claude/`:
- `web-dev-whitelist.json`
- `web-dev-file-categories.json`

### 4. Update Settings
Add web-dev hooks to `.claude/settings.json`:
```json
{
  "hooks": {
    "PostToolUse": {
      "web_dev": [
        {
          "matcher": "Edit|Write",
          "hooks": [
            {
              "type": "command",
              "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-web-dev-file-tracker.sh",
              "timeout": 3
            }
          ]
        },
        {
          "matcher": "Write",
          "hooks": [
            {
              "type": "command",
              "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-web-dev-document-organizer.sh",
              "timeout": 5
            }
          ]
        }
      ]
    },
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/stop-web-dev-quality-gate.sh",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

### 5. Set Permissions
```bash
chmod +x .claude/hooks/*.sh
```

---

## Usage

### Automatic Hook Execution

Hooks execute automatically during file operations:

1. **Edit/Write File** → File Tracker runs
2. **Write File** → Document Organizer runs
3. **Session End** → Quality Gate runs

### Manual Execution

```bash
# Run file tracker manually
.claude/hooks/post-tool-use-web-dev-file-tracker.sh

# Run quality gate manually
.claude/hooks/stop-web-dev-quality-gate.sh
```

---

## Troubleshooting

### Hook Not Executing

1. Check hook permissions: `ls -la .claude/hooks/`
2. Verify settings.json syntax: `jq . .claude/settings.json`
3. Check hook logs: `cat var/log/web-dev/tracing/web-edit-tracker.jsonl`

### Quality Gate Blocking Session

1. Review error messages
2. Fix critical errors (TypeScript compilation, ESLint)
3. Temporarily disable: Remove hook from settings.json
4. Override with exit code 0 in hook script

### Files Being Incorrectly Moved

1. Verify whitelist includes file: `cat .claude/web-dev-whitelist.json`
2. Check file category classification
3. Review organization log: `cat var/log/web-dev/tracing/web-edit-tracker.jsonl`

---

## Maintenance

### Update Whitelist

Edit `.claude/web-dev-whitelist.json` to add new protected files.

### Update File Categories

Edit `.claude/web-dev-file-categories.json` to add new file types.

### Review Logs

Periodically review logs:
```bash
# Recent web edits
tail -20 var/log/web-dev/tracing/web-edit-tracker.jsonl

# Count edits by file type
jq -r '.file_type' var/log/web-dev/tracing/web-edit-tracker.jsonl | sort | uniq -c
```

---

## Integration with Existing Hooks

### Separation of Concerns

| Hook | Purpose | Files Managed |
|------|---------|---------------|
| `post-tool-use-file-edit-tracker.sh` | Python backend tracking | `src/`, `tests/` Python files |
| `post-tool-use-web-dev-file-tracker.sh` | Web frontend tracking | `web/`, TypeScript, Vue, React |
| `post-tool-use-document-organizer.sh` | General doc organization | Root `.md` files |
| `post-tool-use-web-dev-document-organizer.sh` | Web doc validation | `docs/guides/hooks/` |

### Hook Execution Order

1. File Tracker (Python) → `post-tool-use-file-edit-tracker.sh`
2. File Tracker (Web) → `post-tool-use-web-dev-file-tracker.sh`
3. Database Validator → `post-tool-use-database-schema-validator.sh`
4. Mock Data Validator → `post-tool-use-mock-data-validator.sh`
5. Document Organizer (General) → `post-tool-use-document-organizer.sh`
6. Document Organizer (Web) → `post-tool-use-web-dev-document-organizer.sh`
7. Quality Gate (Python) → `stop-python-quality-gate.sh`
8. Quality Gate (Web) → `stop-web-dev-quality-gate.sh`

---

## Examples

### Example 1: Vue Component Edit

**Operation**: Edit `web/frontend/src/components/StockChart.vue`

**Hook Execution**:
1. File Tracker logs edit
2. Classification: Vue Component → components/
3. No organization needed (file in correct location)

**Log Entry**:
```json
{
  "timestamp": "2025-12-30T15:30:45Z",
  "file_path": "/opt/claude/mystocks_spec/web/frontend/src/components/StockChart.vue",
  "relative_path": "web/frontend/src/components/StockChart.vue",
  "file_type": "Vue Component",
  "web_subdir": "components/",
  "tool_name": "Edit",
  "session_id": "session-123",
  "cwd": "/opt/claude/mystocks_spec"
}
```

### Example 2: TypeScript File in Wrong Location

**Operation**: Write `src/types/StockTypes.ts` (should be in web/)

**Hook Execution**:
1. File Tracker logs write
2. Document Organizer validates location
3. Suggests move to `web/frontend/src/types/`

**Suggestion**:
```
⚠️  File Organization Warning
File: src/types/StockTypes.ts
Expected: web/frontend/src/types/StockTypes.ts
Action: Please move file to correct location
```

### Example 3: Quality Gate Failure

**Operation**: Session ends with TypeScript errors

**Hook Execution**:
1. Run `tsc --noEmit`
2. Detect 15 type errors
3. Block session (exceeds threshold of 10)

**Output**:
```
=== Web Development Quality Gate ===

1. TypeScript Compilation Check...
  ❌ TypeScript errors found

Total Errors: 15

❌ Quality check failed: 15 errors found
{
  "decision": "block",
  "reason": "Web development quality gate failed with 15 errors"
}
```

---

## Best Practices

1. **Always run quality gate before committing**
2. **Keep whitelist up to date**
3. **Review logs regularly**
4. **Follow file organization rules**
5. **Use TypeScript strict mode**
6. **Maintain consistent code style**
7. **Test hooks in development environment**
8. **Document hook changes**

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-30 | Initial version |
