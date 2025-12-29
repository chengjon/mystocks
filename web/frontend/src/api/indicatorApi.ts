import apiClient from './apiClient';
import type { OverlayIndicatorResponse, OscillatorIndicatorResponse, IndicatorParams } from '@/types/indicator';

export interface IndicatorRequest {
  symbol: string;
  interval: string;
  indicators: string[];
  params?: IndicatorParams;
}

export const indicatorApi = {
  async getOverlayIndicators(
    symbol: string,
    interval: string,
    indicators: string[],
    params?: IndicatorParams
  ): Promise<OverlayIndicatorResponse> {
    const response = await apiClient.post('/api/indicators/overlay', {
      symbol,
      interval,
      indicators,
      params
    });
    return response.data;
  },

  async getOscillatorIndicators(
    symbol: string,
    interval: string,
    indicators: string[],
    params?: IndicatorParams
  ): Promise<OscillatorIndicatorResponse> {
    const response = await apiClient.post('/api/indicators/oscillator', {
      symbol,
      interval,
      indicators,
      params
    });
    return response.data;
  },

  async getAllIndicators(symbol: string, interval: string): Promise<{
    overlay: OverlayIndicatorResponse;
    oscillator: OscillatorIndicatorResponse;
  }> {
    const [overlay, oscillator] = await Promise.all([
      this.getOverlayIndicators(symbol, interval, ['MA', 'EMA', 'BOLL', 'SAR', 'KAMA']),
      this.getOscillatorIndicators(symbol, interval, ['MACD', 'RSI', 'KDJ', 'CCI', 'WR'])
    ]);
    return { overlay, oscillator };
  }
};

export default indicatorApi;
