/**
 * Market Data Service
 * Refactored 2026-02-14
 * 
 * Standardized service for all market-related API calls.
 * Aligned with Backend API v1.
 */

import { apiClient, apiGet } from '../apiClient.ts'
import type { UnifiedResponse } from '../types/common.ts'

type GenericDataResponse<T = unknown> = {
  data?: T
}

type QuotesResponse = {
  data?: { quotes?: unknown[] }
  quotes?: unknown[]
}

type StocksResponse = {
  data?: { stocks?: unknown[] }
  stocks?: unknown[]
}

export interface SectorFundFlowItem {
  sector_code?: string
  sector_name?: string
  sector_type?: string
  trade_date?: string | null
  timeframe?: string
  latest_price?: number
  change_percent?: number
  main_net_inflow?: number
  main_net_inflow_rate?: number
  leading_stock?: string | null
  leading_stock_change_percent?: number
}

type SectorFundFlowParams = {
  sectorType?: '行业' | '概念' | '地域'
  timeframe?: '今日' | '3日' | '5日' | '10日'
  limit?: number
}

async function getSectorFundFlow(
  params?: SectorFundFlowParams
): Promise<UnifiedResponse<SectorFundFlowItem[]>> {
  return apiGet<UnifiedResponse<SectorFundFlowItem[]>>('/v2/market/sector/fund-flow', {
    sector_type: params?.sectorType ?? '行业',
    timeframe: params?.timeframe ?? '今日',
    limit: params?.limit ?? 10
  })
}

export const marketService = {
  // 实时行情
  getQuotes: async (symbols?: string): Promise<unknown[]> => {
    const response = await apiClient.get<QuotesResponse>('/v1/market/quotes', {
      params: { symbols }
    })
    return response.data?.quotes || response.quotes || []
  },

  // 股票列表
  getStocks: async (params?: Record<string, unknown>): Promise<unknown[]> => {
    const response = await apiClient.get<StocksResponse>('/v1/market/stocks', { params })
    return response.data?.stocks || response.stocks || []
  },

  // 资金流向
  getFundFlow: async (params?: Record<string, unknown>): Promise<unknown> => {
    const response = await apiClient.get<GenericDataResponse<unknown>>('/v1/market/fund-flow', { params })
    return response.data ?? response
  },

  // K线数据
  getKline: async (
    params: { stock_code: string; period?: string; adjust?: string }
  ): Promise<unknown> => {
    const response = await apiClient.get<GenericDataResponse<unknown>>('/v1/market/kline', { params })
    return response.data ?? response
  },

  // 行业/概念资金流向
  getSectorFundFlow,

  // data/concept 稳定边界
  getConceptFundFlow: async (
    params?: Omit<SectorFundFlowParams, 'sectorType'>
  ): Promise<UnifiedResponse<SectorFundFlowItem[]>> => {
    return getSectorFundFlow({
      ...params,
      sectorType: '概念'
    })
  }
}

export default marketService
