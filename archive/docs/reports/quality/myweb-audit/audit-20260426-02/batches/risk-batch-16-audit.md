# Batch Audit Report: risk-batch-16

## Scope
- Module: risk
- Pages:
  - /risk/overview
- Batch rationale: close the canonical `/risk/overview` partial-slice truth gap so a first-load alerts failure cannot hide a verified rules slice or collapse the whole route back to generic no-snapshot copy

## Agent Summary

### route-inventory
- `/risk/overview` remains the canonical routed risk overview workbench at `web/frontend/src/views/risk/Overview.vue`.
- The same owner continues to feed the legacy wrapper `web/frontend/src/views/artdeco-pages/risk-tabs/RiskOverviewTab.vue`, so the repair stays page-local and consumer-compatible.

### functional-audit
- No new routed click-flow defect required a separate repair wave beyond honest partial-slice truth for the canonical route.

### data-state-audit
- One high-severity routed partial-slice truth defect remained: the route treated rules and alerts as one global verified shell, so a first-load alerts failure hid a verified rules slice and rewrote the shell to `当前暂无已验证风险概览快照。`

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a routed page can already have one verified primary slice and still lie about route truth if a sibling primary slice fails before the first full page-level snapshot exists.
- Occurrence basis:
  - `/risk/overview` allowed `alert-rules` to verify independently
  - the route still used one route-global verified flag and one request id, so the `rules` slice could not surface its own verified truth when `alerts` failed
- Shared component or token involved:
  - none for the approved repair
- Suggested follow-up scope: continue applying `v1.71 + v1.69 + v1.66` checks to routed pages that aggregate multiple primary slices and might still collapse verified sibling slices into generic all-unavailable shells.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed partial-slice truth issue
- priority order applied: visible-slice truth > page-local containment > routed verification hardening
- primary owners selected:
  - `web/frontend/src/views/risk/Overview.vue`
- shared-impact review items:
  - `web/frontend/src/views/artdeco-pages/risk-tabs/RiskOverviewTab.vue` was reviewed as a direct consumer and did not require a separate repair
- fixes applied:
  - `risk-overview-issue-16`
- deferred items: none

## Fix Summary
- Added separate verified snapshot tracking for rules and alerts inside the canonical risk overview owner.
- Updated hero `REQ_ID`, summary cards, `RULES` meta, and runtime copy so a verified rules slice remains visible while alerts stay unresolved.
- Added an owner-level regression for the `rules success + alerts fail on first load` path.
- Added a Phase 4 routed matrix assertion for the same partial-slice truth scenario.
- Reused existing `myweb-audit v1.71`; no new skill-version bump was required.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-16-repair-approval.yaml`
- Approved issue ids:
  - `risk-overview-issue-16`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `risk-batch-16`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/risk/__tests__/Overview.spec.ts src/views/risk/__tests__/Alerts.spec.ts src/views/risk/__tests__/Center.spec.ts src/views/risk/__tests__/StopLoss.spec.ts src/views/risk/__tests__/News.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts tests/unit/views/risk-center-template-retention.spec.ts` -> passed `28/28`
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `36` structurally valid tests including the new `/risk/overview` partial-slice assertion
  - targeted system-Chrome browser verification confirmed:
    - the overview shell stays `REQ_ID: N/A / ALERTS: --` while only the rules slice is verified
    - the top stats stay partial as `2 / 2 / -- / 未校验`
    - after switching to `规则清单`, the route renders `REQ_ID: req-live-risk-overview-rules-first-success`, `RULES: 2`, and the verified rule content including `单票止损线`
    - the same controlled proof confirms `risk alerts unavailable，当前预警消息暂不可用。` and no longer shows `当前暂无已验证风险概览快照。`
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system `google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-16-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-16-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-16-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-16-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-16-manifest.yaml` -> passed
  - `git diff --check -- web/frontend/src/views/risk/Overview.vue web/frontend/src/views/risk/__tests__/Overview.spec.ts web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-16-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-16-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-16-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-16-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/risk-overview-partial-slice-selector-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/risk-batch-16-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - `timeout 180s npm run type-check` still fails only on pre-existing unrelated errors in `src/api/services/dashboardService.ts` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- Continue applying `v1.71 + v1.69 + v1.66` to routed pages that aggregate sibling primary slices and can otherwise hide a verified slice behind a generic all-unavailable route shell.
