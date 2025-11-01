/**
 * Indicator TypeScript Type Definitions
 * 技术指标类型定义
 */

/**
 * 指标分类
 */
export enum IndicatorCategory {
  TREND = 'trend',
  MOMENTUM = 'momentum',
  VOLATILITY = 'volatility',
  VOLUME = 'volume',
  CANDLESTICK = 'candlestick'
}

/**
 * 面板类型
 */
export enum PanelType {
  OVERLAY = 'overlay',      // 叠加在主图上
  OSCILLATOR = 'oscillator' // 独立震荡器面板
}

/**
 * 指标参数定义
 */
export interface IndicatorParameter {
  name: string
  type: 'int' | 'float' | 'string' | 'bool'
  default: number | string | boolean
  min?: number
  max?: number
  step?: number
  description: string
}

/**
 * 指标输出定义
 */
export interface IndicatorOutput {
  name: string
  description: string
}

/**
 * 指标元数据
 */
export interface IndicatorMetadata {
  abbreviation: string
  full_name: string
  chinese_name: string
  category: IndicatorCategory
  description: string
  panel_type: PanelType
  parameters: IndicatorParameter[]
  outputs: IndicatorOutput[]
  reference_lines: number[] | null
  min_data_points_formula: string
}

/**
 * 指标规格 (用户选择的指标配置)
 */
export interface IndicatorSpec {
  abbreviation: string
  parameters: Record<string, any>
}

/**
 * 指标计算请求
 */
export interface IndicatorCalculateRequest {
  symbol: string
  start_date: string // YYYY-MM-DD
  end_date: string   // YYYY-MM-DD
  indicators: IndicatorSpec[]
  use_cache?: boolean
}

/**
 * 指标值输出
 */
export interface IndicatorValueOutput {
  output_name: string
  values: (number | null)[]
  display_name: string
}

/**
 * 指标计算结果
 */
export interface IndicatorResult {
  abbreviation: string
  parameters: Record<string, any>
  outputs: IndicatorValueOutput[]
  panel_type: PanelType
  reference_lines: number[] | null
  error: string | null
}

/**
 * OHLCV K线数据
 */
export interface OHLCVData {
  dates: string[]
  open: number[]
  high: number[]
  low: number[]
  close: number[]
  volume: number[]
}

/**
 * 指标计算响应
 */
export interface IndicatorCalculateResponse {
  symbol: string
  symbol_name: string
  start_date: string
  end_date: string
  ohlcv: OHLCVData
  indicators: IndicatorResult[]
  calculation_time_ms: number
  cached: boolean
}

/**
 * 指标注册表响应
 */
export interface IndicatorRegistryResponse {
  total_count: number
  categories: Record<IndicatorCategory, number>
  indicators: IndicatorMetadata[]
}

/**
 * 指标配置 (保存的配置)
 */
export interface IndicatorConfig {
  id: number
  user_id: number
  name: string
  indicators: IndicatorSpec[]
  created_at: string
  updated_at: string
  last_used_at: string | null
}

/**
 * 指标配置列表响应
 */
export interface IndicatorConfigListResponse {
  total_count: number
  configs: IndicatorConfig[]
}

/**
 * 指标配置创建请求
 */
export interface IndicatorConfigCreateRequest {
  name: string
  indicators: IndicatorSpec[]
}

/**
 * 指标配置更新请求
 */
export interface IndicatorConfigUpdateRequest {
  name?: string
  indicators?: IndicatorSpec[]
}

/**
 * 错误详情
 */
export interface ErrorDetail {
  error_code: string
  error_message: string
  details?: Record<string, any>
}

/**
 * API 响应包装器
 */
export interface APIResponse<T = any> {
  success: boolean
  data: T | null
  error: ErrorDetail | null
  timestamp: string
}

/**
 * 指标选择器状态
 */
export interface IndicatorSelectorState {
  selectedCategory: IndicatorCategory | null
  searchKeyword: string
  selectedIndicators: IndicatorSpec[]
}

/**
 * 图表配置
 */
export interface ChartConfig {
  symbol: string
  startDate: string
  endDate: string
  indicators: IndicatorSpec[]
}
