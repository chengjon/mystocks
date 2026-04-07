# TASK-REPORT

> **参考模板说明**:
> 本文件是模板、骨架或示例输入，不是当前共享规则、当前任务状态或当前实现结果的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md` 与对应主线模板/流程文档。
>
> 使用本模板时应结合当前任务上下文填写；模板中的占位内容、示例字段和默认值不得直接当作当前事实。


> Governance template. Copy this file to a dated task report under `reports/governance/` and then fill the placeholders.

- Issue Identifier: `<yyyy-mm-dd-scope-topic-owner>`
- Issue Title: `<task title>`
- Assigned Worker CLI: `<main|worker-name>`
- Current Status: `<planned|in_progress|verified|merged|archived>`
- Latest Progress: `<one-sentence latest progress>`
- Pending Request: `<True|False>`

## Updates
- `<timestamp>` `[status]` `<worker>`: `<summary>`

## Requests
- `<request or (none)>`

## Graphiti

- server_status: `<ok|error|(none)>`
- ingest_status: `<completed|pending|error|(none)>`
- search_summary: `<summary or (none)>`

## Detailed Updates

### `<timestamp>` `[status]` `<worker>`
- Summary: `<summary>`

#### Scope
- `<what this batch touched>`

#### Completed
- `<completed item>`

#### Structural Debt Disclosure
- canonical_source: `<single source of truth after closure or N/A>`
- compatibility_surface: `<compatibility surfaces retained or N/A>`
- callers_or_consumers: `<known callers/consumers or N/A>`
- verification_command: `<commands proving closure or N/A>`
- exit_condition: `<legacy retirement condition or N/A>`

#### Cleanup / Removal Decision
- code_path_verdict: `<used|unused-but-needs-proof|safe-to-remove|N/A>`
- function_tree_verdict: `<有效|失效但兼容保留|实验/灰度|重复冗余|待判定|N/A>`
- removal_basis: `<why removal is safe or N/A>`
- keep_reason: `<why object must remain or N/A>`

#### Temporary / Compatibility Asset Ledger Delta

> Use `introduced_by` = `issue_or_task=<...>; created_at=<...>`.

| path | type | owner | introduced_by | reason | exit_condition | planned_removal_milestone | target_removal_date | current_status |
|---|---|---|---|---|---|---|---|---|
| `<path or N/A>` | `<type>` | `<owner>` | `<issue_or_task=<task-or-issue>; created_at=<yyyy-mm-dd or unknown> or N/A>` | `<reason>` | `<condition>` | `<milestone or N/A>` | `<date or N/A>` | `<status or N/A>` |

#### Metrics Lens

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| `<metric>` | `<value or N/A>` | `<value or N/A>` | `<value or N/A>` | `<value or N/A>` | `<command/file/date>` |

#### Verification Evidence
- `<verification command>`

#### Current Status
- `<current state>`

#### Next
- `<next action or (none)>`

#### Risks / Notes
- `<risk or note or (none)>`
