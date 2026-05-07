/**
 * Unified API Entry Point (v2.0 Standard)
 * Refactored 2026-02-14
 * 
 * This file serves as a bridge between legacy imports and the new 
 * standardized API client. It resolves circular dependencies by 
 * removing router/store imports.
 */

import { apiClient } from './apiClient.ts'
import { kronosApi } from './kronos.ts'
import type { UnifiedResponse } from './types/common.ts'
import type {
  StockListResponse,
  MarketOverview,
  KlineResponse,
  AlertRuleResponse,
  AlertRecordResponse,
  StrategyConfig
} from './types/common.ts'
import type { LoginResponse } from '../types/user/index.ts'

// Legacy compatibility export for modules still importing `request` from this entry.
export const request = apiClient

type TechnicalIndicatorType = 'trend' | 'momentum' | 'volatility' | 'volume'

interface TechnicalIndicatorsPayload {
  symbol?: string
  latest_date?: string
  trend?: Record<string, unknown>
  momentum?: Record<string, unknown>
  volatility?: Record<string, unknown>
  volume?: Record<string, unknown>
}

interface TechnicalIndicatorRow {
  id: string
  name: string
  type: TechnicalIndicatorType
  value: number
  signal?: 'buy' | 'sell' | 'hold'
  status: 'normal' | 'warning' | 'alert'
  description: string
  last_updated: string
}

type TechnicalPatternPeriod = 'daily' | 'weekly' | 'monthly'
type TechnicalPatternName =
  | 'double_top'
  | 'double_bottom'
  | 'head_shoulders_top'
  | 'head_shoulders_bottom'
  | 'common_gap'
  | 'breakaway_gap'
  | 'runaway_gap'
  | 'exhaustion_gap'
export type TechnicalGapSide = 'up' | 'down'
export type TechnicalGapFillStatus = 'open' | 'partially_filled' | 'filled'

export interface TechnicalGapZone {
  start_timestamp: number
  end_timestamp: number
  upper_value: number
  lower_value: number
  filled_at: number | null
}

interface TechnicalPatternAnchorPoint {
  role: string
  timestamp: number
  value: number
}

export interface TechnicalPatternDetection {
  pattern_name: TechnicalPatternName
  direction: 'bullish' | 'bearish'
  confidence: number
  anchor_points: TechnicalPatternAnchorPoint[]
  gap_side: TechnicalGapSide | null
  gap_fill_status: TechnicalGapFillStatus | null
  gap_zone: TechnicalGapZone | null
}

export interface TechnicalPatternData {
  status: 'available' | 'empty'
  symbol: string
  period: TechnicalPatternPeriod
  patterns: TechnicalPatternDetection[]
}

function toNumericValue(value: unknown): number | null {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value
  }

  if (typeof value === 'string') {
    const parsed = Number.parseFloat(value)
    return Number.isFinite(parsed) ? parsed : null
  }

  return null
}

function inferIndicatorSignal(name: string, value: number): 'buy' | 'sell' | 'hold' | undefined {
  if (name.startsWith('rsi')) {
    if (value <= 30) return 'buy'
    if (value >= 70) return 'sell'
    return 'hold'
  }

  if (name === 'macd' || name === 'macd_hist') {
    return value >= 0 ? 'buy' : 'sell'
  }

  return undefined
}

function inferIndicatorStatus(name: string, value: number): 'normal' | 'warning' | 'alert' {
  if (name.startsWith('rsi')) {
    if (value <= 20 || value >= 80) return 'alert'
    if (value <= 30 || value >= 70) return 'warning'
  }

  if ((name === 'macd' || name === 'macd_hist') && value < 0) {
    return 'warning'
  }

  return 'normal'
}

function normalizeTechnicalIndicators(payload: TechnicalIndicatorsPayload) {
  const rows: TechnicalIndicatorRow[] = []
  const indicatorGroups: Array<[TechnicalIndicatorType, Record<string, unknown> | undefined]> = [
    ['trend', payload.trend],
    ['momentum', payload.momentum],
    ['volatility', payload.volatility],
    ['volume', payload.volume],
  ]

  for (const [type, indicators] of indicatorGroups) {
    if (!indicators) {
      continue
    }

    for (const [name, rawValue] of Object.entries(indicators)) {
      const value = toNumericValue(rawValue)
      if (value === null) {
        continue
      }

      rows.push({
        id: `${type}-${name}`,
        name: name.toUpperCase(),
        type,
        value,
        signal: inferIndicatorSignal(name, value),
        status: inferIndicatorStatus(name, value),
        description: `${type} indicator ${name.toUpperCase()}`,
        last_updated: payload.latest_date || new Date().toISOString(),
      })
    }
  }

  return {
    success: true,
    symbol: payload.symbol || '',
    stock_name: payload.symbol || 'UNKNOWN STOCK',
    indicators: rows,
    data: payload,
  }
}

function normalizeTechnicalBatchResult(response: Record<string, unknown>) {
  const results = (response.results && typeof response.results === 'object')
    ? response.results as Record<string, unknown>
    : {}

  const stocksCount = Object.keys(results).length
  return {
    ...response,
    success: response.success !== false,
    data: {
      stocks_count: stocksCount,
      success_count: stocksCount,
      signals_count: stocksCount,
    },
    results,
  }
}

// --- Auth API (v1 compatible) ---
export const authApi = {
  login: (username: string, password: string): Promise<UnifiedResponse<LoginResponse>> => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    return apiClient.post('/v1/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
  },
  logout: (): Promise<UnifiedResponse<void>> => apiClient.post('/v1/auth/logout'),
  getCurrentUser: (): Promise<UnifiedResponse<unknown>> => apiClient.get('/v1/auth/me'),
}

