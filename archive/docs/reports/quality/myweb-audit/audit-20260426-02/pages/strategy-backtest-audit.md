# Page Audit Report: /strategy/backtest

## Purpose
Strategy backtest workbench for execution preparation, task tracking, result sync, and cross-tab handoff from repository and parameter context.

## Agent Findings

### route-inventory
- Routed wrapper: `web/frontend/src/views/strategy/Backtest.vue`
- Canonical downstream owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`

### functional-audit
- The execution rail exposed pseudo-action buttons without bound behavior before repair.

### data-state-audit
- The page mixed REAL wording with task/KPI/report surfaces synthesized only from the strategy list before repair.

### visual-artdeco-audit
- No primary visual defect was selected for this page in the current batch.

### responsive-a11y-audit
- The routed backtest shell and shared workbench child styles still carried unsupported `48rem` branches before the shared strategy cleanup wave.

## Issue Summary
- Blocking: 0
- High: 0
- Medium: 2
- Low: 0

## Consolidated Issues
- [Medium] The execution rail exposed pseudo-actions while overstating REAL runtime truth for list-derived task/KPI/report panels.
- Source roles: functional-audit, data-state-audit
- Why consolidated: both findings came from the same execution-rail action/state boundary inside the backtest workbench
- Primary owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
- Fix bucket: `fix-with-shared-impact-review`
- Reproduction or trigger:
  - open `/strategy/backtest`
  - switch to `执行中枢`
  - inspect the action row and runtime notice after strategy-list sync
- Expected: only real actions should appear executable, and list-derived summaries should be labeled as derived until real backtest task/result APIs fill them
- Actual: two action buttons had no click handlers, while task/KPI/report wording implied full REAL runtime truth even though the page only loaded `strategyApi.getStrategies({})`

- [Medium] Unsupported mobile-width responsive branches existed under the current desktop-first strategy domain baseline.
- Source roles: responsive-a11y-audit
- Why consolidated: part of the repeated strategy-domain responsive cleanup across routed strategy pages and shared workbench child styles
- Primary owner: `web/frontend/src/views/artdeco-pages/strategy-tabs/styles/ArtDecoBacktestAnalysis.scss`
- Fix bucket: `fix-with-shared-impact-review`
- Reproduction or trigger: inspect the routed backtest shell and shared workbench child style files for `@media (width <= 48rem)`
- Expected: routed strategy backtest pages should keep only desktop-relevant breakpoints for the current supported baseline
- Actual: the backtest shell plus shared tab/grid child styles still defined `48rem` branches

## Shared Impact
- Shared component or layout involved:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
  - `web/frontend/src/mock/backtestWorkbenchMock.ts`
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/components/styles/BacktestWorkbenchTabs.scss`
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/components/styles/BacktestKpiGrid.scss`
- Impact basis: the repaired truth boundary spans view-model, derived-config builder, and shared backtest child styles
- Potentially affected related pages:
  - `/strategy/repo`
  - `/strategy/parameters`
- Follow-up check needed: yes

## Repair Plan
- Fix now:
  - bind explicit handlers for non-run execution actions
  - downgrade derived task/KPI/report wording so only real backtest calls claim runtime truth
- Fix with shared-impact review:
  - remove unsupported `48rem` branches from the strategy routed family and shared backtest child styles
- Deferred: none
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-01-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
  - added `handleGenerateParameterSnapshot` and `handleInspectGpuAllocation`
  - tightened runtime notices so strategy-list-derived panels are explicitly marked as derived until real backtest results arrive
- `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
  - wired the execution-row actions to real handlers
  - added explicit helper text so only `立即执行` is presented as the real runtime action
- `web/frontend/src/mock/backtestWorkbenchMock.ts`
  - downgraded synthesized task/KPI/ops/report wording from blanket REAL semantics to strategy-list-derived semantics
- Shared responsive cleanup:
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/styles/ArtDecoBacktestAnalysis.scss`
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/components/styles/BacktestWorkbenchTabs.scss`
  - `web/frontend/src/views/artdeco-pages/strategy-tabs/components/styles/BacktestKpiGrid.scss`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse: targeted Chromium regression reused the PM2 frontend via `PLAYWRIGHT_EXTERNAL_FRONTEND=1`
- Verified at: 2026-04-26
- Checked routes:
  - `/strategy/backtest`
- Checked states:
  - default
  - loading
  - error
  - disabled
- Checked breakpoints:
  - 1920
  - 1440
  - 1280
- Validation notes:
  - `npm run test -- src/mock/__tests__/backtestWorkbenchMock.spec.ts` passed `3/3`
  - `node --test src/views/artdeco-pages/strategy-tabs/__node_tests__/backtestModulePresence.test.ts` passed `2/2`
  - `env PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://127.0.0.1:3020 npm run test:e2e -- --project=chromium tests/e2e/strategy-backtest.spec.ts` passed `6/6`

## Residual Risks
- [Low] Task/KPI/report panels are now labeled honestly, but they are still list-derived placeholders until a later batch connects them to dedicated backtest runtime endpoints.
- Reason: current routed workbench truth still starts from `strategyApi.getStrategies({})`, and this batch intentionally avoided backend/API redesign.
- Next action: if a later strategy batch expands runtime depth, attach KPI/task/report panels to dedicated backtest task/result APIs instead of strategy-list derivation.
