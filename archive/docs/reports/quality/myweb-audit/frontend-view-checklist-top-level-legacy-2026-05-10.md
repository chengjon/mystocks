# Frontend View Redundant Page Review Checklist: Top-Level Legacy Views

Date: 2026-05-10

Scope:
- `web/frontend/src/views/AdvancedAnalysis.vue`
- `web/frontend/src/views/Analysis.vue`
- `web/frontend/src/views/BacktestAnalysis.vue`
- `web/frontend/src/views/BacktestWizard.vue`
- `web/frontend/src/views/Dashboard.vue`
- `web/frontend/src/views/EnhancedDashboard.vue`
- `web/frontend/src/views/EnhancedRiskMonitor.vue`
- `web/frontend/src/views/IndicatorLibrary.vue`
- `web/frontend/src/views/IndustryConceptAnalysis.vue`
- `web/frontend/src/views/Market.vue`
- `web/frontend/src/views/MarketData.vue`
- `web/frontend/src/views/monitor.vue`
- `web/frontend/src/views/Phase4Dashboard.vue`
- `web/frontend/src/views/PortfolioManagement.vue`
- `web/frontend/src/views/RealTimeMonitor.vue`
- `web/frontend/src/views/RiskMonitor.vue`
- `web/frontend/src/views/Settings.vue`
- `web/frontend/src/views/StockDetail.vue`
- `web/frontend/src/views/Stocks.vue`
- `web/frontend/src/views/StrategyManagement.vue`
- `web/frontend/src/views/TaskManagement.vue`
- `web/frontend/src/views/TdxMarket.vue`
- `web/frontend/src/views/TechnicalAnalysis.vue`
- `web/frontend/src/views/TestPage.vue`
- `web/frontend/src/views/TradeManagement.vue`
- `web/frontend/src/views/TradingDecisionCenter.vue`
- `web/frontend/src/views/Wencai.vue`

Purpose:
- Apply redundant-page governance to top-level legacy views that are not current menu/router canonical entries.
- Separate thin compatibility wrappers from honest static shells and composition shells.
- Prevent archive approval while direct owner specs, historical audit records, and compatibility roles remain.

## Current Truth Inputs

Runtime truth:
- The current active route truth remains `web/frontend/src/router/index.ts`.
- Many top-level files are no longer direct router dynamic imports, but several intentionally delegate to canonical owners.
- `TradingDashboard.vue` is not in this checklist because it remains the active `/trade/terminal` route owner.

Historical governance evidence:
- `docs/reports/quality/myweb-audit/audit-20260426-02/closeout/audit-20260426-02-closeout.md`
- `docs/reports/quality/myweb-audit/audit-20260426-02/pages/*legacy*truth-audit.md`
- `docs/reports/quality/myweb-audit/audit-20260426-02/batches/secondary-batch-*.md`

Guard and reference evidence:
- Direct owner specs under `web/frontend/src/views/__tests__/`
- Historical function-tree and audit references in `docs/FUNCTION_TREE.md` and `docs/reports/quality/myweb-audit/`

## Group Classification

### Thin Compatibility Wrappers

| Page | Wrapper target | Route status | Lifecycle status | Archive decision |
|---|---|---:|---|---|
| `Dashboard.vue` | `@/views/artdeco-pages/ArtDecoDashboard.vue` | `redirect` | `compat-retained` | Not archive-approved |
| `EnhancedDashboard.vue` | `@/views/artdeco-pages/ArtDecoDashboard.vue` | `redirect` | `compat-retained` | Not archive-approved |
| `Phase4Dashboard.vue` | `@/views/artdeco-pages/ArtDecoDashboard.vue` | `redirect` | `compat-retained` | Not archive-approved |
| `Settings.vue` | `@/views/system/Settings.vue` | `redirect` | `compat-retained` | Not archive-approved |
| `StrategyManagement.vue` | `@/views/strategy/List.vue` | `redirect` | `compat-retained` | Not archive-approved |
| `BacktestAnalysis.vue` | `@/views/strategy/Backtest.vue` | `redirect` | `compat-retained` | Not archive-approved |
| `RiskMonitor.vue` | `@/views/risk/Center.vue` | `redirect` | `compat-retained` | Not archive-approved |
| `EnhancedRiskMonitor.vue` | `@/views/risk/Center.vue` | `redirect` | `compat-retained` | Not archive-approved |
| `IndicatorLibrary.vue` | `@/views/data/Advanced.vue` | `redirect` | `compat-retained` | Not archive-approved |
| `Market.vue` | `@/views/trade/Portfolio.vue` | `redirect` | `compat-retained` | Not archive-approved |
| `TradeManagement.vue` | `@/views/artdeco-pages/ArtDecoTradingManagement.vue` | `redirect` | `compat-retained` | Not archive-approved |
| `Wencai.vue` | `@/components/market/WencaiPanel.vue` | `redirect` | `compat-retained` | Not archive-approved |

