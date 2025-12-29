import { ref, computed, watch } from 'vue';
import { klineApi, convertApiToChartData } from '../api/klineApi';
import { loadMockKlineData, loadMockIndicators, loadMockStopLimit } from '../api/mockKlineData';
import type { KLineData, IntervalType, AdjustType, StopLimitData } from '../types/kline';

export const useKlineChart = (options: { useMock?: boolean } = {}) => {
  const useMock = ref(options.useMock ?? true);

  const klineData = ref<KLineData[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const limitData = ref<StopLimitData | null>(null);
  const currentSymbol = ref('');
  const currentInterval = ref<IntervalType>('1d');
  const currentAdjust = ref<AdjustType>('qfq');

  const isDataLoaded = computed(() => klineData.value.length > 0);
  const latestPrice = computed(() => klineData.value.length > 0 ? klineData.value[klineData.value.length - 1] : null);
  const priceChange = computed(() => {
    if (klineData.value.length < 2) return null;
    const current = klineData.value[klineData.value.length - 1];
    const previous = klineData.value[klineData.value.length - 2];
    return {
      change: current.close - previous.close,
      percent: ((current.close - previous.close) / previous.close) * 100
    };
  });

  const loadKlineData = async (
    symbol: string,
    interval: IntervalType = '1d',
    adjust: AdjustType = 'qfq',
    startDate?: string,
    endDate?: string
  ) => {
    loading.value = true;
    error.value = null;
    currentSymbol.value = symbol;
    currentInterval.value = interval;
    currentAdjust.value = adjust;

    try {
      let data: { candles: KLineData[] };
      let limitResult: StopLimitData | null = null;

      if (useMock.value) {
        data = await loadMockKlineData(symbol, interval, adjust, startDate, endDate);
        const prevClose = data.candles.length > 1
          ? data.candles[data.candles.length - 2].close
          : data.candles[0]?.close || 10;
        limitResult = await loadMockStopLimit(symbol, prevClose);
      } else {
        const response = await klineApi.getKline(symbol, interval, adjust, startDate, endDate);
        if (response.code === 0) {
          data = { candles: convertApiToChartData(response.data) };
          const today = new Date().toISOString().split('T')[0];
          const prevClose = data.candles.length > 1
            ? data.candles[data.candles.length - 2].close
            : data.candles[0]?.close || 10;
          try {
            const limitResponse = await klineApi.getStopLimit(symbol, today, prevClose);
            limitResult = limitResponse.data;
          } catch {
            limitResult = null;
          }
        } else {
          throw new Error(`API错误: ${response.code}`);
        }
      }

      klineData.value = data.candles;
      limitData.value = limitResult;
    } catch (e) {
      error.value = e instanceof Error ? e.message : '加载数据失败';
      console.error('[useKlineChart] Load failed:', error.value);
    } finally {
      loading.value = false;
    }
  };

  const loadIndicators = async (
    symbol: string,
    interval: IntervalType,
    type: 'overlay' | 'oscillator',
    indicators: string[],
    params?: Record<string, unknown>
  ) => {
    try {
      if (useMock.value) {
        return await loadMockIndicators(symbol, interval, type, indicators);
      } else {
        const response = type === 'overlay'
          ? await klineApi.getOverlayIndicators(symbol, interval, indicators, params)
          : await klineApi.getOscillatorIndicators(symbol, interval, indicators, params);
        return response.code === 0 ? response.data : null;
      }
    } catch (e) {
      console.error('[useKlineChart] Load indicators failed:', e);
      return null;
    }
  };

  const reload = () => {
    if (currentSymbol.value) {
      loadKlineData(currentSymbol.value, currentInterval.value, currentAdjust.value);
    }
  };

  const clearData = () => {
    klineData.value = [];
    limitData.value = null;
    error.value = null;
  };

  const clearCache = () => {
    klineApi.clearCache();
  };

  watch([currentSymbol, currentInterval, currentAdjust], () => {
    if (currentSymbol.value) {
      loadKlineData(currentSymbol.value, currentInterval.value, currentAdjust.value);
    }
  });

  return {
    klineData,
    loading,
    error,
    limitData,
    currentSymbol,
    currentInterval,
    currentAdjust,
    isDataLoaded,
    latestPrice,
    priceChange,
    useMock,
    loadKlineData,
    loadIndicators,
    reload,
    clearData,
    clearCache
  };
};
