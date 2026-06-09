# Batch Audit Report: secondary-batch-19

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) StockDetail.vue`
- Batch rationale: continue the secondary inventory repair phase by collapsing the high-priority legacy `StockDetail.vue` page into an honest static shell because no one-to-one canonical owner exists for direct delegation

## Agent Summary

### route-inventory
- `StockDetail.vue` remained in the high-priority secondary backlog because it still matched selector heuristics and still looked like a standalone live stock-detail workbench.
- The page is not mounted by the current router graph, and the closest canonical detail truth is split across `/detail/graphics/:symbol`, `/detail/news/:symbol`, and `/trade/*` routes rather than a single semantically matching owner.

### data-state-audit
- The legacy page still rendered local quote, chart, technical analysis, trading summary, and trade-operation shell surfaces with no verified contract of its own.
- Because no one-to-one active canonical owner exists, the correct repair was an honest static shell rather than a thin wrapper or a new local snapshot/store.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: honest static shell > no fake live shell truth > no false owner delegation
- primary owners selected:
  - `web/frontend/src/views/StockDetail.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-19`
- deferred items: none

## Fix Summary
- Replaced the legacy stock-detail page with an honest static shell instead of a forked pseudo-live detail-and-trading workbench shell.
- Preserved the page only as a static legacy location and routed users toward the nearest verified canonical detail and trade pages.
- Reused the same precedent family as `TechnicalAnalysis.vue` and `Analysis.vue`: when no active one-to-one canonical owner exists, degrade the legacy page to a static shell instead of inventing or preserving pseudo-live truth.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owner is an unrouted legacy secondary page
- Regression checks completed:
  - `npx vitest run src/views/__tests__/StockDetail.spec.ts` -> passed `1/1`
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed
  - `npm run test:myweb-audit:skill` -> passed
- Runtime and repo gates:
  - `timeout 180s npm run type-check` still failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`
  - `pm2 list` confirmed `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `gitnexus_detect_changes({ scope: "staged" })` is recorded only as a mixed observation because the staged index is already contaminated by unrelated files in this worktree
- No Playwright batch was added because this repair targets an unrouted legacy page with no canonical routed proof surface in the current router graph.
