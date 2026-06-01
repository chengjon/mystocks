# StockDetail SCSS Style Split Report

> Date: 2026-06-01
> Function Tree node: `artdeco-web-design-governance/stock-detail-scss-style-split`
> Scope: `web/frontend/src/views/styles/StockDetail*.scss`

## Summary

This task split the oversized `StockDetail.scss` file into visual-concern partials while preserving the existing `.stock-detail` inner style body exactly.

`BacktestGPU.scss` was skipped for this batch because `BacktestGPU.vue`, `useBacktestGPU.ts`, and `BacktestGPU.scss` already had unrelated uncommitted work in the shared worktree. To avoid mixing runtime/page edits with mechanical style governance, this batch used the next clean route-local SCSS candidate.

The change is a mechanical SCSS organization cleanup only. It does not change `StockDetail.vue`, route registration, API orchestration, backend API contracts, OpenAPI, frontend API clients, shared components, global tokens, or runtime state logic.

## Files Updated

- `web/frontend/src/views/styles/StockDetail.scss`
- `web/frontend/src/views/styles/StockDetail.layout.scss`
- `web/frontend/src/views/styles/StockDetail.cards.scss`
- `web/frontend/src/views/styles/StockDetail.controls.scss`
- `web/frontend/src/views/styles/StockDetail.sections.scss`
- `web/frontend/src/views/styles/StockDetail.forms.scss`

## Split Result

| File | Lines | Disallowed `px` |
| --- | ---: | ---: |
| `StockDetail.scss` | 9 | 0 |
| `StockDetail.layout.scss` | 134 | 0 |
| `StockDetail.cards.scss` | 154 | 0 |
| `StockDetail.controls.scss` | 60 | 0 |
| `StockDetail.sections.scss` | 84 | 0 |
| `StockDetail.forms.scss` | 92 | 0 |

Original file size: 522 lines.

Largest partial after split: 154 lines.

## Reconstruction Check

The partials reconstruct the original `.stock-detail` inner body exactly:

```text
inner_body_match: true
```

The facade preserves the original root selector and imports the partials inside it:

```scss
.stock-detail {
  @import './StockDetail.layout';
  @import './StockDetail.cards';
  @import './StockDetail.controls';
  @import './StockDetail.sections';
  @import './StockDetail.forms';
}
```

This keeps the generated selector context aligned with the original single-root SCSS file.

## Validation

- Focused ArtDeco token check:

  ```text
  ArtDeco Token Validation Passed.
  ```

- Frontend structure build:

  ```text
  npm run build:no-types
  ✓ built in 29.92s
  ```

## Compatibility Boundaries

- No router definitions changed.
- No backend API handlers, schemas, OpenAPI contracts, or frontend API clients changed.
- No Vue or TypeScript runtime code changed.
- No shared component extraction was performed.
- No global token, baseline, or ArtDeco design-system source file changed.
- No token cleanup was needed because the source file already had zero disallowed hardcoded `px` literals.
- Existing dirty `StockDetail.vue`, `BacktestGPU.vue`, `useBacktestGPU.ts`, `BacktestGPU.scss`, `Architecture.vue`, and generated `tree.md` were intentionally left unstaged.

## Follow-Up

Continue the file-size guard sequence with clean route-local or style-local SCSS first. Candidates:

- `web/frontend/src/views/system/styles/Architecture.scss`
- `web/frontend/src/views/strategy/styles/BacktestGPU.scss` only after the current unrelated dirty edits are committed, stashed, or explicitly included in a separate approved scope

Global style files such as `theme-dark.scss`, `theme-apply.scss`, `artdeco-tokens.scss`, and Element Plus overrides should stay behind a separate approval gate because their blast radius is broader.
