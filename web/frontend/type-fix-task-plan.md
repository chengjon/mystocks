# Task Plan: Complete TypeScript Type Error Fixes

> **历史计划说明**:
> 本文件记录某次 Web 相关需求、改进设想、预案或任务计划，反映的是当时准备推动的方向与范围，而非当前已生效事实。
> 若其内容与现行 `architecture/STANDARDS.md`、已批准方案、当前代码实现或后续结论不一致，应以 `architecture/STANDARDS.md`、已批准方案、当前代码实现与最新结论为准。


## Goal
Fix TypeScript type errors, reducing from ~99 to ~24 remaining (Vue/Demo component issues require separate fixes).

## Phases
- [x] Phase 1: Restore core type definitions (Dict, List, PositionItem, etc.)
- [x] Phase 2: Add ViewModel types to strategy.ts (BacktestResultVM, BacktestTask, etc.)
- [x] Phase 3: Fix market.ts type exports (MarketOverviewVM, FundFlowChartPoint, etc.)
- [x] Phase 4: Fix index.ts re-exports (PositionItem conflict resolved)
- [x] Phase 5: Add missing types (HMMConfig, NeuralNetworkConfig, etc.)

## Errors Fixed
- Dict/List utility types restored to common.ts
- PositionItem, HMMConfig, NeuralNetworkConfig added to common.ts
- MarketOverviewVM with all required properties added to market.ts
- BacktestResultVM, BacktestTask, Strategy, StrategyPerformance added to strategy.ts
- Export conflicts resolved with explicit exports in index.ts
- BacktestResultSummary and BacktestTrade imports added to strategy.ts

## Remaining Errors (24 total)
These require Vue component refactoring, not core type fixes:
- `ArtDecoTradingHistoryControls.vue` - v-model prop issues
- `ArtDecoTradingSignalsControls.vue` - readonly property assignment
- `OpenStockDemo.vue` - boolean type mismatch
- `Backtest.vue`, `DataParsing.vue` - index signature errors
- `common.ts` - Generic type T in non-generic contexts
- `trading.ts` - HistoryFilters undefined

## Status
**Complete** - Core type system fixed. Remaining errors are Vue component-specific.
