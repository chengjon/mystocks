# Advanced Analysis Remaining Children Static Shell Truth Audit

## Scope
- `advanced-analysis/AnomalyTrackingView.vue`
- `advanced-analysis/BatchAnalysisView.vue`
- `advanced-analysis/CapitalFlowView.vue`
- `advanced-analysis/ChipDistributionView.vue`
- `advanced-analysis/DecisionModelsView.vue`
- `advanced-analysis/FinancialValuationView.vue`
- `advanced-analysis/SentimentAnalysisView.vue`

## Finding
These seven orphan child pages were not covered by the earlier advanced-analysis child-shell batch. Six still rendered `placeholder-content` module copy. `BatchAnalysisView.vue` went further and rendered result counts, completion counts, average score fallback, Element Plus tags, and metric extraction based on a prop-fed local result object.

Because the parent `AdvancedAnalysis.vue` is already an honest static shell and no independent canonical owner exists for these child modules, preserving those child semantics would keep a second advanced-analysis truth surface alive.

## Repair
- Replaced all seven child pages with honest `legacy-static-shell` surfaces.
- Removed local batch result aggregation, score fallback, metric extraction, and Element Plus dependency from `BatchAnalysisView.vue`.
- Extended the existing advanced-analysis orphan child regression to cover all thirteen child pages.

## Verification
- RED: `npx vitest run src/views/advanced-analysis/__tests__/legacyStaticShells.spec.ts` failed on the seven newly covered pages before repair.
- GREEN: `npx vitest run src/views/advanced-analysis/__tests__/legacyStaticShells.spec.ts src/views/__tests__/AdvancedAnalysis.spec.ts` passed `14/14`.
- Inventory: high-priority secondary shortlist remains `0`.
