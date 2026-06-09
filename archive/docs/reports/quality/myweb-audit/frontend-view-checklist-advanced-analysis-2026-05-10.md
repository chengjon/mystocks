# Frontend View Redundant Page Review Checklist: `views/advanced-analysis`

Date: 2026-05-10

Scope:
- `web/frontend/src/views/advanced-analysis/AnomalyTrackingView.vue`
- `web/frontend/src/views/advanced-analysis/BatchAnalysisView.vue`
- `web/frontend/src/views/advanced-analysis/CapitalFlowView.vue`
- `web/frontend/src/views/advanced-analysis/ChipDistributionView.vue`
- `web/frontend/src/views/advanced-analysis/DecisionModelsView.vue`
- `web/frontend/src/views/advanced-analysis/FinancialValuationView.vue`
- `web/frontend/src/views/advanced-analysis/FundamentalAnalysisView.vue`
- `web/frontend/src/views/advanced-analysis/MarketPanoramaView.vue`
- `web/frontend/src/views/advanced-analysis/RadarAnalysisView.vue`
- `web/frontend/src/views/advanced-analysis/SentimentAnalysisView.vue`
- `web/frontend/src/views/advanced-analysis/TechnicalAnalysisView.vue`
- `web/frontend/src/views/advanced-analysis/TimeSeriesView.vue`
- `web/frontend/src/views/advanced-analysis/TradingSignalsView.vue`

Related parent surface:
- `web/frontend/src/views/AdvancedAnalysis.vue`

Purpose:
- Apply the frontend view governance redundant-page checklist to the orphan advanced-analysis child page group.
- Preserve historical static-shell guard intent while avoiding premature archive movement.
- Flag successor/handoff issues that must be resolved before any archive or route-retirement batch.

## Current Truth Inputs

Runtime truth:
- `web/frontend/src/router/index.ts` does not dynamically import `views/advanced-analysis/*.vue`.
- `web/frontend/src/views/AdvancedAnalysis.vue` is also a legacy static shell rather than an active canonical advanced-analysis workbench.
- Current verified successor families are `/data/indicator`, `/data/fund-flow`, `/market/technical`, `/detail/graphics/:symbol`, `/strategy/signals`, `/ai/sentiment`, and `/strategy/repo`.

Historical governance evidence:
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/advanced-analysis-child-static-shells-truth-audit.md`
- `docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-40-audit.md`
- `docs/reports/quality/myweb-audit/audit-20260426-02/secondary-line-progress-summary.md`

Guard and reference evidence:
- `web/frontend/src/views/advanced-analysis/__tests__/legacyStaticShells.spec.ts`
- `web/frontend/src/views/__tests__/AdvancedAnalysis.spec.ts`
- `web/frontend/tests/unit/config/advanced-analysis-mainline-gate.spec.ts`
- `docs/FUNCTION_TREE.md`

## Page-Level Classification

| Page group | Current implementation | Route status | Guard status | Reusable assets | Successor / owner | Lifecycle status | Archive decision |
|---|---|---:|---:|---|---|---|---|
| `views/advanced-analysis/*.vue` | Honest static child shells | `dead` | `mainline-guarded` + direct owner spec | No dynamic business assets remain in the child views | Multiple canonical handoff routes by topic | `candidate-review` | Not archive-approved |
| `views/AdvancedAnalysis.vue` | Honest static parent shell | `dead` | direct owner spec | No dynamic business assets remain in the parent view | `/data/indicator`, `/detail/graphics/600519`, `/strategy/signals` | `candidate-review` | Not archive-approved |

## Redundant-Page Checklist

### Common Child-Page Checks

- Not menu referenced: pass.
- Not router dynamic import referenced: pass.
- Not active runtime owner: pass.
- Hidden reference check: incomplete; child views are directly imported by `legacyStaticShells.spec.ts`, covered by `advanced-analysis-mainline-gate.spec.ts`, and referenced by historical audit artifacts.
- Function-tree status: legacy advanced-analysis child surfaces, not formally retired.
- Reusable asset review: no reusable child-level chart logic, selector, metrics card, table schema, signal model, score model, or verified analysis contract remains after static-shell conversion.
- Successor proof: partial; each shell points to a nearby verified route family, but no one-to-one child successor exists.
- Archive eligibility: blocked by direct tests, mainline gate, historical docs, and partial successor proof.

Decision: keep all child pages as `candidate-review`; do not mark as `archive-candidate`.

### Handoff Notes By Child Page

| Page | Handoff route | Handoff status |
|---|---|---|
| `AnomalyTrackingView.vue` | `/data/indicator` | Valid successor family |
| `BatchAnalysisView.vue` | `/data/indicator` | Valid but likely weaker than current `/ai/batch`; requires review before archive |
| `CapitalFlowView.vue` | `/data/fund-flow` | Valid successor family |
| `ChipDistributionView.vue` | `/detail/graphics/600519` | Valid detail route family |
| `DecisionModelsView.vue` | `/strategy/repo` | Valid if strategy repo remains canonical for model inventory |
| `FinancialValuationView.vue` | `/data/indicator` | Valid successor family |
| `FundamentalAnalysisView.vue` | `/data/indicator` | Valid successor family |
| `MarketPanoramaView.vue` | `/data/fund-flow` | Valid successor family |
| `RadarAnalysisView.vue` | `/detail/graphics/600519` | Valid detail route family |
| `SentimentAnalysisView.vue` | `/ai/sentiment` | Valid canonical AI sentiment route |
| `TechnicalAnalysisView.vue` | `/market/technical` | Valid market technical route |
| `TimeSeriesView.vue` | `/detail/kline/600519` | Needs correction; current router exposes `/detail/graphics/:symbol` and `/detail/news/:symbol`, not `/detail/kline/:symbol` |
| `TradingSignalsView.vue` | `/strategy/signals` | Valid strategy signal route |

## Parent Surface Note

`web/frontend/src/views/AdvancedAnalysis.vue` is the same retirement family and is already guarded by `web/frontend/src/views/__tests__/AdvancedAnalysis.spec.ts`. It should not be archived together with child pages unless the parent workbench function-tree node and direct owner spec are explicitly migrated or retired.

## Batch Conclusion

The advanced-analysis child group is static and no longer owns pseudo-live analysis state, but it is not archive-approved. The next safe action is to repair or retarget stale handoff links, then decide whether advanced-analysis remains a documented legacy namespace or becomes an archive candidate after guard/test retirement.
