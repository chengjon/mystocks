# ArtDeco Global SCSS Style Split Report

Date: 2026-06-02

## Scope

This Function Tree node implements a mechanical file-size guard cleanup for `web/frontend/src/styles/artdeco-global.scss`.

The user suggested continuing with `web/frontend/src/styles/zhihu-inspired.scss` or `web/frontend/src/styles/accessibility-enhancements.scss`. Those exact paths do not exist in the current repository. The closest real accessibility file, `web/frontend/src/styles/accessibility-focus-enhancement.scss`, is 428 lines and is below the SCSS guard limit of 500 lines. To keep reducing actual SCSS violations from `reports/analysis/file-size-guard-report-2026-06-01.md`, this node instead processed the next real over-limit global style file: `web/frontend/src/styles/artdeco-global.scss`.

The original style body was preserved exactly and moved into concern-based partials:

- `web/frontend/src/styles/artdeco-global.corner-cleanup.scss`
- `web/frontend/src/styles/artdeco-global.base-reset.scss`
- `web/frontend/src/styles/artdeco-global.typography-links.scss`
- `web/frontend/src/styles/artdeco-global.scroll-selection-focus.scss`
- `web/frontend/src/styles/artdeco-global.utilities.scss`
- `web/frontend/src/styles/artdeco-global.accessibility-motion-print.scss`

The facade remains `web/frontend/src/styles/artdeco-global.scss` and keeps the original font and token imports before importing the new partials in the same order as the original sections.

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
| `artdeco-global.scss` | 38 | 0 |
| `artdeco-global.corner-cleanup.scss` | 21 | 0 |
| `artdeco-global.base-reset.scss` | 49 | 7 |
| `artdeco-global.typography-links.scss` | 110 | 7 |
| `artdeco-global.scroll-selection-focus.scss` | 64 | 6 |
| `artdeco-global.utilities.scss` | 109 | 20 |
| `artdeco-global.accessibility-motion-print.scss` | 146 | 8 |

Original file size was 532 split lines. The source report listed this file as 531 lines against the SCSS limit of 500. The largest resulting partial is 146 lines.

## Split Ranges

| Partial | Original line range | Concern |
| --- | --- | --- |
| `corner-cleanup` | 33-53 | global decorative corner marker suppression |
| `base-reset` | 54-102 | global reset, base body/html, and selection defaults |
| `typography-links` | 103-212 | headings, body text, code, and link behavior |
| `scroll-selection-focus` | 213-276 | scrollbars, text selection, and focus-visible |
| `utilities` | 277-385 | reusable ArtDeco utility classes and state helpers |
| `accessibility-motion-print` | 386-532 | screen-reader support, animations, reduced motion, print, and color-scheme media blocks |

## Preservation Evidence

- Original post-import SCSS body reconstruction: `raw_match: true`
- Body comparison against `HEAD:web/frontend/src/styles/artdeco-global.scss`: `body_match: true`
- Original header/import preservation: `header_preserved: true`
- Scope stayed inside the active Function Tree authorization.

## Validation

| Gate | Command | Result |
| --- | --- | --- |
| GitNexus pre-impact | `gitnexus impact File:web/frontend/src/styles/artdeco-global.scss` | LOW risk, 0 direct, 0 affected processes |
| Function Tree scope | `ft-governance.cjs scope-check` | Passed: 12 changed files within active authorization |
| SCSS whitespace | `git diff --check -- web/frontend/src/styles/artdeco-global*.scss` | Passed |
| ArtDeco token check | `node scripts/check-artdeco-tokens.js --target-file ...` | Passed |
| Frontend structural build | `cd web/frontend && npm run build:no-types` | Passed: 2583 modules transformed, built in 27.57s |

## Notes

The remaining raw `px` literals are preserved from the existing style body and were not token-cleaned in this node. The local ArtDeco token checker accepted the split files as-is. Any semantic token migration should remain a separate approved node because it can affect visual output.

This file is an active global style entry imported by the standard frontend path, so the node kept all existing top-level font and token imports in the facade.

## Suggested Next Candidates

- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoChipDistribution.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoSentimentAnalysis.scss`
- `web/frontend/src/components/artdeco/advanced/styles/ArtDecoTimeSeriesAnalysis.scss`
