# HeatmapCard SCSS Style Split Report

## Scope

- Target: `web/frontend/src/components/artdeco/charts/styles/HeatmapCard.scss`
- Consumer: `web/frontend/src/components/artdeco/charts/HeatmapCard.vue`
- Change type: style-structure refactor only

## Split Boundary

- `HeatmapCard.shell.scss`: card root, header, title, controls, and sort select.
- `HeatmapCard.grid.scss`: grid layout, heatmap cells, symbol/change text, and volume bar.
- `HeatmapCard.list.scss`: list view, list headers, list rows, and symbol cell emphasis.
- `HeatmapCard.overlays.scss`: legend and fixed tooltip styling.
- `HeatmapCard.state-responsive.scss`: loading/empty states, spinner keyframe, responsive rules, and performance note.

## Notes

- The original imported entry path is retained.
- The consumer Vue file is intentionally unchanged.
- The entry keeps the file's existing Sass import style because the file depends on mixins from `@/styles/data-dense/index`.
- GitNexus impact lookup for `HeatmapCard` returned `not_found`; this change only edits SCSS selectors and does not modify Vue/TS symbols.

## Verification

- Partial content equivalence: each partial exactly matches the corresponding original line range.
- Sass CSS equivalence: old `HEAD` entry and new entry compile to identical CSS (`9274` bytes each).
- `git diff --check -- <changed files>`: passed.
- `node scripts/check-artdeco-tokens.js --target-file ...`: passed for the entry and all new partials.
- Focused component test: not run; no `HeatmapCard` focused spec/test file exists in `web/frontend/src`, `web/frontend/tests`, or `tests`.
