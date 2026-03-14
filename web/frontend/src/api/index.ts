/**
 * Unified API Entry Point (v2.0 Standard)
 * Refactored 2026-02-14
 * 
 * This file serves as a bridge between legacy imports and the new 
 * standardized API client. It resolves circular dependencies by 
 * removing router/store imports.
 */

import { apiClient } from './apiClient.ts'
import type { UnifiedResponse } from './types/common.ts'
import type {
  StockListResponse,
  MarketOverview,
  KlineResponse,
  AlertRuleResponse,
  AlertRecordResponse,
  StrategyConfig
} from './types/common.ts'
import type { LoginResponse } from './types/admin.ts'

// Legacy compatibility export for modules still importing `request` from this entry.
export const request = apiClient

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
  getAlertRules: (): Promise<UnifiedResponse<AlertRuleResponse[]>> => apiClient.get('/v1/monitoring/alert-rules'),
  getAlerts: (params: Record<string, unknown>): Promise<UnifiedResponse<AlertRecordResponse[]>> => apiClient.get('/v1/monitoring/alerts', { params }),
  // New method for announcements
  getAnnouncements: (params: Record<string, unknown> = {}): Promise<UnifiedResponse<any>> => apiClient.get('/announcement/list', { params }),
  // Data source configuration
  getDataSourceConfig: (): Promise<UnifiedResponse<any>> => apiClient.get('/v1/data-sources/config/'),
  updateDataSourceConfig: (data: Record<string, unknown>): Promise<UnifiedResponse<any>> => apiClient.post('/v1/data-sources/config/batch', data),
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
  getIndicators: (symbol: string): Promise<UnifiedResponse<unknown>> => apiClient.get(`/v1/technical/indicators/${symbol}`),
  getAnalysis: (symbol: string): Promise<UnifiedResponse<unknown>> => apiClient.get(`/v1/technical/analysis/${symbol}`),
  getBatchIndicators: (symbols: string[], params: { indicators: string[] }): Promise<UnifiedResponse<unknown>> =>
    apiClient.post('/v1/technical/batch', { symbols, ...params }),
}

// --- Default Export (Compatibility) ---
const api = {
  auth: authApi,
  data: dataApi,
  market: marketApi,
  monitoring: monitoringApi,
  strategy: strategyApi
}

export default api
