# Page Audit Report: /strategy/gpu

## Purpose
Canonical strategy-domain GPU monitoring route for reading acceleration environment availability, runtime telemetry, and performance snapshot surfaces backed by `web/frontend/src/views/strategy/BacktestGPU.vue`.

## Agent Findings

### route-inventory
- Canonical entry: `web/frontend/src/views/strategy/BacktestGPU.vue`
- Runtime data owners: `web/frontend/src/views/strategy/composables/gpuMonitorData.ts` and `web/frontend/src/views/strategy/composables/useBacktestGPU.ts`

### functional-audit
- No new routed interaction-path defect required a repair wave beyond restoring honest partial-runtime metric semantics on the primary GPU surface and metrics tab.

### data-state-audit
- One high-severity partial-runtime metric truth defect remained: the route accepted successful GPU availability payloads that omitted secondary sensors and benchmark fields, then upgraded those gaps into exact zero-valued live telemetry.

## Issue Summary
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Consolidated Issues
- `strategy-gpu-issue-01`
  - Repair target: `web/frontend/src/views/strategy/composables/gpuMonitorData.ts`
  - Shared impact: none
  - Outcome: fixed in `strategy-batch-04`

## Shared Impact
- Shared component or route-family owners involved:
  - `web/frontend/src/views/strategy/composables/gpuMonitorData.ts`
  - `web/frontend/src/views/strategy/composables/useBacktestGPU.ts`
  - `web/frontend/src/views/strategy/BacktestGPU.vue`
- Impact basis: the routed defect is page-local; the same GPU mapper and routed template owned both the partial payload normalization and the misleading exact-value rendering.
- Potentially affected related pages:
  - `/strategy/gpu`

## Repair Plan
- Fix now:
  - stop coercing absent benchmark and secondary sensor fields into exact zero-valued runtime metrics
  - degrade unsupported thermals, clocks, fan-speed, power, and benchmark surfaces to explicit `未校验` or `待接入` copy
  - preserve verified availability and utilization so the route still shows the partial truth it actually has
- Deferred: none
- Approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-04-repair-approval.yaml`

## Fixes Applied
- `web/frontend/src/views/strategy/composables/gpuMonitorData.ts`
  - now normalizes missing or placeholder thermals, benchmark fields, clocks, fan-speed, and power fields to nullable or pending states instead of exact zeros
- `web/frontend/src/views/strategy/composables/useBacktestGPU.ts`
  - now derives explicit `未校验` and `待接入` display states for unsupported runtime sensors and benchmark slices
- `web/frontend/src/views/strategy/BacktestGPU.vue`
  - now renders temperature, metrics-tab sensors, and performance cards with honest degraded copy instead of `0°C 正常`, `0x`, `-100%`, `0 MHz`, or `0%`
- Regression coverage:
  - `web/frontend/src/views/strategy/composables/__node_tests__/gpuMonitorData.test.ts`
  - `web/frontend/tests/e2e/phase3-mainline-matrix.spec.ts`

## Verification
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - PM2 frontend and backend were reused
  - targeted live browser verification used Playwright-library control of system `google-chrome`
  - both the actual PM2 backend route and a controlled partial-runtime browser scenario were verified because the real backend already reproduces the same partial-payload shape on `/strategy/gpu`
- Verified at: 2026-04-29
- Checked routes:
  - `/strategy/gpu`
- Checked states:
  - default
  - metrics
- Checked breakpoints:
  - 1280
- Validation notes:
  - `node --test web/frontend/src/views/strategy/composables/__node_tests__/gpuMonitorData.test.ts` passed `6/6`
  - `timeout 180s npm run type-check` passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` listed `16` structurally valid phase-3 routed tests, including the strengthened GPU partial-runtime route case
  - live routed verification confirmed the actual PM2 `/strategy/gpu` route now shows `GPU 温度 未校验`, benchmark cards of `待接入`, and metrics-tab sensor rows of `未校验`
  - the same browser verification confirmed the repaired route no longer shows `0°C`, `0x`, `-100%`, `0 MHz`, or `0%` on the primary partial-runtime surface
  - a controlled partial-runtime browser scenario reproduced the same honest degradation path with route-level API fulfillment

## Residual Risks
- [Low] `/strategy/gpu` now tells the truth about the current backend contract, but benchmark and secondary sensor slices will remain pending until `/api/gpu/*` exposes real speedup, GFLOPS, clock, fan, or thermal fields.
- [Low] The repo's default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium bundle is missing, so route verification continues to rely on system `google-chrome`.
