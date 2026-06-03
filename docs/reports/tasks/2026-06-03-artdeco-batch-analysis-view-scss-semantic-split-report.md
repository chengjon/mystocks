# ArtDecoBatchAnalysisView SCSS Semantic Split Report

Date: 2026-06-03

## Scope

- Node: `artdeco-web-design-governance/artdeco-batch-analysis-view-scss-semantic-split`
- Facade: `web/frontend/src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.scss`
- Change type: ArtDeco SCSS file-size governance and semantic partial split.

## User Constraints

- Continue the file-size governance route.
- Next priority is `ArtDecoBatchAnalysisView.scss`, split by layout / controls / panels / charts.
- Route header migration line remains unchanged.
- Only `/market/technical` may proceed under existing header-shell constraints.
- `market/LHB.vue` remains in the pending split list and must not be migrated first.
- Archive-related split work remains style slimming only: do not enable archive pages/layouts online and do not extract global shared components.

## Split Map

Before this task, the facade imported feature-style partials:

- `ArtDecoBatchAnalysisView.layout.scss`
- `ArtDecoBatchAnalysisView.progress.scss`
- `ArtDecoBatchAnalysisView.results.scss`
- `ArtDecoBatchAnalysisView.report.scss`
- `ArtDecoBatchAnalysisView.responsive.scss`

After this task, the facade imports semantic partials:

- `ArtDecoBatchAnalysisView.layout.scss`
- `ArtDecoBatchAnalysisView.controls.scss`
- `ArtDecoBatchAnalysisView.panels.scss`
- `ArtDecoBatchAnalysisView.charts.scss`
- `ArtDecoBatchAnalysisView.responsive.scss`

Role mapping:

- `layout`: root layout and feature layout shells.
- `controls`: section headers, header content, progress/results/report controls, and report action buttons.
- `panels`: progress dashboards, summary panels, report content, and insights panels.
- `charts`: task breakdown charts and results table/list data-display structures.
- `responsive`: existing responsive overrides, unchanged in role.

Old feature-style partials were removed from the import graph and deleted:

- `ArtDecoBatchAnalysisView.progress.scss`
- `ArtDecoBatchAnalysisView.results.scss`
- `ArtDecoBatchAnalysisView.report.scss`

`git grep` found no remaining references to those old partial imports under `web/frontend/src`.

## Line Count Impact

Measurement scope:
- Root: `web/frontend/src`
- Extension: `.scss`
- Threshold: `>500` lines
- Method: LF split count

Measured current line counts:
- `ArtDecoBatchAnalysisView.scss`: `6`
- `ArtDecoBatchAnalysisView.layout.scss`: `44`
- `ArtDecoBatchAnalysisView.controls.scss`: `179`
- `ArtDecoBatchAnalysisView.panels.scss`: `325`
- `ArtDecoBatchAnalysisView.charts.scss`: `263`
- `ArtDecoBatchAnalysisView.responsive.scss`: `113`

SCSS large-file metric after this change:
- SCSS files over 500 lines under `web/frontend/src`: `1`
- Advanced ArtDeco styles over 500 lines: `0`
- `ArtDecoBatchAnalysisView` no longer contributes to the SCSS D1.4 large-file violation list.

Historical context:
- The 2026-06-01 file-size guard report listed `ArtDecoBatchAnalysisView.scss` at `892` lines.
- Earlier facade splitting had already reduced the top-level file to a 6-line importer, but feature-style partials still carried large semantic clusters.
- This task completes the requested semantic split into layout / controls / panels / charts.

## Non-Goals Confirmed

- No Vue templates, scripts, props, emits, slots, or component public APIs changed.
- No route definitions, aliases, navigation truth, backend API contracts, OpenAPI/schema, or frontend API client changed.
- No runtime state, data fetching, computed logic, or layout behavior changed.
- No ArtDeco token definitions or token values changed.
- No global/shared component extraction was performed.
- No `/market/LHB.vue` header-shell migration was performed.
- No archive page/layout activation was performed.
- No unrelated dirty files were intentionally modified or staged.

## Validation

Passed:
- Function Tree scope-check: `14 changed file(s) within active authorization`
- Scoped `git diff --check` for authorized paths
- ArtDeco token checks for:
  - `src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.scss`
  - `src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.layout.scss`
  - `src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.controls.scss`
  - `src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.panels.scss`
  - `src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.charts.scss`
  - `src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.responsive.scss`
- `cd web/frontend && npm run build:no-types`
- Local `gitnexus detect-changes --scope staged --repo mystocks`: `9 files`, `0 symbols`, `0 affected processes`, `risk level: low`
- Local `gitnexus verify-staged --repo mystocks --json`: `ok: true`, index up-to-date, no stale staged diff

GitNexus notes:
- MCP impact could not resolve `ArtDecoBatchAnalysisView` for the SCSS facade/partials.
- Local final staged gate must be run with local `gitnexus analyze`, `gitnexus detect-changes --scope staged --repo mystocks`, and `gitnexus verify-staged --repo mystocks --json`.

Runtime status:
- `mystocks-backend`: online, `http://localhost:8020`
- `mystocks-frontend`: online, `http://localhost:3020`

Not run:
- `vue-tsc`: not run for this SCSS-only semantic split; no TypeScript or Vue script logic changed.
- E2E: not run for this SCSS-only semantic split; no route, API, layout registration, runtime interaction, or user workflow changed. The build and PM2 online checks cover structural runtime readiness for this batch.

## Quality Status

- Structural syntax errors introduced by this change: `0` based on successful `build:no-types`.
- Type inference errors introduced by this change: not applicable; no TS/Vue script logic changed and `vue-tsc` was not run.
- PM2 services: backend and frontend online at required local addresses.
- E2E status: not executed in this narrow SCSS-only batch; no fixed pass-count wording is claimed.

## Staging Policy

Only the authorized files for this node may be staged:

- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `.governance/programs/artdeco-web-design-governance/cards/artdeco-batch-analysis-view-scss-semantic-split.yaml`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.layout.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.progress.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.results.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.report.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.responsive.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.controls.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.panels.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoBatchAnalysisView.charts.scss`
- `docs/reports/tasks/2026-06-03-artdeco-batch-analysis-view-scss-semantic-split-report.md`

Do not stage `.governance/programs/artdeco-web-design-governance/tree.md`, `.planning/*`, route header migration files, `market/LHB.vue`, archive activation work, or any unrelated worktree changes.
