/**
 * Unified HTTP Client with Axios
 *
 * Provides centralized API communication with:
 * - Automatic CSRF token management
 * - Unified response handling
 * - Error handling with user-friendly messages
 * - Request/response interceptors
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { ElMessage, ElNotification } from 'element-plus'
import type { APIResponse } from '@/api/types/generated-types'

// Type definitions
export interface RequestConfig extends AxiosRequestConfig {
  skipErrorHandler?: boolean
  skipCSRF?: boolean
}

export interface ErrorResponse {
  success: false
  code: number
  message: string
  details?: any
  request_id: string
  timestamp: string
}

// Create Axios instance
const instance: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true // Enable cookies for session management
})

// Request interceptor for CSRF token
instance.interceptors.request.use(
  async (config: RequestConfig) => {
    // Skip CSRF for GET requests and explicitly marked requests
    if (
      config.method?.toUpperCase() !== 'GET' &&
      !config.skipCSRF &&
      config.headers?.['X-CSRF-Token'] === undefined
    ) {
      try {
        const token = await getCSRFToken()
        config.headers = config.headers || {}
        config.headers['X-CSRF-Token'] = token
      } catch (error) {
        console.error('Failed to get CSRF token:', error)
      }
    }

    // Add request timestamp
    config.headers['X-Request-Start'] = Date.now().toString()

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for unified handling
instance.interceptors.response.use(
  (response: AxiosResponse<APIResponse>) => {
    // Calculate request duration
    const duration = Date.now() - parseInt(response.config.headers?.['X-Request-Start'] || '0')

    // Log slow requests
    if (duration > 3000) {
      console.warn(`Slow API request: ${response.config.url} took ${duration}ms`)
    }

    // Handle unified response format
    if (response.data && typeof response.data === 'object') {
      if ('success' in response.data) {
        if (response.data.success) {
          // Return only the data part for successful responses
          return response.data.data || null
        } else {
          // Throw error for API-level errors
          throw new Error(response.data.message || 'Request failed')
        }
      }
    }

    // Return response data for non-unified responses
    return response.data
  },
  (error: AxiosError<ErrorResponse>) => {
    const { response, config } = error

    // Skip error handling if explicitly requested
    if (config?.skipErrorHandler) {
      return Promise.reject(error)
    }

    // Handle different error scenarios
    if (response) {
      const status = response.status
      const errorData = response.data

      switch (status) {
        case 400:
          handleError(errorData?.message || '请求参数错误', 'warning')
          break
        case 401:
          handleError('登录已过期，请重新登录', 'error')
          // Redirect to login page
          setTimeout(() => {
            window.location.href = '/login'
          }, 1500)
          break
        case 403:
          handleError('权限不足，无法访问此资源', 'error')
          break
        case 404:
          handleError('请求的资源不存在', 'warning')
          break
        case 422:
          // Validation error
          if (errorData?.details) {
            const details = errorData.details
            const fieldErrors = Object.entries(details)
              .map(([field, msg]) => `${field}: ${msg}`)
              .join(', ')
            handleError(`输入验证失败: ${fieldErrors}`, 'warning')
          } else {
            handleError(errorData?.message || '输入数据验证失败', 'warning')
          }
          break
        case 429:
          handleError('请求过于频繁，请稍后再试', 'warning')
          break
        case 500:
        case 502:
        case 503:
        case 504:
          handleError('服务器暂时无法处理请求，请稍后再试', 'error')
          break
        default:
          handleError(
            errorData?.message || `请求失败 (${status})`,
            'error'
          )
      }
    } else if (error.code === 'ECONNABORTED') {
      handleError('请求超时，请检查网络连接', 'error')
    } else if (error.message === 'Network Error') {
      handleError('网络连接失败，请检查网络设置', 'error')
    } else {
      handleError(error.message || '未知错误', 'error')
    }

    // Always reject the promise
    return Promise.reject(error)
  }
)

// CSRF token management
let csrfTokenCache: string | null = null
let csrfTokenPromise: Promise<string> | null = null

async function getCSRFToken(): Promise<string> {
  // Return cached token if available
  if (csrfTokenCache) {
    return csrfTokenCache
  }

  // Return existing promise if request is in progress
  if (csrfTokenPromise) {
    return csrfTokenPromise
  }

  // Fetch new token
  csrfTokenPromise = fetchCSRFToken()
  csrfTokenCache = await csrfTokenPromise
  csrfTokenPromise = null

  // Set token expiration (1 hour)
  setTimeout(() => {
    csrfTokenCache = null
  }, 3600000)

  return csrfTokenCache
}

async function fetchCSRFToken(): Promise<string> {
  try {
    const response = await axios.get('/api/auth/csrf', {
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      withCredentials: true
    })

    if (response.data?.token) {
      return response.data.token
    } else {
      throw new Error('Invalid CSRF token response')
    }
  } catch (error) {
    console.error('Failed to fetch CSRF token:', error)
    // Return empty string to allow request to proceed
    // but without CSRF token (for development)
    return ''
  }
}

// Error handling helper
function handleError(message: string, type: 'success' | 'warning' | 'error' | 'info' = 'error'): void {
  if (type === 'error') {
    ElNotification({
      title: '错误',
      message,
      type,
      duration: 5000
    })
  } else {
    ElMessage({
      message,
      type,
      duration: 3000
    })
  }
}

// Export common request methods
export const request = {
  get<T = any>(url: string, config?: RequestConfig): Promise<T> {
    return instance.get(url, config)
  },

  post<T = any>(url: string, data?: any, config?: RequestConfig): Promise<T> {
    return instance.post(url, data, config)
  },

  put<T = any>(url: string, data?: any, config?: RequestConfig): Promise<T> {
    return instance.put(url, data, config)
  },

  patch<T = any>(url: string, data?: any, config?: RequestConfig): Promise<T> {
    return instance.patch(url, data, config)
  },

  delete<T = any>(url: string, config?: RequestConfig): Promise<T> {
    return instance.delete(url, config)
  }
}

// Export Axios instance for advanced usage
export default instance

// Export utilities
export { getCSRFToken }
export type { RequestConfig, ErrorResponse }