# Settings And Test Static Shells Truth Audit

## Scope
- `web/frontend/src/views/settings/General.vue`
- `web/frontend/src/views/settings/Notifications.vue`
- `web/frontend/src/views/settings/Security.vue`
- `web/frontend/src/views/settings/Theme.vue`
- `web/frontend/src/views/TestPage.vue`

## Finding
The four settings child pages rendered Element Plus placeholder alerts for future settings modules. `TestPage.vue` rendered local integration-test UI and executed a `console.log` side effect on mount/import.

None of these files are active canonical route truth. Keeping placeholder UI or local test surfaces alive would preserve secondary non-product truth beside the canonical `/system/config` and `/dashboard` owners.

## Repair
- Replaced all four settings child pages with honest static shells that hand off to `/system/config`.
- Replaced `TestPage.vue` with an honest static shell that hands off to `/dashboard`.
- Updated regression coverage to prevent Element Plus placeholder alerts, old test buttons/cards, and console side effects from returning.

## Verification
- RED: `npx vitest run tests/unit/config/settings-style-normalization.spec.ts src/views/__tests__/TestPage.spec.ts` failed before repair.
- GREEN: the same command passed `2/2`.
- Inventory: high-priority secondary shortlist remains `0`.
