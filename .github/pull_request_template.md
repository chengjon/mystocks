## Mainline Governance (Required)

> 所有字段必填；缺失将视为未完成治理信息。

- mainline_id: `<L1-...>`
- task_type: `<fix|feature|cleanup>`
- openspec_change_id: `<change-id|N/A>`
- approval_status: `<approved|not_required|pending|rejected>`

## Task Card

- task_card_path: `governance/mainline/task-cards/pr-<PR号>.yaml`

## Large File Governance (Required)

> 适用于本次改动涉及 `src/` 或 `web/backend/app/` 的情况；如不适用请明确写 `N/A`。

- largest_touched_python_file: `<path> (<lines>) | N/A`
- independent_responsibility_added: `<yes|no>`
- large_file_guardrails: `<passed|not_applicable>`  <!-- line-count + bare-print -->
- backlog_updated: `<yes|no|not_needed>`
- helper_split_introduced: `<yes|no>`
