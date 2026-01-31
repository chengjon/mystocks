/**
 * @fileoverview 投资组合-风险模块类型定义
 * @description 提供投资组合风险相关的类型定义
 * @module types/portfolio
 * @version 1.0.0
 */

import type { UnifiedResponse, PaginationInfo } from '../common/response';

/**
 * 风险指标
 */
export interface RiskMetrics {
  portfolioValue?: number;
  totalValueAtRisk?: number;
  maxDrawdown?: number;
  var95?: number;
  var99?: number;
  cvar95?: number;
  beta?: number;
  trackingError?: number;
  concentrationRatio?: number;
  diversificationRatio?: number;
}

/**
 * 风险度量响应
 */
export interface RiskMetricsResponse extends UnifiedResponse<RiskMetrics> {}

/**
 * 风险分析报告
 */
export interface RiskReport {
  id: string;
  portfolioId: string;
  reportDate: string;
  summary?: string;
  recommendations?: string[];
  metrics: RiskMetrics;
  exposure?: Record<string, any>;
}

/**
 * 风险报告列表响应
 */
export interface RiskReportListResponse extends UnifiedPaginatedResponse<RiskReport[]> {}

/**
 * 风险限额设置
 */
export interface RiskLimitSettings {
  maxPositionSize?: number;
  maxSectorExposure?: number;
  maxSingleStockExposure?: number;
  maxLeverage?: number;
  stopLossPercent?: number;
}

/**
 * 风险限额响应
 */
export interface RiskLimitSettingsResponse extends UnifiedResponse<RiskLimitSettings> {}

/**
 * 更新风险限额请求
 */
export interface UpdateRiskLimitRequest {
  maxPositionSize?: number;
  maxSectorExposure?: number;
  maxSingleStockExposure?: number;
  maxLeverage?: number;
  stopLossPercent?: number;
}
