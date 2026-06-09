# ArtDeco AI Sentiment Route Header Readiness Shape Brief

Date: 2026-05-31

Route: `/ai/sentiment`

Page file: `web/frontend/src/views/ai/Sentiment.vue`

Header component: `web/frontend/src/views/ai/components/AiSentimentHero.vue`

Function Tree node: `artdeco-web-design-governance/ai-sentiment-shape-test-hardening`

## 1. Purpose

Prepare `/ai/sentiment` for a possible future ArtDeco route header shell migration without changing the page implementation in this node.

This brief answers one narrow question: can the current custom AI sentiment header be migrated to `ArtDecoRouteHeader` later without losing route ownership, runtime state, metadata, actions, or sentiment-workbench semantics?

## 2. Current Page Shape

The current page already follows the route grammar at the page level:

- `ai-sentiment-page`: route root
- `ai-sentiment-header`: header band
- `ai-sentiment-refresh`: refresh action
- `ai-sentiment-status-strip`: KPI/status strip
- `ai-sentiment-primary-surface`: primary sentiment work area

The header is not a direct local `ArtDecoHeader` block inside `Sentiment.vue`. The page renders `AiSentimentHero`, and that child component renders the route-local shell markup plus `ArtDecoHeader`.

Current header responsibilities:

- eyebrow: `AI sentiment workbench`
- title: `情感分析工作台`
- subtitle: AI sentiment workbench scope text
- metadata: `REQ_ID`, `DOMAIN: AI`, `ENTRY: sentiment`
- runtime status: `pageStatusText` and `pageStatusType`
- action slot: refresh button wired to `refreshWorkbench`

## 3. Shape Decision

Future migration is feasible, but it should target `AiSentimentHero.vue`, not `Sentiment.vue` first.

Reason:

- `AiSentimentHero` is currently used only by `Sentiment.vue`.
- It already owns the exact header shell that would be replaced.
- Keeping the migration in the child component preserves the routed page's data orchestration and keeps `Sentiment.vue` stable.
- `ArtDecoRouteHeader` can preserve the title, subtitle, status, metadata slot, action slot, and `data-testid` fallthrough contract.

The future route header migration should therefore replace the root header shell inside `AiSentimentHero.vue` with `ArtDecoRouteHeader`.

## 4. Required Future Implementation Shape

Use `ArtDecoRouteHeader` as the visual shell and preserve all existing public props:

- `title`
- `subtitle`
- `eyebrow`
- `requestId`
- `statusText`
- `statusType`

Render metadata through the route header `meta` slot:

- `REQ_ID: {{ requestId }}`
- `DOMAIN: AI`
- `ENTRY: sentiment`

Render the existing action slot through the route header `actions` slot.

Keep the existing `data-testid="ai-sentiment-header"` behavior. The current page passes the test id as a fallthrough attribute to `AiSentimentHero`; the future implementation must confirm this still lands on the final route header section.

## 5. Runtime State That Must Not Move

The future header shell must remain display-only. These stay owned by `useAiSentimentWorkbench` and `Sentiment.vue`:

- announcement, market sentiment, stock trend, and text-analysis data loading
- `refreshWorkbench`
- `runTextAnalysis`
- selected symbol and analysis source state
- stale/error/loading state decisions
- request-id provenance
- `risk/news` wrapper navigation behavior

## 6. Test Hardening Added In This Node

The E2E test now scopes header metadata assertions to `ai-sentiment-header` instead of relying on the broad `.hero-meta` selector.

Hardened assertions:

- header remains visible
- `REQ_ID: req-ai-sentiment-workbench-1` remains inside the header
- `DOMAIN: AI` remains inside the header
- `ENTRY: sentiment` remains inside the header
- `AI 工作台在线` remains inside the header after mocked data loads
- `ai-sentiment-refresh` remains inside the header

These assertions make the next migration safer because a future change cannot satisfy the page-level test while accidentally moving or dropping the header metadata/status/action surface.

## 7. Non-Goals

This node does not:

- migrate to `ArtDecoRouteHeader`
- modify `web/frontend/src/router/index.ts`
- modify backend APIs, OpenAPI/Pydantic schemas, or frontend API clients
- modify `useAiSentimentWorkbench`
- modify AI sentiment child panel behavior
- change `/risk/news` wrapper behavior
- extract shared AI sentiment business components

## 8. Recommended Next Node

After this brief is approved, create a separate Function Tree node:

`route-header-shell-ai-sentiment`

Suggested implementation scope:

- `web/frontend/src/views/ai/components/AiSentimentHero.vue`
- `web/frontend/tests/e2e/ai-sentiment-workbench.spec.ts`
- `docs/reports/tasks/`
- `docs/guides/web/ARTDECO_ROUTE_HEADER_SHELL_MODIFICATION_RULES.md`

Suggested RED assertion for that future node:

```ts
await expect(page.getByTestId('ai-sentiment-header')).toHaveClass(/artdeco-route-header/)
```

Expected RED before migration:

- `ai-sentiment-header` exists
- expected `/artdeco-route-header/`
- received the existing custom `hero-shell artdeco-card-shell` shell

## 9. Confirmation

This brief recommends a future `AiSentimentHero.vue` shell migration and no current page behavior changes. It should be explicitly approved before the future route header shell migration begins.
