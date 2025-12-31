/**
 * Additional API Types
 *
 * Supplementary type definitions for API responses that were
 * not included in the auto-generated types.
 */

// ============================================
// Monitoring Types
// ============================================

export interface SystemStatusResponse {
  status?: string;
  uptime?: number;
  memory?: MemoryInfo;
  cpu?: CPUInfo;
  disk?: DiskInfo;
  services?: ServiceStatus[];
  timestamp?: string;
}

export interface MemoryInfo {
  total?: number;
  used?: number;
  available?: number;
  percent?: number;
}

export interface CPUInfo {
  cores?: number;
  usage?: number;
  model?: string;
}

export interface DiskInfo {
  total?: number;
  used?: number;
  available?: number;
  percent?: number;
}

export interface ServiceStatus {
  name?: string;
  status?: 'running' | 'stopped' | 'error';
  latency?: number;
  lastCheck?: string;
}

export interface MonitoringAlertResponse {
  alerts?: Alert[];
  total?: number;
}

export interface Alert {
  id?: number;
  level?: 'info' | 'warning' | 'error' | 'critical';
  message?: string;
  source?: string;
  timestamp?: string;
  acknowledged?: boolean;
}

export interface LogEntryResponse {
  logs?: LogEntry[];
  total?: number;
  page?: number;
  pageSize?: number;
}

export interface LogEntry {
  id?: number;
  level?: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR';
  message?: string;
  timestamp?: string;
  source?: string;
  details?: Record<string, any>;
}

export interface DataQualityResponse {
  checks?: DataQualityCheck[];
  summary?: DataQualitySummary;
  timestamp?: string;
}

export interface DataQualityCheck {
  table?: string;
  column?: string;
  checkType?: string;
  status?: 'pass' | 'fail' | 'warning';
  message?: string;
  value?: number;
  threshold?: number;
}

export interface DataQualitySummary {
  totalChecks?: number;
  passed?: number;
  failed?: number;
  warnings?: number;
}

// ============================================
// Strategy Types
// ============================================

export interface StrategyConfigResponse {
  id?: number;
  name?: string;
  description?: string;
  type?: string;
  parameters?: Record<string, any>;
  createdAt?: string;
  updatedAt?: string;
}

// ============================================
// Trade Types
// ============================================

export interface OrderRequest {
  symbol?: string;
  type?: 'market' | 'limit' | 'stop';
  side?: 'buy' | 'sell';
  quantity?: number;
  price?: number;
  stopPrice?: number;
  timeInForce?: 'day' | 'gtc' | 'ioc' | 'fok';
  strategyId?: string | null;
}

export interface OrderResponse {
  orderId?: string;
  symbol?: string;
  type?: string;
  side?: string;
  quantity?: number;
  price?: number;
  filledQuantity?: number;
  status?: 'pending' | 'filled' | 'partial' | 'cancelled' | 'rejected';
  createdAt?: string;
  updatedAt?: string;
  message?: string;
}

// ============================================
// User Types
// ============================================

export interface UserProfileResponse {
  id?: number;
  username?: string;
  email?: string;
  name?: string;
  preferences?: UserPreferences;
  createdAt?: string;
  updatedAt?: string;
}

export interface UserPreferences {
  theme?: 'light' | 'dark' | 'system';
  language?: string;
  notifications?: boolean;
  timezone?: string;
}

export interface WatchlistResponse {
  watchlist?: WatchlistItem[];
  total?: number;
}

export interface WatchlistItem {
  symbol?: string;
  name?: string;
  addedAt?: string;
  notes?: string;
  price?: number;
  changePercent?: number;
}

// ============================================
// Indicator Types (supplementary)
// ============================================

export interface OverlayIndicatorResponse {
  success?: boolean;
  data?: OverlayIndicatorData;
  message?: string;
}

export interface OscillatorIndicatorResponse {
  success?: boolean;
  data?: OscillatorIndicatorData;
  message?: string;
}

export interface OverlayIndicatorData {
  abbreviation?: string;
  values?: number[];
  parameters?: Record<string, any>;
}

export interface OscillatorIndicatorData {
  abbreviation?: string;
  values?: number[];
  signals?: OscillatorSignal[];
  parameters?: Record<string, any>;
}

export interface OscillatorSignal {
  type?: 'bullish' | 'bearish' | 'neutral';
  value?: number;
  timestamp?: string;
}

// ============================================
// API Response Types
// ============================================

export interface IndicatorResponse {
  success?: boolean;
  code?: number;
  message?: string;
  data?: any;
  timestamp?: string;
}

// ============================================
// Indicator Parameter Types
// ============================================

export interface IndicatorParameter {
  name?: string;
  type?: string;
  default?: any;
  min?: number;
  max?: number;
  step?: number;
}

// ============================================
// Backtest Types (moved from generated-types)
// ============================================

export interface BacktestRequest {
  strategyName?: string;
  symbols?: string[];
  startDate?: string;
  endDate?: string;
  initialCapital?: number;
  parameters?: Record<string, any>;
}

export interface BacktestResponse {
  taskId?: string;
  status?: string;
  summary?: BacktestResultSummary | null;
  equityCurve?: Record<string, any>[];
  trades?: BacktestTrade[];
  errorMessage?: string | null;
}

export interface BacktestResultSummary {
  totalReturn?: number;
  annualizedReturn?: number;
  maxDrawdown?: number;
  sharpeRatio?: number;
  winRate?: number;
  totalTrades?: number;
}

export interface BacktestTrade {
  symbol?: string;
  entryDate?: string;
  exitDate?: string;
  entryPrice?: number;
  exitPrice?: number;
  quantity?: number;
  pnl?: number;
  returnPct?: number;
}

// ============================================
// Notification Types
// ============================================

export interface NotificationResponse {
  id?: number;
  type?: string;
  title?: string;
  message?: string;
  isRead?: boolean;
  createdAt?: string;
  data?: Record<string, any>;
}
