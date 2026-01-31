/**
 * @fileoverview 市场数据模块类型定义
 * @description 提供市场数据相关的类型定义
 * @module types/market
 * @version 1.0.0
 */

import type { UnifiedResponse, UnifiedPaginatedResponse } from '../common/response';

/**
 * 股票基本信息
 */
export interface StockInfo {
  symbol: string;
  name: string;
  nameEn?: string;
  market: 'SH' | 'SZ' | 'BJ';
  industry?: string;
  sector?: string;
  listDate?: string;
  type?: 'stock' | 'index' | 'etf' | 'bond';
}

/**
 * 股票列表项
 */
export interface StockListItem {
  symbol: string;
  name: string;
  price?: number;
  changePercent?: number;
  volume?: number;
  amount?: number;
  market?: string;
}

/**
 * 股票列表响应
 */
export interface StockListResponse extends UnifiedPaginatedResponse<StockListItem[]> {}

/**
 * 股票详情响应
 */
export interface StockDetailResponse extends UnifiedResponse<StockInfo> {}

/**
 * 实时报价
 */
export interface Quote {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  amount: number;
  high: number;
  low: number;
  open: number;
  preClose: number;
  timestamp: string;
}

/**
 * 实时报价列表
 */
export interface QuoteList {
  quotes: Quote[];
  timestamp: string;
}

/**
 * 实时报价响应
 */
export interface QuoteResponse extends UnifiedResponse<QuoteList> {}
