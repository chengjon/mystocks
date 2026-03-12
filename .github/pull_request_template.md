## Mainline Governance (Required)

> 所有字段必填；缺失将视为未完成治理信息。

- mainline_id: `<L1-...>`
- task_type: `<fix|feature|cleanup>`
- openspec_change_id: `<change-id|N/A>`
- approval_status: `<approved|not_required|pending|rejected>`

## Task Card

- task_card_path: `governance/mainline/task-cards/pr-<PR号>.yaml`

## Function Tree Mapping (Required when functionality, scope, or entrypoints change)

> 若本次改动涉及功能变化、入口变化、跨域影响或行为变更，请完整填写；纯治理/纯格式调整可写 `N/A`。

- change_type: `<feature|bugfix|docs|refactor>`
- function_domain: `<01-市场数据与行情|02-技术分析与指标|03-策略管理与回测|04-风险管理与监控|05-投资组合与交易|06-监控与告警|07-高级分析与AI|08-系统管理与配置|09-数据存储与管理|10-公告与信息|N/A>`
- function_tree_node: `<二级/三级节点名称 | N/A>`
- affected_entrypoints: `<规范|API/契约|前端/交互|核心代码|测试与验证|运行与排障 | N/A>`
- function_tree_updated: `<yes|no|not-needed>`

## Verification And Risk (Required)

- verification_evidence: `<commands/results/key paths>`
- risk_and_rollback: `<impact/risk/rollback steps>`

## Large File Governance (Required)

> 适用于本次改动涉及 `src/` 或 `web/backend/app/` 的情况；如不适用请明确写 `N/A`。

- largest_touched_python_file: `<path> (<lines>) | N/A`
- independent_responsibility_added: `<yes|no>`
- large_file_guardrails: `<passed|not_applicable>`  <!-- line-count + bare-print -->
- backlog_updated: `<yes|no|not_needed>`
- helper_split_introduced: `<yes|no>`
