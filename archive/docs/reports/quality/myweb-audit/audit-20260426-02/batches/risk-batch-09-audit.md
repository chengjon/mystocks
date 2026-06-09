# Batch Audit Report: risk-batch-09

## Scope
- Module: risk
- Pages:
  - /risk/overview
- Batch rationale: reuse existing `v1.43` verified-snapshot provenance rules so the canonical `/risk/overview` route no longer lets first-load failures leak request ids or faux zero-count summary truth, and no longer clears verified rules or alerts when a later refresh fails.

## Agent Summary

### route-inventory
- `/risk/overview` remains the canonical routed overview workbench at `web/frontend/src/views/risk/Overview.vue`.
- The same owner continues to feed the legacy wrapper `web/frontend/src/views/artdeco-pages/risk-tabs/RiskOverviewTab.vue`, so the current repair stays page-local and consumer-compatible.

### functional-audit
- No new interaction-path defect required a separate repair wave beyond restoring honest stale-refresh behavior on the existing `刷新概览` workflow.

### data-state-audit
- One high-severity routed truth cluster remained: the route trusted the latest `useArtDecoApi` request metadata and null-on-failure arrays instead of preserving a page-local verified overview snapshot across its multi-request rules and alerts slices.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a transport-backed multi-request route can correctly render its happy path and still misrepresent first-load failure and refresh-after-success truth if hero request provenance and sibling count surfaces are bound directly to the latest individual request attempt instead of the currently visible verified snapshot.
- Occurrence basis:
  - `/risk/overview` previously let the failed alerts request overwrite `REQ_ID` and zero-fill sibling count surfaces before any verified snapshot existed
  - the same route previously cleared verified rules and alerts on refresh failure instead of preserving last-known-good routed truth
- Shared component or token involved:
  - none for the approved product repair
- Suggested follow-up scope: continue applying `v1.43 + v1.38` to other multi-request canonical routes that expose top-level request meta plus adjacent count surfaces on the same routed shell.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed overview provenance and placeholder-truth issue
- priority order applied: preserve verified request provenance > preserve verified rows on refresh failure > suppress faux zero-count first-load truth
- primary owners selected:
  - `web/frontend/src/views/risk/Overview.vue`
- shared-impact review items:
  - `web/frontend/src/views/artdeco-pages/risk-tabs/RiskOverviewTab.vue` was reviewed as a direct consumer and did not require a separate repair
- fixes applied:
  - `risk-overview-issue-09`
- deferred items: none

## Fix Summary
- Added page-local verified request provenance to the canonical risk-overview route.
- Added first-load placeholder gating so hero `ALERTS`, content `RULES`, and top-strip counts now render `--` until a verified overview snapshot exists.
- Added stale-refresh handling so refresh-after-success failures preserve verified rules and alerts instead of clearing the routed shell to empty arrays.
- Strengthened the routed component regression and the Phase 4 matrix with explicit first-load failure and refresh-after-success assertions.
- Reused existing `myweb-audit v1.43` without a new skill-version bump because the defect exactly matched the current verified-snapshot provenance rule on a transport-backed routed page.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-09-repair-approval.yaml`
- Approved issue ids:
  - `risk-overview-issue-09`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `risk-batch-09`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/risk/__tests__/Overview.spec.ts` -> passed `6/6`
  - `npx vitest run src/views/risk/__tests__/Overview.spec.ts src/views/risk/__tests__/Alerts.spec.ts src/views/risk/__tests__/News.spec.ts src/views/risk/__tests__/StopLoss.spec.ts tests/unit/views/risk-wrapper-retention.spec.ts` -> passed `16/16`
  - `npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts --list` -> listed `18` structurally valid tests including the new `/risk/overview` first-load failure and stale-refresh assertions
  - `timeout 180s npm run type-check` -> passed
  - `git diff --check -- web/frontend/src/views/risk/Overview.vue web/frontend/src/views/risk/__tests__/Overview.spec.ts web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts` -> passed
  - targeted system-Chrome browser verification confirmed:
    - with browser-context interception on `**/api/v1/monitoring/alert-rules**` and `**/api/v1/monitoring/alerts**`, resolved first-load failure now renders `REQ_ID: N/A`, `ALERTS: --`, `RULES: --`, top-strip `-- / -- / -- / --`, and `获取预警记录失败，当前暂无已验证风险概览快照。`
    - the same first-load failure path no longer leaks the failed request id anywhere in the visible route shell
    - the success-then-refresh-fail path is now pinned by component and Phase 4 assertions, but the equivalent headless browser reproduction remained auth/reload observation-only on this machine and is therefore not overclaimed as a live success proof
    - natural PM2 headless observation for `/risk/overview` currently bounces through `/dashboard -> /login` under the same auth/reload timing artifact, so natural-route success proof is not claimed for this batch
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system `google-chrome` Playwright-library verification for the changed browser path
  - auth-restored headless browser contexts reproduced the first-load failure proof but did not stably reproduce the success-then-refresh-fail live shell before auth/reload interference resumed; this was recorded as observation-only instead of a product regression
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-09-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/risk-batch-09-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/risk-batch-09-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-09-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/risk-batch-09-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - GitNexus staged detection returned `risk_level: low`, `changed_files: 85`, `changed_count: 271`, and `affected_count: 0`, but the staged set remained mixed with earlier batch files so the result is recorded as observation-only rather than an isolated `risk-batch-09` verdict

## Next Batch Plan
- Continue the risk and adjacent route families on any remaining transport/store-backed pages that still let the latest request metadata or first-load zero counts impersonate verified routed truth.
