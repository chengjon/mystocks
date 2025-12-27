/**
 * Indicator API Service
 * 技术指标 API 客户端服务
 */

import axios, { AxiosInstance, AxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import type {
  IndicatorCalculateRequest,
  IndicatorCalculateResponse,
  IndicatorRegistryResponse,
  IndicatorMetadata,
  IndicatorConfigCreateRequest,
  IndicatorConfigUpdateRequest,
  IndicatorConfig,
  IndicatorConfigListResponse,
  IndicatorCategory
} from '@/types/indicator'

/**
 * API 基础配置
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_TIMEOUT = 30000 // 30 seconds

/**
 * 重试配置
 */
const MAX_RETRIES = 3
const RETRY_DELAY = 1000 // 初始重试延迟(ms)
const RETRY_BACKOFF = 2 // 指数退避因子

/**
 * 延迟函数
 */
const delay = (ms: number): Promise<void> => new Promise(resolve => setTimeout(resolve, ms))

/**
 * 错误类型枚举
 */
export enum ErrorType {
  NETWORK_ERROR = 'NETWORK_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  AUTH_ERROR = 'AUTH_ERROR',
  SERVER_ERROR = 'SERVER_ERROR',
  NOT_FOUND_ERROR = 'NOT_FOUND_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR'
}

/**
 * 错误信息接口
 */
export interface ErrorInfo {
  type: ErrorType
  message: string
  userMessage: string
  recoverySteps: string[]
  canRetry: boolean
  statusCode?: number
}

/**
 * 分类错误并生成详细错误信息
 */
export function classifyError(error: AxiosError): ErrorInfo {
  if (error.response) {
    const status = error.response.status
    const data = error.response.data as any

    // 优先使用服务器返回的错误消息
    const serverMessage = data?.error_message || data?.detail || ''

    if (status === 401) {
      return {
        type: ErrorType.AUTH_ERROR,
        message: serverMessage || 'Unauthorized',
        userMessage: '登录已过期,请重新登录',
        recoverySteps: ['点击"重新登录"按钮', '或刷新页面重新登录'],
        canRetry: false,
        statusCode: status
      }
    } else if (status === 404) {
      return {
        type: ErrorType.NOT_FOUND_ERROR,
        message: serverMessage || 'Resource not found',
        userMessage: '请求的资源不存在',
        recoverySteps: ['检查请求参数是否正确', '确认资源ID是否有效'],
        canRetry: false,
        statusCode: status
      }
    } else if (status === 422) {
      return {
        type: ErrorType.VALIDATION_ERROR,
        message: serverMessage || 'Validation failed',
        userMessage: '请求参数不符合要求',
        recoverySteps: [
          '检查输入参数格式',
          serverMessage ? `详细错误: ${serverMessage}` : '查看控制台获取更多信息'
        ],
        canRetry: true,
        statusCode: status
      }
    } else if (status >= 500 && status < 600) {
      return {
        type: ErrorType.SERVER_ERROR,
        message: serverMessage || 'Server error',
        userMessage: '服务器内部错误,请稍后重试',
        recoverySteps: [
          '等待几秒后自动重试',
          '如果问题持续,请联系技术支持',
          `错误代码: ${status}`
        ],
        canRetry: true,
        statusCode: status
      }
    }
  } else if (error.request) {
    // 网络错误
    return {
      type: ErrorType.NETWORK_ERROR,
      message: error.message || 'Network error',
      userMessage: '网络连接失败',
      recoverySteps: [
        '检查网络连接是否正常',
        '确认服务器地址是否正确',
        '尝试刷新页面'
      ],
      canRetry: true
    }
  }

  // 未知错误
  return {
    type: ErrorType.UNKNOWN_ERROR,
    message: error.message || 'Unknown error',
    userMessage: '发生未知错误,请稍后重试',
    recoverySteps: ['刷新页面重试', '如果问题持续,请联系技术支持'],
    canRetry: true
  }
}

/**
 * 带重试机制的请求包装器
 */
async function retryRequest<T>(
  requestFn: () => Promise<T>,
  context: string = 'API请求'
): Promise<T> {
  let lastError: Error | null = null

  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    try {
      return await requestFn()
    } catch (error) {
      lastError = error as Error

      // 分类错误
      const axiosError = error as AxiosError
      const errorInfo = classifyError(axiosError)

      // 如果不能重试,直接抛出
      if (!errorInfo.canRetry) {
        throw error
      }

      // 最后一次尝试失败,不再重试
      if (attempt === MAX_RETRIES) {
        break
      }

      // 计算退避延迟
      const waitTime = RETRY_DELAY * Math.pow(RETRY_BACKOFF, attempt)

      console.warn(
        `${context}失败 (尝试 ${attempt + 1}/${MAX_RETRIES + 1}), ` +
        `${waitTime}ms后重试...`,
        errorInfo.message
      )

      // 显示重试提示
      ElMessage.warning({
        message: `${context}失败,正在自动重试... (${attempt + 1}/${MAX_RETRIES})`,
        duration: 2000
      })

      await delay(waitTime)
    }
  }

  // 所有重试都失败
  throw lastError
}

