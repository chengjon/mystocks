/**
 * Common Types
 *
 * Shared type definitions used across the application
 */

/**
 * API Response wrapper
 */
export interface ApiResponse<T = any> {
  code: number
  data: T
  message: string
  timestamp?: number
}

/**
 * Menu item for navigation
 */
export interface MenuItem {
  key: string
  label: string
  icon?: string
  path?: string
  children?: MenuItem[]
  disabled?: boolean
  hidden?: boolean
}

/**
 * Pagination parameters
 */
export interface PaginationParams {
  page: number
  pageSize: number
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

/**
 * Paginated response
 */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

/**
 * Stock symbol
 */
export type StockSymbol = string

/**
 * Date range
 */
export interface DateRange {
  start: string | Date
  end: string | Date
}

/**
 * Time interval for K-line data
 */
export type TimeInterval = '1m' | '5m' | '15m' | '30m' | '1h' | '1d' | '1w' | '1M'

/**
 * Market data types
 */
export interface MarketData {
  symbol: StockSymbol
  name: string
  price: number
  change: number
  changePercent: number
  volume: number
  amount: number
  timestamp: number
}

/**
 * K-line (candlestick) data
 */
export interface KlineData {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount: number
}

/**
 * Technical indicator value
 */
export interface IndicatorValue {
  timestamp: number
  value: number
  name: string
}

/**
 * Trading signal
 */
export interface TradingSignal {
  id: string
  symbol: StockSymbol
  type: 'buy' | 'sell' | 'hold'
  confidence: number
  reason: string
  timestamp: number
}
