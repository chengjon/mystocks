# MyStocks Web 开发工作目录说明

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
