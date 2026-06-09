# ArtDeco Settings SCSS Style Split Report

> Date: 2026-06-01
> Function Tree node: `artdeco-web-design-governance/artdeco-settings-scss-style-split`
> Scope: `web/frontend/src/views/artdeco-pages/styles/ArtDecoSettings*.scss`

## Summary

This task split the oversized `ArtDecoSettings.scss` file into visual-concern partials while preserving the existing settings style body exactly.

The change is a mechanical SCSS organization cleanup only. It does not change settings Vue code, route registration, API orchestration, backend API contracts, OpenAPI, frontend API clients, shared components, global tokens, or runtime state logic.

## Files Updated

- `web/frontend/src/views/artdeco-pages/styles/ArtDecoSettings.scss`
- `web/frontend/src/views/artdeco-pages/styles/ArtDecoSettings.shell.scss`
- `web/frontend/src/views/artdeco-pages/styles/ArtDecoSettings.settings-data.scss`
- `web/frontend/src/views/artdeco-pages/styles/ArtDecoSettings.notifications.scss`
- `web/frontend/src/views/artdeco-pages/styles/ArtDecoSettings.system.scss`
- `web/frontend/src/views/artdeco-pages/styles/ArtDecoSettings.responsive.scss`

## Split Result

| File | Lines | Disallowed `px` |
| --- | ---: | ---: |
| `ArtDecoSettings.scss` | 6 | 0 |
| `ArtDecoSettings.shell.scss` | 212 | 0 |
| `ArtDecoSettings.settings-data.scss` | 188 | 0 |
| `ArtDecoSettings.notifications.scss` | 119 | 0 |
| `ArtDecoSettings.system.scss` | 156 | 0 |
| `ArtDecoSettings.responsive.scss` | 86 | 0 |

Original file size: 757 lines.

Largest partial after split: 212 lines.

## Reconstruction Check

The partials reconstruct the original style body exactly:

```text
body_match: true
```

The facade imports the partials:

```scss
@import './ArtDecoSettings.shell';
@import './ArtDecoSettings.settings-data';
@import './ArtDecoSettings.notifications';
@import './ArtDecoSettings.system';
@import './ArtDecoSettings.responsive';
```

## Validation

- Focused ArtDeco token check:

  ```text
  ArtDeco Token Validation Passed.
  ```

- Frontend structure build:

  ```text
  npm run build:no-types
  ✓ built in 29.46s
  ```

## Compatibility Boundaries

- No router definitions changed.
- No backend API handlers, schemas, OpenAPI contracts, or frontend API clients changed.
- No Vue or TypeScript runtime code changed.
- No shared component extraction was performed.
- No global token, baseline, or ArtDeco design-system source file changed.
- No token cleanup was needed because the source file already had zero disallowed hardcoded `px` literals.

## Follow-Up

Continue the file-size guard sequence with route-local or style-local SCSS before touching global style files. Current lower-risk candidates include:

- `web/frontend/src/views/strategy/styles/BacktestGPU.scss`
- `web/frontend/src/views/styles/StockDetail.scss`
- `web/frontend/src/views/system/styles/Architecture.scss`

Global files such as `theme-dark.scss`, `theme-apply.scss`, `artdeco-tokens.scss`, and Element Plus overrides should stay behind a separate approval gate because their blast radius is broader.
