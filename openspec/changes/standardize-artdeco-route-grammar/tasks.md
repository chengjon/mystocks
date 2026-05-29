## 1. Proposal Validation

- [x] 1.1 Review current ArtDeco page-pilot extraction analysis.
- [x] 1.2 Review existing `artdeco-design-governance` spec.
- [x] 1.3 Create the OpenSpec proposal, design note, task list, and spec delta.
- [x] 1.4 Run `openspec validate standardize-artdeco-route-grammar --strict`.
- [x] 1.5 Present the proposal for approval before implementation.

Approval record:

- Date: 2026-05-29
- User wording: `批准standardize-artdeco-route-grammar，请继续`
- Approved scope: documentation implementation only; no route changes, no API contract changes, no Vue page-source changes, and no shared component extraction.

## 2. Documentation Implementation After Approval

- [x] 2.1 Add the route grammar to the appropriate ArtDeco guide or design-governance documentation.
- [x] 2.2 Add the route-level E2E hook standard to the page review checklist or verification guide.
- [x] 2.3 Update the impeccable line summary to point future route craft work at this standard.
- [x] 2.4 Keep documentation changes free of router, API, shared component, and page-source mutations unless separately approved.

## 3. Optional Page Alignment After Separate Approval

- [x] 3.1 Select one low-risk route to adopt the hook standard.
- [x] 3.2 Add failing route-level E2E assertions before page implementation.
- [x] 3.3 Implement only the approved route-local hook and grammar alignment.
- [x] 3.4 Verify with targeted E2E, ArtDeco token check, eslint, type-check, and `impeccable --json`.

Alignment record:

- Date: 2026-05-29
- User wording: `同意，请继续`
- Selected route: `web/frontend/src/views/risk/Alerts.vue`
- Report: `docs/reports/tasks/2026-05-29-artdeco-risk-alerts-hook-alignment-report.md`
- Boundary: no route changes, no API contract changes, no shared component extraction, and no `web/frontend/src/views/artdeco-pages/**` changes.

Additional alignment record:

- Date: 2026-05-29
- User wording: `请继续`
- Selected route: `web/frontend/src/views/trade/Reconciliation.vue`
- Report: `docs/reports/tasks/2026-05-29-artdeco-trade-reconciliation-hook-alignment-report.md`
- Boundary: no route changes, no API contract changes, no shared component extraction, and no `web/frontend/src/views/artdeco-pages/**` changes.
- Note: this route already contained control-level hooks; this batch added route-level grammar hooks and replaced page-local raw spacing/color literals with existing ArtDeco tokens.

Additional alignment record:

- Date: 2026-05-30
- User wording: `请继续`
- Selected route: `web/frontend/src/views/market/Realtime.vue`
- Report: `docs/reports/tasks/2026-05-30-artdeco-market-realtime-hook-alignment-report.md`
- Boundary: no route changes, no API contract changes, no shared component extraction, and no `web/frontend/src/views/artdeco-pages/**` changes.
- Note: this route was the first ArtDeco page pilot; this batch only adds route-level grammar hooks and targeted E2E coverage.

Additional alignment record:

- Date: 2026-05-30
- User wording: `请继续`
- Selected route: `web/frontend/src/views/trade/Execution.vue`
- Report: `docs/reports/tasks/2026-05-30-artdeco-trade-execution-hook-alignment-report.md`
- Boundary: no route changes, no API contract changes, no shared component extraction, and no `web/frontend/src/views/artdeco-pages/**` changes.
- Note: this batch adds route-level grammar hooks and a focused route hook E2E; existing execution-detail behavior assertions remain outside this grammar slice.

## 4. Shared Component Extraction Gate

- [ ] 4.1 Draft a separate extraction proposal before creating shared Vue components.
- [ ] 4.2 Define component props, slots, events, state vocabulary, token rules, hook names, migration order, and rollback plan.
- [ ] 4.3 Confirm the candidate does not own API orchestration, route metadata, backend contracts, frontend API clients, or financial row semantics.
