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
} from '../types/extensions';
import type {
  ChipRaceItem,
  LongHuBangItem,
} from '../types/common';

// Import new API types
import type {
  MarketOverviewDetailedResponse as MarketOverviewResponse,
  FundFlowAPIResponse,
  KLineDataResponse,
  ChipRaceResponse,
  LongHuBangResponse,
} from '../types/generated-types';

// Import Mock data as fallback
// import mockMarketOverview from '@/mock/marketOverview';  // Unused - using inline mock
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

      // Return a minimal valid MarketOverviewVM object
      // Note: This is a simplified version - the full object would require all fields
      return {
        ...this.getMockMarketOverview(), // Start with mock data to ensure all required fields
        price_distribution: {
          up_stocks: rise,
          down_stocks: fall,
          flat_stocks: flat,
          limit_up: 0, // Not available in new API response
          limit_down: 0, // Not available in new API response
          total_stocks: total,
        },
        // Note: topEtfs, chipRaces, longHuBang are fetched separately in new API
        last_update: apiData.timestamp ? new Date(apiData.timestamp).toISOString() : new Date().toISOString(),
        timestamp: apiData.timestamp || new Date().toISOString(),
      } as MarketOverviewVM;
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

      // Transform API data to match FundFlowChartPoint interface
      return fundFlowData.map((item) => ({
        date: item.trade_date || '',
        timestamp: item.trade_date ? new Date(item.trade_date).getTime() : Date.now(),

        // Main force (large institutions)
        main_force: {
          inflow: item.super_large_net_inflow || 0,
          outflow: 0, // API only provides inflow
          net_flow: item.super_large_net_inflow || 0,
          ratio: 0 // Will be calculated based on total
        },

        // Large orders (>400,000 yuan)
        large_orders: {
          inflow: item.large_net_inflow || 0,
          outflow: 0, // API only provides inflow
          net_flow: item.large_net_inflow || 0,
          ratio: 0
        },

        // Big orders (200,000-400,000 yuan)
        big_orders: {
          inflow: item.medium_net_inflow || 0,
          outflow: 0, // API only provides inflow
          net_flow: item.medium_net_inflow || 0,
          ratio: 0
        },

        // Medium orders (40,000-200,000 yuan)
        medium_orders: {
          inflow: item.small_net_inflow || 0,
          outflow: 0, // API only provides inflow
          net_flow: item.small_net_inflow || 0,
          ratio: 0
        },

        // Small orders (<40,000 yuan)
        small_orders: {
          inflow: 0,
          outflow: 0,
          net_flow: 0,
          ratio: 0
        },

        // Market totals - calculated from components
        total_inflow: (item.super_large_net_inflow || 0) + (item.large_net_inflow || 0) + (item.medium_net_inflow || 0) + (item.small_net_inflow || 0),
        total_outflow: 0, // API only provides inflow data
        total_net_flow: (item.super_large_net_inflow || 0) + (item.large_net_inflow || 0) + (item.medium_net_inflow || 0) + (item.small_net_inflow || 0)
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
      const values = points.map((p) => ({
        open: p.open || 0,
        close: p.close || 0,
        low: p.low || 0,
        high: p.high || 0,
        volume: p.volume || 0,
      }));
      const volumes = points.map((p) => p.volume || 0);

      return {
        categoryData,
        values,
        volumes,
      } as any;
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
          net_amount: stock.net_amount || 0,
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
        market_status: 'sideways',
        market_phase: 'accumulation',
        indices: {
          shanghai: {
            name: '上证指数',
            code: '000001',
            full_name: '上证综合指数',
            current_price: 0,
            change_amount: 0,
            change_percent: 0,
            volume: 0,
            amount: 0,
            open: 0,
            high: 0,
            low: 0,
            close: 0,
            prev_close: 0
          },
          shenzhen: {
            name: '深证成指',
            code: '399001',
            full_name: '深证成份指数',
            current_price: 0,
            change_amount: 0,
            change_percent: 0,
            volume: 0,
            amount: 0,
            open: 0,
            high: 0,
            low: 0,
            close: 0,
            prev_close: 0
          },
          chiNext: {
            name: '创业板指',
            code: '399006',
            full_name: '创业板指数',
            current_price: 0,
            change_amount: 0,
            change_percent: 0,
            volume: 0,
            amount: 0,
            open: 0,
            high: 0,
            low: 0,
            close: 0,
            prev_close: 0
          }
        },
        sentiment: {
          advance_decline_ratio: 0,
          up_down_volume_ratio: 0,
          new_highs_new_lows_ratio: 0
        },
        turnover: {
          total_value: 0,
          total_volume: 0,
          average_price: 0,
          turnover_rate: 0
        },
        price_distribution: {
          up_stocks: 0,
          down_stocks: 0,
          flat_stocks: 0,
          limit_up: 0,
          limit_down: 0,
          total_stocks: 0
        },
        technical_summary: {
          market_breadth: 0,
          momentum_index: 0
        },
        sector_performance: [],
        hot_concepts: [],
        capital_flow: {
          northbound: { inflow: 0, outflow: 0, net_flow: 0, net_flow_ratio: 0, large_order_ratio: 0, large_orders: { buy: 0, sell: 0, net: 0 }, big_orders: { buy: 0, sell: 0, net: 0 }, medium_orders: { buy: 0, sell: 0, net: 0 }, small_orders: { buy: 0, sell: 0, net: 0 } },
          southbound: { inflow: 0, outflow: 0, net_flow: 0, net_flow_ratio: 0, large_order_ratio: 0, large_orders: { buy: 0, sell: 0, net: 0 }, big_orders: { buy: 0, sell: 0, net: 0 }, medium_orders: { buy: 0, sell: 0, net: 0 }, small_orders: { buy: 0, sell: 0, net: 0 } },
          institutional: { inflow: 0, outflow: 0, net_flow: 0, net_flow_ratio: 0, large_order_ratio: 0, large_orders: { buy: 0, sell: 0, net: 0 }, big_orders: { buy: 0, sell: 0, net: 0 }, medium_orders: { buy: 0, sell: 0, net: 0 }, small_orders: { buy: 0, sell: 0, net: 0 } },
          retail: { inflow: 0, outflow: 0, net_flow: 0, net_flow_ratio: 0, large_order_ratio: 0, large_orders: { buy: 0, sell: 0, net: 0 }, big_orders: { buy: 0, sell: 0, net: 0 }, medium_orders: { buy: 0, sell: 0, net: 0 }, small_orders: { buy: 0, sell: 0, net: 0 } },
          foreign: { inflow: 0, outflow: 0, net_flow: 0, net_flow_ratio: 0, large_order_ratio: 0, large_orders: { buy: 0, sell: 0, net: 0 }, big_orders: { buy: 0, sell: 0, net: 0 }, medium_orders: { buy: 0, sell: 0, net: 0 }, small_orders: { buy: 0, sell: 0, net: 0 } }
        },
        timestamp: new Date().toISOString(),
        last_update: new Date().toISOString(),
        market_session: 'open' as const
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
    if (!data.indices || !data.price_distribution) return false;
    return true;
  }
}

export default MarketAdapter;
