# Page Audit: RealTimeMonitor Legacy Static Shell Truth

## Scope
- Batch: `secondary-batch-43`
- Execution surface: `code-review-only`
- Owner: `web/frontend/src/views/RealTimeMonitor.vue`

## Finding
`RealTimeMonitor.vue` was an unrouted legacy realtime monitor surface. It mounted SSE demo widgets and preserved pseudo-live runtime behavior:

- `DashboardMetrics`, `RiskAlerts`, `TrainingProgress`, and `BacktestProgress` widget mounting
- direct `/api/v1/sse/status` request on mount
- connection count displays with fallback zero semantics
- local test buttons for training, backtest, risk alert, and dashboard updates
- page-only `RealTimeMonitor.scss` style import

Because there is no verified one-to-one canonical SSE workbench owner, keeping this page live would preserve a duplicate realtime truth surface.

## Repair
- `RealTimeMonitor.vue` now renders an honest static shell and points users to `/market/realtime`, `/risk/alerts`, and `/strategy/backtest`.
- The page no longer imports SSE demo widgets, axios, Element Plus message APIs, or the page-only SCSS.
- `views/styles/RealTimeMonitor.scss` was deleted after confirming the page stopped importing it.

## Cleanup Decision
- Cleanup object: `web/frontend/src/views/styles/RealTimeMonitor.scss`.
- Code-path status: no remaining references after `RealTimeMonitor.vue` stopped importing it.
- Functional-tree status: duplicate legacy page-local style tied to a static-shelled legacy realtime monitor page.
- Deletion basis: preserving the file would keep orphan style infrastructure for a retired pseudo-live monitor surface.

## Verification
- RED: `cd web/frontend && npx vitest run src/views/__tests__/RealTimeMonitor.spec.ts` failed before repair because the page did not render `legacy-static-shell` and mounted legacy SSE runtime widgets.
- GREEN: `cd web/frontend && npx vitest run src/views/__tests__/RealTimeMonitor.spec.ts tests/unit/config/realtime-monitor-types-cleanup.spec.ts tests/unit/config/root-demo-style-entrypoints.spec.ts` passed `4/4`.
- Secondary inventory: `npm run generate:myweb-audit:secondary-inventory` passed and reduced high-priority items from `12` to `11`.

## Residual Risk
No live browser proof was added because this is an unrouted secondary inventory page with no independent routed proof surface in the current router graph.
