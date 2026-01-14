// Auto-generated types for common domain
// Generated at: 2026-01-14T14:57:47.572281

export interface APIResponse {
  success?: boolean;
  data?: Record<string, any> | null;
  timestamp?: string;
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

export interface AhoCorasickMatchRequest {
  automaton_id?: string;
  time_series?: number[];
  threshold?: number;
}

export interface AhoCorasickTrainRequest {
  patterns?: PatternDefinition[];
  market?: string;
}

export type AlertLevel = 'info' | 'warning' | 'critical';

export interface AlertRecordResponse {
  id?: number;
  rule_id?: number | null;
  rule_name?: string | null;
  symbol?: string;
  stock_name?: string | null;
  alert_time?: string;
  alert_type?: string;
  alert_level?: string;
  alert_title?: string | null;
  alert_message?: string | null;
  alert_details?: Record<string, any> | null;
  snapshot_data?: Record<string, any> | null;
  is_read?: boolean;
  is_handled?: boolean;
  created_at?: string;
}

export interface AlertRuleCreate {
  rule_name?: string;
  rule_type?: AlertRuleType;
  description?: string | null;
  symbol?: string | null;
  stock_name?: string | null;
  parameters?: Record<string, any>;
  trigger_conditions?: Record<string, any>;
  notification_config?: Record<string, any>;
  priority?: number;
  is_active?: boolean;
}

export interface AlertRuleResponse {
  id?: number;
  rule_name?: string;
  rule_type?: string;
  description?: string | null;
  symbol?: string | null;
  stock_name?: string | null;
  parameters?: Record<string, any>;
  trigger_conditions?: Record<string, any>;
  notification_config?: Record<string, any>;
  is_active?: boolean;
  priority?: number;
  created_at?: string;
  updated_at?: string;
}

export type AlertRuleType = 'price_change' | 'volume_surge' | 'technical_break' | 'limit_up' | 'limit_down' | 'dragon_tiger';

export interface AlertRuleUpdate {
  rule_name?: string | null;
  description?: string | null;
  parameters?: Record<string, any> | null;
  trigger_conditions?: Record<string, any> | null;
  notification_config?: Record<string, any> | null;
  priority?: number | null;
  is_active?: boolean | null;
}

export interface AlgorithmConfig {
  enable_gpu?: boolean;
  gpu_memory_limit_mb?: number | null;
  enable_validation?: boolean;
  random_seed?: number | null;
}

export interface AlgorithmHealthStatus {
  service?: string;
  status?: string;
  algorithms_loaded?: boolean;
  gpu_available?: boolean;
  supported_algorithms?: number;
  timestamp?: string;
}

export interface AlgorithmInfo {
  type?: string;
  category?: string;
  description?: string;
  parameters?: Record<string, any>;
  use_cases?: string[];
  performance?: Record<string, any>;
}

export interface AlgorithmInfoRequest {
  algorithm_type?: AlgorithmType;
}

export interface AlgorithmMetadata {
  algorithm_type?: AlgorithmType;
  algorithm_name?: string;
  version?: string;
  description?: string | null;
}

export interface AlgorithmMetrics {
  accuracy?: number | null;
  precision?: number | null;
  recall?: number | null;
  f1_score?: number | null;
  training_time?: number | null;
  prediction_time?: number | null;
}

export interface AlgorithmPredictRequest {
  model_id?: string;
  features_data?: (List[number] | List[List[number]]);
  prediction_config?: Record<string, any> | null;
}

export interface AlgorithmResult {
  algorithm_id?: string;
  algorithm_type?: string;
  execution_timestamp?: string;
  status?: AlgorithmStatus;
  success?: boolean;
  message?: string | null;
  data?: Record<string, any> | null;
}

export type AlgorithmStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface AlgorithmTrainRequest {
  algorithm_type?: AlgorithmType;
  symbol?: string;
  features?: string[];
  labels?: string[] | null;
  config?: AlgorithmConfig;
  training_data?: Record<string, any> | null;
}

export type AlgorithmType = 'svm' | 'decision_tree' | 'naive_bayes' | 'brute_force' | 'knuth_morris_pratt' | 'boyer_moore_horspool' | 'aho_corasick' | 'hidden_markov_model' | 'bayesian_network' | 'n_gram' | 'neural_network';

export interface AnnouncementBase {
  stock_code?: string;
  stock_name?: string | null;
  announcement_title?: string;
  announcement_type?: string | null;
  publish_date?: string;
  publish_time?: string | null;
  url?: string | null;
  content?: string | null;
  summary?: string | null;
  keywords?: any[];
  importance_level?: number;
  data_source?: string;
  source_id?: string | null;
  sentiment?: string | null;
  impact_score?: number | null;
}

export interface AnnouncementMonitorRecordResponse {
  id?: number;
  rule_id?: number;
  announcement_id?: number;
  matched_keywords?: any[];
  triggered_at?: string;
  notified?: boolean;
  notified_at?: string | null;
  notification_result?: string | null;
  rule_name?: string | null;
  announcement_title?: string | null;
}

export interface AnnouncementMonitorRuleBase {
  rule_name?: string;
  keywords?: any[];
  announcement_types?: any[];
  stock_codes?: any[];
  min_importance_level?: number;
  notify_enabled?: boolean;
  notify_channels?: any[];
}

export interface AnnouncementMonitorRuleUpdate {
  rule_name?: string | null;
  keywords?: any[] | null;
  announcement_types?: any[] | null;
  stock_codes?: any[] | null;
  min_importance_level?: number | null;
  notify_enabled?: boolean | null;
  notify_channels?: any[] | null;
  is_active?: boolean | null;
}

export interface AnnouncementSearchRequest {
  keywords?: string | null;
  stock_code?: string | null;
  announcement_type?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  min_importance_level?: number | null;
  data_source?: string | null;
  page?: number;
  page_size?: number;
}

export interface AnnouncementStatsResponse {
  total_count?: number;
  today_count?: number;
  important_count?: number;
  by_source?: Record<string, any>;
  by_type?: Record<string, any>;
  by_sentiment?: Record<string, any>;
}

export interface BOLLParams {
  period?: number;
  std_dev?: number;
}

export interface BacktestExecuteRequest {
  strategy_id?: number;
  user_id?: number;
  symbols?: string[];
  start_date?: string;
  end_date?: string;
  initial_capital?: number;
  commission_rate?: number;
  slippage_rate?: number;
  benchmark?: string | null;
}

export interface BacktestListResponse {
  total_count?: number;
  backtests?: BacktestResultSummary[];
  page?: number;
  page_size?: number;
}

export interface BacktestRequest {
  strategy_id?: number;
  user_id?: number;
  symbols?: string[];
  start_date?: string;
  end_date?: string;
  initial_capital?: number;
  commission_rate?: number;
  slippage_rate?: number;
  benchmark?: string | null;
  include_analysis?: boolean;
}

export interface BacktestResponse {
  task_id?: string;
  status?: string;
  summary?: BacktestResultSummary | null;
  equity_curve?: Record<string, any>[];
  trades?: BacktestTrade[];
  error_message?: string | null;
}

export interface BacktestResult {
  backtest_id?: number;
  strategy_id?: number;
  user_id?: number;
  symbols?: string[];
  start_date?: string;
  end_date?: string;
  initial_capital?: number;
  final_capital?: number;
  performance?: PerformanceMetrics;
  equity_curve?: EquityCurvePoint[];
  trades?: TradeRecord[];
  status?: BacktestStatus;
  created_at?: string;
  completed_at?: string | null;
  error_message?: string | null;
}

export interface BacktestResultSummary {
  backtest_id?: number;
  strategy_id?: number;
  strategy_name?: string;
  symbols?: string[];
  date_range?: string;
  total_return?: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  status?: BacktestStatus;
  created_at?: string;
}

export type BacktestStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface BacktestTrade {
  symbol?: string;
  entry_date?: string;
  exit_date?: string;
  entry_price?: number;
  exit_price?: number;
  quantity?: number;
  pnl?: number;
  return_pct?: number;
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
}

export interface BatchOperationResult {
  id?: string | null;
  success?: boolean;
  data?: any | null;
  error?: string | null;
}

export interface BayesianNetworkBuildRequest {
  symbols?: string[];
  relationships?: RelationshipDefinition[];
  time_window?: number;
}

export interface BayesianNetworkInferRequest {
  network_id?: string;
  trigger_event?: Record<string, any>;
  max_delay?: number;
}

export interface BetaRequest {
  entity_type?: string;
  entity_id?: number;
  market_index?: string;
}

export interface BetaResult {
  beta?: number | null;
  correlation?: number | null;
  entity_type?: string | null;
  entity_id?: number | null;
  market_index?: string | null;
}

export interface CancelOrderRequest {
  order_id?: string;
}

export interface CancelOrderResponse {
  order_id?: string;
  success?: boolean;
  message?: string;
  cancelled_quantity?: number;
  remaining_quantity?: number;
  cancelled_at?: string;
}

export interface ChipRaceItem {
  symbol?: string;
  name?: string;
  race_amount?: number;
  change_percent?: number;
}

export interface ChipRaceRequest {
  race_type?: string;
  trade_date?: string | null;
  min_race_amount?: number | null;
  limit?: number;
}

export interface ChipRaceResponse {
  id?: number;
  symbol?: string;
  name?: string;
  trade_date?: string;
  race_type?: string;
  latest_price?: number;
  change_percent?: number;
  prev_close?: number;
  open_price?: number;
  race_amount?: number;
  race_amplitude?: number;
  race_commission?: number;
  race_transaction?: number;
  race_ratio?: number;
  created_at?: string | null;
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

export interface ConceptInfo {
  concept_code?: string;
  concept_name?: string;
  stock_count?: number | null;
  up_count?: number | null;
  down_count?: number | null;
  leader_stock?: string | null;
  latest_price?: number | null;
  change_percent?: number | null;
  change_amount?: number | null;
  volume?: number | null;
  amount?: number | null;
  total_market_value?: number | null;
  turnover_rate?: number | null;
  updated_at?: string | null;
}

export interface ConceptListResponse {
  success?: boolean;
  data?: Record<string, any>;
  timestamp?: string;
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

export interface DragonTigerListResponse {
  id?: number;
  symbol?: string;
  stock_name?: string | null;
  trade_date?: string;
  reason?: string | null;
  total_buy_amount?: number | null;
  total_sell_amount?: number | null;
  net_amount?: number | null;
  institution_buy_count?: number;
  institution_sell_count?: number;
  institution_net_amount?: number | null;
  detail_data?: Record<string, any> | null;
  impact_score?: number | null;
}

export interface EMAParams {
  period?: number;
  price_type?: string;
}

export interface ETFDataRequest {
  symbol?: string | null;
  keyword?: string | null;
  limit?: number;
}

export interface ETFDataResponse {
  id?: number;
  symbol?: string;
  name?: string;
  trade_date?: string;
  latest_price?: number;
  change_percent?: number;
  change_amount?: number;
  volume?: number;
  amount?: number;
  open_price?: number;
  high_price?: number;
  low_price?: number;
  prev_close?: number;
  turnover_rate?: number;
  total_market_cap?: number;
  circulating_market_cap?: number;
  created_at?: string | null;
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
  success?: 'False';
  message?: string;
  error_code?: string;
  details?: Record<string, any> | null;
  timestamp?: string;
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

export interface FundFlowDataResponse {
  fund_flow?: FundFlowItem[];
  total?: number;
  symbol?: string | null;
  timeframe?: string | null;
}

export interface FundFlowItem {
  trade_date?: string;
  main_net_inflow?: number;
  main_net_inflow_rate?: number;
  super_large_net_inflow?: number;
  large_net_inflow?: number;
  medium_net_inflow?: number;
  small_net_inflow?: number;
}

export interface FundFlowRequest {
  symbol?: string;
  timeframe?: string;
  start_date?: string | null;
  end_date?: string | null;
}

export interface FundFlowResponse {
  id?: number;
  symbol?: string;
  trade_date?: string;
  timeframe?: string;
  main_net_inflow?: number;
  main_net_inflow_rate?: number;
  super_large_net_inflow?: number;
  large_net_inflow?: number;
  medium_net_inflow?: number;
  small_net_inflow?: number;
  created_at?: string | null;
}

export interface HMMPredictRequest {
  model_id?: string;
  current_observations?: string[];
}

export interface HMMTrainRequest {
  symbol?: string;
  observations?: string[];
  hmm_config?: HMMConfig;
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

export interface IndicatorCalculateRequest {
  symbol?: string;
  start_date?: string;
  end_date?: string;
  indicators?: IndicatorSpec[];
  use_cache?: boolean;
}

export interface IndicatorCalculateResponse {
  symbol?: string;
  symbol_name?: string;
  start_date?: string;
  end_date?: string;
  ohlcv?: OHLCVData;
  indicators?: IndicatorResult[];
  calculation_time_ms?: number;
  cached?: boolean;
}

export interface IndicatorConfigCreateRequest {
  name?: string;
  indicators?: IndicatorSpec[];
}

export interface IndicatorConfigListResponse {
  total_count?: number;
  configs?: IndicatorConfigResponse[];
}

export interface IndicatorConfigResponse {
  id?: number;
  user_id?: number;
  name?: string;
  indicators?: Record<string, any>[];
  created_at?: string;
  updated_at?: string;
  last_used_at?: string | null;
}

export interface IndicatorConfigUpdateRequest {
  name?: string | null;
  indicators?: IndicatorSpec[] | null;
}

export interface IndicatorInfo {
  indicator_type?: string;
  indicator_name?: string;
  category?: string;
  description?: string;
  default_params?: Record<string, any>;
  output_fields?: string[];
}

export interface IndicatorMetadata {
  abbreviation?: string;
  full_name?: string;
  chinese_name?: string;
  category?: string;
  description?: string;
  panel_type?: string;
  parameters?: Record<string, any>[];
  outputs?: Record<string, string>[];
  reference_lines?: number[] | null;
  min_data_points_formula?: string;
}

export interface IndicatorRegistryResponse {
  indicators?: IndicatorInfo[];
  total_count?: number;
  last_updated?: string;
}

export interface IndicatorResponseItem {
  indicator_type?: string;
  indicator_name?: string;
  data?: Record<string, any>[];
  params?: Record<string, any>;
}

export interface IndicatorResult {
  abbreviation?: string;
  parameters?: Record<string, any>;
  outputs?: IndicatorValueOutput[];
  panel_type?: string;
  reference_lines?: number[] | null;
  error?: string | null;
}

export interface IndicatorSpec {
  abbreviation?: string;
  parameters?: Record<string, any>;
}

export interface IndicatorValueOutput {
  output_name?: string;
  values?: number | null[];
  display_name?: string;
}

export interface IndustryInfo {
  industry_code?: string;
  industry_name?: string;
  stock_count?: number | null;
  up_count?: number | null;
  down_count?: number | null;
  leader_stock?: string | null;
  latest_price?: number | null;
  change_percent?: number | null;
  change_amount?: number | null;
  volume?: number | null;
  amount?: number | null;
  total_market_value?: number | null;
  turnover_rate?: number | null;
  updated_at?: string | null;
}

export interface IndustryListResponse {
  success?: boolean;
  data?: Record<string, any>;
  timestamp?: string;
}

export interface IndustryPerformanceResponse {
  success?: boolean;
  data?: Record<string, any>;
  timestamp?: string;
}

export interface IntegrityVerificationResult {
  backup_id?: string;
  is_valid?: boolean;
  verification_details?: Record<string, any>;
  report_file_path?: string | null;
  verification_time?: string;
}

export interface KDJParams {
  n?: number;
  m1?: number;
  m2?: number;
}

export interface KLineCandleV2 {
  timestamp?: number;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  volume?: number;
  amount?: number | null;
}

export interface KLineRequestV2 {
  symbol?: string;
  interval?: string;
  start_date?: string | null;
  end_date?: string | null;
  adjust?: string;
  limit?: number;
}

export interface KLineResponseV2 {
  klines?: KLineCandleV2[];
  total_count?: number;
  symbol?: string;
  interval?: string;
}

export interface KlineCandle {
  datetime?: string;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  volume?: number;
  amount?: number | null;
}

export interface KlineDataPoint {
  date?: string;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  volume?: number;
  amount?: number | null;
}

export interface KlineRequest {
  symbol?: string;
  start_date?: string | null;
  end_date?: string | null;
  period?: string;
}

export interface KlineResponse {
  symbol?: string;
  period?: string;
  data?: KlineCandle[];
  count?: number;
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

export interface MACDParams {
  fast_period?: number;
  slow_period?: number;
  signal_period?: number;
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

export interface MarketDataQueryModel {
  symbol?: string;
  start_date?: string;
  end_date?: string;
  interval?: string | null;
}

export interface MarketOverviewDetailedResponse {
  market_stats?: MarketOverviewStats;
  top_etfs?: TopETFItem[];
  chip_races?: ChipRaceItem[];
  long_hu_bang?: LongHuBangItem[];
  timestamp?: string;
}

export interface MarketOverviewRequest {
  date?: string | null;
}

export interface MarketOverviewResponse {
  date?: string;
  indices?: IndexQuote[];
  hot_sectors?: HotSector[];
  market_sentiment?: string;
}

export interface MarketOverviewStats {
  total_stocks?: number;
  rising_stocks?: number;
  falling_stocks?: number;
  avg_change_percent?: number;
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
  data?: T[];
  total?: number;
  page?: number;
  page_size?: number;
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

export interface PositionsResponse {
  positions?: Position[];
  total_count?: number;
  total_market_value?: number;
  total_profit_loss?: number;
  total_profit_loss_percent?: number;
}

export type PredictionLabel = 'BUY' | 'SELL' | 'HOLD';

export interface PredictionResult {
  prediction?: (string | number | List[number]);
  confidence?: number | null;
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
  indicators?: Record<string, any> | null;
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
  date?: date_type;
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

export interface StockRatingItem {
  股票代码?: string;
  股票名称?: string;
  目标价?: string;
  最新评级?: string;
  评级机构?: string;
  分析师?: string;
  行业?: string;
  评级日期?: string;
  摘要?: string;
}

export interface StockRatingsHealthResponse {
  status?: string;
  last_successful_scrape?: string | null;
  average_response_time?: number;
  success_rate?: number;
  total_scrapes?: number;
  recent_errors?: string[];
}

export interface StockRatingsRequest {
  max_pages?: number | null;
}

export interface StockRatingsResponse {
  data?: StockRatingItem[];
  total_count?: number;
  pages_scraped?: number;
  max_pages?: number;
  timestamp?: string;
  source?: string;
}

export interface StockRatingsSummary {
  total_ratings?: number;
  unique_stocks?: number;
  rating_agencies?: number;
  industries?: number;
  latest_update?: string;
  rating_distribution?: Record<string, any>;
}

export interface StockSymbolField {
  symbol?: string;
}

export interface StockSymbolModel {
  symbol?: string;
}

export interface StrategyConfig {
  strategy_id?: number | null;
  user_id?: number;
  strategy_name?: string;
  strategy_type?: StrategyType;
  description?: string | null;
  parameters?: StrategyParameter[];
  max_position_size?: number;
  stop_loss_percent?: number | null;
  take_profit_percent?: number | null;
  status?: StrategyStatus;
  created_at?: string | null;
  updated_at?: string | null;
  tags?: string[];
}

export interface StrategyCreateRequest {
  user_id?: number;
  strategy_name?: string;
  strategy_type?: StrategyType;
  description?: string | null;
  parameters?: StrategyParameter[];
  max_position_size?: number;
  stop_loss_percent?: number | null;
  take_profit_percent?: number | null;
  tags?: string[];
}

export interface StrategyErrorResponse {
  error_code?: string;
  error_message?: string;
  details?: Record<string, any> | null;
  timestamp?: string;
}

export interface StrategyListResponse {
  total_count?: number;
  strategies?: StrategyConfig[];
  page?: number;
  page_size?: number;
}

export interface StrategyParameter {
  name?: string;
  value?: any;
  description?: string | null;
  data_type?: string;
}

export type StrategyStatus = 'draft' | 'active' | 'paused' | 'archived';

export type StrategyType = 'momentum' | 'mean_reversion' | 'breakout' | 'grid' | 'custom';

export interface StrategyUpdateRequest {
  strategy_name?: string | null;
  description?: string | null;
  parameters?: StrategyParameter[] | null;
  max_position_size?: number | null;
  stop_loss_percent?: number | null;
  take_profit_percent?: number | null;
  status?: StrategyStatus | null;
  tags?: string[] | null;
}

export interface SubscriptionInfo {
  plan?: string;
  status?: string;
  startDate?: string;
  endDate?: string;
  trialEndDate?: string | null;
  autoRenew?: boolean;
  features?: string[];
  limits?: Record<string, number>;
  nextBillingAmount?: number | null;
  nextBillingDate?: string | null;
}

export type SyncDirection = 'tdengine_to_postgresql' | 'postgresql_to_tdengine' | 'bidirectional';

export interface TDenginePITRRequest {
  target_time?: string;
  target_tables?: string[] | null;
  restore_to_database?: string | null;
}

export interface TaskConfig {
  task_id?: string;
  task_name?: string;
  task_type?: TaskType;
  task_module?: string;
  task_function?: string;
  description?: string | null;
  priority?: TaskPriority;
  schedule?: TaskSchedule | null;
  params?: Record<string, any>;
  timeout?: number;
  retry_count?: number;
  retry_delay?: number;
  dependencies?: string[];
  tags?: string[];
  auto_restart?: boolean;
  stop_on_error?: boolean;
}

export interface TaskExecution {
  execution_id?: string;
  task_id?: string;
  status?: TaskStatus;
  start_time?: string | null;
  end_time?: string | null;
  duration?: number | null;
  result?: Record<string, any> | null;
  error_message?: string | null;
  log_path?: string | null;
  retry_count?: number;
}

export type TaskPriority = 100 | 200 | 500 | 800 | 900;

export interface TaskResponse {
  success?: boolean;
  message?: string;
  data?: Record<string, any> | null;
  task_id?: string | null;
  execution_id?: string | null;
}

export interface TaskSchedule {
  schedule_type?: string;
  cron_expression?: string | null;
  interval_seconds?: number | null;
  start_time?: string | null;
  end_time?: string | null;
  enabled?: boolean;
}

export interface TaskStatistics {
  task_id?: string;
  task_name?: string;
  total_executions?: number;
  success_count?: number;
  failed_count?: number;
  avg_duration?: number;
  last_execution_time?: string | null;
  last_status?: TaskStatus | null;
  success_rate?: number;
}

export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export type TaskType = 'cron' | 'supervisor' | 'manual' | 'data_sync' | 'indicator_calc' | 'market_fetch' | 'data_processing' | 'strategy_backtest' | 'cache_cleanup' | 'market_sync' | 'notification' | 'health_check' | 'cache_warmup' | 'report_generation';

export interface TdxDataRequest {
  stock_code?: string;
  market?: string;
}

export interface TdxDataResponse {
  code?: string;
  market?: string;
  data?: Record<string, any>[];
  total_records?: number;
}

export interface TdxExportRequest {
  stock_code?: string;
  market?: string;
  output_format?: string;
}

export interface TdxHealthResponse {
  status?: string;
  tdx_connected?: boolean;
  timestamp?: string;
  server_info?: Record<string, any> | null;
}

export interface TechnicalIndicatorQueryModel {
  symbol?: string;
  indicators?: string[];
  period?: number | null;
  start_date?: string | null;
  end_date?: string | null;
}

export interface TimestampField {
  timestamp?: string;
}

export interface TopETFItem {
  symbol?: string;
  name?: string;
  latest_price?: number;
  change_percent?: number;
  volume?: number;
}

export interface TradeHistoryItem {
  trade_id?: string;
  order_id?: string;
  symbol?: string;
  direction?: string;
  price?: number;
  quantity?: number;
  amount?: number;
  commission?: number;
  trade_time?: string;
  trade_type?: string;
}

export interface TradeHistoryRequest {
  start_date?: string | null;
  end_date?: string | null;
  symbol?: string | null;
  page?: number;
  page_size?: number;
}

export interface TradeHistoryResponse {
  trades?: TradeHistoryItem[];
  total_count?: number;
  total_amount?: number;
  total_commission?: number;
  page?: number;
  page_size?: number;
}

export interface TradeOrderModel {
  symbol?: string;
  order_type?: string;
  price?: number;
  quantity?: number;
  order_validity?: string | null;
}

export interface TradeRecord {
  trade_id?: number;
  symbol?: string;
  trade_date?: string;
  action?: string;
  price?: number;
  quantity?: number;
  amount?: number;
  commission?: number;
  profit_loss?: number | null;
}

export interface UserPermissions {
  canTrade?: boolean;
  canWithdraw?: boolean;
  canUseStrategies?: boolean;
  canAccessAdvancedFeatures?: boolean;
  canViewMarketData?: boolean;
  canExportData?: boolean;
  canManageUsers?: boolean;
  canViewAnalytics?: boolean;
  maxStrategies?: number;
  maxWatchlists?: number;
  maxApiCalls?: number;
}

export interface UserPreferences {
  theme?: string;
  language?: string;
  timezone?: string;
  dateFormat?: string;
  timeFormat?: string;
  defaultDashboard?: string;
  watchlistLayout?: string;
  chartSettings?: Record<string, any>;
  notifications?: Record<string, boolean>;
  privacy?: Record<string, any>;
}

export interface UserProfileResponse {
  userId?: string;
  username?: string;
  email?: string;
  displayName?: string | null;
  avatar?: string | null;
  role?: string;
  status?: string;
  preferences?: UserPreferences;
  permissions?: UserPermissions;
  subscription?: SubscriptionInfo;
  statistics?: UserStatistics;
  createdAt?: string;
  lastLoginAt?: string;
  lastUpdateAt?: string;
}

export interface UserStatistics {
  totalTrades?: number;
  winningTrades?: number;
  losingTrades?: number;
  winRate?: number;
  totalPnL?: number;
  totalPnLPercent?: number;
  averageReturn?: number;
  sharpeRatio?: number;
  maxDrawdown?: number;
  totalCommission?: number;
  joinDate?: string;
  activeStrategies?: number;
  activeWatchlists?: number;
  followers?: number;
  following?: number;
}

export interface VaRCVaRRequest {
  entity_type?: string;
  entity_id?: number;
  confidence_level?: number;
}

export interface VaRCVaRResult {
  var_95_hist?: number | null;
  var_95_param?: number | null;
  var_99_hist?: number | null;
  cvar_95?: number | null;
  cvar_99?: number | null;
  entity_type?: string | null;
  entity_id?: number | null;
  confidence_level?: number | null;
}

export interface VolumeField {
  volume?: number;
}

export interface WatchlistItem {
  symbol?: string;
  name?: string | null;
  current_price?: number | null;
  change_percent?: number | null;
  note?: string | null;
  added_at?: string | null;
}

export interface WatchlistResponse {
  id?: string;
  name?: string;
  description?: string | null;
  isDefault?: boolean;
  isPublic?: boolean;
  owner?: Record<string, string>;
  stocks?: WatchlistStockResponse[];
  statistics?: Record<string, any>;
  tags?: string[];
  createdAt?: string;
  updatedAt?: string;
  lastViewedAt?: string | null;
  sortOrder?: number;
}

export interface WatchlistStockResponse {
  symbol?: string;
  name?: string;
  market?: string;
  currentPrice?: number;
  changeAmount?: number;
  changePercent?: number;
  volume?: number;
  marketCap?: number;
  pe?: number | null;
  pb?: number | null;
  addedAt?: string;
  notes?: string | null;
  alerts?: Record<string, any>[];
  customFields?: Record<string, any> | null;
}

export interface WatchlistSummary {
  total_count?: number;
  items?: WatchlistItem[];
  avg_change_percent?: number | null;
}

export type WebSocketErrorCode = 'AUTH_REQUIRED' | 'AUTH_FAILED' | 'AUTH_TOKEN_EXPIRED' | 'INVALID_MESSAGE_FORMAT' | 'INVALID_ACTION' | 'INVALID_SYMBOL' | 'INVALID_PARAMETERS' | 'PERMISSION_DENIED' | 'RATE_LIMIT_EXCEEDED' | 'ROOM_NOT_FOUND' | 'SUBSCRIPTION_FAILED' | 'ALREADY_SUBSCRIBED' | 'INTERNAL_ERROR' | 'SERVICE_UNAVAILABLE' | 'TIMEOUT';

export interface WebSocketErrorMessage {
  type?: WebSocketMessageType;
  request_id?: string | null;
  error_code?: string;
  error_message?: string;
  error_details?: Record<string, any> | null;
  timestamp?: number;
  trace_id?: string | null;
}

export interface WebSocketHeartbeatMessage {
  type?: WebSocketMessageType;
  timestamp?: number;
  server_time?: number | null;
}

export type WebSocketMessageType = 'request' | 'subscribe' | 'unsubscribe' | 'ping' | 'response' | 'error' | 'notification' | 'pong';

export interface WebSocketNotificationMessage {
  type?: WebSocketMessageType;
  room?: string;
  event?: string;
  data?: any;
  timestamp?: number;
  server_time?: number;
}

export interface WebSocketRequestMessage {
  type?: WebSocketMessageType;
  request_id?: string;
  action?: string;
  payload?: Record<string, any>;
  user_id?: string | null;
  timestamp?: number;
  trace_id?: string | null;
}

export interface WebSocketResponseMessage {
  type?: WebSocketMessageType;
  request_id?: string;
  success?: boolean;
  data?: any;
  timestamp?: number;
  server_time?: number;
  trace_id?: string | null;
}

export interface WebSocketSubscribeMessage {
  type?: WebSocketMessageType;
  request_id?: string;
  room?: string;
  user_id?: string | null;
  timestamp?: number;
}

export interface WencaiCustomQueryRequest {
  query_text?: string;
  pages?: number;
}

export interface WencaiCustomQueryResponse {
  success?: boolean;
  message?: string;
  query_text?: string;
  total_records?: number;
  results?: Record<string, any>[];
  columns?: string[];
  fetch_time?: string;
}

export interface WencaiErrorResponse {
  success?: boolean;
  error?: string;
  message?: string;
  details?: Record<string, any> | null;
}

export interface WencaiHistoryItem {
  date?: string;
  total_records?: number;
  fetch_count?: number;
}

export interface WencaiHistoryResponse {
  query_name?: string;
  date_range?: string[];
  history?: WencaiHistoryItem[];
  total_days?: number;
}

export interface WencaiQueryInfo {
  id?: number;
  query_name?: string;
  query_text?: string;
  description?: string | null;
  is_active?: boolean;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface WencaiQueryListResponse {
  queries?: WencaiQueryInfo[];
  total?: number;
}

export interface WencaiQueryRequest {
  query_name?: string;
  pages?: number;
}

export interface WencaiQueryResponse {
  success?: boolean;
  message?: string;
  query_name?: string;
  total_records?: number;
  new_records?: number;
  duplicate_records?: number;
  table_name?: string;
  fetch_time?: string;
}

export interface WencaiRefreshRequest {
  pages?: number;
  force?: boolean;
}

export interface WencaiRefreshResponse {
  status?: string;
  message?: string;
  task_id?: string | null;
  query_name?: string;
}

export interface WencaiResultItem {
  data?: Record<string, any>;
  fetch_time?: string;
}

export interface WencaiResultsResponse {
  query_name?: string;
  total?: number;
  results?: Record<string, any>[];
  columns?: string[];
  latest_fetch_time?: string | null;
}

export interface WencaiStatsResponse {
  total_queries?: number;
  active_queries?: number;
  total_records?: number;
  last_refresh_time?: string | null;
}
