# Frontend View Governance 3.14 Lint Disposition

> **Scope**: `openspec/changes/update-frontend-view-governance`
> **Task**: `3.14 Resolve or explicitly record the unrelated lint:artdeco:changed failure caused by existing advanced-analysis token debt before marking global frontend lint clean.`
> **Date**: 2026-05-12

## Decision

`3.14` is closed by explicit record, not by fixing the unrelated token debt.

The broad ArtDeco changed-scope lint command is still not globally clean. The current failure is outside the completed frontend-view governance archive batches and is caused by existing `src/views/advanced-analysis/*.vue` hardcoded spacing/color token debt.

This record must not be used to claim global frontend lint is clean.

## Verification

Command:

```bash
cd web/frontend && npm run lint:artdeco:changed
```

Result:

- Exit code: `1`
- First sandboxed attempt failed before running the project command with `bwrap: Can't mkdir /opt/claude/mystocks_spec/web/frontend/.agents: Permission denied`.
- Escalated rerun executed the project command and failed in `src/views/advanced-analysis`.

Observed failure class:

- hardcoded spacing literals such as `12px`, `18px`, `22px`, and `720px`
- hardcoded color literals that should use `var(--artdeco-*)`

Observed files include:

- `src/views/advanced-analysis/AnomalyTrackingView.vue`
- `src/views/advanced-analysis/BatchAnalysisView.vue`
- `src/views/advanced-analysis/CapitalFlowView.vue`
- `src/views/advanced-analysis/ChipDistributionView.vue`
- `src/views/advanced-analysis/DecisionModelsView.vue`
- `src/views/advanced-analysis/FinancialValuationView.vue`
- `src/views/advanced-analysis/FundamentalAnalysisView.vue`
- `src/views/advanced-analysis/MarketPanoramaView.vue`
- `src/views/advanced-analysis/RadarAnalysisView.vue`
- `src/views/advanced-analysis/SentimentAnalysisView.vue`
- `src/views/advanced-analysis/TechnicalAnalysisView.vue`
- `src/views/advanced-analysis/TimeSeriesView.vue`
- `src/views/advanced-analysis/TradingSignalsView.vue`

## Boundary

This is a pre-existing ArtDeco token debt in the `advanced-analysis` directory.

It is not evidence that the A2/A3/A4 frontend-view governance archive or absorption batches changed global lint status.

Global frontend lint clean remains unclaimed until the `advanced-analysis` token debt is fixed in a separate approved scope.
