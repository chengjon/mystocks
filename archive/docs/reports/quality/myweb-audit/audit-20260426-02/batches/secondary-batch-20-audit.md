# Batch Audit Report: secondary-batch-20

## Scope
- Module: secondary-legacy-surfaces
- Pages:
  - `(unrouted) trading/History.vue`
  - `(unrouted) trading/Positions.vue`
- Batch rationale: continue the secondary inventory repair phase by replacing two nested legacy trading placeholder pages with thin wrappers over the existing canonical `/trade/*` owners

## Agent Summary

### route-inventory
- Both nested legacy trading pages were still classified as secondary candidates because they remained standalone placeholder shells under `views/trading/*`.
- The current router graph already exposes semantically matching canonical owners for both surfaces, so static-shell degradation was unnecessary.

### data-state-audit
- `trading/History.vue` still rendered a local `Trade History` placeholder instead of delegating to the canonical `/trade/history` owner.
- `trading/Positions.vue` still rendered a local `Current Positions` placeholder instead of delegating to the canonical `/trade/positions` owner.

## Consolidated Issue Statistics
- Blocking: 0
- High: 0
- Medium: 1
- Low: 0

## Main Skill Decisions
- duplicates merged: no
- priority order applied: canonical delegation > no duplicate placeholder shell > no new secondary truth source
- primary owners selected:
  - `web/frontend/src/views/trading/History.vue`
  - `web/frontend/src/views/trading/Positions.vue`
- shared-impact review items:
  - none
- fixes applied:
  - `secondary-shell-issue-20`
- deferred items: none

## Fix Summary
- Replaced `trading/History.vue` with a thin wrapper over the canonical `/trade/history` owner.
- Replaced `trading/Positions.vue` with a thin wrapper over the canonical `/trade/positions` owner.
- Recorded the reusable precedent that a nested legacy placeholder should delegate to the current route entrypoint even when that route entrypoint is itself a thin wrapper over a deeper canonical page.

## Verification Summary
- Verification policy: code-review-plus-owner-regression
- Routed/browser proof: not applicable in this batch because both repaired owners are unrouted legacy secondary pages
- Regression checks completed:
  - `npx vitest run src/views/trading/__tests__/History.spec.ts src/views/trading/__tests__/Positions.spec.ts` -> passed `2/2`
- Secondary tooling:
  - `npm run generate:myweb-audit:secondary-inventory` -> passed; inventory remains `275` total view files, `40` routed, `235` unrouted, `H=42 / M=98 / L=95`
  - `npm run test:myweb-audit:skill` -> passed
- Runtime and repo gates:
  - `timeout 180s npm run type-check` still fails only on pre-existing frontend debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`
  - `pm2 list` should confirm `mystocks-backend` (`http://localhost:8020`) and `mystocks-frontend` (`http://localhost:3020`) remain online
  - `gitnexus_detect_changes({ scope: "staged" })` must be recorded only as a mixed observation because the staged index is already contaminated by unrelated files in this worktree
- No Playwright batch was added because these repairs target unrouted legacy pages with no canonical routed proof surface in the current router graph.
