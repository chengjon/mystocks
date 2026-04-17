/**
 * Market Composable
 *
 * Vue 3 composable for market data management with automatic error handling,
 * loading states, caching, and Mock data fallback.
 */

import { ref, readonly, onMounted } from 'vue';
import { dataApi } from '@/api/index.ts';
import { marketService } from '@/api/services/marketService';
import { getCache } from '@/utils/cache/part-1';
import type { MarketOverview } from '@/api/types/common.ts';
import type { MarketIndexItem } from '@/api/types/market.ts';
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

const createEmptyCapitalFlow = () => ({
  inflow: 0,
  outflow: 0,
  net_flow: 0,
  large_orders: { buy: 0, sell: 0, net: 0 },
  big_orders: { buy: 0, sell: 0, net: 0 },
  medium_orders: { buy: 0, sell: 0, net: 0 },
  small_orders: { buy: 0, sell: 0, net: 0 },
  net_flow_ratio: 0,
  large_order_ratio: 0,
});

const toMarketIndex = (
  item: MarketIndexItem | undefined,
  fallbackCode: string,
  fallbackName: string
) => ({
  code: item?.symbol || fallbackCode,
  name: item?.name || fallbackName,
  current_price: item?.current_price || 0,
  change_amount: 0,
  change_percent: item?.change_percent || 0,
  volume: item?.volume || 0,
  amount: item?.turnover || 0,
  open: item?.current_price || 0,
  high: item?.current_price || 0,
  low: item?.current_price || 0,
  close: item?.current_price || 0,
  prev_close: item?.current_price || 0,
});

const toMarketOverviewVM = (overview: MarketOverview): MarketOverviewVM => {
  const indices = overview.indices || [];
  const shanghai = indices[0];
  const shenzhen = indices[1];
  const chiNext = indices[2];
  const totalStocks =
    (overview.up_count || 0) +
    (overview.down_count || 0) +
    (overview.flat_count || 0);
  const turnover = overview.total_turnover || 0;
  const volume = overview.total_volume || 0;

  return {
    market_status: 'sideways',
    market_phase: 'accumulation',
    indices: {
      shanghai: toMarketIndex(shanghai, 'SH000001', '上证指数'),
      shenzhen: toMarketIndex(shenzhen, 'SZ399001', '深证成指'),
      chiNext: toMarketIndex(chiNext, 'SZ399006', '创业板指'),
    },
    sentiment: {
      advance_decline_ratio:
        overview.down_count && overview.down_count > 0
          ? (overview.up_count || 0) / overview.down_count
          : overview.up_count || 0,
      up_down_volume_ratio: 0,
      new_highs_new_lows_ratio: 0,
    },
    turnover: {
      total_value: turnover,
      total_volume: volume,
      average_price: volume > 0 ? turnover / volume : 0,
      turnover_rate: 0,
    },
    price_distribution: {
      up_stocks: overview.up_count || 0,
      down_stocks: overview.down_count || 0,
      flat_stocks: overview.flat_count || 0,
      limit_up: 0,
      limit_down: 0,
      total_stocks: totalStocks,
    },
    sector_performance: [],
    hot_concepts: [],
    capital_flow: {
      northbound: createEmptyCapitalFlow(),
      southbound: createEmptyCapitalFlow(),
      institutional: createEmptyCapitalFlow(),
      retail: createEmptyCapitalFlow(),
      foreign: createEmptyCapitalFlow(),
    },
    technical_summary: {
      market_breadth: totalStocks > 0 ? (overview.up_count || 0) / totalStocks : 0,
      momentum_index: 0,
    },
    timestamp: new Date().toISOString(),
    last_update: new Date().toISOString(),
    market_session: 'close',
  };
};

const toFundFlowChartPoints = (
  payload: {
    fund_flow?: Array<{
      trade_date?: string;
      main_net_inflow?: number;
      super_large_net_inflow?: number;
      large_net_inflow?: number;
      medium_net_inflow?: number;
      small_net_inflow?: number;
    }>;
  } | null | undefined
): FundFlowChartPoint[] =>
  (payload?.fund_flow || []).map((item) => {
    const large = item.super_large_net_inflow || 0;
    const big = item.large_net_inflow || 0;
    const medium = item.medium_net_inflow || 0;
    const small = item.small_net_inflow || 0;
    const total = large + big + medium + small;

    return {
      date: item.trade_date || '',
      timestamp: item.trade_date ? new Date(item.trade_date).getTime() : Date.now(),
      main_force: {
        inflow: item.main_net_inflow || large,
        outflow: 0,
        net_flow: item.main_net_inflow || large,
        ratio: total > 0 ? ((item.main_net_inflow || large) / total) * 100 : 0,
      },
      large_orders: {
        inflow: large,
        outflow: 0,
        net_flow: large,
        ratio: total > 0 ? (large / total) * 100 : 0,
      },
      big_orders: {
        inflow: big,
        outflow: 0,
        net_flow: big,
        ratio: total > 0 ? (big / total) * 100 : 0,
      },
      medium_orders: {
        inflow: medium,
        outflow: 0,
        net_flow: medium,
        ratio: total > 0 ? (medium / total) * 100 : 0,
      },
      small_orders: {
        inflow: small,
        outflow: 0,
        net_flow: small,
        ratio: total > 0 ? (small / total) * 100 : 0,
      },
      total_inflow: total,
      total_outflow: 0,
      total_net_flow: total,
    };
  });

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
          marketOverview.value = cached;
          return;
        }
      }

      const response = await dataApi.getMarketOverview();
      const vm = toMarketOverviewVM(response.data || {});

      // Cache the result
      if (enableCache) {
        cache.set(cacheKey, vm, { ttl: CACHE_TTL.MARKET_OVERVIEW });
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
          fundFlowData.value = cached;
          return;
        }
      }

      const response = await marketService.getFundFlow(params) as {
        fund_flow?: Array<{
          trade_date?: string;
          main_net_inflow?: number;
          super_large_net_inflow?: number;
          large_net_inflow?: number;
          medium_net_inflow?: number;
          small_net_inflow?: number;
        }>;
      };
      const vm = toFundFlowChartPoints(response);

      // Cache the result
      if (enableCache) {
        cache.set(cacheKey, vm, { ttl: CACHE_TTL.FUND_FLOW });
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
          klineData.value = cached;
          return;
        }
      }

      // Adapt parameters for API (startDate -> start_date)
      const _apiParams = {
        symbol: params.symbol,
        interval: params.interval,
        start_date: params.startDate,
        end_date: params.endDate,
        limit: params.limit
      };

      // Use getKline instead of getKLine
      const response = await marketService.getKline({
        stock_code: params.symbol,
        period: params.interval,
      });

      // For now, create a simple adapter since response format may not match
      interface KLineItem {
        timestamp?: string | number
        date?: string | number
        open?: number
        high?: number
        low?: number
        close?: number
        volume?: number
        amount?: number
      }
      const vm: KLineChartData[] = ((response as unknown as { data?: KLineItem[] }).data || []).map((item) => ({
        timestamp: String(item.timestamp || item.date || ''),
        date: String(item.date || item.timestamp || ''),
        open: item.open || 0,
        high: item.high || 0,
        low: item.low || 0,
        close: item.close || 0,
        volume: item.volume || 0,
        amount: item.amount || 0,
        symbol: params.symbol,
        interval: params.interval
      }));

      // Cache the result
      if (enableCache) {
        cache.set(cacheKey, vm, { ttl: CACHE_TTL.K_LINE });
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
