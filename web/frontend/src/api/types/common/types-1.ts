
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
  alert_details?: Dict | null;
  snapshot_data?: Dict | null;
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
  parameters?: Dict;
  trigger_conditions?: Dict;
  notification_config?: Dict;
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
  parameters?: Dict;
  trigger_conditions?: Dict;
  notification_config?: Dict;
  is_active?: boolean;
  priority?: number;
  created_at?: string;
  updated_at?: string;
}

export type AlertRuleType = 'price_change' | 'volume_surge' | 'technical_break' | 'limit_up' | 'limit_down' | 'dragon_tiger';

export interface AlertRuleUpdate {
  rule_name?: string | null;
  description?: string | null;
  parameters?: Dict | null;
  trigger_conditions?: Dict | null;
  notification_config?: Dict | null;
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
  total_return?: number;
  annualized_return?: number;
  max_drawdown?: number;
  sharpe_ratio?: number;
  win_rate?: number;
  total_trades?: number;
  backtest_id?: number;
  strategy_id?: number;
  strategy_name?: string;
  symbols?: string[];
  date_range?: string;
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

