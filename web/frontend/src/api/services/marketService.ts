/**
 * Market API Service
 *
 * Service layer for market data with full UnifiedResponse support.
 * All methods return complete UnifiedResponse objects for fallback handling.
 * This service ONLY handles API calls - no data transformation, caching, or mock fallback.
 */

import { apiGet } from '../apiClient';
import type { UnifiedResponse } from '../apiClient';
import type {
  MarketOverviewDetailedResponse as MarketOverviewResponse,
  FundFlowAPIResponse,
  KLineDataResponse,
} from '../types/generated-types';

export class MarketApiService {
  private readonly baseUrl = '/api/market';

  /**
   * Get market overview
   *
   * @returns UnifiedResponse with market overview data
   */
  async getMarketOverview(): Promise<UnifiedResponse<MarketOverviewResponse>> {
    return apiGet<UnifiedResponse<MarketOverviewResponse>>(
      `${this.baseUrl}/overview`
    );
  }

  /**
   * Get fund flow data
   *
   * @param params - Query parameters (startDate, endDate, market)
   * @returns UnifiedResponse with fund flow data
   */
  async getFundFlow(params?: {
    startDate?: string;
    endDate?: string;
    market?: string;
  }): Promise<UnifiedResponse<FundFlowAPIResponse>> {
    return apiGet<UnifiedResponse<FundFlowAPIResponse>>(
      `${this.baseUrl}/fund-flow`,
      params
    );
  }

  /**
   * Get K-line data
   *
   * @param params - K-line parameters (symbol, interval, startDate, endDate, limit)
   * @returns UnifiedResponse with K-line data
   */
  async getKLineData(params: {
    symbol: string;
    interval: '1m' | '5m' | '15m' | '30m' | '1h' | '4h' | '1d' | '1w' | '1M';
    startDate?: string;
    endDate?: string;
    limit?: number;
  }): Promise<UnifiedResponse<KLineDataResponse>> {
    return apiGet<UnifiedResponse<KLineDataResponse>>(
      `${this.baseUrl}/kline`,
      params
    );
  }

  /**
   * Get real-time market data for a symbol
   *
   * @param symbol - Stock symbol
   * @returns UnifiedResponse with real-time data
   */
  async getRealtimeData(symbol: string): Promise<UnifiedResponse<any>> {
    return apiGet<UnifiedResponse<any>>(
      `${this.baseUrl}/realtime/${symbol}`
    );
  }

  /**
   * Get market index data
   *
   * @param indices - Index codes (e.g., ['000001', '399001'])
   * @returns UnifiedResponse with index data
   */
  async getMarketIndices(indices?: string[]): Promise<UnifiedResponse<any[]>> {
    return apiGet<UnifiedResponse<any[]>>(
      `${this.baseUrl}/indices`,
      { indices }
    );
  }

  /**
   * Get sector performance data
   *
   * @param params - Query parameters (sector, limit)
   * @returns UnifiedResponse with sector data
   */
  async getSectorPerformance(params?: {
    sector?: string;
    limit?: number;
  }): Promise<UnifiedResponse<any[]>> {
    return apiGet<UnifiedResponse<any[]>>(
      `${this.baseUrl}/sectors`,
      params
    );
  }

  /**
   * Get top ETFs
   *
   * @param limit - Number of ETFs to return (default: 10)
   * @returns UnifiedResponse with ETF data
   */
  async getTopETFs(limit: number = 10): Promise<UnifiedResponse<any[]>> {
    return apiGet<UnifiedResponse<any[]>>(
      `${this.baseUrl}/top-etfs`,
      { limit }
    );
  }

  /**
   * Get chip race data (主力筹码比拼)
   *
   * @param params - Query parameters (raceType, tradeDate, limit)
   * @returns UnifiedResponse with chip race data
   */
  async getChipRaces(params?: {
    raceType?: string;
    tradeDate?: string;
    limit?: number;
  }): Promise<UnifiedResponse<any[]>> {
    return apiGet<UnifiedResponse<any[]>>(
      `${this.baseUrl}/chip-races`,
      params
    );
  }

  /**
   * Get long-hu-bang data (龙虎榜)
   *
   * @param params - Query parameters (tradeDate, limit)
   * @returns UnifiedResponse with long-hu-bang data
   */
  async getLongHuBang(params?: {
    tradeDate?: string;
    limit?: number;
  }): Promise<UnifiedResponse<any[]>> {
    return apiGet<UnifiedResponse<any[]>>(
      `${this.baseUrl}/long-hu-bang`,
      params
    );
  }

  /**
   * Get market breadth data
   *
   * @param params - Query parameters (market, date)
   * @returns UnifiedResponse with breadth data
   */
  async getMarketBreadth(params?: {
    market?: string;
    date?: string;
  }): Promise<UnifiedResponse<any>> {
    return apiGet<UnifiedResponse<any>>(
      `${this.baseUrl}/breadth`,
      params
    );
  }
}

// Export singleton instance
export const marketApiService = new MarketApiService();

// Export class for dependency injection
export default MarketApiService;
