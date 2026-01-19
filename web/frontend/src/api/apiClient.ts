// @ts-nocheck
/**
 * API Client for Strategy Module
 *
 * Lightweight HTTP client that returns full UnifiedResponse objects
 * for fallback strategy implementation.
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios';

// UnifiedResponse v2.0.0 format
export interface UnifiedResponse<T = any> {
  success: boolean;
  code: number;
  message: string;
  data: T;
  timestamp: string;
  request_id: string;
  errors: any;
}

// Request configuration
interface RequestConfig extends AxiosRequestConfig {
  skipErrorHandler?: boolean;
  skipCSRF?: boolean;
}

// Internal request config for interceptors
interface InternalRequestConfig extends InternalAxiosRequestConfig {
  skipErrorHandler?: boolean;
  skipCSRF?: boolean;
}

// Create axios instance
const instance: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
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
      if (!config.headers) {
        config.headers = {} as any;
      }
      (config.headers as any)['Authorization'] = `Bearer ${jwtToken}`;
    }

    // Add CSRF token for POST/PUT/PATCH/DELETE
    if (
      config.method?.toUpperCase() !== 'GET' &&
      !(config as RequestConfig).skipCSRF &&
      !config.headers?.['X-CSRF-Token']
    ) {
      try {
        const token = await getCSRFToken();
        if (!config.headers) {
          config.headers = {} as any;
        }
        (config.headers as any)['X-CSRF-Token'] = token;
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
  (response: AxiosResponse<UnifiedResponse>): any => {
    // Return full response for fallback handling
    return response.data;
  },
  (error) => {
    // Handle JWT token expiration
    if (error.response?.status === 401) {
      // Clear expired token
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');

      // Redirect to login if not already there
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }

      const unifiedError: UnifiedResponse = {
        success: false,
        code: 401,
        message: '登录已过期，请重新登录',
        data: null,
        timestamp: new Date().toISOString(),
        request_id: '',
        errors: null,
      };

      return Promise.resolve(unifiedError);
    }

    // Transform error to UnifiedResponse format
    const unifiedError: UnifiedResponse = {
      success: false,
      code: error.response?.status || 500,
      message: error.response?.data?.message || error.message || 'Request failed',
      data: null,
      timestamp: new Date().toISOString(),
      request_id: '',
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
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      withCredentials: true,
    });

    if (response.data?.data?.csrf_token) {
      csrfTokenCache = response.data.data.csrf_token;
      return csrfTokenCache;
    }
  } catch (error) {
    console.error('[apiClient] Failed to fetch CSRF token:', error);
  }

  return '';
}

// Export API methods
export const apiClient = {
  get<T = UnifiedResponse>(url: string, config?: RequestConfig): Promise<T> {
    return instance.get(url, config);
  },

  post<T = UnifiedResponse>(url: string, data?: any, config?: RequestConfig): Promise<T> {
    return instance.post(url, data, config);
  },

  put<T = UnifiedResponse>(url: string, data?: any, config?: RequestConfig): Promise<T> {
    return instance.put(url, data, config);
  },

  patch<T = UnifiedResponse>(url: string, data?: any, config?: RequestConfig): Promise<T> {
    return instance.patch(url, data, config);
  },

  delete<T = UnifiedResponse>(url: string, config?: RequestConfig): Promise<T> {
    return instance.delete(url, config);
  },
};

// Convenience wrappers
export const apiGet = <T = UnifiedResponse>(url: string, params?: any, config?: RequestConfig): Promise<T> => {
  return apiClient.get<T>(url, { ...config, params });
};

export const apiPost = <T = UnifiedResponse>(url: string, data?: any, config?: RequestConfig): Promise<T> => {
  return apiClient.post<T>(url, data, config);
};

export const apiPut = <T = UnifiedResponse>(url: string, data?: any, config?: RequestConfig): Promise<T> => {
  return apiClient.put<T>(url, data, config);
};

export const apiDelete = <T = UnifiedResponse>(url: string, config?: RequestConfig): Promise<T> => {
  return apiClient.delete<T>(url, config);
};

export default instance;
