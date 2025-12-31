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
} from '../types/market';

// Import new API types
import type {
  MarketOverviewDetailedResponse as MarketOverviewResponse,
  FundFlowAPIResponse,
  KLineDataResponse,
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
    apiResponse: UnifiedResponse<ApiMarketOverviewData>
  ): MarketOverviewVM {
    if (!apiResponse.success || !apiResponse.data) {
      console.warn('[MarketAdapter] API failed, using mock data:', apiResponse.message);
      return this.getMockMarketOverview();
    }

    try {
      const data = apiResponse.data;
      const rise = data.rise_fall_count?.rise || 0;
      const fall = data.rise_fall_count?.fall || 0;
      const flat = data.rise_fall_count?.flat || 0;
      const total = rise + fall + flat;

      return {
        marketStats: {
          totalStocks: total,
          risingStocks: rise,
          fallingStocks: fall,
          avgChangePercent: 0, // Not available in new API response
        },
        topEtfs: data.top_etfs?.map((etf) => ({
          symbol: etf.symbol || '',
          name: etf.name || '',
          latestPrice: 0, // Not available in new API response
          changePercent: etf.change_percent || 0,
          volume: 0, // Not available in new API response
        })) || [],
        chipRaces: [], // Fetched separately in new API
        longHuBang: [], // Fetched separately in new API
        lastUpdate: data.timestamp ? new Date(data.timestamp) : new Date(),
        marketIndex: data.market_index,
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
        date: item.tradeDate || '',
        mainInflow: item.superLargeNetInflow || 0,
        mainOutflow: item.largeNetInflow || 0,
        netInflow: item.mainNetInflow || 0,
        timestamp: item.tradeDate ? new Date(item.tradeDate).getTime() : Date.now(),
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
    apiResponse: UnifiedResponse<ApiKlineData>
  ): KLineChartData {
    if (!apiResponse.success || !apiResponse.data) {
      console.warn('[MarketAdapter] K-line API failed, using mock data:', apiResponse.message);
      return this.getMockKLineData();
    }

    try {
      const klineData = apiResponse.data;
      const points = klineData.data || [];

      const categoryData = points.map((p) => p.timestamp || '');
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
    apiResponse: UnifiedResponse<ApiChipRaceData>
  ): ChipRaceItem[] {
      if (!apiResponse.success || !apiResponse.data || !apiResponse.data.stocks) {
          return [];
      }
      return apiResponse.data.stocks.map(stock => ({
          symbol: stock.symbol || '',
          name: stock.name || '',
          raceAmount: stock.main_buy_amount || 0, // Using main_buy_amount as raceAmount
          changePercent: stock.race_ratio || 0 // Using race_ratio as changePercent for now, or 0
      }));
  }

  /**
   * Adapt Long Hu Bang data
   */
  static adaptLongHuBang(
    apiResponse: UnifiedResponse<ApiLongHuBangData>
  ): LongHuBangItem[] {
      if (!apiResponse.success || !apiResponse.data || !apiResponse.data.stocks) {
          return [];
      }
      return apiResponse.data.stocks.map(stock => ({
          symbol: stock.symbol || '',
          name: stock.name || '',
          netAmount: (stock.buy_amount || 0) - (stock.sell_amount || 0),
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
