# Context-Mode GitNexus Workflow Implementation Plan

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

## 背景

本项目同时使用 `context-mode` 与 GitNexus。两者不是替代关系，而是前后承接关系：

- `context-mode` 是上下文与输出治理层，负责把命令输出、日志、报告、文件分析、网页内容和历史上下文压缩进可搜索知识库，避免 raw 输出淹没上下文窗口。
- GitNexus 是代码知识图谱与变更风险层，负责符号调用关系、执行流、影响面、重构 rename 和提交前变更影响确认。

正确关系是：`context-mode` 管“信息怎么进入上下文”，GitNexus 管“代码改动会影响谁”。

## 目标

- 让 `context-mode -> GitNexus -> edit -> validate -> detect/analyze` 成为默认工作流。
- 避免 `context-mode` 因为更常用而隐式替代 GitNexus 的代码影响分析职责。
- 在实际 hook 中形成证据链：GitNexus 调用会落盘为 evidence，编辑和提交门禁读取 evidence。
- 保持可绕过机制，避免在紧急维护或 GitNexus 索引不可用时卡死开发。

## 分工模型

| 层级 | 工具 | 职责 | 典型触发 |
|---|---|---|---|
| Intake | `context-mode` | 大输出治理、批量收集、日志/报告/文档分析、历史会话检索 | `ctx_batch_execute`、`ctx_execute_file`、`ctx_search` |
| Code Graph Gate | GitNexus | 符号定位、调用图、影响分析、重构风险、提交前影响确认 | `query`、`context`、`impact`、`detect_changes`、`rename` |
| Edit | Agent 编辑工具 | 代码、配置、文档修改 | `Edit`、`Write`、`apply_patch` |
| Validate | `context-mode` + 项目命令 | 语法、测试、构建、日志分析 | `bash -n`、JSON 校验、pytest、npm、PM2/E2E |
| Refresh | Git hooks + GitNexus | 提交后刷新本地代码图谱 | `gitnexus analyze` |

## 默认状态机

```text
用户请求
  -> context-mode 收集/压缩上下文
  -> 判断是否涉及代码符号或 hook/配置行为修改
  -> GitNexus query/context/impact
  -> 编辑代码
  -> context-mode 承接测试/日志/构建输出
  -> GitNexus detect_changes 或 staged scope 检查
  -> commit
  -> post-commit gitnexus analyze
```

## Hook 设计

### 1. GitNexus Evidence Recorder

Claude `PostToolUse` 监听 GitNexus MCP 工具：

- `mcp__gitnexus__query`
- `mcp__gitnexus__context`
- `mcp__gitnexus__impact`
- `mcp__gitnexus__detect_changes`
- `mcp__gitnexus__rename`
- `mcp__gitnexus__cypher`

每次调用写入：

```text
.claude/gitnexus-evidence.jsonl
```

记录字段包括：

- `timestamp`
- `session_id`
- `repo`
- `tool_name`
- `action`
- `target`
- `scope`
- `direction`
- `success`
- `risk`

### 2. Stop Gate

Claude `Stop` 阶段检查：

- 本轮是否有代码类文件编辑记录。
- 本轮是否有 GitNexus evidence。
- 若缺失 evidence，则输出明确提示。

默认行为可由环境变量控制：

```text
GITNEXUS_WORKFLOW_GATE_MODE=block
GITNEXUS_WORKFLOW_GATE_MODE=warn
DISABLE_GITNEXUS_WORKFLOW_GATE=1
SKIP=gitnexus-workflow-gate
```

### 3. Pre-Commit Gate

`.githooks/pre-commit` 检查 staged code-like 文件：

- 若只改文档，放行。
- 若 staged 文件包含 `.py`、`.ts`、`.vue`、`.sh`、`.json` hook/config 等代码或运行配置，要求存在近期 GitNexus evidence。
- 若缺失 evidence，阻断提交，并提示先运行 GitNexus impact 或 detect_changes。

### 4. Post-Commit Refresh

`.githooks/post-commit` 异步运行：

