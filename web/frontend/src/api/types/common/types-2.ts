
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
  detail_data?: Dict | null;
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
  total_count?: number;
  categories?: Record<string, number>;
  indicators?: IndicatorInfo[];
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
  indicator_type?: string;
  params?: Record<string, any> | null;
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
  code?: string;
  period?: string;
  data?: KlineCandle[];
  count?: number;
  symbol?: string;
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

export interface MarketIndexItem {
  symbol?: string;
  name?: string;
  current_price?: number;
  change_percent?: number;
  volume?: number | null;
  turnover?: number | null;
  update_time?: string | null;
}

export interface MarketOverview {
  indices?: MarketIndexItem[];
  up_count?: number;
  down_count?: number;
  flat_count?: number;
  total_volume?: number | null;
  total_turnover?: number | null;
  top_gainers?: Record<string, any>[];
  top_losers?: Record<string, any>[];
  most_active?: Record<string, any>[];
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

