# Batch Audit Report: secondary-batch-15

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) TradeManagement.vue`
- Batch rationale: continue the secondary inventory repair phase by collapsing the high-priority legacy `TradeManagement.vue` page into a thin wrapper over the active trading orchestration shell instead of preserving a forked pseudo-live trade-management workbench

## Agent Summary

### route-inventory
- `TradeManagement.vue` remained in the high-priority secondary backlog because it still matched selector heuristics and still looked like a standalone live trade-management workbench.
- The page is not mounted by the current router graph, but it still presented itself as a full live trade-management surface even though the active trading orchestration shell already exists.

### data-state-audit
- The legacy page still rendered local header, portfolio overview, positions, trade-history, and statistics shell surfaces with no verified contract of its own.
- Because a semantically matching active trading orchestration shell already exists, the correct repair was a thin orchestration wrapper rather than a static shell or a new local snapshot/store.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: active-owner delegation > honest orchestration wrapper > static legacy shell > no fake live shell truth
- primary owners selected:
  - `web/frontend/src/views/TradeManagement.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-15`
- deferred items: none

## Fix Summary
- Replaced the legacy trade-management page with a thin orchestration wrapper over the active trading orchestration shell instead of a forked pseudo-live workbench shell.
- Preserved the page only as a compatibility wrapper and delegated all real trading-workbench truth to the active shell.
- Reused the same precedent family as `Dashboard.vue`, `Market.vue`, `IndicatorLibrary.vue`, and `StrategyManagement.vue`: if an unrouted legacy page already has a semantically matching owner, keep it as a thin wrapper over that truth instead of preserving local pseudo-live shell surfaces.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owner is an unrouted legacy secondary page
- Regression checks completed:
  - `npx vitest run src/views/__tests__/TradeManagement.spec.ts src/views/artdeco-pages/__tests__/ArtDecoTradingManagement.spec.ts` -> passed `2/2`
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed
  - `npm run test:myweb-audit:skill` -> passed
- Runtime and repo gates:
  - `timeout 180s npm run type-check` still failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`
  - `pm2 list` confirmed `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `gitnexus_detect_changes({ scope: "staged" })` is recorded only as a mixed observation because the staged index is already contaminated by unrelated files in this worktree
- No Playwright batch was added because this repair targets an unrouted legacy page with no canonical routed proof surface in the current router graph.
