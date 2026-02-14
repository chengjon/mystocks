
export interface APIResponse {
  success?: boolean;
  data?: Record<string, any> | null;
  error?: ErrorDetail | null;
  timestamp?: string;
  code?: number;
  message?: string;
  request_id?: string;
}

export interface AccountInfo {
  account_id?: string;
  account_type?: string;
  total_assets?: number;
  cash?: number;
  market_value?: number;
  frozen_cash?: number | null;
  total_profit_loss?: number;
  profit_loss_percent?: number;
  risk_level?: string;
  last_update?: string;
}

export interface ActiveAlert {
  id?: number;
  name?: string;
  metric_type?: string;
  threshold_value?: number;
}

export interface BackupListQueryParams {
  database?: string | null;
  backup_type?: string | null;
  status?: string | null;
  limit?: number;
  offset?: number;
  start_date?: string | null;
  end_date?: string | null;
}

export interface BackupMetadata {
  backup_id?: string;
  backup_type?: string;
  database?: string;
  start_time?: string;
  end_time?: string | null;
  duration_seconds?: number | null;
  tables_backed_up?: string[];
  total_rows?: number;
  backup_size_mb?: number;
  compression_ratio?: number | null;
  status?: string;
  error_message?: string | null;
  description?: string | null;
  tags?: string[] | null;
}

export interface BackupRequestBase {
}

export interface BaseEvent {
  event_type?: EventType;
  timestamp?: string;
  version?: string;
}

export interface BaseResponse {
  success?: boolean;
  message?: string;
  data?: T | null;
  timestamp?: string;
  request_id?: string | null;
}

export interface BatchOperation {
  operation?: string;
  data?: Record<string, any>;
  id?: string | null;
}

export interface BatchOperationRequest {
  operations?: BatchOperation[];
  parallel_execution?: boolean;
  max_concurrent?: number | null;
}

export interface BatchOperationResult {
  total_operations?: number;
  successful_operations?: number;
  failed_operations?: number;
  results?: AlgorithmResult[];
  execution_time?: number;
  id?: string | null;
  success?: boolean;
  data?: any | null;
  error?: string | null;
}

export interface CleanupBackupsRequest {
  retention_days?: number;
  database?: string | null;
  backup_type?: string | null;
  dry_run?: boolean;
  force?: boolean;
}

export interface CleanupResult {
  success?: boolean;
  message?: string;
  deleted_count?: number;
  freed_space_mb?: number;
  deleted_files?: string[] | null;
  retention_days?: number;
  dry_run?: boolean;
}

export interface CommonError {
  code?: number;
  message?: string;
  data?: Record<string, any> | null;
  detail?: string | null;
}

export interface CurrencyField {
  amount?: number;
}

export interface DashboardRequest {
  user_id?: number;
  trade_date?: string | null;
  include_market_overview?: boolean;
  include_watchlist?: boolean;
  include_portfolio?: boolean;
  include_risk_alerts?: boolean;
}

export interface DashboardResponse {
  user_id?: number;
  trade_date?: string;
  generated_at?: string;
  market_overview?: MarketOverview | null;
  watchlist?: WatchlistSummary | null;
  portfolio?: PortfolioSummary | null;
  risk_alerts?: RiskAlertSummary | null;
  data_source?: string;
  cache_hit?: boolean;
}

export interface DateField {
  date?: string;
}

export interface DateRangeModel {
  start_date?: string;
  end_date?: string;
}

export interface EMAParams {
  period?: number;
  price_type?: string;
}

export interface EquityCurvePoint {
  date_field?: string;
  equity?: number;
  drawdown?: number;
  benchmark_equity?: number | null;
}

export interface ErrorDetail {
  error_code?: string;
  error_message?: string;
  details?: Record<string, any> | null;
}

export interface ErrorResponse {
  error?: string;
  detail?: string | null;
  message?: string;
  error_code?: string;
  error_message?: string;
  details?: Record<string, any> | null;
  timestamp?: string;
  success?: 'False';
  path?: string | null;
  request_id?: string | null;
}

