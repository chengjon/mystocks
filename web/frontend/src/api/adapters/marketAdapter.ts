/**
 * Market Data Adapter
 *
 * Handles data transformation between API responses and frontend models.
 * Implements fallback to mock data on API failures.
 */

import type { UnifiedResponse } from '../apiClient';
import type {
  MarketOverviewVM,
  FundFlowChartPoint,
  KLineChartData,
  ChipRaceItem,
  LongHuBangItem,
} from '../types/market';

// Import new API types
import type {
  MarketOverviewDetailedResponse as MarketOverviewResponse,
  FundFlowAPIResponse,
  KLineDataResponse,
  ChipRaceResponse,
  LongHuBangResponse,
} from '../types/generated-types';

// Import Mock data as fallback
import mockMarketOverview from '@/mock/marketOverview';
import mockFundFlow from '@/mock/fundFlow';
import mockKLineData from '@/mock/klineData';

export class MarketAdapter {
  /**
   * Adapt market overview from API response
   *
   * @param apiResponse - Raw API response
   * @returns Adapted MarketOverviewVM object (falls back to mock on error)
   */
  static adaptMarketOverview(
    apiResponse: UnifiedResponse<MarketOverviewResponse>
  ): MarketOverviewVM {
    if (!apiResponse.success || !apiResponse.data) {
      console.warn('[MarketAdapter] API failed, using mock data:', apiResponse.message);
      return this.getMockMarketOverview();
    }

    try {
      const data = apiResponse.data;

      // Handle missing fields gracefully - backend API may not have all fields yet
      // Use type assertions to access fields that may not be in the type definition
      const apiData = data as any;

      const rise = apiData.rise_fall_count?.rise || 0;
      const fall = apiData.rise_fall_count?.fall || 0;
      const flat = apiData.rise_fall_count?.flat || 0;
      const total = rise + fall + flat;

      return {
        marketStats: {
          totalStocks: total,
          risingStocks: rise,
          fallingStocks: fall,
          avgChangePercent: 0, // Not available in new API response
        },
        topEtfs: apiData.top_etfs?.map((etf: any) => ({
          symbol: etf.symbol || '',
          name: etf.name || '',
          latestPrice: 0, // Not available in new API response
          changePercent: etf.change_percent || 0,
          volume: 0, // Not available in new API response
        })) || [],
        chipRaces: [], // Fetched separately in new API
        longHuBang: [], // Fetched separately in new API
        lastUpdate: apiData.timestamp ? new Date(apiData.timestamp) : new Date(),
        marketIndex: apiData.market_index,
      };
    } catch (error) {
      console.error('[MarketAdapter] Failed to adapt market overview:', error);
      return this.getMockMarketOverview();
    }
  }

  /**
   * Adapt fund flow data from API response
   *
   * @param apiResponse - Raw API response
   * @returns Array of adapted FundFlowChartPoint objects (falls back to mock on error)
   */
  static adaptFundFlow(
    apiResponse: UnifiedResponse<FundFlowAPIResponse>
  ): FundFlowChartPoint[] {
    if (!apiResponse.success || !apiResponse.data) {
      console.warn('[MarketAdapter] Fund flow API failed, using mock data:', apiResponse.message);
      return this.getMockFundFlow();
    }

    try {
      // Access fundFlow array directly from the response data
      const fundFlowData = apiResponse.data?.fundFlow || [];

      return fundFlowData.map((item) => ({
        date: item.trade_date || '',
        mainInflow: item.super_large_net_inflow || 0,
        mainOutflow: item.large_net_inflow || 0,
        netInflow: item.main_net_inflow || 0,
        timestamp: item.trade_date ? new Date(item.trade_date).getTime() : Date.now(),
      }));
    } catch (error) {
      console.error('[MarketAdapter] Failed to adapt fund flow:', error);
      return this.getMockFundFlow();
    }
  }

