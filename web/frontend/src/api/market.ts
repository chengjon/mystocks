/**
 * Market Data API Service
 *
 * Provides methods for fetching market data from the backend.
 */

import { request } from '@/utils/request'
import { DataAdapter } from '@/utils/adapters'
import type {
  MarketOverviewResponse,
  FundFlowResponse,
  KLineDataResponse
} from '@/api/types/generated-types'
import type {
  MarketOverviewVM,
  FundFlowChartPoint,
  KLineChartData,
  StockSearchVM
} from '@/utils/adapters'

class MarketApiService {
  private baseUrl = '/api/market'

  /**
   * Get market overview data
   */
  async getMarketOverview(): Promise<MarketOverviewVM> {
    const rawData = await request.get<MarketOverviewResponse>(`${this.baseUrl}/overview`)
    return DataAdapter.toMarketOverviewVM(rawData)
  }

  /**
   * Get fund flow data
   */
  async getFundFlow(params?: {
    startDate?: string
    endDate?: string
    market?: string
  }): Promise<FundFlowChartPoint[]> {
    const rawData = await request.get<FundFlowResponse>(`${this.baseUrl}/fund-flow`, {
      params
    })
    return DataAdapter.toFundFlowChartData(rawData)
  }

  /**
   * Get K-line data
   */
  async getKLineData(params: {
    symbol: string
    interval: '1m' | '5m' | '15m' | '30m' | '1h' | '4h' | '1d' | '1w' | '1M'
    startDate?: string
    endDate?: string
    limit?: number
  }): Promise<KLineChartData> {
    const rawData = await request.get<KLineDataResponse>(`${this.baseUrl}/kline`, {
      params
    })
    return DataAdapter.toKLineChartData(rawData)
  }

  /**
   * Search stocks
   */
  async searchStocks(query: string, limit: number = 20): Promise<StockSearchVM[]> {
    const rawData = await request.get(`/api/stock-search`, {
      params: { q: query, limit }
    })
    return DataAdapter.toStockSearchVM(rawData)
  }

  /**
   * Get real-time quote
   */
  async getRealtimeQuote(symbol: string) {
    return request.get(`${this.baseUrl}/quote`, {
      params: { symbol }
    })
  }

  /**
   * Get market heatmap data
   */
  async getMarketHeatmap() {
    return request.get(`${this.baseUrl}/heatmap`)
  }

  /**
   * Get sector performance
   */
  async getSectorPerformance() {
    return request.get(`${this.baseUrl}/sectors`)
  }

  /**
   * Get market statistics
   */
  async getMarketStatistics() {
    return request.get(`${this.baseUrl}/statistics`)
  }

  /**
   * Refresh market data
   */
  async refreshMarketData(dataType: string) {
    return request.post(`${this.baseUrl}/refresh`, { dataType })
  }
}

// Export singleton instance
export const marketApi = new MarketApiService()

// Export class for dependency injection
export default MarketApiService
