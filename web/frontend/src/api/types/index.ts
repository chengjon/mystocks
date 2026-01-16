// Auto-generated index file for TypeScript types
// Generated at: 2026-01-15T21:06:03.936028

// Common types (includes BacktestResult, BacktestRequest, PositionItem, etc.)
// Note: Uses explicit exports to avoid duplicate conflicts
export type { Dict, List, BaseResponse, PagedResponse, APIResponse, ErrorDetail } from './common';
export type { AccountInfo, ActiveAlert, AlertLevel } from './common';
export type { BacktestRequest as BacktestParams, BacktestResponse, BacktestResultSummary, BacktestTrade, BacktestResult } from './common';
export type { PositionItem, Position, PositionsResponse } from './common';
export type { PortfolioSummary } from './common';
export type { StrategyCreateRequest as CreateStrategyRequest, StrategyUpdateRequest as UpdateStrategyRequest, StrategyConfig, StrategyListResponse } from './common';

// Admin domain types
export * from './admin';

// Analysis domain types
export * from './analysis';

// Market domain types (explicit exports to avoid conflicts with common.ts)
export type { MarketIndexItem, MarketOverview } from './market';
export type { MarketOverviewVM, FundFlowChartPoint, KLineChartData, ChipRaceItem, LongHuBangItem } from './market';

// Strategy domain types
export type { Strategy } from './strategy';
export type { StrategyPerformance } from './strategy';
export type { BacktestTask } from './strategy';
export type { BacktestResultVM } from './strategy';
export type { StrategyInfo, StrategyPredictionRequest, StrategyPredictionResponse, StrategyTrainingRequest, StrategyTrainingResponse, TechnicalIndicatorResponse } from './strategy';

// System domain types
export * from './system';

// Trading domain types
export * from './trading';
