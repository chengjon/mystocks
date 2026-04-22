# MyStocks Hooks System

**Version**: 2.0 (Python/FastAPI)
**Last Updated**: 2025-11-11
**Status**: ✅ Production Ready

---

## Overview

This directory contains Claude Code hooks that enforce code quality, architectural standards, and development workflows for the MyStocks project. All hooks are designed following [Claude官方hooks文档规范](https://docs.claude.com/en/docs/claude-code/hooks).

### Architecture Migration

This hooks system was migrated from TypeScript/Node.js to Python/FastAPI architecture in November 2025. See `HOOKS_IMPROVEMENT_COMPLETION_REPORT.md` for full migration details.

---

## Active Hooks (7 hooks across 5 events)

### 1. UserPromptSubmit Hook
**File**: `user-prompt-submit-skill-activation.sh`
**Purpose**: Automatically activates relevant skills based on user prompts
**Timeout**: 5 seconds
**Behavior**: Non-blocking (exit 0)

**Triggers**:
- Matches keywords from `skill-rules.json`
- Supports both English and Chinese keywords
- Activates skills like `backend-dev-guidelines`, `database-architecture-guidelines`, `python-quality-patterns`

**Example**:
- User: "创建一个新的API接口" → Activates `backend-dev-guidelines`
- User: "存储tick数据" → Activates `database-architecture-guidelines` (critical warning)

---

### 2. PostToolUse Hooks (3 hooks)

#### 2.1 File Edit Tracker
**File**: `post-tool-use-file-edit-tracker.sh`
**Purpose**: Logs all file edits to `.claude/edit_log.jsonl` for Stop hook batch checking
**Timeout**: 3 seconds
**Behavior**: Non-blocking (exit 0)

**Features**:
- Project-level logs (`.claude/edit_log.jsonl`, not global)
- JSONL format (one JSON per line)
- Automatic size limiting (max 10,000 lines)
- Session tracking for cleanup

**Reddit Pattern**: Record phase of "Reddit Case Study" pattern (PostToolUse → Stop)

#### 2.2 Database Schema Validator
**File**: `post-tool-use-database-schema-validator.sh`
**Purpose**: Validates dual-database architecture compliance (TDengine vs PostgreSQL)
**Timeout**: 5 seconds
**Behavior**: Non-blocking warning (exit 0)

**MyStocks Dual-Database Rules**:
- ⚠️ **Tick data** → TDengine (not PostgreSQL)
- ⚠️ **Minute data** → TDengine (not PostgreSQL)
- ⚠️ **Daily data** → PostgreSQL (TDengine needs justification)
- 🚨 **DROP STABLE** → Critical warning (data loss!)

**Triggers**: Only scans database-related files:
- `table_config.yaml`
- `*_adapter.py`
- `database_manager.py`
- `data_access/**/*.py`

**Output**: Injects warnings via `hookSpecificOutput.additionalContext` (visible to Claude)

#### 2.3 Document Organizer
**File**: `post-tool-use-document-organizer.sh`
**Purpose**: Validates new document placement according to project file organization rules
**Timeout**: 5 seconds
**Behavior**: Non-blocking suggestion (exit 0)

**MyStocks File Organization Rules**:
- 📁 **Root directory**: Only 5 core files allowed (README, CLAUDE, CHANGELOG, requirements.txt, .mcp.json)
- 📁 **All documents**: Must be in `docs/` subdirectories
- 📁 **Document classification**:
  - `docs/guides/` - User guides, tutorials (QUICKSTART.md, IFLOW.md)
  - `docs/api/` - API documentation (endpoint docs, OpenAPI specs)
  - `docs/architecture/` - Architecture design documents
  - `docs/standards/` - Standards and guidelines
  - `docs/archived/` - Deprecated documentation (with deprecation notice)

**Triggers**: Only on new document files (`.md`, `.txt`, `.rst`, `.adoc`, `.org`)

**Smart Classification**:
- Analyzes filename patterns and content to suggest correct location
- Recommends using `git mv` to preserve file history
- Suggests updating related index files (e.g., `docs/api/README.md`)

**Output**: Provides guidance via `hookSpecificOutput.additionalContext` with:
- Current location vs suggested location
- Full file organization rules reference
- Recommended `git mv` command
- Index file update suggestions

**Reference Guide**: See `FILE_ORGANIZATION_GUIDE.md` for quick decision tree

---

### 3. Stop Hook
**File**: `stop-python-quality-gate.sh`
**Purpose**: Python code quality gate - blocks stopping if errors ≥ threshold
**Timeout**: 120 seconds
**Behavior**: **Blocking** (exit 2 if errors ≥ 10, exit 0 otherwise)

**Quality Checks** (configured in `.claude/build-checker-python.json`):
1. **Critical Imports**: Validates `from src.core import ConfigDrivenTableManager`
2. **Backend Syntax**: `python -m py_compile` on all `web/backend/app/**/*.py`
3. **Future checks**: Can add mypy, pylint, pytest

**Error Threshold**: 10 errors (configurable in `build-checker-python.json`)

**Reddit Pattern**: Batch check phase of "Reddit Case Study" pattern (PostToolUse → Stop)

**Design Philosophy**:
- ✅ Allows temporary breakage during development (threshold > 0)
- ✅ Catches accumulated errors before finishing
- ✅ Non-destructive checks only (no auto-fixes)

---

### 4. SessionStart Hook
**File**: `session-start-task-master-injector.sh`
**Purpose**: Injects Task Master context at session start (combat context loss)
**Timeout**: 5 seconds
**Behavior**: Non-blocking (exit 0), stdout → Claude context

**Features**:
- Reads `.taskmaster/tasks/tasks.json`
- Injects **in-progress** tasks with full details
- Shows top 3 **high-priority pending** tasks
- Limits output to 100 lines (token optimization)
- Graceful handling when Task Master not initialized

**Why This Hook**:
- Claude's auto-compression causes context loss across sessions
- Task Master already tracks project tasks → No need for separate Dev Docs system
- Automatic context restoration prevents "失忆"

**SessionStart Special Behavior**: Stdout is injected to Claude (unique to SessionStart and UserPromptSubmit)

---

### 5. SessionEnd Hook
**File**: `session-end-cleanup.sh`
**Purpose**: Cleans up session logs when session ends
**Timeout**: 5 seconds
**Behavior**: Non-blocking (exit 0)

**Cleanup Actions**:
1. Removes current session entries from `.claude/edit_log.jsonl`
2. Truncates log to last 5,000 lines (if > 5,000)
3. Preserves other sessions' data

**Why This Hook**:
- Prevents edit log from growing indefinitely
- Maintains session isolation
- Complements File Edit Tracker hook

---

## Configuration Files

### `.claude/settings.json`
Main hooks registration file. See current configuration:

```json
{
  "hooks": {
    "UserPromptSubmit": [...],
    "PostToolUse": [
      {"hooks": ["file-edit-tracker.sh"], "timeout": 3},
      {"hooks": ["database-schema-validator.sh"], "timeout": 5}
    ],
    "Stop": [{"hooks": ["python-quality-gate.sh"], "timeout": 120}],
    "SessionStart": [{"hooks": ["task-master-injector.sh"], "timeout": 5}],
    "SessionEnd": [{"hooks": ["session-end-cleanup.sh"], "timeout": 5}]
  }
}
```

### `.claude/skill-rules.json`
Skill activation triggers for UserPromptSubmit hook. Version 2.0 features:
- Python/FastAPI path patterns (replaced TypeScript)
- Chinese keyword support (双语支持)
- MyStocks-specific skills:
  - `database-architecture-guidelines` (critical priority)
  - `python-quality-patterns` (high priority)
  - `backend-dev-guidelines` (high priority, FastAPI-aware)

### `.claude/build-checker-python.json`
Stop hook quality checks configuration:
```json
{
  "version": "2.0",
  "errorThreshold": 10,
  "repos": {
    "/opt/claude/mystocks_spec": {
      "qualityChecks": [
        {"name": "critical_imports", "command": "python -c 'from src.core import ...'", "critical": true},
        {"name": "backend_syntax", "command": "find web/backend -name '*.py' -exec python -m py_compile {} \\;"}
      ]
    }
  }
}
```

---

## Hooks Lifecycle

### Execution Order in Typical Development Flow

1. **SessionStart** → Task Master context injected
   - Claude receives current in-progress tasks
   - User continues work from last session

2. **UserPromptSubmit** → Skills activated
   - User: "创建API接口"
   - Hook activates `backend-dev-guidelines` skill
   - Claude responds with FastAPI best practices

3. **PostToolUse (Edit/Write)** → Dual tracking
   - File Edit Tracker logs edited file
   - Database Schema Validator checks architecture (if database file)

4. **Stop** → Quality gate check
   - Reads all edited files from edit log
   - Runs Python quality checks
   - Blocks if errors ≥ 10

5. **SessionEnd** → Cleanup
   - Removes current session from edit log
   - Truncates log if > 5,000 lines

---

## Compliance with Claude Official Specifications

All hooks follow [Claude官方hooks文档](https://docs.claude.com/en/docs/claude-code/hooks):

### Exit Codes ✅
- `exit 0`: Allow/Success (used by all non-blocking hooks)
- `exit 2`: Block operation (used by Stop hook when errors ≥ threshold)
- `exit 1`: Warning (not currently used, reserved for future)

### JSON Output Format ✅
All hooks using JSON output use official `hookSpecificOutput` structure:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "⚠️ Warning message here...",
    "decision": "block",
    "reason": "Explanation...",
    "errorDetails": {...}
  }
}
```

### Stdout Injection ✅
Only SessionStart and UserPromptSubmit hooks use stdout for Claude context injection.

### Timeouts ✅
All timeouts are reasonable for their operations:
- 3-5s for fast operations (logging, pattern matching)
- 120s for comprehensive quality checks (Stop hook)

---

## Testing and Validation

### Automated Testing
See `HOOKS_TESTING_REPORT.md` for comprehensive test plan (23 test cases across 6 phases).

### Manual Testing Recommendations

#### Test 1: Database Validator
```python
# Edit any Python file and add this line:
tick_data_df.to_sql('tick_data', postgres_engine)  # ❌ Wrong database!

