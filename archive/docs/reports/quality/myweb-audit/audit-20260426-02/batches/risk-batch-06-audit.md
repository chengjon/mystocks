# Batch Audit Report: risk-batch-06

## Scope
- Module: risk
- Pages:
  - /risk/management
- Batch rationale: apply the strengthened `v1.35` unsupported-tab slice truth rule so the canonical risk-management stock tab stops promising executable single-name analysis and remains switchable in a real browser

## Agent Summary

### route-inventory
- `/risk/management` continues to resolve directly to canonical `web/frontend/src/views/risk/Center.vue`.

### functional-audit
- One high-severity routed interaction defect dominated this batch: the stock tab could not switch in a live browser session because the custom tab control lacked explicit non-submit semantics.

### data-state-audit
- The stock tab still had no separate live single-name contract, yet its routed subtitle and panel copy implied a working actionable analysis slice instead of a pending entry surface.

### visual-artdeco-audit
- No batch-dominant visual defect required a repair wave.

### responsive-a11y-audit
- No new desktop-breakpoint defect required a repair wave.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a multi-tab routed page can pass code-review and component checks while still failing in a real browser when custom tab controls inherit default button semantics, and the same unsupported tab can continue to promise a live actionable slice even though it only hosts a placeholder entry surface.
- Occurrence basis:
  - `/risk/management` previously left `个股分析` stuck on the overview slice during live browser interaction
  - the same stock-tab subtitle still claimed `形成可执行的个股风控动作` and the panel only showed a selector hint
- Shared component or token involved:
  - none confirmed; the approved repair stayed page-local
- Suggested follow-up scope: continue applying `v1.35` to other canonical multi-tab routes that replace shared tab controls or expose unsupported secondary slices.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: tab-switch truth > unsupported-tab semantics > cosmetic cleanup
- primary owners selected:
  - `web/frontend/src/views/risk/Center.vue`
  - `web/frontend/src/views/artdeco-pages/risk-tabs/riskManagementHelpers.ts`
  - `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskStockPanel.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `risk-management-issue-03`
- deferred items: none

## Fix Summary
- Added `type="button"` to the canonical custom risk-tab control so the stock tab remains switchable in a live browser.
- Rewrote the stock-tab subtitle, panel title, CTA, and pending copy so the routed slice now states it is only an entry surface and that single-name risk analysis is still pending integration.
- Updated the stock-tab toast to stay aligned with the same pending-integration truth.
- Added node, component, route-family, and phase4 structural regressions, then verified the real PM2 route with Playwright-library plus system `google-chrome`.
- Upgraded `myweb-audit` to `v1.35` so future audits must check both unsupported-tab truth and live-browser tab operability for custom routed tab controls.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-06-repair-approval.yaml`
- Approved issue ids:
  - `risk-management-issue-03`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `risk-batch-06`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `node --test web/frontend/src/views/artdeco-pages/risk-tabs/__node_tests__/riskManagementHelpers.test.ts web/frontend/src/views/artdeco-pages/risk-tabs/__node_tests__/riskManagementModulePresence.test.ts` -> passed `7/7`
  - `npx vitest run src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskStockPanel.spec.ts src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskOverviewPanel.spec.ts src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskStatsGrid.spec.ts tests/unit/views/risk-center-template-retention.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts` -> passed `22/22`
  - `npx vitest run src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskStockPanel.spec.ts tests/unit/views/risk-center-template-retention.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts` -> passed `9/9`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `12` structurally valid tests including the new stock-tab route assertion
  - targeted routed-page verification confirmed:
    - the real PM2 `/risk/management` route issued `200` responses for `/api/health/ready`, `/api/health`, and `/api/v1/trade/positions`
    - the same route now switches `个股分析` to `aria-selected="true"`
    - the stock-tab subtitle now reads `当前仅保留个股风险分析入口，个股级仓位、止损与波动联动待接入。`
    - the stock panel now shows `个股风险分析入口`, `查看接入说明`, and `当前路由仍复用组合级风险数据，不直接生成单标的风控动作。`
    - the CTA toast now reads `个股风险分析入口待接入，当前仅保留接入说明与反馈。`
    - the old action promise `形成可执行的个股风控动作` and the old hint `选择持仓股票查看详细风险分析` are absent
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` is recorded as mixed-staged observation only for this run
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- Continue applying `v1.35` to remaining canonical multi-tab routes, prioritizing tabs that promise route-local analysis or actions without a true tab-local contract and routes that replace shared tab controls with custom button implementations.
