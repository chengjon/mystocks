import type {
  MarketOverviewDetailedResponse,
  PortfolioSummary,
  RiskAlertSummary,
  WatchlistSummary
} from '@/api/types/common.ts'

export interface UnifiedResponse<T> {
  success: boolean
  code: number
  message: string
  data: T
  timestamp: string
  request_id: string
  errors: Record<string, unknown> | null
}

export interface ChartDataPoint {
  name: string
  value: number
  change_percent: number
}

export interface DashboardSummary {
  marketOverview?: MarketOverviewDetailedResponse
  watchlist?: WatchlistSummary
  portfolio?: PortfolioSummary
  riskAlerts?: RiskAlertSummary
}

export interface IndustryConceptData {
  industry_name: string
  avg_change: number
  stock_count: number
}

export interface EtfItem {
  symbol: string
  name: string
  latest_price?: number
  change_percent?: number
  change_amount?: number
  volume?: number
  amount?: number
  created_at?: string
  trade_date?: string
}

export interface MarketOverviewData {
  up_count?: number
  down_count?: number
  flat_count?: number
  total_volume?: number
  total_turnover?: number
  top_gainers?: unknown[]
  top_losers?: unknown[]
}

export interface PortfolioData {
  total_value?: number
  total_cost?: number
  profit_loss?: number
  profit_loss_percent?: number
  positions?: unknown[]
}

export interface IndustryPerformanceItem {
  name?: string
  industry_name?: string
  change_percent?: number
  avg_change?: number
  stock_count?: number
}

export interface SectorFundFlowItem {
  sector_name?: string
  sector_code?: string
  main_net_inflow?: number
  main_net_inflow_rate?: number
}

export interface ConceptStockItem {
  concept_name?: string
  name?: string
}

export interface StrategyItem {
  status?: string
  is_active?: boolean
}

export interface StockSearchItem {
  code?: string
  symbol?: string
  name?: string
  price?: number
  latest_price?: number
  change_percent?: number
  chg_pct?: number
}

export interface WencaiResponse {
  results?: StockSearchItem[]
}
