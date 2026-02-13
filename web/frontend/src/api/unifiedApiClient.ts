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
import { LRUCache } from '@/utils/cache'
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

// 契约验证错误类
export class ContractValidationError extends Error {
    constructor(
        message: string,
        public contractName: string,
        public endpoint: string,
        public expectedSchema?: any,
        public actualData?: any
    ) {
        super(message)
        this.name = 'ContractValidationError'
    }
}

// 运行时契约验证器
class RuntimeContractValidator {
    private contractCache = new Map<string, any>()
    private validationEnabled: boolean

    constructor() {
        // 从环境变量或配置中读取验证启用状态
        this.validationEnabled = import.meta.env.VITE_CONTRACT_VALIDATION_ENABLED === 'true' ||
                                import.meta.env.DEV // 开发环境默认启用
    }

    async validateResponse(endpoint: string, method: string, response: any): Promise<void> {
        if (!this.validationEnabled) {
            return
        }

        try {
            const contractSchema = await this.fetchContractSchema(endpoint, method)

            if (!contractSchema) {
                console.warn(`No contract schema found for ${method} ${endpoint}`)
                return
            }

            // 使用Zod验证响应
            const result = contractSchema.safeParse(response.data || response)

            if (!result.success) {
                throw new ContractValidationError(
                    `Contract validation failed for ${method} ${endpoint}: ${result.error.message}`,
                    this.getContractName(endpoint),
                    endpoint,
                    contractSchema,
                    response.data || response
                )
            }

            console.debug(`Contract validation passed for ${method} ${endpoint}`)
        } catch (error) {
            if (error instanceof ContractValidationError) {
                throw error
            }
            // 如果契约获取或验证过程出错，在开发环境抛出，在生产环境记录警告
            if (import.meta.env.DEV) {
                throw new ContractValidationError(
                    `Contract validation error: ${error instanceof Error ? error.message : String(error)}`,
                    this.getContractName(endpoint),
                    endpoint
                )
            } else {
                console.warn(`Contract validation skipped due to error:`, error)
            }
        }
    }

    private async fetchContractSchema(endpoint: string, method: string): Promise<any | null> {
        const contractName = this.getContractName(endpoint)

        // 检查缓存
        if (this.contractCache.has(contractName)) {
            return this.contractCache.get(contractName)
        }

        try {
            // 从后端API获取契约
            const response: any = await request({
                method: 'get',
                url: `/api/contracts/${contractName}/active`
            })

            if (response?.success && response.data?.spec) {
                const openApiSpec = response.data.spec

                // 转换为Zod schema (简化实现)
                const zodSchema = this.convertOpenAPIToZod(openApiSpec, endpoint, method)

                // 缓存结果
                this.contractCache.set(contractName, zodSchema)
                return zodSchema
            }
        } catch (error) {
            console.warn(`Failed to fetch contract for ${contractName}:`, error)
        }

        return null
    }

    private convertOpenAPIToZod(openApiSpec: any, endpoint: string, method: string): any {
        const { z } = require('zod')

        // 查找对应的操作
        const paths = openApiSpec.paths || {}
        const pathItem = paths[endpoint]

        if (!pathItem) {
            console.warn(`Path ${endpoint} not found in OpenAPI spec`)
            return z.any() // 返回宽松的schema
        }

        const operation = pathItem[method.toLowerCase()]
        if (!operation) {
            console.warn(`Method ${method} not found for path ${endpoint}`)
            return z.any()
        }

        // 获取响应的schema
        const responses = operation.responses || {}
        const successResponse = responses['200'] || responses['201'] || Object.values(responses)[0]

        if (!successResponse) {
            return z.any()
        }

        // 解析response schema
        const schema = successResponse.content?.['application/json']?.schema
        if (!schema) {
            return z.any()
        }

        return this.convertJsonSchemaToZod(schema)
    }

