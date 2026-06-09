# ArtDeco Trade Positions Hook Alignment Report

Date: 2026-05-30

Target route: `/trade/positions`

Target component: `web/frontend/src/views/trade/Center.vue`

OpenSpec change: `standardize-artdeco-route-grammar`

## 1. Scope

This batch applies the approved route-level ArtDeco grammar to the trade positions page.

It is intentionally route-local:

- No router changes.
- No API contract changes.
- No shared Vue component extraction.
- No mutation under `web/frontend/src/views/artdeco-pages/**`.
- No trade positions API client, portfolio calculation, or strategy position behavior change.

## 2. Route Grammar Hooks Added

The page already exposed legacy `data-test` hooks used by existing component and E2E tests. This batch preserves those hooks and adds standard Playwright `data-testid` route-level hooks:

| Hook | Surface |
|---|---|
| `trade-positions-page` | Route root |
| `trade-positions-header` | Header band |
| `trade-positions-refresh` | Refresh action |
| `trade-positions-status-strip` | KPI/status strip |
| `trade-positions-control-lens` | Segment control lens |
| `trade-positions-primary-surface` | Primary positions work area |

Existing `data-test` hooks remain unchanged:

- `trade-positions-page`
- `trade-positions-header`
- `trade-positions-refresh`
- `trade-positions-segments`
- `trade-positions-runtime`
- `trade-positions-table`
- `trade-positions-error`
- `trade-positions-retry`
- `trade-positions-empty`
- `trade-positions-filtered-empty`
- `trade-positions-row`

## 3. TDD Evidence

RED:

```text
npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Positions renders mocked position ledger via trade route" --project=chromium
```

Result: failed as expected because `trade-positions-page` did not exist as a `data-testid` selector.

GREEN:

```text
npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Positions renders mocked position ledger via trade route" --project=chromium
```

Result: Chromium, `1 passed`.

## 4. Verification

Completed:

- `npx eslint src/views/trade/Center.vue --quiet`: pass.
- `node scripts/check-artdeco-tokens.js --target-file src/views/trade/Center.vue`: pass.
- `npx impeccable --json src/views/trade/Center.vue`: `[]`.
- `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Positions renders mocked position ledger via trade route" --project=chromium`: Chromium, `1 passed`.
- `npm run type-check -- --pretty false`: pass, no TypeScript errors reported.
- `openspec validate standardize-artdeco-route-grammar --strict`: valid. PostHog flush warnings were emitted after validation, but the command exited successfully.
- PM2 status: `mystocks-backend` online at `http://localhost:8020`, `mystocks-frontend` online at `http://localhost:3020`.
- `git diff --check` for the scoped files: pass.

Pre-commit scope gate:

- `gitnexus detect-changes --scope staged --repo mystocks`: LOW risk, `5` files, `4` changed symbols, `0` affected processes.

Impact gate:

- `gitnexus impact --target_uid File:web/frontend/src/views/trade/Center.vue --direction upstream --repo mystocks --summary-only --include-tests`: LOW risk, `4` direct dependents, `0` affected processes.

## 5. Boundary Confirmation

This is a route-local hook alignment. It does not implement a new page design brief, alter the route tree, alter backend or frontend API contracts, or extract shared components.
