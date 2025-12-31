/**
 * Market API Service
 *
 * Service layer for market data with full UnifiedResponse support.
 * All methods return complete UnifiedResponse objects for fallback handling.
 * This service ONLY handles API calls - no data transformation, caching, or mock fallback.
 */

import { apiGet } from '../apiClient';
import type { UnifiedResponse } from '../apiClient';
import type { components } from '../../types/market-data-api';

// Type aliases for easier usage
export type MarketOverviewData = components["schemas"]["MarketOverviewData"];
export type FundFlowData = components["schemas"]["FundFlowData"];
export type KlineData = components["schemas"]["KlineData"];
export type ETFData = components["schemas"]["ETFData"];
export type LongHuBangData = components["schemas"]["LongHuBangData"];
export type ChipRaceData = components["schemas"]["ChipRaceData"];

export class MarketApiService {
  private readonly baseUrl = '/api/market';

  /**
   * Get market overview
   * GET /api/market/overview
   */
  async getMarketOverview(): Promise<UnifiedResponse<MarketOverviewData>> {
    return apiGet<UnifiedResponse<MarketOverviewData>>(
      `${this.baseUrl}/overview`
    );
  }

  /**
   * Get fund flow data
   * GET /api/market/fund-flow
   */
  async getFundFlow(params: {
    symbol: string;
    timeframe?: "1" | "3" | "5" | "10";
    start_date?: string;
    end_date?: string;
  }): Promise<UnifiedResponse<FundFlowData>> {
    return apiGet<UnifiedResponse<FundFlowData>>(
      `${this.baseUrl}/fund-flow`,
      params
    );
  }

  /**
   * Get K-line data
   * GET /api/market/kline
   */
  async getKLineData(params: {
    symbol: string;
    interval?: "1m" | "5m" | "15m" | "30m" | "1h" | "1d";
    start_date?: string;
    end_date?: string;
    limit?: number;
  }): Promise<UnifiedResponse<KlineData>> {
    return apiGet<UnifiedResponse<KlineData>>(
      `${this.baseUrl}/kline`,
      params
    );
  }

  /**
   * Get ETF list
   * GET /api/market/etf/list
   */
  async getETFList(params?: {
    symbol?: string;
    keyword?: string;
    market?: "SH" | "SZ";
    category?: "股票" | "债券" | "商品" | "货币" | "QDII";
    limit?: number;
    offset?: number;
  }): Promise<UnifiedResponse<{
      etfs?: ETFData[];
      total?: number;
      page?: number;
      page_size?: number;
  }>> {
    return apiGet<UnifiedResponse<{
      etfs?: ETFData[];
      total?: number;
      page?: number;
      page_size?: number;
  }>>(
      `${this.baseUrl}/etf/list`,
      params
    );
  }

  /**
   * Get Long Hu Bang data
   * GET /api/market/lhb
   */
  async getLongHuBang(params?: {
    date?: string;
    type?: "rise" | "fall" | "all";
  }): Promise<UnifiedResponse<LongHuBangData>> {
    return apiGet<UnifiedResponse<LongHuBangData>>(
      `${this.baseUrl}/lhb`,
      params
    );
  }

  /**
   * Get Chip Race data
   * GET /api/market/chip-race
   */
  async getChipRace(params?: {
    date?: string;
    limit?: number;
  }): Promise<UnifiedResponse<ChipRaceData>> {
    return apiGet<UnifiedResponse<ChipRaceData>>(
      `${this.baseUrl}/chip-race`,
      params
    );
  }
}

// Export singleton instance
export const marketApiService = new MarketApiService();

// Export class for dependency injection
export default MarketApiService;
