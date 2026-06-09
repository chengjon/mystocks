# Page Audit Report: /strategy/gpu

## Purpose
Strategy GPU monitoring workbench for reading acceleration environment status, runtime telemetry, and performance snapshots for backtest infrastructure.

## Agent Findings

### route-inventory
- Canonical entry: `web/frontend/src/views/strategy/BacktestGPU.vue`
- Runtime behavior owner: `web/frontend/src/views/strategy/composables/useBacktestGPU.ts`

### functional-audit
- The page exposed simulated benchmark, reset, and compute-mode controls as if they were live runtime actions before repair.

### data-state-audit
- The page seeded hardcoded RTX4090-class telemetry and kept misleading values on failure before repair.

### visual-artdeco-audit
- No separate batch-dominant ArtDeco defect was selected beyond the runtime-truth boundary repair.

### responsive-a11y-audit
- The page stylesheet still carried an unsupported `48rem` branch before the shared secondary-strategy cleanup wave.

## Issue Summary
- Blocking: 0
- High: 0
- Medium: 2
- Low: 0

## Consolidated Issues
- [Medium] The GPU workbench presented simulated control actions and hardcoded telemetry as if they were live runtime capabilities.
- Source roles: functional-audit, data-state-audit
- Why consolidated: the same composable owned both false control affordances and false live telemetry defaults
- Primary owner: `web/frontend/src/views/strategy/composables/useBacktestGPU.ts`
- Fix bucket: `fix-with-shared-impact-review`
- Reproduction or trigger:
  - open `/strategy/gpu`
  - inspect the control panel and default KPI cards before the first successful API sync
  - trigger a failed GPU status/performance refresh
- Expected: routed GPU monitoring should show unknown state before sync, keep monitor-only controls honest, and surface failures without falling back to invented live telemetry
- Actual: the page exposed local-only actions and defaulted to hardcoded high-end telemetry

- [Medium] Secondary strategy routed pages should remove unsupported `48rem` responsive branches under the desktop-first baseline.
- Source roles: responsive-a11y-audit
- Why consolidated: same repeated breakpoint policy defect also existed on `/strategy/signals` and `/strategy/opt`
- Primary owner: `web/frontend/src/views/strategy/styles/BacktestGPU.scss`
- Fix bucket: `fix-with-shared-impact-review`
- Reproduction or trigger: inspect `BacktestGPU.scss` for `@media (width <= 48rem)`
- Expected: current supported strategy routes keep only desktop-relevant breakpoints
- Actual: `/strategy/gpu` still carried a `48rem` branch

## Shared Impact
- Shared component or layout involved:
  - `web/frontend/src/views/strategy/composables/useBacktestGPU.ts`
  - `web/frontend/src/views/strategy/BacktestGPU.vue`
  - `web/frontend/src/views/strategy/styles/BacktestGPU.scss`
- Impact basis: runtime truth, monitoring affordances, and fallback visuals are owned by the same routed GPU page stack
- Potentially affected related pages:
  - `/strategy/gpu`
- Follow-up check needed: yes

## Repair Plan
- Fix now:
  - replace hardcoded live telemetry defaults with explicit unknown monitor state
  - remove fake runtime controls and downgrade the panel to monitoring-only settings
  - keep failure states visible instead of implying healthy runtime capability
- Fix with shared-impact review:
  - remove the unsupported `48rem` branch from the routed GPU stylesheet
- Deferred: none
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-02-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/strategy/composables/gpuMonitorData.ts`
  - added explicit unknown-state factories for GPU status and performance summary
- `web/frontend/src/views/strategy/composables/useBacktestGPU.ts`
  - replaced hardcoded live telemetry defaults with unknown monitor state
  - removed simulated benchmark/reset/compute-mode behavior
  - kept the page monitor-only and preserved failures visibly until a real snapshot lands
- `web/frontend/src/views/strategy/BacktestGPU.vue`
  - relabeled the page as runtime monitoring
  - removed fake control affordances
  - rendered unsynced metrics as `--` or `待同步` instead of invented values
- `web/frontend/src/views/strategy/styles/BacktestGPU.scss`
  - removed the unsupported `@media (width <= 48rem)` branch
- Verification support:
  - `web/frontend/src/views/strategy/composables/__node_tests__/gpuMonitorData.test.ts`
  - `web/frontend/tests/e2e/phase3-mainline-matrix.spec.ts`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend/backend were reused
  - live verification used a Playwright-library Chromium-compatible script against system `google-chrome` with `serviceWorkers: 'block'`
- Verified at: 2026-04-26
- Checked routes:
  - `/strategy/gpu`
- Checked states:
  - default
  - error
  - disabled
- Checked breakpoints:
  - 1920
  - 1440
  - 1280
- Validation notes:
  - `node --test web/frontend/src/views/strategy/composables/__node_tests__/gpuMonitorData.test.ts` passed `4/4`
  - `timeout 180s npm run type-check` passed
  - custom Chromium-compatible browser verification against `http://127.0.0.1:3020/strategy/gpu` with forced GPU API failures passed `1/1`
  - `rg -n "@media \\(width <= 48rem\\)" web/frontend/src/views/artdeco-pages/strategy-tabs/styles/StrategySignalsTab.scss web/frontend/src/views/artdeco-pages/strategy-tabs/styles/ArtDecoStrategyOptimization.scss web/frontend/src/views/strategy/styles/BacktestGPU.scss` returned no matches

## Residual Risks
- [Low] The page now tells the truth about being monitor-only, but it still depends on `/api/gpu/status` and `/api/gpu/performance` shape stability for richer telemetry.
- Reason: this batch intentionally fixed truth boundaries and UI affordances without changing backend contracts.
- Next action: if a later GPU runtime batch adds real execution APIs, bind new controls only after those endpoints exist and are contract-verified.
