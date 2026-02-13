/**
 * Market Composable
 *
 * Vue 3 composable for market data management with automatic error handling,
 * loading states, caching, and Mock data fallback.
 */

import { ref, readonly, onMounted } from 'vue';
import { marketService } from '@/api/services/marketService';
import { MarketAdapter } from '@/api/adapters/marketAdapter';
import { getCache } from '@/utils/cache';
import type { MarketOverviewVM, FundFlowChartPoint, KLineChartData } from '@/api/types/extensions';

/**
 * Cache keys
 */
const CACHE_KEYS = {
  MARKET_OVERVIEW: 'market:overview',
  FUND_FLOW: 'market:fund_flow',
  K_LINE: 'market:kline',
};

/**
 * Cache TTL (in seconds)
 */
const CACHE_TTL = {
  MARKET_OVERVIEW: 300, // 5 minutes
  FUND_FLOW: 600,       // 10 minutes
  K_LINE: 180,          // 3 minutes
};

/**
 * Market data management composable
 *
 * @param options - Configuration options
 * @returns Market data state and methods
 */
export function useMarket(options?: {
  autoFetch?: boolean;
  enableCache?: boolean;
}) {
  const { autoFetch = true, enableCache = true } = options || {};

  // State
  const marketOverview = ref<MarketOverviewVM | null>(null);
  const fundFlowData = ref<FundFlowChartPoint[]>([]);
  const klineData = ref<KLineChartData[] | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Cache manager instance
  const cache = getCache('market-api');

  /**
   * Fetch market overview with caching and automatic fallback
   *
   * @param forceRefresh - Force refresh from API, bypassing cache
   */
  const fetchMarketOverview = async (forceRefresh = false) => {
    loading.value = true;
    error.value = null;

    const cacheKey = CACHE_KEYS.MARKET_OVERVIEW;

    try {
      // Try cache first (if enabled and not forcing refresh)
      if (enableCache && !forceRefresh) {
        const cached = cache.get(cacheKey) as MarketOverviewVM | undefined;
        if (cached) {
          console.log('[useMarket] ✅ Market Overview from cache');
          marketOverview.value = cached;
          return;
        }
      }

      console.log('[useMarket] 🔄 Fetching Market Overview from API...');

      // TODO: Implement these methods in marketService
      // For now, return mock data with minimal required fields
      const vm = {
        market_status: 'sideways' as const,
        market_phase: 'accumulation' as const,
        indices: {
          shanghai: {
            code: 'SH000001',
            name: '上证指数',
            current_price: 3000,
            change_amount: 0,
            change_percent: 0,
            volume: 0,
            amount: 0,
            open: 3000,
            high: 3000,
            low: 3000,
            close: 3000,
            prev_close: 3000
          },
          shenzhen: {
            code: 'SZ399001',
            name: '深证成指',
            current_price: 10000,
            change_amount: 0,
            change_percent: 0,
            volume: 0,
            amount: 0,
            open: 10000,
            high: 10000,
            low: 10000,
            close: 10000,
            prev_close: 10000
          },
          chiNext: {
            code: 'SZ399006',
            name: '创业板指',
            current_price: 2000,
            change_amount: 0,
            change_percent: 0,
            volume: 0,
            amount: 0,
            open: 2000,
            high: 2000,
            low: 2000,
            close: 2000,
            prev_close: 2000
          }
        },
        sentiment: {
          advance_decline_ratio: 1.0,
          up_down_volume_ratio: 1.0,
          new_highs_new_lows_ratio: 1.0
        },
        turnover: { total: 0, shanghai: 0, shenzhen: 0 },
        price_distribution: { up: 0, down: 0, flat: 0 },
        sector_performance: [],
        hot_concepts: [],
        capital_flow: { main_net: 0, retail_net: 0, institution_net: 0 },
        top_gainers: [],
        top_losers: [],
        technical_summary: { trend: 'neutral' as const, support: 0, resistance: 0 },
        last_update: new Date().toISOString(),
        market_session: 'closed' as const,
        timestamp: new Date().toISOString()
      } as unknown as MarketOverviewVM;

      // Merge Chip Race data
      // TODO: MarketOverviewVM interface doesn't have chipRaces field
      // if (chipRes.success) {
      //     vm.chipRaces = MarketAdapter.adaptChipRace(chipRes);
      // }

      // Merge Long Hu Bang data
      // TODO: MarketOverviewVM interface doesn't have longHuBang field
      // if (lhbRes.success) {
      //     vm.longHuBang = MarketAdapter.adaptLongHuBang(lhbRes);
      // }

      // Cache the result
      if (enableCache) {
        cache.set(cacheKey, vm, { ttl: CACHE_TTL.MARKET_OVERVIEW });
        console.log('[useMarket] ✅ Market Overview from API - cached for 5min');
      }

      marketOverview.value = vm;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `获取市场概览失败: ${errorMsg}`;
      console.error('[useMarket] fetchMarketOverview error:', err);

      // Adapter handles Mock fallback for individual calls, but since we are assembling,
      // if the main overview fails, the adapter returns mock overview.
      // If separate calls fail, we just have empty lists for those sections (safe).
    } finally {
      loading.value = false;
    }
  };

  /**
   * Fetch fund flow data with caching and automatic fallback
   *
   * @param params - Fund flow parameters
   * @param forceRefresh - Force refresh from API, bypassing cache
   */
  const fetchFundFlow = async (
    params: {
      symbol: string;
      timeframe?: "1" | "3" | "5" | "10";
      start_date?: string;
      end_date?: string;
    },
    forceRefresh = false
  ) => {
    loading.value = true;
    error.value = null;

    const cacheKey = `${CACHE_KEYS.FUND_FLOW}:${JSON.stringify(params || {})}`;

    try {
      // Try cache first (if enabled and not forcing refresh)
      if (enableCache && !forceRefresh) {
        const cached = cache.get(cacheKey) as FundFlowChartPoint[] | undefined;
        if (cached) {
          console.log('[useMarket] ✅ Fund Flow from cache');
          fundFlowData.value = cached;
          return;
        }
      }

      console.log('[useMarket] 🔄 Fetching Fund Flow from API...');

      // TODO: Implement getFundFlow in marketService
      // For now, return mock data
      const vm: FundFlowChartPoint[] = [];

      // Cache the result
      if (enableCache) {
        cache.set(cacheKey, vm, { ttl: CACHE_TTL.FUND_FLOW });
        console.log('[useMarket] ✅ Fund Flow from API - cached for 10min');
      }

      fundFlowData.value = vm;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `获取资金流向失败: ${errorMsg}`;
      console.error('[useMarket] fetchFundFlow error:', err);
    } finally {
      loading.value = false;
    }
  };

  /**
   * Fetch K-line data with caching and automatic fallback
   *
   * @param params - K-line parameters
   * @param forceRefresh - Force refresh from API, bypassing cache
   */
  const fetchKLineData = async (
    params: {
      symbol: string;
      interval: '1m' | '5m' | '15m' | '30m' | '1h' | '1d';
      startDate?: string;
      endDate?: string;
      limit?: number;
    },
    forceRefresh = false
  ) => {
    loading.value = true;
    error.value = null;

    const cacheKey = `${CACHE_KEYS.K_LINE}:${params.symbol}:${params.interval}`;

    try {
      // Try cache first (if enabled and not forcing refresh)
      if (enableCache && !forceRefresh) {
        const cached = cache.get(cacheKey) as KLineChartData[] | undefined;
        if (cached) {
          console.log('[useMarket] ✅ K-Line from cache');
          klineData.value = cached;
          return;
        }
      }

      // Adapt parameters for API (startDate -> start_date)
      const apiParams = {
        symbol: params.symbol,
        interval: params.interval,
        start_date: params.startDate,
        end_date: params.endDate,
        limit: params.limit
      };

      console.log(`[useMarket] 🔄 Fetching K-Line for ${params.symbol} from API...`);

      // Use getKLine instead of getKLineData
      const response = await marketService.getKLine(params.symbol, params.interval);

      // For now, create a simple adapter since response format may not match
      const vm: KLineChartData[] = (response.data || []).map((item: any) => ({
        timestamp: item.timestamp || item.date || '',
        date: item.date || item.timestamp || '',
        open: item.open || 0,
        high: item.high || 0,
        low: item.low || 0,
        close: item.close || 0,
        volume: item.volume || 0
      }));

      // Cache the result
      if (enableCache) {
        cache.set(cacheKey, vm, { ttl: CACHE_TTL.K_LINE });
        console.log(`[useMarket] ✅ K-Line from API - cached for 3min`);
      }

      klineData.value = vm;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `获取K线数据失败: ${errorMsg}`;
      console.error('[useMarket] fetchKLineData error:', err);
    } finally {
      loading.value = false;
    }
  };

  /**
   * Clear all market data cache
   */
  const clearCache = () => {
    cache.clear();
    console.log('[useMarket] 🗑️ Market data cache cleared');
  };

  /**
   * Get cache statistics
   */
  const getCacheStats = () => {
    return cache.getStats();
  };

  // Auto-fetch on mount (if enabled)
  onMounted(() => {
    if (autoFetch) {
      fetchMarketOverview();
    }
  });

  // Return readonly state and methods
  return {
    // Readonly state
    marketOverview: readonly(marketOverview),
    fundFlowData: readonly(fundFlowData),
    klineData: readonly(klineData),
    loading: readonly(loading),
    error: readonly(error),

    // Methods
    fetchMarketOverview,
    fetchFundFlow,
    fetchKLineData,
    clearCache,
    getCacheStats,
  };
}

export default useMarket;
