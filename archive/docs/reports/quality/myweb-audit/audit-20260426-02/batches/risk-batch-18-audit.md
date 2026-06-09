# Batch Audit Report: risk-batch-18

## Scope
- Module: risk
- Pages:
  - /risk/stop-loss
- Batch rationale: close the canonical `/risk/stop-loss` selector-pending truth gap so a new primary watchlist without its own verified stocks slice cannot keep the previous watchlist cards visible

## Agent Summary

### route-inventory
- `/risk/stop-loss` remains the canonical routed stop-loss workbench at `web/frontend/src/views/risk/StopLoss.vue`.
- The same owner continues to feed the legacy wrapper `web/frontend/src/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue`, so the repair stays page-local and consumer-compatible.

### functional-audit
- No new routed click-flow defect required a separate repair wave beyond honest selector-pending truth for the canonical route.

### data-state-audit
- One high-severity selector-pending truth defect remained: after the primary watchlist changed, the route already switched hero provenance and placeholder stats to the new selector but kept rendering the previous watchlist cards until the new stocks request resolved.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a routed page can switch to a new selector shell and still leak the previous selector's rows or cards while the new selector remains unresolved.
- Occurrence basis:
  - `/risk/stop-loss` already tracked selector-scoped verified request provenance for fail states
  - the owner still left `stopLossItems` populated until the new `watchlists/:watchlistId/stocks` request returned, so pending selector switches leaked the prior selector cards
- Shared component or token involved:
  - none for the approved repair
- Suggested follow-up scope: continue applying `v1.71 + v1.69 + v1.66` checks to routed pages that already switch shell metadata to a new selector but may still leave prior rows or cards visible during unresolved first loads.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` selector-pending truth issue
- priority order applied: selector-owned visible-row truth > page-local containment > routed verification hardening
- primary owners selected:
  - `web/frontend/src/views/risk/StopLoss.vue`
- shared-impact review items:
  - `web/frontend/src/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue` was reviewed as a direct consumer and did not require a separate repair
- fixes applied:
  - `risk-stop-loss-issue-18`
- deferred items: none

## Fix Summary
- Cleared visible stop-loss cards immediately when the resolved primary watchlist selector changes away from the last verified selector key.
- Preserved the earlier stale-retention behavior for same-selector refresh failures after success.
- Added an owner-level regression for the `selector switch + pending new stocks slice` path.
- Added a Phase 4 routed matrix assertion for the same selector-pending truth scenario.
- Reused existing `myweb-audit v1.71`; no new skill-version bump was required.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-18-repair-approval.yaml`
- Approved issue ids:
  - `risk-stop-loss-issue-18`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `risk-batch-18`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/risk/__tests__/StopLoss.spec.ts src/views/risk/__tests__/Alerts.spec.ts src/views/risk/__tests__/Overview.spec.ts src/views/risk/__tests__/News.spec.ts src/views/risk/__tests__/Center.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts tests/unit/views/risk-center-template-retention.spec.ts` -> passed `30/30`
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `38` structurally valid tests including the new unresolved selector-switch assertion for `/risk/stop-loss`
  - targeted system-Chrome browser verification confirmed:
    - the initial verified shell shows `REQ_ID: req-live-stoploss-101-success` and visible `贵州茅台 / 宁德时代`
    - after the primary selector switches to an unresolved watchlist, hero changes to `REQ_ID: N/A / CRITICAL: -- / TRIGGERED: --`
    - the top stats change to `-- / -- / -- / --`
    - the visible stop-loss card count drops to `0`
    - the same controlled proof confirms stale `贵州茅台` no longer remains visible while the route reports `止损标的同步中...`
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system `google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-18-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-18-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-18-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-18-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-18-manifest.yaml` -> passed
  - `git diff --check -- web/frontend/src/views/risk/StopLoss.vue web/frontend/src/views/risk/__tests__/StopLoss.spec.ts web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-18-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-18-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-18-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-18-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/risk-stop-loss-selector-pending-card-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/risk-batch-18-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - `timeout 180s npm run type-check` still fails only on pre-existing unrelated errors in `src/api/services/dashboardService.ts` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- Continue applying `v1.71 + v1.69 + v1.66` to routed pages that switch shell metadata to a new selector but may still leave prior rows or cards visible during unresolved first loads.
