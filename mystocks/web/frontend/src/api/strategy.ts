/**
 * 策略管理 API
 *
 * 与后端 strategy_api.py 接口对接
 */

import request from '@/utils/request'

export interface Strategy {
  id: number
  name: string
  description: string
  strategy_type: 'model_based' | 'rule_based' | 'hybrid'
  model_id?: number
  parameters: Record<string, any>
  status: 'draft' | 'active' | 'archived'
  created_at: string
  updated_at: string
}

export interface ListStrategiesParams {
  status?: string
  page?: number
  page_size?: number
}

export const strategyApi = {
  // 获取策略列表
  listStrategies(params: ListStrategiesParams) {
    return request.get('/api/v1/strategy/strategies', { params })
  },

  // 创建策略
  createStrategy(data: Partial<Strategy>) {
    return request.post('/api/v1/strategy/strategies', data)
  },

  // 获取策略详情
  getStrategy(id: number) {
    return request.get(`/api/v1/strategy/strategies/${id}`)
  },

  // 更新策略
  updateStrategy(id: number, data: Partial<Strategy>) {
    return request.put(`/api/v1/strategy/strategies/${id}`, data)
  },

  // 删除策略
  deleteStrategy(id: number) {
    return request.delete(`/api/v1/strategy/strategies/${id}`)
  },

  // 训练模型
  trainModel(data: any) {
    return request.post('/api/v1/strategy/models/train', data)
  },

  // 获取训练状态
  getTrainingStatus(taskId: string) {
    return request.get(`/api/v1/strategy/models/training/${taskId}/status`)
  },

  // 获取模型列表
  listModels(params?: { model_type?: string; status?: string }) {
    return request.get('/api/v1/strategy/models', { params })
  },

  // 获取模型指标
  getModelMetrics(modelId: number) {
    return request.get(`/api/v1/strategy/models/${modelId}/metrics`)
  }
}