    private convertJsonSchemaToZod(schema: any): any {
        const { z } = require('zod')

        if (!schema) {
            return z.any()
        }

        switch (schema.type) {
            case 'string':
                let stringSchema = z.string()
                if (schema.format === 'date-time') {
                    stringSchema = stringSchema.datetime()
                } else if (schema.format === 'email') {
                    stringSchema = stringSchema.email()
                } else if (schema.format === 'uuid') {
                    stringSchema = stringSchema.uuid()
                }
                return schema.required === false ? stringSchema.optional() : stringSchema

            case 'number':
            case 'integer':
                let numberSchema = schema.type === 'integer' ? z.number().int() : z.number()
                if (typeof schema.minimum === 'number') {
                    numberSchema = numberSchema.min(schema.minimum)
                }
                if (typeof schema.maximum === 'number') {
                    numberSchema = numberSchema.max(schema.maximum)
                }
                return schema.required === false ? numberSchema.optional() : numberSchema

            case 'boolean':
                return schema.required === false ? z.boolean().optional() : z.boolean()

            case 'array':
                const itemSchema = this.convertJsonSchemaToZod(schema.items)
                return schema.required === false ?
                    z.array(itemSchema).optional() :
                    z.array(itemSchema)

            case 'object':
                if (schema.properties) {
                    const shape: any = {}
                    for (const [key, propSchema] of Object.entries(schema.properties)) {
                        shape[key] = this.convertJsonSchemaToZod(propSchema)
                    }
                    const objectSchema = z.object(shape)

                    // 处理必需字段
                    if (schema.required && Array.isArray(schema.required)) {
                        // Zod会自动处理required字段，无需额外处理
                    }

                    return schema.required === false ? objectSchema.optional() : objectSchema
                }
                return z.record(z.any())

            default:
                return z.any()
        }
    }

    private getContractName(endpoint: string): string {
        // 根据endpoint路径推断契约名称
        // 例如: /api/market/symbols -> market-api
        const pathParts = endpoint.split('/')
        if (pathParts.length >= 3 && pathParts[1] === 'api') {
            return `${pathParts[2]}-api`
        }
        return 'default-api'
    }

    setValidationEnabled(enabled: boolean): void {
        this.validationEnabled = enabled
    }

    clearCache(): void {
        this.contractCache.clear()
    }
}

// 全局契约验证器实例
export const contractValidator = new RuntimeContractValidator()

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

    static getUserFriendlyMessage(error: ApiError | ContractValidationError): string {
        // 处理契约验证错误
        if (error instanceof ContractValidationError) {
            if (import.meta.env.DEV) {
                // 开发环境显示详细错误信息
                return `API响应格式不匹配：${error.message}`
            } else {
                // 生产环境显示用户友好的信息
                return '数据格式异常，请联系技术支持'
            }
        }

        // 处理普通API错误
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
    private loadingStore: ReturnType<typeof useLoadingStore> | null = null
    private cache: LRUCache

    constructor(baseURL = '') {
        this.baseURL = baseURL
        // Don't initialize store in constructor to avoid "no active Pinia" error
        this.cache = new LRUCache({
            maxSize: 100,
            ttl: 5 * 60 * 1000 // 5 minutes
        })
    }

    private getStore() {
        if (!this.loadingStore) {
            this.loadingStore = useLoadingStore()
        }
        return this.loadingStore
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

                // 添加契约验证拦截器
                await contractValidator.validateResponse(url, method, response)

                return response
            } catch (error) {
                // 如果是契约验证错误，直接抛出
                if (error instanceof ContractValidationError) {
                    throw error
                }
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
            this.getStore().setLoading(config.loading.key, true)
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
                this.getStore().setLoading(config.loading.key, false)
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

// 导出工具函数
export const isLoading = (key: string): boolean => {
    try {
        return useLoadingStore().isLoading(key)
    } catch (e) {
        return false
    }
}
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
