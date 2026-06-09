# ArtDecoTable SCSS Style Split Report

Date: 2026-06-05

## Scope

- Split `web/frontend/src/components/artdeco/trading/styles/ArtDecoTable.scss` into semantic SCSS partials.
- Replaced three moved hardcoded spacing literals with equivalent ArtDeco spacing token expressions required by the local token gate.
- Preserved the original imported entry path used by `ArtDecoTable.vue`.
- Did not change Vue, TypeScript, router, API, or runtime logic.

## Split Boundary

- `ArtDecoTable.shell.scss`: table shell, mode variants, title/action layout, container, table head base.
- `ArtDecoTable.header.scss`: header cell and sortable header interaction styles.
- `ArtDecoTable.cells.scss`: body cells, financial color states, rows, row actions, pagination.
- `ArtDecoTable.states.scss`: loading, empty state, spinner animation, performance marker.
- `ArtDecoTable.sizes-responsive.scss`: compact/comfortable/spacious variants and responsive layout.

The entry file keeps `@import '@/styles/data-dense/index';` because the moved rules depend on Sass mixins from the data-dense style bundle.

## GitNexus Note

`gitnexus impact ArtDecoTable -r mystocks --depth 2 --summary-only` returned `not_found` while the GitNexus index was stale. The local `gitnexus analyze` path was not rerun in this batch because earlier attempts failed during index rebuild, and `gitnexus verify-staged` previously hung. Scope was checked with Git and this batch is style-only SCSS.

## Token Normalization

- `height: 36px` became `height: calc(var(--artdeco-spacing-8) + var(--artdeco-spacing-1))`.
- `box-shadow: inset 2px 0 0 ...` became `box-shadow: inset calc(var(--artdeco-spacing-1) / 2) 0 0 ...`.
- `height: 32px` became `height: var(--artdeco-spacing-8)`.

## Verification

- Split equivalence before token normalization: old `ArtDecoTable.scss` body equals concatenated new partials.
- Final SCSS body delta after token normalization: only the three spacing-token declarations listed above.
- Sass compile: old entry and final new entry both compile successfully.
- Final CSS SHA-256 old/new:
  - old: `4839030a01e049364b0f7741660d91153c58841a9aa767bdda5cdf05660ff6cd`
  - new: `55073eb6c7a4a492baa97941fd7a203d1ce76c4fce890f89ee5176fba0d7f4cf`
- `git diff --check`: passed.
- ArtDeco token validation: passed.
- Focused tests: no matching `ArtDecoTable` spec/test files found.
