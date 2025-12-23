/**
 * System & Monitoring API Service
 *
 * Provides methods for monitoring system status, alerts, logs, and data quality.
 */

import { request } from '@/utils/request'
import { MonitoringAdapter } from '@/utils/monitoring-adapters'
import type {
  SystemStatusResponse,
  MonitoringAlertResponse,
  LogEntryResponse,
  DataQualityResponse
} from '@/api/types/generated-types'
import type {
  SystemStatusVM,
  MonitoringAlertVM,
  LogEntryVM,
  DataQualityVM
} from '@/utils/monitoring-adapters'

class MonitoringApiService {
  private baseUrl = '/api/monitoring'

  /**
   * Get system status overview
   */
  async getSystemStatus(): Promise<SystemStatusVM> {
    const rawData = await request.get(`${this.baseUrl}/system/status`)
    return MonitoringAdapter.toSystemStatusVM(rawData)
  }

  /**
   * Get detailed system metrics
   */
  async getSystemMetrics(params?: {
    startTime?: string
    endTime?: string
    interval?: string
  }): Promise<{
    cpu: Array<{ timestamp: number; value: number }>
    memory: Array<{ timestamp: number; value: number }>
    disk: Array<{ timestamp: number; value: number }>
    network: Array<{ timestamp: number; inbound: number; outbound: number }>
  }> {
    return request.get(`${this.baseUrl}/system/metrics`, { params })
  }

  /**
   * Get monitoring alerts
   */
  async getAlerts(params?: {
    severity?: string
    category?: string
    acknowledged?: boolean
    resolved?: boolean
    startDate?: string
    endDate?: string
    limit?: number
    offset?: number
  }): Promise<MonitoringAlertVM[]> {
    const rawData = await request.get(`${this.baseUrl}/alerts`, { params })
    return MonitoringAdapter.toMonitoringAlertVM(rawData)
  }

  /**
   * Get alert details
   */
  async getAlert(alertId: string): Promise<MonitoringAlertVM> {
    const rawData = await request.get(`${this.baseUrl}/alerts/${alertId}`)
    const alerts = MonitoringAdapter.toMonitoringAlertVM([rawData])
    return alerts[0]
  }

  /**
   * Acknowledge alert
   */
  async acknowledgeAlert(alertId: string, comment?: string): Promise<void> {
    await request.post(`${this.baseUrl}/alerts/${alertId}/acknowledge`, { comment })
  }

  /**
   * Resolve alert
   */
  async resolveAlert(alertId: string, resolution?: string): Promise<void> {
    await request.post(`${this.baseUrl}/alerts/${alertId}/resolve`, { resolution })
  }

  /**
   * Get log entries
   */
  async getLogs(params?: {
    level?: string
    logger?: string
    module?: string
    startTime?: string
    endTime?: string
    message?: string
    limit?: number
    offset?: number
  }): Promise<LogEntryVM[]> {
    const rawData = await request.get(`${this.baseUrl}/logs`, { params })
    return MonitoringAdapter.toLogEntryVM(rawData)
  }

  /**
   * Get log details
   */
  async getLog(logId: string): Promise<LogEntryVM> {
    const rawData = await request.get(`${this.baseUrl}/logs/${logId}`)
    const logs = MonitoringAdapter.toLogEntryVM([rawData])
    return logs[0]
  }

  /**
   * Search logs
   */
  async searchLogs(query: {
    searchTerm: string
    filters?: {
      level?: string
      logger?: string
      module?: string
      timeRange?: {
        start: string
        end: string
      }
    }
    limit?: number
  }): Promise<LogEntryVM[]> {
    const rawData = await request.post(`${this.baseUrl}/logs/search`, query)
    return MonitoringAdapter.toLogEntryVM(rawData)
  }

  /**
   * Get data quality metrics
   */
  async getDataQuality(params?: {
    dataType?: string
    startTime?: string
    endTime?: string
  }): Promise<DataQualityVM> {
    const rawData = await request.get(`${this.baseUrl}/data-quality`, { params })
    return MonitoringAdapter.toDataQualityVM(rawData)
  }

  /**
   * Get data quality issues
   */
  async getDataQualityIssues(params?: {
    type?: string
    severity?: string
    resolved?: boolean
    limit?: number
  }): Promise<Array<{
    id: string
    type: string
    severity: string
    description: string
    affectedRecords: number
    suggestion: string
    resolved: boolean
    resolvedAt?: string
    resolvedBy?: string
  }>> {
    return request.get(`${this.baseUrl}/data-quality/issues`, { params })
  }

  /**
   * Resolve data quality issue
   */
  async resolveDataQualityIssue(issueId: string, resolution: {
    action: string
    comment?: string
  }): Promise<void> {
    await request.post(`${this.baseUrl}/data-quality/issues/${issueId}/resolve`, resolution)
  }

