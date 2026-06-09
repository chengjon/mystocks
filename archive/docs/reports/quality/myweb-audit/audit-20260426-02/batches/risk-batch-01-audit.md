# Batch Audit Report: risk-batch-01

## Scope
- Module: risk
- Pages:
  - /risk/overview
- Batch rationale: close the routed risk-overview hybrid live-surface truth gap and fold the mixed-live-placeholder rule back into the audit skill

## Agent Summary

### route-inventory
- `/risk/overview` continues to resolve directly to canonical `web/frontend/src/views/risk/Overview.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave beyond truthful tab-state rendering.

### data-state-audit
- One medium-severity hybrid live-surface truth defect remained: the routed page loaded real monitoring rules but kept embedded alert copy and fabricated KPI metrics on the same primary surface.
- Comparator spot-checks showed `/risk/alerts` and `/risk/news` already handled empty live data honestly and did not require a repair wave.

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
- Repeated issue pattern: routed overview pages can accidentally lend live credibility to adjacent placeholder KPI cards or alert panels when only one nearby slice is actually wired to a real API.
- Occurrence basis:
  - `/risk/overview` previously fetched real rule data while still showing embedded alert messages and fabricated overview metrics on the same primary workbench surface
- Shared component or token involved:
  - none; ownership stayed page-local in `web/frontend/src/views/risk/Overview.vue`
- Suggested follow-up scope: extend future routed overview audits in `risk`, `system`, and `strategy` to inspect whether any partially live page mixes one real slice with adjacent embedded KPI or alert placeholders.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: hybrid live-surface truth > generic placeholder cleanup
- primary owners selected:
  - `web/frontend/src/views/risk/Overview.vue`
- shared-impact review items: none
- fixes applied:
  - `risk-overview-issue-01`
- deferred items: none

## Fix Summary
- Updated the canonical risk overview page to fetch both live alert rules and live alert records.
- Replaced embedded alert messages with live-derived alert rows and an honest empty-state fallback.
- Replaced fabricated KPI and overview metric numbers with explicit `未校验` and `待接入` states until a real risk-summary source exists.
- Added canonical routed-page and wrapper-retention regression coverage, and updated routed E2E expectations to match live alert-record truth.
- Extended `myweb-audit` with a `v1.22` hybrid live-surface truth rule so future audits catch this pattern earlier.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-01-repair-approval.yaml`
- Approved issue ids:
  - `risk-overview-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `risk-batch-01`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/risk/__tests__/Overview.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts` -> passed `6/6`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/risk-overview.spec.ts tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `11` tests
  - `npx playwright test tests/e2e/risk-overview.spec.ts --project=chromium` -> blocked by missing local Playwright chromium executable
  - targeted routed-page verification confirmed:
    - a real backend login token plus system `google-chrome` reached `/risk/overview`
    - the live route issued `GET /api/v1/monitoring/alert-rules` and `GET /api/v1/monitoring/alerts?page=1&page_size=50`
    - the live KPI strip now shows `今日告警 0` and `仓位集中度 未校验`
    - the live overview table now shows `组合Beta`, `波动率(20日)`, `最大回撤(近3月)`, and `VaR(95%)` as `未校验 / 待接入`
    - the live alert tab now shows `暂无预警消息。`
    - the embedded placeholder alert strings and fabricated KPI numbers are absent
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` runner still cannot execute Chromium on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
  - fake-token same-tab automation could loop through the login guard, so batch conclusions use real backend login plus system `google-chrome` as route truth
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged" })` is recorded as mixed-staged observation only for this run
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-01-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-01-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-01-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-01-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- If the user continues the risk-domain audit, apply the strengthened hybrid live-surface truth, automation false-positive handling, runtime-status truth, and payload-normalization truth rules to the remaining routed risk pages and related overview workbenches.
