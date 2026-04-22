# Change: Add Stop Hook Graphiti Task Closeout

## Why

当前仓库已经具备 Claude hooks、Graphiti MCP 与共享 Graphiti CLI 合同，但“任务完成后的收尾总结”仍依赖手动执行，导致后续检查时存在三个问题：

- 完成态总结不稳定，容易漏记到 Graphiti；
- 已完成任务的总结格式不统一，不利于后续搜索和审计；
- Stop hook 已能读取 transcript 并识别 completion 文案，但尚未把这类完成信号投影到 Graphiti 记忆层。

本次变更希望在不引入第二套记忆入口的前提下，扩展现有 Stop hook 链路：当 assistant 最后消息明确表达“收尾已完成”“任务完成”“已完成”等完成态语义时，自动生成标准化任务总结，并通过现有共享 Graphiti CLI 合同上报，保留审计元数据供后续检查。

## What Changes

- add a Stop-hook closeout reporter that listens for completion-style final assistant messages;
- define a completion trigger policy with dedupe and negative-pattern protection to reduce false positives;
- define a standard Graphiti closeout payload format for task summary, verification, changed files, and audit metadata;
- route the write through the existing shared Graphiti CLI contract instead of direct hook-private MCP calls;
- record hook behavior, output format, and opt-out / coexistence rules in project docs and tests.

## Impact

- Affected specs:
  - `agent-memory-workflow`
- Affected code:
  - `.claude/settings.json`
  - `.claude/hooks/`
  - `scripts/runtime/`
  - `tests/unit/services/maestro/`
  - `docs/guides/hooks/`
- Expected outcomes:
  - completion summaries are automatically projected into Graphiti when a task is clearly finished,
  - closeout payloads are normalized and auditable,
  - follow-up review can search Graphiti for task-level closeout evidence instead of relying on ad hoc manual notes.
