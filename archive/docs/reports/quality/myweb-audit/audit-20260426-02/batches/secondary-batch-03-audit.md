# Batch Audit Report: secondary-batch-03

## Scope
- Module: secondary-embedded-shells
- Pages:
  - `(unrouted) ArtDecoTradingCenter.vue` active monitor wrappers
- Batch rationale: continue the secondary inventory repair phase by replacing live monitor wrapper placeholder shells with canonical market and risk truth, without introducing any new shell snapshot or store

## Agent Summary

### route-inventory
- `ArtDecoRealtimeMonitor.vue` and `ArtDecoRiskMonitor.vue` were still active through the `ArtDecoTradingCenter.vue` import chain.
- Their heuristic rank understated their real repair priority because both wrappers sat directly in front of canonical truth already used elsewhere in the repo.

### data-state-audit
- Both wrappers still rendered local `STATUS: PLACEHOLDER` migration shells instead of delegating to existing canonical `/market/realtime` and `/risk/management` owners.
- The correct repair was wrapper-only canonical delegation, not preserving local monitor placeholder cards.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: active import chain > canonical delegation > no new shell truth
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/market-data-tabs/ArtDecoRealtimeMonitor.vue`
  - sibling wrapper: `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskMonitor.vue`
- shared-impact review items:
  - `web/frontend/src/views/market/Realtime.vue`
  - `web/frontend/src/views/risk/Center.vue`
- fixes applied:
  - `secondary-shell-issue-03`
- deferred items: none

## Fix Summary
- Replaced the active realtime wrapper with a pure canonical embed of `/market/realtime`.
- Replaced the active risk wrapper with a pure canonical embed of `/risk/management`.
- Recorded a new secondary-phase precedent: active import-chain promotion can override low heuristic score for embedded wrappers that still block canonical truth.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owners are unrouted secondary embedded wrappers
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/market-data-tabs/__tests__/ArtDecoRealtimeMonitor.spec.ts src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskMonitor.spec.ts` -> passed `2/2`
  - `npx vitest run src/views/artdeco-pages/market-data-tabs/__tests__/ArtDecoRealtimeMonitor.spec.ts src/views/artdeco-pages/risk-tabs/__tests__/ArtDecoRiskMonitor.spec.ts src/views/market/__tests__/Realtime.spec.ts src/views/risk/__tests__/Center.spec.ts` -> passed `9/9`
- Runtime and repo gates:
  - `timeout 180s npm run type-check` still failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`
  - `pm2 list` confirmed `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `gitnexus_detect_changes({ scope: "staged" })` may only be reported as a mixed observation because the staged index is already contaminated by unrelated files in this worktree
- No Playwright batch was added because there is no canonical route or independent routed proof surface for these wrapper-only panels in the current router graph.
