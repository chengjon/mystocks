# Batch Audit Report: secondary-batch-01

## Scope
- Module: secondary-embedded-shells
- Pages:
  - `(unrouted) ArtDecoTradingManagement.vue`
- Batch rationale: start the secondary inventory repair phase with a narrow embedded-shell owner that still leaked fake live truth, then demote it to pure canonical orchestration without introducing any new shell snapshot/store

## Agent Summary

### route-inventory
- `ArtDecoTradingManagement.vue` sits in the secondary inventory as an embedded shell candidate, not a canonical routed page.
- The owner still rendered shell-level runtime chrome even though the live canonical trading shell had already moved to canonical `/trade/*` routes and wrappers.

### data-state-audit
- The shell leaked fake `REQ_ID`, `SYNC`, market status, P&L, and hardcoded signal count surfaces without any verified snapshot contract.
- Supported tabs could reuse canonical `/trade/*` owners directly; unsupported `绩效归因` needed a static explanatory shell instead of fake local data.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: shell demotion > canonical embedded reuse > static fallback for unsupported tabs
- primary owners selected:
  - `web/frontend/src/views/artdeco-pages/ArtDecoTradingManagement.vue`
  - direct canonical dependency: `web/frontend/src/views/trade/Portfolio.vue`
- shared-impact review items:
  - `Portfolio.vue` embedded entrypoint
- fixes applied:
  - `secondary-shell-issue-01`
- deferred items: none

## Fix Summary
- Replaced the old shell-level fake runtime hero and stats-strip in `ArtDecoTradingManagement.vue` with static orchestration copy only.
- Rewired the owner to embed canonical `/trade/portfolio`, `/trade/signals`, `/trade/positions`, and `/trade/history` pages directly.
- Downgraded unsupported `绩效归因` to a static explanatory shell instead of maintaining fake local live data.
- Added an embedded mode to canonical `Portfolio.vue` so the outer shell can reuse verified truth without duplicating route-level hero/stats chrome.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owner is an unrouted secondary embedded shell
- Regression checks completed:
  - `npx vitest run src/views/artdeco-pages/__tests__/ArtDecoTradingManagement.spec.ts src/views/trade/__tests__/Portfolio.spec.ts` -> passed `7/7`
  - `npx vitest run src/views/artdeco-pages/__tests__/ArtDecoTradingManagement.spec.ts src/views/trade/__tests__/Portfolio.spec.ts src/views/trade/__tests__/Signals.spec.ts src/views/trade/__tests__/Center.spec.ts src/views/trade/__tests__/History.spec.ts` -> passed `20/20`
- Runtime and repo gates:
  - `timeout 180s npm run type-check` still failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`
  - `pm2 list` confirmed `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
- No Playwright batch was added because there is no canonical route or live wrapper import chain for this owner in the current router graph.
