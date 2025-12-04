/**
 * HTTP Client with CSRF Protection
 *
 * This client automatically handles:
 * 1. CSRF token retrieval from backend
 * 2. CSRF token injection into request headers
 * 3. CSRF token storage in meta tag
 * 4. Request/response interceptors for security
 */

import { API_BASE_URL } from '../config/api.js'

class HttpClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL
    this.csrfToken = null
    // 更新至v1标准版本端点
    this.csrfTokenEndpoint = `${baseURL}/api/v1/auth/csrf/token`
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  }

  /**
   * 从后端获取CSRF Token
   * SECURITY: 初始化时调用，获取一次性的CSRF token
   */
  async initializeCsrfToken() {
    try {
      const response = await fetch(this.csrfTokenEndpoint, {
        method: 'GET',
        credentials: 'include', // 包含cookies
        headers: this.defaultHeaders
      })

      if (response.ok) {
        const data = await response.json()

        // 处理两种响应格式
        // 新的v1格式: { code, message, data: { token, ... } }
        // 旧格式: { csrf_token, ... }
        if (data.data && data.data.token) {
          this.csrfToken = data.data.token
        } else if (data.csrf_token) {
          this.csrfToken = data.csrf_token
        } else {
          console.warn('⚠️ Unexpected CSRF token response format:', data)
          return null
        }

        // 将CSRF token存储到meta标签中，供其他模块使用
        const csrfMetaTag = document.querySelector('meta[name="csrf-token"]')
        if (csrfMetaTag) {
          csrfMetaTag.setAttribute('content', this.csrfToken)
        }

        console.log('✅ CSRF Token initialized successfully')
        return this.csrfToken
      } else {
        console.warn('⚠️ Failed to retrieve CSRF token')
        return null
      }
    } catch (error) {
      console.error('❌ Error initializing CSRF token:', error)
      return null
    }
  }

  /**
   * 获取CSRF Token（从内存或meta标签）
   */
  getCsrfToken() {
    // 首先尝试从内存中获取
    if (this.csrfToken) {
      return this.csrfToken
    }

    // 否则从meta标签中获取
    const csrfMetaTag = document.querySelector('meta[name="csrf-token"]')
    if (csrfMetaTag && csrfMetaTag.getAttribute('content')) {
      this.csrfToken = csrfMetaTag.getAttribute('content')
      return this.csrfToken
    }

    return null
  }

  /**
   * 为请求添加CSRF Token
   * SECURITY: 所有修改操作(POST, PUT, PATCH, DELETE)都需要CSRF token
   */
  getRequestHeaders(method) {
    const headers = { ...this.defaultHeaders }

    // 对于需要CSRF保护的请求方法，添加CSRF Token
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method.toUpperCase())) {
      const csrfToken = this.getCsrfToken()
      if (csrfToken) {
        headers['X-CSRF-Token'] = csrfToken
      } else {
        console.warn('⚠️ CSRF token not available for', method, 'request')
      }
    }

    return headers
  }

  /**
   * 构建完整URL
   */
  buildUrl(path) {
    if (path.startsWith('http')) {
      return path
    }
    return `${this.baseURL}${path.startsWith('/') ? '' : '/'}${path}`
  }

  /**
   * 统一的请求处理
   * SECURITY: 处理请求验证、响应处理和错误处理
   */
  async request(path, options = {}) {
    const url = this.buildUrl(path)
    const method = (options.method || 'GET').toUpperCase()
    const headers = this.getRequestHeaders(method)

    const config = {
      method,
      headers: { ...headers, ...options.headers },
      credentials: 'include', // SECURITY: 包含cookies用于会话管理
      ...options
    }

    try {
      const response = await fetch(url, config)

      // 处理响应
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      // 尝试解析JSON
      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        return await response.json()
      }

      return response
    } catch (error) {
      console.error(`❌ Request failed [${method} ${url}]:`, error)
      throw error
    }
  }

  /**
   * GET 请求
   */
  get(path, options = {}) {
    return this.request(path, { ...options, method: 'GET' })
  }

  /**
   * POST 请求 (CSRF保护)
   * SECURITY: 自动注入CSRF token
   */
  post(path, data = {}, options = {}) {
    return this.request(path, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  /**
   * PUT 请求 (CSRF保护)
   * SECURITY: 自动注入CSRF token
   */
  put(path, data = {}, options = {}) {
    return this.request(path, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  /**
   * PATCH 请求 (CSRF保护)
   * SECURITY: 自动注入CSRF token
   */
  patch(path, data = {}, options = {}) {
    return this.request(path, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(data)
    })
  }

  /**
   * DELETE 请求 (CSRF保护)
   * SECURITY: 自动注入CSRF token
   */
  delete(path, options = {}) {
    return this.request(path, {
      ...options,
      method: 'DELETE'
    })
  }
}

// 创建全局HTTP客户端实例
export const httpClient = new HttpClient()

/**
 * 应用启动时初始化CSRF token
 * 这应该在Vue应用mount前调用
 */
export async function initializeSecurity() {
  await httpClient.initializeCsrfToken()
}

export default httpClient