Wrapper decision:
- These files are not archive candidates while they preserve intentional compatibility paths and direct owner specs.
- Archive eligibility requires an explicit compatibility-retirement decision plus migration/removal of direct tests and historical references.

### Honest Static Shells

| Page | Handoff family | Route status | Lifecycle status | Archive decision |
|---|---|---:|---|---|
| `AdvancedAnalysis.vue` | `/data/indicator`, `/detail/graphics/:symbol`, `/strategy/signals` | `dead` | `candidate-review` | Not archive-approved |
| `Analysis.vue` | `/detail/graphics/:symbol`, `/data/indicator`, `/ai/sentiment` | `dead` | `candidate-review` | Not archive-approved |
| `BacktestWizard.vue` | `/strategy/backtest`, `/strategy/repo`, `/strategy/opt` | `dead` | `candidate-review` | Not archive-approved |
| `IndustryConceptAnalysis.vue` | `/data/industry`, `/data/concept`, `/data/fund-flow` | `dead` | `candidate-review` | Not archive-approved |
| `MarketData.vue` | `/market/realtime`, `/market/lhb`, `/data/fund-flow`, `/data/industry` | `dead` | `candidate-review` | Not archive-approved |
| `monitor.vue` | `/system/health`, `/system/resources`, `/trade/terminal` | `dead` | `candidate-review` | Not archive-approved |
| `PortfolioManagement.vue` | `/watchlist/manage`, `/trade/portfolio`, `/risk/management` | `dead` | `candidate-review` | Not archive-approved |
| `RealTimeMonitor.vue` | `/market/realtime`, `/risk/alerts`, `/strategy/backtest` | `dead` | `candidate-review` | Not archive-approved |
| `StockDetail.vue` | `/detail/graphics/:symbol`, `/detail/news/:symbol`, `/trade/positions` | `dead` | `candidate-review` | Not archive-approved |
| `Stocks.vue` | `/watchlist/screener`, `/market/realtime`, `/detail/graphics/:symbol` | `dead` | `candidate-review` | Not archive-approved |
| `TaskManagement.vue` | `/strategy/backtest`, `/trade/terminal`, `/system/health` | `dead` | `candidate-review` | Not archive-approved |
| `TdxMarket.vue` | `/market/realtime`, `/market/technical`, `/system/data` | `dead` | `candidate-review` | Not archive-approved |
| `TechnicalAnalysis.vue` | `/detail/graphics/:symbol`, `/market/technical`, `/data/indicator` | `dead` | `candidate-review` | Not archive-approved |
| `TestPage.vue` | `/dashboard` | `dead` | `candidate-review` | Not archive-approved |

Static-shell decision:
- These files no longer contain reusable runtime business assets after previous static-shell conversion.
- They remain blocked from archive because direct owner specs and historical docs intentionally preserve their static-shell truth.
- Some handoff routes may require later link verification before archive eligibility, but no runtime file movement is approved here.

### Composition Shell

| Page | Current implementation | Route status | Lifecycle status | Archive decision |
|---|---|---:|---|---|
| `TradingDecisionCenter.vue` | Composes `trading-decision/{DecisionHeader,DecisionPortfolio,DecisionPositions,DecisionOrders}.vue` | `dead` / embedded legacy | `candidate-review` | Not archive-approved |

Composition-shell decision:
- `TradingDecisionCenter.vue` is not a canonical router owner, but it is the historical parent for the trading-decision child pages.
- Its child components already have separate checklist decisions: portfolio/positions are compatibility wrappers; header/orders are static shells.
- Archive eligibility requires a parent-level compatibility-retirement decision and direct review of all child imports.

## Redundant-Page Checklist

Common checks:
- Not current menu canonical entry: pass for this scope.
- Not current router canonical entry: pass, except wrapper targets that intentionally point to active owners.
- Hidden-reference check: incomplete; direct owner specs and historical audit docs still reference the files.
- Function-tree status: mixed `失效但兼容保留` and `重复冗余待判定`; not formally retired.
- Reusable asset review: runtime logic was already either delegated to canonical owners or removed during prior static-shell repairs.
- Successor proof: partial; wrapper pages have direct successors, static shells have handoff families, and `TradingDecisionCenter.vue` has no single successor.
- Archive eligibility: blocked for every file in this batch.

## Batch Conclusion

No top-level legacy file in this checklist is archive-approved.

The correct next action is to decide compatibility retirement policy by subgroup:
- Wrapper subgroup: retire only after direct tests and historical compatibility expectations are migrated or removed.
- Static-shell subgroup: retire only after function-tree status changes from legacy/static-shell retention to formally retired.
- Composition subgroup: retire only after `trading-decision/*` child decisions are absorbed or explicitly abandoned.
