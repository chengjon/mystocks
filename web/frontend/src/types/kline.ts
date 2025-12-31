export interface KLineData {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount?: number;
  [key: string]: any;
}

export interface KLineResponse {
  code: number;
  data: {
    symbol: string;
    interval: string;
    adjust: string;
    candles: KLineData[];
  };
}

export type IntervalType = '1m' | '5m' | '15m' | '1h' | '1d' | '1w' | '1M';
export type AdjustType = 'qfq' | 'hfq' | 'none';

export interface ChartConfig {
  symbol: string;
  interval: IntervalType;
  adjust: AdjustType;
  startDate?: string;
  endDate?: string;
}

export interface StopLimitData {
  limit_up: number;
  limit_down: number;
  limit_pct: number;
}

export interface T1SellableData {
  sellable_date: string;
  t_status: string;
}

export interface IndicatorPoint {
  timestamp: number;
  value?: number;
  upper?: number;
  middle?: number;
  lower?: number;
  dif?: number;
  dea?: number;
  macd?: number;
}

export interface OverlayIndicator {
  MA?: IndicatorPoint[];
  EMA?: IndicatorPoint[];
  BOLL?: IndicatorPoint[];
}

export interface OscillatorIndicator {
  MACD?: IndicatorPoint[];
  RSI?: IndicatorPoint[];
  KDJ?: IndicatorPoint[];
}

export interface IndicatorResponse {
  code: number;
  data: OverlayIndicator | OscillatorIndicator;
}
