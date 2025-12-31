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
    apiResponse: UnifiedResponse<MarketOverviewResponse>
  ): MarketOverviewVM {
    if (!apiResponse.success || !apiResponse.data) {
      console.warn('[MarketAdapter] API failed, using mock data:', apiResponse.message);
      return this.getMockMarketOverview();
    }

    try {
      const data = apiResponse.data;

      return {
        marketStats: {
          totalStocks: data.marketStats?.totalStocks || 0,
          risingStocks: data.marketStats?.risingStocks || 0,
          fallingStocks: data.marketStats?.fallingStocks || 0,
          avgChangePercent: data.marketStats?.avgChangePercent || 0,
        },
        topEtfs: data.topEtfs?.map((etf) => ({
          symbol: etf.symbol || '',
          name: etf.name || '',
          latestPrice: etf.latestPrice || 0,
          changePercent: etf.changePercent || 0,
          volume: etf.volume || 0,
        })) || [],
        chipRaces: data.chipRaces?.map((race) => ({
          symbol: race.symbol || '',
          name: race.name || '',
          raceAmount: race.raceAmount || 0,
          changePercent: race.changePercent || 0,
        })) || [],
        longHuBang: data.longHuBang?.map((item) => ({
          symbol: item.symbol || '',
          name: item.name || '',
          netAmount: item.netAmount || 0,
          reason: item.reason || '',
        })) || [],
        lastUpdate: data.timestamp ? new Date(data.timestamp) : new Date(),
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
    apiResponse: UnifiedResponse<KLineDataResponse>
  ): KLineChartData {
    if (!apiResponse.success || !apiResponse.data) {
      console.warn('[MarketAdapter] K-line API failed, using mock data:', apiResponse.message);
      return this.getMockKLineData();
    }

    try {
      const klineData = apiResponse.data;

      const categoryData = klineData.data?.map((candle) => candle.datetime || '') || [];
      const values = klineData.data?.map((candle) => [
        candle.open || 0,
        candle.close || 0,
        candle.low || 0,
        candle.high || 0,
      ]) || [];
      const volumes = klineData.data?.map((candle) => candle.volume || 0) || [];

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

  // ==================== Mock Data Fallback Methods ====================

  /**
   * Get mock market overview data
   */
  private static getMockMarketOverview(): MarketOverviewVM {
    console.log('[MarketAdapter] 📦 Using Mock Market Overview data');

    // Wrap mock data in UnifiedResponse format
    const mockResponse: UnifiedResponse<MarketOverviewResponse> = {
      success: true,
      code: 200,
      message: 'Mock data',
      data: mockMarketOverview,
      timestamp: new Date().toISOString(),
      request_id: 'mock',
      errors: null,
    };

    return this.adaptMarketOverview(mockResponse);
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
   *
   * @param data - Market overview data to validate
   * @returns True if valid, false otherwise
   */
  static validateMarketOverview(data: MarketOverviewVM): boolean {
    if (!data.marketStats) {
      console.error('[MarketAdapter] Invalid market overview: missing marketStats');
      return false;
    }

    if (data.marketStats.totalStocks < 0) {
      console.error('[MarketAdapter] Invalid market overview: negative totalStocks');
      return false;
    }

    return true;
  }

  /**
   * Validate fund flow parameters
   *
   * @param params - Fund flow parameters to validate
   * @returns True if valid, false otherwise
   */
  static validateFundFlowParams(params: {
    startDate?: string;
    endDate?: string;
    market?: string;
  }): boolean {
    if (params.startDate && params.endDate) {
      const start = new Date(params.startDate);
      const end = new Date(params.endDate);

      if (start > end) {
        console.error('[MarketAdapter] Invalid fund flow params: startDate > endDate');
        return false;
      }
    }

    return true;
  }

  /**
   * Validate K-line parameters
   *
   * @param params - K-line parameters to validate
   * @returns True if valid, false otherwise
   */
  static validateKLineParams(params: {
    symbol: string;
    interval: string;
    startDate?: string;
    endDate?: string;
  }): boolean {
    if (!params.symbol) {
      console.error('[MarketAdapter] Invalid K-line params: missing symbol');
      return false;
    }

    const validIntervals = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M'];
    if (!validIntervals.includes(params.interval)) {
      console.error('[MarketAdapter] Invalid K-line params: invalid interval');
      return false;
    }

    if (params.startDate && params.endDate) {
      const start = new Date(params.startDate);
      const end = new Date(params.endDate);

      if (start > end) {
        console.error('[MarketAdapter] Invalid K-line params: startDate > endDate');
        return false;
      }
    }

    return true;
  }
}

export default MarketAdapter;
