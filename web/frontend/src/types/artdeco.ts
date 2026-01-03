/**
 * ArtDeco Design System Type Definitions
 *
 * This file contains all TypeScript interfaces and types used across
 * the ArtDeco Vue components for type safety and consistency.
 */

// ============================================
// Dashboard Types
// ============================================

export interface MarketData {
  shIndex: number
  shChange: number
  szIndex: number
  szChange: number
  cybIndex: number
  cybChange: number
  northFlow: number
}

export interface SectorHeatmapData {
  name: string
  value: number
  change: number
}

export interface LimitUpData {
  code: string
  name: string
  limitUpTime: string
}

export interface LimitDownData {
  code: string
  name: string
  limitDownTime: string
}

export interface DataSourceStatus {
  source: string
  status: 'normal' | 'slow' | 'error'
  lastUpdate: string
}

// ============================================
// Market Center Types
// ============================================

export interface StockInfo {
  label: string
  value: string
  valueClass?: string
}

export interface TimePeriod {
  label: string
  value: string
}

export interface AdjustType {
  label: string
  value: string
}

export interface MarketStock {
  code: string
  name: string
  price: string
  change: number
  volume: string
  turnover: string
}

export interface KlineData {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

// ============================================
// Stock Screener Types
// ============================================

export interface StockPool {
  key: string
  label: string
}

export interface Filter {
  key: string
  label: string
  type: 'input' | 'select' | 'range'
  placeholder?: string
  options?: { label: string; value: string }[]
}

export interface ResultColumn {
  key: string
  label: string
}

export interface StockResult {
  code: string
  name: string
  price: string
  change: number
  pe: string
  pb: string
  marketCap: string
  turnoverRate: number
}

// ============================================
// Data Analysis Types
// ============================================

export interface IndicatorDetail {
  name: string
  overboughtCount: number
  overboughtRatio: number
  oversoldCount: number
  oversoldRatio: number
  neutralRatio: number
}

// ============================================
// Strategy Lab Types
// ============================================

export interface Strategy {
  name: string
  type: string
  status: 'running' | 'paused'
  return: number
  sharpe: number
  drawdown: number
  created: string
}

export interface StrategyStats {
  total: number
  running: number
  paused: number
  bestReturn: number
  avgReturn: number
  maxDrawdown: number
}

// ============================================
// Backtest Arena Types
// ============================================

export interface BacktestMetrics {
  totalReturn: number
  sharpe: number
  maxDrawdown: number
  winRate: number
}

export interface Trade {
  date: string
  code: string
  name: string
  action: '买入' | '卖出'
  price: number
  quantity: number
  profit: number
  profitRatio: number
}

// ============================================
// Trade Station Types
// ============================================

export interface AccountOverview {
  totalAssets: number
  positionValue: number
  availableCash: number
}

export interface Order {
  id: string
  code: string
  type: '买入' | '卖出'
  quantity: number
  price: number
  status: 'pending' | 'filled' | 'cancelled'
}

export interface Position {
  code: string
  name: string
  quantity: number
  cost: number
  current: number
  profit: number
}

export interface TradeHistory {
  time: string
  code: string
  name: string
  action: '买入' | '卖出'
  quantity: number
  price: number
  amount: number
}

// ============================================
// Risk Center Types
// ============================================

export interface RiskMetrics {
  riskLevel: string
  currentDrawdown: number
  positionRatio: number
  concentration: number
}

export interface RiskAlert {
  time: string
  type: string
  content: string
  level: 'danger' | 'warning' | 'info'
  status: 'pending' | 'resolved'
}

export interface PositionDistribution {
  name: string
  value: number
  color: string
}

// ============================================
// System Settings Types
// ============================================

export interface DataSource {
  name: string
  status: 'normal' | 'maintenance' | 'error'
  priority: number
  latency: string
  enabled: boolean
}

export interface UserSettings {
  username: string
  email: string
  timezone: string
  language: string
}

export interface SystemConfig {
  refreshRate: number
  defaultPeriod: string
  wsAutoReconnect: boolean
  enableCache: boolean
}

export interface RiskConfig {
  maxPositionRatio: number
  maxSingleStock: number
  maxDrawdown: number
}

export interface LogConfig {
  level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR'
  retentionDays: number
  enablePerformance: boolean
  enableTrade: boolean
}

// ============================================
// API Response Types
// ============================================

export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

// ============================================
// Common Utility Types
// ============================================

export type ChangeClass = 'data-rise' | 'data-fall' | 'data-flat'

export type StatusBadge = 'success' | 'warning' | 'danger' | 'info'

export interface ChartRef {
  init: () => void
  resize: () => void
  dispose: () => void
}

// ============================================
// Component Props Types
// ============================================

export interface BaseComponentProps {
  loading?: boolean
  error?: string | null
}

export interface TableProps {
  data: any[]
  columns: string[]
  sortable?: boolean
  filterable?: boolean
}

export interface ChartProps {
  data: any[]
  type: 'line' | 'bar' | 'pie' | 'candlestick'
  height?: string | number
}

// ============================================
// Form Types
// ============================================

export interface FormField {
  key: string
  label: string
  type: 'text' | 'number' | 'email' | 'select' | 'checkbox' | 'toggle'
  value: any
  placeholder?: string
  options?: { label: string; value: any }[]
  min?: number
  max?: number
  required?: boolean
  readonly?: boolean
}

export interface FormConfig {
  fields: FormField[]
  submitLabel?: string
  resetLabel?: string
}

// ============================================
// Router Types
// ============================================

export interface RouteMeta {
  title: string
  icon?: string
  description?: string
  requiresAuth?: boolean
  roles?: string[]
}

// ============================================
// ECharts Types
// ============================================

import type { EChartsOption } from 'echarts'

export type ChartOption = EChartsOption

export interface ChartSeries {
  type: 'line' | 'bar' | 'pie' | 'scatter' | 'effectScatter'
  name?: string
  data: any[]
  [key: string]: any
}

// ============================================
// Validation Types
// ============================================

export interface ValidationResult {
  valid: boolean
  errors: Record<string, string[]>
}

export interface FormRules {
  [key: string]: {
    required?: boolean
    min?: number
    max?: number
    pattern?: RegExp
    validator?: (value: any) => boolean | string
    message?: string
  }
}

// ============================================
// Note: All types are already exported inline above
// No need for duplicate export declarations
// ============================================
