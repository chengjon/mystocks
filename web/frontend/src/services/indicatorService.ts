/**
 * Indicator API Service
 * 技术指标 API 客户端服务
 */

import axios, { AxiosInstance, AxiosError } from 'axios'
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
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8888'
const API_TIMEOUT = 30000 // 30 seconds

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
   * 获取指标注册表
   * @returns 所有可用指标及其元数据
   */
  async getRegistry(): Promise<IndicatorRegistryResponse> {
    const response = await apiClient.get<IndicatorRegistryResponse>('/indicators/registry')
    return response.data
  }

  /**
   * 获取指定分类的指标
   * @param category 指标分类
   * @returns 该分类下的所有指标
   */
  async getIndicatorsByCategory(category: IndicatorCategory): Promise<IndicatorMetadata[]> {
    const response = await apiClient.get<IndicatorMetadata[]>(`/indicators/registry/${category}`)
    return response.data
  }

  /**
   * 计算技术指标
   * @param request 指标计算请求
   * @returns 指标计算结果
   */
  async calculateIndicators(request: IndicatorCalculateRequest): Promise<IndicatorCalculateResponse> {
    const response = await apiClient.post<IndicatorCalculateResponse>(
      '/indicators/calculate',
      request
    )
    return response.data
  }

  /**
   * 创建指标配置
   * @param request 配置创建请求
   * @returns 创建的配置
   */
  async createConfig(request: IndicatorConfigCreateRequest): Promise<IndicatorConfig> {
    const response = await apiClient.post<IndicatorConfig>('/indicators/configs', request)
    return response.data
  }

  /**
   * 获取用户的所有指标配置
   * @returns 配置列表
   */
  async listConfigs(): Promise<IndicatorConfigListResponse> {
    const response = await apiClient.get<IndicatorConfigListResponse>('/indicators/configs')
    return response.data
  }

  /**
   * 获取指定ID的配置
   * @param configId 配置ID
   * @returns 配置详情
   */
  async getConfig(configId: number): Promise<IndicatorConfig> {
    const response = await apiClient.get<IndicatorConfig>(`/indicators/configs/${configId}`)
    return response.data
  }

  /**
   * 更新指标配置
   * @param configId 配置ID
   * @param request 更新请求
   * @returns 更新后的配置
   */
  async updateConfig(
    configId: number,
    request: IndicatorConfigUpdateRequest
  ): Promise<IndicatorConfig> {
    const response = await apiClient.put<IndicatorConfig>(
      `/indicators/configs/${configId}`,
      request
    )
    return response.data
  }

  /**
   * 删除指标配置
   * @param configId 配置ID
   */
  async deleteConfig(configId: number): Promise<void> {
    await apiClient.delete(`/indicators/configs/${configId}`)
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
 * 错误处理辅助函数
 */
export function handleIndicatorError(error: AxiosError): string {
  if (error.response) {
    const data = error.response.data as any

    // 如果有error_message字段,优先使用
    if (data?.error_message) {
      return data.error_message
    }

    // 如果有detail字段
    if (data?.detail) {
      if (typeof data.detail === 'string') {
        return data.detail
      } else if (data.detail?.error_message) {
        return data.detail.error_message
      }
    }

    // 通用错误消息
    if (error.response.status === 422) {
      return '请求参数验证失败,请检查输入'
    } else if (error.response.status === 500) {
      return '服务器内部错误,请稍后重试'
    }
  } else if (error.request) {
    return '网络连接失败,请检查网络连接'
  }

  return '未知错误,请稍后重试'
}

/**
 * 默认导出
 */
export default indicatorService
