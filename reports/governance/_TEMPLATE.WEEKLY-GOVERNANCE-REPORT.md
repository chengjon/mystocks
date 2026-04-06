# WEEKLY GOVERNANCE REPORT

> Weekly governance template aligned with `docs/standards/technical-debt-governance-charter-v1.md`.

- Week Range: `<yyyy-mm-dd .. yyyy-mm-dd>`
- Report Owner: `<owner>`
- Generated At: `<timestamp>`

## 6.1 概览
- 本周新增债务数: `<count>`
- 本周消化债务数: `<count>`
- 当前存量债务数: `<count>`
- 过期未清理例外数: `<count>`

## 6.2 关键指标（KPI）

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| 新增 Type 错误数 | `<value>` | `<value>` | `N/A` | `<= 0` | `<command/file>` |
| 新增 suppression 数 | `<value>` | `<value>` | `N/A` | `<= 0` | `<command/file>` |
| 新增 skip/xfail 数 | `<value>` | `<value>` | `N/A` | `<= 0` | `<command/file>` |
| 例外合规率 | `<value>` | `<value or N/A>` | `N/A` | `100%` | `<source>` |
| 到期清理率 | `<value>` | `<value or N/A>` | `N/A` | `>= 90%` | `<source>` |

## 6.3 热点与行动
- Top 10 热点文件（含路径）:
  - `<path>`
- 下周治理任务（owner + deadline）:
  - `<task>`
- 阻塞项与所需决策:
  - `<blocker>`

## 6.4 结构性技术债补充项

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| 活跃兼容层 / shim 数量 | `<value>` | `<value or N/A>` | `<value or N/A>` | `<target or N/A>` | `<source>` |
| 活跃临时入口 / `*_new.py` 数量 | `<value>` | `<value or N/A>` | `<value or N/A>` | `<target or N/A>` | `<source>` |
| 活跃机械拆分文件数量 | `<value>` | `<value or N/A>` | `<value or N/A>` | `<target or N/A>` | `<source>` |
| 活跃备份文件数量 | `<value>` | `<value or N/A>` | `<value or N/A>` | `<target or N/A>` | `<source>` |
| 已满足退出条件但尚未退役对象数量 | `<value>` | `<value or N/A>` | `<value or N/A>` | `<target or N/A>` | `<source>` |
| 本周已完成代码路径判定 / 功能树判定清理项数量 | `<value>` | `<value or N/A>` | `<value or N/A>` | `<target or N/A>` | `<source>` |

## Structural Notes
- canonical_source changes:
  - `<note or (none)>`
- cleanup / removal verdicts:
  - `<note or (none)>`
- temporary asset ledger delta:
  - `<note or (none)>`