```bash
gitnexus analyze "$PROJECT_ROOT"
```

跳过方式：

```text
DISABLE_GITNEXUS_POST_COMMIT_ANALYZE=1
SKIP=gitnexus-analyze
```

同步执行方式：

```text
GITNEXUS_ANALYZE_SYNC=1
```

## 文件结构

- Create: `docs/agents/context-mode-gitnexus-workflow.md`  
  保存本方案和实施说明。
- Create: `scripts/hooks/gitnexus_workflow_gate.py`  
  统一实现 evidence 记录、Stop gate、pre-commit gate。
- Create: `.claude/hooks/post-tool-use-gitnexus-evidence-recorder.sh`  
  Claude `PostToolUse` 包装脚本，将 GitNexus MCP 调用传给 Python gate。
- Create: `.claude/hooks/stop-gitnexus-workflow-gate.sh`  
  Claude `Stop` 包装脚本，检查本轮编辑是否有 GitNexus evidence。
- Modify: `.claude/settings.json`  
  接入 evidence recorder 和 Stop gate。
- Modify: `.githooks/pre-commit`  
  接入 staged code-like 文件的 GitNexus workflow gate。
- Modify: `.githooks/post-commit`  
  添加异步 `gitnexus analyze` 刷新。

## 实施任务

### Task 1: 文档落盘

- [x] **Step 1:** 创建本方案文档。
- [x] **Step 2:** 明确 `context-mode` 与 GitNexus 的分工、状态机和 hook 接入点。

### Task 2: Evidence 与 Gate 脚本

- [x] **Step 1:** 新增统一 Python gate。
- [x] **Step 2:** 新增 Claude `PostToolUse` evidence recorder 包装脚本。
- [x] **Step 3:** 新增 Claude `Stop` gate 包装脚本。

### Task 3: Hook 接线

- [x] **Step 1:** 在 `.claude/settings.json` 中接入 GitNexus evidence recorder。
- [x] **Step 2:** 在 `.claude/settings.json` 中接入 Stop gate。
- [x] **Step 3:** 在 `.githooks/pre-commit` 中接入 staged gate。
- [x] **Step 4:** 在 `.githooks/post-commit` 中接入异步 `gitnexus analyze`。

### Task 4: 验证

- [x] **Step 1:** 校验 Python 脚本语法。
- [x] **Step 2:** 校验 shell hook 语法。
- [x] **Step 3:** 校验 `.claude/settings.json` JSON 语法。
- [x] **Step 4:** 运行 gate 的 dry-run/无 staged 场景。
- [x] **Step 5:** 使用 GitNexus `detect_changes` 检查本次变更影响范围。

## 运行规则

实际工作时，agent 应按以下顺序执行：

1. 使用 `ctx_search(sort: "timeline")` 恢复历史上下文。
2. 使用 `ctx_batch_execute`、`ctx_execute_file`、`ctx_search` 收集大范围上下文。
3. 定位到具体符号、脚本或配置行为后，使用 GitNexus `query/context/impact`。
4. 编辑代码。
5. 使用 context-mode 承接测试、构建、日志和质量门禁输出。
6. 提交前 stage 本批文件，并运行 GitNexus staged scope 检查。
7. 提交后由 post-commit hook 异步刷新 GitNexus 索引。

## 边界与豁免

- GitNexus 不一定索引所有 hook/config 文件；此时 impact 可能返回 `Target not found`。不能伪造 blast radius，应报告 GitNexus 无法覆盖，并用脚本语法检查、JSON 校验、staged diff 和 smoke test 补偿。
- `context-mode` 不提供调用图语义，不能替代 GitNexus 的符号级影响分析。
- 紧急情况下可使用 `SKIP=gitnexus-workflow-gate` 或 `DISABLE_GITNEXUS_WORKFLOW_GATE=1`，但任务汇报必须说明原因。
- `post-commit` 的 `gitnexus analyze` 默认异步执行，避免拖慢提交；需要严格刷新时设置 `GITNEXUS_ANALYZE_SYNC=1`。
