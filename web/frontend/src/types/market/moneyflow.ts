/**
 * @fileoverview 资金流向数据类型定义
 * @description 提供资金流向相关的类型定义
 * @module types/market
 * @version 1.0.0
 */

import type { UnifiedResponse } from '../common/response';

/**
 * 资金流向类型
 */
export type FlowType = 'main' | 'retail' | 'institution' | 'foreign';

/**
 * 资金流向数据点
 */
export interface MoneyFlowItem {
  date: string;
  symbol?: string;
  mainNetInflow?: number;
  mainNetOutflow?: number;
  retailNetInflow?: number;
  retailNetOutflow?: number;
  institutionNetInflow?: number;
  institutionNetOutflow?: number;
  foreignNetInflow?: number;
  foreignNetOutflow?: number;
  totalNetInflow?: number;
  totalNetOutflow?: number;
}

/**
 * 资金流向数据集合
 */
export interface MoneyFlowData {
  symbol: string;
  period?: string;
  flowType?: FlowType;
  data: MoneyFlowItem[];
  startTime?: string;
  endTime?: string;
}

/**
 * 资金流向响应
 */
export interface MoneyFlowResponse extends UnifiedResponse<MoneyFlowData> {}
