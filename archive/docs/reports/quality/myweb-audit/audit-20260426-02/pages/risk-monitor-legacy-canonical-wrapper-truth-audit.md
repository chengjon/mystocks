# Risk Monitor Legacy Canonical Wrapper Truth Audit

## Scope
- Page: `web/frontend/src/views/RiskMonitor.vue`
- Synthetic route key: `/secondary/legacy-risk-monitor-canonical-wrapper`
- Family: `selector-scoped / canonical-owner delegation`

## Problem
- The top-level legacy risk monitor page still owned its own pseudo-live risk workbench shell even though the router-backed canonical risk-management owner already exists at `web/frontend/src/views/risk/Center.vue`.
- The legacy shell exposed local summary cards, chart placeholders, position-risk table semantics, and risk alerts with no independent verified contract.

## Repair
- Collapse `web/frontend/src/views/RiskMonitor.vue` into a thin wrapper over the canonical `/risk/management` owner.
- Remove the legacy page's forked pseudo-live risk workbench shell instead of preserving or partially patching it.

## Verification
- Owner regression:
  - `cd web/frontend && npx vitest run src/views/__tests__/RiskMonitor.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `RiskMonitor.vue` now delegates entirely to the canonical `/risk/management` owner.
- The page no longer fabricates local risk-monitor truth and now drops out of the high-priority secondary shortlist.
