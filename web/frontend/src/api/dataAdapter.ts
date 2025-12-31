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
} from '@/api/adapters/marketAdapter'

// Strategy Data Adapters
export {
  StrategyAdapter,
  default as strategyAdapter
} from '@/api/adapters/strategyAdapter'

// Utility Adapters
export {
  DataAdapter,
  default as dataAdapter
} from '@/utils/adapters'

// Trade Adapters
export {
  TradeAdapter,
  default as tradeAdapter
} from '@/utils/trade-adapters'

// Monitoring Adapters
export {
  MonitoringAdapter,
  default as monitoringAdapter
} from '@/utils/monitoring-adapters'

// Strategy Adapters
export {
  StrategyAdapter as StrategyAdapters,
  default as strategyAdapters
} from '@/utils/strategy-adapters'

// User Adapters
export {
  UserAdapter,
  default as userAdapter
} from '@/utils/user-adapters'

// ============================================
// Re-export Types
// ============================================

// Market Types
export type { MarketOverviewVM } from '@/utils/adapters'
export type { FundFlowChartPoint, KLineChartData } from '@/utils/adapters'
export type { MarketOverviewData } from '@/api/types/market'
export type { MarketOverviewDetailedResponse as MarketOverviewResponse, KLineDataResponse } from '@/api/types/generated-types'

// Strategy Types
export type { Strategy, StrategyListResponse } from '@/api/types/strategy'
export type { BacktestTask, BacktestResult, BacktestParams } from '@/api/types/strategy'

// Trade Types
export type { OrderVM, PositionVM, AccountOverviewVM, TradeHistoryVM } from '@/utils/trade-adapters'

// Monitoring Types
export type { SystemStatusVM, MonitoringAlertVM, LogEntryVM, DataQualityVM } from '@/utils/monitoring-adapters'

// User Types
export type { UserProfileVM, WatchlistVM, NotificationVM, UserPreferencesVM } from '@/utils/user-adapters'
