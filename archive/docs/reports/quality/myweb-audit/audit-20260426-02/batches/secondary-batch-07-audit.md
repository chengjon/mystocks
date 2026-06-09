# Batch Audit Report: secondary-batch-07

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) Analysis.vue`
- Batch rationale: continue the secondary inventory repair phase by degrading a high-priority legacy analysis workbench that still exposed pseudo-live analysis truth into an honest static shell because no semantically matching canonical owner exists for this page

## Agent Summary

### route-inventory
- `Analysis.vue` remained in the high-priority secondary backlog because it still matched the stats-strip + selector + shared-composable heuristic cluster.
- The page has no current router mount or live wrapper import chain, but it still presents itself as a full live analysis workbench and is therefore a suitable preserve-or-retire truth candidate.

### data-state-audit
- The page still rendered local analysis configuration, mock signals, recent signal rows, and export actions with no verified backend contract.
- The correct repair was an honest static legacy shell, not preserving pseudo-live analysis data and not force-mapping the page to an unrelated canonical route.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: preserve-or-retire truth > honest static degradation > no fake live shell truth
- primary owners selected:
  - `web/frontend/src/views/Analysis.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-07`
- deferred items: none

## Fix Summary
- Replaced the legacy analysis workbench with an honest static shell instead of pseudo-live analysis controls, signal summaries, recent signal rows, and export actions.
- Preserved the page only as a legacy reference point and redirected attention to semantically relevant canonical routes.
- Recorded a new secondary-phase precedent: if an unrouted legacy analysis page only carries fabricated workbench truth and no canonical contract, the page must degrade to a static shell instead of preserving fake analysis semantics.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owner is an unrouted legacy secondary page
- Regression checks completed:
  - `npx vitest run src/views/__tests__/Analysis.spec.ts tests/unit/config/root-demo-style-entrypoints.spec.ts` -> passed `3/3`
- Secondary tooling:
  - `npm run test:myweb-audit:skill` -> passed
  - `npm run generate:myweb-audit:secondary-inventory` -> passed
- Runtime and repo gates:
  - `timeout 180s npm run type-check` still failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`
  - `pm2 list` confirmed `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `gitnexus_detect_changes({ scope: "staged" })` is recorded only as a mixed observation because the staged index is already contaminated by unrelated files in this worktree
- No Playwright batch was added because this repair targets an unrouted legacy page with no canonical routed proof surface in the current router graph.
