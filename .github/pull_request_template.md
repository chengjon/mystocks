## Mainline Governance (Required)

> **参考模板说明**:
> 本文件是用于生成提案、计划、任务、检查清单或 PR 内容的参考模板，用于统一结构与字段。
> 模板字段、示例文本和占位符不自动等同于当前事实；生成或填写时，仓库级共享规则与审批门禁仍以 `architecture/STANDARDS.md` 为准，执行流程与协作约束再参考根目录 `AGENTS.md`。


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
> 若本次新增主路由目录 / 主页面、主 API 包路由或 canonical 后端入口，必须将 `function_tree_update_status` 设为 `required`，并同步更新 `docs/FUNCTION_TREE.md`。
> 若本次退役兼容层、旧页面、旧 API 根入口、shim、re-export 或平行实现，必须在 `function_tree_exemption_reason` 或 PR 说明中写清继任入口 / 兼容保留状态。

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

## Frontend Gate Evidence (Required when `web/frontend/**`, `.github/workflows/frontend-testing.yml`, `.github/workflows/e2e-testing.yml`, `.github/workflows/visual-testing.yml` change)

> 如不涉及前端/UI/视觉/前端 CI，请写 `N/A`。如涉及，请按实际执行结果填写，不允许写“同前”“已跑过”“应该通过”。
> reviewer 速查可参考 [docs/guides/frontend/PR_GATE_QUICK_REFERENCE.md](/opt/claude/mystocks_spec/docs/guides/frontend/PR_GATE_QUICK_REFERENCE.md)。

- frontend_gate_scope: `<none|unit-only|frontend-mainline|frontend-mainline+visual|N/A>`
- pm2_status: `<mystocks-backend online @ http://localhost:8020 ; mystocks-frontend online @ http://localhost:3020 | N/A>`
- unit_gate: `<npm run test:unit:stable => 33 files / 343 tests passed | N/A>`
- selector_gate: `<npm run test:e2e:selectors => pass/fail + details | N/A>`
- business_smoke_gate: `<npm run test:e2e:business-smoke => browser/project + passed/failed/skipped | N/A>`
- a11y_gate: `<npm run test:e2e:axe => browser/project + passed/failed/skipped | N/A>`
- lighthouse_gate: `<npm run test:e2e:lighthouse => urls + finalDisplayedUrl summary + score summary | N/A>`
- visual_gate_dashboard: `<npm run test:visual:dashboard => browser/project + passed/failed | N/A>`
- visual_gate_charts: `<npm run test:visual:charts => browser/project + passed/failed | N/A>`
- cross_browser_evidence: `<firefox/webkit smoke results or workflow run id | N/A>`
- type_ceiling_evidence: `<npm run test:type-ceiling => current errors / ceiling / baseline | N/A>`

## Large File Governance (Required)

> 适用于本次改动涉及 `src/` 或 `web/backend/app/` 的情况；如不适用请明确写 `N/A`。

- largest_touched_python_file: `<path> (<lines>) | N/A`
- independent_responsibility_added: `<yes|no>`
- large_file_guardrails: `<passed|not_applicable>`  <!-- line-count + bare-print -->
- backlog_updated: `<yes|no|not_needed>`
- helper_split_introduced: `<yes|no>`
