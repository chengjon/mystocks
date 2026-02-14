
export interface ModelEvaluationResponse {
  success?: boolean;
  message?: string;
  model_name?: string;
  metrics?: Record<string, any>;
}

export interface ModelInfo {
  name?: string;
  path?: string;
  trained_at?: string;
  test_rmse?: number;
  test_r2?: number;
  train_samples?: number | null;
  test_samples?: number | null;
  feature_dim?: number | null;
  model_id?: string;
  algorithm_type?: string;
  symbol?: string;
  created_at?: string;
  metrics?: AlgorithmMetrics | null;
  config?: Record<string, any>;
  status?: string;
}

export interface ModelListResponse {
  total?: number;
  models?: ModelInfo[];
}

export interface ModelPredictRequest {
  model_name?: string;
  stock_code?: string;
  market?: string;
  days?: number;
}

export interface ModelPredictResponse {
  success?: boolean;
  message?: string;
  model_name?: string;
  stock_code?: string;
  predictions?: PredictionResult[];
}

export interface ModelTrainRequest {
  stock_code?: string;
  market?: string;
  step?: number;
  test_size?: number;
  model_name?: string;
  model_params?: Record<string, any> | null;
}

export interface ModelTrainResponse {
  success?: boolean;
  message?: string;
  model_name?: string;
  metrics?: Record<string, any>;
}

export interface MonitoringSummaryResponse {
  total_stocks?: number;
  limit_up_count?: number;
  limit_down_count?: number;
  strong_up_count?: number;
  strong_down_count?: number;
  avg_change_percent?: number | null;
  total_amount?: number | null;
  active_alerts?: number;
  unread_alerts?: number;
}

export interface MultiIndicatorRequest {
  symbol?: string;
  indicators?: IndicatorSpec[];
  start_date?: string | null;
  end_date?: string | null;
}

export interface MultiIndicatorResponse {
  symbol?: string;
  indicators?: IndicatorResponseItem[];
  calculated_at?: string;
}

export interface NGramPredictRequest {
  model_id?: string;
  current_sequence?: number[];
  n?: number;
}

export interface NGramTrainRequest {
  symbol?: string;
  n?: number;
  sequence_type?: string;
  window_size?: number;
}

export interface NeuralNetworkPredictRequest {
  model_id?: string;
  current_data?: Record<string, List[number]>;
}

export interface NeuralNetworkTrainRequest {
  symbol?: string;
  input_features?: string[];
  prediction_horizon?: number;
  lookback_window?: number;
  nn_config?: NeuralNetworkConfig;
}

export interface NotificationResponse {
  id?: string;
  type?: string;
  title?: string;
  message?: string;
  data?: Record<string, any> | null;
  priority?: string;
  isRead?: boolean;
  createdAt?: string;
  expiresAt?: string | null;
  actionUrl?: string | null;
  actionText?: string | null;
  icon?: string | null;
  category?: string;
}

export interface NotificationTestRequest {
  notification_type?: string;
  config_data?: Record<string, any>;
}

export interface NotificationTestResponse {
  success?: boolean;
  message?: string;
}

export interface OHLCVData {
  dates?: string[];
  open?: number[];
  high?: number[];
  low?: number[];
  close?: number[];
  volume?: number[];
  turnover?: number[];
}

export type OperationType = 'insert' | 'update' | 'delete' | 'bulk_insert';

export interface OrderRequest {
  symbol?: string;
  direction?: string;
  order_type?: string;
  price?: number | null;
  quantity?: number;
}

export interface OrderResponse {
  order_id?: string;
  symbol?: string;
  direction?: string;
  order_type?: string;
  price?: number | null;
  quantity?: number;
  filled_quantity?: number;
  average_price?: number | null;
  status?: string;
  commission?: number | null;
  created_at?: string;
  updated_at?: string | null;
}

export interface OscillatorIndicatorRequest {
  symbol?: string;
  indicator_type?: string;
  params?: Record<string, any> | null;
  start_date?: string | null;
  end_date?: string | null;
}

