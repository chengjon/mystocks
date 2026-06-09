# Overview Operations Testing Wave 1

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 的 `6.x` 第一批收敛动作。
> 本波次聚焦三件事：收缩 `overview/operations/testing` 根入口、补齐 taxonomy 与 decision register、迁出 `docs/testing/legacy-cn/` 历史中文测试资料。

## Overview Outcome

### Before

- `docs/overview/README.md` 仍带有旧式 docs-root 导览职责
- `docs/overview/INDEX.md` 仍是 broad flat index
- overview 根入口与 `docs/README.md` / `documentation-system.md` 存在角色重叠

### After

- `docs/overview/README.md` 改为 transition index
- `docs/overview/INDEX.md` 改为 secondary index
- overview 根入口只保留项目总览与 onboarding supporting routing，不再模拟 docs 根入口

## Operations Outcome

### Before

- `docs/operations/README.md` 混入历史指标表、联系方式和大而全目录清单
- `docs/operations/INDEX.md` 仍是平铺式全量索引

### After

- `docs/operations/README.md` 收敛为 canonical runbook trunk
- `docs/operations/INDEX.md` 收敛为 secondary index，只分流到 active runbook families
- 当前运行状态判断明确回到 PM2 / health / logs / monitoring，而不是文档里的历史表格

## Testing Outcome

### Before

- `docs/testing/README.md` 和 `docs/testing/INDEX.md` 同时承担 active guidance 与 legacy 导览
- `docs/testing/legacy-cn/` 仍处于 active tree
- 活跃链接仍能把读者导向旧中文测试资料

### After

- `docs/testing/README.md` 保留为唯一 testing trunk
- `docs/testing/INDEX.md` 改为 secondary index
- `docs/testing/legacy-cn/` 已归档到 `archive/docs/testing/legacy-cn-2026-04-08/`
- `docs/INDEX.md` 与相关 guide 引用已改为 archived path 或 active trunk

## Governance Metadata Changes

- taxonomy 新增或收紧了：
  - `overview-transition-indexes`
  - `docs-root-secondary-index`
  - `operations-secondary-indexes`
  - `testing-secondary-indexes`
  - `testing-legacy-cn`
- decision register 已把 wave 3 执行状态写回 `overview/operations/testing`

## Executed Archive Batch

- source:
  - `docs/testing/legacy-cn/`
- archive target:
  - `archive/docs/testing/legacy-cn-2026-04-08/`

## Resulting Decision Changes

- `docs/overview/README.md` + `docs/overview/INDEX.md`: from overlapping root entrypoints to executed transition indexes
- `docs/operations/INDEX.md`: from broad flat index to executed secondary index
- `docs/testing/INDEX.md`: from mixed active/legacy index to executed secondary index
- `docs/testing/legacy-cn/`: from gated archive candidate to executed archive batch