/**
 * 创建 Axios 实例
 */
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: `${API_BASE_URL}/api`,
    timeout: API_TIMEOUT,
    headers: {
      'Content-Type': 'application/json'
    }
  })

  // 请求拦截器: 添加认证token
  client.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  // 响应拦截器: 统一错误处理
  client.interceptors.response.use(
    (response) => {
      return response
    },
    (error: AxiosError) => {
      if (error.response) {
        // 服务器响应错误
        const status = error.response.status
        const data = error.response.data as any

        if (status === 401) {
          // 未授权,清除token并跳转登录
          localStorage.removeItem('access_token')
          window.location.href = '/login'
        } else if (status === 422) {
          // 验证错误
          console.error('Validation Error:', data)
        } else if (status === 500) {
          // 服务器错误
          console.error('Server Error:', data)
        }
      } else if (error.request) {
        // 请求已发送但没有响应
        console.error('Network Error:', error.message)
      } else {
        // 请求配置错误
        console.error('Request Config Error:', error.message)
      }
      return Promise.reject(error)
    }
  )

  return client
}

const apiClient = createApiClient()

/**
 * Indicator Service 类
 */
export class IndicatorService {
  /**
   * 获取指标注册表 (带重试)
   * @returns 所有可用指标及其元数据
   */
  async getRegistry(): Promise<IndicatorRegistryResponse> {
    return await retryRequest(
      async () => {
        const response = await apiClient.get<IndicatorRegistryResponse>('/indicators/registry')
        return response.data
      },
      '获取指标列表'
    )
  }

  /**
   * 获取指定分类的指标 (带重试)
   * @param category 指标分类
   * @returns 该分类下的所有指标
   */
  async getIndicatorsByCategory(category: IndicatorCategory): Promise<IndicatorMetadata[]> {
    return await retryRequest(
      async () => {
        const response = await apiClient.get<IndicatorMetadata[]>(`/indicators/registry/${category}`)
        return response.data
      },
      '获取分类指标'
    )
  }

  /**
   * 计算技术指标 (带重试)
   * @param request 指标计算请求
   * @returns 指标计算结果
   */
  async calculateIndicators(request: IndicatorCalculateRequest): Promise<IndicatorCalculateResponse> {
    return await retryRequest(
      async () => {
        const response = await apiClient.post<IndicatorCalculateResponse>(
          '/indicators/calculate',
          request
        )
        return response.data
      },
      '计算技术指标'
    )
  }

  /**
   * 创建指标配置 (带重试)
   * @param request 配置创建请求
   * @returns 创建的配置
   */
  async createConfig(request: IndicatorConfigCreateRequest): Promise<IndicatorConfig> {
    return await retryRequest(
      async () => {
        const response = await apiClient.post<IndicatorConfig>('/indicators/configs', request)
        return response.data
      },
      '创建指标配置'
    )
  }

  /**
   * 获取用户的所有指标配置 (带重试)
   * @returns 配置列表
   */
  async listConfigs(): Promise<IndicatorConfigListResponse> {
    return await retryRequest(
      async () => {
        const response = await apiClient.get<IndicatorConfigListResponse>('/indicators/configs')
        return response.data
      },
      '获取配置列表'
    )
  }

  /**
   * 获取指定ID的配置 (带重试)
   * @param configId 配置ID
   * @returns 配置详情
   */
  async getConfig(configId: number): Promise<IndicatorConfig> {
    return await retryRequest(
      async () => {
        const response = await apiClient.get<IndicatorConfig>(`/indicators/configs/${configId}`)
        return response.data
      },
      '获取配置详情'
    )
  }

  /**
   * 更新指标配置 (带重试)
   * @param configId 配置ID
   * @param request 更新请求
   * @returns 更新后的配置
   */
  async updateConfig(
    configId: number,
    request: IndicatorConfigUpdateRequest
  ): Promise<IndicatorConfig> {
    return await retryRequest(
      async () => {
        const response = await apiClient.put<IndicatorConfig>(
          `/indicators/configs/${configId}`,
          request
        )
        return response.data
      },
      '更新配置'
    )
  }

  /**
   * 删除指标配置 (带重试)
   * @param configId 配置ID
   */
  async deleteConfig(configId: number): Promise<void> {
    return await retryRequest(
      async () => {
        await apiClient.delete(`/indicators/configs/${configId}`)
      },
      '删除配置'
    )
  }

  /**
   * 应用保存的配置 (加载并更新last_used_at)
   * @param configId 配置ID
   * @returns 配置详情
   */
  async applyConfig(configId: number): Promise<IndicatorConfig> {
    // 先获取配置
    const config = await this.getConfig(configId)

    // 更新last_used_at (通过PUT请求触发服务器端更新)
    await this.updateConfig(configId, {})

    return config
  }
}

/**
 * 导出单例实例
 */
export const indicatorService = new IndicatorService()

/**
 * 错误处理辅助函数 (使用分类错误系统)
 */
export function handleIndicatorError(error: AxiosError): string {
  const errorInfo = classifyError(error)

  // 显示用户友好的错误消息
  ElMessage.error({
    message: errorInfo.userMessage,
    duration: 5000,
    showClose: true
  })

  // 记录详细错误信息到控制台
  console.error('错误详情:', {
    type: errorInfo.type,
    message: errorInfo.message,
    recoverySteps: errorInfo.recoverySteps
  })

  return errorInfo.userMessage
}

/**
 * 默认导出
 */
export default indicatorService
