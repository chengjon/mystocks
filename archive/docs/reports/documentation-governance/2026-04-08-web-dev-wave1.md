# Web Dev Transition Wave 1

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/web-dev/` 的第一轮 bounded transition 执行。

## Why

- `docs/web-dev/` 只剩两个入口文件，但活动索引仍把它当作独立家族暴露
- 当前更完整的 Web Hook / 工作流说明已经位于 `docs/guides/hooks/`
- hook 指南和历史材料仍显式提到 `docs/web-dev/`，因此不适合直接删除目录

## Changes

- `docs/INDEX.md` 的 Web Dev 入口改为直接指向：
  - `docs/guides/hooks/WEB_DEV_HOOKS_GUIDE.md`
  - `docs/guides/hooks/web-dev-hooks-guide.md`
- `docs/web-dev/GUIDE.md` 改为 transition/compatibility guide
- `docs/web-dev/INDEX.md` 改为 secondary compatibility index，不再充当主入口

## Gate Check

- canonical replacement:
  - `docs/guides/hooks/WEB_DEV_HOOKS_GUIDE.md`
  - `docs/guides/hooks/web-dev-hooks-guide.md`
- inbound-link status:
  - active navigation cleaned
  - compatibility path retained for older references
- retention duty:
  - 仍需保留最薄入口层，避免 hook 相关旧引用立即失效
- decision:
  - `merge-into-trunk`，当前执行到 transition stage，而非 physical delete

## Expected Effect

- Web Hook / 工作流说明回到 `docs/guides/hooks/` 主干家族
- `docs/web-dev/` 不再作为活动树里的第二个并行 guide 家族
- 后续若清理 hook 文档中的旧路径引用，可再评估是否彻底移除 `docs/web-dev/`
