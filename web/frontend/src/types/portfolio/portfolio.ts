/**
 * @fileoverview 投资组合模块类型定义
 * @description 提供投资组合相关的类型定义
 * @module types/portfolio
 * @version 1.0.0
 */

import type { UnifiedResponse, UnifiedPaginatedResponse } from '../common/response';

/**
 * 投资组合
 */
export interface Portfolio {
  id: string;
  name: string;
  description?: string;
  type?: 'conservative' | 'balanced' | 'aggressive' | 'custom';
  riskLevel?: 'low' | 'medium' | 'high';
  targetReturn?: number;
  targetVolatility?: number;
  createdAt?: string;
  updatedAt?: string;
}

/**
 * 投资组合列表响应
 */
export interface PortfolioListResponse extends UnifiedPaginatedResponse<Portfolio[]> {}

/**
 * 投资组合详情响应
 */
export interface PortfolioDetailResponse extends UnifiedResponse<Portfolio> {}

/**
 * 持仓项
 */
export interface Position {
  id: string;
  portfolioId: string;
  symbol: string;
  name?: string;
  type?: 'long' | 'short';
  quantity: number;
  avgCost: number;
  currentPrice: number;
  marketValue: number;
  costValue: number;
  pnl?: number;
  pnlPercent?: number;
  weight?: number;
  riskAmount?: number;
  stopLoss?: number;
  takeProfit?: number;
  entryDate?: string;
  lastUpdate?: string;
}

/**
 * 持仓列表响应
 */
export interface PositionListResponse extends UnifiedPaginatedResponse<Position[]> {}

/**
 * 创建投资组合请求
 */
export interface CreatePortfolioRequest {
  name: string;
  description?: string;
  type?: 'conservative' | 'balanced' | 'aggressive' | 'custom';
  riskLevel?: 'low' | 'medium' | 'high';
  targetReturn?: number;
  targetVolatility?: number;
}

/**
 * 创建投资组合响应
 */
export interface CreatePortfolioResponse extends UnifiedResponse<Portfolio> {}

/**
 * 更新投资组合请求
 */
export interface UpdatePortfolioRequest {
  name?: string;
  description?: string;
  type?: 'conservative' | 'balanced' | 'aggressive' | 'custom';
  riskLevel?: 'low' | 'medium' | 'high';
  targetReturn?: number;
  targetVolatility?: number;
}

/**
 * 更新投资组合响应
 */
export interface UpdatePortfolioResponse extends UnifiedResponse<Portfolio> {}

/**
 * 删除投资组合请求
 */
export interface DeletePortfolioRequest {
  portfolioId: string;
}

/**
 * 删除投资组合响应
 */
export interface DeletePortfolioResponse extends UnifiedResponse<null> {}
