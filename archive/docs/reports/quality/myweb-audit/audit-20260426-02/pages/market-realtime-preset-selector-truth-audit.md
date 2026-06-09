# Page Audit: /market/realtime

## Scope
- Route: `/market/realtime`
- Canonical entry: `web/frontend/src/views/market/Realtime.vue`
- Batch: `market-batch-09`

## Defect Summary
- The canonical realtime route already exposed a local preset selector:
  - `核心蓝筹样本`
  - `金融权重样本`
  - `消费白马样本`
- But the page still kept one route-global verified quote snapshot and one route-global verified request id.
- That meant a same-instance selector change could drift visible rows away from the active preset:
  - `/market/realtime` first verified successfully under `核心蓝筹样本`
  - the same mounted route switched to `金融权重样本`
  - the first finance-preset quotes request stayed unresolved
  - the page could still render the old verified `核心蓝筹样本` rows and provenance under the new preset shell

## Repair
- Updated `Realtime.vue` so verified quote snapshots are stored by preset instead of one route-global `overview`.
- Scoped hero `TRACE_ID` to the active preset's own verified request provenance.
- A same-instance `核心蓝筹样本 -> 金融权重样本` switch with no verified finance snapshot now:
  - clears the old rows
  - clears the old request provenance
  - shows selector-local pending copy instead of stale quote rows
- Added owner regressions and a Phase 1 routed assertion for the preset-switch unresolved path.

## Verification
- Owner regressions:
  - `npx vitest run src/views/market/__tests__/Realtime.spec.ts src/views/market/__tests__/LHB.spec.ts src/views/market/__tests__/Technical.spec.ts` passed `12/12`
- Type check:
  - `timeout 180s npm run type-check` failed only on pre-existing unrelated errors in `src/components/technical/composables/useKLinePatternOverlays.ts`; no new type errors were introduced by this batch
- Routed matrix structure:
  - `npx playwright test tests/e2e/phase1-mainline-matrix.spec.ts --list` listed `44` tests including the new preset-switch assertion
- Targeted browser verification with Playwright-library + system `google-chrome`:
  - the initial controlled route rendered a verified `核心蓝筹样本` snapshot with `3` visible rows
  - after switching the same mounted route to `金融权重样本` while the finance-preset quotes request was still unresolved, the page reached `TRACE_ID: N/A / PRESET: 金融权重样本 / SAMPLE: --`
  - the quote table then showed `0` visible rows and the distribution card showed `当前暂无已验证样本快照，涨跌分布待接入。`

## Skill Feedback
- This batch reused existing `myweb-audit v1.71`.
- No new version was required because selector-scoped verified-snapshot truth was already codified by the existing guidance.
