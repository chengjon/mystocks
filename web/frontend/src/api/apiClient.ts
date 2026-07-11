/**
 * API Client for Strategy Module
 *
 * Lightweight HTTP client that returns full UnifiedResponse objects
 * for fallback strategy implementation.
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import type { UnifiedResponse } from './types/common.ts';
import { createCSRFTokenResolver } from './csrfTokenResolver.ts';

// Request configuration
interface RequestConfig extends AxiosRequestConfig {
  skipErrorHandler?: boolean;
  skipCSRF?: boolean;
}

// Internal request config for interceptors (currently unused)
// interface InternalRequestConfig extends InternalAxiosRequestConfig {
//   skipErrorHandler?: boolean;
//   skipCSRF?: boolean;
// }

// Create axios instance
const instance: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor
instance.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Add JWT token for authentication
    const jwtToken = getJWTToken();
    if (jwtToken) {
      config.headers.Authorization = `Bearer ${jwtToken}`;
    }

    // Add CSRF token for POST/PUT/PATCH/DELETE
    if (
      config.method?.toUpperCase() !== 'GET' &&
      !(config as RequestConfig).skipCSRF &&
      !config.headers['X-CSRF-Token']
    ) {
      try {
        const token = await getCSRFToken();
        config.headers['X-CSRF-Token'] = token;
      } catch (error) {
        console.error('[apiClient] Failed to get CSRF token:', error);
      }
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - preserve AxiosResponse shape
instance.interceptors.response.use(
  (response: AxiosResponse<UnifiedResponse<unknown>>): AxiosResponse<UnifiedResponse<unknown>> => {
    // Extract tracing headers
    const requestId = response.headers['x-request-id'] || ''
    const processTime =
      response.headers['x-process-time'] ||
      response.headers['x-process-time-ms'] ||
      ''

    // Merge tracing into data if it's a UnifiedResponse
    if (response.data && typeof response.data === 'object') {
      response.data.request_id = requestId || response.data.request_id || ''
      if (!response.data.process_time && typeof processTime === 'string' && processTime.trim()) {
        response.data.process_time = processTime
      }
    }

    return response
  },
  (error) => {
    // Extract tracing headers even on error if available
    const requestId = error.response?.headers?.['x-request-id'] || '';

    // Handle 401 — return unified error without side effects.
    // Token clearing and login redirect are handled by the auth store / login
    // flow, NOT here. Aggressive clearing here destroys valid sessions when
    // the 401 came from a transient backend issue (e.g. SQL bug returning 500
    // that the request layer mistook as auth failure, or cold-start race).
    if (error.response?.status === 401) {
      const unifiedError: UnifiedResponse<null> = {
        success: false,
        code: 401,
        message: error.response?.data?.message || '未授权或登录已过期',
        data: null,
        timestamp: new Date().toISOString(),
        request_id: requestId,
        errors: error.response?.data || null,
      };

      return Promise.resolve({
        data: unifiedError,
        status: 401,
        statusText: 'Unauthorized',
        headers: error.response?.headers || {},
        config: error.config || ({ headers: {} } as InternalAxiosRequestConfig),
      } as AxiosResponse<UnifiedResponse<null>>);
    }

    // Transform error to UnifiedResponse format
    const unifiedError: UnifiedResponse<null> = {
      success: false,
      code: error.response?.status || 500,
      message: error.response?.data?.message || error.message || 'Request failed',
      data: null,
      timestamp: new Date().toISOString(),
      request_id: requestId,
      errors: error.response?.data || null,
    };

    // Return unified error format instead of throwing
    // This allows adapters to implement fallback logic
    return Promise.resolve({
      data: unifiedError,
      status: error.response?.status || 500,
      statusText: error.response?.statusText || 'Error',
      headers: error.response?.headers || {},
      config: error.config || ({ headers: {} } as InternalAxiosRequestConfig),
    } as AxiosResponse<UnifiedResponse<null>>);
  }
);

// JWT token management
function getJWTToken(): string | null {
  return localStorage.getItem('auth_token');
}

const getCSRFToken = createCSRFTokenResolver(async () => {
  try {
    const response = await axios.get('/csrf-token', {
      withCredentials: true,
    });

    if (response.data?.data?.csrf_token) {
      return response.data.data.csrf_token || '';
    }
  } catch (error) {
    console.error('[apiClient] Failed to fetch CSRF token:', error);
  }

  return '';
})

import { mockApiClient } from './mockApiClient.ts';

// Export API methods
export const apiClient = {
  get<T = UnifiedResponse>(url: string, config?: RequestConfig): Promise<T> {
    if (import.meta.env.VITE_USE_MOCK_DATA) {
      return mockApiClient.get<T>(url, config);
    }
    return instance.get<T>(url, config).then((response) => response.data);
  },

  post<T = UnifiedResponse>(url: string, data?: unknown, config?: RequestConfig): Promise<T> {
    if (import.meta.env.VITE_USE_MOCK_DATA) {
      return mockApiClient.post<T>(url, data, config);
    }
    return instance.post<T>(url, data, config).then((response) => response.data);
  },

  put<T = UnifiedResponse>(url: string, data?: unknown, config?: RequestConfig): Promise<T> {
    if (import.meta.env.VITE_USE_MOCK_DATA) {
      return mockApiClient.put<T>(url, data, config);
    }
    return instance.put<T>(url, data, config).then((response) => response.data);
  },

  patch<T = UnifiedResponse>(url: string, data?: unknown, config?: RequestConfig): Promise<T> {
    if (import.meta.env.VITE_USE_MOCK_DATA) {
      return mockApiClient.patch<T>(url, data, config);
    }
    return instance.patch<T>(url, data, config).then((response) => response.data);
  },

  delete<T = UnifiedResponse>(url: string, config?: RequestConfig): Promise<T> {
    if (import.meta.env.VITE_USE_MOCK_DATA) {
      return mockApiClient.delete<T>(url, config);
    }
    return instance.delete<T>(url, config).then((response) => response.data);
  },
};

// Convenience wrappers
export const apiGet = <T = UnifiedResponse>(url: string, params?: unknown, config?: RequestConfig): Promise<T> => {
  return apiClient.get<T>(url, { ...config, params });
};

export const apiPost = <T = UnifiedResponse>(url: string, data?: unknown, config?: RequestConfig): Promise<T> => {
  return apiClient.post<T>(url, data, config);
};

export const apiPut = <T = UnifiedResponse>(url: string, data?: unknown, config?: RequestConfig): Promise<T> => {
  return apiClient.put<T>(url, data, config);
};

export const apiDelete = <T = UnifiedResponse>(url: string, config?: RequestConfig): Promise<T> => {
  return apiClient.delete<T>(url, config);
};

export default instance;