export interface ErrorResponseModel {
  code?: string;
  message?: string;
  details?: any | null;
  timestamp?: number;
}

export type EventType = 'task.created' | 'task.started' | 'task.progress' | 'task.completed' | 'task.failed' | 'indicator.calculation.started' | 'indicator.calculation.completed' | 'indicator.calculation.failed' | 'stock.indicators.completed' | 'market.data.update' | 'market.price.update' | 'system.heartbeat' | 'system.status_changed';

export interface FeatureGenerationRequest {
  stock_code?: string;
  market?: string;
  step?: number;
  include_indicators?: boolean;
}

export interface FeatureGenerationResponse {
  success?: boolean;
  message?: string;
  total_samples?: number;
  feature_dim?: number;
  step?: number;
  feature_columns?: string[];
  metadata?: Record<string, any>;
}

export interface FilterParams {
}

export interface FilterRequest {
  filters?: Record<string, any> | null;
}

export interface HealthCheckResponse {
  status?: string;
  version?: string;
  uptime?: number;
  timestamp?: string;
  services?: Record<string, any> | null;
}

export interface HeatmapResponse {
  sector?: string;
  stocks?: HeatmapStock[];
  avg_change?: number;
}

export interface HeatmapStock {
  symbol?: string;
  name?: string;
  change_percent?: number;
  market_cap?: number | null;
}

export interface HotSector {
  sector_name?: string;
  change_percent?: number;
  leading_stock?: string | null;
  stock_count?: number;
}

export interface HyperparameterSearchRequest {
  stock_code?: string;
  market?: string;
  step?: number;
  cv?: number;
  param_grid?: Record<string, List[any]> | null;
}

export interface HyperparameterSearchResponse {
  success?: boolean;
  message?: string;
  best_params?: Record<string, any>;
  best_rmse?: number;
  best_mse?: number;
  cv_results?: Record<string, any>;
}

export interface IndexQuote {
  index_code?: string;
  index_name?: string;
  current_price?: number;
  change?: number;
  change_percent?: number;
  volume?: number | null;
  amount?: number | null;
}

export interface IndexQuoteResponse {
  code?: string;
  name?: string;
  price?: number;
  pre_close?: number;
  open?: number;
  high?: number;
  low?: number;
  volume?: number;
  amount?: number;
  change?: number | null;
  change_pct?: number | null;
  timestamp?: string;
}

export interface IntegrityVerificationResult {
  backup_id?: string;
  is_valid?: boolean;
  verification_details?: Record<string, any>;
  report_file_path?: string | null;
  verification_time?: string;
}

export interface LongHuBangItem {
  symbol?: string;
  name?: string;
  net_amount?: number;
  reason?: string | null;
}

export interface LongHuBangRequest {
  symbol?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  min_net_amount?: number | null;
  limit?: number;
}

export interface LongHuBangResponse {
  id?: number;
  symbol?: string;
  name?: string;
  trade_date?: string;
  reason?: string | null;
  buy_amount?: number;
  sell_amount?: number;
  net_amount?: number;
  turnover_rate?: number;
  institution_buy?: number | null;
  institution_sell?: number | null;
  created_at?: string | null;
}

export interface MAParams {
  period?: number;
  price_type?: string;
}

export interface MLResponse {
  success?: boolean;
  message?: string;
  data?: any | null;
}

export interface MessageResponse {
  success?: boolean;
  message?: string;
  data?: Record<string, any> | null;
}

export type MessageStatus = 'pending' | 'in_progress' | 'success' | 'failed' | 'retry' | 'dead_letter';

export interface MillisecondTimestampField {
  timestamp?: number;
}

export interface ModelDetailResponse {
  name?: string;
  metadata?: Record<string, any>;
  training_history?: Record<string, any>[];
  feature_importance?: Record<string, any>[] | null;
}

export interface ModelEvaluationRequest {
  model_name?: string;
  stock_code?: string;
  market?: string;
}

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

