# TimeSeriesChart SCSS Style Split Report

Date: 2026-06-05

## Scope

- Split `web/frontend/src/components/artdeco/charts/styles/TimeSeriesChart.scss` into semantic SCSS partials.
- Preserved the original imported entry path used by `TimeSeriesChart.vue`.
- Did not change Vue, TypeScript, router, API, or runtime logic.

## Split Boundary

- `TimeSeriesChart.shell.scss`: chart root and card header shell styles.
- `TimeSeriesChart.header.scss`: chart header, title, subtitle, and title icon styles.
- `TimeSeriesChart.container.scss`: chart container, loading state, wrapper, and canvas.
- `TimeSeriesChart.empty-state.scss`: centered empty state icon, text, and hint.
- `TimeSeriesChart.tooltip.scss`: tooltip layout, value state colors, and change state colors.
- `TimeSeriesChart.legend.scss`: legend layout, legend color chips, labels, and stats.

The entry file keeps `@import '@/styles/artdeco-tokens';` and imports the partials in the same order as the original sections.

## GitNexus Note

`gitnexus impact TimeSeriesChart -r mystocks --depth 2 --summary-only` returned `not_found` with a stale index notice. Per the current session constraint, `gitnexus analyze` was not run for this batch. Scope was checked with Git and this batch is style-only SCSS.

## Verification

- SCSS content equivalence: old `TimeSeriesChart.scss` body equals concatenated new partials.
- Sass compile equivalence: old and new entries compile to identical CSS.
- CSS SHA-256: `891462ed06ba43284aa9374b49d8c1ef6d7d6f703ca4ed4d16a370810ecef760`.
- `git diff --check`: passed.
- ArtDeco token validation: passed.
- Focused tests: no matching `TimeSeriesChart` spec/test files found.

