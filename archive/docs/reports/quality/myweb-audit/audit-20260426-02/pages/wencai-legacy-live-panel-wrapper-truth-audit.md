# Wencai Legacy Live-Panel Wrapper Truth Audit

## Scope
- Page: `web/frontend/src/views/Wencai.vue`
- Synthetic route key: `/secondary/wencai-live-truth-wrapper`
- Family: `secondary wrapper / live truth component delegation`

## Problem
- `Wencai.vue` already embedded the live `WencaiPanel.vue`, but it still layered a wrapper-local pseudo overview card, fake API status, pseudo statistics tabs, and a local `loadStatistics()` fetch in front of that real panel.
- Keeping those extra shell semantics in place created a second, weaker truth source in front of the actual Wencai query/result contract.

## Repair
- Replace `web/frontend/src/views/Wencai.vue` with a thin wrapper over `WencaiPanel.vue`.
- Remove the outer pseudo overview, fake statistics tabs, and wrapper-local summary fetch instead of preserving duplicated live-truth chrome.

## Verification
- Owner regressions:
  - `cd web/frontend && npx vitest run src/views/__tests__/Wencai.spec.ts`
- Secondary governance tooling:
  - `npm run generate:myweb-audit:secondary-inventory`
  - `npm run test:myweb-audit:skill`
- Runtime gate:
  - `cd web/frontend && timeout 180s npm run type-check` still fails only on pre-existing debt in `src/api/services/dashboardService.ts:331` and `src/components/technical/composables/useKLinePatternOverlays.ts`

## Outcome
- `Wencai.vue` now renders a thin wrapper over `WencaiPanel.vue`.
- The legacy page no longer duplicates Wencai overview, API-status, or statistics truth in front of the real live panel.
