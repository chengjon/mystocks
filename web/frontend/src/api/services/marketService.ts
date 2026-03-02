/**
 * Market Data Service
 * Refactored 2026-02-14
 * 
 * Standardized service for all market-related API calls.
 * Aligned with Backend API v1.
 */

import { apiClient } from '../apiClient'

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

export const marketService = {
  // 实时行情
  getQuotes: async (symbols?: string) => {
    const response = await apiClient.get<QuotesResponse>('/v1/market/quotes', {
      params: { symbols }
    })
    return response.data?.quotes || response.quotes || []
  },

  // 股票列表
  getStocks: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get<StocksResponse>('/v1/market/stocks', { params })
    return response.data?.stocks || response.stocks || []
  },

  // 资金流向
  getFundFlow: async (params?: Record<string, unknown>) => {
    const response = await apiClient.get<GenericDataResponse<unknown>>('/v1/market/fund-flow', { params })
    return response.data ?? response
  },

  // K线数据
  getKline: async (params: { stock_code: string; period?: string; adjust?: string }) => {
    const response = await apiClient.get<GenericDataResponse<unknown>>('/v1/market/kline', { params })
    return response.data ?? response
  }
}

export default marketService
