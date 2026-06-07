# B4.008-M2a Shared Shell Layout Header Summary Repair

Date: 2026-06-08

Branch: `wip/root-dirty-20260403`

Implementation commit: `15316c9a8d2f1424411c89cd49ed35473832964c`

FUNCTION_TREE node: `.governance/programs/artdeco-web-design-governance/cards/b4-frontend-shared-ui-component-truth.yaml`

Status: `implementation-landed`

## Authorization

User granted source-authorized approval for:

`B4.008-M2a UI-1 shared shell/layout/header summary`

Authorized source paths:

- `web/frontend/src/layouts/ArtDecoLayoutEnhanced.vue`
- `web/frontend/src/layouts/BaseLayout.vue`
- `web/frontend/src/composables/useHeaderSummary.ts`

Held out of scope:

- `web/frontend/src/components.d.ts`
- `web/frontend/src/layouts/archive/BaseLayout.vue`
- B4.007 route truth and root legacy archives.
- ST-HOLD.
- `marketKlineData`.
- External dirty files and unrelated frontend/backend domains.

## Change Summary

`useHeaderSummary.ts`

- Added explicit singleton `canRefresh` state.
- `setRefreshFn()` now marks refresh availability true.
- `reset()` clears refresh availability and refresh callback together.
- Returned `canRefresh` to consumers so layout state no longer infers refresh availability from market status text.

`ArtDecoLayoutEnhanced.vue`

- Changed the header refresh/time action visibility guard from `marketStatus` to `canRefresh`.
- This keeps the refresh affordance tied to the registered dashboard refresh capability instead of an incidental market-summary string.

`BaseLayout.vue`

- Normalized the sidebar persistence TODO into an owned, time-boxed technical-debt marker.

## Risk Controls

- `components.d.ts` remained clean and was not staged.
- `web/frontend/src/layouts/archive/BaseLayout.vue` remained out of scope and was not staged.
- No route, menu, API, archive, ST-HOLD, or `marketKlineData` files were changed.
- Vue SFC component names are not directly impactable symbols in the current GitNexus index; M2a therefore uses exact staged-file GitNexus checks as the hard scope gate.
- GitNexus impact for `useHeaderSummary` was LOW: 1 direct dependent, 0 affected indexed processes.

## Gate Evidence

Pre-commit gates:

- `npm run type-check`: passed.
- Focused unit:
  - Command: `npm run test -- tests/unit/useHeaderSummary.spec.ts tests/unit/layout/ArtDecoLayoutEnhanced.accessibility.spec.ts tests/unit/components/ArtDecoDashboardLogic.spec.ts`
  - Result: 3 files passed, 28 tests passed.
- Stable unit:
  - Command: `npm run test:unit:stable`
  - Result: 33 files passed, 415 tests passed.
- PM2 services:
  - `mystocks-backend`: online at `http://localhost:8020`.
  - `mystocks-frontend`: online at `http://localhost:3020`.
- PM2 business smoke:
  - Command: `PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://localhost:3020 npm run test:e2e:business-smoke`
  - First run: 38 passed, 1 transient `market-data` waitForURL timeout, 16 not run.
  - Failing case single rerun: passed, 1/1.
  - Full rerun: passed, chromium 55/55.
- OPENDOG:
  - Recorded type-check passed.
  - Recorded focused unit passed.
  - Recorded business smoke passed, 55 passed.
  - Verification fresh, failing runs 0.

Required commit gates:

- Stage only the three authorized source files plus this B4.008 governance evidence.
- Run `git diff --cached --check`.
- Parse `nodes.json`.
- Run GitNexus staged detect.
- Run `node .gitnexus/run.cjs verify-staged --repo mystocks`.
- Post-commit run `node .gitnexus/run.cjs analyze --force`.

## Next Gate

Recommended next package:

`B4.008-M2b UI-3 shared market chart/query component chain`

Do not start M2b until source authorization is explicit.
