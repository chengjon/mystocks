# Batch Audit Report: trade-batch-08

## Scope
- Module: trade
- Pages:
  - /trade/history
- Batch rationale: reuse the existing `v1.32 + v1.38 + v1.40` rules so the canonical trade-history route no longer collapses first-load pending or failed ledger states into faux zero-row and faux empty-history truth.

## Agent Summary

### route-inventory
- `/trade/history` remains the canonical routed trade-ledger workbench at `web/frontend/src/views/trade/History.vue`.
- The owner route is still reused by `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue`, so the current repair keeps embedded consumers aligned without widening into shared layers.

### functional-audit
- No new routed interaction-path defect required a separate repair wave beyond restoring honest first-load provenance.

### data-state-audit
- One high-severity route-truth defect remained: before repair, the history route treated unresolved and failed first loads as if they were verified empty ledgers, surfacing `ROWS: 0`, zero-valued tallies, and empty-history copy before any verified history snapshot existed.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a routed workbench can preserve stale-refresh truth correctly and still mislabel first-load pending or first-load failure as verified empty route truth if hero meta, KPI strips, and empty-copy surfaces are not all gated on the same verified-snapshot boundary.
- Occurrence basis:
  - `/trade/history` previously rendered `ROWS: 0` while the first trade-ledger payload was unresolved
  - the same route previously rendered `REQ_ID`, `TIME`, `ROWS: 0`, and zero-valued tallies when the first request resolved as `success: false` before any verified ledger snapshot existed
- Shared component or token involved:
  - `web/frontend/src/views/trade/History.vue`
  - `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue`
- Suggested follow-up scope: continue applying the existing first-load placeholder and route-provenance rules to routed workbenches that still mix hero request meta, count surfaces, and empty-state copy on unverified first loads.

## Main Skill Decisions
- duplicates merged: none
- priority order applied: first-load route provenance > count-surface placeholder honesty > empty-copy honesty
- primary owners selected:
  - `web/frontend/src/views/trade/History.vue`
- shared-impact review items:
  - `ArtDecoTradingHistory.vue` was reviewed as a route-family consumer but did not require a separate fix
- fixes applied:
  - `trade-history-issue-03`
- deferred items:
  - no new shared-layer redesign was approved for this batch

## Fix Summary
- Added page-local first-load placeholder gating for hero `REQ_ID / TIME / ROWS`, top KPI cards, and content-shell `COMPLETED / CANCELLED` summaries.
- Added a page-local pending-state gate so status text, runtime message, table `aria-busy`, and empty copy now reflect unresolved first loads instead of empty-history truth.
- Extended routed component regression to cover both unresolved and first-load failure history states.
- Strengthened the Phase 3 matrix with pending and unavailable `/trade/history` route assertions.
- Reused existing `myweb-audit` rules instead of creating a new skill-version branch.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/trade-batch-08-repair-approval.yaml`
- Approved issue ids:
  - `trade-history-issue-03`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved trade repair remains unimplemented in `trade-batch-08`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - authenticated browser contexts plus browser-context interception with `serviceWorkers: block` were used to isolate pending, first-load failure, and verified-success history states
- Regression checks completed:
  - `npx vitest run src/views/trade/__tests__/History.spec.ts src/views/trade/__tests__/Signals.spec.ts src/views/trade/__tests__/Portfolio.spec.ts tests/unit/views/trade-wrapper-retention.spec.ts` -> passed `16/16`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `28` structurally valid tests including the strengthened `/trade/history` pending and unavailable provenance assertions
  - targeted routed-page verification confirmed:
    - the browser-context unresolved-first-load route rendered `REQ_ID: N/A`, `TIME: N/A`, `ROWS: --`, `COMPLETED: --`, `CANCELLED: --`, top-strip `-- / -- / -- / --`, and `交易历史同步中...`
    - the browser-context first-load failure route rendered `REQ_ID: N/A`, `TIME: N/A`, `ROWS: --`, placeholder tallies, and `交易历史接口失败，当前显示空历史状态。`
    - the browser-context success route rendered `REQ_ID: REQ-TRADE-HISTORY-LIVE`, `TIME: 29.00MS`, `ROWS: 2`, `COMPLETED: 1`, `CANCELLED: 0`, top-strip `2 / 1 / 1 / ¥44394`, and retained ledger rows such as `600519`
    - all three browser-context paths had `0` `.artdeco-stat-change` nodes on the KPI strip
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
  - because the natural PM2 route is auth-gated in this environment, route proof for this batch used an authenticated browser context before interception was applied
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` is recorded as mixed-staged observation only for this run
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict (`risk_level: low`, `changed_files: 77`, `changed_count: 260`, `affected_count: 0`)

## Next Batch Plan
- Apply the existing first-load placeholder and provenance rules to the next canonical routed workbench that still mixes request meta, count surfaces, and empty-copy truth before any verified snapshot exists.
