# Trading Decision Header Static Shell Truth Audit

## Scope
- `web/frontend/src/views/trading-decision/DecisionHeader.vue`

## Finding
The header was the last high-priority secondary inventory asset. It retained local quick actions, panel selectors, auto-refresh dispatch state, and a missing `ArtDecoCardCompact.vue` dependency even though its sibling decision panels had already been delegated to canonical trade owners or degraded to honest static shells.

## Repair
- Replaced the header with an honest `decision-header-legacy-shell`.
- Removed local button execution state, tab scrolling state, timer dispatch, router actions, Element Plus dependencies, icon dependencies, and the missing ArtDeco component import.
- Added owner regression coverage.

## Verification
- RED: `npx vitest run src/views/trading-decision/__tests__/DecisionHeader.spec.ts` failed before repair on the stale missing import.
- GREEN: decision header and sibling trading-decision panel regressions passed after repair.
- Inventory: high-priority secondary shortlist dropped from `1` to `0`.
