/**
 * @fileoverview 投资组合-资产配置模块类型定义
 * @description 提供投资组合资产配置相关的类型定义
 * @module types/portfolio
 * @version 1.0.0
 */

import type { UnifiedResponse, PaginationInfo } from '../common/response';

/**
 * 资产配置项
 */
export interface AssetAllocation {
  id: string;
  portfolioId: string;
  symbol: string;
  name: string;
  assetType: 'stock' | 'bond' | 'etf' | 'fund' | 'cash' | 'other';
  weight: number;
  targetWeight?: number;
  currentWeight?: number;
  category?: string;
  subCategory?: string;
  riskLevel?: 'low' | 'medium' | 'high';
  expectedReturn?: number;
  updatedAt?: string;
}

/**
 * 资产配置列表响应
 */
export interface AssetAllocationListResponse extends UnifiedPaginatedResponse<AssetAllocation[]> {}

/**
 * 资产类别
 */
export interface AssetCategory {
  id: string;
  name: string;
  icon?: string;
  description?: string;
  assets: AssetAllocation[];
}

/**
 * 资产类别响应
 */
export interface AssetCategoryResponse extends UnifiedResponse<AssetCategory[]> {}

/**
 * 更新资产配置请求
 */
export interface UpdateAssetAllocationRequest {
  allocationId: string;
  weight?: number;
  targetWeight?: number;
  category?: string;
  subCategory?: string;
}

/**
 * 更新资产配置响应
 */
export interface UpdateAssetAllocationResponse extends UnifiedResponse<AssetAllocation> {}

/**
 * 调整资产权重请求
 */
export interface RebalanceAssetsRequest {
  portfolioId: string;
  reason?: string;
  tolerance?: number;
}

/**
 * 调整资产权重响应
 */
export interface RebalanceAssetsResponse extends UnifiedResponse<{
  newAllocations: AssetAllocation[];
  transactionCosts?: number;
}> {}
