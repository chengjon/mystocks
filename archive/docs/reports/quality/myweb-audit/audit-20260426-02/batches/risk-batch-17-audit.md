# Batch Audit Report: risk-batch-17

## Scope
- Module: risk
- Pages:
  - /risk/alerts
- Batch rationale: close the canonical `/risk/alerts` partial-slice truth gap so a first-load alert-records failure cannot hide a verified rules slice or collapse the whole route back to generic no-snapshot copy

## Agent Summary

### route-inventory
- `/risk/alerts` remains the canonical routed alerts workbench at `web/frontend/src/views/risk/Alerts.vue`.
- The same owner continues to feed the legacy wrapper `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue`, so the repair stays page-local and consumer-compatible.

### functional-audit
- No new routed click-flow defect required a separate repair wave beyond honest partial-slice truth for the canonical route.

### data-state-audit
- One high-severity routed partial-slice truth defect remained: the route treated rules and alerts as one global verified shell, so a first-load alerts failure hid a verified rules slice and rewrote the shell to `当前暂无已验证告警快照。`

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a routed page can already have one verified primary slice and still lie about route truth if a sibling primary slice fails before the first full page-level snapshot exists.
- Occurrence basis:
  - `/risk/alerts` allowed `alert-rules` to verify independently
  - the route still used one route-global verified flag and one route-global request id, so the rules slice could not surface its own verified truth when `alerts` failed
- Shared component or token involved:
  - none for the approved repair
- Suggested follow-up scope: continue applying `v1.71 + v1.69 + v1.66` checks to routed pages that aggregate multiple primary slices and might still collapse a verified sibling slice into a generic all-unavailable shell.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed partial-slice truth issue
- priority order applied: visible-slice truth > page-local containment > routed verification hardening
- primary owners selected:
  - `web/frontend/src/views/risk/Alerts.vue`
- shared-impact review items:
  - `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue` was reviewed as a direct consumer and did not require a separate repair
- fixes applied:
  - `risk-alerts-issue-17`
- deferred items: none

## Fix Summary
- Added separate verified snapshot tracking for rules and alert records inside the canonical risk alerts owner.
- Updated hero `REQ_ID`, summary counts, `RULES / ALERTS` meta, runtime copy, and table empty states so a verified rules slice remains visible while alert records stay unresolved.
- Added an owner-level regression for the `rules success + alerts fail on first load` path.
- Added a Phase 4 routed matrix assertion for the same partial-slice truth scenario.
- Reused existing `myweb-audit v1.71`; no new skill-version bump was required.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-17-repair-approval.yaml`
- Approved issue ids:
  - `risk-alerts-issue-17`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `risk-batch-17`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/risk/__tests__/Alerts.spec.ts src/views/risk/__tests__/Overview.spec.ts src/views/risk/__tests__/StopLoss.spec.ts src/views/risk/__tests__/News.spec.ts src/views/risk/__tests__/Center.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts tests/unit/views/risk-center-template-retention.spec.ts` -> passed `29/29`
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `37` structurally valid tests including the new `/risk/alerts` partial-slice assertion
  - targeted system-Chrome browser verification confirmed:
    - the alerts shell stays `REQ_ID: N/A / UNREAD: --`
    - the content meta stays partial as `RULES: 2 / ALERTS: --`
    - the top stats stay partial as `2 / 2 / -- / --`
    - the verified rules table still renders `组合波动率约束`
    - the same controlled proof confirms `获取告警记录失败，当前告警记录暂不可用。` and no longer shows `当前暂无已验证告警快照。`
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system `google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-17-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-17-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-17-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-17-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-17-manifest.yaml` -> passed
  - `git diff --check -- web/frontend/src/views/risk/Alerts.vue web/frontend/src/views/risk/__tests__/Alerts.spec.ts web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-17-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-17-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-17-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-17-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/risk-alerts-partial-slice-selector-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/risk-batch-17-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - `timeout 180s npm run type-check` still fails only on pre-existing unrelated errors in `src/api/services/dashboardService.ts` and `src/components/technical/composables/useKLinePatternOverlays.ts`
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- Continue applying `v1.71 + v1.69 + v1.66` to routed pages that aggregate sibling primary slices and can otherwise hide a verified slice behind a generic all-unavailable route shell.
