# Architecture Legacy Archive Wave 1

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/architecture/legacy-cn/` 的第一轮 bounded archive 执行。

## Why

- `docs/architecture/legacy-cn/` 已被 taxonomy 明确标记为 `archive_candidate`
- 该分支属于历史中文架构资料，不应继续作为活跃架构导航的一部分
- 在活动树中仍存在来自索引页的直链，需要先清理再归档

## Changes

- 从活动索引中移除 `docs/architecture/legacy-cn/02-架构与设计文档/*` 的直链
- 在以下索引中改为“已归档快照”提示，而不是继续当作活跃入口：
  - `docs/architecture/INDEX.md`
  - `docs/INDEX.md`
  - `architecture/INDEX.md`
- 执行归档：
  - `docs/architecture/legacy-cn/` -> `archive/docs/architecture/legacy-cn-2026-04-08/`

## Gate Check

- canonical replacement: `docs/architecture/README.md` + 活跃 architecture indexes
- inbound-link status: `cleaned`
- retention duty: 历史资料保留，选择 `archive` 而非 `delete`
- decision register: 已登记为 `archive` 并记录执行结果

## Expected Effect

- 活跃 architecture 导航不再把历史中文分支当作当前主线入口
- 历史资料仍可在 `archive/docs/architecture/legacy-cn-2026-04-08/` 中保留
- 文档治理后续可以继续按 cluster 推进 archive/delete，而不需要回退到逐篇免责声明修补
