/**
 * Market Data API Service
 *
 * Provides methods for fetching market data from the backend.
 */

import { request } from '@/utils/request.ts'
import { DataAdapter } from '@/utils/adapters.ts'
import type {
  MarketOverviewResponse,
  FundFlowResponse,
  KlineResponse
} from '@/api/types/generated-types.ts'
import type {
  MarketOverviewVM,
  FundFlowChartPoint,
  KLineChartData,
  StockSearchVM
} from '@/utils/adapters.ts'

interface StockSearchResult {
  symbol?: string
  name?: string
  market?: string
  current?: number
  changePercent?: number
  change?: number
}

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
    const rawData = await request.get<KlineResponse>(`${this.baseUrl}/kline`, {
      params
    })
    return DataAdapter.toKLineChartData(rawData)
  }

  /**
   * Search stocks
   */
  async searchStocks(query: string, limit: number = 20): Promise<StockSearchVM[]> {
    const rawData = await request.get<StockSearchResult[]>(`/api/stock-search`, {
      params: { q: query, limit }
    })
    return DataAdapter.toStockSearchVM(rawData as unknown as StockSearchResult[])
  }

  /**
   * Get real-time quote
   */
  async getRealtimeQuote(symbol: string): Promise<unknown> {
    return request.get(`${this.baseUrl}/quote`, {
      params: { symbol }
    })
  }

  /**
   * Get market heatmap data
   */
  async getMarketHeatmap(): Promise<unknown> {
    return request.get(`${this.baseUrl}/heatmap`)
  }

  /**
   * Get sector performance
   */
  async getSectorPerformance(): Promise<unknown> {
    return request.get(`${this.baseUrl}/sectors`)
  }

  /**
   * Get market statistics
   */
  async getMarketStatistics(): Promise<unknown> {
    return request.get(`${this.baseUrl}/statistics`)
  }

  /**
   * Refresh market data
   */
  async refreshMarketData(dataType: string): Promise<unknown> {
    return request.post(`${this.baseUrl}/refresh`, { dataType })
  }
}

// Export singleton instance
export const marketApi = new MarketApiService()

// Export class for dependency injection
export default MarketApiService
