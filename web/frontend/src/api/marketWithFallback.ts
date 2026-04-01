/**
 * Market Data API with Fallback - Refactored
 *
 * This file has been refactored to use the new 6-layer architecture:
 * 1. Types (types/market.ts)
 * 2. API Service (services/marketService.ts)
 * 3. Adapter (adapters/marketAdapter.ts)
 * 4. Mock Data (mock/*)
 * 5. Composable (composables/useMarket.ts)
 * 6. Components
 *
 * This file now serves as a compatibility layer for existing code.
 * New code should use the composable: useMarket()
 *
 * @deprecated Use useMarket() composable instead
 */

import MarketApiServiceClass from './market.ts';
import type { MarketOverviewVM, FundFlowChartPoint, KLineChartData } from '@/utils/adapters.ts';

// Re-export types for backward compatibility
export type {
  MarketOverviewVM,
  FundFlowChartPoint,
  KLineChartData,
};

/**
 * Legacy Market API Service with Fallback
 *
 * @deprecated This class is kept for backward compatibility.
 * Use the useMarket() composable for new code.
 */
class MarketApiServiceWithFallback {
  private useRealData = import.meta.env.VITE_USE_REAL_DATA !== 'false';
  private marketService: MarketApiServiceClass;

  constructor() {
    this.marketService = new MarketApiServiceClass();
  }

  /**
   * Get market overview with caching and fallback
   *
   * @param _forceRefresh - Force refresh from API (deprecated parameter)
   * @returns Market overview data
   * @deprecated Use useMarket().fetchMarketOverview() instead
   */
  async getMarketOverview(_forceRefresh = false): Promise<MarketOverviewVM> {
    console.warn('[DEPRECATED] getMarketOverview() - use useMarket() composable instead');

    return this.marketService.getMarketOverview();
  }

  /**
   * Get fund flow data with caching and fallback
   *
   * @param params - Query parameters
   * @param _forceRefresh - Force refresh from API (deprecated parameter)
   * @returns Fund flow chart data
   * @deprecated Use useMarket().fetchFundFlow() instead
   */
  async getFundFlow(
    params?: {
      startDate?: string;
      endDate?: string;
      market?: string;
    },
    _forceRefresh = false
  ): Promise<FundFlowChartPoint[]> {
    console.warn('[DEPRECATED] getFundFlow() - use useMarket() composable instead');

    void this.useRealData;

    return this.marketService.getFundFlow(params);
  }

  /**
   * Get K-line data with caching and fallback
   *
   * @param params - K-line parameters
   * @param _forceRefresh - Force refresh from API (deprecated parameter)
   * @returns K-line chart data
   * @deprecated Use useMarket().fetchKLineData() instead
   */
  async getKLineData(
    params: {
      symbol: string;
      interval: '1m' | '5m' | '15m' | '30m' | '1h' | '4h' | '1d' | '1w' | '1M';
      startDate?: string;
      endDate?: string;
      limit?: number;
    },
    _forceRefresh = false
  ): Promise<KLineChartData> {
    console.warn('[DEPRECATED] getKLineData() - use useMarket() composable instead');

    // Map legacy intervals to new API intervals
    // New API only supports: "1m" | "5m" | "15m" | "30m" | "1h" | "1d"
    type SupportedInterval = '1m' | '5m' | '15m' | '30m' | '1h' | '1d';
    const supportedIntervals = new Set<SupportedInterval>(['1m', '5m', '15m', '30m', '1h', '1d']);
    const interval: SupportedInterval = supportedIntervals.has(params.interval as SupportedInterval)
      ? (params.interval as SupportedInterval)
      : '1d';

    if (interval !== params.interval) {
      console.warn(`[MarketApiServiceWithFallback] Interval '${params.interval}' not supported by new API, using '1d' instead`);
    }

    return this.marketService.getKLineData({
      symbol: params.symbol,
      interval,
      startDate: params.startDate,
      endDate: params.endDate,
      limit: params.limit,
    });
  }

  /**
   * Clear all market data cache
   *
   * @deprecated Use useMarket().clearCache() instead
   */
  clearCache(): void {
    console.warn('[DEPRECATED] clearCache() - use useMarket() composable instead');
    // Cache is now managed by the composable
  }

  /**
   * Get cache statistics
   *
   * @deprecated Use useMarket().getCacheStats() instead
   */
  getCacheStats(): { size: number; hits: number; misses: number } {
    console.warn('[DEPRECATED] getCacheStats() - use useMarket() composable instead');
    // Cache is now managed by the composable
    return {
      size: 0,
      hits: 0,
      misses: 0,
    };
  }
}

// Export singleton instance for backward compatibility
export const legacyMarketApiService = new MarketApiServiceWithFallback();
export const marketApiService = legacyMarketApiService;

// Export the class for testing
export default MarketApiServiceWithFallback;

// Export new architecture for migration
export { useMarket } from '../composables/useMarket.ts';
