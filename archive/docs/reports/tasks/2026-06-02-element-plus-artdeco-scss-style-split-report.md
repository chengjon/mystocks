# Element Plus ArtDeco SCSS Style Split Report

Date: 2026-06-02

## Scope

This Function Tree node implements a mechanical file-size guard cleanup for `web/frontend/src/styles/element-plus-artdeco.scss`.

The original style body was preserved exactly and moved into concern-based partials:

- `web/frontend/src/styles/element-plus-artdeco.variables.scss`
- `web/frontend/src/styles/element-plus-artdeco.core-components.scss`
- `web/frontend/src/styles/element-plus-artdeco.data-overlays.scss`
- `web/frontend/src/styles/element-plus-artdeco.indicators-controls.scss`
- `web/frontend/src/styles/element-plus-artdeco.feedback-states.scss`

The facade remains `web/frontend/src/styles/element-plus-artdeco.scss` and imports the new partials in the same order as the original sections.

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
| `element-plus-artdeco.scss` | 19 | 0 |
| `element-plus-artdeco.variables.scss` | 123 | 3 |
| `element-plus-artdeco.core-components.scss` | 93 | 3 |
| `element-plus-artdeco.data-overlays.scss` | 100 | 6 |
| `element-plus-artdeco.indicators-controls.scss` | 102 | 1 |
| `element-plus-artdeco.feedback-states.scss` | 110 | 5 |

Original file size was 543 lines. The largest resulting partial is 123 lines.

## Split Ranges

| Partial | Original line range | Concern |
| --- | --- | --- |
| `variables` | 15-137 | Element Plus CSS variable mappings to ArtDeco tokens |
| `core-components` | 138-230 | buttons, cards, and inputs |
| `data-overlays` | 231-330 | tables, select dropdowns, dialogs, and tabs |
| `indicators-controls` | 331-432 | tags, progress, switch, checkbox, and radio controls |
| `feedback-states` | 433-543 | alerts, tooltips, notifications, loading masks, and messages |

## Preservation Evidence

- Original post-import SCSS body reconstruction: `raw_match: true`
- Body comparison against `HEAD:web/frontend/src/styles/element-plus-artdeco.scss`: `body_match: true`
- Original header preservation: `header_preserved: true`
- Scope stayed inside the active Function Tree authorization.

## Validation

| Gate | Command | Result |
| --- | --- | --- |
| GitNexus pre-impact | `gitnexus impact File:web/frontend/src/styles/element-plus-artdeco.scss` | LOW risk, 0 direct, 0 affected processes |
| Function Tree scope | `ft-governance.cjs scope-check` | Passed: 11 changed files within active authorization |
| SCSS whitespace | `git diff --check -- web/frontend/src/styles/element-plus-artdeco*.scss` | Passed |
| ArtDeco token check | `node scripts/check-artdeco-tokens.js --target-file ...` | Passed |
| Frontend structural build | `cd web/frontend && npm run build:no-types` | Passed: 2583 modules transformed, built in 27.41s |

## Notes

The remaining raw `px` literals are preserved from the existing style body and were not token-cleaned in this node. The local ArtDeco token checker accepted the split files as-is. Any semantic token migration should remain a separate approved node because it can affect visual output.

## Suggested Next Candidates

- `web/frontend/src/styles/zhihu-inspired.scss`
- `web/frontend/src/styles/accessibility-enhancements.scss`
- `web/frontend/src/styles/critical-rendering.scss`
