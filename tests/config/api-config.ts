/**
 * API Configuration Module
 *
 * Centralized configuration for all API endpoints used in E2E tests.
 * Supports dynamic endpoint resolution based on environment variables.
 */

export interface ApiEndpointConfig {
  path: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  description: string;
}

/**
 * API endpoint definitions for all pages
 */
export const API_ENDPOINTS = {
  // Dashboard endpoints
  dashboard: {
    overview: '/api/dashboard/overview',
    portfolio: '/api/dashboard/portfolio',
    performance: '/api/dashboard/performance',
  },

  // Market endpoints
  market: {
    overview: '/api/market/overview',
    search: '/api/market/search',
    stockDetail: '/api/market/stock/:symbol/detail',
    technicalIndicators: '/api/market/stock/:symbol/indicators',
    historicalData: '/api/market/stock/:symbol/historical',
  },

  // Trading endpoints
  trading: {
    orders: '/api/trading/orders',
    positions: '/api/trading/positions',
    executeOrder: '/api/trading/orders/execute',
    cancelOrder: '/api/trading/orders/:orderId/cancel',
  },

  // Portfolio endpoints
  portfolio: {
    positions: '/api/portfolio/positions',
    performance: '/api/portfolio/performance',
    allocation: '/api/portfolio/allocation',
  },

  // Risk endpoints
  risk: {
    metrics: '/api/risk/metrics',
    alerts: '/api/risk/alerts',
    analysis: '/api/risk/analysis',
  },

  // Strategy endpoints
  strategies: {
    list: '/api/strategies',
    create: '/api/strategies',
    detail: '/api/strategies/:strategyId',
    backtest: '/api/strategies/:strategyId/backtest',
    performance: '/api/strategies/:strategyId/performance',
  },

  // Technical analysis endpoints
  technicalAnalysis: {
    indicators: '/api/technical/indicators',
    patterns: '/api/technical/patterns',
    signals: '/api/technical/signals',
  },

  // Task endpoints
  tasks: {
    list: '/api/tasks',
    create: '/api/tasks',
    detail: '/api/tasks/:taskId',
    update: '/api/tasks/:taskId',
    delete: '/api/tasks/:taskId',
  },

  // Settings endpoints
  settings: {
    account: '/api/settings/account',
    notifications: '/api/settings/notifications',
    apiKeys: '/api/settings/api-keys',
    preferences: '/api/settings/preferences',
  },

  // Real-time monitoring endpoints
  monitoring: {
    realTime: '/api/v1/sse/status',
    alerts: '/api/monitoring/alerts',
  },

  // Wencai endpoints (natural language search)
  wencai: {
    queries: '/api/market/wencai/queries',
    search: '/api/market/wencai/search',
  },
};

/**
 * Get full API URL from endpoint path
 *
 * @param endpoint - The endpoint path (e.g., '/api/dashboard/overview')
 * @param baseUrl - Optional base URL, defaults to API_BASE_URL environment variable
 * @returns Full URL
 *
 * @example
 * const url = getApiUrl('/api/dashboard/overview');
 * // Returns: 'http://localhost:8000/api/dashboard/overview'
 */
export function getApiUrl(
  endpoint: string,
  baseUrl: string = process.env.API_BASE_URL || 'http://localhost:8000'
): string {
  // Remove trailing slash from baseUrl if present
  const cleanBaseUrl = baseUrl.replace(/\/$/, '');

  // Ensure endpoint starts with /
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;

  return `${cleanBaseUrl}${cleanEndpoint}`;
}

/**
 * Replace path parameters in endpoint
 *
 * @param endpoint - The endpoint template (e.g., '/api/market/stock/:symbol/detail')
 * @param params - Object containing parameter values
 * @returns Endpoint with parameters replaced
 *
 * @example
 * const endpoint = replacePathParams('/api/market/stock/:symbol/detail', { symbol: 'AAPL' });
 * // Returns: '/api/market/stock/AAPL/detail'
 */
export function replacePathParams(
  endpoint: string,
  params: Record<string, string | number>
): string {
  let result = endpoint;
  Object.entries(params).forEach(([key, value]) => {
    result = result.replace(`:${key}`, String(value));
  });
  return result;
}

/**
 * Build full API URL with parameter replacement
 *
 * @param endpoint - The endpoint template
 * @param params - Path parameters to replace
 * @param baseUrl - Optional base URL
 * @returns Full URL with parameters replaced
 *
 * @example
 * const url = buildApiUrl('/api/market/stock/:symbol/detail', { symbol: 'AAPL' });
 * // Returns: 'http://localhost:8000/api/market/stock/AAPL/detail'
 */
export function buildApiUrl(
  endpoint: string,
  params?: Record<string, string | number>,
  baseUrl?: string
): string {
  const endpointWithParams = params ? replacePathParams(endpoint, params) : endpoint;
  return getApiUrl(endpointWithParams, baseUrl);
}

/**
 * Get endpoint metadata for validation
 *
 * @param category - API category (e.g., 'dashboard', 'market')
 * @param key - Endpoint key within category
 * @returns The endpoint path
 *
 * @example
 * const endpoint = getEndpoint('dashboard', 'overview');
 * // Returns: '/api/dashboard/overview'
 */
export function getEndpoint(category: keyof typeof API_ENDPOINTS, key: string): string {
  const categoryEndpoints = API_ENDPOINTS[category] as Record<string, string>;
  if (!categoryEndpoints || !categoryEndpoints[key]) {
    throw new Error(`Endpoint not found: ${category}.${key}`);
  }
  return categoryEndpoints[key];
}

/**
 * Validate if endpoint exists in configuration
 *
 * @param category - API category
 * @param key - Endpoint key
 * @returns true if endpoint exists, false otherwise
 */
export function endpointExists(category: string, key: string): boolean {
  try {
    getEndpoint(category as keyof typeof API_ENDPOINTS, key);
    return true;
  } catch {
    return false;
  }
}

/**
 * Get all endpoints for a category
 *
 * @param category - API category
 * @returns Object containing all endpoints in the category
 *
 * @example
 * const dashboardEndpoints = getCategoryEndpoints('dashboard');
 * // Returns: { overview: '/api/dashboard/overview', ... }
 */
export function getCategoryEndpoints(
  category: keyof typeof API_ENDPOINTS
): Record<string, string> {
  const categoryEndpoints = API_ENDPOINTS[category] as Record<string, string>;
  if (!categoryEndpoints) {
    throw new Error(`Category not found: ${category}`);
  }
  return categoryEndpoints;
}

/**
 * List all available API categories
 *
 * @returns Array of category names
 *
 * @example
 * const categories = getAvailableCategories();
 * // Returns: ['dashboard', 'market', 'trading', ...]
 */
export function getAvailableCategories(): string[] {
  return Object.keys(API_ENDPOINTS);
}
