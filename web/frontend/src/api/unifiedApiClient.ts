/**
 * 统一API客户端 - 标准化数据获取模式
 *
 * 特性:
 * - 统一的缓存策略
 * - 标准化的错误处理
 * - 加载状态管理
 * - 自动重试机制
 * - TypeScript 类型安全
 */

import request from './index.js'
import LRUCache from '@/utils/cache'
import { useLoadingStore } from '@/stores/loading'

// 缓存策略配置
export const CACHE_STRATEGIES = {
    // 实时数据 - 短缓存，高频更新
    realtime: { ttl: 30000, strategy: 'memory' }, // 30秒

    // 频繁查询数据 - 中等缓存
    frequent: { ttl: 300000, strategy: 'memory' }, // 5分钟

    // 静态参考数据 - 长缓存
    reference: { ttl: 3600000, strategy: 'localStorage' }, // 1小时

    // 历史数据 - 超长缓存
    historical: { ttl: 86400000, strategy: 'localStorage' }, // 24小时

    // 用户数据 - 会话缓存
    user: { ttl: 1800000, strategy: 'sessionStorage' }, // 30分钟

    // 临时数据 - 无缓存
    temporary: { ttl: 0, strategy: 'memory' }
} as const

// 类型定义
export interface CacheConfig {
    enabled: boolean
    key: string
    ttl: number
    strategy: 'memory' | 'localStorage' | 'sessionStorage'
}

export interface RetryConfig {
    enabled: boolean
    maxAttempts: number
    delay: number
    backoffFactor: number
}

export interface LoadingConfig {
    enabled: boolean
    key: string
}

export interface ApiConfig {
    cache?: CacheConfig
    retry?: RetryConfig
    loading?: LoadingConfig
    timeout?: number
}

// 错误处理类
export class ApiError extends Error {
    constructor(
        message: string,
        public statusCode?: number,
        public originalError?: any
    ) {
        super(message)
        this.name = 'ApiError'
    }
}

// 重试处理器
class RetryHandler {
    static async withRetry<T>(operation: () => Promise<T>, config: RetryConfig): Promise<T> {
        let lastError: any

        for (let attempt = 1; attempt <= config.maxAttempts; attempt++) {
            try {
                return await operation()
            } catch (error) {
                lastError = error

                // 如果是最后一次尝试，抛出错误
                if (attempt === config.maxAttempts) {
                    break
                }

                // 检查是否应该重试
                if (this.shouldRetry(error)) {
                    const delay = config.delay * Math.pow(config.backoffFactor, attempt - 1)
                    await this.delay(delay)
                    continue
                }

                // 不应该重试，直接抛出错误
                break
            }
        }

        throw lastError
    }

    private static shouldRetry(error: any): boolean {
        // 网络错误应该重试
        if (!error.response) {
            return true
        }

        // 服务器错误应该重试
        const statusCode = error.response.status
        return statusCode >= 500
    }

    private static delay(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms))
    }
}

// 错误处理器
class ApiErrorHandler {
    static handle(error: any, context: string): never {
        console.error(`API Error in ${context}:`, error)

        // 网络错误
        if (!error.response) {
            throw new ApiError('网络连接失败，请检查网络连接', undefined, error)
        }

        const statusCode = error.response.status
        const message = error.response.data?.detail || error.response.data?.message || error.message

        switch (statusCode) {
            case 400:
                throw new ApiError(`请求参数错误: ${message}`, 400, error)
            case 401:
                throw new ApiError('登录已过期，请重新登录', 401, error)
            case 403:
                throw new ApiError('权限不足', 403, error)
            case 404:
                throw new ApiError('请求的资源不存在', 404, error)
            case 429:
                throw new ApiError('请求过于频繁，请稍后再试', 429, error)
            case 500:
                throw new ApiError('服务器内部错误', 500, error)
            case 502:
            case 503:
            case 504:
                throw new ApiError('服务器暂时不可用，请稍后再试', statusCode, error)
            default:
                throw new ApiError(`请求失败: ${message}`, statusCode, error)
        }
    }

    static getUserFriendlyMessage(error: ApiError): string {
        const statusCode = error.statusCode
        if (statusCode === 401) {
            return '您的登录已过期，请重新登录'
        }
        if (statusCode === 403) {
            return '您没有权限执行此操作'
        }
        if (statusCode === 404) {
            return '请求的资源不存在'
        }
        if (statusCode && statusCode >= 500) {
            return '服务器暂时出现问题，请稍后再试'
        }
        return error.message || '操作失败，请重试'
    }
}

