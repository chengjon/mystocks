# ArtDeco AI Batch Route Header Shell Report

Date: 2026-05-31

Function Tree node: `artdeco-web-design-governance/route-header-shell-ai-batch`

Implementation commit: `39c8a3b2d feat(web): migrate ai batch route header shell`

## Scope

Migrated `/ai/batch` from a page-local custom header shell to the shared `ArtDecoRouteHeader` route header shell.

Touched implementation surface:

- `web/frontend/src/views/ai/BatchAnalysis.vue`
- `web/frontend/tests/e2e/ai-batch-analysis.spec.ts`

Governance/report surface:

- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `.governance/programs/artdeco-web-design-governance/cards/route-header-shell-ai-batch.yaml`
- `docs/guides/web/ARTDECO_ROUTE_HEADER_SHELL_MODIFICATION_RULES.md`
- `docs/reports/tasks/2026-05-31-artdeco-ai-batch-route-header-readiness-shape-brief.md`
- `docs/reports/tasks/2026-05-31-artdeco-ai-batch-route-header-shell-report.md`

## Compatibility Boundary

Preserved:

- `/ai/batch` route path and router ownership
- `ai-batch-page`, `ai-batch-header`, `ai-batch-refresh`, `ai-batch-status-strip`, `ai-batch-runtime-message`, `ai-batch-primary-surface`, `ai-batch-control-lens`, `batch-analysis-submit`, `batch-analysis-task-row`, and `batch-analysis-result-row` test hooks
- title text: `批量分析`
- subtitle meaning: unified observation of batch backtest, batch screening, and batch monitoring runtime evidence
- refresh action wired through the existing `refreshRuntime` handler
- runtime status strip position below the route header
- batch task submission, selected task summary, task rows, and result rows

Not changed:

- `web/frontend/src/router/index.ts`
- route names, aliases, redirects, metadata, or menu wiring
- backend API routes, OpenAPI/Pydantic schemas, or frontend API clients
- E2E mock endpoint URLs or payload shape
- `useBatchAnalysisWorkbench`
- runtime readiness labels, runtime message display, active task count, selected task state, task submission, task selection, or result semantics
- shared AI batch business components

## Implementation Notes

`BatchAnalysis.vue` now renders `ArtDecoRouteHeader` directly.

The migration keeps the existing route-level public hooks:

- `test-id="ai-batch-header"` lands on the `ArtDecoRouteHeader` root shell
- the existing `ai-batch-refresh` button stays in the header actions slot
- the page root stays `data-testid="ai-batch-page"`

The status band remains a sibling below the route header because it reports batch workbench runtime state, not route identity.

The page still owns its local form, task list, selected task summary, and result table.

## GitNexus Evidence

Pre-edit impact analysis for `web/frontend/src/views/ai/BatchAnalysis.vue`:

- initial target lookup by component name was not found
- file symbol resolved as `File:web/frontend/src/views/ai/BatchAnalysis.vue`
- risk: LOW
- direct affected symbols: 1
- affected processes: 0

Staged scope gate:

- changed files: 6
- risk level: low
- affected processes: 0

GitNexus index note:

- Local `gitnexus analyze` was run, not `npx gitnexus analyze`.
- Analyze result before implementation commit: repository indexed successfully in 178.0s, `230,293 nodes`, `315,799 edges`, `2730 clusters`, `300 flows`.
- MCP metadata still reported stale `indexed_commit` after analyze; this is the same known MCP metadata residual observed in this route-header workline.

## TDD Evidence

RED command:

```bash
npx playwright test tests/e2e/ai-batch-analysis.spec.ts -g "renders runtime" --project=chromium
```

Expected failure:

- `ai-batch-header` existed
- expected `/artdeco-route-header/`
- received `workbench-header`

GREEN command:

```bash
npx playwright test tests/e2e/ai-batch-analysis.spec.ts -g "renders runtime" --project=chromium
```

Result:

- Chromium
- 1 test passed

Full AI batch E2E file:

```bash
npx playwright test tests/e2e/ai-batch-analysis.spec.ts --project=chromium
```

Result:

- Chromium
- 1 test passed

## Static And Governance Gates

Passed:

- `npx eslint src/views/ai/BatchAnalysis.vue tests/e2e/ai-batch-analysis.spec.ts --no-warn-ignored`
- `node scripts/check-artdeco-tokens.js --target-file src/views/ai/BatchAnalysis.vue`
- `npx impeccable --json src/views/ai/BatchAnalysis.vue` returned `[]`
- `npm run type-check -- --pretty false`: exit code 0, 0 structural syntax errors, 0 type errors
- `openspec validate --all --strict`: 63 passed, 0 failed
- `ft-governance validate --steward`: passed
- `git diff --cached --check`: passed

## Dirty Worktree Note

The repository contains unrelated dirty files. This node staged only the implementation, E2E assertion, Function Tree governance files, ledger update, and this report.

Known unrelated files left unstaged include:

- `.governance/programs/artdeco-web-design-governance/tree.md`
- `docs/reports/quality/myweb-audit/frontend-view-inventory-correction-ai-batch-analysis-2026-05-10.md`

## Closeout Result

The `/ai/batch` route now uses the shared ArtDeco route header shell while preserving route ownership, API/client contracts, batch-analysis runtime state, refresh behavior, task submission, task selection, and result rendering.
