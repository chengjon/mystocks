# DrawdownChart SCSS Style Split Report

Date: 2026-06-05

## Scope

- Split `web/frontend/src/components/artdeco/charts/styles/DrawdownChart.scss` into semantic SCSS partials.
- Preserved the original imported entry path used by `DrawdownChart.vue`.
- Did not change Vue, TypeScript, router, API, or runtime logic.

## Split Boundary

- `DrawdownChart.shell.scss`: chart root and card header shell styles.
- `DrawdownChart.header.scss`: chart header, title, subtitle, and stat severity states.
- `DrawdownChart.container.scss`: chart container, loading state, wrapper, and canvas.
- `DrawdownChart.empty-state.scss`: centered empty state icon, text, and hint.
- `DrawdownChart.tooltip.scss`: tooltip layout, drawdown severity values, and recovery values.
- `DrawdownChart.legend.scss`: legend layout, legend colors, and legend labels.

The entry file keeps `@import '@/styles/artdeco-tokens';` and imports the partials in the same order as the original sections.

## GitNexus Note

`gitnexus impact DrawdownChart -r mystocks --depth 2 --summary-only` returned `not_found` with a stale index notice. Per the current session constraint, `gitnexus analyze` was not run for this batch. Scope was checked with Git and this batch is style-only SCSS.

## Verification

- SCSS content equivalence: old `DrawdownChart.scss` body equals concatenated new partials.
- Sass compile equivalence: old and new entries compile to identical CSS.
- CSS SHA-256: `4a21b570bef2400ce75882c922c444c1d47f4433c91a5ad6c3e838fb3a962e47`.
- `git diff --check`: passed.
- ArtDeco token validation: passed.
- Focused tests: no matching `DrawdownChart` spec/test files found.

