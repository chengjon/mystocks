# Frontend View Lifecycle Classification Focus - 2026-05-10

## Scope

Read-only lifecycle classification for the 24-file zero-router-reference focus set. No files were moved, archived, or deleted.

## Summary

- generated_at: `2026-05-10T02:42:10.069Z`
- total_files: `24`
- by_lifecycle: `candidate-review=19 / compat-retained=5`
- by_route_status: `dead=19 / redirect=5`
- by_guard_status: `mainline-guarded=18 / spec-guarded=6`

## Classification Table

| Page | Lifecycle | Route | Guard | Hints | Successor / rationale | Decision |
|---|---|---|---|---|---|---|
| `web/frontend/src/views/settings/General.vue` | candidate-review | dead | mainline-guarded | static-closed-shell | - | Static closed shell with guard/doc references; can only become archive-candidate after guard retirement/migration and checklist evidence. |
| `web/frontend/src/views/settings/Notifications.vue` | candidate-review | dead | mainline-guarded | static-closed-shell | - | Static closed shell with guard/doc references; can only become archive-candidate after guard retirement/migration and checklist evidence. |
| `web/frontend/src/views/settings/Security.vue` | candidate-review | dead | mainline-guarded | static-closed-shell | - | Static closed shell with guard/doc references; can only become archive-candidate after guard retirement/migration and checklist evidence. |
| `web/frontend/src/views/settings/Theme.vue` | candidate-review | dead | mainline-guarded | static-closed-shell | - | Static closed shell with guard/doc references; can only become archive-candidate after guard retirement/migration and checklist evidence. |
| `web/frontend/src/views/stocks/Activity.vue` | candidate-review | dead | spec-guarded | static-closed-shell | - | Static closed shell with guard/doc references; can only become archive-candidate after guard retirement/migration and checklist evidence. |
| `web/frontend/src/views/stocks/Concept.vue` | candidate-review | dead | spec-guarded | static-closed-shell | - | Static closed shell with guard/doc references; can only become archive-candidate after guard retirement/migration and checklist evidence. |
| `web/frontend/src/views/stocks/Industry.vue` | candidate-review | dead | spec-guarded | static-closed-shell | - | Static closed shell with guard/doc references; can only become archive-candidate after guard retirement/migration and checklist evidence. |
| `web/frontend/src/views/stocks/Portfolio.vue` | candidate-review | dead | spec-guarded | static-closed-shell | - | Static closed shell with guard/doc references; can only become archive-candidate after guard retirement/migration and checklist evidence. |
| `web/frontend/src/views/stocks/Screener.vue` | compat-retained | redirect | spec-guarded | implementation-assets, stats-strip, selector, fallback-literal | views/watchlist/Screener.vue wraps this implementation | Indirect active implementation; do not archive before implementation is moved or successor absorbs it. |
| `web/frontend/src/views/stocks/Watchlist.vue` | candidate-review | dead | mainline-guarded | static-closed-shell | - | Static closed shell with guard/doc references; can only become archive-candidate after guard retirement/migration and checklist evidence. |
| `web/frontend/src/views/technical/TechnicalAnalysis.vue` | candidate-review | dead | spec-guarded | - | - | Needs manual functional coverage review. |
| `web/frontend/src/views/trade-management/components/PortfolioOverview.vue` | candidate-review | dead | mainline-guarded | static-closed-shell | - | Static closed shell with guard/doc references; can only become archive-candidate after guard retirement/migration and checklist evidence. |
| `web/frontend/src/views/trade-management/components/PositionsTab.vue` | candidate-review | dead | mainline-guarded | static-closed-shell | - | Static closed shell with guard/doc references; can only become archive-candidate after guard retirement/migration and checklist evidence. |
| `web/frontend/src/views/trade-management/components/StatisticsTab.vue` | candidate-review | dead | mainline-guarded | static-closed-shell | - | Static closed shell with guard/doc references; can only become archive-candidate after guard retirement/migration and checklist evidence. |
| `web/frontend/src/views/trade-management/components/TradeDialog.vue` | candidate-review | dead | mainline-guarded | static-closed-shell | - | Static closed shell with guard/doc references; can only become archive-candidate after guard retirement/migration and checklist evidence. |
| `web/frontend/src/views/trade-management/components/TradeHistoryTab.vue` | candidate-review | dead | mainline-guarded | static-closed-shell | - | Static closed shell with guard/doc references; can only become archive-candidate after guard retirement/migration and checklist evidence. |
| `web/frontend/src/views/trading-decision/DecisionHeader.vue` | candidate-review | dead | mainline-guarded | static-closed-shell | - | Static closed shell with guard/doc references; can only become archive-candidate after guard retirement/migration and checklist evidence. |
| `web/frontend/src/views/trading-decision/DecisionOrders.vue` | candidate-review | dead | mainline-guarded | - | - | Needs manual functional coverage review. |
| `web/frontend/src/views/trading-decision/DecisionPortfolio.vue` | compat-retained | redirect | mainline-guarded | thin-wrapper | @/views/trade/Portfolio.vue | Thin compatibility wrapper; archive only after historical imports/tests/docs are migrated. |
| `web/frontend/src/views/trading-decision/DecisionPositions.vue` | compat-retained | redirect | mainline-guarded | thin-wrapper | @/views/trade/Center.vue | Thin compatibility wrapper; archive only after historical imports/tests/docs are migrated. |
| `web/frontend/src/views/trading/Execution.vue` | candidate-review | dead | mainline-guarded | - | - | Needs manual functional coverage review. |
| `web/frontend/src/views/trading/History.vue` | compat-retained | redirect | mainline-guarded | implementation-assets, thin-wrapper | @/views/trade/History.vue | Thin compatibility wrapper; archive only after historical imports/tests/docs are migrated. |
| `web/frontend/src/views/trading/Orders.vue` | candidate-review | dead | mainline-guarded | - | - | Needs manual functional coverage review. |
| `web/frontend/src/views/trading/Positions.vue` | compat-retained | redirect | mainline-guarded | implementation-assets, thin-wrapper | @/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue | Thin compatibility wrapper; archive only after historical imports/tests/docs are migrated. |

