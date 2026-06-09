# Batch Audit Report: strategy-batch-08

## Scope
- Module: strategy
- Pages:
  - /strategy/repo
- Batch rationale: reuse the existing `v1.32 + v1.37 + v1.38 + v1.39` rules on the canonical strategy-repo route so count-only repository tally cards and sibling `MATCHED / PAGE` meta stop leaking shared faux delta chrome, and unresolved first repository payloads no longer present fabricated zero counts or false real-empty semantics before any verified inventory exists.

## Agent Summary

### route-inventory
- `/strategy/repo` remains the canonical routed repository workbench at `web/frontend/src/views/strategy/List.vue`, with the routed surface owned by `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue`.

### functional-audit
- No new CRUD or lifecycle-path defect required a repair wave beyond honest summary presentation and pending-state semantics on the selected route.

### data-state-audit
- One high-severity routed summary-state cluster remained: the page could not distinguish verified count-only repository tallies, real empty-state zero counts, unavailable-state placeholders, and unresolved first-load inventory state because all of these surfaces reused the same shared stat-card or raw-count behavior.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: routed workbenches that combine count-only KPI strips, sibling count meta, and first-load or unavailable states can leak shared faux delta chrome, pseudo precision, or false real-empty copy unless the page explicitly separates verified counts, empty-state counts, and unverified placeholders.
- Occurrence basis:
  - `/strategy/repo` previously delegated verified count-only tallies into shared numeric stat-card behavior
  - the same route also reused zero-valued `MATCHED / PAGE` surfaces and a false `REAL 数据为空，请先创建策略。` message while the first `/api/v1/strategy/strategies` payload was still unresolved
- Shared component or token involved:
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue`
- Suggested follow-up scope: continue applying the existing `v1.32 + v1.37 + v1.38 + v1.39` rules to routed pages that mix count-only KPI strips, sibling count meta, and first-load or unavailable summary states.

## Main Skill Decisions
- duplicates merged: `1` raw finding into `1` routed summary-state issue
- priority order applied: routed truth > page-local containment > shared-default observation
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue`
- shared-impact review items:
  - `web/frontend/src/components/artdeco/base/ArtDecoStatCard.vue` remained an observation-only candidate; the approved repair stayed page-local
- fixes applied:
  - `strategy-repo-issue-01`
- deferred items:
  - shared `ArtDecoStatCard.vue` default behavior remains deferred to a later shared-component batch

## Fix Summary
- Added page-local summary placeholder gating to the canonical strategy-repo route.
- Converted verified count-only repository tally cards to explicit string values with `show-change=false`.
- Added sibling `MATCHED / PAGE` placeholder gating so adjacent count meta no longer reuses unresolved zero values.
- Replaced false first-load real-empty copy with explicit synchronization copy while the first repository inventory is still unresolved.
- Preserved natural empty-state zero counts when the backend returns a real empty strategy inventory.
- Added a routed component regression for verified, pending, and unavailable repository summary truth.
- Strengthened the Phase 3 matrix with exact tally-card assertions for the verified repository path, the route-level failure path, and the hanging-first-load path.
- Reused existing `myweb-audit v1.32 + v1.37 + v1.38 + v1.39` without a new skill-version bump because the defect matched the current count-kpi, numeric-cluster, unresolved-first-load, and browser-context verification rules exactly.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-08-repair-approval.yaml`
- Approved issue ids:
  - `strategy-repo-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch:
  - shared `ArtDecoStatCard.vue` default behavior remains deferred because the current blast radius is higher than this micro-batch warrants

## Unresolved Items
- No approved repair remains unimplemented in `strategy-batch-08`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts` -> passed `3/3`
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/watchlist/__tests__/Signals.spec.ts` -> passed `11/11`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `22` structurally valid tests including the strengthened `/strategy/repo` success, unavailable, and unresolved-first-load assertions
  - targeted routed-page verification confirmed:
    - the natural PM2 empty-state path now shows `0 / 0 / 0 / 全部状态`, `MATCHED: 0`, `PAGE: 1 / 1`, and `0` `.artdeco-stat-change` nodes when `/api/v1/strategy/strategies` returns `200` with an empty inventory in this environment
    - browser-context failure verification now shows `-- / -- / -- / 全部状态`, `MATCHED: --`, `PAGE: -- / --`, and the visible `REAL 请求失败，请稍后重试。` state instead of zero tallies
    - browser-context hanging-first-load verification now shows `-- / -- / -- / 全部状态`, `MATCHED: --`, `PAGE: -- / --`, `0` `.artdeco-stat-change` nodes, and the visible `策略仓库同步中，正在等待真实策略返回。` state before any verified inventory exists
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
