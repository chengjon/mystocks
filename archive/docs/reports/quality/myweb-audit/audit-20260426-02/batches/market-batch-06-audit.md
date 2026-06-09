# Batch Audit Report: market-batch-06

## Scope
- Module: market
- Pages:
  - /market/lhb
- Batch rationale: close the canonical `/market/lhb` leaderboard request-provenance defect so first-load failures and stale-refresh failures cannot leak failed `REQ` ids into hero metadata when the visible leaderboard snapshot was never verified or still belongs to an earlier successful sync, while reusing existing `myweb-audit v1.41` route-truth and `v1.39` verification-method rules

## Agent Summary

### route-inventory
- `/market/lhb` continues to resolve directly to canonical `web/frontend/src/views/market/LHB.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave in this batch.

### data-state-audit
- One high-severity routed request-provenance cluster remained: the page treated the latest request id as if it always represented the currently visible leaderboard snapshot, even when the latest request had failed before any verified board existed or after a successful board was already on screen.

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
- Repeated issue pattern: routed request metadata can leak failure-attempt provenance when a page-level request wrapper exposes the most recent request id rather than the request id that produced the currently visible verified snapshot.
- Occurrence basis:
  - `/market/lhb` previously rendered a failed first-load leaderboard `request_id` before any verified board snapshot existed
  - the same route previously replaced the hero `REQ` with a failed refresh request id even though the visible rows still came from the earlier successful leaderboard sync
- Shared component or token involved:
  - none for the product repair
- Suggested follow-up scope: continue applying `v1.41` request/envelope truth checks to remaining routes that expose top-level `REQ`, `REQ_ID`, or similar meta directly from `lastRequestId`, especially where stale-refresh warnings claim the page is preserving a previous successful snapshot.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed request-provenance cluster issue
- priority order applied: routed visible-snapshot truth > page-local containment
- primary owners selected:
  - `web/frontend/src/views/market/LHB.vue`
- shared-impact review items:
  - none for the product repair
- fixes applied:
  - `market-lhb-issue-03`
- deferred items: none

## Fix Summary
- Added a page-local verified-request-id state so the routed hero `REQ` now tracks the request that actually produced the visible leaderboard snapshot.
- Added a first-load/failure placeholder gate so hero `REQ / ROWS` metadata degrades to `N/A / --` before any verified leaderboard snapshot exists.
- Strengthened the routed component regression with first-load failure and stale-refresh failure cases.
- Strengthened the Phase 1 matrix with explicit `/market/lhb` failure-provenance assertions.
- Reused `myweb-audit v1.41` for route-truth handling and `v1.39` for browser-context interception fallback.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/market-batch-06-repair-approval.yaml`
- Approved issue ids:
  - `market-lhb-issue-03`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved repair remains unimplemented in `market-batch-06`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend/backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/market/__tests__/LHB.spec.ts src/views/market/__tests__/Technical.spec.ts src/views/market/__tests__/Realtime.spec.ts` -> passed `7/7`
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` -> listed `17` structurally valid tests including the new `/market/lhb` request-provenance assertions
  - `timeout 180s npm run type-check` -> passed
  - `git diff --check -- web/frontend/src/views/market/LHB.vue web/frontend/src/views/market/__tests__/LHB.spec.ts web/frontend/tests/e2e/phase1-mainline-matrix.spec.ts docs/reports/quality/myweb-audit/audit-20260426-02/findings/market-batch-06-raw-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/findings/market-batch-06-merged-findings.yaml docs/reports/quality/myweb-audit/audit-20260426-02/approvals/market-batch-06-repair-approval.yaml docs/reports/quality/myweb-audit/audit-20260426-02/manifests/market-batch-06-manifest.yaml docs/reports/quality/myweb-audit/audit-20260426-02/pages/market-lhb-request-provenance-truth-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/batches/market-batch-06-audit.md docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md` -> passed
  - targeted system-Chrome browser verification confirmed:
    - with browser-context interception and `serviceWorkers: block`, failed first-load `/market/lhb` now renders `REQ: N/A`, `ROWS: --`, and top stat values `-- / 今日 / 买入榜 / --`
    - the same first-load failure route no longer leaks the failed request id anywhere in the visible page shell
    - a controlled success-then-fail refresh path now keeps `REQ: req-market-b06-success`, preserves the visible `贵州茅台` row, and shows the stale-refresh error banner without leaking the failed retry id
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright Chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/market-batch-06-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/market-batch-06-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/market-batch-06-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/market-batch-06-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/market-batch-06-manifest.yaml` -> passed
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- Continue the market and adjacent runtime family on any remaining top-level request-metadata surfaces that still derive `REQ` directly from the latest transport attempt instead of the currently visible verified snapshot.
