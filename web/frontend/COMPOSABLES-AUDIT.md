# Composables Audit: views/composables/

**Created:** 2026-04-07
**Phase:** 03-structural-consolidation (Plan 03-02, Task 4)

## Inventory (17 files)

| # | File | Consumers | Consumer Paths | Classification |
|---|------|-----------|----------------|----------------|
| 1 | tradingDashboardActions.ts | 1 | TradingDashboard.vue | Extraction candidate |
| 2 | useAdvancedAnalysis.ts | 1 | AdvancedAnalysis.vue | Keep view-local |
| 3 | useAnalysis.ts | 1 | Analysis.vue | Keep view-local |
| 4 | useBacktestWizard.ts | 1 | BacktestWizard.vue | Keep view-local |
| 5 | useEnhancedDashboard.ts | 1 | EnhancedDashboard.vue | Keep view-local |
| 6 | useIndustryConceptAnalysis.ts | 1 | IndustryConceptAnalysis.vue | Keep view-local |
| 7 | usePhase4Dashboard.ts | 1 | Phase4Dashboard.vue | Keep view-local |
| 8 | usePortfolioManagement.ts | 1 | PortfolioManagement.vue | Keep view-local |
| 9 | usePyprofilingDemo.ts | 1 | (demo view) | Keep view-local |
| 10 | useSettings.ts | 1 | Settings.vue | Keep view-local |
| 11 | useTechnicalAnalysis.shortcuts.ts | 1 | TechnicalAnalysis.vue | Keep view-local |
| 12 | useTechnicalAnalysis.ts | 1 | TechnicalAnalysis.vue | Keep view-local |
| 13 | useTechnicalAnalysis.types.ts | 1 | TechnicalAnalysis.vue | Keep view-local |
| 14 | useTradingDashboard.ts | 1 | TradingDashboard.vue | Extraction candidate |
| 15 | usemonitor.ts | 1 | monitor.vue | Keep view-local |
| 16 | __tests__/ | 0 | (test dir) | Keep view-local |
| 17 | __node_tests__/ | 0 | (test dir) | Keep view-local |

Additionally, feature-specific `composables/` subdirectories exist under 11 view groups (monitoring, market, strategy, announcement, etc.) with their own local composables.

## Summary

- **Keep view-local:** 15 files — each consumed by exactly 1 view via relative `./composables/` imports
- **Extraction candidates:** 2 files (`useTradingDashboard.ts`, `tradingDashboardActions.ts`)
- **MIGRATION_PROGRESS.md agreement:** Fully consistent — 15/17 classified "Keep view-local"

## Recommendation

**Do NOT bulk-move `views/composables/` to `src/composables/`.**

Rationale:
1. 15/17 files are consumed by single views via relative imports (`./composables/xxx`)
2. Moving them would break 15+ import paths
3. These composables are tightly coupled to their consuming views — they are not shared utilities
4. The 2 extraction candidates should only move after TradingDashboard disposition is resolved (per MIGRATION_PROGRESS.md task 8.5)

**STRU-04 status:** Cannot complete without breaking active code. Recommend updating REQUIREMENTS.md to mark STRU-04 as deferred.
