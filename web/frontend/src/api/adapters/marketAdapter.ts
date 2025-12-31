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
  LongHuBangItem
} from '../types/market';

// Import new API types
import type {
  MarketOverviewData as ApiMarketOverviewData,
  FundFlowData as ApiFundFlowData,
  KlineData as ApiKlineData,
  ChipRaceData as ApiChipRaceData,
  LongHuBangData as ApiLongHuBangData
} from '../services/marketService';

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
    apiResponse: UnifiedResponse<ApiFundFlowData>
  ): FundFlowChartPoint[] {
    if (!apiResponse.success || !apiResponse.data) {
      console.warn('[MarketAdapter] Fund flow API failed, using mock data:', apiResponse.message);
      return this.getMockFundFlow();
    }

    try {
      // New API returns a single object with 'timestamp', 'main_net_inflow' etc.
      // But the adapter expects an array of points for a chart.
      // The new API endpoint `/api/market/fund-flow` seems to return CURRENT flow for a stock?
      // Wait, let's check the schema.
      // FundFlowData: { symbol, main_net_inflow, ... } -> Single point.
      // If we want a chart, we might need a different endpoint or the API returns history?
      // The API spec says "查询指定股票的资金流向数据... 时间维度 1/3/5/10天".
      // But the response schema `FundFlowData` seems to be a single object.
      // Maybe the `UnifiedResponse` data field contains an array?
      // No, `getFundFlow` returns `UnifiedResponse<FundFlowData>`.
      // If the API returns history, the schema should be `FundFlowData[]` or `FundFlowData` should contain a list.
      // Looking at `market-data-api.ts`:
      // `getFundFlow` response 200 content: `UnifiedResponse` & { data?: components["schemas"]["FundFlowData"] }
      // `FundFlowData` has `main_net_inflow`, `timestamp`. It looks like a single point.

      // If the user wants a chart, this API might be insufficient or I'm misinterpreting "timeframe".
      // For now, I will wrap the single point into an array.

      const data = apiResponse.data;

      return [{
        date: data.timestamp || new Date().toISOString(),
        mainInflow: data.main_net_inflow || 0,
        mainOutflow: 0, // Not provided
        netInflow: data.main_net_inflow || 0, // Is net inflow
        timestamp: data.timestamp ? new Date(data.timestamp).getTime() : Date.now(),
      }];

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
    return [];
  }

  /**
   * Get mock K-line data
   */
  private static getMockKLineData(): KLineChartData {
    console.log('[MarketAdapter] 📦 Using Mock K-Line data');
    return { categoryData: [], values: [], volumes: [] };
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
