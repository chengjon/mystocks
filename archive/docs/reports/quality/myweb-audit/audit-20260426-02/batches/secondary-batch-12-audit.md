# Batch Audit Report: secondary-batch-12

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) RiskMonitor.vue`
- Batch rationale: continue the secondary inventory repair phase by collapsing the high-priority legacy `RiskMonitor.vue` page into a thin wrapper over the canonical `/risk/management` owner instead of preserving a forked pseudo-live risk workbench shell

## Agent Summary

### route-inventory
- `RiskMonitor.vue` remained in the high-priority secondary backlog because it still matched selector heuristics and still looked like a standalone live risk-monitoring workbench.
- The page is not mounted by the current router graph, but it still presented itself as a full live risk-monitor surface even though a canonical `/risk/management` owner already exists.

### data-state-audit
- The legacy page still rendered local summary cards, distribution placeholders, table shells, and alert surfaces with no verified contract of its own.
- Because a semantically matching canonical risk-management owner already exists, the correct repair was a thin orchestration wrapper rather than a static shell or a new local snapshot/store.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: canonical-owner delegation > honest orchestration wrapper > static legacy shell > no fake live shell truth
- primary owners selected:
  - `web/frontend/src/views/RiskMonitor.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-12`
- deferred items: none

## Fix Summary
- Replaced the legacy risk-monitor page with a thin orchestration wrapper over the canonical `/risk/management` owner instead of a forked pseudo-live shell.
- Preserved the page only as a compatibility wrapper and delegated all real risk-management truth to the canonical owner.
- Reused the same precedent family as `BacktestAnalysis.vue`: if an unrouted legacy page already has a semantically matching canonical owner, keep it as a thin wrapper over that canonical truth instead of preserving local pseudo-live workbench surfaces.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because the repaired owner is an unrouted legacy secondary page
- Regression checks completed:
  - `npx vitest run src/views/__tests__/RiskMonitor.spec.ts` -> passed `1/1`
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed
  - `npm run test:myweb-audit:skill` -> passed
- Runtime and repo gates:
  - `timeout 180s npm run type-check` still failed only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`
  - `pm2 list` confirmed `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remained online
  - `gitnexus_detect_changes({ scope: "staged" })` is recorded only as a mixed observation because the staged index is already contaminated by unrelated files in this worktree
- No Playwright batch was added because this repair targets an unrouted legacy page with no canonical routed proof surface in the current router graph.
