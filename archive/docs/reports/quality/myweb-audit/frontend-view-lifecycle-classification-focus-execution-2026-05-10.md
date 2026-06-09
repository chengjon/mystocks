# Frontend View Lifecycle Classification Focus Execution - 2026-05-10

## Scope

This batch performs read-only lifecycle classification for the 24-file zero-router-reference focus set:

- `views/stocks/`
- `views/trading/`
- `views/trading-decision/`
- `views/trade-management/`
- `views/technical/`
- `views/settings/`

No frontend runtime code was modified. No view files were moved, archived, or deleted.

## Inputs

| Artifact | Purpose |
|---|---|
| `frontend-view-governance-inventory-2026-05-10.json` | Initial view inventory and heuristic hints |
| `frontend-view-guard-map-2026-05-10.json` | Guard/spec/runtime/docs reference evidence |
| `frontend-view-redundant-page-review-checklist-2026-05-10.md` | Per-page decision criteria |

## Generated Artifacts

| Artifact | Purpose |
|---|---|
| `docs/reports/quality/myweb-audit/frontend-view-lifecycle-classification-focus-2026-05-10.json` | Machine-readable lifecycle classification |
| `docs/reports/quality/myweb-audit/frontend-view-lifecycle-classification-focus-2026-05-10.md` | Human-readable classification table |

## Results

| Metric | Value |
|---|---:|
| Files classified | 24 |
| `candidate-review` | 19 |
| `compat-retained` | 5 |
| `archive-candidate` | 0 |
| `mainline-guarded` | 18 |
| `spec-guarded` | 6 |

## Key Findings

- No page in the focus set is approved for archive.
- `stocks/Screener.vue` is indirectly active because `watchlist/Screener.vue` wraps it; it is `compat-retained`.
- Thin wrappers such as `trading/History.vue`, `trading/Positions.vue`, `trading-decision/DecisionPortfolio.vue`, and `trading-decision/DecisionPositions.vue` are `compat-retained` until historical references/tests/docs are migrated or retired.
- Static closed shells in `settings/`, `trade-management/`, and parts of `stocks/` remain `candidate-review` because guard/spec/doc evidence still exists.
- `technical/TechnicalAnalysis.vue`, `trading/Execution.vue`, `trading/Orders.vue`, and `trading-decision/DecisionOrders.vue` need manual functional coverage review before any successor/rationale decision.

## Interpretation

This batch narrows the next work. It does not authorize cleanup. The next mutation-safe path is:

1. Choose one small guarded directory group.
2. Complete the redundant-page review checklist for each page.
3. Decide guard migration or retirement.
4. Only then propose an archive mutation batch if every redundant eligibility condition passes.

## OpenSpec Task Status

This completes a focus-set sub-batch of Step 2. It does not complete global Step 2 for all non-canonical views.

