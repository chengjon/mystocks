# ArtDeco Time Series SCSS Token Cleanup Report

Date: 2026-06-01

Function Tree node: `artdeco-scss-time-series-token-cleanup`

## 1. Summary

This task tokenized the remaining hardcoded dimensional literals in the split `ArtDecoTimeSeriesAnalysis` SCSS partials.

The cleanup is scoped to SCSS token normalization only:

- No Vue or TypeScript runtime logic changed.
- No router configuration changed.
- No backend API contract changed.
- No frontend API client changed.
- No shared component was extracted.
- No global ArtDeco token or technical debt baseline changed.

## 2. Tokenization Strategy

Component-local semantic CSS variables were added under `.artdeco-time-series-analysis` in `ArtDecoTimeSeriesAnalysis.layout.scss`.

Those variables map local dimensions to existing ArtDeco tokens:

- Icon sizes use `--artdeco-spacing-12` and `--artdeco-spacing-6`.
- Card and chart minimum sizes use `calc(...)` compositions of existing spacing tokens.
- Radius values use existing radius tokens or spacing-derived local variables.
- Chart heights use local semantic variables backed by spacing-token calculations.
- The former `768px` media query was normalized to `48rem`, matching the existing breakpoint value without using a hardcoded px literal.

The prediction insight accent width was normalized from a hardcoded side stripe to `--time-series-insight-accent-width`, backed by `--artdeco-spacing-px`, aligning with the ArtDeco design rule that avoids heavy side-stripe borders.

## 3. Result

Focused files:

| File | Disallowed px before | Disallowed px after |
| --- | ---: | ---: |
| `ArtDecoTimeSeriesAnalysis.layout.scss` | 1 | 0 |
| `ArtDecoTimeSeriesAnalysis.chart.scss` | 13 | 0 |
| `ArtDecoTimeSeriesAnalysis.inflection.scss` | 11 | 0 |
| `ArtDecoTimeSeriesAnalysis.periodicity.scss` | 19 | 0 |
| `ArtDecoTimeSeriesAnalysis.prediction.scss` | 21 | 0 |
| `ArtDecoTimeSeriesAnalysis.responsive.scss` | 1 | 0 |

Total: 66 -> 0 disallowed hardcoded px literals.

## 4. Validation

| Gate | Result |
| --- | --- |
| Focused hardcoded px scan | Pass: all target partials at 0 disallowed px |
| Focused ArtDeco token check | Pass: 6/6 target partials |
| `npm run build:no-types` | Pass: `EXIT_STATUS=0`, built in `47.69s` |

## 5. Compatibility

The public SCSS facade `ArtDecoTimeSeriesAnalysis.scss` remains unchanged by this task, and `ArtDecoTimeSeriesAnalysis.vue` continues to import the same style entrypoint.

The task is not a route migration, API change, client transport change, or runtime state change.
