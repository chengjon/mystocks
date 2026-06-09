# Frontend View Checklist: `views/artdeco-pages/_templates/*`

> Date: 2026-05-10
> Scope: `web/frontend/src/views/artdeco-pages/_templates/*`
> Change: `openspec/changes/update-frontend-view-governance`
> Mode: read-only evidence batch, no file moves, no runtime code changes.

## Scope Inventory

| Path | Type | Route/Menu Owner | Runtime Import | Guard/Test Evidence | Classification | Archive Status |
| --- | --- | --- | --- | --- | --- | --- |
| `web/frontend/src/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue` | Vue skeleton template | no direct route/menu | imported by `web/frontend/src/views/risk/Center.vue` and `ExampleRiskManagement.vue` | `ArtDecoPageTemplate.spec.ts`, composable tests, docs, prior OpenSpec retain rule | `active-shared-skeleton` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/_templates/ExampleRiskManagement.vue` | Vue example/template page | no direct route/menu | imports `ArtDecoPageTemplate.vue` and risk-tab components | docs/plans governance references, guard-map references | `candidate-review/template-example` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/_templates/composables/useArtDecoPageTemplate.ts` | local skeleton composable | n/a | imported by `ArtDecoPageTemplate.vue` | `useArtDecoPageTemplate.spec.ts` | `active-shared-skeleton-support` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/_templates/composables/artDecoPageTemplateHelpers.ts` | local helper module | n/a | imported by `useArtDecoPageTemplate.ts` | `useArtDecoPageTemplateHelpers.test.ts` | `active-shared-skeleton-support` | `not-archive-approved` |
| `web/frontend/src/views/artdeco-pages/_templates/styles/ArtDecoPageTemplate.scss` | local style asset | n/a | imported by `ArtDecoPageTemplate.vue` | template component render tests indirectly guard it | `active-shared-skeleton-style` | `not-archive-approved` |

## Route And Menu Truth

- `router/index.ts`: no direct `_templates/*` route owner found.
- `MenuConfig.ts`: no direct `_templates/*` menu owner found.
- Current active consumer: `web/frontend/src/views/risk/Center.vue` imports `@/views/artdeco-pages/_templates/ArtDecoPageTemplate.vue`.
- Historical structure spec already says this dependency must be retained because risk center depends on the template skeleton.

## Hidden Reference And Guard Evidence

- Unit/component guard: `web/frontend/src/views/artdeco-pages/_templates/__tests__/ArtDecoPageTemplate.spec.ts`.
- Composable guard: `web/frontend/src/views/artdeco-pages/_templates/composables/__tests__/useArtDecoPageTemplate.spec.ts`.
- Node helper guard: `web/frontend/src/views/artdeco-pages/_templates/composables/__node_tests__/useArtDecoPageTemplateHelpers.test.ts`.
- Documentation references: `docs/plans/ARTDECO_COMPONENT_GOVERNANCE_RECORD_ARTDECO_PAGE_TEMPLATE.md`, `docs/guides/web/ARTDECO_PAGE_TEMPLATE_GUIDE.md`, and the frontend structure OpenSpec change explicitly identify `ArtDecoPageTemplate` as a retained skeleton dependency.
- Guard-map references in `docs/reports/quality/myweb-audit/frontend-view-guard-map-2026-05-10.json` include both `ArtDecoPageTemplate` and `ExampleRiskManagement`.

## Functional Asset Assessment

- `ArtDecoPageTemplate.vue` provides page-level skeleton behavior: header actions, refresh, loading, error, empty state, stats slot, tablist semantics, content panel, footer slot, trace id, and permission gate.
- `useArtDecoPageTemplate.ts` owns real page orchestration behavior: API request dispatch, cache timing, request id extraction, empty-state calculation, permission checks, active tab reconciliation, and keyboard navigation.
- `artDecoPageTemplateHelpers.ts` holds reusable pure helpers for response normalization, permission fallback, empty-state checks, and cache timing.
- `ExampleRiskManagement.vue` is not an active route, but it is a template/example page demonstrating the skeleton contract with risk domain slots and components.

## Redundant Page Decision

No file in this batch is archive-approved.

- `ArtDecoPageTemplate.vue` is active shared infrastructure, not a redundant page.
- The composable, helper, and style files are direct dependencies of the active skeleton.
- `ExampleRiskManagement.vue` can remain `candidate-review/template-example`; archive eligibility would require a separate approved mutation batch that first proves all template guide, governance docs, guard-map references, and example value have been retired or absorbed.

## Follow-Up Notes

- If `_templates` is later moved out of `views`, the target truth should be declared first, for example `components/artdeco/skeletons` or another approved shared-layer location.
- Do not mechanically archive `ExampleRiskManagement.vue` just because it has no route/menu owner; it still carries template demonstration and governance evidence.
- Any future mutation touching `ArtDecoPageTemplate.vue` must include risk center verification because `views/risk/Center.vue` is an active canonical page consumer.
