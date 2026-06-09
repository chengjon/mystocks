# Reports Root Refinement Wave 1

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 对 `docs/reports/` 根入口与 root-level markdown classification 的第一轮 refinement。

## Why

- `docs/reports/README.md` 仍停留在旧的 `Phase 10` 快照语义
- `docs/reports/INDEX.md` 仍是超大平铺索引
- `docs/reports/*.md` 根级历史文件未被 taxonomy 覆盖，造成大量 `unclassified`

## Changes

- `docs/reports/README.md` 改为 canonical historical-evidence trunk
- `docs/reports/INDEX.md` 改为 secondary index
- taxonomy 现在显式覆盖：
  - `docs/reports/*.md`
  - `docs/reports/INDEX.md`
- `docs/INDEX.md` 中 reports legacy-cn 入口改为 archived path

## Expected Effect

- reports root 不再把旧 phase snapshot 误导成当前主线
- root-level historical files 统一被表达为 `report`
- `docs/reports/` 的主要治理问题从“未分类”降级为“后续是否需要继续分波次归档”