// --- Data API (v1 compatible) ---
export const dataApi = {
  getStocksBasic: (params: Record<string, unknown>): Promise<UnifiedResponse<StockListResponse>> => apiClient.get('/v1/data/stocks/basic', { params }),
  getMarketOverview: (): Promise<UnifiedResponse<MarketOverview>> => apiClient.get('/v1/data/markets/overview'),
  getStockDetail: (symbol: string): Promise<UnifiedResponse<unknown>> => apiClient.get(`/v1/data/stocks/${symbol}/detail`),
  getKline: (params: Record<string, unknown>): Promise<UnifiedResponse<KlineResponse>> => apiClient.get('/v1/market/kline', { params }),
  getStocksIndustries: (): Promise<UnifiedResponse<Array<{ industry_name: string }>>> => apiClient.get('/v1/data/stocks/industries'),
  getStocksConcepts: (): Promise<UnifiedResponse<Array<{ concept_name: string }>>> => apiClient.get('/v1/data/stocks/concepts'),
}

// --- Market API (v1 compatible) ---
export const marketApi = {
  getQuotes: (symbols?: string): Promise<UnifiedResponse<unknown>> => apiClient.get('/v1/market/quotes', { params: { symbols } }),
  getStocks: (params?: Record<string, unknown>): Promise<UnifiedResponse<StockListResponse>> => apiClient.get('/v1/market/stocks', { params }),
}

// --- Monitoring API (v1 compatible) ---
export const monitoringApi = {
  // Existing methods
  getSystemHealth: (): Promise<UnifiedResponse<unknown>> => apiClient.get('/health'),
  getDetailedSystemHealth: (): Promise<UnifiedResponse<unknown>> => apiClient.get('/health/detailed'),
  getSystemResources: (params: Record<string, unknown>): Promise<UnifiedResponse<unknown>> =>
    apiClient.get('/v1/system/resources', { params }),
  getSystemGeneralSettings: (): Promise<UnifiedResponse<unknown>> => apiClient.get('/v1/system/settings/general'),
  updateSystemGeneralSettings: (data: Record<string, unknown>): Promise<UnifiedResponse<unknown>> =>
    apiClient.post('/v1/system/settings/general', data),
  getAlertRules: (): Promise<UnifiedResponse<AlertRuleResponse[]>> => apiClient.get('/v1/monitoring/alert-rules'),
  getAlerts: (params: Record<string, unknown>): Promise<UnifiedResponse<AlertRecordResponse[]>> => apiClient.get('/v1/monitoring/alerts', { params }),
  // New method for announcements
  getAnnouncements: (params: Record<string, unknown> = {}): Promise<UnifiedResponse<any>> => apiClient.get('/announcement/list', { params }),
  // Data source configuration
  getDataSourceConfig: (): Promise<UnifiedResponse<any>> => apiClient.get('/v1/data-sources/config/'),
  getSystemSecuritySettings: (): Promise<UnifiedResponse<unknown>> => apiClient.get('/v1/system/settings/security'),
  updateDataSourceConfig: (data: Record<string, unknown>): Promise<UnifiedResponse<any>> => apiClient.post('/v1/data-sources/config/batch', data),
  updateSystemSecuritySettings: (data: Record<string, unknown>): Promise<UnifiedResponse<unknown>> =>
    apiClient.post('/v1/system/settings/security', data),
  // CRUD for alert rules
  createAlertRule: (data: Record<string, unknown>): Promise<UnifiedResponse<AlertRuleResponse>> => apiClient.post('/v1/monitoring/alert-rules', data),
  updateAlertRule: (id: string, data: Record<string, unknown>): Promise<UnifiedResponse<AlertRuleResponse>> => apiClient.put(`/v1/monitoring/alert-rules/${id}`, data),
  deleteAlertRule: (id: string): Promise<UnifiedResponse<void>> => apiClient.delete(`/v1/monitoring/alert-rules/${id}`),
};
// --- Strategy API (v1 compatible) ---
export const strategyApi = {
  getStrategies: (params: Record<string, unknown>): Promise<UnifiedResponse<StrategyConfig[]>> => apiClient.get('/v1/strategy/strategies', { params }),
  getSignals: (params?: Record<string, unknown>): Promise<UnifiedResponse<unknown>> => apiClient.get('/v1/trade/signals', { params }),
}

// --- Technical API (v1 compatible) ---
export const technicalApi = {
  async getIndicators(symbol: string): Promise<UnifiedResponse<unknown>> {
    const response = await apiClient.get<TechnicalIndicatorsPayload>(`/v1/technical/${symbol}/indicators`)
    return normalizeTechnicalIndicators(response) as unknown as UnifiedResponse<unknown>
  },
  getAnalysis: (symbol: string): Promise<UnifiedResponse<unknown>> => apiClient.get(`/v1/technical/${symbol}/signals`),
  getPatterns: (symbol: string, period: TechnicalPatternPeriod): Promise<UnifiedResponse<TechnicalPatternData>> =>
    apiClient.get(`/v1/technical/patterns/${symbol}`, { params: { period } }),
  async getBatchIndicators(symbols: string[], _params: { indicators: string[] }): Promise<UnifiedResponse<unknown>> {
    const response = await apiClient.post<Record<string, unknown>>(
      '/v1/technical/batch/indicators',
      {},
      { params: { symbols } },
    )
    return normalizeTechnicalBatchResult(response) as unknown as UnifiedResponse<unknown>
  },
}

// --- Default Export (Compatibility) ---
const api = {
  auth: authApi,
  data: dataApi,
  market: marketApi,
  monitoring: monitoringApi,
  strategy: strategyApi,
  kronos: kronosApi
}

export default api
export { kronosApi }
