# Batch Audit Report: secondary-batch-06

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) Dashboard.vue`
- Batch rationale: continue the secondary inventory repair phase by collapsing the high-priority legacy dashboard page into a thin orchestration wrapper over the canonical ArtDeco dashboard owner instead of preserving a forked pseudo-live shell

## Agent Summary

### route-inventory
- `Dashboard.vue` remained in the high-priority secondary backlog because it still matched the hero/meta/stats-strip + selector heuristic cluster.
- The page has no current router mount or live wrapper import chain, but it still presents itself as a full live dashboard and therefore is a suitable preserve-or-orchestrate truth candidate.

### data-state-audit
- The page still rendered hardcoded dashboard summary cards, heat-flow panels, and sector tables with no verified router-backed contract of its own.
- Because a semantically matching canonical dashboard owner already exists, the correct repair was a thin orchestration wrapper rather than an unrelated static shell or a new local snapshot/store.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: canonical-owner delegation > honest orchestration wrapper > static legacy shell > no fake live shell truth
- primary owners selected:
  - `web/frontend/src/views/Dashboard.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-06`
- deferred items: none

## Fix Summary
- Replaced the legacy dashboard with a thin orchestration wrapper over the canonical ArtDeco dashboard owner instead of hardcoded pseudo-live summary cards, heat panels, and sector tables.
- Preserved the page only as a legacy compatibility wrapper and delegated all real dashboard truth to the canonical owner.
- Recorded a new secondary-phase precedent: if an unrouted legacy page already has a semantically matching canonical owner, keep it as a thin wrapper over that canonical truth instead of preserving a pseudo-live fork.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owner is an unrouted legacy secondary page
- Regression checks completed:
  - `npx vitest run src/views/__tests__/Dashboard.spec.ts` -> passed `1/1`
- Secondary tooling:
  - `npm run test:myweb-audit:skill` -> passed
  - `npm run generate:myweb-audit:secondary-inventory` -> passed
- Runtime and repo gates:
  - `timeout 180s npm run type-check` still failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`
  - `pm2 list` confirmed `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `gitnexus_detect_changes({ scope: "staged" })` is recorded only as a mixed observation because the staged index is already contaminated by unrelated files in this worktree
- No Playwright batch was added because this repair targets an unrouted legacy page with no canonical routed proof surface in the current router graph.
