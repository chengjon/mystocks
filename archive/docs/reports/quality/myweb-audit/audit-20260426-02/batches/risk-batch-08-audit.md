# Batch Audit Report: risk-batch-08

## Scope
- Module: risk
- Pages:
  - /risk/stop-loss
- Batch rationale: close the canonical `/risk/stop-loss` store-envelope and request-provenance truth defect so resolved `success:false` watchlist-stock failures cannot be swallowed by shared store transforms as empty monitoring success and failed request ids cannot replace the currently visible verified stop-loss snapshot, while promoting `myweb-audit v1.42`.

## Agent Summary

### route-inventory
- `/risk/stop-loss` remains the canonical routed stop-loss entry at `web/frontend/src/views/risk/StopLoss.vue`, with the ArtDeco risk-tab path retained only as the compatibility wrapper.

### functional-audit
- No new routed interaction-path defect required a repair wave in this batch.

### data-state-audit
- One high-severity routed truth cluster remained: the route trusted shared watchlist-store transforms and latest request metadata instead of preserving resolved failure envelopes and verified-snapshot provenance at the page owner boundary.

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
- Repeated issue pattern: a routed page backed by shared Pinia-store transforms can silently lose resolved `success:false` failure truth before the route owner sees it, allowing empty arrays and latest request ids to impersonate verified visible state.
- Occurrence basis:
  - `/risk/stop-loss` previously let the shared watchlist-stock store collapse a resolved failure envelope into empty monitoring success
  - the same route previously let failed first-load or refresh request provenance replace the visible verified-snapshot request id
- Shared component or token involved:
  - none for the approved product repair
- Suggested follow-up scope: continue applying `v1.42 + v1.41 + v1.39` to remaining store-backed routes that expose top-level `REQ`, `REQ_ID`, or similar shell provenance while also consuming resolved failure envelopes through shared transforms.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed store-envelope and request-provenance truth issue
- priority order applied: preserve failure-envelope truth before transform boundary > preserve verified request provenance > keep stale-refresh cards visible
- primary owners selected:
  - `web/frontend/src/views/risk/StopLoss.vue`
- shared-impact review items:
  - none for the approved product repair
- fixes applied:
  - `risk-stop-loss-issue-08`
- deferred items: none

## Fix Summary
- Switched the routed stop-loss owner from shared watchlist-store consumption to page-local raw-contract fetching so resolved `success:false` watchlist-stock failures stay visible to the route.
- Added verified-snapshot request provenance so hero `REQ_ID` now follows the currently visible verified stop-loss snapshot.
- Added first-load placeholder gating and stale-refresh preservation so failed first loads render `N/A / --`, while refresh-after-success failures keep the verified cards visible with stale-copy messaging.
- Strengthened the routed component regression and the Phase 4 matrix with explicit resolved first-load failure and refresh-after-success failure paths.
- Promoted `myweb-audit v1.42` to encode the new rule: routed owners must preserve failure truth before any shared transform boundary that would otherwise erase resolved envelopes.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-08-repair-approval.yaml`
- Approved issue ids:
  - `risk-stop-loss-issue-08`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `risk-batch-08`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/risk/__tests__/StopLoss.spec.ts` -> passed `4/4`
  - `npx vitest run src/views/risk/__tests__/StopLoss.spec.ts src/views/risk/__tests__/Overview.spec.ts src/views/risk/__tests__/Alerts.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts` -> passed `13/13`
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `16` structurally valid tests including the new `/risk/stop-loss` failure-envelope and stale-refresh assertions
  - `timeout 180s npm run type-check` -> passed
  - `git diff --check -- web/frontend/src/views/risk/StopLoss.vue web/frontend/src/views/risk/__tests__/StopLoss.spec.ts web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts web/frontend/tests/unit/views/risk-wrapper-retention.spec.ts .claude/skills/myweb-audit/SKILL.md .claude/skills/myweb-audit/references/audit-checklist.md .claude/agents/myweb-audit-data-state-audit.md .claude/skills/myweb-audit/references/CHANGELOG.md docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-08-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-08-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-08-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-08-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/risk-stop-loss-store-envelope-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/risk-batch-08-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - targeted system-Chrome browser verification confirmed:
    - with browser-context interception on `**/api/v1/monitoring/watchlists/101/stocks`, resolved first-load failure now renders `REQ_ID: N/A`, `CRITICAL: --`, `TRIGGERED: --`, top-strip `-- / -- / -- / --`, and `watchlist stocks unavailable，当前暂无已验证止损快照。`
    - the same first-load failure path no longer leaks the failed request id anywhere in the visible route shell
    - a controlled success-then-fail refresh path now keeps `REQ_ID: req-live-stoploss-success`, preserves visible cards such as `贵州茅台` and `宁德时代`, and shows the stale-refresh copy without leaking the failed retry id
    - the natural PM2 success path still loads `/risk/stop-loss` and currently renders the honest live empty-state shell with a real request id plus `0 / 0 / 0 / --`
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-08-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-08-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-08-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-08-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-08-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- Continue the risk and adjacent route families on any remaining store-backed pages that still let shared transforms erase resolved failure truth before the routed owner can classify unavailable versus real empty-success state.
