# Frontend Gates PR Draft

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


## Suggested PR Title

`test(frontend): consolidate CI, E2E, Lighthouse, and visual gates`

## Short Summary

- Consolidate frontend verification around canonical package scripts for auth smoke, business smoke, a11y, Lighthouse, dashboard visual, and chart visual checks.
- Align `frontend-testing.yml`, `e2e-testing.yml`, and `visual-testing.yml` with those scripts so CI and local runs share the same entrypoints.
- Fix LHCI protected-route auditing so `dashboard`, `market/realtime`, and `strategy/repo` are measured as authenticated business pages instead of login redirects.
- Restore active dashboard and chart visual baselines, split visual artifacts into `dashboard` and `charts`, and add grouped visual summary output.
- Update reviewer-facing docs and PR evidence fields so frontend gate status is reported consistently.

## Mainline Governance

- mainline_id: `L1-frontend-gates-2026-03-23`
- task_type: `feature`
- openspec_change_id: `N/A`
- approval_status: `not_required`

## Task Card

- task_card_path: `N/A`

## Function Tree Mapping

- change_type: `feature`
- function_tree_domain_id: `domain-frontend`
- function_tree_node_id: `frontend-testing-gates`
- function_tree_secondary_domains: `[tests, operations, governance]`
- affected_entrypoints: `frontend,tests,operations,governance`
- function_tree_update_status: `not-needed`
- function_tree_exemption_reason: `frontend gate consolidation only`

## Verification And Risk

- verification_evidence:
  - `npm run test:unit:stable` => 33 files / 343 tests passed
  - `npm run test:e2e:selectors` => pass
  - `npm run test:e2e:auth` => chromium 2/2 passed
  - `npm run test:e2e:business-smoke` => chromium 39/39 passed
  - `npm run test:e2e:axe` => chromium 2/2 passed
  - `npm run test:e2e:lighthouse` => 4 URLs processed, protected routes stay on business pages
  - `npm run test:visual:dashboard` => chromium 6/6 passed
  - `npm run test:visual:charts` => chromium 4/4 passed
  - cross-browser smoke => firefox 12/12 passed, webkit 12/12 passed
  - `npm run build` => passed
  - `npm run test:type-ceiling` => 0 errors within ceiling 0
- risk_and_rollback:
  - Risk is concentrated in frontend test tooling and CI wiring, not runtime business logic.
  - If CI instability appears, rollback can be limited to `.github/workflows/*`, `web/frontend/package.json`, and the visual/E2E helper files added in this change.
  - Runtime-facing fallback: revert `web/frontend/src/stores/auth.ts`, `web/frontend/src/router/guards.ts`, and `web/frontend/src/api/services/dashboardService.ts` together.

## Frontend Gate Evidence

- frontend_gate_scope: `frontend-mainline+visual`
- pm2_status: `mystocks-backend online @ http://localhost:8020 ; mystocks-frontend online @ http://localhost:3020`
- unit_gate: `npm run test:unit:stable => 33 files / 343 tests passed`
- selector_gate: `npm run test:e2e:selectors => passed`
- business_smoke_gate: `npm run test:e2e:business-smoke => chromium / 39 passed / 0 failed / 0 skipped`
- a11y_gate: `npm run test:e2e:axe => chromium / 2 passed / 0 failed / 0 skipped`
- lighthouse_gate: `npm run test:e2e:lighthouse => login/dashboard/market/realtime/strategy/repo audited; finalDisplayedUrl stayed on each target page; scores: login P1.00 A0.91 BP0.96, dashboard P0.97 A0.92 BP0.96, market P1.00 A0.86 BP0.96, strategy P1.00 A0.94 BP0.96`
- visual_gate_dashboard: `npm run test:visual:dashboard => chromium / 6 passed / 0 failed`
- visual_gate_charts: `npm run test:visual:charts => chromium / 4 passed / 0 failed`
- cross_browser_evidence: `firefox smoke => 12 passed / 0 failed ; webkit smoke => 12 passed / 0 failed`
- type_ceiling_evidence: `npm run test:type-ceiling => current errors 0 / ceiling 0 / baseline reports/analysis/tech-debt-baseline.json frontend_type_errors=0`

## Large File Governance

- largest_touched_python_file: `N/A`
- independent_responsibility_added: `yes`
- large_file_guardrails: `not_applicable`
- backlog_updated: `not_needed`
- helper_split_introduced: `yes`

## Summary

This PR consolidates the frontend verification stack into a reviewable mainline:

- adds canonical Playwright auth and business-smoke entrypoints
- aligns `frontend-testing.yml` with the business-smoke gate
- aligns `e2e-testing.yml` with cross-browser auth/menu/kline smoke
- makes LHCI measure authenticated protected pages instead of login redirects
- restores dashboard and chart visual baselines with grouped package scripts
- splits visual workflow outputs and summary into `dashboard` and `charts`
- updates E2E docs, reviewer quick reference, and PR evidence requirements

## File Groups

### CI / Workflow

- `.github/workflows/frontend-testing.yml`
- `.github/workflows/e2e-testing.yml`
- `.github/workflows/visual-testing.yml`

### Frontend Tooling

- `web/frontend/package.json`
- `web/frontend/package-lock.json`
- `web/frontend/lighthouserc.cjs`
- `web/frontend/scripts/lighthouse-auth.cjs`
- `web/frontend/scripts/stable-unit-suite.js`
- `web/frontend/validate-e2e-setup.js`

### Runtime Support

- `web/frontend/src/stores/auth.ts`
- `web/frontend/src/stores/__tests__/auth-guard.spec.ts`
- `web/frontend/src/router/guards.ts`
- `web/frontend/src/api/services/dashboardService.ts`
- `web/frontend/src/api/services/__tests__/dashboardService.spec.ts`

### Browser Tests

- `web/frontend/tests/e2e/auth-login.spec.ts`
- `web/frontend/tests/e2e/critical/menu-navigation-fixed.spec.ts`
- `web/frontend/tests/visual/pages/dashboard.spec.ts`
- `web/frontend/tests/visual/components/charts/backtest.spec.ts`
- `web/frontend/tests/visual/components/charts/technical-analysis.spec.ts`
- `web/frontend/tests/visual/config/visual.config.ts`
- `web/frontend/tests/visual/utils/helpers.ts`

### Test Gates / Docs

- `web/frontend/tests/unit/config/lighthouse-mainline-gates.spec.ts`
- `web/frontend/tests/unit/config/testing-mainline-gates.spec.ts`
- `web/frontend/tests/unit/config/visual-chart-gates.spec.ts`
- `web/frontend/tests/unit/scripts/stable-unit-suite.spec.ts`
- `web/frontend/tests/unit/scripts/validate-e2e-setup.spec.ts`
- `web/frontend/tests/unit/workflows/ci-workflow-gates.spec.ts`
- `web/frontend/tests/README-E2E.md`
- `docs/testing/e2e/README.md`
- `docs/guides/frontend/PR_GATE_QUICK_REFERENCE.md`
- `docs/guides/frontend/INDEX.md`
- `.github/pull_request_template.md`
- `docs/superpowers/plans/2026-03-23-frontend-test-gates.md`
