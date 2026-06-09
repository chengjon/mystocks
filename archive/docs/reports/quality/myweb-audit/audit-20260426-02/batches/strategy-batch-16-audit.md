# Batch Audit Report: strategy-batch-16

## Scope
- Module: strategy
- Pages:
  - /strategy/backtest
- Batch rationale: extend numeric-strip truth auditing so the canonical strategy-backtest route no longer lets its page-local KPI wrapper leak shared delta chrome or exact-decimal pseudo precision onto absolute KPI surfaces.

## Agent Summary

### route-inventory
- `/strategy/backtest` remains the canonical routed backtest workbench through `web/frontend/src/views/strategy/Backtest.vue` and its downstream owner `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`.

### data-state-audit
- One high-severity route-truth defect remained: before repair, the route-local `BacktestKpiGrid.vue` wrapper fed raw absolute KPI values into shared `ArtDecoStatCard` defaults, which surfaced faux `.artdeco-stat-change`, `+0%`, and exact-decimal count precision on the visible stats strip.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: when a routed page owns a KPI wrapper around shared stat-card primitives, the wrapper must explicitly suppress shared delta chrome and shared exact-decimal defaults for absolute or count-only cards.
- Occurrence basis:
  - `/strategy/backtest` uses `BacktestKpiGrid.vue` as the canonical owner of the visible top KPI strip
  - the shared wrapper default leaked both faux `+0%` semantics and same-strip `0.00` pseudo precision
- Shared component or token involved:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/components/BacktestKpiGrid.vue`
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
- Suggested follow-up scope: continue applying `v1.58` to routed workbenches and dashboards whose page-local KPI wrappers still inherit shared stat-card defaults on absolute-value strips.

## Main Skill Decisions
- duplicates merged: same-strip delta-chrome and pseudo-precision leaks were consolidated into one KPI-wrapper numeric-cluster issue
- priority order applied: routed numeric truth > same-strip cluster completeness
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/components/BacktestKpiGrid.vue`
- shared-impact review items:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue` was reviewed as the routed owner and did not require a separate template rewrite
  - `web/frontend/src/views/strategy/Backtest.vue` was reviewed as the wrapper route and inherited the safer strip semantics without a direct edit
- fixes applied:
  - `strategy-backtest-issue-05`
- deferred items:
  - no widening into shared `ArtDecoStatCard.vue` defaults was approved for this batch

## Fix Summary
- Forced route-local KPI cards to render with `show-change=false`.
- Normalized finite numeric KPI values to strings so count-only cards no longer leak `0.00`.
- Added owner regression coverage for shared change-chrome and pseudo-precision leaks.
- Strengthened routed Phase 3 matrix coverage so `/strategy/backtest` keeps the stats strip free of `.artdeco-stat-change`, `+0%`, and `0.00`.
- Promoted `myweb-audit` to `v1.58` for routed KPI-wrapper numeric-cluster truth.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-16-repair-approval.yaml`
- Approved issue ids:
  - `strategy-backtest-issue-05`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved strategy repair remains unimplemented in `strategy-batch-16`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - auth-seeded browser contexts plus browser-context interception with `serviceWorkers: block` were used to isolate the routed KPI-strip proof on `/strategy/backtest`
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/components/__tests__/BacktestKpiGrid.spec.ts` -> passed `1/1`
  - `npx vitest run src/views/artdeco-pages/strategy-tabs/components/__tests__/BacktestKpiGrid.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoBacktestAnalysis.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyManagement.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/ArtDecoStrategyOptimization.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategyParametersTab.spec.ts src/views/artdeco-pages/strategy-tabs/__tests__/StrategySignalsTab.spec.ts` -> passed `21/21`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `41` structurally valid tests including the strengthened `/strategy/backtest` KPI-strip assertion
  - targeted routed-page verification confirmed:
    - `/strategy/backtest?strategyId=101` now renders `0` `.artdeco-stat-change` nodes
    - the same route no longer shows `+0%`
    - the same route no longer shows `0.00`
    - the visible card values are `总回测次数=0 / 策略胜率=0% / 年化收益=0% / 最大回撤=0%`

## Artifact Checklist
- Manifest: `docs/reports/quality/myweb-audit/audit-20260426-02/manifests/strategy-batch-16-manifest.yaml`
- Raw findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-16-raw-findings.yaml`
- Merged findings: `docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-16-merged-findings.yaml`
- Approval package: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-16-repair-approval.yaml`
- Page report: `docs/reports/quality/myweb-audit/audit-20260426-02/pages/strategy-backtest-kpi-numeric-truth-audit.md`
- Closeout update: `docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`
