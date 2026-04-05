export interface MarketOverview {
  indices: unknown[]
  rankings: unknown[]
  volume: unknown
  lastUpdate: string
}

export interface TradingSignals {
  signals: unknown[]
  total: number
  filters: SignalFilters
}

export interface TradingHistory {
  records: unknown[]
  total: number
  filters: HistoryFilters
}

export interface PositionMonitorData {
  positions: unknown[]
  pnlAnalysis: unknown
  riskMetrics: unknown[]
}

export interface PerformanceAnalysis {
  returnCurve: unknown[]
  attribution: unknown
  metrics: unknown
}

export interface StrategyManagementData {
  strategies: unknown[]
  templates: unknown[]
}

export interface RiskMonitorData {
  overview: unknown
  trends: unknown[]
  alerts: unknown[]
}

export interface AnnouncementMonitorData {
  announcements: unknown[]
  sentimentAnalysis: unknown
}

export interface RiskAlertsData {
  activeAlerts: unknown[]
  alertRules: unknown[]
  alertHistory: unknown[]
}

export interface MonitoringDashboardData {
  systemStatus: unknown
  performanceMetrics: unknown[]
  dataQuality: unknown
}

export type SystemSettingsSection = 'general' | 'datasource' | 'notification' | 'security'

export interface SystemSettingsMeta {
  contractStatus: 'degraded' | 'full'
  unifiedBackendApiAvailable: boolean
  backendReadSections: SystemSettingsSection[]
  backendWriteSections: SystemSettingsSection[]
  unsupportedSections: SystemSettingsSection[]
  pageSaveMode: 'local-storage-degrade' | 'backend'
}

export interface SystemSettings {
  general: unknown
  datasource: unknown
  notification: unknown
  security: unknown
  meta: SystemSettingsMeta
}

export interface SystemHealth {
  api: 'healthy' | 'degraded'
  data: 'healthy' | 'degraded'
  monitoring: 'healthy' | 'degraded'
  overall: 'healthy' | 'degraded'
}

export enum DataClassification {
  TICK_DATA = 'tick_data',
  MINUTE_KLINE = 'minute_kline',
  DAILY_KLINE = 'daily_kline',
  SYMBOLS_INFO = 'symbols_info',
  INDUSTRY_CLASS = 'industry_class',
  CONCEPT_CLASS = 'concept_class',
  TECHNICAL_INDICATORS = 'technical_indicators',
  QUANT_FACTORS = 'quant_factors',
  TRADE_SIGNALS = 'trade_signals',
  ORDER_RECORDS = 'order_records',
  TRADE_RECORDS = 'trade_records',
  POSITION_HISTORY = 'position_history',
  USER_CONFIG = 'user_config',
  SYSTEM_CONFIG = 'system_config',
  DATA_QUALITY_METRICS = 'data_quality_metrics',
  STRATEGY_PARAMS = 'strategy_params'
}

export interface DataRoute {
  database: 'tdengine' | 'postgresql'
  table: string
}

export interface CachedData {
  data: unknown
  timestamp: number
  ttl: number
}

export interface RealtimeUpdateConfig {
  channel: string
  callback: Function
}

export interface SignalFilters {
  type?: string
  status?: string
  symbol?: string
  dateRange?: [Date, Date]
}

export interface HistoryFilters {
  symbol?: string
  type?: string
  dateRange?: [Date, Date]
  status?: string
}

export interface AnnouncementFilters {
  type?: string
  dateRange?: [Date, Date]
  symbol?: string
}

export interface BacktestConfig {
  strategyId: string
  symbol: string
  startDate: string
  endDate: string
  initialCapital: number
  parameters?: Record<string, unknown>
}

export interface OptimizationConfig {
  method: 'grid' | 'genetic' | 'bayesian'
  parameters: Record<string, unknown[]>
  target: 'sharpe' | 'returns' | 'max_drawdown'
  constraints?: Record<string, unknown>
}

export interface DataConfig {
  source?: string
  destination?: string
  filters?: unknown
  format?: string
}

export type DataOperation = 'import' | 'export' | 'cleanup'
export type BatchExecutionResult = unknown
export type BacktestResult = unknown
export type BacktestResults = unknown[]
export type OptimizationResult = unknown
export type DataOperationResult = unknown
