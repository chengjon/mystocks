## Mainline Governance (Required)

> 所有字段必填；缺失将视为未完成治理信息。

- mainline_id: `<L1-...>`
- task_type: `<fix|feature|cleanup>`
- openspec_change_id: `<change-id|N/A>`
- approval_status: `<approved|not_required|pending|rejected>`

## Task Card

- task_card_path: `governance/mainline/task-cards/pr-<PR号>.yaml`

> task card 是唯一机器事实源。PR 模板只做 reviewer 镜像，不替代 `task_card_path` 中的 machine-readable `function_tree`。

## Function Tree Mapping (Required when functionality, scope, or entrypoints change)

> 若本次改动涉及功能变化、入口变化、跨域影响或行为变更，请完整填写；纯治理/纯格式调整可写 `N/A`。

- change_type: `<feature|bugfix|docs|refactor>`
- function_tree_domain_id: `<domain-01|...|domain-10|meta-governance|N/A>`
- function_tree_node_id: `<domain-xx-node-yy|meta-governance-mainline|N/A>`
- function_tree_secondary_domains: `<domain-xx,... | [] | N/A>`
- affected_entrypoints: `<governance|api|frontend|core|tests|operations | N/A>`
- function_tree_update_status: `<required|not-needed|N/A>`
- function_tree_exemption_reason: `<why exempt or self-bootstrap | N/A>`

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
