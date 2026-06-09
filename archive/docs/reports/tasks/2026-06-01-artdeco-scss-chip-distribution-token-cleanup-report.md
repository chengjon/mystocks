# ArtDeco Chip Distribution SCSS Token Cleanup Report

Date: 2026-06-01

Function Tree node: `artdeco-scss-chip-distribution-token-cleanup`

## 1. Summary

This task tokenized the remaining hardcoded dimensional literals in the split `ArtDecoChipDistribution` SCSS partials.

The cleanup is scoped to SCSS token normalization only:

- No Vue or TypeScript runtime logic changed.
- No router configuration changed.
- No backend API contract changed.
- No frontend API client changed.
- No shared component was extracted.
- No global ArtDeco token or technical debt baseline changed.

## 2. Tokenization Strategy

Component-local semantic CSS variables were added under `.artdeco-chip-distribution` in `ArtDecoChipDistribution.layout.scss`.

Those variables map local dimensions to existing ArtDeco tokens:

- Icon dimensions use `--artdeco-spacing-12`, `--artdeco-spacing-6`, and `--artdeco-spacing-8`.
- Grid minimum widths and chart heights use `calc(...)` compositions of existing spacing tokens.
- Radius values use `--artdeco-radius-md`, `--artdeco-radius-sm`, or spacing-derived component-local variables.
- Glow, blur, marker, line, and progress dimensions use component-local variables backed by ArtDeco spacing tokens.
- The former `768px` media query was normalized to `48rem`, matching the same breakpoint value without retaining a hardcoded px literal.

Side-accent borders that were previously `3px` were normalized to `--chip-accent-width`, backed by `--artdeco-spacing-px`, aligning with the ArtDeco design rule that avoids heavy side-stripe borders.

## 3. Result

Focused files:

| File | Disallowed px before | Disallowed px after |
| --- | ---: | ---: |
| `ArtDecoChipDistribution.layout.scss` | 1 | 0 |
| `ArtDecoChipDistribution.chart.scss` | 16 | 0 |
| `ArtDecoChipDistribution.cost.scss` | 18 | 0 |
| `ArtDecoChipDistribution.profit.scss` | 20 | 0 |
| `ArtDecoChipDistribution.stability.scss` | 25 | 0 |
| `ArtDecoChipDistribution.responsive.scss` | 1 | 0 |

Total: 81 -> 0 disallowed hardcoded px literals.

## 4. Validation

| Gate | Result |
| --- | --- |
| Focused hardcoded px scan | Pass: all target partials at 0 disallowed px |
| Focused ArtDeco token check | Pass: 6/6 target partials |
| `npm run build:no-types` | Pass: `EXIT_STATUS=0`, built in `35.02s` |

## 5. Compatibility

The public SCSS facade `ArtDecoChipDistribution.scss` remains unchanged by this task, and `ArtDecoChipDistribution.vue` continues to import the same style entrypoint.

The task is not a route migration, API change, client transport change, shared component extraction, or runtime state change.
