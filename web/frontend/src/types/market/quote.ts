/**
 * @fileoverview 市场行情数据类型定义
 * @description 提供市场行情相关的类型定义
 * @module types/market
 * @version 1.0.0
 */

/**
 * K线周期类型
 */
export type KLinePeriod = '1m' | '5m' | '15m' | '30m' | '1h' | '4h' | '1d' | '1w' | '1M';

/**
 * K线数据点
 */
export interface KLineDataPoint {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount?: number;
}

/**
 * K线数据
 */
export interface KLineData {
  symbol: string;
  period: KLinePeriod;
  data: KLineDataPoint[];
  startTime?: string;
  endTime?: string;
}

/**
 * K线数据响应
 */
export interface KlineResponse extends UnifiedResponse<KLineData> {}

/**
 * 资金流向数据
 */
export interface MoneyFlowData {
  symbol: string;
  date: string;
  mainInflow?: number;
  mainOutflow?: number;
  retailInflow?: number;
  retailOutflow?: number;
  netInflow?: number;
}

/**
 * 资金流向列表响应
 */
export interface MoneyFlowResponse extends UnifiedResponse<MoneyFlowData[]> {}

/**
 * 深度数据
 */
export interface DepthData {
  price: number;
  volume: number;
  bids: { price: number; volume: number }[];
  asks: { price: number; volume: number }[];
  timestamp: string;
}

/**
 * 深度数据响应
 */
export interface DepthResponse extends UnifiedResponse<DepthData> {}

/**
 * 筹码分布
 */
export interface OrderBookData {
  symbol: string;
  timestamp: string;
  levels: {
    price: number;
    volume: number;
    orders: number;
  }[];
}

/**
 * 筹码分布响应
 */
export interface OrderBookResponse extends UnifiedResponse<OrderBookData> {}
