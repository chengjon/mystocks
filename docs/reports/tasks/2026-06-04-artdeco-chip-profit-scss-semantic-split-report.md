# ArtDecoChipDistribution Profit SCSS Semantic Split Report

Date: 2026-06-04

## Scope

- Facade: `web/frontend/src/components/artdeco/advanced/styles/ArtDecoChipDistribution.profit.scss`
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

Before this task, `ArtDecoChipDistribution.profit.scss` contained all chip profit analysis styles in one file.

After this task, the facade imports semantic partials:

- `ArtDecoChipDistribution.profit-section.scss`
- `ArtDecoChipDistribution.profit-metrics.scss`
- `ArtDecoChipDistribution.profit-bars.scss`
- `ArtDecoChipDistribution.profit-distribution.scss`

Role mapping:

- `profit-section`: section wrapper and header presentation.
- `profit-metrics`: profit metrics grid, metric cards, and gauge visualization.
- `profit-bars`: horizontal profit bar rows inside metric charts.
- `profit-distribution`: profit distribution zones, range/count/percentage metadata, and zone fills.

## Line Count Impact

Measured current line counts:

- `ArtDecoChipDistribution.profit.scss`: `5`
- `ArtDecoChipDistribution.profit-section.scss`: `52`
- `ArtDecoChipDistribution.profit-metrics.scss`: `107`
- `ArtDecoChipDistribution.profit-bars.scss`: `60`
- `ArtDecoChipDistribution.profit-distribution.scss`: `103`

The former `ArtDecoChipDistribution.profit.scss` body was reduced from a single 304-line file to a 5-line importer.

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

- Import existence check for all `ArtDecoChipDistribution.profit.scss` partial imports.
- SCSS brace-balance check for all new partial files.
- Scoped `git diff --check`.
- Scoped `npx stylelint` for the changed chip-profit SCSS files.
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
