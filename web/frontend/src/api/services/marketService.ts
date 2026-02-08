// web/frontend/src/api/services/marketService.ts

import apiClient from '../apiClient'

export const marketService = {
  // Get Real-time Quote (Snapshot)
  getQuote: async (symbol: string) => {
    const response = await apiClient.get<any>(`/api/market/quote/${symbol}`)
    return response.data || response // Adapt based on if data is wrapped
  },

  // Get Intraday Trend (Line Chart)
  getTrend: async (symbol: string) => {
    // In real API this might be /api/market/trend or derived from kline
    // For now we map it to kline with '1m' or specific trend endpoint if exists
    // Let's assume we use kline for trend or a specific trend endpoint
    // If mockApiClient doesn't handle /trend, we can add it or use kline
    // Let's use a specific endpoint for clarity
    const response = await apiClient.get<any>(`/api/market/trend/${symbol}`)
    return response.data || response
  },

  // Get K-Line History (Candlestick)
  getKLine: async (symbol: string, period: string = '1d') => {
    const response = await apiClient.get<any>('/api/market/kline', {
        params: { symbol, period }
    })
    return {
        symbol,
        period,
        data: response.data || response // mockApiClient returns candles directly or wrapped
    }
  }
}
