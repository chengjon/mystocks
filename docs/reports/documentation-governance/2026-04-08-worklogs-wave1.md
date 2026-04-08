# Worklogs Merge Wave 1

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/worklogs/` 平行历史树的第一轮 bounded merge 执行。

## Why

- `docs/reports/worklogs/` 已经是历史工作日志的主干目录
- `docs/worklogs/` 形成了第二套平行 worklog 树，只承载少量增量文件
- 活跃导航仍从 `docs/INDEX.md` 暴露该平行目录，不符合 trunk-first 治理原则

## Changes

- 将 `docs/worklogs/claude-auto/` 下的 4 份增量 worklog 合并到 `docs/reports/worklogs/claude-auto/`
- 更新 `docs/reports/worklogs/INDEX.md`，纳入 2026-03-24、2026-04-06、2026-04-07、2026-04-08
- 更新 `docs/INDEX.md`，把 worklogs 入口改为 `reports/worklogs/`
- 执行收口：删除已空的 `docs/worklogs/` 平行目录

## Gate Check

- canonical replacement: `docs/reports/worklogs/`
- inbound-link status: `cleaned` for active-tree navigation
- retention duty: 历史日志仍需保留，因此执行 `merge-into-trunk` 而非 delete
- decision register: 已登记并记录执行结果

## Expected Effect

- 历史工作日志只保留一套主干目录
- `docs/INDEX.md` 不再把 `docs/worklogs/` 暴露为并行历史树
- 后续新增 worklog 应直接进入 `docs/reports/worklogs/`
