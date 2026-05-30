# ArtDeco Trade Portfolio Hook Alignment Report

Date: 2026-05-30
Route: `/trade/portfolio`
Page: `web/frontend/src/views/trade/Portfolio.vue`
OpenSpec change: `standardize-artdeco-route-grammar`

## 1. Scope

This batch applies the approved ArtDeco route-level E2E hook grammar to the canonical trade portfolio page.

Included:

- Add route-level `data-testid` hooks to the page shell, header, refresh action, status strip, primary surface, runtime state, control lens, position surface, and rebalance surface.
- Add focused Playwright assertions to the existing Phase 3 trade portfolio E2E coverage.
- Keep the route-local implementation unchanged except for stable test hooks.

Excluded:

- No route tree changes.
- No backend or frontend API contract changes.
- No shared Vue component extraction.
- No `web/frontend/src/views/artdeco-pages/**` edits.

## 2. Route Grammar Hooks Added

Route-level hooks:

- `trade-portfolio-page`
- `trade-portfolio-header`
- `trade-portfolio-refresh`
- `trade-portfolio-status-strip`
- `trade-portfolio-primary-surface`
- `trade-portfolio-runtime-state`
- `trade-portfolio-position-surface`
- `trade-portfolio-control-lens`
- `trade-portfolio-rebalance-surface`

Existing local attribution hooks were preserved:

- `attribution-mode-current`
- `attribution-mode-date`
- `attribution-date-input`

## 3. TDD Evidence

RED:

```bash
npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Portfolio renders mocked portfolio overview" --project=chromium
```

Expected failure:

- `getByTestId('trade-portfolio-page')` not found.

GREEN:

```bash
npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Portfolio renders mocked portfolio overview" --project=chromium
```

Result: Chromium, `1 passed`.

## 4. Verification

Completed:

- `npx eslint src/views/trade/Portfolio.vue tests/e2e/phase3-mainline-matrix.spec.ts --quiet`: pass.
- `node scripts/check-artdeco-tokens.js --target-file src/views/trade/Portfolio.vue`: pass.
- `npx impeccable --json src/views/trade/Portfolio.vue`: `[]`.
- `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g "Trade-Portfolio renders mocked portfolio overview" --project=chromium`: Chromium, `1 passed`.
- `npm run type-check -- --pretty false`: pass, no TypeScript errors reported.
- `openspec validate standardize-artdeco-route-grammar --strict`: valid.
- PM2 status: `mystocks-backend` online at `http://localhost:8020`, `mystocks-frontend` online at `http://localhost:3020`.
- `git diff --check` for the scoped files: pass.

Pre-commit scope gate:

- `git diff --cached --check`: pass for the staged 5-file scope.
- `gitnexus detect-changes --scope staged --repo mystocks`: LOW risk, `5` changed files, `4` changed symbols, `0` affected processes.
- GitNexus index hygiene: local `.gitnexus/meta.json` matched the current HEAD before commit. The MCP response still displayed a stale commit metadata warning inherited from its index metadata; this is recorded as a tool metadata warning rather than a route-scope expansion.

Impact gate:

- `gitnexus impact --target Portfolio.vue --file_path web/frontend/src/views/trade/Portfolio.vue --direction upstream --includeTests`: MEDIUM risk, `5` direct dependents, `0` affected processes. The direct dependents are importing views; this batch only adds static route hooks and does not alter state, API calls, props, or rendered business data.

## 5. Boundary Confirmation

This is a route-local hook alignment only. It does not implement a new design brief, alter the route tree, alter backend or frontend API contracts, or extract shared components.
