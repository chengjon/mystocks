# Pro Fintech Optimization SCSS Style Split Report

Date: 2026-06-01

## Scope

This Function Tree node implements a mechanical file-size guard cleanup for `web/frontend/src/styles/pro-fintech-optimization.scss`.

The original style body was preserved exactly and moved into concern-based partials:

- `web/frontend/src/styles/pro-fintech-optimization.tokens.scss`
- `web/frontend/src/styles/pro-fintech-optimization.layout.scss`
- `web/frontend/src/styles/pro-fintech-optimization.surfaces-tables.scss`
- `web/frontend/src/styles/pro-fintech-optimization.controls-navigation.scss`
- `web/frontend/src/styles/pro-fintech-optimization.metrics-charts.scss`
- `web/frontend/src/styles/pro-fintech-optimization.interactions-accessibility.scss`

The facade remains `web/frontend/src/styles/pro-fintech-optimization.scss` and imports the new partials in the same order as the original sections.

## Compatibility Boundaries

This node did not change:

- Vue or TypeScript runtime logic
- Vue Router route definitions
- backend API routes, OpenAPI contracts, schemas, or generated client contracts
- frontend API client code
- shared component extraction
- ArtDeco token values or global token baselines
- visual behavior beyond preserving the existing compiled SCSS body

## Split Result

| File | Lines | Raw `px` Literals |
| --- | ---: | ---: |
| `pro-fintech-optimization.scss` | 24 | 0 |
| `pro-fintech-optimization.tokens.scss` | 232 | 30 |
| `pro-fintech-optimization.layout.scss` | 43 | 1 |
| `pro-fintech-optimization.surfaces-tables.scss` | 67 | 5 |
| `pro-fintech-optimization.controls-navigation.scss` | 85 | 4 |
| `pro-fintech-optimization.metrics-charts.scss` | 71 | 5 |
| `pro-fintech-optimization.interactions-accessibility.scss` | 102 | 14 |

Original file size was 619 lines. The largest resulting partial is 232 lines.

## Preservation Evidence

- Original post-header SCSS body reconstruction: `raw_match: true`
- Body comparison against `HEAD:web/frontend/src/styles/pro-fintech-optimization.scss`: `body_match: true`
- Original header preservation: `header_preserved: true`
- Scope stayed inside the active Function Tree authorization.

## Validation

| Gate | Command | Result |
| --- | --- | --- |
| Function Tree scope | `ft-governance.cjs scope-check` | Passed: 12 changed files within active authorization |
| SCSS whitespace | `git diff --check -- web/frontend/src/styles/pro-fintech-optimization*.scss` | Passed |
| ArtDeco token check | `node scripts/check-artdeco-tokens.js --target-file ...` | Passed |
| Frontend structural build | `cd web/frontend && npm run build:no-types` | Passed: 2583 modules transformed, built in 26.23s |

## Notes

The remaining raw `px` literals are preserved from the existing style body and were not token-cleaned in this node. The local ArtDeco token checker accepted the split files as-is. Any semantic token migration should remain a separate approved node because it can affect visual output.

## Suggested Next Candidates

- `web/frontend/src/styles/bloomberg-terminal-override.scss`
- `web/frontend/src/styles/element-plus-artdeco.scss`
- `web/frontend/src/styles/zhihu-inspired.scss`
