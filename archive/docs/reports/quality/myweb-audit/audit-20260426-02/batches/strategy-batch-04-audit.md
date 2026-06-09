# Batch Audit Report: strategy-batch-04

## Scope
- Module: strategy
- Pages:
  - /strategy/gpu
- Batch rationale: close the routed partial-runtime metric truth gap on the GPU monitoring workbench and fold that newly observed success-path placeholder pattern back into myweb-audit.

## Agent Summary

### route-inventory
- `/strategy/gpu` remains the canonical GPU monitoring route at `web/frontend/src/views/strategy/BacktestGPU.vue`.
- The route's runtime truth is shared between the page-local template and the local GPU data mapper/composable pair.

### functional-audit
- No new routed interaction-path defect required a repair wave beyond restoring honest partial-runtime metric semantics on the primary GPU surface and metrics tab.

### data-state-audit
- One high-severity partial-runtime metric truth defect remained: the page accepted successful GPU availability responses that omitted secondary sensors and benchmark fields, then upgraded those gaps into exact zero-valued runtime metrics.

## Consolidated Issue Statistics
- Blocking: 0
- High: 1
- Medium: 0
- Low: 0

## Pattern Findings
- Repeated issue pattern: a routed runtime page can still become misleading even when every request succeeds if the backend contract proves only partial runtime truth and the frontend upgrades missing fields into exact zero-valued metrics.
- Occurrence basis:
  - `/strategy/gpu` previously rendered `0°C 正常`, `0x`, `-100%`, `0 MHz`, `0%`, and `0 W` even though the actual PM2 backend only proved availability and utilization while omitting benchmark and secondary sensor fields
- Shared component or token involved:
  - `web/frontend/src/views/strategy/composables/gpuMonitorData.ts`
  - `web/frontend/src/views/strategy/composables/useBacktestGPU.ts`
  - `web/frontend/src/views/strategy/BacktestGPU.vue`
- Suggested follow-up scope:
  - continue auditing routed runtime, telemetry, or hardware-monitor pages for successful partial payloads that still masquerade as fully verified exact-value runtime truth
  - treat missing sensor and benchmark fields as a first-class audit dimension, not only failed-request fallbacks

## Main Skill Decisions
- duplicates merged: none
- priority order applied: partial-runtime metric truth > page-local GPU polish
- primary owners selected:
  - `web/frontend/src/views/strategy/composables/gpuMonitorData.ts`
- shared-impact review items: none
- fixes applied:
  - `strategy-gpu-issue-01`
- deferred items: none

## Fix Summary
- Changed the GPU mapper so missing thermals, benchmark fields, clocks, fan-speed, and power fields normalize to explicit nullable or pending states instead of zero-valued runtime truth.
- Degraded the temperature card, metrics-tab sensor rows, and benchmark cards to `未校验` or `待接入` when the current routed source only proves partial runtime availability.
- Preserved verified availability and utilization so the route still presents the live truth it actually has.
- Extended both mapper regression coverage and the routed phase-3 E2E matrix file for the partial-runtime GPU path.
- Extended `myweb-audit` to `v1.31` so future route audits check successful partial runtime payloads as rigorously as failure-path placeholders.

## Approval Accounting
- Repair approval status: approved
- Approval package artifact: `docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-04-repair-approval.yaml`
- Approved issue ids:
  - `strategy-gpu-issue-01`
- Deferred issue ids: none
- Shared-impact items approved for current batch: none
- Shared-impact items deferred to later batch: none

## Unresolved Items
- No approved strategy repair remains unimplemented in `strategy-batch-04`.

## Reasons Not Fixed
- No approved finding was left unfixed in this batch.

## Verification Summary
- Verification policy: code-review-plus-targeted-live-verification
- Browser project or runtime reuse:
  - existing PM2 frontend and backend remained online
  - targeted browser verification reused the PM2 frontend via Playwright-library control of system `google-chrome`
  - both the actual PM2 backend route and a controlled partial-runtime browser scenario were verified because the real backend already reproduces the same partial-payload shape on `/strategy/gpu`
- Regression checks completed:
  - `node --test web/frontend/src/views/strategy/composables/__node_tests__/gpuMonitorData.test.ts` -> passed `6/6`
  - `timeout 180s npm run type-check` -> passed
  - `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts --list` -> listed `16` structurally valid routed tests including the strengthened GPU partial-runtime route assertion
  - `git diff --check -- web/frontend/src/views/strategy/composables/gpuMonitorData.ts web/frontend/src/views/strategy/composables/useBacktestGPU.ts web/frontend/src/views/strategy/BacktestGPU.vue web/frontend/src/views/strategy/composables/__node_tests__/gpuMonitorData.test.ts web/frontend/tests/e2e/phase3-mainline-matrix.spec.ts` -> passed
  - targeted routed-page verification confirmed:
    - actual PM2 `/strategy/gpu` now shows `GPU 温度 未校验`
    - the benchmark card now renders `待接入` plus `基准性能待接入`
    - the metrics tab now renders `GPU 核心频率 未校验`, `显存频率 未校验`, `风扇转速 未校验`, and `电源使用 未校验`
    - the old exact-value strings `0°C`, `0x`, `-100%`, `0 MHz`, and `0%` are absent after repair
    - the same honest degradation path reproduces under a controlled partial-runtime browser scenario with route-level API fulfillment
- `pm2 list` confirmed `mystocks-backend` and `mystocks-frontend` online
- Environment fallback recorded:
  - the default `npx playwright test` Chromium runner still cannot execute browser tests on this machine because the local Playwright chromium executable is missing, so the batch relied on system-`google-chrome` Playwright-library verification for the changed browser path
- Artifact validation commands completed:
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema findings --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-04-raw-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema merged --file docs/reports/quality/myweb-audit/audit-20260426-02/findings/strategy-batch-04-merged-findings.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema approval --file docs/reports/quality/myweb-audit/audit-20260426-02/approvals/strategy-batch-04-repair-approval.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --schema manifest --file docs/reports/quality/myweb-audit/audit-20260426-02/manifests/strategy-batch-04-manifest.yaml` -> passed
  - `node scripts/dev/tools/validate-myweb-audit-artifacts.mjs --from-manifest docs/reports/quality/myweb-audit/audit-20260426-02/manifests/strategy-batch-04-manifest.yaml` -> passed
- GitNexus staged-scope note:
  - `gitnexus_detect_changes({ scope: "staged", repo: "mystocks_spec" })` returned `risk_level: low`, `changed_files: 77`, `changed_count: 256`, and `affected_count: 0`, but the staged set remained mixed with earlier batch files so the result is recorded as observation-only rather than isolated `strategy-batch-04` scope
- Risk notes:
  - frontend URL target: `http://localhost:3020`
  - backend URL target: `http://localhost:8020`
  - PM2 reports both required services online

## Next Batch Plan
- If the user continues the strategy or adjacent runtime audit wave, prioritize other routed runtime or monitoring pages that may be receiving successful partial payloads and still rendering unsupported sensor or benchmark fields as exact zero-valued truth.
