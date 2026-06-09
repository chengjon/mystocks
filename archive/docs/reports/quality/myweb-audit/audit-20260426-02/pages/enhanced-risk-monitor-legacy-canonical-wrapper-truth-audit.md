# Enhanced Risk Monitor Legacy Canonical Wrapper Truth Audit

## Scope
- Page: `web/frontend/src/views/EnhancedRiskMonitor.vue`
- Synthetic route key: `/secondary/legacy-enhanced-risk-monitor-canonical-wrapper`
- Family: `selector-scoped / canonical-owner delegation`

## Problem
- The top-level legacy enhanced risk monitor page still owned its own pseudo-live risk workbench shell even though the router-backed canonical risk-management owner already exists at `web/frontend/src/views/risk/Center.vue`.
- The legacy shell exposed local stop-loss, alert, websocket, GPU, and tabbed risk-management semantics with no independent verified contract.

## Repair
- Collapse `web/frontend/src/views/EnhancedRiskMonitor.vue` into a thin wrapper over the canonical `/risk/management` owner.
- Remove the legacy page's forked pseudo-live control cards, dialog wiring, websocket bootstrap, and tabbed shell instead of preserving or partially patching them.

## Verification
- Owner regressions:
  - `cd web/frontend && npx vitest run src/views/__tests__/EnhancedRiskMonitor.spec.ts src/views/risk/__tests__/Center.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `EnhancedRiskMonitor.vue` now delegates entirely to the canonical `/risk/management` owner.
- The page no longer fabricates local risk-monitor truth and now drops out of the high-priority secondary shortlist.
