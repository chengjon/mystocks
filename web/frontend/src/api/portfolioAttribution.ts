import { apiClient } from './apiClient.ts'
import type { UnifiedResponse } from './types/common.ts'

export interface AttributionSnapshotMeta {
  analysis_date?: string
  constituent_count?: number
  total_weight?: number
  total_market_value?: number | null
  total_return?: number
  stale?: boolean
  stale_reason?: string | null
}

export interface AttributionIndustryBreakdown {
  portfolio_weight?: number
  benchmark_weight?: number
  portfolio_return?: number
  benchmark_return?: number
  allocation_effect?: number
  selection_effect?: number
  interaction_effect?: number
}

export interface BrinsonBreakdown {
  allocation_effect?: number
  selection_effect?: number
  interaction_effect?: number
  industry_breakdown?: Record<string, AttributionIndustryBreakdown>
}

export interface FactorExposureDetail {
  portfolio_exposure?: number
  benchmark_exposure?: number
  active_exposure?: number
}

export interface FactorAttributionPayload {
  factor_exposures?: Record<string, FactorExposureDetail>
  factor_contributions?: Record<string, number>
  specific_return?: number
}

export interface AttributionContributionRow {
  symbol: string
  industry?: string
  weight?: number
  return_rate?: number
  contribution_value?: number
}

export interface AttributionAnalysisResponse {
  analysis_date?: string
  snapshot_meta?: AttributionSnapshotMeta
  benchmark_meta?: AttributionSnapshotMeta
  brinson?: BrinsonBreakdown
  factor_attribution?: FactorAttributionPayload
  top_contributors?: AttributionContributionRow[]
  top_detractors?: AttributionContributionRow[]
}

export interface PositionAttributionQuery {
  date?: string
  sessionId?: string
}

export const getPositionAttribution = (
  query: PositionAttributionQuery = {},
): Promise<UnifiedResponse<AttributionAnalysisResponse>> => {
  const params: Record<string, string> = {}
  if (query.date) {
    params.date = query.date
  }
  if (query.sessionId) {
    params.session_id = query.sessionId
  }
  return apiClient.get<UnifiedResponse<AttributionAnalysisResponse>>('/v1/positions/attribution', { params })
}

export const getBacktestAttribution = (
  backtestId: number,
): Promise<UnifiedResponse<AttributionAnalysisResponse>> => (
  apiClient.get<UnifiedResponse<AttributionAnalysisResponse>>(`/v1/backtest/${backtestId}/attribution`)
)
