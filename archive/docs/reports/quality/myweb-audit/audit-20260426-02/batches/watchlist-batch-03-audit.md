# Batch Audit Report: watchlist-batch-03

## Scope
- Module: watchlist
- Pages:
  - /watchlist/screener
- Batch rationale: reuse the existing `v1.32 + v1.37 + v1.38` rules on the canonical watchlist-screener route so count-only summary cards stop leaking shared faux precision and first-load or failed-universe states stop presenting resolved zero metrics before any verified stock-universe summary exists.

## Agent Summary

### route-inventory
- `/watchlist/screener` remains the canonical routed screener workbench at `web/frontend/src/views/watchlist/Screener.vue`, with the routed surface owned by `web/frontend/src/views/stocks/Screener.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave beyond honest summary presentation on the selected route.

### data-state-audit
- One high-severity routed summary-state cluster remained: the page could not distinguish verified count-only stock-universe tallies, natural backend error state, and unresolved first-load state because all three reused the same shared numeric presentation surfaces.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: routed workbenches that combine count-only KPI strips with first-load or backend-failure states can leak shared faux precision unless the page explicitly separates verified counts from unverified placeholders.
- Occurrence basis:
  - `/watchlist/screener` previously rendered `UNIVERSE: 0` and top summary cards `0.00 / 0.00 / 0.00 / --` under unresolved or failed first-load state
  - the same route also rendered verified count-only summary cards as `3.00 / 3.00 / 2.00 / 1.61亿`
- Shared component or token involved:
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue`
- Suggested follow-up scope: continue applying the existing `v1.32 + v1.37 + v1.38` rules to routed pages that mix count-only KPI strips with first-load or backend-failure states.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed summary-state issue
- priority order applied: routed truth > page-local containment > shared-default observation
- primary owners selected:
  - `web/frontend/src/views/stocks/Screener.vue`
- shared-impact review items:
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue` remained an observation-only candidate; the approved repair stayed page-local
- fixes applied:
  - `watchlist-screener-issue-01`
- deferred items:
  - shared `ArtDecoStatCard.vue` default behavior remains deferred to a later shared-component batch

## Fix Summary
- Added route-local placeholder gating to the watchlist screener hero universe count and top summary strip.
- Converted verified count-only summary cards to explicit string values with `show-change=false`.
- Preserved unresolved or failed first-load summary state as `--` instead of inherited zero values.
- Added a routed component regression for verified and failed-first-load screener summary truth.
- Strengthened the Phase 2 matrix with exact summary-card assertions for both the verified stock-universe path and the hanging first-load path.
- Reused existing `myweb-audit v1.32 + v1.37 + v1.38` without a new skill-version bump because the defect matched the current count-kpi, cluster-review, and unresolved-first-load rules directly.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/watchlist-batch-03-repair-approval.yaml`
- Approved issue ids:
  - `watchlist-screener-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch:
  - shared `ArtDecoStatCard.vue` default behavior remains deferred because the current blast radius is higher than this micro-batch warrants

## Unresolved Items
- No approved repair remains unimplemented in `watchlist-batch-03`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/watchlist/__tests__/Screener.spec.ts src/views/watchlist/__tests__/Signals.spec.ts src/views/watchlist/__tests__/Manage.spec.ts` -> passed `5/5`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase2-mainline-matrix.spec.ts --list` -> listed `15` structurally valid tests including the strengthened `/watchlist/screener` success and unresolved-first-load assertions
  - targeted routed-page verification confirmed:
    - the natural PM2 error path now shows `UNIVERSE: --`, top-strip `-- / -- / -- / --`, and zero `.artdeco-stat-change` nodes while `/api/v1/data/stocks/basic` returns `401`
    - browser-context success verification now shows `3 / 3 / 2 / 1.61亿` with zero `.artdeco-stat-change` nodes
    - browser-context hanging-first-load verification now shows `UNIVERSE: --`, top-strip `-- / -- / -- / --`, zero `.artdeco-stat-change` nodes, and the visible `股票池同步中` state
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` is recorded as mixed-staged observation only for this run
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online
  - GitNexus staged detection remains a mixed-staged observation rather than an isolated batch verdict

## Next Batch Plan
- Continue applying the existing `v1.32 + v1.37 + v1.38 + v1.39` rules to canonical routes that mix count-only KPI strips, first-load truth, and browser-context verification fallbacks.
