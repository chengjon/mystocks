# ArtDeco Capital Flow SCSS Split Report

Date: 2026-06-01

Function Tree node: `artdeco-scss-capital-flow-style-split`

## 1. Summary

This task split `ArtDecoCapitalFlow.scss` by its existing semantic sections while preserving the existing style entrypoint.

The split is mechanical:

- `ArtDecoCapitalFlow.scss` remains the only public facade imported by `ArtDecoCapitalFlow.vue`.
- Selector order and declaration order are preserved by the facade import sequence.
- No token cleanup, visual redesign, runtime logic, router, API contract, or frontend API client changes were included in this split commit.

## 2. Split Result

| File | Lines | Purpose |
| --- | ---: | --- |
| `ArtDecoCapitalFlow.scss` | 9 | Facade: token import plus partial imports |
| `ArtDecoCapitalFlow.layout.scss` | 15 | Root wrapper and flow overview grid |
| `ArtDecoCapitalFlow.heatmap.scss` | 188 | Capital heatmap section |
| `ArtDecoCapitalFlow.clustering.scss` | 256 | Clustering analysis section |
| `ArtDecoCapitalFlow.control.scss` | 292 | Main force control section |
| `ArtDecoCapitalFlow.opportunity.scss` | 293 | Opportunity diagnosis section |
| `ArtDecoCapitalFlow.responsive.scss` | 74 | Existing responsive rules |

Original file size: 1120 lines.

Reconstruction check: `exact_content_match=true`.

## 3. Existing Token Debt

The focused ArtDeco token check still fails as expected because this task intentionally did not perform token cleanup.

| File | Disallowed px count |
| --- | ---: |
| `ArtDecoCapitalFlow.layout.scss` | 1 |
| `ArtDecoCapitalFlow.heatmap.scss` | 20 |
| `ArtDecoCapitalFlow.clustering.scss` | 20 |
| `ArtDecoCapitalFlow.control.scss` | 19 |
| `ArtDecoCapitalFlow.opportunity.scss` | 22 |
| `ArtDecoCapitalFlow.responsive.scss` | 1 |

Total disallowed hardcoded px count remains 83, matching the pre-split source count.

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
| `npm run build:no-types` | Pass: `EXIT_STATUS=0`, built in `32.71s` |
| Focused ArtDeco token check | Expected fail: existing hardcoded px debt preserved |

## 6. Follow-Up Recommendation

Open a separate Function Tree node for `ArtDecoCapitalFlow` token cleanup. That follow-up should reduce the 83 hardcoded px literals to existing ArtDeco spacing, radius, chart-size, icon-size, and breakpoint tokens without changing selectors or component logic.
