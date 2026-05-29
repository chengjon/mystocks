# Implementation Report: `trade/Signals.vue` ArtDeco Signal Trust Desk

> Date: 2026-05-29
> Target route: `/trade/signals`
> Target component: `web/frontend/src/views/trade/Signals.vue`
> Scope boundary: no route changes, no API contract changes, no shared component extraction.

## 1. Implementation Summary

This implementation applies the approved `trade/Signals.vue` shape brief as a route-local craft slice.

Implemented page changes:

- added stable route-level E2E hooks for the trade signals page, header, refresh action, review lens, trust strip, runtime message, and primary signal list
- added a route-local signal trust strip for `PENDING`, `REAL`, `EMPTY`, `UNAVAILABLE`, stale refresh, and syncing states
- exposed the review lens as a route-level verification surface while keeping the existing control implementation and API behavior
- added the `观望` lens so the visible filter model matches the live signal row types
- moved route-facing labels toward Chinese operational copy for the signal review workflow
- removed `Signals.vue` local desktop-incompatible `@media` rules after approval

No changes were made to:

- `web/frontend/src/router/index.ts`
- `web/backend/app/api/**`
- `docs/api/**`
- `web/frontend/src/api/**`
- shared ArtDeco components
- `web/frontend/src/views/artdeco-pages/**`

## 2. TDD Evidence

RED was created first in `web/frontend/tests/e2e/phase3-mainline-matrix.spec.ts` by adding route-level assertions for:

- `trade-signals-page`
- `trade-signals-header`
- `trade-signals-review-lens`
- `trade-signals-trust-strip`
- trust strip state copy for verified, pending, unavailable, and stale-refresh states

Initial RED result:

```text
npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Signals" --project=chromium
4 failed
```

The failures were expected because the new route-level surfaces did not exist yet.

GREEN result after implementation:

```text
npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Signals" --project=chromium
4 passed
```

## 3. Verification Results

Commands run from `web/frontend` unless noted:

```text
npx eslint src/views/trade/Signals.vue
pass
```

```text
node scripts/check-artdeco-tokens.js --target-file src/views/trade/Signals.vue
ArtDeco Token Validation Passed.
```

```text
npm run type-check -- --pretty false
pass
```

```text
npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Signals" --project=chromium
chromium: 4 passed
```

```text
npx impeccable --json src/views/trade/Signals.vue
[]
```

Additional browser inspection:

- viewport: `1440x900`
- screenshot artifact: `/tmp/artdeco-trade-signals-1440.png`
- route: `http://localhost:3020/trade/signals`
- API route stubs: all handled; no unhandled requests
- inspected visible surfaces: route header, trust strip, review lens, primary list entry area

## 4. Resulting User-Facing Improvements

The route now makes signal trust state visible before the user acts:

- first-load pending state says the signal payload is syncing and exposes `PENDING`
- verified state says `已验证` and `信号在线`
- first-load failure says `信号异常` and exposes `UNAVAILABLE`
- refresh failure with previous data keeps the last verified rows visible and makes the route state explicit

The page also gains a stable verification surface for future design governance:

- E2E can target route-local hooks instead of brittle nested ArtDeco internals
- the page can be audited for trust strip, review lens, and primary list presence
- local `@media` drift is removed from this route without touching shared components

## 5. Residual Notes

`trade/Signals.vue` still imports existing ArtDeco workbench internals from `web/frontend/src/views/artdeco-pages/**`. This was deliberately preserved because shared extraction was out of scope for the approved craft slice.

The next design-governance step should remain documentation-first: compare the repeated route grammar across `market/Realtime.vue`, `risk/Alerts.vue`, `trade/Center.vue`, and `trade/Signals.vue` before proposing any shared component extraction.
