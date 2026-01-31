/**
 * @fileoverview 投资组合-再平衡模块类型定义
 * @description 提供投资组合再平衡相关的类型定义
 * @module types/portfolio
 * @version 1.0.0
 */

import type { UnifiedResponse, PaginationInfo } from '../common/response';
import type { Position } from './portfolio';

/**
 * 再平衡策略
 */
export type RebalanceStrategy = 'equal_weight' | 'optimal' | 'risk_parity' | 'custom';

/**
 * 再平衡建议
 */
export interface RebalanceRecommendation {
  portfolioId: string;
  strategy?: RebalanceStrategy;
  reason?: string;
  targetAllocations?: {
    symbol: string;
    targetWeight: number;
    action: 'buy' | 'sell' | 'hold';
  }[];
  estimatedImpact?: {
    cost?: number;
    expectedImprovement?: string;
  };
  priority?: 'low' | 'medium' | 'high';
  timestamp?: string;
}

/**
 * 再平衡建议列表响应
 */
export interface RebalanceRecommendationListResponse extends UnifiedResponse<RebalanceRecommendation[]> {}

/**
 * 执行再平衡请求
 */
export interface ExecuteRebalanceRequest {
  portfolioId: string;
  strategy?: RebalanceStrategy;
  tolerance?: number;
  minTradeSize?: number;
  executeNow?: boolean;
}

/**
 * 执行再平衡响应
 */
export interface ExecuteRebalanceResponse extends UnifiedResponse<{
  executionId: string;
  status: 'pending' | 'executing' | 'completed' | 'failed';
  trades?: Position[];
  totalCost?: number;
  estimatedTime?: string;
}> {}
