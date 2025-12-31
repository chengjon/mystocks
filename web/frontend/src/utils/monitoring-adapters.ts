
/**
 * System & Monitoring Module Data Adapters
 *
 * Transforms API responses into ViewModels for UI components.
 */

// Temporary: Use any for missing generated types
// TODO: Fix type generation to include these types
type SystemStatusResponse = any
type MonitoringAlertResponse = any
type LogEntryResponse = any
type DataQualityResponse = any
type DataQualityIssue = any

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
   * Note: This adapter handles two API response formats:
   * 1. cpu/memory/disk as number (direct value) - current format
   * 2. cpu/memory/disk as object { current, total, percentage } - expected format
   */
  static toSystemStatusVM(data: SystemStatusResponse): SystemStatusVM {
    // Handle cpu - can be number or object
    const cpuData = data.cpu
    const cpu = typeof cpuData === 'number'
      ? { current: cpuData, total: 100, percentage: cpuData }
      : (cpuData as any) || { current: 0, total: 100, percentage: 0 }

    // Handle memory - can be number (MB) or object
    const memoryData = data.memory
    const memory = typeof memoryData === 'number'
      ? { current: memoryData, total: 0, percentage: 0 }
      : (memoryData as any) || { current: 0, total: 0, percentage: 0 }

    // Handle disk - can be number (GB) or object
    const diskData = data.disk
    const disk = typeof diskData === 'number'
      ? { current: diskData, total: 0, percentage: 0 }
      : (diskData as any) || { current: 0, total: 0, percentage: 0 }

    // Handle network - can be object or undefined
    const networkData = (data as any).network
    const network = networkData || { inbound: 0, outbound: 0, errors: 0, status: 'normal' as const, unit: 'req/s' }

    // Handle database - can be object or undefined
    const databaseData = (data as any).database
    const database = databaseData || { connected: false, responseTime: 0, connections: 0, maxConnections: 0, status: 'critical' as const }

    // Handle api - can be object or undefined
    const apiData = (data as any).api
    const api = apiData || { uptime: 0, requestsPerMinute: 0, averageResponseTime: 0, errorRate: 0, status: 'normal' as const }

    return {
      cpu: {
        current: cpu.current,
        total: cpu.total,
        percentage: cpu.percentage,
        status: this.getMetricStatus(cpu.percentage),
        unit: '%'
      },
      memory: {
        current: memory.current,
        total: memory.total,
        percentage: memory.percentage,
        status: this.getMetricStatus(memory.percentage),
        unit: 'MB'
      },
      disk: {
        current: disk.current,
        total: disk.total,
        percentage: disk.percentage,
        status: this.getMetricStatus(disk.percentage),
        unit: 'GB'
      },
      network: {
        inbound: network.inbound || 0,
        outbound: network.outbound || 0,
        errors: network.errors || 0,
        status: this.getNetworkStatus(network.errors),
        unit: 'req/s'
      },
      database: {
        connected: database.connected ?? false,
        responseTime: database.responseTime ?? 0,
        connections: database.connections ?? 0,
        maxConnections: database.maxConnections ?? 0,
        status: database.connected ? this.getMetricStatus(database.responseTime) : 'critical'
      },
      api: {
        uptime: api.uptime ?? 0,
        requestsPerMinute: api.requestsPerMinute ?? 0,
        averageResponseTime: api.averageResponseTime ?? 0,
        errorRate: api.errorRate ?? 0,
        status: this.getApiStatus(api)
      },
      websocket: ((data as any).websocket as any)?.connected ?? false,
      services: ((data as any).services || []).map((service: any) => ({
        name: service.name || '',
        status: this.getServiceStatus(service.status),
        cpu: service.cpu ?? 0,
        memory: service.memory ?? 0,
        lastCheck: this.formatDateTime(service.lastCheck),
        healthEndpoint: service.healthEndpoint
      })),
      lastUpdate: Date.now(),
      status: this.getOverallStatus(data)
    }
  }

  /**
   * Convert monitoring alerts to ViewModel
   * Note: API returns alerts array inside alerts field, with different field names
   */
  static toMonitoringAlertVM(data: MonitoringAlertResponse[]): MonitoringAlertVM[] {
    // Handle different response formats
    const alerts = Array.isArray(data)
      ? data
      : (data as any).alerts || []

    return alerts.map((alert: any) => ({
      id: String(alert.id || ''),
      title: alert.message || alert.title || '系统告警',
      description: alert.message || alert.description || '',
      severity: this.getSeverity(alert.severity),
      category: 'system',
      source: alert.source || 'system',
      timestamp: alert.timestamp ? new Date(alert.timestamp).getTime() : Date.now(),
      acknowledged: alert.acknowledged || false,
      resolved: alert.resolved || false,
      assignee: alert.assignee,
      tags: []
    }))
  }

  /**
   * Convert log entries to ViewModel
   * Note: API returns logs array inside logs field, with different field names
   */
  static toLogEntryVM(data: LogEntryResponse[]): LogEntryVM[] {
    // Handle different response formats
    const logs = Array.isArray(data)
      ? data
      : (data as any).logs || []

    return logs.map((log: any) => ({
      id: String(log.id || Date.now()),
      timestamp: this.formatDateTime(log.timestamp),
      level: this.getLogLevel(log.level) as 'debug' | 'info' | 'warning' | 'error' | 'fatal',
      logger: log.source || log.logger || 'system',
      message: log.message || '',
      module: log.module || 'unknown',
      context: {},
      stackTrace: undefined
    }))
  }

  /**
   * Convert data quality metrics to ViewModel
   * Note: API returns checks array and summary, not the expected format
   */
  static toDataQualityVM(data: DataQualityResponse): DataQualityVM {
    // Handle actual API response format
    const checks = (data as any).checks || []
    const summary = (data as any).summary || {}

    // Calculate overall score from checks
    const passedChecks = checks.filter((c: any) => c.status === 'passed' || c.status === 'success').length
    const totalChecks = checks.length
    const overallScore = totalChecks > 0 ? (passedChecks / totalChecks) * 100 : 0

    return {
      overallScore,
      completeness: this.toQualityMetric(summary.completeness || overallScore),
      accuracy: this.toQualityMetric(summary.accuracy || overallScore),
      timeliness: this.toQualityMetric(summary.timeliness || overallScore),
      consistency: this.toQualityMetric(summary.consistency || overallScore),
      lastCheck: this.formatDateTime(Date.now()),
      issues: []
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
