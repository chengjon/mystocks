# Batch Audit Report: risk-batch-04

## Scope
- Module: risk
- Pages:
  - /risk/stop-loss
- Batch rationale: close the routed stop-loss threshold-policy truth gap so watchlist and quote data cannot be mislabeled as active stop-loss monitoring when real threshold inputs such as `stop_loss_price` are absent

## Agent Summary

### route-inventory
- `/risk/stop-loss` continues to resolve directly to canonical `web/frontend/src/views/risk/StopLoss.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave beyond truthful threshold-policy degradation on the stop-loss surface.

### data-state-audit
- One medium-severity threshold-policy truth defect remained: the routed page loaded watchlist rows and quote data while presenting those rows as an active stop-loss radar even when the current payload lacked real stop-loss thresholds.

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
- Repeated issue pattern: a routed threshold or stop-loss page can accidentally impersonate active monitoring once watchlist symbols and quotes arrive, even though the page never received real threshold-policy inputs.
- Occurrence basis:
  - `/risk/stop-loss` previously fetched real or intercepted watchlist rows plus quotes but still labeled the route as `止损观察中`
  - the same route rendered `STOP LOSS --` and `Distance to Stop --%` even when the current payload omitted `stop_loss_price`
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/risk-tabs/stopLossMonitorData.ts`
  - `web/frontend/src/views/risk/StopLoss.vue`
- Suggested follow-up scope: extend future routed risk, trade, and strategy audits to verify that threshold-dependent cards, distances, and badges never borrow credibility from nearby symbol or quote truth when policy inputs are absent.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: threshold-policy truth > generic copy cleanup
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/risk-tabs/stopLossMonitorData.ts`
- shared-impact review items: none
- fixes applied:
  - `risk-stop-loss-issue-01`
- deferred items: none

## Fix Summary
- Reworked the shared stop-loss mapper so rows without `stop_loss_price` are marked pending-policy and render `待接入` instead of fake threshold math placeholders.
- Updated the canonical stop-loss route so status, runtime message, and distance rendering degrade to `策略待接入` when watchlist rows lack real threshold inputs.
- Added node, routed component, and phase4 route-matrix coverage for the new pending-policy state.
- Extended `myweb-audit` with a `v1.29` threshold-policy truth rule so future audits catch this pattern earlier.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-04-repair-approval.yaml`
- Approved issue ids:
  - `risk-stop-loss-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `risk-batch-04`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - the live backend route naturally exercised the honest empty state, while the missing-threshold state was isolated through targeted watchlist and quote endpoint fulfillment
- Regression checks completed:
  - `node --test src/views/artdeco-pages/risk-tabs/__node_tests__/stopLossMonitorData.test.ts src/views/artdeco-pages/risk-tabs/__node_tests__/riskManagementData.test.ts src/views/artdeco-pages/risk-tabs/__node_tests__/riskManagementHelpers.test.ts src/views/artdeco-pages/risk-tabs/__node_tests__/riskManagementModulePresence.test.ts` -> passed `17/17`
  - `npx vitest run src/views/risk/__tests__/Overview.spec.ts src/views/risk/__tests__/StopLoss.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts` -> passed `7/7`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `11` structurally valid tests including the new pending-policy stop-loss assertion path
  - targeted routed-page verification confirmed:
    - the real PM2 `/risk/stop-loss` route issued `/api/health/ready`, `/api/health`, `/api/v1/monitoring/watchlists`, and `/api/v1/monitoring/watchlists/18/stocks`
    - the real routed page still shows `暂无监控标的` and `当前没有可用于止损监控的活跃标的。` when no active stop-loss rows exist
    - the targeted missing-threshold verification issued `/api/v1/monitoring/watchlists`, `/api/v1/monitoring/watchlists/101/stocks`, and `/api/v1/market/quotes`
    - under that controlled threshold-missing path, the routed page now shows `策略待接入`, `当前仅同步观察标的与行情，止损参数待接入。`, `STOP LOSS 待接入`, and `Distance to Stop 待接入`
    - the old active-monitoring status `止损观察中` is absent from the threshold-missing routed surface after repair
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged" })` is recorded as mixed-staged observation only for this run
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-04-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-04-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-04-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-04-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-04-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- If the user continues the risk-domain audit, apply the strengthened threshold-policy truth, alert-policy truth, and policy-derived action truth rules to remaining routed pages that compute threshold, trigger, or action semantics from partial live payloads.
