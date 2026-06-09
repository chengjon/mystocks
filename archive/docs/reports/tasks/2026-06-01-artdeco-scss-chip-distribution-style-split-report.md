# ArtDeco Chip Distribution SCSS Split Report

Date: 2026-06-01

Function Tree node: `artdeco-scss-chip-distribution-style-split`

## 1. Summary

This task split `ArtDecoChipDistribution.scss` by its existing semantic sections while preserving the existing style entrypoint.

The split is mechanical:

- `ArtDecoChipDistribution.scss` remains the only public facade imported by `ArtDecoChipDistribution.vue`.
- Selector order and declaration order are preserved by the facade import sequence.
- No token cleanup, visual redesign, runtime logic, router, API contract, or frontend API client changes were included in this split commit.

## 2. Split Result

| File | Lines | Purpose |
| --- | ---: | --- |
| `ArtDecoChipDistribution.scss` | 9 | Facade: token import plus partial imports |
| `ArtDecoChipDistribution.layout.scss` | 15 | Root wrapper and distribution overview grid |
| `ArtDecoChipDistribution.chart.scss` | 174 | Chip distribution chart section |
| `ArtDecoChipDistribution.cost.scss` | 232 | Cost distribution analysis section |
| `ArtDecoChipDistribution.profit.scss` | 304 | Chip profit analysis section |
| `ArtDecoChipDistribution.stability.scss` | 264 | Chip stability analysis section |
| `ArtDecoChipDistribution.responsive.scss` | 72 | Existing responsive rules |

Original file size: 1063 lines.

Reconstruction check: `exact_content_match=true`.

## 3. Existing Token Debt

The focused ArtDeco token check still fails as expected because this task intentionally did not perform token cleanup.

| File | Disallowed px count |
| --- | ---: |
| `ArtDecoChipDistribution.layout.scss` | 1 |
| `ArtDecoChipDistribution.chart.scss` | 16 |
| `ArtDecoChipDistribution.cost.scss` | 18 |
| `ArtDecoChipDistribution.profit.scss` | 20 |
| `ArtDecoChipDistribution.stability.scss` | 25 |
| `ArtDecoChipDistribution.responsive.scss` | 1 |

Total disallowed hardcoded px count remains 81, matching the pre-split source count.

## 4. Non-Goal Confirmation

No changes were made to:

- Vue or TypeScript runtime logic.
- `web/frontend/src/router/`.
- Backend route handlers or API contracts.
- `web/frontend/src/api/` or frontend API client code.
- Shared component extraction.
- Global token definitions or technical debt baselines.
- Deletion behavior or visual redesign.

## 5. Validation

| Gate | Result |
| --- | --- |
| Exact split reconstruction | Pass: `exact_content_match=true` |
| `npm run build:no-types` | Pass: `EXIT_STATUS=0`, built in `26.82s` |
| Focused ArtDeco token check | Expected fail: existing hardcoded px debt preserved |

## 6. Follow-Up Recommendation

Open a separate Function Tree node for `ArtDecoChipDistribution` token cleanup. That follow-up should reduce the 81 hardcoded px literals to existing ArtDeco spacing, radius, chart-size, icon-size, and breakpoint tokens without changing selectors or component logic.
