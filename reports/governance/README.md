# Governance Reports

> **补充规范说明**:
> 本文件是项目补充标准、执行细则或专题规范，不是仓库共享规则的唯一事实来源。
> 仓库级共享规则总入口仍以 `architecture/STANDARDS.md` 为准；执行流程、命令与协作约束再参考根目录 `AGENTS.md`。本文件用于补充某一专题的执行细则、约束或参考模板。
>
> 若本文件与 `architecture/STANDARDS.md`、根目录 `AGENTS.md` 或当前已批准执行口径不一致，应优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md` 与当前实现；若无冲突，则按本文件的专题范围执行。


本目录用于保存治理任务、治理任务汇报和治理周报。

## Naming

- 任务文件：`YYYY-MM-DD-<topic>.TASK.md`
- 任务汇报：`YYYY-MM-DD-<topic>.TASK-REPORT.md`
- 周报：`YYYY-MM-DD-<topic>.WEEKLY.md` 或等价命名

## Templates

- 任务模板：`reports/governance/_TEMPLATE.TASK.md`
- 汇报模板：`reports/governance/_TEMPLATE.TASK-REPORT.md`
- 周报模板：`reports/governance/_TEMPLATE.WEEKLY-GOVERNANCE-REPORT.md`

## Required Structural Debt Fields

当任务涉及以下任一情形时，必须按模板填写结构性技术债字段：

- 迁移收口
- 重复层 / 平行层治理
- 兼容层 / `shim` / re-export
- `*_new.py`、临时入口、实验入口
- `part1/part2/part3` 机械拆分
- `.bak` / `.backup` / 备份快照
- 清理 / 删除 / 归档
- 技术债指标、周报、基线更新

最低要求：

- 迁移类：`canonical_source`、`compatibility_surface`、`callers_or_consumers`、`verification_command`、`exit_condition`
- 清理类：`code_path_verdict`、`function_tree_verdict`、`removal_basis`、`keep_reason`
- 指标类：`measured`、`baseline`、`inferred`、`target`、`source_or_command`

## Asset Ledger Encoding

临时层 / 兼容层 / 备份文件类不要再在正文里平行发明另一套字段，统一落在 `Temporary / Compatibility Asset Ledger` 表中：

- `introduced_by` 必须写成 `issue_or_task=<...>; created_at=<...>`
- `exit_condition` 承载 `sunset_condition`
- `planned_removal_milestone` 单独成列；未知时写 `N/A`
- `target_removal_date` 填计划日期或 `N/A`
- `current_status` 使用 `active`、`planned-removal`、`retained`、`removed`

本目录下的 `*.TASK.md` / `*.TASK-REPORT.md` 若命中结构性技术债场景，会被 `python scripts/dev/quality_gate/governance_report_fields_guard.py --format json` 校验上述表头和关键字段格式。

## Source of Truth

规则正文与裁定标准不在本目录重复维护。

- 结构性技术债规则唯一事实来源：
  - `architecture/STANDARDS.md` 第“三、迁移收口与技术债治理规则”
- 门禁、基线、例外、周报执行细则：
  - `docs/standards/technical-debt-governance-charter-v1.md`
