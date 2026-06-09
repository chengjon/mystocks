# Page Audit: market/Tdx Legacy Static Shell Truth

## Scope
- Batch: `secondary-batch-41`
- Execution surface: `code-review-only`
- Owner: `web/frontend/src/views/market/Tdx.vue`

## Finding
`market/Tdx.vue` was an unrouted legacy TDX data-interface surface. It imported `useTdx()` and displayed simulated runtime data:

- `REFRESH ALL` action and success/error toasts
- connection status, response time, and active sessions
- hardcoded primary/backup TDX server metadata
- mock quote rows, bid/ask spread, and random price changes
- K-line period/date controls and simulated chart loading

Because there is no verified canonical TDX owner and the top-level `TdxMarket.vue` had already been degraded to a static shell, keeping this page live would preserve a second pseudo market-data truth surface.

## Repair
- `market/Tdx.vue` now renders an honest static shell and points users to `/market/realtime`, `/market/technical`, and `/system/data`.
- `market/composables/useTdx.ts` was deleted after confirming it was only consumed by this legacy page.
- `market/styles/Tdx.scss` was deleted after confirming it had no remaining imports.

## Cleanup Decision
- Cleanup objects: `web/frontend/src/views/market/composables/useTdx.ts`, `web/frontend/src/views/market/styles/Tdx.scss`.
- Code-path status: no remaining references from Vue, TypeScript, or SCSS sources after the page stopped importing them.
- Functional-tree status: duplicate legacy page-local implementation tied to a static-shelled legacy TDX page.
- Deletion basis: the only consumer was removed, and preserving the files would keep an orphan pseudo-live TDX implementation with TODO API and random/mock runtime semantics.

## Verification
- RED: `cd web/frontend && npx vitest run src/views/market/__tests__/Tdx.spec.ts` failed before repair because the page did not render `legacy-static-shell`.
- GREEN: `cd web/frontend && npx vitest run src/views/market/__tests__/Tdx.spec.ts` passed `1/1`.
- Same-domain regression: `cd web/frontend && npx vitest run src/views/market/__tests__/*.spec.ts` passed `19/19`.
- Secondary inventory: `npm run generate:myweb-audit:secondary-inventory` passed and reduced high-priority items from `14` to `13`.

## Residual Risk
No live browser proof was added because this is an unrouted secondary inventory page with no independent routed proof surface in the current router graph.
