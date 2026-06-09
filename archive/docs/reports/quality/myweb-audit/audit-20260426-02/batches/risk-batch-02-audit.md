# Batch Audit Report: risk-batch-02

## Scope
- Module: risk
- Pages:
  - /risk/management
- Batch rationale: close the routed risk-management holdings-derived truth gap and fold the live-holdings-derived rule back into the audit skill

## Agent Summary

### route-inventory
- `/risk/management` continues to resolve directly to canonical `web/frontend/src/views/risk/Center.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave beyond truthful holdings-derived overview rendering.

### data-state-audit
- One medium-severity holdings-derived truth defect remained: the routed page loaded live positions data while keeping embedded sector rows, static concentration-threshold samples, and unsupported risk-ratio placeholders on the same primary surface.

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
- Repeated issue pattern: a routed holdings page can accidentally lend live credibility to adjacent derived panels that still depend on embedded portfolio samples rather than current payload fields.
- Occurrence basis:
  - `/risk/management` previously fetched real positions data while still showing static sector rows, concentration-threshold samples, and unsupported ratio placeholders on the same primary workbench surface
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/risk-tabs/riskManagementData.ts`
  - `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskOverviewPanel.vue`
  - `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskStatsGrid.vue`
- Suggested follow-up scope: extend future routed portfolio and holdings audits in `risk`, `trade`, and `strategy` to verify that every derived exposure or ratio panel is bounded by the current live payload field set.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: holdings-derived truth > generic placeholder cleanup
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/risk-tabs/riskManagementData.ts`
- shared-impact review items: none
- fixes applied:
  - `risk-management-issue-01`
- deferred items: none

## Fix Summary
- Updated the canonical risk-management route to initialize from an honest empty holdings state rather than sample risk data.
- Reworked the shared holdings mapper so only live positions-derived concentration rows remain, while unsupported risk metrics now degrade to `null`.
- Updated the shared overview and stats panels so missing sector or higher-order analytics inputs render `待接入` or `未校验` states instead of embedded sector samples, threshold strings, or numeric placeholders.
- Added routed holdings-mapper and shared-panel regression coverage for the new truthful degradation behavior.
- Extended `myweb-audit` with a `v1.23` holdings-derived truth rule so future audits catch this pattern earlier.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-02-repair-approval.yaml`
- Approved issue ids:
  - `risk-management-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `risk-batch-02`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `node --test web/frontend/src/views/artdeco-pages/risk-tabs/__node_tests__/riskManagementData.test.ts` -> passed `5/5`
  - `node --test web/frontend/src/views/artdeco-pages/risk-tabs/__node_tests__/riskManagementHelpers.test.ts web/frontend/src/views/artdeco-pages/risk-tabs/__node_tests__/riskManagementModulePresence.test.ts` -> passed `7/7`
  - `npx vitest run src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskOverviewPanel.spec.ts src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskStatsGrid.spec.ts` -> passed `12/12`
  - `npx vitest run src/views/risk/__tests__/Overview.spec.ts src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskOverviewPanel.spec.ts src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskStatsGrid.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts tests/unit/views/risk-center-template-retention.spec.ts tests/unit/config/risk-route-canonical-paths.spec.ts` -> passed `26/26`
  - `timeout 180s npm run type-check` -> passed
  - targeted routed-page verification confirmed:
    - a real backend login token plus system `google-chrome` reached `/risk/management`
    - the live route issued real `GET /api/v1/trade/positions` requests
    - the live stats grid now shows `最大回撤`, `夏普比率`, `年化波动率`, `贝塔值`, and `索提诺比率` as `未校验 / 待接入`
    - the live overview surface now shows `行业分布待接入` and `集中度指标待接入`
    - the embedded sector rows `科技股`, `医药生物` and static threshold strings `65 / 70`, `12 / 15` are absent
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` runner still cannot execute Chromium on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged" })` is recorded as mixed-staged observation only for this run
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-02-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-02-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-02-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-02-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-02-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict (`risk_level: low`, `changed_files: 83`, `changed_count: 300`, `affected_count: 0`)

## Next Batch Plan
- If the user continues the risk-domain audit, apply the strengthened hybrid live-surface truth, automation false-positive handling, and holdings-derived truth rules to the remaining routed risk pages and related holdings workbenches.
