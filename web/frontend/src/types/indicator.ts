/**
 * Indicator TypeScript Type Definitions
 * 技术指标类型定义
 */

import type { PanelType, IndicatorCategory } from './backend_types';

// Re-export types from backend_types for convenience
export type { PanelType, IndicatorCategory };
 
/**
 * 指标参数定义
 */
export interface IndicatorParameter {
  name: string;
  type: 'int' | 'float' | 'string' | 'bool';
  default: number | string | boolean;
  min?: number;
  max?: number;
  step?: number;
  description: string;
}
 
/**
 * 指标输出定义
 */
export interface IndicatorOutput {
  name: string;
  description: string;
}
 
/**
 * 指标元数据
 */
export interface IndicatorMetadata {
  abbreviation: string;
  fullName: string;
  chineseName: string;
  category: IndicatorCategory;
  description: string;
  panelType: PanelType;
  parameters: IndicatorParameter[];
  outputs: IndicatorOutput[];
  referenceLines: number[] | null;
  minDataPointsFormula: string;
}
 
/**
 * 指标规格 (用户选择的指标配置)
 */
export interface IndicatorSpec {
  abbreviation: string;
  parameters: Record<string, any>;
}
 
/**
 * 指标计算请求
 */
export interface IndicatorCalculateRequest {
  symbol: string;
  startDate: string; // YYYY-MM-DD
  endDate: string;   // YYYY-MM-DD
  indicators: IndicatorSpec[];
  useCache?: boolean;
}
 
/**
 * 指标值输出
 */
export interface IndicatorValueOutput {
  outputName: string;
  values: (number | null)[];
  displayName: string;
}
 
/**
 * 指标计算结果
 */
export interface IndicatorResult {
  abbreviation: string;
  parameters: Record<string, any>;
  outputs: IndicatorValueOutput[];
  panelType: PanelType;
  referenceLines: number[] | null;
  error: string | null;
}
 
/**
 * OHLCV K线数据
 */
export interface OHLCVData {
  dates: string[];
  open: number[];
  high: number[];
  low: number[];
  close: number[];
  volume: number[];
}
 
/**
 * 指标计算响应
 */
export interface IndicatorCalculateResponse {
  symbol: string;
  symbolName: string;
  startDate: string;
  endDate: string;
  ohlcv: OHLCVData;
  indicators: IndicatorResult[];
  calculationTimeMs: number;
  cached: boolean;
}
 
/**
 * 指标注册表响应
 */
export interface IndicatorRegistryResponse {
  totalCount: number;
  categories: Record<IndicatorCategory, number>;
  indicators: IndicatorMetadata[];
}
 
/**
 * 指标配置 (保存的配置)
 */
export interface IndicatorConfig {
  id: number;
  userId: number;
  name: string;
  indicators: IndicatorSpec[];
  createdAt: string;
  updatedAt: string;
  lastUsedAt: string | null;
}
 
/**
 * 指标配置列表响应
 */
export interface IndicatorConfigListResponse {
  totalCount: number;
  configs: IndicatorConfig[];
}
 
/**
 * 指标配置创建请求
 */
export interface IndicatorConfigCreateRequest {
  name: string;
  indicators: IndicatorSpec[];
}
 
/**
 * 指标配置更新请求
 */
export interface IndicatorConfigUpdateRequest {
  name?: string;
  indicators?: IndicatorSpec[];
}
 
/**
 * API响应包装器
 */
export interface APIResponse<T = any> {
  success: boolean;
  data: T | null;
  error: { errorCode: string; errorMessage: string; details?: Record<string, any> } | null;
  timestamp: string;
}
 
/**
 * 指标选择器状态
 */
export interface IndicatorSelectorState {
  selectedCategory: IndicatorCategory | null;
  searchKeyword: string;
  selectedIndicators: IndicatorSpec[];
}
 
/**
 * 图表配置
 */
export interface ChartConfig {
  symbol: string;
  startDate: string;
  endDate: string;
  indicators: IndicatorSpec[];
}
