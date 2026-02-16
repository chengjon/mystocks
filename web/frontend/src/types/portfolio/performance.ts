/**
 * @fileoverview 投资组合-绩效模块类型定义
 * @description 提供投资组合绩效相关的类型定义
 * @module types/portfolio
 * @version 1.0.0
 */

import type { UnifiedResponse, UnifiedPaginatedResponse } from '../common/response';

/**
 * 绩效指标
 */
export interface PerformanceMetrics {
  totalReturn?: number;
  annualizedReturn?: number;
  volatility?: number;
  sharpeRatio?: number;
  maxDrawdown?: number;
  beta?: number;
  alpha?: number;
  informationRatio?: number;
  trackingError?: number;
  totalValue?: number;
  startDate?: string;
  endDate?: string;
  benchmark?: string;
}

/**
 * 绩效指标响应
 */
export interface PerformanceMetricsResponse extends UnifiedResponse<PerformanceMetrics> {}

/**
 * 收益分解
 */
export interface ReturnBreakdown {
  period: string;
  totalReturn?: number;
  annualizedReturn?: number;
  contribution?: number;
  benchmarkReturn?: number;
  excessReturn?: number;
}

/**
 * 收益分解列表
 */
export interface ReturnBreakdownListResponse extends UnifiedResponse<ReturnBreakdown[]> {}

/**
 * 风险分析
 */
export interface RiskAnalysis {
  valueAtRisk?: number;
  varAtRisk?: number;
  cvar?: number;
  stressTestVaR?: number;
  concentrationRisk?: number;
  liquidityRisk?: number;
  currencyRisk?: number;
}

/**
 * 风险分析响应
 */
export interface RiskAnalysisResponse extends UnifiedResponse<RiskAnalysis> {}

/**
 * 获取绩效请求
 */
export interface GetPerformanceRequest {
  portfolioId: string;
  startDate?: string;
  endDate?: string;
  benchmark?: string;
}

/**
 * 获取绩效响应
 */
export interface GetPerformanceResponse extends UnifiedResponse<{
  metrics: PerformanceMetrics;
  returnBreakdowns?: ReturnBreakdown[];
  riskAnalysis?: RiskAnalysis;
}> {}
