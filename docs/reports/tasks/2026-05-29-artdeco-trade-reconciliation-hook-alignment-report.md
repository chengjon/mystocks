# ArtDeco Trade Reconciliation Hook Alignment Report

Date: 2026-05-29

Target route: `/trade/reconciliation`

Target component: `web/frontend/src/views/trade/Reconciliation.vue`

OpenSpec change: `standardize-artdeco-route-grammar`

## 1. Scope

This batch applies the approved route-level ArtDeco grammar to the trade reconciliation page.

It is intentionally route-local:

- No router changes.
- No API contract changes.
- No shared Vue component extraction.
- No mutation under `web/frontend/src/views/artdeco-pages/**`.
- No data orchestration or reconciliation semantics change.

## 2. Route Grammar Hooks Added

The page now exposes route-level `data-testid` hooks for Playwright and ArtDeco page review:

| Hook | Surface |
|---|---|
| `trade-reconciliation-page` | Route root |
| `trade-reconciliation-header` | Header band |
| `trade-reconciliation-refresh` | Refresh action |
| `trade-reconciliation-control-row` | Account/source/import controls |
| `trade-reconciliation-status-strip` | Runtime metric/status strip |
| `trade-reconciliation-runtime-state` | Conditional runtime message |
| `trade-reconciliation-execution-context` | Optional execution context return strip |
| `trade-reconciliation-work-area` | Primary reconciliation work area |
| `trade-reconciliation-statement-panel` | Internal statement panel |
| `trade-reconciliation-result-panel` | Reconciliation result panel |

Existing control hooks remain available:

- `reconciliation-export-button`
- `reconciliation-account-select`
- `reconciliation-source-select`
- `reconciliation-file-input`
- `reconciliation-import-button`

## 3. Token Cleanup

The page previously failed the changed-file ArtDeco token check because its scoped style block used fixed pixel spacing, raw color fallbacks, and local status chip colors.

This batch replaced the touched page-local values with existing ArtDeco tokens:

- spacing: `--artdeco-spacing-*`
- radius: `--artdeco-radius-*`
- foreground/background: `--artdeco-fg-*`, `--artdeco-bg-*`
- borders: `--artdeco-border-default`, `--artdeco-gold-opacity-10`
- chip state colors: `--ad-chip-*`

No new shared token was introduced.

## 4. TDD Evidence

RED:

```text
npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g Trade-Reconciliation --project=chromium
```

Result: failed as expected because `trade-reconciliation-page` did not exist.

GREEN:

```text
npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g Trade-Reconciliation --project=chromium
```

Result: `1 passed`.

## 5. Verification

Completed:

- `npx eslint src/views/trade/Reconciliation.vue --quiet`: pass.
- `node scripts/check-artdeco-tokens.js --target-file src/views/trade/Reconciliation.vue`: pass.
- `npx impeccable --json src/views/trade/Reconciliation.vue`: `[]`.
- `npx playwright test tests/e2e/phase3-mainline-matrix.spec.ts -g Trade-Reconciliation --project=chromium`: Chromium, `1 passed`.
- `npm run type-check -- --pretty false`: pass, no TypeScript errors reported.
- `openspec validate standardize-artdeco-route-grammar --strict`: valid. PostHog flush warnings were emitted after validation, but the command exited `0`.
- PM2 status: `mystocks-backend` online at `http://localhost:8020`, `mystocks-frontend` online at `http://localhost:3020`.
- `git diff --check` for the scoped files: pass.

Pre-commit scope gate:

- `gitnexus impact Reconciliation.vue --direction upstream --repo mystocks --summary-only --include-tests`: LOW risk, `0` direct dependents, `0` affected processes.
- Staged `gitnexus detect-changes` must be run immediately before commit after the scoped files are staged.

## 6. Boundary Confirmation

This is a route-local hook/token alignment. It does not implement a new page design brief, alter the route tree, alter backend or frontend API contracts, or extract shared components.
