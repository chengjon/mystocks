/**
 * @fileoverview 技术信号模块类型定义
 * @description 提供技术信号相关的类型定义
 * @module types/technical
 * @version 1.0.0
 */

import type { UnifiedResponse } from '../common/response';

/**
 * 信号类型
 */
export type SignalType =
  | 'buy'
  | 'sell'
  | 'hold'
  | 'strong_buy'
  | 'strong_sell';

/**
 * 信号强度
 */
export type SignalStrength = 'weak' | 'medium' | 'strong';

/**
 * 技术信号
 */
export interface TechnicalSignal {
  id?: string;
  symbol: string;
  type: SignalType;
  strength?: SignalStrength;
  price?: number;
  indicatorType?: string;
  indicatorValue?: number;
  timestamp: string;
  description?: string;
  confidence?: number;
}

/**
 * 信号列表响应
 */
export interface SignalListResponse extends UnifiedResponse<TechnicalSignal[]> {}

/**
 * 信号详情响应
 */
export interface SignalDetailResponse extends UnifiedResponse<TechnicalSignal> {}
