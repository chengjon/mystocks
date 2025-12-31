/**
 * System & Monitoring Module Data Adapters
 *
 * Transforms API responses into ViewModels for UI components.
 */

import type {
  SystemStatusResponse,
  MonitoringAlertResponse,
  LogEntryResponse,
  DataQualityResponse,
  DataQualityIssue
} from '@/api/types/generated-types'

// ViewModel interfaces
export interface SystemStatusVM {
  cpu: SystemMetricVM
  memory: SystemMetricVM
  disk: SystemMetricVM
  network: NetworkMetricVM
  database: DatabaseStatusVM
  api: ApiStatusVM
  websocket: boolean
  services: ServiceStatusVM[]
  lastUpdate: number
  status: 'healthy' | 'warning' | 'critical'
}

export interface SystemMetricVM {
  current: number
  total: number
  percentage: number
  status: 'normal' | 'warning' | 'critical'
  unit: string
}

export interface NetworkMetricVM {
  inbound: number
  outbound: number
  errors: number
  status: 'normal' | 'warning' | 'critical'
  unit: string
}

export interface DatabaseStatusVM {
  connected: boolean
  responseTime: number
  connections: number
  maxConnections: number
  status: 'normal' | 'warning' | 'critical'
}

export interface ApiStatusVM {
  uptime: number
  requestsPerMinute: number
  averageResponseTime: number
  errorRate: number
  status: 'normal' | 'warning' | 'critical'
}

export interface ServiceStatusVM {
  name: string
  status: 'running' | 'stopped' | 'error'
  cpu: number
  memory: number
  lastCheck: string
  healthEndpoint?: string
}

export interface MonitoringAlertVM {
  id: string
  title: string
  description: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  category: 'system' | 'performance' | 'security' | 'business'
  source: string
  timestamp: number
  acknowledged: boolean
  resolved: boolean
  assignee?: string
  tags: string[]
}

export interface LogEntryVM {
  id: string
  timestamp: string
  level: 'debug' | 'info' | 'warning' | 'error' | 'fatal'
  logger: string
  message: string
  module: string
  context: Record<string, any>
  stackTrace?: string
}

export interface DataQualityVM {
  overallScore: number
  completeness: QualityMetricVM
  accuracy: QualityMetricVM
  timeliness: QualityMetricVM
  consistency: QualityMetricVM
  lastCheck: string
  issues: DataQualityIssueVM[]
}

export interface QualityMetricVM {
  score: number
  status: 'good' | 'warning' | 'critical'
  details: string
}

export interface DataQualityIssueVM {
  id: string
  type: 'missing' | 'invalid' | 'outdated' | 'duplicate'
  severity: 'low' | 'medium' | 'high' | 'critical'
  description: string
  affectedRecords: number
  suggestion: string
}

export class MonitoringAdapter {
  /**
   * Convert system status to ViewModel
   */
  static toSystemStatusVM(data: SystemStatusResponse): SystemStatusVM {
    return {
      cpu: {
        current: data.cpu?.current || 0,
        total: data.cpu?.total || 0,
        percentage: data.cpu?.percentage || 0,
        status: this.getMetricStatus(data.cpu?.percentage),
        unit: '%'
      },
      memory: {
        current: data.memory?.current || 0,
        total: data.memory?.total || 0,
        percentage: data.memory?.percentage || 0,
        status: this.getMetricStatus(data.memory?.percentage),
        unit: 'MB'
      },
      disk: {
        current: data.disk?.current || 0,
        total: data.disk?.total || 0,
        percentage: data.disk?.percentage || 0,
        status: this.getMetricStatus(data.disk?.percentage),
        unit: 'GB'
      },
      network: {
        inbound: data.network?.inbound || 0,
        outbound: data.network?.outbound || 0,
        errors: data.network?.errors || 0,
        status: this.getNetworkStatus(data.network?.errorRate),
        unit: 'req/s'
      },
      database: {
        connected: data.database?.connected || false,
        responseTime: data.database?.responseTime || 0,
        connections: data.database?.connections || 0,
        maxConnections: data.database?.maxConnections || 0,
        status: data.database?.connected ? this.getMetricStatus(data.database?.responseTime) : 'critical'
      },
      api: {
        uptime: data.api?.uptime || 0,
        requestsPerMinute: data.api?.requestsPerMinute || 0,
        averageResponseTime: data.api?.averageResponseTime || 0,
        errorRate: data.api?.errorRate || 0,
        status: this.getApiStatus(data.api)
      },
      websocket: data.websocket?.connected || false,
      services: (data.services || []).map(service => ({
        name: service.name || '',
        status: this.getServiceStatus(service.status),
        cpu: service.cpu || 0,
        memory: service.memory || 0,
        lastCheck: this.formatDateTime(service.lastCheck),
        healthEndpoint: service.healthEndpoint
      })),
      lastUpdate: Date.now(),
      status: this.getOverallStatus(data)
    }
  }

  /**
   * Convert monitoring alerts to ViewModel
   */
  static toMonitoringAlertVM(data: MonitoringAlertResponse[]): MonitoringAlertVM[] {
    return data.map(alert => ({
      id: alert.id || '',
      title: alert.title || '',
      description: alert.description || '',
      severity: this.getSeverity(alert.severity),
      category: (alert.category || 'system') as 'system' | 'performance' | 'security' | 'business',
      source: alert.source || 'system',
      timestamp: alert.timestamp ? new Date(alert.timestamp).getTime() : Date.now(),
      acknowledged: alert.acknowledged || false,
      resolved: alert.resolved || false,
      assignee: alert.assignee,
      tags: alert.tags || []
    }))
  }

