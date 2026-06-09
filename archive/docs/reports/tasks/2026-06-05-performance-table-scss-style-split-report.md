# PerformanceTable SCSS Style Split Report

## Scope

- Target: `web/frontend/src/components/artdeco/charts/styles/PerformanceTable.scss`
- Consumer: `web/frontend/src/components/artdeco/charts/PerformanceTable.vue`
- Change type: style-structure refactor only

## Split Boundary

- `PerformanceTable.shell.scss`: root table surface, table card header reset, header controls, container, and empty state.
- `PerformanceTable.table.scss`: Element Plus table wrappers, strategy name cell, metric values, value colors, rating classes, drawdown classes, and row actions.
- `PerformanceTable.pagination.scss`: pagination wrapper and Element Plus pagination styling.
- `PerformanceTable.footer.scss`: summary footer, stat labels, and stat value color states.

## Notes

- The original imported entry path is retained.
- The consumer Vue file is intentionally unchanged.
- The entry keeps the file's existing Sass import style to avoid introducing unrelated `@use` migration semantics.
- GitNexus impact lookup for `PerformanceTable` returned `not_found`; this change only edits SCSS selectors and does not modify Vue/TS symbols.

## Verification

- Partial content equivalence: each partial exactly matches the corresponding original line range.
- Sass CSS equivalence: old `HEAD` entry and new entry compile to identical CSS (`20615` bytes each).
- `git diff --check -- <changed files>`: passed.
- `node scripts/check-artdeco-tokens.js --target-file ...`: passed for the entry and all new partials.
- Focused component test: not run; no `PerformanceTable` focused spec/test file exists in `web/frontend/src`, `web/frontend/tests`, or `tests`.
