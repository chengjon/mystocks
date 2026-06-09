# ArtDeco Capital Flow SCSS Token Cleanup Report

> Date: 2026-06-01
> Function Tree node: `artdeco-web-design-governance/artdeco-scss-capital-flow-token-cleanup`
> Scope: `web/frontend/src/components/artdeco/advanced/styles/ArtDecoCapitalFlow.*.scss` partials only

## Summary

This task cleaned the hardcoded spacing and dimension literals left after the `ArtDecoCapitalFlow` SCSS split. The work preserves the existing visual geometry while binding fixed values to ArtDeco spacing/radius tokens or local `--capital-flow-*` variables derived from those tokens.

No Vue, TypeScript, router, backend API contract, OpenAPI, frontend API client, shared component, route shell, or global token file was changed.

## Files Updated

- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoCapitalFlow.layout.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoCapitalFlow.heatmap.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoCapitalFlow.clustering.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoCapitalFlow.control.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoCapitalFlow.opportunity.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoCapitalFlow.responsive.scss`

## Tokenization Result

Before cleanup, the six partials contained 83 disallowed hardcoded `px` literals:

| File | Disallowed `px` Before | Disallowed `px` After |
| --- | ---: | ---: |
| `ArtDecoCapitalFlow.layout.scss` | 1 | 0 |
| `ArtDecoCapitalFlow.heatmap.scss` | 20 | 0 |
| `ArtDecoCapitalFlow.clustering.scss` | 20 | 0 |
| `ArtDecoCapitalFlow.control.scss` | 19 | 0 |
| `ArtDecoCapitalFlow.opportunity.scss` | 22 | 0 |
| `ArtDecoCapitalFlow.responsive.scss` | 1 | 0 |
| **Total** | **83** | **0** |

The cleanup introduced local custom properties on `.artdeco-capital-flow`, including:

- `--capital-flow-section-icon-size`
- `--capital-flow-section-icon-glyph-size`
- `--capital-flow-card-min-width`
- `--capital-flow-heatmap-height`
- `--capital-flow-chart-min-width`
- `--capital-flow-chart-height`
- `--capital-flow-control-height`
- `--capital-flow-opportunity-min-width`
- `--capital-flow-glow-radius`

The legacy responsive breakpoint changed from `768px` to the equivalent `48rem` because CSS custom properties cannot be used reliably inside media query conditions.

## Validation

- Focused ArtDeco token check:

  ```text
  ArtDeco Token Validation Passed.
  ```

- Frontend structure build:

  ```text
  npm run build:no-types
  ✓ built in 27.68s
  ```

## Compatibility Boundaries

This was a style-token cleanup only.

- Router definitions were not modified.
- Backend API handlers, schemas, OpenAPI contracts, and frontend API clients were not modified.
- No component extraction was performed.
- No global ArtDeco token or baseline file was modified.
- Existing `1px` border literals remain allowed by the current `check-artdeco-tokens.js` allow-list where they already existed.

## Follow-Up

Continue the SCSS governance sequence with the next oversized ArtDeco advanced style file. Each file should keep the same two-step pattern:

1. Split oversized SCSS into exact-reconstruction partials.
2. Run a separate token cleanup node that reduces disallowed hardcoded dimensions to zero.