// 使用全局loading store进行加载状态管理

// 主API客户端类
export class UnifiedApiClient {
    private baseURL: string
    private loadingStore: ReturnType<typeof useLoadingStore>
    private cache: LRUCache

    constructor(baseURL = '/api') {
        this.baseURL = baseURL
        this.loadingStore = useLoadingStore()
        this.cache = new LRUCache({
            maxSize: 100,
            ttl: 5 * 60 * 1000 // 5 minutes
        })
    }

    // 统一的API调用方法
    async call<T = any>(config: {
        method: 'GET' | 'POST' | 'PUT' | 'DELETE'
        url: string
        params?: any
        data?: any
        config?: ApiConfig
    }): Promise<T> {
        const { method, url, params, data, config: apiConfig = {} } = config
        const fullUrl = url.startsWith('http') ? url : `${this.baseURL}${url}`

        // 准备请求配置
        const requestConfig = {
            method: method.toLowerCase(),
            url: fullUrl,
            params,
            data,
            timeout: apiConfig.timeout
        }

        // 执行请求的函数
        const executeRequest = async (): Promise<T> => {
            try {
                const response = (await request(requestConfig)) as T
                return response
            } catch (error) {
                ApiErrorHandler.handle(error, `${method} ${url}`)
            }
        }

        // 处理缓存
        if (apiConfig.cache?.enabled && method === 'GET') {
            const cacheKey = apiConfig.cache.key
            const cached = this.cache.get(cacheKey)

            if (cached !== null) {
                return cached
            }

            // 执行请求并缓存结果
            const result = await this.executeWithLoadingAndRetry(executeRequest, apiConfig)
            this.cache.set(cacheKey, result, { ttl: apiConfig.cache.ttl })
            return result
        }

        // 执行请求（无缓存）
        return this.executeWithLoadingAndRetry(executeRequest, apiConfig)
    }

    private async executeWithLoadingAndRetry<T>(operation: () => Promise<T>, config: ApiConfig): Promise<T> {
        // 设置加载状态
        if (config.loading?.enabled) {
            this.loadingStore.setLoading(config.loading.key, true)
        }

        try {
            // 处理重试
            if (config.retry?.enabled) {
                return await RetryHandler.withRetry(operation, config.retry)
            } else {
                return await operation()
            }
        } finally {
            // 清除加载状态
            if (config.loading?.enabled) {
                this.loadingStore.setLoading(config.loading.key, false)
            }
        }
    }

    // 便捷方法
    async get<T = any>(url: string, config?: ApiConfig): Promise<T> {
        return this.call({ method: 'GET', url, config })
    }

    async post<T = any>(url: string, data?: any, config?: ApiConfig): Promise<T> {
        return this.call({ method: 'POST', url, data, config })
    }

    async put<T = any>(url: string, data?: any, config?: ApiConfig): Promise<T> {
        return this.call({ method: 'PUT', url, data, config })
    }

    async delete<T = any>(url: string, config?: ApiConfig): Promise<T> {
        return this.call({ method: 'DELETE', url, config })
    }
}

// 创建全局API客户端实例
export const unifiedApiClient = new UnifiedApiClient()

// 创建全局API客户端实例
const globalLoadingStore = useLoadingStore()

// 导出工具函数
export const isLoading = (key: string): boolean => globalLoadingStore.isLoading(key)
export const getUserFriendlyErrorMessage = (error: any): string => {
    if (error instanceof ApiError) {
        return ApiErrorHandler.getUserFriendlyMessage(error)
    }
    return '操作失败，请重试'
}

// 默认重试配置
export const DEFAULT_RETRY_CONFIG: RetryConfig = {
    enabled: true,
    maxAttempts: 3,
    delay: 1000,
    backoffFactor: 2
}

// 默认缓存配置生成器
export const createCacheConfig = (key: string, strategy: keyof typeof CACHE_STRATEGIES): CacheConfig => ({
    enabled: true,
    key,
    ...CACHE_STRATEGIES[strategy]
})

// 默认加载配置生成器
export const createLoadingConfig = (key: string): LoadingConfig => ({
    enabled: true,
    key
})

export default unifiedApiClient