## Reference Counts

| Page | Runtime refs | Spec refs | Mainline refs | Docs refs |
|---|---:|---:|---:|---:|
| `web/frontend/src/views/settings/General.vue` | 0 | 4 | 2 | 12 |
| `web/frontend/src/views/settings/Notifications.vue` | 0 | 4 | 2 | 12 |
| `web/frontend/src/views/settings/Security.vue` | 0 | 4 | 2 | 14 |
| `web/frontend/src/views/settings/Theme.vue` | 0 | 4 | 2 | 12 |
| `web/frontend/src/views/stocks/Activity.vue` | 2 | 6 | 0 | 41 |
| `web/frontend/src/views/stocks/Concept.vue` | 6 | 17 | 0 | 116 |
| `web/frontend/src/views/stocks/Industry.vue` | 4 | 14 | 0 | 106 |
| `web/frontend/src/views/stocks/Portfolio.vue` | 9 | 17 | 0 | 197 |
| `web/frontend/src/views/stocks/Screener.vue` | 4 | 6 | 0 | 68 |
| `web/frontend/src/views/stocks/Watchlist.vue` | 3 | 10 | 2 | 76 |
| `web/frontend/src/views/technical/TechnicalAnalysis.vue` | 0 | 5 | 0 | 30 |
| `web/frontend/src/views/trade-management/components/PortfolioOverview.vue` | 1 | 7 | 4 | 31 |
| `web/frontend/src/views/trade-management/components/PositionsTab.vue` | 0 | 6 | 4 | 16 |
| `web/frontend/src/views/trade-management/components/StatisticsTab.vue` | 0 | 6 | 4 | 16 |
| `web/frontend/src/views/trade-management/components/TradeDialog.vue` | 0 | 6 | 4 | 16 |
| `web/frontend/src/views/trade-management/components/TradeHistoryTab.vue` | 0 | 6 | 4 | 16 |
| `web/frontend/src/views/trading-decision/DecisionHeader.vue` | 0 | 2 | 2 | 45 |
| `web/frontend/src/views/trading-decision/DecisionOrders.vue` | 0 | 2 | 2 | 45 |
| `web/frontend/src/views/trading-decision/DecisionPortfolio.vue` | 0 | 2 | 2 | 45 |
| `web/frontend/src/views/trading-decision/DecisionPositions.vue` | 0 | 2 | 2 | 45 |
| `web/frontend/src/views/trading/Execution.vue` | 1 | 6 | 4 | 81 |
| `web/frontend/src/views/trading/History.vue` | 5 | 15 | 4 | 178 |
| `web/frontend/src/views/trading/Orders.vue` | 0 | 6 | 4 | 81 |
| `web/frontend/src/views/trading/Positions.vue` | 2 | 10 | 4 | 96 |

## Interpretation

- `compat-retained` means the page is currently serving compatibility or indirect implementation duties; it is not archive-ready.
- `absorb-assets` means useful assets must be absorbed or explicitly rejected before any archive decision.
- `candidate-review` means the page still needs checklist evidence; it is not an archive approval.
- Guarded files cannot move to archive until matching specs are migrated or explicitly retired.
