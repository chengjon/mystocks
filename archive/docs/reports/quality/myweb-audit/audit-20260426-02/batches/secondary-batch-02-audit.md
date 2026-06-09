# Batch Audit Report: secondary-batch-02

## Scope
- Module: secondary-embedded-shells
- Pages:
  - `(unrouted) ArtDecoTradingCenter.vue` active trading wrappers
- Batch rationale: continue the secondary inventory repair phase by replacing active placeholder migration wrappers with canonical trade history and portfolio truth, without introducing any new shell snapshot or store

## Agent Summary

### route-inventory
- `ArtDecoHistoryView.vue` and `ArtDecoPerformanceAnalysis.vue` were low-heuristic embedded wrappers, but they still sat on the live import chain behind `ArtDecoTradingCenter.vue`.
- The active-usage triage therefore promoted them ahead of higher-scoring orphan legacy pages.

### data-state-audit
- Both wrappers still rendered local `STATUS: PLACEHOLDER` migration shells even though canonical `/trade/history` and `/trade/portfolio` truth already existed.
- The correct repair was canonical delegation, not preserving local wrapper placeholder cards.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: active import chain > canonical embedded reuse > no new shell truth
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoHistoryView.vue`
  - sibling wrapper: `web/frontend/src/views/artdeco-pages/trading-tabs/ArtDecoPerformanceAnalysis.vue`
- shared-impact review items:
  - `web/frontend/src/views/trade/History.vue`
  - `web/frontend/src/views/trade/Portfolio.vue`
- fixes applied:
  - `secondary-shell-issue-02`
- deferred items: none

## Fix Summary
- Replaced the active history wrapper with a pure canonical embed of `/trade/history`.
- Replaced the active performance wrapper with a pure canonical embed of `/trade/portfolio`.
- Added explicit embedded regression coverage for canonical `History.vue`.
- Updated `myweb-audit` governance notes so active import-chain wrappers can outrank higher-score orphan pages in secondary triage.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owner is an unrouted secondary embedded shell
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/trading-tabs/__tests__/ArtDecoHistoryView.spec.ts src/views/artdeco-pages/trading-tabs/__tests__/ArtDecoPerformanceAnalysis.spec.ts src/views/trade/__tests__/History.spec.ts` -> passed `7/7`
  - `npx vitest run src/views/artdeco-pages/trading-tabs/__tests__/ArtDecoHistoryView.spec.ts src/views/artdeco-pages/trading-tabs/__tests__/ArtDecoPerformanceAnalysis.spec.ts src/views/trade/__tests__/History.spec.ts src/views/trade/__tests__/Portfolio.spec.ts src/views/trade/__tests__/Signals.spec.ts src/views/trade/__tests__/Center.spec.ts` -> passed `22/22`
- Runtime and repo gates:
  - `timeout 180s npm run type-check` still failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`
  - `pm2 list` confirmed `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `gitnexus_detect_changes({ scope: "staged" })` returned a mixed staged observation (`risk_level: low`, `changed_files: 122`, `changed_count: 0`, `affected_count: 0`), but the staged index was already contaminated by unrelated files before this batch, so it is not treated as an isolated verdict for `secondary-batch-02`
- No Playwright batch was added because there is no canonical route or independent routed proof surface for these wrapper-only panels in the current router graph.
