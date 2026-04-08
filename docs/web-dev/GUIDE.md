# MyStocks Web Development Transition Guide

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


> `docs/web-dev/` 现已降级为兼容入口，不再作为 Web Hook / 工作流说明的主干目录。
> 当前主入口请优先阅读 `docs/guides/hooks/WEB_DEV_HOOKS_GUIDE.md` 与 `docs/guides/hooks/web-dev-hooks-guide.md`。

## Current Status

- `docs/web-dev/` 仅保留兼容入口，避免旧链接失效
- 运行态追踪日志统一写入 `var/log/web-dev/tracing/web-edit-tracker.jsonl`
- 实际写入脚本为 `.claude/hooks/post-tool-use-web-dev-file-tracker.sh`
- 权威说明位于：
  - `docs/guides/hooks/WEB_DEV_HOOKS_GUIDE.md`
  - `docs/guides/hooks/web-dev-hooks-guide.md`

## Routing

- 需要 Web Hook 方案、保护规则或运行说明：
  - 转到 `docs/guides/hooks/WEB_DEV_HOOKS_GUIDE.md`
  - 或 `docs/guides/hooks/web-dev-hooks-guide.md`
- 需要运行态追踪日志：
  - 转到 `var/log/web-dev/tracing/web-edit-tracker.jsonl`
- 后续新增长期维护文档：
  - 默认归入 `docs/guides/hooks/` 或相关 guide family

## Retention Rule

- `docs/web-dev/` 不再扩展为独立文档家族
- 仅在需要兼容旧入口时保留最薄说明层
