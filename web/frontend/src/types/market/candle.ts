/**
 * @fileoverview 市场K线数据类型定义
 * @description 提供K线数据相关的类型定义
 * @module types/market
 * @version 1.0.0
 */

/**
 * 复权类型
 */
export type AdjustType = 'none' | 'qfq' | 'hfq' | 'adj';

/**
 * K线数据项
 */
export interface KlineDataItem {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount: number;
  adjustClose?: number;
  change?: number;
  changePercent?: number;
  turnover?: number;
}

/**
 * K线数据集合
 */
export interface KlineData {
  symbol: string;
  period: string;
  adjustType: AdjustType;
  data: KlineDataItem[];
  startTime?: string;
  endTime?: string;
}

/**
 * K线数据响应
 */
export interface KlineResponse extends UnifiedResponse<KlineData> {}
