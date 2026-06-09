# Page Audit: Monitor Legacy Static Shell Truth

## Scope
- Batch: `secondary-batch-42`
- Execution surface: `code-review-only`
- Owner: `web/frontend/src/views/monitor.vue`

## Finding
`monitor.vue` was an unrouted legacy system monitor surface. It imported `usemonitor()` and displayed local pseudo-live runtime data:

- refresh and auto-refresh controls
- local service status cards and details
- generated monitor history rows
- hardcoded local endpoint and database metadata
- seeded warning/healthy states before any verified monitoring contract existed

Because there is no verified one-to-one canonical monitoring owner for this legacy page, keeping those controls would preserve a second pseudo system-monitoring truth surface.

## Repair
- `monitor.vue` now renders an honest static shell and points users to `/system/health`, `/system/resources`, and `/trade/terminal`.
- `views/composables/usemonitor.ts` was deleted after confirming it was only consumed by this legacy page.
- `views/styles/monitor.scss` was deleted after confirming the page stopped importing it.

## Cleanup Decision
- Cleanup objects: `web/frontend/src/views/composables/usemonitor.ts`, `web/frontend/src/views/styles/monitor.scss`.
- Code-path status: no remaining references from Vue, TypeScript, or SCSS sources after the page stopped importing them.
- Functional-tree status: duplicate legacy page-local implementation tied to a static-shelled legacy monitor page.
- Deletion basis: the only consumer was removed, and preserving the files would keep orphan pseudo-live monitor state with local refresh and endpoint semantics.

## Verification
- RED: `cd web/frontend && npx vitest run src/views/__tests__/monitor.spec.ts` failed before repair because the old page did not render `legacy-static-shell` and entered the legacy runtime path.
- GREEN: `cd web/frontend && npx vitest run src/views/__tests__/monitor.spec.ts` passed `1/1`.
- Secondary inventory: `npm run generate:myweb-audit:secondary-inventory` passed and reduced high-priority items from `13` to `12`.

## Residual Risk
No live browser proof was added because this is an unrouted secondary inventory page with no independent routed proof surface in the current router graph.
