# Mongo Multi-CLI Operation Checklist

## Purpose

本清单给 main CLI 与 worker CLI 提供当前有效的最小操作顺序。

当前约定：

- Mongo 是任务状态与审批流的唯一真相源
- Graphiti MCP 是长期记忆层
- Graphiti 的 canonical repo-local 入口是共享 CLI，而不是某个助手专属 hook
- `TASK.md` / `TASK-REPORT.md` 仅作为 Mongo 导出的可读快照
- Worker 收到任务后的统一开工口令保持为：
  - `请按你当前 worktree 的 TASK.md 开工。`

## Main CLI Checklist

### 派单前

1. 确认当前任务范围与 owner
2. 如需历史上下文，先查 Graphiti：
   - `get_status`
   - `search_nodes`
   - `search_memory_facts`
3. 在 Mongo control plane 中创建或核对 work item
4. 如需生成 worker 可读快照，导出：

```bash
python scripts/runtime/coordctl.py work export-task <WORK_ITEM_ID> --output-path /path/to/TASK.md --output json
python scripts/runtime/coordctl.py work export-task-report <WORK_ITEM_ID> --output-path /path/to/TASK-REPORT.md --output json
```

### 正式派单

1. 确保 worker worktree 中的 `TASK.md` 是从 Mongo 导出的当前快照，至少包含：
   - 任务目标
   - 范围边界
   - Mongo 操作要求
   - Graphiti 记忆要求
   - 最小验证要求
2. 发给 worker 的统一指令：

```text
请按你当前 worktree 的 TASK.md 开工。
```

### 复核时

1. 查 Mongo：
   - `claim`
   - `plan`
   - `submit`
   - `ready_for_review`
2. 查 Graphiti：
   - handoff 摘要
   - 历史事实
   - review 结论

## Worker CLI Checklist

### 收到任务后

1. 阅读当前 worktree 的 `TASK.md`
2. 阅读：
   - `docs/guides/GRAPHITI_MCP_WORKFLOW.md`
   - 涉及的 `openspec` / `docs` / ownership 文件
3. 先在 Mongo control plane 中开工留痕：
   - `work claim`
4. 如需要历史上下文，再查 Graphiti：
   - 优先运行 `graphiti preflight`
   - 或手工执行 `get_status` / `search_nodes` / `search_memory_facts`

### 执行中

1. 只修改任务范围内文件
2. 任务分解走 Mongo：
   - `plan add`
   - `plan mark`
3. 每完成一个批次：
   - 在 `TASK-REPORT.md` 记录证据
   - 必要时向 Graphiti 写入 handoff / fact summary
   - 如需 repo-local 预检结果，统一读取 Graphiti preflight 审计事件或 `TASK-REPORT` 的 Graphiti 区块

### 提交前

1. 做最小必要验证
2. 更新 `TASK-REPORT.md`
3. 在 Mongo control plane 中提交：
   - `work submit`
4. 不要只把状态写到 Graphiti 而跳过 Mongo

## Boundary Summary

### Mongo

负责：

- work item lifecycle
- owner / worker
- claim / plan / submit
- ready_for_review / verified / merged

### Graphiti

负责：

- 长期记忆
- handoff 摘要
- 架构 / 审核 / 排障事实
- 恢复上下文时的历史检索

repo-local canonical 命令：

- `python scripts/runtime/coordctl.py graphiti preflight ...`
- `python scripts/runtime/coordctl.py graphiti remember ...`
- `python scripts/runtime/coordctl.py graphiti search ...`
- `python scripts/runtime/smoke_graphiti_cli.py ...`

说明：

- assistant-specific hook 只应包装这组共享 CLI
- `@graphiti` 一类 prompt 标记只是可选 sugar，不是主接口
- `graphiti preflight` 仍然是 Mongo-backed scoped mode
- `graphiti remember` / `graphiti search` 可用于 direct generic mode

## Fast Reference

### Main CLI

```text
查状态 -> Mongo
查历史事实 -> Graphiti
给 worker 的唯一开工口令 -> 请按你当前 worktree 的 TASK.md 开工。
```

### Worker CLI

```text
开工留痕 -> Mongo claim
Graphiti 预检 -> coordctl graphiti preflight
做任务分解 -> Mongo plan
导出快照 -> coordctl work export-task / export-task-report
写长期记忆 -> coordctl graphiti remember
提审 -> Mongo submit
```