# Expected: Hook outputs warning via additionalContext
```

#### Test 2: Stop Hook Quality Gate
```python
# Edit a Python file and introduce syntax error:
def broken_function(
    return "missing closing parenthesis"

# Then try to stop Claude
# Expected: Stop hook blocks with exit 2, shows syntax error
```

#### Test 3: SessionStart Context Injection
```bash
# Set a task to in-progress in Task Master
task-master set-status --id=1 --status=in-progress

# Start new Claude session
# Expected: Claude receives task context at startup
```

---

## Troubleshooting

### Hook Not Executing
1. Check permissions: `ls -l *.sh` (should be `-rwxr-xr-x`)
2. Check registration: `cat ../ settings.json | jq '.hooks'`
3. Enable debug mode: `export HOOK_NAME_DEBUG=true`

### Mock Data Validator Threshold Tuning
`post-tool-use-mock-data-validator.sh` supports environment-variable thresholds for reducing noise or increasing sensitivity:

- `MOCK_VALIDATOR_PRICE_MIN` (default: `3`)
  - Trigger when hardcoded price-related fields (`price/open/close/high/low/volume/...`) count reaches this threshold.
- `MOCK_VALIDATOR_STOCK_CODE_MIN` (default: `5`)
  - Trigger when hardcoded stock-code literals count reaches this threshold.

Example:
```bash
export MOCK_VALIDATOR_PRICE_MIN=6
export MOCK_VALIDATOR_STOCK_CODE_MIN=8
```

Use higher values to reduce warnings in large legacy files; use lower values for stricter detection in newly modified modules.

### Stop Hook Too Strict
Adjust error threshold in `.claude/build-checker-python.json`:
```json
{
  "errorThreshold": 20  // Increase from 10 to 20
}
```

### Database Validator False Positives
Edit `post-tool-use-database-schema-validator.sh` and modify `DANGEROUS_PATTERNS` associative array.

### Edit Log Growing Too Large
SessionEnd hook auto-limits to 5,000 lines. If needed, manually clean:
```bash
tail -n 1000 .claude/edit_log.jsonl > .claude/edit_log.jsonl.tmp
mv .claude/edit_log.jsonl.tmp .claude/edit_log.jsonl
```

---

## Development Guidelines

### Adding New Quality Checks to Stop Hook
1. Edit `.claude/build-checker-python.json`
2. Add new check to `qualityChecks` array:
```json
{
  "name": "mypy_check",
  "description": "类型检查",
  "command": "mypy src/ web/backend/app/ --ignore-missing-imports",
  "critical": false,
  "timeout": 30
}
```

### Adding New Database Architecture Rules
1. Edit `post-tool-use-database-schema-validator.sh`
2. Add pattern to `DANGEROUS_PATTERNS`:
```bash
["new_pattern.*PostgreSQL"]="⚠️ New anti-pattern warning"
```

### Creating New Hooks
1. Copy template from existing hook
2. Follow Claude exit code specs (0/1/2)
3. Use `hookSpecificOutput` for JSON output
4. Test thoroughly before production
5. Add execute permission: `chmod +x new-hook.sh`
6. Register in `.claude/settings.json`

---

## Documentation

- **HOOKS_IMPROVEMENT_PLAN.md**: Original 5-phase migration plan
- **HOOKS_IMPROVEMENT_COMPLETION_REPORT.md**: Detailed completion report with test results
- **HOOKS_TESTING_REPORT.md**: Comprehensive test plan (23 test cases)
- **README.md**: This file - User guide and reference

---

## Support and Maintenance

### Reporting Issues
1. Check logs: Enable debug mode for specific hook
2. Review test cases in `HOOKS_TESTING_REPORT.md`
3. Check Claude official docs: https://docs.claude.com/en/docs/claude-code/hooks
4. Consult completion report for known issues

### Version History
- **v1.0** (Pre-Nov 2025): TypeScript/Node.js hooks
- **v2.0** (2025-11-11): **Current** - Python/FastAPI hooks with dual-database architecture support

---

**Maintained By**: Claude Code Assistant
**Last Review**: 2025-11-11
**Status**: ✅ Production Ready
**Compliance**: ✅ Claude Official Specs v2024

### 6. Stop Hook (Three-Layer Task Recorder)
**File**: `stop-three-layer-task-recorder.sh`
**Purpose**: 在 Claude 响应结束时触发后台记录任务，将结果同步到三层记录体系
**Timeout**: 8 seconds
**Behavior**: Non-blocking (`exit 0`, 输出 `{}`)

**Background Task**:
- 异步执行 `record_three_layers.py`（`nohup` 后台）
- 读取 `transcript_path` 最后一条 assistant 消息
- 基于完成关键词判断是否“任务完成”
- 去重后写入三层记录

**Three-Layer Outputs**:
1. **Layer 1** (`TASK.md`)
   - 维护自动区块 `AUTO_LAYER1_START/END`
   - 更新当前会话的 Now/Next/Blocked 快照
2. **Layer 2** (`TASK-REPORT.md`)
   - 仅在检测到“任务完成”时追加自动记录条目
3. **Layer 3** (`docs/worklogs/claude-auto/YYYY-MM-DD.md`)
   - 每日归档完成项，便于后续检索

**State & Dedupe**:
- 状态文件：`.claude/task-recorder-state.json`
- 去重键：`session_id + assistant_message_id`

**Notes**:
- 若需提高“完成识别”准确性，可在 Claude 最终交付时显式使用“已完成/Completed”等关键词。
- 如不希望自动记录某次输出，可在本次响应后手工回退对应条目（见项目文档回滚命令）。

### 7. Stop Hook (Graphiti Task Closeout Reporter)
**File**: `stop-graphiti-task-closeout.sh`
**Purpose**: 在 Claude 响应结束时监听完成态收尾语句，并把标准化任务总结写入 Graphiti
**Timeout**: 8 seconds
**Behavior**: Non-blocking (`exit 0`, 输出 `{}`)

**Background Task**:
- 异步执行 `record_graphiti_closeout.py`（`nohup` 后台）
- 读取 `transcript_path` 最后一条 assistant 消息和最近 user 消息
- 仅在命中完成短语且未命中否定短语时触发写入
- 通过共享 CLI 合同 `scripts/runtime/coordctl.py graphiti remember` 写入 Graphiti

**Trigger Policy**:
- 正向短语示例：`收尾已完成`、`任务完成`、`已完成`、`完成了`、`已修复`、`done`、`finished`、`task completed`
- 否定短语示例：`未完成`、`尚未完成`、`not completed`、`待继续`

**Payload Highlights**:
- `event_type`
- `session_id`
- `actor_cli`
- `project_root`
- `summary`
- `completion_phrase`
- `changed_files`
- `verification`
- `request_context`
- `audit`

**State & Dedupe**:
- 状态文件：`.claude/graphiti-closeout-state.json`
- 去重键：`session_id + assistant_message_id`
- 仅成功写入 Graphiti 的 closeout 会进入 processed 去重集合

**Failure Handling**:
- Graphiti 写入失败不会阻塞 Stop
- 本地状态文件会记录失败摘要，供后续审计与排查
