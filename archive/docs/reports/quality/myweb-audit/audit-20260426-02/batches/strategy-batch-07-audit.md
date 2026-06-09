# Batch Audit Report: strategy-batch-07

## Scope
- Module: strategy
- Pages:
  - /strategy/opt
- Batch rationale: reuse the existing `v1.32 + v1.37 + v1.38 + v1.39` rules on the canonical strategy-opt route so count-only optimization tally cards stop leaking shared faux delta chrome and unresolved first-load optimization surfaces stop presenting fabricated zero counts or false missing-state semantics before any verified candidate inventory exists.

## Agent Summary

### route-inventory
- `/strategy/opt` remains the canonical routed optimization workbench at `web/frontend/src/views/strategy/Optimization.vue`, with the routed surface owned by `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`.

### functional-audit
- No new writeback-path defect required a repair wave beyond honest tally presentation and pending-state semantics on the selected route.

### data-state-audit
- One high-severity routed summary-state cluster remained: the page could not distinguish verified count-only optimization tallies, real empty-state zero counts, unavailable-state placeholders, and unresolved first-load candidate state because all of these surfaces reused the same shared stat-card or empty-array behavior.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: routed workbenches that combine count-only KPI strips, sibling count meta, and first-load or unavailable states can leak shared faux delta chrome, pseudo precision, or false empty-state copy unless the page explicitly separates verified counts, empty-state counts, and unverified placeholders.
- Occurrence basis:
  - `/strategy/opt` previously delegated verified count-only tallies into shared numeric stat-card behavior
  - the same route also reused zero-valued `VISIBLE / TOTAL` surfaces and a false missing-strategy message while the first `/api/v1/strategy/strategies` payload was still unresolved
- Shared component or token involved:
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue`
- Suggested follow-up scope: continue applying the existing `v1.32 + v1.37 + v1.38 + v1.39` rules to routed pages that mix count-only KPI strips, sibling count meta, and first-load or unavailable summary states.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed summary-state issue
- priority order applied: routed truth > page-local containment > shared-default observation
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue`
- shared-impact review items:
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue` remained an observation-only candidate; the approved repair stayed page-local
- fixes applied:
  - `strategy-opt-issue-01`
- deferred items:
  - shared `ArtDecoStatCard.vue` default behavior remains deferred to a later shared-component batch

## Fix Summary
- Added page-local tally placeholder gating to the canonical strategy-opt route.
- Converted verified count-only tally cards to explicit string values with `show-change=false`.
- Added sibling `VISIBLE / TOTAL` placeholder gating so adjacent count meta no longer reuses unresolved zero values.
- Replaced false first-load missing-strategy copy with explicit synchronization copy while the first candidate inventory is still unresolved.
- Preserved natural empty-state zero counts when the backend returns a real empty strategy inventory.
- Added a routed component regression for verified and pending optimization summary truth.
- Strengthened the Phase 3 matrix with exact tally-card assertions for the verified optimization path, the route-level failure path, and the hanging-first-load path.
- Reused existing `myweb-audit v1.32 + v1.37 + v1.38 + v1.39` without a new skill-version bump because the defect matched the current count-kpi, numeric-cluster, unresolved-first-load, and browser-context verification rules exactly.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-07-repair-approval.yaml`
- Approved issue ids:
  - `strategy-opt-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch:
  - shared `ArtDecoStatCard.vue` default behavior remains deferred because the current blast radius is higher than this micro-batch warrants

## Unresolved Items
- No approved repair remains unimplemented in `strategy-batch-07`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts` -> passed `2/2`
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/watchlist/__tests__/Signals.spec.ts` -> passed `8/8`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `20` structurally valid tests including the strengthened `/strategy/opt` success, unavailable, and unresolved-first-load assertions
  - targeted routed-page verification confirmed:
    - the natural PM2 empty-state path now shows `0 / 0 / 0 / ID 101`, `VISIBLE: 0`, `TOTAL: 0`, and `0` `.artdeco-stat-change` nodes when `/api/v1/strategy/strategies` returns `200` with an empty inventory in this environment
    - browser-context success verification now shows `2 / 1 / 0 / ID 101`, `VISIBLE: 1`, `TOTAL: 2`, and `0` `.artdeco-stat-change` nodes with one visible optimization row
    - browser-context failure verification now shows `-- / -- / -- / ID 101`, `VISIBLE: --`, `TOTAL: --`, `SOURCE: REAL-OFFLINE`, and the visible `REAL 数据不可用` state instead of zero tallies
    - browser-context hanging-first-load verification now shows `-- / -- / -- / ID 101`, `VISIBLE: --`, `TOTAL: --`, `0` `.artdeco-stat-change` nodes, and the visible `优化候选同步中，正在等待真实候选返回。` state before any verified candidate payload exists
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
- Continue applying the existing `v1.32 + v1.37 + v1.38 + v1.39` rules to canonical routes that mix count-only KPI strips, sibling count meta, and browser-context pending verification fallbacks.