export interface OscillatorIndicatorResponse {
  symbol?: string;
  indicator_type?: string;
  indicator_name?: string;
  values?: OscillatorIndicatorValue[];
  params?: Record<string, any>;
  calculated_at?: string;
}

export interface OscillatorIndicatorValue {
  timestamp?: number;
  dif?: number | null;
  dea?: number | null;
  macd?: number | null;
  k?: number | null;
  d?: number | null;
  j?: number | null;
  rsi?: number | null;
}

export interface OverlayIndicatorRequest {
  symbol?: string;
  indicator_type?: string;
  params?: Record<string, any>;
  start_date?: string | null;
  end_date?: string | null;
}

export interface OverlayIndicatorResponse {
  symbol?: string;
  indicator_type?: string;
  indicator_name?: string;
  values?: OverlayIndicatorValue[];
  params?: Record<string, any>;
  calculated_at?: string;
}

export interface OverlayIndicatorValue {
  timestamp?: number;
  value?: number;
  upper?: number | null;
  middle?: number | null;
  lower?: number | null;
}

export interface PagedResponse {
  success?: boolean;
  message?: string;
  data?: T[];
  total?: number;
  page?: number;
  page_size?: number;
  total_pages?: number;
  has_next?: boolean;
  has_prev?: boolean;
  timestamp?: string;
}

export interface PaginatedResponse {
  items?: T[];
  total?: number;
  page?: number;
  page_size?: number;
  total_pages?: number;
  data?: T[];
}

export interface PaginationInfo {
  page?: number;
  page_size?: number;
  total?: number;
  pages?: number | null;
}

export interface PaginationModel {
  page?: number;
  page_size?: number;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
}

export interface PaginationRequest {
  page?: number;
  page_size?: number;
}

export interface PatternDefinition {
  name?: string;
  sequence?: number[];
}

export interface PercentageField {
  percentage?: number;
}

export interface PerformanceMetrics {
  total_return?: number;
  annual_return?: number;
  benchmark_return?: number | null;
  alpha?: number | null;
  beta?: number | null;
  sharpe_ratio?: number;
  max_drawdown?: number;
  volatility?: number;
  total_trades?: number;
  win_rate?: number;
  profit_factor?: number;
  calmar_ratio?: number | null;
  sortino_ratio?: number | null;
}

export interface PortfolioSummary {
  total_market_value?: number;
  total_cost?: number;
  total_profit_loss?: number;
  total_profit_loss_percent?: number;
  position_count?: number;
  positions?: PositionItem[];
}

export interface Position {
  symbol?: string;
  symbol_name?: string | null;
  quantity?: number;
  available_quantity?: number;
  cost_price?: number;
  current_price?: number | null;
  market_value?: number;
  profit_loss?: number;
  profit_loss_percent?: number;
  last_update?: string;
}

export interface PositionItem {
  symbol?: string;
  name?: string | null;
  quantity?: number;
  avg_cost?: number;
  current_price?: number | null;
  market_value?: number | null;
  profit_loss?: number | null;
  profit_loss_percent?: number | null;
  position_percent?: number | null;
}

export interface PositionsResponse {
  positions?: Position[];
  total_count?: number;
  total_market_value?: number;
  total_profit_loss?: number;
  total_profit_loss_percent?: number;
}

export type PredictionLabel = 'BUY' | 'SELL' | 'HOLD';

export interface PredictionResult {
  date?: string;
  predicted_price?: number;
  confidence?: number | null;
  prediction?: (string | number | List[number]);
  probabilities?: Record<string, number> | null;
  metadata?: Record<string, any> | null;
}

export interface PriceField {
  price?: number;
}

export interface RSIParams {
  period?: number;
}

export interface RealTimeQuoteResponse {
  code?: string;
  name?: string;
  price?: number;
  pre_close?: number;
  open?: number;
  high?: number;
  low?: number;
  volume?: number;
  amount?: number;
  bid1?: number;
  bid1_volume?: number;
  ask1?: number;
  ask1_volume?: number;
  timestamp?: string;
  change?: number | null;
  change_pct?: number | null;
}