  /**
   * Convert log entries to ViewModel
   */
  static toLogEntryVM(data: LogEntryResponse[]): LogEntryVM[] {
    return data.map(log => ({
      id: log.id || '',
      timestamp: this.formatDateTime(log.timestamp),
      level: this.getLogLevel(log.level) as 'debug' | 'info' | 'warning' | 'error' | 'fatal',
      logger: log.logger || '',
      message: log.message || '',
      module: log.module || '',
      context: log.context || {},
      stackTrace: log.stackTrace
    }))
  }

  /**
   * Convert data quality metrics to ViewModel
   */
  static toDataQualityVM(data: DataQualityResponse): DataQualityVM {
    return {
      overallScore: data.overallScore || 0,
      completeness: this.toQualityMetric(data.completeness),
      accuracy: this.toQualityMetric(data.accuracy),
      timeliness: this.toQualityMetric(data.timeliness),
      consistency: this.toQualityMetric(data.consistency),
      lastCheck: this.formatDateTime(data.lastCheck),
      issues: (data.issues || [])
        .filter((issue): issue is DataQualityIssue => typeof issue !== 'string')
        .map((issue): DataQualityIssueVM => ({
          id: issue.id || '',
          type: (issue.type || 'missing') as 'missing' | 'invalid' | 'outdated' | 'duplicate',
          severity: this.getSeverity(issue.severity),
          description: issue.description || '',
          affectedRecords: issue.affectedRecords || 0,
          suggestion: issue.suggestion || ''
        }))
    }
  }

  /**
   * Convert quality metric to ViewModel
   */
  private static toQualityMetric(metric: any): QualityMetricVM {
    return {
      score: metric.score || 0,
      status: this.getQualityStatus(metric.score),
      details: metric.details || ''
    }
  }

  /**
   * Get metric status based on percentage
   */
  private static getMetricStatus(percentage?: number): 'normal' | 'warning' | 'critical' {
    if (!percentage) return 'normal'
    if (percentage >= 80) return 'critical'
    if (percentage >= 60) return 'warning'
    return 'normal'
  }

  /**
   * Get network status based on error rate
   */
  private static getNetworkStatus(errorRate?: number): 'normal' | 'warning' | 'critical' {
    if (!errorRate) return 'normal'
    if (errorRate >= 5) return 'critical'
    if (errorRate >= 1) return 'warning'
    return 'normal'
  }

  /**
   * Get API status
   */
  private static getApiStatus(api: any): 'normal' | 'warning' | 'critical' {
    const hasIssue = api.errorRate >= 1 || api.averageResponseTime > 1000
    const hasCriticalIssue = api.errorRate >= 5 || api.averageResponseTime > 3000

    if (hasCriticalIssue) return 'critical'
    if (hasIssue) return 'warning'
    return 'normal'
  }

  /**
   * Get service status
   */
  private static getServiceStatus(status: string): 'running' | 'stopped' | 'error' {
    switch (status?.toLowerCase()) {
      case 'running':
      case 'active':
      case 'healthy':
        return 'running'
      case 'stopped':
      case 'inactive':
      case 'disabled':
        return 'stopped'
      case 'error':
      case 'failed':
      case 'unhealthy':
        return 'error'
      default:
        return 'stopped'
    }
  }

  /**
   * Get overall system status
   */
  private static getOverallStatus(data: any): 'healthy' | 'warning' | 'critical' {
    const hasCritical =
      data.cpu?.percentage >= 90 ||
      data.memory?.percentage >= 90 ||
      !data.database?.connected ||
      data.api?.errorRate >= 10

    const hasWarning =
      data.cpu?.percentage >= 70 ||
      data.memory?.percentage >= 70 ||
      data.network?.errorRate >= 3 ||
      data.api?.errorRate >= 3

    if (hasCritical) return 'critical'
    if (hasWarning) return 'warning'
    return 'healthy'
  }

  /**
   * Get severity level
   */
  private static getSeverity(severity: string): 'low' | 'medium' | 'high' | 'critical' {
    switch (severity?.toLowerCase()) {
      case 'low':
        return 'low'
      case 'medium':
        return 'medium'
      case 'high':
        return 'high'
      case 'critical':
      case 'fatal':
        return 'critical'
      default:
        return 'medium'
    }
  }

  /**
   * Get log level
   */
  private static getLogLevel(level: string): string {
    const levels = ['debug', 'info', 'warning', 'error', 'fatal']
    return levels.includes(level?.toLowerCase()) ? level.toLowerCase() : 'info'
  }

  /**
   * Get quality status
   */
  private static getQualityStatus(score: number): 'good' | 'warning' | 'critical' {
    if (score >= 90) return 'good'
    if (score >= 70) return 'warning'
    return 'critical'
  }

  /**
   * Format date and time
   */
  private static formatDateTime(timestamp: string | number | Date): string {
    const date = new Date(timestamp)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  /**
   * Format number with unit
   */
  static formatWithUnit(value: number, unit: string): string {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M ${unit}`
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}k ${unit}`
    }
    return `${value} ${unit}`
  }

  /**
   * Get status color
   */
  static getStatusColor(status: string): string {
    switch (status) {
      case 'healthy':
      case 'running':
      case 'good':
      case 'normal':
        return '#67C23A'
      case 'warning':
      case 'medium':
        return '#E6A23C'
      case 'critical':
      case 'error':
      case 'high':
        return '#F56C6C'
      case 'stopped':
        return '#909399'
      default:
        return '#409EFF'
    }
  }

  /**
   * Get severity color
   */
  static getSeverityColor(severity: string): string {
    switch (severity) {
      case 'low':
        return '#67C23A'
      case 'medium':
        return '#E6A23C'
      case 'high':
        return '#F56C6C'
      case 'critical':
        return '#C62828'
      default:
        return '#409EFF'
    }
  }
}

export default MonitoringAdapter
