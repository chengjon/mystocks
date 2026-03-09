# Wave 3: Large File Splitting Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Split two large TypeScript files into modular directories to improve maintainability and keep file sizes under 500 lines, while maintaining backward compatibility.

**Architecture:**
- `tests/helpers/page-objects.ts` (already a barrel) implementation currently in `tests/helpers/page-objects/part-*.ts`. This will be further granularized into `tests/helpers/pages/*.page.ts` (one file per class).
- `web/frontend/src/api/types/common.ts` (2235 lines) will be split into domain-specific files in `web/frontend/src/api/types/domains/`.

**Tech Stack:** TypeScript, Playwright, Vue 3 (types).

---

### Task 1: Granularize Page Objects

**Files:**
- Create directory: `tests/helpers/pages/`
- Create: `tests/helpers/pages/base.page.ts`, `tests/helpers/pages/dashboard.page.ts`, etc.
- Modify: `tests/helpers/page-objects.ts`
- Delete: `tests/helpers/page-objects/` (after move)

**Step 1: Create the new directory**
```bash
mkdir -p tests/helpers/pages
```

**Step 2: Extract classes from part-1.ts**
- `BasePage` -> `base.page.ts`
- `DashboardPage` -> `dashboard.page.ts` (imports BasePage)
- `MarketPage` -> `market.page.ts` (imports BasePage)
- `StockDetailPage` -> `stock-detail.page.ts` (imports BasePage)

**Step 3: Extract classes from part-2.ts**
- `TechnicalAnalysisPage` -> `technical-analysis.page.ts` (imports BasePage)
- `TradeManagementPage` -> `trade-management.page.ts` (imports BasePage)
- `StrategyManagementPage` -> `strategy-management.page.ts` (imports BasePage)
- `RiskMonitorPage` -> `risk-monitor.page.ts` (imports BasePage)

**Step 4: Extract classes from part-3.ts**
- `TaskManagementPage` -> `task-management.page.ts` (imports BasePage)
- `SettingsPage` -> `settings.page.ts` (imports BasePage)

**Step 5: Create index.ts barrel in pages directory**
```typescript
export * from './base.page';
export * from './dashboard.page';
// ... all others
```

**Step 6: Update tests/helpers/page-objects.ts**
```typescript
export * from './pages';
```

**Step 7: Verify and cleanup**
- Run `npx tsc --noEmit` in `tests/` or use `lsp_diagnostics`.
- `rm -rf tests/helpers/page-objects`

---

### Task 2: Split common.ts types into domains

**Files:**
- Create directory: `web/frontend/src/api/types/domains/`
- Create: `system-base.ts`, `market-data.ts`, `trading-ops.ts`, `strategy-types.ts`
- Modify: `web/frontend/src/api/types/common.ts`

**Step 1: Identify and Move System Base types**
- Types: `UnifiedResponse`, `APIResponse`, `BaseResponse`, `ErrorDetail`, `ErrorResponse`, `ResponseModel`, `MessageResponse`, `MessageStatus`, `OperationType`, `Pagination*`, `Sort*`, `DateField`, `TimestampField`, `MillisecondTimestampField`, `CurrencyField`, `PercentageField`, `PriceField`, etc.
- File: `web/frontend/src/api/types/domains/system-base.ts`

**Step 2: Identify and Move Market Data types**
- Types: `StockInfo`, `ConceptInfo`, `ConceptListResponse`, `IndustryInfo`, `IndustryListResponse`, `IndexQuote`, `IndexQuoteResponse`, `KLineCandleV2`, `KLineResponseV2`, `IndicatorSpec`, `IndicatorResult`, `IndicatorInfo`, `IndicatorMetadata`, `TechnicalIndicatorQueryModel`, `MarketOverview`, `LongHuBangItem`, `ChipRaceItem`, `ETFDataResponse`, `HeatmapStock`, `Announcement*`, `OHLCVData`, `IndicatorCalculate*`, etc.
- File: `web/frontend/src/api/types/domains/market-data.ts`
- Imports from `system-base.ts` if needed.

**Step 3: Identify and Move Trading Ops types**
- Types: `OrderRequest`, `OrderResponse`, `CancelOrderRequest`, `CancelOrderResponse`, `Position`, `PositionItem`, `PositionsResponse`, `TradeRecord`, `TradeHistoryItem`, `TradeHistoryResponse`, `TradeOrderModel`, `PortfolioSummary`, `AccountInfo`, `RiskAlert*`, `RiskMetrics*`, `RiskDashboardResponse`, etc.
- File: `web/frontend/src/api/types/domains/trading-ops.ts`
- Imports from `system-base.ts` and `market-data.ts` if needed.

**Step 4: Identify and Move Strategy & ML types**
- Types: `StrategyConfig`, `StrategyCreateRequest`, `StrategyUpdateRequest`, `StrategyParameter`, `StrategyStatus`, `StrategyType`, `BacktestExecuteRequest`, `BacktestResult`, `BacktestResultSummary`, `BacktestStatus`, `BacktestTrade`, `Algorithm*`, `Model*`, `Prediction*`, `FeatureGeneration*`, `TaskConfig`, `TaskExecution`, `TaskStatus`, `TaskType`, `TaskStatistics`, etc.
- File: `web/frontend/src/api/types/domains/strategy-types.ts`
- Imports from `system-base.ts`, `market-data.ts`, `trading-ops.ts`.

**Step 5: Create barrel and update common.ts**
- Update `web/frontend/src/api/types/common.ts` to re-export everything from `domains/*.ts`.

---

### Task 3: Final Verification

**Step 1: Check for any missing types**
- Ensure all 2235 lines are accounted for or re-exported.

**Step 2: Project-wide type check**
- `cd web/frontend && npx vue-tsc --noEmit`

**Step 3: Commit changes**
- Create separate commits for Page Objects and Common Types.
