/**
 * Market Composable
 *
 * Vue 3 composable for market data management with automatic error handling,
 * loading states, caching, and Mock data fallback.
 */

import { ref, readonly, onMounted } from 'vue';
import { marketApiService } from '@/api/services/marketService';
import { MarketAdapter } from '@/api/adapters/marketAdapter';
import { CacheManager } from '@/utils/cache';
import type { MarketOverviewVM, FundFlowChartPoint, KLineChartData } from '@/api/types/market';

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
  const cache = new CacheManager('market-api');

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
        const cached = cache.get<MarketOverviewVM>(cacheKey);
        if (cached) {
          console.log('[useMarket] ✅ Market Overview from cache');
          marketOverview.value = cached;
          return;
        }
      }

      console.log('[useMarket] 🔄 Fetching Market Overview from API...');

      // Call API service
      const response = await marketApiService.getMarketOverview();

      // Adapt data (includes automatic Mock fallback)
      const vm = MarketAdapter.adaptMarketOverview(response);

      // Validate adapted data
      if (!MarketAdapter.validateMarketOverview(vm)) {
        throw new Error('Invalid market overview data');
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

      // Adapter already handles Mock fallback, so no need for additional fallback here
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
    params?: {
      startDate?: string;
      endDate?: string;
      market?: string;
    },
    forceRefresh = false
  ) => {
    loading.value = true;
    error.value = null;

    const cacheKey = `${CACHE_KEYS.FUND_FLOW}:${JSON.stringify(params || {})}`;

    try {
      // Try cache first (if enabled and not forcing refresh)
      if (enableCache && !forceRefresh) {
        const cached = cache.get<FundFlowChartPoint[]>(cacheKey);
        if (cached) {
          console.log('[useMarket] ✅ Fund Flow from cache');
          fundFlowData.value = cached;
          return;
        }
      }

      // Validate parameters
      if (!MarketAdapter.validateFundFlowParams(params || {})) {
        throw new Error('Invalid fund flow parameters');
      }

      console.log('[useMarket] 🔄 Fetching Fund Flow from API...');

      // Call API service
      const response = await marketApiService.getFundFlow(params);

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

      // Adapter already handles Mock fallback
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
      interval: '1m' | '5m' | '15m' | '30m' | '1h' | '4h' | '1d' | '1w' | '1M';
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
        const cached = cache.get<KLineChartData>(cacheKey);
        if (cached) {
          console.log('[useMarket] ✅ K-Line from cache');
          klineData.value = cached;
          return;
        }
      }

      // Validate parameters
      if (!MarketAdapter.validateKLineParams(params)) {
        throw new Error('Invalid K-line parameters');
      }

      console.log(`[useMarket] 🔄 Fetching K-Line for ${params.symbol} from API...`);

      // Call API service
      const response = await marketApiService.getKLineData(params);

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

      // Adapter already handles Mock fallback
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
