# Batch Audit Report: strategy-batch-05

## Scope
- Module: strategy
- Pages:
  - /strategy/parameters
- Batch rationale: reuse the existing `v1.32 + v1.38` rules on the canonical strategy-parameters route so count-only summary cards stop leaking shared faux delta chrome and failed first-load tallies stop presenting resolved zero metrics before any verified strategy summary exists.

## Agent Summary

### route-inventory
- `/strategy/parameters` remains the canonical routed parameter workbench at `web/frontend/src/views/strategy/Parameters.vue`, with the routed surface owned by `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue`.

### functional-audit
- No new routed interaction-path defect required a repair wave beyond honest summary presentation on the selected route.

### data-state-audit
- One high-severity routed summary-state cluster remained: the page could not distinguish verified count-only parameter tallies, real empty-state zero counts, and failed first-load unverified summary state because all three reused the same shared stat-card behavior.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: routed workbenches that combine count-only KPI strips with first-load or failure states can leak shared faux delta chrome and pseudo precision unless the page explicitly separates verified counts, empty-state counts, and unverified placeholders.
- Occurrence basis:
  - `/strategy/parameters` previously rendered verified summary cards as `1.00 / 2.00 / 0.00` with shared `+0%`
  - the same route also rendered failed first-load summary cards as `0.00 / 0.00 / 0.00 / 101` instead of placeholders
- Shared component or token involved:
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue`
- Suggested follow-up scope: continue applying the existing `v1.32 + v1.38` rules to routed pages that mix count-only KPI strips with first-load or failure states.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed summary-state issue
- priority order applied: routed truth > page-local containment > shared-default observation
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue`
- shared-impact review items:
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue` remained an observation-only candidate; the approved repair stayed page-local
- fixes applied:
  - `strategy-parameters-issue-01`
- deferred items:
  - shared `ArtDecoStatCard.vue` default behavior remains deferred to a later shared-component batch

## Fix Summary
- Added page-local summary placeholder gating to the canonical strategy-parameters route.
- Converted verified count-only summary cards to explicit string values with `show-change=false`.
- Preserved natural empty-state zero counts when the backend returns a real empty strategy list.
- Added a routed component regression for verified and failed-first-load strategy parameter summary truth.
- Strengthened the Phase 3 matrix with exact summary-card assertions for both the verified strategy context and the forced first-load failure path.
- Reused existing `myweb-audit v1.32 + v1.38` without a new skill-version bump because the defect matched the current count-kpi and unverified-summary rules exactly.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-05-repair-approval.yaml`
- Approved issue ids:
  - `strategy-parameters-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch:
  - shared `ArtDecoStatCard.vue` default behavior remains deferred because the current blast radius is higher than this micro-batch warrants

## Unresolved Items
- No approved repair remains unimplemented in `strategy-batch-05`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts tests/unit/strategy-parameters-data.spec.ts` -> passed `5/5`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `18` structurally valid tests including the strengthened `/strategy/parameters` success and failure assertions
  - targeted routed-page verification confirmed:
    - the natural PM2 empty-state path now shows `0 / 0 / 0 / 101`, `0` `.artdeco-stat-change` nodes, and the visible `暂无策略参数` state when the backend returns an empty strategy list
    - browser-context success verification now shows `1 / 2 / 0 / 101` with `0` `.artdeco-stat-change` nodes and the expected `Momentum Alpha` strategy card
    - browser-context failure verification now shows `-- / -- / -- / 101`, `0` `.artdeco-stat-change` nodes, and the visible `策略参数加载失败` state before any verified strategy payload exists
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
