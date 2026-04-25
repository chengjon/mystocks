/**
 * Market Data Adapter
 *
 * Handles data transformation between API responses and frontend models.
 * Returns explicit empty-state inputs instead of silent mock payloads on failures.
 */

import type { UnifiedResponse } from '../types/common.ts';
import type {
  MarketOverviewVM,
  FundFlowChartPoint,
} from '../types/extensions/index.ts';
import type {
  ChipRaceItem,
  LongHuBangItem,
} from '../types/common.ts';

// Import new API types
import type {
  MarketOverviewDetailedResponse as MarketOverviewResponse,
  FundFlowDataResponse as FundFlowAPIResponse,
  KlineResponse as KLineDataResponse,
  ChipRaceResponse,
  LongHuBangResponse,
} from '../types/common.ts';

interface AdaptedKLineData {
  categoryData: string[];
  values: {
    open: number;
    close: number;
    low: number;
    high: number;
    volume: number;
  }[];
  volumes: number[];
}

export class MarketAdapter {
  /**
   * Adapt market overview from API response
   *
   * @param apiResponse - Raw API response
   * @returns Adapted MarketOverviewVM object
   */
  static adaptMarketOverview(
    apiResponse: UnifiedResponse<MarketOverviewResponse>
  ): MarketOverviewVM {
    if (!apiResponse.success || !apiResponse.data) {
      console.warn('[MarketAdapter] API failed, returning empty market overview:', apiResponse.message);
      return this.createEmptyMarketOverview(apiResponse.timestamp);
    }

    try {
      const data = apiResponse.data;

      const apiData = data as Partial<MarketOverviewResponse> & {
        rise_fall_count?: {
          rise?: number;
          fall?: number;
          flat?: number;
        };
        timestamp?: string;
      };

      const rise = apiData.rise_fall_count?.rise || 0;
      const fall = apiData.rise_fall_count?.fall || 0;
      const flat = apiData.rise_fall_count?.flat || 0;
      const total = rise + fall + flat;

      // Return a minimal valid MarketOverviewVM object
      // Note: This is a simplified version - the full object would require all fields
      return {
        ...this.createEmptyMarketOverview(apiData.timestamp), // Start with empty state to ensure all required fields
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
      return this.createEmptyMarketOverview(apiResponse.timestamp);
    }
  }

  /**
   * Adapt fund flow data from API response
   *
   * @param apiResponse - Raw API response
   * @returns Array of adapted FundFlowChartPoint objects
   */
  static adaptFundFlow(
    apiResponse: UnifiedResponse<FundFlowAPIResponse>
  ): FundFlowChartPoint[] {
    if (!apiResponse.success || !apiResponse.data) {
      console.warn('[MarketAdapter] Fund flow API failed, returning empty fund flow:', apiResponse.message);
      return [];
    }

    try {
      // Access fundFlow array directly from the response data
      const fundFlowData = apiResponse.data?.fund_flow || [];

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
      return [];
    }
  }

  /**
   * Adapt K-line data from API response
   *
   * @param apiResponse - Raw API response
   * @returns Adapted KLineChartData object
   */
  static adaptKLineData(
    apiResponse: UnifiedResponse<KLineDataResponse>
  ): AdaptedKLineData {
    if (!apiResponse.success || !apiResponse.data) {
      console.warn('[MarketAdapter] K-line API failed, returning empty K-line dataset:', apiResponse.message);
      return this.createEmptyKLineData();
    }

    try {
      const klineData = apiResponse.data;
      const points = klineData.data || [];

      const categoryData = points.map((p) => {
        const point = p as {
          date?: string;
          datetime?: string;
          timestamp?: string;
        };

        return point.date || point.datetime || point.timestamp || '';
      });
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
      };
    } catch (error) {
      console.error('[MarketAdapter] Failed to adapt K-line data:', error);
      return this.createEmptyKLineData();
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
      return items.map((stock) => ({
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
      return items.map((stock) => ({
          symbol: stock.symbol || '',
          name: stock.name || '',
          net_amount: stock.net_amount || 0,
          reason: stock.reason || ''
      }));
  }

  // ==================== Empty State Helpers ====================

  private static createEmptyMarketOverview(timestamp?: string): MarketOverviewVM {
    const resolvedTimestamp = timestamp || new Date().toISOString();

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
        timestamp: resolvedTimestamp,
        last_update: resolvedTimestamp,
        market_session: 'open' as const
    };
  }

  private static createEmptyKLineData(): AdaptedKLineData {
    return {
      categoryData: [],
      values: [],
      volumes: [],
    };
  }

  // ==================== Validation Methods ====================

  /**
   * Validate market overview data
   */
  static validateMarketOverview(data: MarketOverviewVM): boolean {
    if (!data.indices || !data.price_distribution) return false;
    if (data.price_distribution.total_stocks < 0) return false;
    return true;
  }
}

export default MarketAdapter;
