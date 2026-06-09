# Settings Legacy Canonical Wrapper Truth Audit

## Scope
- Page: `web/frontend/src/views/Settings.vue`
- Synthetic route key: `/secondary/legacy-settings-canonical-wrapper`
- Family: `selector-scoped / canonical-owner delegation`

## Problem
- The top-level legacy settings page still owned its own pseudo-live shell even though the router-backed canonical system-config owner already exists at `web/frontend/src/views/system/Settings.vue`.
- The legacy shell exposed local display-setting controls, faux database-status rows, and faux log-summary cards with no independent verified contract.

## Repair
- Collapse `web/frontend/src/views/Settings.vue` into a thin wrapper over the canonical `/system/config` owner.
- Remove the legacy page's forked pseudo-live settings shell instead of preserving or partially patching it.

## Verification
- Owner regression:
  - `cd web/frontend && npx vitest run src/views/__tests__/Settings.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts:56`

## Outcome
- `Settings.vue` now delegates entirely to the canonical `/system/config` owner.
- The page no longer fabricates local settings truth and now drops out of the high-priority secondary shortlist.
