/**
 * Market Composable
 *
 * Vue 3 composable for market data management with automatic error handling,
 * loading states, caching, and Mock data fallback.
 */

import { ref, readonly, onMounted } from 'vue';
import { marketApiService } from '@/api/services/marketService';
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
  const klineData = ref<KLineChartData | null>(null);
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

      // Parallel fetch to gather all data for the Dashboard VM
      const [overviewRes, etfRes, chipRes, lhbRes] = await Promise.all([
        marketApiService.getMarketOverview(),
        marketApiService.getETFList({ limit: 10 }),
        marketApiService.getChipRace({ limit: 10 }),
        marketApiService.getLongHuBang() // Removed limit parameter
      ]);

      // Adapt Overview
      const vm = MarketAdapter.adaptMarketOverview(overviewRes);

      // Validate adapted data (basic check)
      if (!MarketAdapter.validateMarketOverview(vm)) {
        throw new Error('Invalid market overview data');
      }

      // Merge ETF data if available
      if (etfRes.success && etfRes.data && etfRes.data.etfs) {
          vm.topEtfs = etfRes.data.etfs.map(etf => ({
              symbol: etf.symbol || '',
              name: etf.name || '',
              latestPrice: etf.latest_price || 0,
              changePercent: etf.change_percent || 0,
              volume: etf.volume || 0
          }));
      }

      // Merge Chip Race data
      if (chipRes.success) {
          vm.chipRaces = MarketAdapter.adaptChipRace(chipRes);
      }

      // Merge Long Hu Bang data
      if (lhbRes.success) {
          vm.longHuBang = MarketAdapter.adaptLongHuBang(lhbRes);
      }

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

      // Transform parameters to match API service expectations
      const apiParams = {
        startDate: params.start_date,
        endDate: params.end_date,
        market: params.symbol // Map symbol to market parameter
      };

      // Call API service
      const response = await marketApiService.getFundFlow(apiParams);

      // Adapt data (includes automatic Mock fallback)
      const vm = MarketAdapter.adaptFundFlow(response);

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
        const cached = cache.get(cacheKey) as KLineChartData | undefined;
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

      // Call API service
      const response = await marketApiService.getKLineData(apiParams);

      // Adapt data (includes automatic Mock fallback)
      const vm = MarketAdapter.adaptKLineData(response);

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
