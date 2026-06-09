# Bloomberg Terminal Override SCSS Style Split Report

Date: 2026-06-02

## Scope

This Function Tree node implements a mechanical file-size guard cleanup for `web/frontend/src/styles/bloomberg-terminal-override.scss`.

The original style body was preserved exactly and moved into concern-based partials:

- `web/frontend/src/styles/bloomberg-terminal-override.tokens.scss`
- `web/frontend/src/styles/bloomberg-terminal-override.base-shell.scss`
- `web/frontend/src/styles/bloomberg-terminal-override.surfaces-data.scss`
- `web/frontend/src/styles/bloomberg-terminal-override.controls-forms.scss`
- `web/frontend/src/styles/bloomberg-terminal-override.metrics-charts.scss`
- `web/frontend/src/styles/bloomberg-terminal-override.navigation-overlays.scss`
- `web/frontend/src/styles/bloomberg-terminal-override.data-display-responsive.scss`
- `web/frontend/src/styles/bloomberg-terminal-override.motion-final-overrides.scss`

The facade remains `web/frontend/src/styles/bloomberg-terminal-override.scss` and imports the new partials in the same order as the original sections.

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
| `bloomberg-terminal-override.scss` | 19 | 0 |
| `bloomberg-terminal-override.tokens.scss` | 59 | 0 |
| `bloomberg-terminal-override.base-shell.scss` | 50 | 2 |
| `bloomberg-terminal-override.surfaces-data.scss` | 72 | 15 |
| `bloomberg-terminal-override.controls-forms.scss` | 56 | 11 |
| `bloomberg-terminal-override.metrics-charts.scss` | 72 | 18 |
| `bloomberg-terminal-override.navigation-overlays.scss` | 92 | 8 |
| `bloomberg-terminal-override.data-display-responsive.scss` | 80 | 6 |
| `bloomberg-terminal-override.motion-final-overrides.scss` | 58 | 2 |

Original file size was 551 lines. The largest resulting partial is 92 lines.

## Split Ranges

| Partial | Original line range | Concern |
| --- | --- | --- |
| `tokens` | 12-70 | Element Plus OLED/dark theme variable overrides |
| `base-shell` | 71-120 | global background and sidebar/menu shell overrides |
| `surfaces-data` | 121-192 | cards and table/data-density overrides |
| `controls-forms` | 193-248 | button and input/form overrides |
| `metrics-charts` | 249-320 | stat cards, A-share color semantics, chart containers |
| `navigation-overlays` | 321-412 | tabs, dropdowns, dialogs, progress, switches, scrollbars |
| `data-display-responsive` | 413-492 | professional data utility classes, viewport adjustment, VitePress override |
| `motion-final-overrides` | 493-551 | glow animation and final dark-background enforcement |

## Preservation Evidence

- Original post-header SCSS body reconstruction: `raw_match: true`
- Body comparison against `HEAD:web/frontend/src/styles/bloomberg-terminal-override.scss`: `body_match: true`
- Original header preservation: `header_preserved: true`
- Scope stayed inside the active Function Tree authorization.

## Validation

| Gate | Command | Result |
| --- | --- | --- |
| GitNexus pre-impact | `gitnexus impact File:web/frontend/src/styles/bloomberg-terminal-override.scss` | LOW risk, 0 direct, 0 affected processes |
| Function Tree scope | `ft-governance.cjs scope-check` | Passed: 14 changed files within active authorization |
| SCSS whitespace | `git diff --check -- web/frontend/src/styles/bloomberg-terminal-override*.scss` | Passed |
| ArtDeco token check | `node scripts/check-artdeco-tokens.js --target-file ...` | Passed |
| Frontend structural build | `cd web/frontend && npm run build:no-types` | Passed: 2583 modules transformed, built in 56.45s |

## Notes

The remaining raw `px` literals are preserved from the existing style body and were not token-cleaned in this node. The local ArtDeco token checker accepted the split files as-is. Any semantic token migration should remain a separate approved node because it can affect visual output.

## Suggested Next Candidates

- `web/frontend/src/styles/element-plus-artdeco.scss`
- `web/frontend/src/styles/zhihu-inspired.scss`
- `web/frontend/src/styles/accessibility-enhancements.scss`
