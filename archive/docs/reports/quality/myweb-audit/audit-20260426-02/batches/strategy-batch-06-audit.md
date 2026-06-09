# Batch Audit Report: strategy-batch-06

## Scope
- Module: strategy
- Pages:
  - /strategy/signals
- Batch rationale: reuse the existing `v1.32 + v1.38 + v1.39` rules on the canonical strategy-signals route so count-only signal tally cards stop leaking shared faux delta chrome and unresolved first-load signal tallies stop presenting resolved zero counts before any verified signal evidence exists.

## Agent Summary

### route-inventory
- `/strategy/signals` remains the canonical routed signal workbench at `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`, and the same surface is also reused by the watchlist wrapper route.

### functional-audit
- No new routed interaction-path defect required a repair wave beyond honest tally presentation on the selected route.

### data-state-audit
- One high-severity routed summary-state cluster remained: the page could not distinguish verified count-only signal tallies, real empty-state zero counts, and unresolved first-load unverified tally state because all three reused the same shared stat-card behavior.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: routed workbenches that combine count-only KPI strips with first-load or unresolved states can leak shared faux delta chrome and pseudo precision unless the page explicitly separates verified counts, empty-state counts, and unverified placeholders.
- Occurrence basis:
  - `/strategy/signals` previously delegated verified count-only tallies into shared numeric stat-card behavior
  - the same route also reused zero-valued `signals.length` tallies while the first `/api/v1/trade/signals` request was still unresolved
- Shared component or token involved:
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue`
- Suggested follow-up scope: continue applying the existing `v1.32 + v1.38 + v1.39` rules to routed pages that mix count-only KPI strips with first-load or unresolved summary states.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed summary-state issue
- priority order applied: routed truth > page-local containment > shared-default observation
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue`
- shared-impact review items:
  - `web/frontend/src/views/watchlist/Signals.vue` remained an observation-only related route that inherits the repaired surface
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue` remained an observation-only candidate; the approved repair stayed page-local
- fixes applied:
  - `strategy-signals-issue-01`
- deferred items:
  - shared `ArtDecoStatCard.vue` default behavior remains deferred to a later shared-component batch

## Fix Summary
- Added page-local tally placeholder gating to the canonical strategy-signals route.
- Converted verified count-only tally cards to explicit string values with `show-change=false`.
- Preserved natural empty-state zero counts when the backend returns a real empty signal list.
- Added a routed component regression for verified and failed-first-load strategy signal summary truth.
- Strengthened the Phase 3 matrix with exact tally-card assertions for both the verified signal path and the forced unresolved-first-load path.
- Reused existing `myweb-audit v1.32 + v1.38 + v1.39` without a new skill-version bump because the defect matched the current count-kpi, first-load placeholder, and browser-context verification rules exactly.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-06-repair-approval.yaml`
- Approved issue ids:
  - `strategy-signals-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch:
  - shared `ArtDecoStatCard.vue` default behavior remains deferred because the current blast radius is higher than this micro-batch warrants

## Unresolved Items
- No approved repair remains unimplemented in `strategy-batch-06`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts src/views/watchlist/__tests__/Signals.spec.ts` -> passed `4/4`
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts src/views/watchlist/__tests__/Signals.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts` -> passed `6/6`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `19` structurally valid tests including the strengthened `/strategy/signals` success and unresolved-first-load assertions
  - targeted routed-page verification confirmed:
    - the natural PM2 empty-state path now shows `0 / 0 / 0 / 0`, `COUNT: 0`, and `0` `.artdeco-stat-change` nodes when `/api/v1/trade/signals?limit=10` returns `200` with no signal items in this environment
    - browser-context success verification now shows `3 / 1 / 1 / 1`, `COUNT: 3`, and `0` `.artdeco-stat-change` nodes with three rendered signal items
    - browser-context hanging-first-load verification now shows `-- / -- / -- / --`, `COUNT: --`, `0` `.artdeco-stat-change` nodes, and the visible `策略信号同步中` state before any verified signal payload exists
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
- Continue applying the existing `v1.32 + v1.38 + v1.39` rules to canonical routes that mix count-only KPI strips, first-load truth, and browser-context verification fallbacks.
