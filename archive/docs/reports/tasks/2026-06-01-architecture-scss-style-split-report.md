# Architecture SCSS Style Split Report

> Date: 2026-06-01
> Function Tree node: `artdeco-web-design-governance/architecture-scss-style-split`
> Scope: `web/frontend/src/views/system/styles/Architecture*.scss`

## Summary

This task split the oversized `Architecture.scss` file into visual-concern partials while preserving the existing post-`@use` style body exactly.

The change is a mechanical SCSS organization cleanup only. It does not change `Architecture.vue`, route registration, API orchestration, backend API contracts, OpenAPI, frontend API clients, shared components, global tokens, or runtime state logic.

`Architecture.vue` and `web/frontend/src/views/system/__tests__/Architecture.spec.ts` already had unrelated worktree changes before this task and were intentionally left unstaged.

## Files Updated

- `web/frontend/src/views/system/styles/Architecture.scss`
- `web/frontend/src/views/system/styles/Architecture.layout.scss`
- `web/frontend/src/views/system/styles/Architecture.cards.scss`
- `web/frontend/src/views/system/styles/Architecture.databases.scss`
- `web/frontend/src/views/system/styles/Architecture.routing.scss`
- `web/frontend/src/views/system/styles/Architecture.tech-responsive.scss`

## Split Result

| File | Lines | Disallowed `px` |
| --- | ---: | ---: |
| `Architecture.scss` | 7 | 0 |
| `Architecture.layout.scss` | 97 | 0 |
| `Architecture.cards.scss` | 112 | 0 |
| `Architecture.databases.scss` | 99 | 0 |
| `Architecture.routing.scss` | 117 | 0 |
| `Architecture.tech-responsive.scss` | 73 | 0 |

Original file size: 501 lines.

Largest partial after split: 117 lines.

## Reconstruction Check

The partials reconstruct the original post-`@use` style body exactly:

```text
body_match: true
raw_match: true
```

The facade keeps the original token module and imports the partials:

```scss
@use '../../../styles/artdeco-tokens.scss' as *;

@import './Architecture.layout';
@import './Architecture.cards';
@import './Architecture.databases';
@import './Architecture.routing';
@import './Architecture.tech-responsive';
```

## Validation

- Focused ArtDeco token check:

  ```text
  ArtDeco Token Validation Passed.
  ```

- Frontend structure build:

  ```text
  npm run build:no-types
  ✓ built in 45.42s
  ```

## Compatibility Boundaries

- No router definitions changed.
- No backend API handlers, schemas, OpenAPI contracts, or frontend API clients changed.
- No Vue or TypeScript runtime code changed.
- No shared component extraction was performed.
- No global token, baseline, or ArtDeco design-system source file changed.
- No token cleanup was needed because the source file already had zero disallowed hardcoded `px` literals.
- Existing dirty `Architecture.vue`, `Architecture.spec.ts`, `BacktestGPU*`, `StockDetail.vue`, `docs/api/ArtDeco_System_Architecture_Summary.md`, and generated `tree.md` were intentionally left unstaged.

## Follow-Up

The remaining SCSS file-size guard work should split into two tracks:

- Route-local/style-local files when their corresponding Vue/TS files are clean.
- Global style files only under a separate approval gate because `theme-dark.scss`, `theme-apply.scss`, `artdeco-tokens.scss`, Element Plus overrides, and related global style layers have broader blast radius.
