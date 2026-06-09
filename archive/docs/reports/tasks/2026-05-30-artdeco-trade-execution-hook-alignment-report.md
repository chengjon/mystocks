# ArtDeco Trade Execution Hook Alignment Report

Date: 2026-05-30

Target route: `/trade/execution`

Target component: `web/frontend/src/views/trade/Execution.vue`

OpenSpec change: `standardize-artdeco-route-grammar`

## 1. Scope

This batch applies the approved route-level ArtDeco grammar to the trade execution tracking page.

It is intentionally route-local:

- No router changes.
- No API contract changes.
- No shared Vue component extraction.
- No mutation under `web/frontend/src/views/artdeco-pages/**`.
- No trade execution API client, orchestration, or reconciliation behavior change.

## 2. Route Grammar Hooks Added

The page now exposes route-level `data-testid` hooks for Playwright and ArtDeco page review:

| Hook | Surface |
|---|---|
| `trade-execution-page` | Route root |
| `trade-execution-header` | Header band |
| `trade-execution-refresh` | Refresh action |
| `trade-execution-stats-strip` | KPI/status strip |
| `trade-execution-filter-row` | Execution tracking filter row |
| `trade-execution-trigger-row` | External-trigger control row |
| `trade-execution-runtime-state` | Conditional runtime state banner |
| `trade-execution-work-area` | Primary execution chain work area |
| `trade-execution-evidence-drawer` | Existing execution evidence drawer |

Existing row-level hooks remain unchanged:

- `execution-detail-${row.trackingId}`
- `execution-reconcile-${row.trackingId}`
- `execution-symbol-input`
- `execution-quantity-input`
- `execution-price-input`
- `execution-trigger-button`

## 3. TDD Evidence

RED:

```text
npx playwright test tests/e2e/trade-execution-tracking.spec.ts -g "observes external triggers" --project=chromium
```

Result: failed as expected because `trade-execution-page` did not exist.

GREEN:

```text
npx playwright test tests/e2e/trade-execution-tracking.spec.ts -g "route-level ArtDeco hooks" --project=chromium
```

Result: Chromium, `1 passed`.

The route-level hook assertions were moved into a focused E2E test so this grammar batch does not expand into the existing execution-detail async behavior test.

## 4. Verification

Completed:

- `npx eslint src/views/trade/Execution.vue --quiet`: pass.
- `node scripts/check-artdeco-tokens.js --target-file src/views/trade/Execution.vue`: pass.
- `npx impeccable --json src/views/trade/Execution.vue`: `[]`.
- `npx playwright test tests/e2e/trade-execution-tracking.spec.ts -g "route-level ArtDeco hooks" --project=chromium`: Chromium, `1 passed`.
- `npm run type-check -- --pretty false`: pass, no TypeScript errors reported.
- `openspec validate standardize-artdeco-route-grammar --strict`: valid. PostHog flush warnings were emitted after validation, but the command exited successfully.
- PM2 status: `mystocks-backend` online at `http://localhost:8020`, `mystocks-frontend` online at `http://localhost:3020`.
- `git diff --check` for the scoped files: pass.

Pre-commit scope gate:

- `gitnexus detect-changes --scope staged --repo mystocks`: LOW risk, `5` files, `4` changed symbols, `0` affected processes.

Impact gate:

- `gitnexus impact --target web/frontend/src/views/trade/Execution.vue --direction upstream --repo mystocks --summary-only --include-tests`: LOW risk, `1` direct dependent, `0` affected processes.

## 5. Boundary Confirmation

This is a route-local hook alignment. It does not implement a new page design brief, alter the route tree, alter backend or frontend API contracts, or extract shared components.
