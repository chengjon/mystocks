
/**
 * System & Monitoring Module Data Adapters
 *
 * Transforms API responses into ViewModels for UI components.
 */

// Temporary: Use any for missing generated types
// TODO: Fix type generation to include these types
type SystemStatusResponse = Record<string, unknown>
type MonitoringAlertResponse = Record<string, unknown>
type LogEntryResponse = Record<string, unknown>
type DataQualityResponse = Record<string, unknown>
type _DataQualityIssue = Record<string, unknown>

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
  context: Record<string, unknown>
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
    // Type alias for internal metric data
    type MetricData = { current: number; total: number; percentage: number }
    type NetworkData = { inbound: number; outbound: number; errors: number; status: string; unit: string }
    type DatabaseData = { connected: boolean; responseTime: number; connections: number; maxConnections: number; status: string }
    type ApiData = { uptime: number; requestsPerMinute: number; averageResponseTime: number; errorRate: number }

    const rawData = data as Record<string, unknown>

    // Handle cpu - can be number or object
    const cpuData = rawData.cpu
    const cpu: MetricData = typeof cpuData === 'number'
      ? { current: cpuData, total: 100, percentage: cpuData }
      : (cpuData as MetricData) || { current: 0, total: 100, percentage: 0 }

    // Handle memory - can be number (MB) or object
    const memoryData = rawData.memory
    const memory: MetricData = typeof memoryData === 'number'
      ? { current: memoryData, total: 0, percentage: 0 }
      : (memoryData as MetricData) || { current: 0, total: 0, percentage: 0 }

    // Handle disk - can be number (GB) or object
    const diskData = rawData.disk
    const disk: MetricData = typeof diskData === 'number'
      ? { current: diskData, total: 0, percentage: 0 }
      : (diskData as MetricData) || { current: 0, total: 0, percentage: 0 }

    // Handle network - can be object or undefined
    const networkData = rawData.network as NetworkData | undefined
    const network: NetworkData = networkData || { inbound: 0, outbound: 0, errors: 0, status: 'normal', unit: 'req/s' }

    // Handle database - can be object or undefined
    const databaseData = rawData.database as DatabaseData | undefined
    const database: DatabaseData = databaseData || { connected: false, responseTime: 0, connections: 0, maxConnections: 0, status: 'critical' }

    // Handle api - can be object or undefined
    const apiData = rawData.api as ApiData | undefined
    const api: ApiData = apiData || { uptime: 0, requestsPerMinute: 0, averageResponseTime: 0, errorRate: 0 }

    // Type for service data
    type ServiceData = { name: string; status: string; cpu?: number; memory?: number; lastCheck?: string | number; healthEndpoint?: string }
    type WebsocketData = { connected?: boolean }

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
      websocket: (rawData.websocket as WebsocketData)?.connected ?? false,
      services: ((rawData.services || []) as ServiceData[]).map((service: ServiceData) => ({
        name: service.name || '',
        status: this.getServiceStatus(service.status),
        cpu: service.cpu ?? 0,
        memory: service.memory ?? 0,
        lastCheck: this.formatDateTime(service.lastCheck || Date.now()),
        healthEndpoint: service.healthEndpoint
      })),
      lastUpdate: Date.now(),
      status: this.getOverallStatus(rawData)
    }
  }

  /**
   * Convert monitoring alerts to ViewModel
   * Note: API returns alerts array inside alerts field, with different field names
   */
  static toMonitoringAlertVM(data: MonitoringAlertResponse[]): MonitoringAlertVM[] {
    // Type for alert data
    type AlertData = {
      id?: string | number
      message?: string
      title?: string
      description?: string
      severity?: string
      source?: string
      timestamp?: string | number
      acknowledged?: boolean
      resolved?: boolean
      assignee?: string
    }

    // Handle different response formats
    const rawData = data as unknown
    const alerts: AlertData[] = Array.isArray(data)
      ? data
      : ((rawData as Record<string, unknown>).alerts || []) as AlertData[]

    return alerts.map((alert: AlertData) => ({
      id: String(alert.id || ''),
      title: alert.message || alert.title || '系统告警',
      description: alert.message || alert.description || '',
      severity: this.getSeverity(alert.severity || ''),
      category: 'system' as const,
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
    // Type for log data
    type LogData = {
      id?: string | number
      timestamp?: string | number
      level?: string
      source?: string
      logger?: string
      message?: string
      module?: string
    }

    // Handle different response formats
    const rawData = data as unknown
    const logs: LogData[] = Array.isArray(data)
      ? data
      : ((rawData as Record<string, unknown>).logs || []) as LogData[]

    return logs.map((log: LogData) => ({
      id: String(log.id || Date.now()),
      timestamp: this.formatDateTime(log.timestamp || Date.now()),
      level: this.getLogLevel(log.level || '') as 'debug' | 'info' | 'warning' | 'error' | 'fatal',
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
    // Types for data quality response
    type CheckData = { status: string }
    type SummaryData = {
      completeness?: number | { score?: number; details?: string }
      accuracy?: number | { score?: number; details?: string }
      timeliness?: number | { score?: number; details?: string }
      consistency?: number | { score?: number; details?: string }
    }

    const rawData = data as Record<string, unknown>

    // Handle actual API response format
    const checks = (rawData.checks || []) as CheckData[]
    const summary = (rawData.summary || {}) as SummaryData

    // Calculate overall score from checks
    const passedChecks = checks.filter((c: CheckData) => c.status === 'passed' || c.status === 'success').length
    const totalChecks = checks.length
    const overallScore = totalChecks > 0 ? (passedChecks / totalChecks) * 100 : 0

    // Helper to extract score from number or object
    const extractScore = (val: unknown): number => {
      if (typeof val === 'number') return val
      if (val && typeof val === 'object' && 'score' in val) return (val as { score: number }).score
      return overallScore
    }

    return {
      overallScore,
      completeness: this.toQualityMetric(extractScore(summary.completeness)),
      accuracy: this.toQualityMetric(extractScore(summary.accuracy)),
      timeliness: this.toQualityMetric(extractScore(summary.timeliness)),
      consistency: this.toQualityMetric(extractScore(summary.consistency)),
      lastCheck: this.formatDateTime(Date.now()),
      issues: []
    }
  }

  /**
   * Convert quality metric to ViewModel
   */
  private static toQualityMetric(score: number): QualityMetricVM {
    return {
      score: score || 0,
      status: this.getQualityStatus(score || 0),
      details: ''
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
  private static getApiStatus(api: { errorRate?: number; averageResponseTime?: number }): 'normal' | 'warning' | 'critical' {
    const errorRate = api.errorRate ?? 0
    const avgResponseTime = api.averageResponseTime ?? 0
    const hasIssue = errorRate >= 1 || avgResponseTime > 1000
    const hasCriticalIssue = errorRate >= 5 || avgResponseTime > 3000

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
  private static getOverallStatus(data: Record<string, unknown>): 'healthy' | 'warning' | 'critical' {
    type MetricObj = { percentage?: number }
    type DatabaseObj = { connected?: boolean }
    type ApiObj = { errorRate?: number }
    type NetworkObj = { errors?: number }

    const cpu = data.cpu as MetricObj | undefined
    const memory = data.memory as MetricObj | undefined
    const database = data.database as DatabaseObj | undefined
    const api = data.api as ApiObj | undefined
    const network = data.network as NetworkObj | undefined

    const hasCritical =
      (cpu?.percentage ?? 0) >= 90 ||
      (memory?.percentage ?? 0) >= 90 ||
      database?.connected === false ||
      (api?.errorRate ?? 0) >= 10

    const hasWarning =
      (cpu?.percentage ?? 0) >= 70 ||
      (memory?.percentage ?? 0) >= 70 ||
      (network?.errors ?? 0) >= 3 ||
      (api?.errorRate ?? 0) >= 3

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