export interface RealtimeMonitoringResponse {
  id?: number;
  symbol?: string;
  stock_name?: string | null;
  timestamp?: string;
  trade_date?: string;
  price?: number | null;
  change_percent?: number | null;
  volume?: number | null;
  amount?: number | null;
  indicators?: Dict | null;
  market_strength?: string | null;
  is_limit_up?: boolean;
  is_limit_down?: boolean;
}

export interface RecoveryMetadata {
  backup_id?: string;
  recovery_type?: string;
  target_time?: string | null;
  target_tables?: string[] | null;
  dry_run?: boolean;
  success?: boolean;
  message?: string;
  start_time?: string;
  end_time?: string | null;
  duration_seconds?: number | null;
}

export interface RecoveryRequestBase {
  dry_run?: boolean;
  force?: boolean;
  backup_id?: string;
}

export interface RelationshipDefinition {
  from_symbol?: string;
  to_symbol?: string;
  delay?: number;
}

export interface ResponseModel {
  code?: string;
  message?: string;
  data?: any | null;
  timestamp?: number;
}

export interface RiskAlert {
  alert_id?: number;
  alert_type?: string;
  alert_level?: string;
  symbol?: string | null;
  message?: string;
  triggered_at?: string;
  is_read?: boolean;
}

export interface RiskAlertCreate {
  name?: string;
  metric_type?: string;
  threshold_value?: number;
  condition?: string;
  entity_type?: string;
  entity_id?: number | null;
  is_active?: boolean;
  notification_channels?: string[];
}

export interface RiskAlertListResponse {
  alerts?: RiskAlertResponse[];
}

export interface RiskAlertResponse {
  id?: number;
  name?: string;
  metric_type?: string;
  threshold_value?: number;
  condition?: string;
  entity_type?: string;
  entity_id?: number | null;
  is_active?: boolean;
  notification_channels?: string[];
  created_at?: string;
  updated_at?: string | null;
}

export interface RiskAlertSummary {
  total_count?: number;
  unread_count?: number;
  critical_count?: number;
  alerts?: RiskAlert[];
}

export interface RiskAlertUpdate {
  name?: string | null;
  metric_type?: string | null;
  threshold_value?: number | null;
  condition?: string | null;
  entity_type?: string | null;
  entity_id?: number | null;
  is_active?: boolean | null;
  notification_channels?: string[] | null;
}

export interface RiskDashboardResponse {
  metrics?: RiskMetricsSummary;
  active_alerts?: ActiveAlert[];
  risk_history?: RiskHistoryPoint[];
}

export interface RiskHistoryPoint {
  date?: string;
  var_95_hist?: number | null;
  cvar_95?: number | null;
  beta?: number | null;
}

export interface RiskMetricsHistoryResponse {
  metrics_history?: RiskHistoryPoint[];
}

export interface RiskMetricsSummary {
  var_95_hist?: number | null;
  cvar_95?: number | null;
  beta?: number | null;
}

export interface ScheduledJobInfo {
  job_id?: string;
  job_type?: string;
  schedule?: string;
  next_run?: string | null;
  last_run?: string | null;
  status?: string;
  description?: string | null;
}

export interface SchedulerControlRequest {
  action?: 'start' | 'stop' | 'restart' | 'status';
  force?: boolean;
}

export interface SortParams {
  sort_by?: string;
  order?: string;
}

export interface SortRequest {
  sort_by?: string | null;
  sort_order?: string | null;
}

export interface StandardResponse {
  status?: string;
  code?: number;
  message?: string;
  timestamp?: string;
}

export interface StockInfo {
  symbol?: string;
  name?: string | null;
  latest_price?: number | null;
  change_percent?: number | null;
  volume?: number | null;
  amount?: number | null;
}

export interface StockListResponse {
  success?: boolean;
  data?: Record<string, any>;
  timestamp?: string;
}

