export type SystemStatusResponse = Record<string, unknown>
export type MonitoringAlertResponse = Record<string, unknown>
export type LogEntryResponse = Record<string, unknown>
export type DataQualityResponse = Record<string, unknown>
export type _DataQualityIssue = Record<string, unknown>

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
