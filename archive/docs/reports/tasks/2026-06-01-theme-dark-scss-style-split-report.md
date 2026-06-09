# Theme Dark SCSS Style Split Report

Date: 2026-06-01

Function Tree node: `artdeco-web-design-governance/theme-dark-scss-style-split`

## Summary

This task split the oversized global `theme-dark.scss` file into visual-concern partials while preserving the existing post-header style body exactly.

The change is a mechanical SCSS organization cleanup only. It does not change Vue, TypeScript, runtime logic, router registration, backend API contracts, OpenAPI, frontend API clients, shared components, token values, or design-system baselines.

## Files Updated

- `web/frontend/src/styles/theme-dark.scss`
- `web/frontend/src/styles/theme-dark.variables.scss`
- `web/frontend/src/styles/theme-dark.components.scss`
- `web/frontend/src/styles/theme-dark.utilities.scss`
- `web/frontend/src/styles/theme-dark.element-plus.scss`
- `web/frontend/src/styles/theme-dark.media-motion-debug.scss`

## Split Result

| File | Lines | Existing hardcoded `px` literals |
| --- | ---: | ---: |
| `theme-dark.scss` | 20 | 0 |
| `theme-dark.variables.scss` | 238 | 24 |
| `theme-dark.components.scss` | 115 | 4 |
| `theme-dark.utilities.scss` | 34 | 0 |
| `theme-dark.element-plus.scss` | 108 | 4 |
| `theme-dark.media-motion-debug.scss` | 263 | 17 |

Original file size: 773 lines.

Largest partial after split: 263 lines.

## Reconstruction Check

The partials reconstruct the original post-header style body exactly:

```text
body_match: true
raw_match: true
```

The facade keeps the original file header and imports the partials:

```scss
@import './theme-dark.variables';
@import './theme-dark.components';
@import './theme-dark.utilities';
@import './theme-dark.element-plus';
@import './theme-dark.media-motion-debug';
```

## Validation

- Function Tree scope check:

  ```text
  scope-check: 11 changed file(s) within active authorization
  ```

- Focused whitespace check:

  ```text
  git diff --check -- web/frontend/src/styles/theme-dark*.scss
  pass
  ```

- Frontend structure build:

  ```text
  npm run build:no-types
  ✓ built in 27.09s
  ```

## Token Debt Observation

The source file already had hardcoded spacing and color literals before this task. A focused ArtDeco token check on the original `theme-dark.scss` failed on existing literals, so token cleanup was intentionally excluded from this mechanical split node.

This node preserves those values and relocates them into partials without semantic changes. Tokenization should be handled by a separate approval gate because `theme-dark.scss` is a global theme layer with broad visual blast radius.

## Compatibility Boundaries

- No router definitions changed.
- No backend API handlers, schemas, OpenAPI contracts, or frontend API clients changed.
- No Vue or TypeScript source changed.
- No shared component extraction was performed.
- No global token values or ArtDeco baseline files changed.
- Existing dirty files and generated `tree.md` were intentionally left unstaged.

## Follow-Up

- Continue global-style cleanup only in separately authorized nodes.
- Recommended next candidates, in order of risk containment:
  - `theme-apply.scss` facade split.
  - `visual-optimization.scss` facade split.
  - `element-plus-override.scss` facade split.
- Token cleanup for `theme-dark.scss` should be a separate node after reviewing whether legacy CSS variables should map to `artdeco-tokens.scss` or remain as compatibility aliases.
