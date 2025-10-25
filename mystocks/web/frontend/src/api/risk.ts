/**
 * 风险监控 API
 *
 * 与后端 risk_api.py 接口对接
 */

import request from '@/utils/request'

export const riskApi = {
  // 计算 VaR/CVaR
  calculateVarCvar(params: { entity_type: string; entity_id: number; confidence_level?: number }) {
    return request.get('/api/v1/risk/var-cvar', { params })
  },

  // 计算 Beta
  calculateBeta(params: { entity_type: string; entity_id: number; market_index?: string }) {
    return request.get('/api/v1/risk/beta', { params })
  },

  // 获取风险仪表盘
  getDashboard() {
    return request.get('/api/v1/risk/dashboard')
  },

  // 获取风险指标历史
  getMetricsHistory(params: {
    entity_type: string
    entity_id: number
    start_date: string
    end_date: string
  }) {
    return request.get('/api/v1/risk/metrics/history', { params })
  },

  // 获取风险预警列表
  listAlerts(params?: { is_active?: boolean }) {
    return request.get('/api/v1/risk/alerts', { params })
  },

  // 创建风险预警
  createAlert(data: any) {
    return request.post('/api/v1/risk/alerts', data)
  },

  // 更新风险预警
  updateAlert(id: number, data: any) {
    return request.put(`/api/v1/risk/alerts/${id}`, data)
  },

  // 删除风险预警
  deleteAlert(id: number) {
    return request.delete(`/api/v1/risk/alerts/${id}`)
  },

  // 发送测试通知
  testNotification(data: { notification_type: string; config_data: any }) {
    return request.post('/api/v1/risk/notifications/test', data)
  }
}
