# ArtDeco AI Batch Hook Alignment Report

Date: 2026-05-30

Target route: `/ai/batch`

Target component: `web/frontend/src/views/ai/BatchAnalysis.vue`

OpenSpec change: `standardize-artdeco-route-grammar`

## 1. Scope

This batch applies the approved route-level ArtDeco grammar to the canonical AI batch analysis page.

It is intentionally route-local:

- No router changes.
- No API contract changes.
- No shared Vue component extraction.
- No mutation under `web/frontend/src/views/artdeco-pages/**`.
- No AI batch API client, runtime registry, task submission, or result semantics change.

## 2. Route Grammar Hooks Added

The page now exposes standard Playwright `data-testid` route-level hooks:

| Hook | Surface |
|---|---|
| `ai-batch-page` | Route root |
| `ai-batch-header` | Header band |
| `ai-batch-refresh` | Refresh action |
| `ai-batch-status-strip` | Runtime status strip |
| `ai-batch-runtime-message` | Conditional runtime message |
| `ai-batch-control-lens` | Batch task configuration panel |
| `ai-batch-primary-surface` | Primary batch work area |

Existing task-level hooks remain unchanged:

- `batch-analysis-submit`
- `batch-analysis-task-row`
- `batch-analysis-result-row`

## 3. TDD Evidence

RED:

```text
npx playwright test tests/e2e/ai-batch-analysis.spec.ts -g "renders runtime" --project=chromium
```

Result: failed as expected because `ai-batch-page` did not exist as a `data-testid` selector.

GREEN:

```text
npx playwright test tests/e2e/ai-batch-analysis.spec.ts -g "renders runtime" --project=chromium
```

Result: Chromium, `1 passed`.

## 4. Verification

Completed:

- `npx eslint src/views/ai/BatchAnalysis.vue --quiet`: pass.
- `node scripts/check-artdeco-tokens.js --target-file src/views/ai/BatchAnalysis.vue`: pass after replacing pre-existing hardcoded route-local spacing/color values with existing ArtDeco tokens.
- `npx impeccable --json src/views/ai/BatchAnalysis.vue`: `[]` after rerun with an escalated writable npm cache because the sandboxed first run hit `EROFS` in `/root/.npm/_cacache`.
- `npx playwright test tests/e2e/ai-batch-analysis.spec.ts -g "renders runtime" --project=chromium`: Chromium, `1 passed`.
- `npm run type-check -- --pretty false`: pass, no TypeScript errors reported.
- `openspec validate standardize-artdeco-route-grammar --strict`: valid.
- PM2 status: `mystocks-backend` online at `http://localhost:8020`, `mystocks-frontend` online at `http://localhost:3020`.
- `git diff --check` for the scoped files: pass.

Pre-commit scope gate:

- `git diff --cached --check`: pass for the staged 5-file scope.
- `gitnexus detect-changes --scope staged --repo mystocks`: LOW risk, `5` changed files, `10` changed symbols, `0` affected processes.
- GitNexus index hygiene: `npx gitnexus analyze` was rerun before the staged scope gate and completed with `234,114` nodes, `321,415` edges, `2,738` clusters, and `300` flows. The MCP response still displayed a stale commit metadata warning after the refresh; local `.gitnexus/meta.json` matched the current HEAD, so this is recorded as a tool metadata warning rather than a route-scope expansion.

Impact gate:

- `gitnexus impact --target_uid File:web/frontend/src/views/ai/BatchAnalysis.vue --direction upstream --repo mystocks --summary-only --include-tests`: LOW risk, `1` direct dependent, `0` affected processes.

## 5. Boundary Confirmation

This is a route-local hook alignment plus page-local token cleanup required by the changed-file ArtDeco gate. It does not implement a new page design brief, alter the route tree, alter backend or frontend API contracts, or extract shared components.
