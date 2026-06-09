# Theme Apply SCSS Style Split Report

Date: 2026-06-01

Function Tree node: `artdeco-web-design-governance/theme-apply-scss-style-split`

## Summary

This task split the oversized global `theme-apply.scss` file into visual-concern partials while preserving the existing post-header style body exactly.

The change is a mechanical SCSS organization cleanup only. It does not change Vue, TypeScript, runtime logic, router registration, backend API contracts, OpenAPI, frontend API clients, shared components, token values, or design-system baselines.

## Files Updated

- `web/frontend/src/styles/theme-apply.scss`
- `web/frontend/src/styles/theme-apply.base-market.scss`
- `web/frontend/src/styles/theme-apply.element-plus.scss`
- `web/frontend/src/styles/theme-apply.routes.scss`
- `web/frontend/src/styles/theme-apply.surfaces-utilities.scss`
- `web/frontend/src/styles/theme-apply.motion-media-print.scss`

## Split Result

| File | Lines | Existing hardcoded `px` literals |
| --- | ---: | ---: |
| `theme-apply.scss` | 21 | 0 |
| `theme-apply.base-market.scss` | 69 | 0 |
| `theme-apply.element-plus.scss` | 351 | 10 |
| `theme-apply.routes.scss` | 88 | 3 |
| `theme-apply.surfaces-utilities.scss` | 88 | 3 |
| `theme-apply.motion-media-print.scss` | 76 | 3 |

Original file size: 688 lines.

Largest partial after split: 351 lines.

## Reconstruction Check

The partials reconstruct the original post-header style body exactly:

```text
body_match: true
raw_match: true
```

The facade keeps the original file header and imports the partials:

```scss
@import './theme-apply.base-market';
@import './theme-apply.element-plus';
@import './theme-apply.routes';
@import './theme-apply.surfaces-utilities';
@import './theme-apply.motion-media-print';
```

## Validation

- Function Tree scope check:

  ```text
  scope-check: 11 changed file(s) within active authorization
  ```

- Focused whitespace check:

  ```text
  git diff --check -- web/frontend/src/styles/theme-apply*.scss
  pass
  ```

- Frontend structure build:

  ```text
  npm run build:no-types
  ✓ built in 1m 4s
  ```

## Token Debt Observation

The source file already had hardcoded spacing literals before this task. A focused ArtDeco token check on the split files still fails on preserved literals:

```text
theme-apply.element-plus.scss:123: hardcoded spacing literal (2px)
theme-apply.surfaces-utilities.scss:15: hardcoded spacing literal (8px)
theme-apply.surfaces-utilities.scss:16: hardcoded spacing literal (8px)
theme-apply.motion-media-print.scss:15: hardcoded spacing literal (20px)
theme-apply.motion-media-print.scss:34: hardcoded spacing literal (768px)
ArtDeco Token Validation Failed.
```

This node intentionally preserves those values and relocates them into partials without semantic changes. Tokenization should be handled by a separate approval gate because `theme-apply.scss` is a global theme application layer with broad visual blast radius.

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
  - `visual-optimization.scss` facade split.
  - `element-plus-override.scss` facade split.
  - `pro-fintech-optimization.scss` facade split.
- Token cleanup for `theme-apply.scss` should be a separate node after deciding whether legacy CSS variables should map to `artdeco-tokens.scss` or remain compatibility aliases.
