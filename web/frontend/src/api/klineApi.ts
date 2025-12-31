import axios from 'axios';
import { klineCache } from '../utils/cacheManager';
import type { KLineResponse, IndicatorResponse, StopLimitData, KLineData, IntervalType, AdjustType } from '../types/kline';

const API_BASE = import.meta.env.VITE_API_BASE || '/api';
const TIMEOUT = 30000;

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: TIMEOUT,
  headers: {
    'Content-Type': 'application/json'
  }
});

apiClient.interceptors.response.use(
  response => response.data,
  error => {
    const message = error.response?.data?.message || error.message || 'API请求失败';
    console.error('[KLINE API] Error:', message);
    return Promise.reject(new Error(message));
  }
);

// Helper function to get data directly (reflected by interceptor)
async function apiGet<T>(url: string): Promise<T> {
  return apiClient.get<T>(url) as Promise<T>;
}

apiClient.interceptors.request.use(
  config => {
    const timestamp = new Date().toISOString();
    console.log(`[KLINE API] ${config.method?.toUpperCase()} ${config.url} [${timestamp}]`);
    return config;
  },
  error => Promise.reject(error)
);

export const klineApi = {
  async getKline(
    symbol: string,
    interval: IntervalType = '1d',
    adjust: AdjustType = 'qfq',
    startDate?: string,
    endDate?: string,
    useCache = true
  ): Promise<KLineResponse> {
    const cacheKey = klineCache.generateKey(symbol, interval, adjust, startDate, endDate);

    if (useCache) {
      const cached = klineCache.get<KLineResponse>(cacheKey);
      if (cached) {
        console.log('[KLINE API] Cache hit:', cacheKey);
        return cached;
      }
    }

    const params = new URLSearchParams({ symbol, interval, adjust });
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const response = await apiGet<KLineResponse>(`/market/kline?${params}`);
    klineCache.set(cacheKey, response);
    return response;
  },

  async getOverlayIndicators(
    symbol: string,
    interval: IntervalType,
    indicators: string[],
    params?: Record<string,unknown>
  ): Promise<IndicatorResponse> {
    const queryParams = new URLSearchParams({ symbol, interval, indicators: indicators.join(',') });
    if (params) queryParams.append('params', JSON.stringify(params));
    return apiGet<IndicatorResponse>(`/indicators/overlay?${queryParams}`);
  },

  async getOscillatorIndicators(
    symbol: string,
    interval: IntervalType,
    indicators: string[],
    params?: Record<string,unknown>
  ): Promise<IndicatorResponse> {
    const queryParams = new URLSearchParams({ symbol, interval, indicators: indicators.join(',') });
    if (params) queryParams.append('params', JSON.stringify(params));
    return apiGet<IndicatorResponse>(`/indicators/oscillator?${queryParams}`);
  },

  async getStopLimit(symbol: string, date: string, prevClose: number): Promise<{ data: StopLimitData }> {
    const params = new URLSearchParams({ symbol, date, prev_close: prevClose.toString() });
    return apiGet<{ data: StopLimitData }>(`/astock/stop-limit?${params}`);
  },

  async getT1Sellable(buyDate: string): Promise<{ data: { sellable_date: string; t_status: string } }> {
    return apiGet<{ data: { sellable_date: string; t_status: string } }>(`/astock/t1-sellable?buy_date=${buyDate}`);
  },

  clearCache(): void {
    klineCache.clear();
    console.log('[KLINE API] Cache cleared');
  }
};

export const convertApiToChartData = (apiData: KLineResponse['data']): KLineData[] => {
  return apiData.candles.map(candle => ({
    timestamp: candle.timestamp,
    open: Number(candle.open),
    high: Number(candle.high),
    low: Number(candle.low),
    close: Number(candle.close),
    volume: Number(candle.volume),
    amount: candle.amount ? Number(candle.amount) : undefined
  }));
};

export default klineApi;
