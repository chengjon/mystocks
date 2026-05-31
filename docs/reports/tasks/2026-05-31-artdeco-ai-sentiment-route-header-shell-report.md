# ArtDeco AI Sentiment Route Header Shell Report

Date: 2026-05-31

Function Tree node: `artdeco-web-design-governance/route-header-shell-ai-sentiment`

Implementation commit: `50a91d20b feat(web): migrate ai sentiment route header shell`

## Scope

Migrated `/ai/sentiment` from the custom `AiSentimentHero` header shell to the shared `ArtDecoRouteHeader` route header shell.

Touched implementation surface:

- `web/frontend/src/views/ai/components/AiSentimentHero.vue`
- `web/frontend/tests/e2e/ai-sentiment-workbench.spec.ts`

Governance/report surface:

- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `.governance/programs/artdeco-web-design-governance/cards/route-header-shell-ai-sentiment.yaml`
- `docs/guides/web/ARTDECO_ROUTE_HEADER_SHELL_MODIFICATION_RULES.md`
- `docs/reports/tasks/2026-05-31-artdeco-ai-sentiment-route-header-shell-report.md`

## Compatibility Boundary

Preserved:

- `/ai/sentiment` route path and router ownership
- `ai-sentiment-page`, `ai-sentiment-header`, `ai-sentiment-refresh`, `ai-sentiment-status-strip`, and `ai-sentiment-primary-surface` test hooks
- header metadata: `REQ_ID`, `DOMAIN: AI`, `ENTRY: sentiment`
- header status text and type from `pageStatusText` and `pageStatusType`
- refresh action slot wired through the existing `refreshWorkbench` handler
- `/risk/news` wrapper navigation back into the canonical AI sentiment page

Not changed:

- `web/frontend/src/router/index.ts`
- backend API routes, OpenAPI/Pydantic schemas, or frontend API clients
- request URLs, stores, transport wrappers, or composables
- `web/frontend/src/views/ai/Sentiment.vue`
- `useAiSentimentWorkbench`
- AI sentiment summary cards, workbench panels, text analysis behavior, announcement feed behavior, or risk/news wrapper behavior
- shared AI sentiment business components

## Implementation Notes

`AiSentimentHero.vue` now renders `ArtDecoRouteHeader` directly.

The component preserves the existing public props:

- `eyebrow`
- `title`
- `subtitle`
- `requestId`
- `statusText`
- `statusType`

The old metadata rail was moved into the `ArtDecoRouteHeader` `meta` slot.

The migration required explicit `data-testid` forwarding because `ArtDecoRouteHeader` owns the final `test-id` prop. `AiSentimentHero` now maps the parent `data-testid` attr to `ArtDecoRouteHeader`'s `test-id` prop and forwards the remaining attrs unchanged.

## GitNexus Evidence

Pre-edit impact analysis for `web/frontend/src/views/ai/components/AiSentimentHero.vue`:

- risk: LOW
- direct affected symbols: 1
- affected processes: 0

Staged scope gate:

- changed files: 6
- risk level: low
- affected processes: 0

GitNexus index note:

- Local `gitnexus analyze` was run, not `npx gitnexus analyze`.
- Analyze result: repository indexed successfully in 298.5s, `234,298 nodes`, `321,614 edges`, `2738 clusters`, `300 flows`.
- MCP metadata still reported stale `indexed_commit` after analyze; this is the same known MCP metadata residual observed in this route-header workline.

## TDD Evidence

RED command:

```bash
npx playwright test tests/e2e/ai-sentiment-workbench.spec.ts -g "renders the canonical ai sentiment page" --project=chromium
```

Expected failure:

- `ai-sentiment-header` existed
- expected `/artdeco-route-header/`
- received `hero-shell artdeco-card-shell`

First GREEN attempt:

- failed because `data-testid="ai-sentiment-header"` did not land on the final `ArtDecoRouteHeader` section
- root cause: the route header component uses the `test-id` prop for the final `data-testid`, so a plain fallthrough `data-testid` attr was not enough

Final GREEN command:

```bash
npx playwright test tests/e2e/ai-sentiment-workbench.spec.ts -g "renders the canonical ai sentiment page" --project=chromium
```

Result:

- Chromium
- 1 test passed

Full AI sentiment E2E file:

```bash
npx playwright test tests/e2e/ai-sentiment-workbench.spec.ts --project=chromium
```

Result:

- Chromium
- 2 tests passed

## Static And Governance Gates

Passed:

- `npx eslint src/views/ai/components/AiSentimentHero.vue tests/e2e/ai-sentiment-workbench.spec.ts --no-warn-ignored`
- `node scripts/check-artdeco-tokens.js --target-file src/views/ai/components/AiSentimentHero.vue`
- `npx impeccable --json src/views/ai/components/AiSentimentHero.vue` returned `[]`
- `npm run type-check`: exit code 0, 0 total errors, 0 structural syntax errors, 0 changed-file errors
- `openspec validate --all --strict`: 63 passed, 0 failed
- `ft-governance scope-check --files ...`: within active authorization
- `ft-governance validate --steward`: passed
- `git diff --cached --check`: passed

PM2:

- `mystocks-backend`: online, expected URL `http://localhost:8020`
- `mystocks-frontend`: online, expected URL `http://localhost:3020`

## Dirty Worktree Note

The repository contains unrelated dirty files. This node staged only the implementation, E2E assertion, governance node/card/active-gate files, ledger update, and this report.

Known unrelated file to keep unstaged:

- `.governance/programs/artdeco-web-design-governance/tree.md`

## Closeout Result

The `/ai/sentiment` route now uses the shared ArtDeco route header shell through its `AiSentimentHero` component while preserving route ownership, API/client contracts, AI sentiment runtime state, header metadata, status, refresh behavior, and the `/risk/news` wrapper path.
