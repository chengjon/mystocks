# Batch Audit Report: secondary-batch-21

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) trading/Orders.vue`
  - `(unrouted) trading/Execution.vue`
- Batch rationale: continue the secondary inventory repair phase by collapsing two nested legacy trading placeholder pages into honest static shells because no semantically matching canonical trade orders or trade execution owners exist

## Agent Summary

### route-inventory
- Both nested legacy trading pages remained in the secondary backlog because they still rendered standalone placeholder shells under `views/trading/*`.
- The current router graph exposes neighboring `/trade/*` routes, but no semantically matching `/trade/orders` or `/trade/execution` owner for direct delegation.

### data-state-audit
- `trading/Orders.vue` still rendered a local `Order Management` placeholder shell and implied an eventual order-management workbench with no verified contract behind it.
- `trading/Execution.vue` still rendered a local `Trade Execution` placeholder shell and implied an eventual execution-routing workbench with no verified contract behind it.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: honest static shell > no fake local execution truth > no false canonical delegation
- primary owners selected:
  - `web/frontend/src/views/trading/Orders.vue`
  - `web/frontend/src/views/trading/Execution.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-21`
- deferred items: none

## Fix Summary
- Replaced `trading/Orders.vue` with an honest static shell instead of a local order-management placeholder surface.
- Replaced `trading/Execution.vue` with an honest static shell instead of a local trade-execution placeholder surface.
- Preserved the pages only as static legacy locations that hand users off to the nearest verified canonical `/trade/*` routes.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because both repaired owners are unrouted legacy secondary pages
- Regression checks completed:
  - `npx vitest run src/views/trading/__tests__/Orders.spec.ts src/views/trading/__tests__/Execution.spec.ts` -> passed `2/2`
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed; inventory remains `275` total view files, `40` routed, `235` unrouted, `H=42 / M=98 / L=95`
  - `npm run test:myweb-audit:skill` -> passed
- Runtime and repo gates:
  - `timeout 180s npm run type-check` still fails only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`
  - `pm2 list` should confirm `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remain online
  - `gitnexus_detect_changes({ scope: "staged" })` must be recorded only as a mixed observation because the staged index is already contaminated by unrelated files in this worktree
- No Playwright batch was added because these repairs target unrouted legacy pages with no canonical routed proof surface in the current router graph.
