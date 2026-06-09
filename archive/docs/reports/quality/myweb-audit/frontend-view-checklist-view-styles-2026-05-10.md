# Frontend View Checklist: `views/styles` Batch

Date: 2026-05-10

Scope:
- `web/frontend/src/views/styles/*`

This checklist records lifecycle evidence for root-level view style assets. It does not approve deletion, archive movement, or style relocation.

## Summary

Current file-system count: 21 files.

| Group | Files | Current Evidence | Lifecycle Result |
| --- | ---: | --- | --- |
| Directly imported root styles | 4 | Imported by root/demo legacy pages | `active-support/root-legacy-style` |
| Test-guarded support styles | 4 | Directly read by config/style tests | `candidate-review/test-guarded-style` |
| Residual root/demo style assets | 13 | No active page import found in current static search; still under directory gate | `candidate-review/legacy-style-asset` |

No file in this batch is `archive-approved`.

## Evidence

### Directory Gate

- `web/frontend/package.json` includes `--target-dir src/views/styles --changed-from-git` in `lint:artdeco:changed`.
- This means the directory still participates in ArtDeco changed-scope governance even when individual files are not route-owned.

### Direct Page Imports

Current static search found direct root page imports for:

- `DataVisualizationShowcase.vue` -> `./styles/DataVisualizationShowcase.scss`
- `PyprofilingDemo.vue` -> `./styles/PyprofilingDemo.css`
- `SmartDataSourceTest.vue` -> `./styles/SmartDataSourceTest.css`
- `TradingDashboard.vue` -> `./styles/TradingDashboard.css`

These style files are active support assets for their owning root pages and are excluded from archive flow unless the owning page is moved or retired in the same batch.

### Test And Guard References

- `root-demo-style-entrypoints.spec.ts` directly verifies `Analysis.scss`, `Dashboard.scss`, `Settings.scss`, and `TradingDecisionCenter.scss` exist and use `@use`.
- `wencai-style-normalization.spec.ts` directly reads `Market.scss`.
- `stock-analysis-style-normalization.spec.ts` explicitly asserts removed `StockAnalysisDemo.scss` stays absent; this confirms style cleanup must keep tests aligned.
- Prior directory-governance inventory classified `src/views/styles` as a root/historical page companion style layer, not as a shared style foundation.

## Classification

| File | Current Result | Reason | Successor / Action Hint |
| --- | --- | --- | --- |
| `DataVisualizationShowcase.scss` | `active-support/root-legacy-style` | Directly imported by `DataVisualizationShowcase.vue` | Govern with owning page |
| `PyprofilingDemo.css` | `active-support/root-demo-style` | Directly imported by root `PyprofilingDemo.vue` | Govern with root demo lifecycle |
| `SmartDataSourceTest.css` | `active-support/root-demo-style` | Directly imported by `SmartDataSourceTest.vue` | Govern with owning test/demo page |
| `TradingDashboard.css` | `active-support/trade-terminal-style` | Directly imported by active `TradingDashboard.vue` | Do not archive without `/trade/terminal` style migration |
| `Analysis.scss` | `candidate-review/test-guarded-style` | Test reads it; no active page import found in current static search | Compare against `Analysis.vue` lifecycle before retirement |
| `Dashboard.scss` | `candidate-review/test-guarded-style` | Test reads it; no active page import found in current static search | Compare against current `/dashboard` owner before retirement |
| `Settings.scss` | `candidate-review/test-guarded-style` | Test reads it; no active page import found in current static search | Compare against settings/system canonical pages |
| `TradingDecisionCenter.scss` | `candidate-review/test-guarded-style` | Test reads it; no active page import found in current static search | Govern with trading-decision root shell lifecycle |
| `Market.scss` | `candidate-review/test-guarded-style` | `wencai-style-normalization.spec.ts` reads it | Keep until Wencai/Market style guard is retired or replaced |
| `BacktestAnalysis.css` | `candidate-review/legacy-style-asset` | No active importer found | Requires owning root page successor/no-successor rationale |
| `EnhancedDashboard.scss` | `candidate-review/legacy-style-asset` | No active importer found | Govern with `EnhancedDashboard.vue` lifecycle |
| `FreqtradeDemo.css` | `candidate-review/legacy-demo-style` | No active importer found; separate demo SCSS exists under `views/demo/styles` | Compare with root `FreqtradeDemo.vue` and demo directory styles |
| `IndicatorLibrary.css` | `candidate-review/legacy-style-asset` | No active importer found | Govern with `IndicatorLibrary.vue` lifecycle |
| `Phase4Dashboard.scss` | `candidate-review/legacy-style-asset` | No active importer found; separate demo SCSS exists under `views/demo/styles` | Do not merge mechanically with demo fork |
| `StockDetail.scss` | `candidate-review/legacy-style-asset` | No active importer found | Govern with `StockDetail.vue` lifecycle |
| `StrategyManagement.css` | `candidate-review/legacy-style-asset` | No active importer found | Govern with strategy root shell lifecycle |
| `TaskManagement.scss` | `candidate-review/legacy-style-asset` | No active importer found | Govern with `TaskManagement.vue` lifecycle |
| `TdxMarket.scss` | `candidate-review/legacy-style-asset` | No active importer found | Compare against canonical `views/market/Tdx.vue` before retirement |
| `TdxpyDemo.css` | `candidate-review/legacy-demo-style` | No active importer found; separate demo SCSS exists under `views/demo/styles` | Govern with root/demo Tdxpy lifecycle |
| `TechnicalAnalysis.css` | `candidate-review/legacy-style-asset` | No active importer found; canonical technical style exists under `views/technical/styles` | Compare before any retirement |
| `Wencai.scss` | `candidate-review/legacy-style-asset` | No active importer found; separate demo `Wencai.scss` exists under `views/demo/styles` | Govern with Wencai ownership decision |

## Archive Eligibility

Current eligibility: not approved.

Blocking conditions:
- The whole directory remains in `lint:artdeco:changed`.
- Several files are directly imported by still-present root/demo pages.
- Several files are directly read by style/config tests.
- Some files appear superseded by domain-local or demo-local style files, but per-file successor mapping has not been approved.
- This worktree already has unrelated deletions and style movement in progress; this checklist must not be used as implicit deletion approval.

Required before archive or deletion:
- For each file, confirm no page import, no test read, no package-script guard dependency, and no doc/runtime mapping dependency.
- Record owning page lifecycle and successor or `no-successor-needed` rationale.
- Update or retire the relevant style tests in the same mutation batch.
- Remove the directory from `lint:artdeco:changed` only after all retained files are moved or the directory remains intentionally governed.

## Governance Conclusion

`views/styles` is a root/historical page companion style layer, not a canonical shared style system. A few files still actively support root pages, while others are test-guarded or residual style assets. The correct next action is per-owner style lifecycle mapping, not bulk archive or bulk extraction.
