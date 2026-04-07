# MyStocks Web 开发工作目录说明

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


> `docs/web-dev/` 是 Web 开发相关的特殊说明目录，只保留入口文档与工作流说明，不再承载运行态追踪产物。

## 当前定位

- 保留 `GUIDE.md`、`INDEX.md` 作为 Web Hook / 工作流入口文档
- 运行态追踪日志统一写入 `var/log/web-dev/tracing/web-edit-tracker.jsonl`
- 实际写入脚本为 `.claude/hooks/post-tool-use-web-dev-file-tracker.sh`
- 详细方案与历史说明位于 `docs/guides/hooks/WEB_DEV_HOOKS_GUIDE.md` 与 `docs/guides/hooks/web-dev-hooks-guide.md`

## 收纳规则

- `docs/web-dev/` 只放说明、入口和少量工作流文档
- JSONL、调试日志、追踪产物等运行态文件统一放入 `var/log/`
- 若后续新增长期维护指南，优先收敛到 `docs/guides/`