  /**
   * Get service health status
   */
  async getServiceHealth(): Promise<{
    services: Array<{
      name: string
      status: 'healthy' | 'warning' | 'critical'
      lastCheck: string
      responseTime: number
      errorRate: number
      uptime: number
      healthEndpoint?: string
    }>
    overallStatus: 'healthy' | 'warning' | 'critical'
  }> {
    return request.get(`${this.baseUrl}/health/services`)
  }

  /**
   * Get performance metrics
   */
  async getPerformanceMetrics(params?: {
    startTime?: string
    endTime?: string
    granularity?: 'minute' | 'hour' | 'day'
  }): Promise<{
    apiMetrics: {
      requestsPerMinute: number
      averageResponseTime: number
      errorRate: number
      p95ResponseTime: number
      p99ResponseTime: number
    }
    systemMetrics: {
      cpuUsage: number
      memoryUsage: number
      diskUsage: number
      networkThroughput: number
    }
    databaseMetrics: {
      connectionCount: number
      queryPerformance: number
      slowQueries: number
    }
  }> {
    return request.get(`${this.baseUrl}/performance`, { params })
  }

  /**
   * Get monitoring dashboard data
   */
  async getDashboardData(): Promise<{
    systemStatus: SystemStatusVM
    recentAlerts: MonitoringAlertVM[]
    performanceMetrics: any
    healthSummary: {
      totalServices: number
      healthyServices: number
      servicesWithIssues: number
      criticalServices: number
    }
  }> {
    const [systemStatus, recentAlerts, performanceMetrics, healthSummary] = await Promise.all([
      this.getSystemStatus(),
      this.getAlerts({ limit: 10 }),
      this.getPerformanceMetrics(),
      this.getServiceHealth()
    ])

    return {
      systemStatus,
      recentAlerts,
      performanceMetrics,
      healthSummary: {
        totalServices: healthSummary.services.length,
        healthyServices: healthSummary.services.filter(s => s.status === 'healthy').length,
        servicesWithIssues: healthSummary.services.filter(s => s.status !== 'healthy').length,
        criticalServices: healthSummary.services.filter(s => s.status === 'critical').length
      }
    }
  }

  /**
   * Export monitoring data
   */
  async exportData(params: {
    type: 'alerts' | 'logs' | 'metrics' | 'all'
    format?: 'csv' | 'json' | 'excel'
    startDate?: string
    endDate?: string
    filters?: Record<string, any>
  }): Promise<Blob> {
    const response = await request.get(`${this.baseUrl}/export`, {
      params,
      responseType: 'blob'
    })
    return response
  }

  /**
   * Get monitoring statistics
   */
  async getStatistics(period?: string): Promise<{
    alerts: {
      total: number
      critical: number
      high: number
      medium: number
      low: number
      acknowledged: number
      resolved: number
      avgResolutionTime: number
    }
    logs: {
      total: number
      errors: number
      warnings: number
      info: number
      debug: number
      errorRate: number
    }
    system: {
      avgUptime: number
      avgResponseTime: number
      avgCpuUsage: number
      avgMemoryUsage: number
      incidents: number
    }
  }> {
    return request.get(`${this.baseUrl}/statistics`, {
      params: { period }
    })
  }

  /**
   * Create custom alert rule
   */
  async createAlertRule(rule: {
    name: string
    description?: string
    condition: {
      metric: string
      operator: 'gt' | 'lt' | 'eq' | 'gte' | 'lte'
      threshold: number
      duration?: number
    }
    severity: 'low' | 'medium' | 'high' | 'critical'
    category: string
    actions?: Array<{
      type: 'email' | 'webhook' | 'sms'
      target: string
      template?: string
    }>
    enabled?: boolean
  }): Promise<void> {
    await request.post(`${this.baseUrl}/alert-rules`, rule)
  }

  /**
   * Get alert rules
   */
  async getAlertRules(params?: {
    enabled?: boolean
    category?: string
    limit?: number
  }): Promise<Array<{
    id: string
    name: string
    description?: string
    condition: any
    severity: string
    category: string
    actions: any[]
    enabled: boolean
    createdAt: string
    lastTriggered?: string
  }>> {
    return request.get(`${this.baseUrl}/alert-rules`, { params })
  }

  /**
   * Update alert rule
   */
  async updateAlertRule(ruleId: string, updates: Partial<{
    name: string
    description: string
    condition: any
    severity: string
    actions: any[]
    enabled: boolean
  }>): Promise<void> {
    await request.put(`${this.baseUrl}/alert-rules/${ruleId}`, updates)
  }

  /**
   * Delete alert rule
   */
  async deleteAlertRule(ruleId: string): Promise<void> {
    await request.delete(`${this.baseUrl}/alert-rules/${ruleId}`)
  }

  /**
   * Test alert rule
   */
  async testAlertRule(ruleId: string): Promise<{
    success: boolean
    message: string
    triggeredAt?: string
  }> {
    return request.post(`${this.baseUrl}/alert-rules/${ruleId}/test`)
  }
}

// Export singleton instance
export const monitoringApi = new MonitoringApiService()

// Export class for dependency injection
export default MonitoringApiService