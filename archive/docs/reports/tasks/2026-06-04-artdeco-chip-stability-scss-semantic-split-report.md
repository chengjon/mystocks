# ArtDecoChipDistribution Stability SCSS Semantic Split Report

Date: 2026-06-04

## Scope

- Facade: `web/frontend/src/components/artdeco/advanced/styles/ArtDecoChipDistribution.stability.scss`
- Change type: ArtDeco SCSS file-size governance and semantic partial split.

## User Constraints

- Continue the established SCSS governance route.
- Reuse the semantic split pattern from the prior ArtDeco SCSS governance commits.
- Keep route header migration unchanged:
  - `/market/technical` remains the only allowed header-shell migration line.
  - `market/LHB.vue` remains pending and was not touched.
- Archive-related work remains style slimming only:
  - Do not enable archive pages or archive layouts online.
  - Do not extract global shared components.
- Keep existing dirty files isolated and unstaged.

## Split Map

Before this task, `ArtDecoChipDistribution.stability.scss` contained all chip stability analysis styles in one file.

After this task, the facade imports semantic partials:

- `ArtDecoChipDistribution.stability-section.scss`
- `ArtDecoChipDistribution.stability-metrics.scss`
- `ArtDecoChipDistribution.stability-timeline.scss`
- `ArtDecoChipDistribution.stability-insights.scss`

Role mapping:

- `stability-section`: section wrapper and header presentation.
- `stability-metrics`: stability metric grid and metric cards.
- `stability-timeline`: timeline heading, chart shell, axis labels, line, and points.
- `stability-insights`: stability insight heading, insight list, and insight cards.

## Line Count Impact

Measured current line counts:

- `ArtDecoChipDistribution.stability.scss`: `5`
- `ArtDecoChipDistribution.stability-section.scss`: `52`
- `ArtDecoChipDistribution.stability-metrics.scss`: `56`
- `ArtDecoChipDistribution.stability-timeline.scss`: `88`
- `ArtDecoChipDistribution.stability-insights.scss`: `78`

The former `ArtDecoChipDistribution.stability.scss` body was reduced from a single 264-line file to a 5-line importer.

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

- Import existence check for all `ArtDecoChipDistribution.stability.scss` partial imports.
- SCSS brace-balance check for all new partial files.
- Scoped `git diff --check`.
- Scoped `npx stylelint` for the changed chip stability SCSS files.
- `cd web/frontend && npm run build:no-types`.
- PM2 service status confirmation:
  - `mystocks-backend`: online, `http://localhost:8020`
  - `mystocks-frontend`: online, `http://localhost:3020`
- GitNexus staged detect-changes:
  - Changed files: `6`
  - Changed symbols: `0`
  - Affected processes: `0`
  - Risk level: `low`
  - File classes: `style=5`, `documentation=1`
  - Note: GitNexus reported the index as stale relative to current `HEAD`; result still showed no indexed symbol/process impact for the staged SCSS/doc-only diff.

Pending:

- None for this scoped split.

Not run:

- `vue-tsc --noEmit`: not run for this SCSS-only semantic split; no TypeScript or Vue script logic changed.
- E2E: not run for this SCSS-only semantic split; no route, API, layout registration, runtime interaction, or user workflow changed.

## Quality Status

- Structural syntax errors: `0` observed in scoped `stylelint`, scoped `git diff --check`, and `npm run build:no-types`.
- Type inference errors: not evaluated in this SCSS-only batch; no TypeScript/Vue script files changed, so no new type-inference surface was introduced.
- PM2 service status:
  - `mystocks-backend`: online, `http://localhost:8020`
  - `mystocks-frontend`: online, `http://localhost:3020`
- E2E status: not executed for this scoped SCSS semantic split. No fixed historical pass-count wording is used.
