# Batch Audit Report: risk-batch-03

## Scope
- Module: risk
- Pages:
  - /risk/management
- Batch rationale: close the routed risk-management alert-policy truth gap so live positions or exposure data cannot be mislabeled as true alerts, stop-loss states, or action recommendations when no alert-policy inputs exist

## Agent Summary

### route-inventory
- `/risk/management` continues to resolve directly to canonical `web/frontend/src/views/risk/Center.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave beyond truthful holdings-observation rendering on the alert-style table.

### data-state-audit
- One medium-severity alert-policy truth defect remained: the routed page loaded live positions data while presenting those rows as a true alert table with stop-loss states and action recommendations derived locally from position size or PnL.

### visual-artdeco-audit
- No batch-dominant visual defect required a repair wave.

### responsive-a11y-audit
- No new desktop-breakpoint defect required a repair wave.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Pattern Findings
- Repeated issue pattern: a routed holdings page can accidentally impersonate the behavior of a real alert engine once live positions data arrives, even though the page never received policy-backed alert or stop-loss inputs.
- Occurrence basis:
  - `/risk/management` previously fetched real `/api/v1/trade/positions` data but still labeled rows as `风险预警列表`
  - the same route inferred stop-loss states such as `已触发` or `接近` and action buttons such as `止损`, `减仓`, or `监控` without a dedicated alert-policy contract
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/risk-tabs/riskManagementData.ts`
  - `web/frontend/src/views/artdeco-pages/risk-tabs/riskManagementHelpers.ts`
  - `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskOverviewPanel.vue`
- Suggested follow-up scope: extend future routed risk, trade, and strategy audits to verify that alert-style tables and action buttons never borrow credibility from nearby live holdings or exposure data when alert-policy inputs are absent.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: alert-policy truth > generic copy cleanup
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/risk-tabs/riskManagementData.ts`
- shared-impact review items: none
- fixes applied:
  - `risk-management-issue-02`
- deferred items: none

## Fix Summary
- Reworked the shared holdings-alert mapper so routed position rows stay in `unverified` and `待复核` states until explicit alert-policy fields are present.
- Updated the overview panel so holdings-derived rows render `风险观察列表`, `策略状态`, and `复核状态` plus an explicit pending-policy note instead of old alert-engine wording.
- Updated the canonical risk-management route so header meta shows `OBS` and action toasts clearly state that stop-loss or reduce-position policy inputs are still pending.
- Added node, component, route-family, and routed browser verification coverage for the new truthful observation mode.
- Extended `myweb-audit` with a `v1.25` alert-policy truth rule so future audits catch this pattern earlier.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-03-repair-approval.yaml`
- Approved issue ids:
  - `risk-management-issue-02`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `risk-batch-03`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - routed alert-policy verification blocked service workers and fulfilled `/api/v1/trade/positions` directly to isolate the holdings-observation path
- Regression checks completed:
  - `node --test src/views/artdeco-pages/risk-tabs/__node_tests__/riskManagementData.test.ts src/views/artdeco-pages/risk-tabs/__node_tests__/riskManagementHelpers.test.ts src/views/artdeco-pages/risk-tabs/__node_tests__/riskManagementModulePresence.test.ts` -> passed `12/12`
  - `npx vitest run src/views/risk/__tests__/Overview.spec.ts src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskOverviewPanel.spec.ts src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskStatsGrid.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts tests/unit/views/risk-center-template-retention.spec.ts tests/unit/config/risk-route-canonical-paths.spec.ts` -> passed `27/27`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `10` structurally valid tests including the strengthened risk-management assertion path
  - targeted routed-page verification confirmed:
    - `/risk/management` issued `/api/health/ready`, `/api/health`, and `/api/v1/trade/positions`
    - the routed page now shows `风险观察列表`, `策略状态`, `复核状态`, `未校验`, and `待复核`
    - clicking the first action button shows `贵州茅台：当前仅生成持仓风险观察，止损/减仓策略参数待接入。`
    - the old table title `风险预警列表` and stop-status labels such as `已触发` or `接近` are absent after repair
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged" })` is recorded as mixed-staged observation only for this run
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-03-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-03-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-03-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-03-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-03-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- If the user continues the risk-domain audit, apply the strengthened alert-policy truth, policy-derived action truth, and holdings-derived truth rules to any remaining routed pages that mix live holdings data with locally inferred action or alert semantics.
