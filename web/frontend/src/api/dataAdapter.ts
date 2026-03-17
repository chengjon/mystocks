/**
 * Unified Data Adapter Layer
 *
 * Central export point for all data transformation adapters.
 * Transforms API responses (DTOs) into ViewModels for UI consumption.
 */

// Market Data Adapters
export {
  MarketAdapter,
  default as marketAdapter
} from '@/api/adapters/marketAdapter.ts'

// Strategy Data Adapters
export {
  StrategyAdapter,
  default as strategyAdapter
} from '@/api/adapters/strategyAdapter.ts'

// Utility Adapters
export {
  DataAdapter,
  default as dataAdapter
} from '@/utils/adapters.ts'

// Trade Adapters
export {
  TradeAdapter,
  default as tradeAdapter
} from '@/utils/trade-adapters.ts'

// Monitoring Adapters
export {
  MonitoringAdapter,
  default as monitoringAdapter
} from '@/utils/monitoring-adapters.ts'

// Strategy Adapters
export {
  StrategyAdapter as StrategyAdapters,
  default as strategyAdapters
} from '@/utils/strategy-adapters.ts'

// User Adapters
export {
  UserAdapter,
  default as userAdapter
} from '@/utils/user-adapters.ts'

// ============================================
// Re-export Types
// ============================================

// Market Types
export type { MarketOverviewVM } from '@/api/types/extensions/index.ts'
export type { MarketOverview } from '@/api/types/market.ts'
export type { FundFlowChartPoint, KLineChartData } from '@/api/types/extensions/index.ts'
export type { MarketOverviewDetailedResponse as MarketOverviewResponse, KLineDataResponse } from '@/api/types/generated-types.ts'

// Strategy Types
export type { StrategyVM as Strategy, StrategyListResponseVM as StrategyListResponse } from '@/api/types/extensions/index.ts'
export type { BacktestRequestVM as BacktestTask, BacktestResultVM as BacktestResult } from '@/api/types/extensions/index.ts'

// Trade Types
export type { OrderVM, PositionVM, AccountOverviewVM, TradeHistoryVM } from '@/utils/trade-adapters.ts'

// Monitoring Types
export type { SystemStatusVM, MonitoringAlertVM, LogEntryVM, DataQualityVM } from '@/utils/monitoring-adapters.ts'

// User Types
export type { UserProfileVM, WatchlistVM, NotificationVM, UserPreferencesVM } from '@/utils/user-adapters.ts'
