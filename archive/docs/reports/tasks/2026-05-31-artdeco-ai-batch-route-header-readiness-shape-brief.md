# ArtDeco AI Batch Route Header Readiness Shape Brief

Date: 2026-05-31

Function Tree node: `artdeco-web-design-governance/ai-batch-shape-readiness`

Target future route: `/ai/batch`

Target future page: `web/frontend/src/views/ai/BatchAnalysis.vue`

## 1. Purpose

This document is a readiness shape brief only. It prepares a future, separately approved `ArtDecoRouteHeader` migration for `/ai/batch`.

No page implementation is changed in this readiness node.

The goal is to decide whether the current `/ai/batch` custom header is a valid route-header-shell migration target, define the exact future shape, and preserve the current AI batch runtime, form, task, and result semantics.

IMPECCABLE_PREFLIGHT: context=pass product=pass command_reference=pass shape=not_required image_gate=skipped:docs-only-readiness-brief mutation=docs-only

## 2. Current Page Shape

`BatchAnalysis.vue` currently renders a page-local custom shell:

- root hook: `data-testid="ai-batch-page"`
- header hook: `data-testid="ai-batch-header"`
- refresh action hook: `data-testid="ai-batch-refresh"`
- runtime strip hook: `data-testid="ai-batch-status-strip"`
- runtime message hook: `data-testid="ai-batch-runtime-message"`
- primary surface hook: `data-testid="ai-batch-primary-surface"`
- control lens hook: `data-testid="ai-batch-control-lens"`
- submit hook: `data-testid="batch-analysis-submit"`
- task row hook: `data-testid="batch-analysis-task-row"`
- result row hook: `data-testid="batch-analysis-result-row"`

The current visual hierarchy is:

1. Custom page header: title, subtitle, and refresh icon button.
2. Runtime status band: readiness label, last update, active task count, safety copy, and optional runtime message.
3. Primary grid: control lens, task list, selected task summary, and result table.

The existing E2E coverage in `web/frontend/tests/e2e/ai-batch-analysis.spec.ts` already asserts the route, header, refresh button, status strip, control lens, primary surface, task row, submit action, summary panel, and result row.

## 3. Shape Decision

`/ai/batch` is a valid second-wave route-header-shell candidate.

The page should migrate its custom header to `ArtDecoRouteHeader` in a future implementation node, but only after this brief is approved.

The future migration should be narrower than a page redesign:

- replace the `<header class="workbench-header" data-testid="ai-batch-header">` shell with `ArtDecoRouteHeader`
- keep the page root `data-testid="ai-batch-page"` unchanged
- keep the route-level header hook as `test-id="ai-batch-header"`
- keep the refresh command inside the route header `#actions` slot
- keep the title text as `批量分析`
- keep the current subtitle meaning: unified observation of batch backtest, batch screening, and batch monitoring runtime evidence
- use an ArtDeco eyebrow such as `AI batch workbench`
- do not move the runtime status band into the header
- do not change task submission, task selection, result rendering, mock routes, or API payload expectations

This matches the established `/ai/sentiment` route-header pattern while avoiding accidental ownership changes to batch-analysis runtime state.

## 4. Required Future Implementation Shape

The future implementation node should use this shape:

```vue
<ArtDecoRouteHeader
  title="批量分析"
  subtitle="统一观察批量回测、批量选股与批量监控任务的运行时证据。"
  eyebrow="AI batch workbench"
  test-id="ai-batch-header"
>
  <template #actions>
    <button
      type="button"
      class="icon-button"
      data-testid="ai-batch-refresh"
      :disabled="isSubmitting"
      aria-label="刷新批量分析状态"
      @click="refresh"
    >
      ...
    </button>
  </template>
</ArtDecoRouteHeader>
```

The future E2E RED/GREEN assertion should be:

```ts
await expect(page.getByTestId('ai-batch-header')).toHaveClass(/artdeco-route-header/)
```

The assertion must be added before the implementation and fail first against the current custom header.

## 5. Runtime State That Must Not Move

The future route-header-shell migration must not change ownership or behavior of:

- `useBatchAnalysisWorkbench`
- runtime status loading and refresh behavior
- readiness label and readiness class
- runtime message display
- active task count and selected task state
- task submission and pending/disabled state
- `batch-analysis-task-row` selection behavior
- selected task summary
- result table rows
- E2E mock endpoints:
  - `/api/csrf-token`
  - `/api/v1/strategies/batch-analysis/runtime-status`
  - `/api/v1/strategies/batch-analysis/tasks`
  - `/api/v1/strategies/batch-analysis/tasks/batch_abc`
  - `/api/v1/strategies/batch-analysis/submit`

The runtime strip should remain a sibling below the route header because it reports batch workbench state, not route identity.

## 6. Visual Token And Design Guardrails

The future implementation should preserve the product UI register:

- dense operational layout, not a marketing hero
- restrained ArtDeco shell around the route identity only
- no new decorative blobs, orbs, or unrelated gradients
- no mobile/tablet responsive branch or `@media (max-width)` rule
- no token bypass for visual colors, borders, shadow, or spacing
- no nested card treatment around the whole page
- no change to financial/risk/data semantic colors

The page can keep existing local classes for the status band, panels, rows, and result table until a separately approved extraction or polish node exists.

## 7. Non-Goals

This readiness node and the future route-header-shell migration must not:

- modify router paths, aliases, redirects, route names, or route metadata
- modify backend API contracts or OpenAPI shape
- modify frontend API clients
- change E2E mock payload structure
- change form fields or submission semantics
- change task status, result, score, or evidence semantics
- extract shared AI batch components
- introduce a new shared workbench header abstraction
- redesign the full page
- change `/ai/sentiment` or other AI routes

## 8. Recommended Future Function Tree Node

After user approval of this brief, create a separate implementation node:

```text
route-header-shell-ai-batch
```

Recommended allowed paths:

- `web/frontend/src/views/ai/BatchAnalysis.vue`
- `web/frontend/tests/e2e/ai-batch-analysis.spec.ts`
- `docs/reports/tasks/`
- `docs/guides/web/ARTDECO_ROUTE_HEADER_SHELL_MODIFICATION_RULES.md`
- `web/frontend/src/components/artdeco/route-shell/`

Recommended gates:

1. GitNexus impact for `BatchAnalysis.vue` or documented SFC-resolution limitation.
2. RED E2E assertion proving `ai-batch-header` does not yet have `artdeco-route-header`.
3. Minimal `ArtDecoRouteHeader` migration.
4. GREEN focused E2E for `ai-batch-analysis.spec.ts`.
5. Target ESLint.
6. ArtDeco token check.
7. `npx impeccable --json web/frontend/src/views/ai/BatchAnalysis.vue`.
8. `npm run type-check -- --pretty false`.
9. OpenSpec validation if the implementation discovers a spec-relevant change.
10. Function Tree validation and gate.
11. GitNexus staged scope gate.
12. Implementation commit.
13. Function Tree closeout and closeout report.

## 9. Approval Requirement

This brief is not implementation approval by itself.

The next route-header-shell code change should start only after the user explicitly approves the `/ai/batch` shape brief.
