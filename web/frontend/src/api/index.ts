/**
 * Unified API Entry Point (v2.0 Standard)
 * Refactored 2026-02-14
 * 
 * This file serves as a bridge between legacy imports and the new 
 * standardized API client. It resolves circular dependencies by 
 * removing router/store imports.
 */

import { apiClient } from './apiClient'

// --- Auth API (v1 compatible) ---
export const authApi = {
  login: (username: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    return apiClient.post('/v1/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
  },
  logout: () => apiClient.post('/v1/auth/logout'),
  getCurrentUser: () => apiClient.get('/v1/auth/me'),
}

// --- Data API (v1 compatible) ---
export const dataApi = {
  getStocksBasic: (params: any) => apiClient.get('/v1/data/stocks/basic', { params }),
  getMarketOverview: () => apiClient.get('/v1/data/markets/overview'),
  getStockDetail: (symbol: string) => apiClient.get(`/v1/data/stocks/${symbol}/detail`),
  getKline: (params: any) => apiClient.get('/v1/market/kline', { params }),
}

// --- Market API (v1 compatible) ---
export const marketApi = {
  getQuotes: (symbols?: string) => apiClient.get('/v1/market/quotes', { params: { symbols } }),
  getStocks: (params?: any) => apiClient.get('/v1/market/stocks', { params }),
}

// --- Monitoring API (v1 compatible) ---
export const monitoringApi = {
  getAlertRules: () => apiClient.get('/v1/monitoring/alert-rules'),
  getAlerts: (params: any) => apiClient.get('/v1/monitoring/alerts', { params }),
}

// --- Strategy API (v1 compatible) ---
export const strategyApi = {
  getStrategies: (params: any) => apiClient.get('/v1/strategy/strategies', { params }),
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
