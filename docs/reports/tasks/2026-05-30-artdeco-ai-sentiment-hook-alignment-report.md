# ArtDeco AI Sentiment Hook Alignment Report

Date: 2026-05-30

Target route: `/ai/sentiment`

Target component: `web/frontend/src/views/ai/Sentiment.vue`

OpenSpec change: `standardize-artdeco-route-grammar`

## 1. Scope

This batch applies the approved route-level ArtDeco grammar to the canonical AI sentiment page.

It is intentionally route-local:

- No router changes.
- No API contract changes.
- No shared Vue component extraction.
- No mutation under `web/frontend/src/views/artdeco-pages/**`.
- No AI sentiment API client, composable orchestration, or child component behavior change.

## 2. Route Grammar Hooks Added

The page now exposes standard Playwright `data-testid` route-level hooks:

| Hook | Surface |
|---|---|
| `ai-sentiment-page` | Route root |
| `ai-sentiment-header` | Header band |
| `ai-sentiment-refresh` | Refresh action |
| `ai-sentiment-status-strip` | KPI/status strip |
| `ai-sentiment-primary-surface` | Primary sentiment work area |

The child components already provide single-root visible surfaces, so the route page owns the hook contract through fallthrough attributes without changing the child component implementations.

## 3. TDD Evidence

RED:

```text
npx playwright test tests/e2e/ai-sentiment-workbench.spec.ts -g "renders the canonical ai sentiment page" --project=chromium
```

Result: failed as expected because `ai-sentiment-page` did not exist as a `data-testid` selector.

GREEN:

```text
npx playwright test tests/e2e/ai-sentiment-workbench.spec.ts -g "renders the canonical ai sentiment page" --project=chromium
```

Result: Chromium, `1 passed`.

## 4. Verification

Completed:

- `npx eslint src/views/ai/Sentiment.vue --quiet`: pass.
- `node scripts/check-artdeco-tokens.js --target-file src/views/ai/Sentiment.vue`: pass.
- `npx impeccable --json src/views/ai/Sentiment.vue`: `[]`.
- `npx playwright test tests/e2e/ai-sentiment-workbench.spec.ts -g "renders the canonical ai sentiment page" --project=chromium`: Chromium, `1 passed`.
- `npm run type-check -- --pretty false`: pass, no TypeScript errors reported.
- `openspec validate standardize-artdeco-route-grammar --strict`: valid. PostHog flush warnings were emitted after validation, but the command exited successfully.
- PM2 status: `mystocks-backend` online at `http://localhost:8020`, `mystocks-frontend` online at `http://localhost:3020`.
- `git diff --check` for the scoped files: pass.

Pre-commit scope gate:

- `gitnexus detect-changes --scope staged --repo mystocks`: LOW risk, `5` files, `4` changed symbols, `0` affected processes.

Impact gate:

- `gitnexus impact --target_uid File:web/frontend/src/views/ai/Sentiment.vue --direction upstream --repo mystocks --summary-only --include-tests`: LOW risk, `1` direct dependent, `0` affected processes.

## 5. Boundary Confirmation

This is a route-local hook alignment. It does not implement a new page design brief, alter the route tree, alter backend or frontend API contracts, or extract shared components.
