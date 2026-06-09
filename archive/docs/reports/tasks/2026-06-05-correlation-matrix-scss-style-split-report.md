# CorrelationMatrix SCSS Style Split Report

## Scope

- Target: `web/frontend/src/components/artdeco/charts/styles/CorrelationMatrix.scss`
- Consumer: `web/frontend/src/components/artdeco/charts/CorrelationMatrix.vue`
- Change type: style-structure refactor only

## Split Boundary

- `CorrelationMatrix.shell.scss`: root matrix surface, matrix header, container state, and empty state.
- `CorrelationMatrix.matrix.scss`: scroll wrapper, row headers, column headers, rows, cells, and intensity states.
- `CorrelationMatrix.tooltip.scss`: fixed tooltip, symbol pair display, correlation value, and interpretation text.
- `CorrelationMatrix.legend.scss`: legend title, gradient bar, and legend labels.

## Notes

- The original imported entry path is retained.
- The consumer Vue file is intentionally unchanged.
- The entry keeps the file's existing Sass import style to avoid introducing unrelated `@use` migration semantics.
- GitNexus impact lookup for `CorrelationMatrix` returned `not_found`; this change only edits SCSS selectors and does not modify Vue/TS symbols.

## Verification

- Partial content equivalence: each partial exactly matches the corresponding original line range.
- Sass CSS equivalence: old `HEAD` entry and new entry compile to identical CSS (`22981` bytes each).
- `git diff --check -- <changed files>`: passed.
- `node scripts/check-artdeco-tokens.js --target-file ...`: passed for the entry and all new partials.
- Focused component test: not run; no `CorrelationMatrix` focused spec/test file exists in `web/frontend/src`, `web/frontend/tests`, or `tests`.
