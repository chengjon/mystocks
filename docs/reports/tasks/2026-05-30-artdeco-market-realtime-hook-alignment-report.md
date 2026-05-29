# ArtDeco Market Realtime Hook Alignment Report

Date: 2026-05-30

Target route: `/market/realtime`

Target component: `web/frontend/src/views/market/Realtime.vue`

OpenSpec change: `standardize-artdeco-route-grammar`

## 1. Scope

This batch applies the approved route-level ArtDeco grammar to the market realtime page.

It is intentionally route-local:

- No router changes.
- No API contract changes.
- No shared Vue component extraction.
- No mutation under `web/frontend/src/views/artdeco-pages/**`.
- No market data orchestration or API client change.

## 2. Route Grammar Hooks Added

The page now exposes route-level `data-testid` hooks for Playwright and ArtDeco page review:

| Hook | Surface |
|---|---|
| `market-realtime-page` | Route root |
| `market-realtime-header` | Header band |
| `market-realtime-refresh` | Refresh action |
| `market-realtime-status-strip` | Runtime status strip |
| `market-realtime-control-row` | Preset/filter control row |
| `market-realtime-stats-strip` | KPI/status strip |
| `market-realtime-runtime-state` | Conditional runtime state banner |
| `market-realtime-work-area` | Primary work area |
| `market-realtime-quotes-panel` | Quotes table panel |
| `market-realtime-distribution-panel` | Distribution panel |

## 3. TDD Evidence

RED:

```text
npx playwright test tests/e2e/market-data.spec.ts -g "should display core realtime widgets" --project=chromium
```

Result: failed as expected because `market-realtime-page` did not exist.

GREEN:

```text
npx playwright test tests/e2e/market-data.spec.ts -g "should display core realtime widgets" --project=chromium
```

Result: `1 passed`.

## 4. Verification

Completed:

- `npx eslint src/views/market/Realtime.vue --quiet`: pass.
- `node scripts/check-artdeco-tokens.js --target-file src/views/market/Realtime.vue`: pass.
- `npx impeccable --json src/views/market/Realtime.vue`: `[]`.
- `npx playwright test tests/e2e/market-data.spec.ts -g "should display core realtime widgets" --project=chromium`: Chromium, `1 passed`.
- `npm run type-check -- --pretty false`: pass, no TypeScript errors reported.
- `openspec validate standardize-artdeco-route-grammar --strict`: valid. PostHog flush warnings were emitted after validation, but the command exited `0`.
- PM2 status: `mystocks-backend` online at `http://localhost:8020`, `mystocks-frontend` online at `http://localhost:3020`.
- `git diff --check` for the scoped files: pass.

Pre-commit scope gate:

- `gitnexus impact File:web/frontend/src/views/market/Realtime.vue --direction upstream --repo mystocks --summary-only --include-tests`: LOW risk, `2` direct dependents, `0` affected processes.
- Staged `gitnexus detect-changes` must be run immediately before commit after the scoped files are staged.

## 5. Boundary Confirmation

This is a route-local hook alignment. It does not implement a new page design brief, alter the route tree, alter backend or frontend API contracts, or extract shared components.
