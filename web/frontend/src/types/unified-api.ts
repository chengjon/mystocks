/**
 * MyStocks 统一API响应类型定义
 *
 * 完全匹配后端统一API响应结构
 * 对应文件: web/backend/app/core/responses.py
 * 对应文件: web/backend/app/schemas/base_schemas.py
 *
 * @version 2.0
 * @updated 2026-01-20
 */

// ============================================
//   错误详情类型
// ============================================

export interface ErrorDetail {
  field?: string
  code: string
  message: string
}

// ============================================
//   统一API响应类型 (增强版)
// ============================================

/**
 * 统一API响应模型 (增强版)
 *
 * 匹配后端 UnifiedResponse 类
 * success: 操作是否成功
 * code: 业务状态码 (200=成功, 400=参数错误, 401=未认证, 404=未找到, 500=服务器错误)
 * message: 给前端展示的消息
 * data: 实际的业务数据，成功时返回，失败时为null
 * timestamp: 响应生成的时间戳 (UTC)
 * request_id: 请求ID，用于追踪请求日志
 * errors: 详细错误信息数组，仅在请求失败时存在
 */
export interface UnifiedResponse<T = any> {
  success: boolean
  code: number
  message: string
  data?: T | null
  timestamp: string
  request_id?: string
  errors?: ErrorDetail[]
}

/**
 * 统一分页响应模型
 */
export interface UnifiedPaginatedResponse<T = any> extends UnifiedResponse<T> {
  pagination: PaginationInfo
}

/**
 * 分页信息
 */
export interface PaginationInfo {
  page: number
  page_size: number
  total: number
  pages?: number
}

// ============================================
//   标准错误响应
// ============================================

/**
 * 未授权错误响应 (401)
 */
export interface UnauthorizedResponse {
  success: false
  code: 401
  message: string
  data: null
  timestamp: string
  request_id?: string
  errors?: ErrorDetail[]
}

/**
 * 禁止访问响应 (403)
 */
export interface ForbiddenResponse {
  success: false
  code: 403
  message: string
  data: null
  timestamp: string
  request_id?: string
  errors?: ErrorDetail[]
}

/**
 * 未找到响应 (404)
 */
export interface NotFoundResponse {
  success: false
  code: 404
  message: string
  data: null
  timestamp: string
  request_id?: string
  errors?: ErrorDetail[]
}

/**
 * 验证错误响应 (422)
 */
export interface ValidationErrorResponse {
  success: false
  code: 422
  message: string
  data: null
  timestamp: string
  request_id?: string
  errors: ErrorDetail[]
}

/**
 * 服务器错误响应 (500)
 */
export interface ServerErrorResponse {
  success: false
  code: 500
  message: string
  data: null
  timestamp: string
  request_id?: string
  errors?: ErrorDetail[]
}

// ============================================
//   业务数据类型
// ============================================

/**
 * JWT Token 数据
 */
export interface AuthTokenData {
  access_token: string
  token_type: 'bearer'
  expires_in: number
  refresh_token?: string
}

/**
 * CSRF Token 数据
 */
export interface CSRFTokenData {
  csrf_token: string
}

/**
 * 实时行情数据
 */
export interface RealtimeQuote {
  symbol: string
  name?: string
  price: number
  change: number
  change_percent: number
  volume?: number
  amount?: number
  timestamp: string
}

/**
 * K线数据点
 */
export interface KLineData {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount?: number
}

/**
 * 技术指标数据
 */
export interface TechnicalIndicator {
  symbol: string
  indicator: string
  params: Record<string, any>
  values: number[]
  timestamps: number[]
}

/**
 * 资金流向数据
 */
export interface FundFlowData {
  symbol: string
  date: string
  main_inflow: number
  main_outflow: number
  retail_inflow: number
  retail_outflow: number
  net_inflow: number
}

/**
 * 投资组合信息
 */
export interface PortfolioInfo {
  id: string
  name: string
  total_value: number
  total_value_change: number
  total_value_change_percent: number
  positions_count: number
  created_at: string
  updated_at: string
}

/**
 * 持仓信息
 */
export interface Position {
  id: string
  symbol: string
  shares: number
  avg_cost: number
  current_price: number
  market_value: number
  profit_loss: number
  profit_loss_percent: number
  weight: number
}

/**
 * 策略信息
 */
export interface StrategyInfo {
  id: string
  name: string
  type: string
  description?: string
  status: 'active' | 'inactive' | 'testing'
  created_at: string
  updated_at: string
}

/**
 * 回测参数
 */
export interface BacktestParams {
  strategy_id: string
  symbol?: string
  start_date: string
  end_date: string
  initial_capital: number
  params?: Record<string, any>
}

/**
 * 回测结果
 */
export interface BacktestResult {
  id: string
  strategy_id: string
  symbol: string
  start_date: string
  end_date: string
  initial_capital: number
  final_capital: number
  total_return: number
  total_return_percent: number
  annual_return: number
  max_drawdown: number
  sharpe_ratio: number
  trades_count: number
  win_rate: number
}

/**
 * 风险指标
 */
