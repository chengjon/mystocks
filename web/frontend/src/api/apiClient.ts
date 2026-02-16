/**
 * API Client for Strategy Module
 *
 * Lightweight HTTP client that returns full UnifiedResponse objects
 * for fallback strategy implementation.
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { UnifiedResponse } from './types/common';

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

// Response interceptor - returns full UnifiedResponse
instance.interceptors.response.use(
  (response: AxiosResponse<UnifiedResponse<any>>): any => {
    // Extract tracing headers
    const requestId = response.headers['x-request-id'] || ''
    const processTime = response.headers['x-process-time'] || ''

    // Merge tracing into data if it's a UnifiedResponse
    if (response.data && typeof response.data === 'object') {
      response.data.request_id = requestId || response.data.request_id || ''
      // We can also attach process time to the object if needed for monitoring
      if (processTime) {
        (response.data as any).process_time = processTime
      }
    }

    return response.data
  },
  (error) => {
    // Extract tracing headers even on error if available
    const requestId = error.response?.headers?.['x-request-id'] || '';
    
    // Handle JWT token expiration
    if (error.response?.status === 401) {
      // Clear expired token
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');

      // Redirect to login if not already there
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }

      const unifiedError: UnifiedResponse<null> = {
        success: false,
        code: 401,
        message: '登录已过期，请重新登录',
        data: null,
        timestamp: new Date().toISOString(),
        request_id: requestId,
        errors: null,
      };

      return Promise.resolve(unifiedError);
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
    return Promise.resolve(unifiedError);
  }
);

// JWT token management
function getJWTToken(): string | null {
  return localStorage.getItem('auth_token');
}

// CSRF token management
let csrfTokenCache: string | null = null;

async function getCSRFToken(): Promise<string> {
  if (csrfTokenCache) {
    return csrfTokenCache;
  }

  try {
    const response = await axios.get('/api/csrf-token', {
      withCredentials: true,
    });

    if (response.data?.data?.csrf_token) {
      csrfTokenCache = response.data.data.csrf_token;
      return csrfTokenCache || '';
    }
  } catch (error) {
    console.error('[apiClient] Failed to fetch CSRF token:', error);
  }

  return '';
}

import { mockApiClient } from './mockApiClient';

// Export API methods
export const apiClient = {
  get<T = UnifiedResponse>(url: string, config?: RequestConfig): Promise<T> {
    if (import.meta.env.VITE_USE_MOCK_DATA) {
      return mockApiClient.get<T>(url, config);
    }
    return instance.get(url, config);
  },

  post<T = UnifiedResponse>(url: string, data?: unknown, config?: RequestConfig): Promise<T> {
    if (import.meta.env.VITE_USE_MOCK_DATA) {
      return mockApiClient.post<T>(url, data, config);
    }
    return instance.post(url, data, config);
  },

  put<T = UnifiedResponse>(url: string, data?: unknown, config?: RequestConfig): Promise<T> {
    if (import.meta.env.VITE_USE_MOCK_DATA) {
      return mockApiClient.put<T>(url, data, config);
    }
    return instance.put(url, data, config);
  },

  patch<T = UnifiedResponse>(url: string, data?: unknown, config?: RequestConfig): Promise<T> {
    if (import.meta.env.VITE_USE_MOCK_DATA) {
      return mockApiClient.patch<T>(url, data, config);
    }
    return instance.patch(url, data, config);
  },

  delete<T = UnifiedResponse>(url: string, config?: RequestConfig): Promise<T> {
    if (import.meta.env.VITE_USE_MOCK_DATA) {
      return mockApiClient.delete<T>(url, config);
    }
    return instance.delete(url, config);
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
