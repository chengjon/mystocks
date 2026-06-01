# ArtDeco Dashboard SCSS Style Split Report

> Date: 2026-06-01
> Function Tree node: `artdeco-web-design-governance/artdeco-dashboard-scss-style-split`
> Scope: `web/frontend/src/views/artdeco-pages/styles/ArtDecoDashboard*.scss`

## Summary

This task split the oversized `ArtDecoDashboard.scss` file into visual-concern partials while preserving the existing dashboard style body exactly.

The change is a mechanical SCSS organization cleanup only. It does not change dashboard Vue code, route registration, API orchestration, backend API contracts, OpenAPI, frontend API clients, shared components, global tokens, or runtime state logic.

## Files Updated

- `web/frontend/src/views/artdeco-pages/styles/ArtDecoDashboard.scss`
- `web/frontend/src/views/artdeco-pages/styles/ArtDecoDashboard.layout.scss`
- `web/frontend/src/views/artdeco-pages/styles/ArtDecoDashboard.market.scss`
- `web/frontend/src/views/artdeco-pages/styles/ArtDecoDashboard.pool-nav.scss`
- `web/frontend/src/views/artdeco-pages/styles/ArtDecoDashboard.monitoring.scss`
- `web/frontend/src/views/artdeco-pages/styles/ArtDecoDashboard.rhythm.scss`

## Split Result

| File | Lines | Disallowed `px` |
| --- | ---: | ---: |
| `ArtDecoDashboard.scss` | 9 | 0 |
| `ArtDecoDashboard.layout.scss` | 166 | 0 |
| `ArtDecoDashboard.market.scss` | 180 | 0 |
| `ArtDecoDashboard.pool-nav.scss` | 163 | 0 |
| `ArtDecoDashboard.monitoring.scss` | 134 | 0 |
| `ArtDecoDashboard.rhythm.scss` | 243 | 0 |

Original file size: 885 lines.

Largest partial after split: 243 lines.

## Reconstruction Check

The partials reconstruct the original post-`@use` style body exactly:

```text
body_match: true
```

The facade keeps the original quant extension module and imports the partials:

```scss
@use '@/styles/artdeco-quant-extended.scss' as *;

@import './ArtDecoDashboard.layout';
@import './ArtDecoDashboard.market';
@import './ArtDecoDashboard.pool-nav';
@import './ArtDecoDashboard.monitoring';
@import './ArtDecoDashboard.rhythm';
```

The import paths are quoted because Sass expects string import targets after `@use`.

## Validation

- Focused ArtDeco token check:

  ```text
  ArtDeco Token Validation Passed.
  ```

- Frontend structure build:

  ```text
  npm run build:no-types
  ✓ built in 30.74s
  ```

## Compatibility Boundaries

- No router definitions changed.
- No backend API handlers, schemas, OpenAPI contracts, or frontend API clients changed.
- No Vue or TypeScript runtime code changed.
- No shared component extraction was performed.
- No global token, baseline, or ArtDeco design-system source file changed.
- No token cleanup was needed because the source file already had zero disallowed hardcoded `px` literals.

## Follow-Up

Continue the file-size guard sequence with the next route-local or style-local SCSS file that can be split without changing route/API/client contracts. Current high-priority candidates after this batch include:

- `web/frontend/src/views/artdeco-pages/styles/ArtDecoSettings.scss`
- `web/frontend/src/views/strategy/styles/BacktestGPU.scss`
- selected global style files only after explicit approval because they have broader blast radius.
