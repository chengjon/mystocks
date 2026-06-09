# ArtDeco Risk Alerts Hook Alignment Report

> Date: 2026-05-29
> Target route: `/risk/alerts`
> Target component: `web/frontend/src/views/risk/Alerts.vue`
> OpenSpec change: `standardize-artdeco-route-grammar`
> Scope boundary: route-local hook alignment only.

## 1. Summary

This batch applies the approved ArtDeco route-level verification hook standard to `risk/Alerts.vue`.

Added stable `data-testid` hooks for:

- `risk-alerts-page`
- `risk-alerts-header`
- `risk-alerts-refresh`
- `risk-alerts-review-lens`
- `risk-alerts-status-strip`
- `risk-alerts-table`
- `risk-alerts-rules-secondary`

Existing `data-test` attributes were preserved for compatibility.

## 2. Boundary

No changes were made to:

- route definitions
- backend API handlers
- API contracts or OpenAPI files
- frontend API clients
- shared ArtDeco components
- `web/frontend/src/views/artdeco-pages/**`

## 3. TDD Evidence

RED was introduced first in `web/frontend/tests/e2e/phase4-mainline-matrix.spec.ts` by asserting route-level hooks that did not yet exist.

Initial RED command:

```text
npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts -g "Risk-Alerts" --project=chromium
```

Expected RED result:

- `risk-alerts-page` was not found
- `risk-alerts-status-strip` was not found

GREEN result after route-local hook alignment:

```text
npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts -g "Risk-Alerts" --project=chromium
4 passed
```

## 4. Verification

Commands run from `web/frontend` unless noted:

```text
npx eslint src/views/risk/Alerts.vue --quiet
pass
```

```text
node scripts/check-artdeco-tokens.js --target-file src/views/risk/Alerts.vue
ArtDeco Token Validation Passed.
```

```text
npm run type-check -- --pretty false
pass
```

```text
npx playwright test tests/e2e/phase4-mainline-matrix.spec.ts -g "Risk-Alerts" --project=chromium
chromium: 4 passed
```

```text
npx impeccable --json src/views/risk/Alerts.vue
[]
```

```text
POSTHOG_DISABLED=true openspec validate standardize-artdeco-route-grammar --strict
Change 'standardize-artdeco-route-grammar' is valid
```

## 5. Notes

This is a hook-alignment batch, not a visual redesign. It intentionally preserves the existing Risk Alerts page layout, runtime state copy, API orchestration, and table/rule-management behavior.