export interface RiskMetrics {
  symbol: string
  var_95?: number
  var_99?: number
  beta?: number
  volatility?: number
  max_drawdown?: number
  sharpe?: number
  timestamp: string
}

/**
 * 预警规则
 */
export interface AlertRule {
  id: string
  name: string
  type: 'price' | 'percent' | 'volume' | 'custom'
  condition: string
  threshold: number
  enabled: boolean
  created_at: string
}

/**
 * 系统健康状态
 */
export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy'
  services: Record<string, 'healthy' | 'unhealthy'>
  database: 'healthy' | 'unhealthy'
  cache: 'healthy' | 'unhealthy'
  timestamp: string
}

// ============================================
//   API 错误类
// ============================================

/**
 * API 错误类
 */
export class APIError extends Error {
  constructor(
    public code: number,
    public message: string,
    public errors?: ErrorDetail[]
  ) {
    super(message)
    this.name = 'APIError'
  }

  static isNotFound(error: any): error is NotFoundResponse {
    return error?.code === 404
  }

  static isUnauthorized(error: any): error is UnauthorizedResponse {
    return error?.code === 401
  }

  static isValidation(error: any): error is ValidationErrorResponse {
    return error?.code === 422 || error?.code === 400
  }

  static isServerError(error: any): error is ServerErrorResponse {
    return error?.code >= 500
  }
}

// ============================================
//   类型保护函数
// ============================================

/**
 * 检查是否为成功响应
 */
export function isSuccessResponse<T>(response: UnifiedResponse<T>): response is UnifiedResponse<T> & { success: true } {
  return response.success === true
}

/**
 * 检查是否为错误响应
 */
export function isErrorResponse(response: UnifiedResponse): response is UnifiedResponse & { success: false } {
  return response.success === false
}

/**
 * 检查是否为分页响应
 */
export function isPaginatedResponse<T>(response: any): response is UnifiedPaginatedResponse<T> {
  return response?.pagination !== undefined
}

// ============================================
//   标准 API 端点路径
// ============================================

/**
 * API 端点路径常量 (完整映射)
 */
export const API_ENDPOINTS = {
  // 认证
  AUTH: {
    CSRF_TOKEN: '/api/auth/csrf-token',
    LOGIN: '/api/auth/login',
    LOGOUT: '/api/auth/logout',
    REFRESH: '/api/auth/refresh',
  },

  // 市场数据 (120+ endpoints)
  MARKET: {
    SUMMARY: '/api/v1/data/market/summary',
    REALTIME: '/api/v1/data/market/realtime',
    TECHNICAL: '/api/indicators/technical',
    FUND_FLOW: '/api/v1/data/market/fund-flow',
    ETF: '/api/v1/data/market/etf',
    CONCEPT: '/api/v1/data/market/concept',
    AUCTION: '/api/v1/data/market/auction',
    LONGHU: '/api/v1/data/market/longhubang',
    INSTITUTION: '/api/v1/data/market/institution',
    WENCAI: '/api/v1/market/wencai',
    SCREENER: '/api/v1/data/market/screener',
  },

  // 股票管理 (50+ endpoints)
  STOCKS: {
    PORTFOLIO: '/api/portfolio/overview',
    WATCHLIST: '/api/watchlist',
    ACTIVITY: '/api/trading/activity',
    STRATEGY_SELECTION: '/api/selection/strategy',
    INDUSTRY_SELECTION: '/api/selection/industry',
    CONCEPT_SELECTION: '/api/selection/concept',
  },

  // 投资分析 (45+ endpoints)
  ANALYSIS: {
    TECHNICAL: '/api/technical/analyze',
    FUNDAMENTAL: '/api/fundamental/analyze',
    INDICATOR: '/api/indicators/calculate',
    CUSTOM_INDICATOR: '/api/indicators/custom',
    STOCK: '/api/analysis/stock',
    LIST: '/api/analysis/list',
  },

  // 风险管理 (37+ endpoints)
  RISK: {
    OVERVIEW: '/api/risk/overview',
    ALERTS: '/api/risk/alerts',
    INDICATORS: '/api/risk/indicators',
    SENTIMENT: '/api/risk/sentiment',
    POSITION: '/api/risk/position',
    FACTORS: '/api/risk/factors',
  },

  // 策略交易 (50+ endpoints)
  STRATEGY: {
    OVERVIEW: '/api/strategy/overview',
    DESIGN: '/api/strategy/design',
    LIST: '/api/strategy/list',
    BACKTEST: '/api/backtest/run',
    GPU_BACKTEST: '/api/gpu/backtest',
    SIGNALS: '/api/signals',
    TRADE_HISTORY: '/api/trading/history',
    POSITIONS: '/api/positions',
    ATTRIBUTION: '/api/attribution',
  },

  // 系统监控 (35+ endpoints)
  SYSTEM: {
    MONITORING: '/api/monitoring/dashboard',
    SETTINGS: '/api/system/settings',
    DATA_UPDATE: '/api/system/data-update',
    DATA_QUALITY: '/api/monitoring/data-quality',
    API_HEALTH: '/api/monitoring/api-health',
  },
} as const

// 导出类型
export type APIEndpointPath = typeof API_ENDPOINTS[keyof typeof API_ENDPOINTS]
