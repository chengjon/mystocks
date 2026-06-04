# ArtDecoTradingManagement SCSS Style Split Report

## Scope

- Target: `web/frontend/src/views/artdeco-pages/styles/ArtDecoTradingManagement.scss`
- Consumer: `web/frontend/src/views/artdeco-pages/ArtDecoTradingManagement.vue`
- Change type: style-structure refactor only

## Split Boundary

- `ArtDecoTradingManagement.shell.scss`: page root, shared shell, hero, tabs shell, stats strip, content shell.
- `ArtDecoTradingManagement.cards.scss`: content grid, overview/control/realtime/history card surfaces.
- `ArtDecoTradingManagement.controls.scss`: card header, header icon/content/actions, main tab controls.
- `ArtDecoTradingManagement.panels.scss`: tab content, panel grid, panel section, history spacing.
- `ArtDecoTradingManagement.responsive.scss`: pulse animation and responsive layout rules.

## Notes

- The original imported entry path is retained.
- The consumer Vue file is intentionally unchanged.
- Sass partial imports use `as *` because the multi-part filenames otherwise resolve to the same default namespace.

## Verification

- Partial content equivalence: each partial exactly matches the corresponding original line range.
- Sass CSS equivalence: old snapshot and new entry compile to identical CSS (`28787` bytes each).
- `git diff --check -- <changed files>`: passed.
- `node scripts/check-artdeco-tokens.js --target-file ...`: passed for the entry and all new partials.
- `npm run test -- src/views/artdeco-pages/__tests__/ArtDecoTradingManagement.spec.ts`: passed (`1` file, `1` test).