  /**
   * Adapt K-line data from API response
   *
   * @param apiResponse - Raw API response
   * @returns Adapted KLineChartData object (falls back to mock on error)
   */
  static adaptKLineData(
    apiResponse: UnifiedResponse<KLineDataResponse>
  ): KLineChartData {
    if (!apiResponse.success || !apiResponse.data) {
      console.warn('[MarketAdapter] K-line API failed, using mock data:', apiResponse.message);
      return this.getMockKLineData();
    }

    try {
      const klineData = apiResponse.data;
      const points = klineData.data || [];

      const categoryData = points.map((p) => p.datetime || '');
      const values = points.map((p) => [
        p.open || 0,
        p.close || 0,
        p.low || 0,
        p.high || 0,
      ]);
      const volumes = points.map((p) => p.volume || 0);

      return {
        categoryData,
        values,
        volumes,
      };
    } catch (error) {
      console.error('[MarketAdapter] Failed to adapt K-line data:', error);
      return this.getMockKLineData();
    }
  }

  /**
   * Adapt Chip Race data
   */
  static adaptChipRace(
    apiResponse: UnifiedResponse<ChipRaceResponse | ChipRaceResponse[]>
  ): ChipRaceItem[] {
      if (!apiResponse.success || !apiResponse.data) {
          return [];
      }
      // Handle both single item and array responses
      const items = Array.isArray(apiResponse.data) ? apiResponse.data : [apiResponse.data];
      return items.map(stock => ({
          symbol: stock.symbol || '',
          name: stock.name || '',
          raceAmount: stock.race_amount || 0,
          changePercent: stock.change_percent || 0
      }));
  }

  /**
   * Adapt Long Hu Bang data
   */
  static adaptLongHuBang(
    apiResponse: UnifiedResponse<LongHuBangResponse | LongHuBangResponse[]>
  ): LongHuBangItem[] {
      if (!apiResponse.success || !apiResponse.data) {
          return [];
      }
      // Handle both single item and array responses
      const items = Array.isArray(apiResponse.data) ? apiResponse.data : [apiResponse.data];
      return items.map(stock => ({
          symbol: stock.symbol || '',
          name: stock.name || '',
          netAmount: stock.net_amount || 0,
          reason: stock.reason || ''
      }));
  }

  // ==================== Mock Data Fallback Methods ====================

  /**
   * Get mock market overview data
   */
  private static getMockMarketOverview(): MarketOverviewVM {
    console.log('[MarketAdapter] 📦 Using Mock Market Overview data');
    // Basic fallback that matches VM structure
    return {
        marketStats: { totalStocks: 0, risingStocks: 0, fallingStocks: 0, avgChangePercent: 0 },
        topEtfs: [],
        chipRaces: [],
        longHuBang: [],
        lastUpdate: new Date()
    };
  }

  /**
   * Get mock fund flow data
   */
  private static getMockFundFlow(): FundFlowChartPoint[] {
    console.log('[MarketAdapter] 📦 Using Mock Fund Flow data');

    // mockFundFlow is in UnifiedResponse format - extract the data part and wrap properly
    const mockResponse: UnifiedResponse<FundFlowAPIResponse> = {
      success: mockFundFlow.success,
      code: mockFundFlow.code,
      message: mockFundFlow.message,
      data: mockFundFlow.data,
      timestamp: mockFundFlow.timestamp,
      request_id: mockFundFlow.request_id,
      errors: mockFundFlow.errors,
    };

    return this.adaptFundFlow(mockResponse);
  }

  /**
   * Get mock K-line data
   */
  private static getMockKLineData(): KLineChartData {
    console.log('[MarketAdapter] 📦 Using Mock K-Line data');

    // Wrap mock data in KlineResponse structure
    const mockWrappedResponse: UnifiedResponse<KLineDataResponse> = {
      success: true,
      code: 200,
      message: 'Mock data',
      data: {
        symbol: '000001',
        period: '1d',
        data: mockKLineData,
        count: mockKLineData.length,
      },
      timestamp: new Date().toISOString(),
      request_id: 'mock',
      errors: null,
    };

    return this.adaptKLineData(mockWrappedResponse);
  }

  // ==================== Validation Methods ====================

  /**
   * Validate market overview data
   */
  static validateMarketOverview(data: MarketOverviewVM): boolean {
    if (!data.marketStats) return false;
    return true;
  }
}

export default MarketAdapter;
