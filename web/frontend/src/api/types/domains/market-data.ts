import { Dict } from './system-base';

export interface OHLCVData {
  dates?: string[];
  open?: number[];
  high?: number[];
  low?: number[];
  close?: number[];
  volume?: number[];
  turnover?: number[];
}

export interface StockInfo {
  symbol?: string;
  name?: string | null;
  latest_price?: number | null;
  change_percent?: number | null;
  volume?: number | null;
  amount?: number | null;
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
  data?: Record<string, unknown>;
  timestamp?: string;
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
  data?: Record<string, unknown>;
  timestamp?: string;
}

export interface IndustryPerformanceResponse {
  success?: boolean;
  data?: Record<string, unknown>;
  timestamp?: string;
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

export interface IndicatorSpec {
  indicator_type?: string;
  params?: Record<string, unknown> | null;
  abbreviation?: string;
  parameters?: Record<string, unknown>;
}

export interface IndicatorResult {
  abbreviation?: string;
  parameters?: Record<string, unknown>;
  outputs?: IndicatorValueOutput[];
  panel_type?: string;
  reference_lines?: number[] | null;
  error?: string | null;
}

export interface IndicatorValueOutput {
  output_name?: string;
  values?: number | null[];
  display_name?: string;
}

export interface IndicatorInfo {
  indicator_type?: string;
  indicator_name?: string;
  category?: string;
  description?: string;
  default_params?: Record<string, unknown>;
  output_fields?: string[];
}

export interface IndicatorMetadata {
  abbreviation?: string;
  full_name?: string;
  chinese_name?: string;
  category?: string;
  description?: string;
  panel_type?: string;
  parameters?: Record<string, unknown>[];
  outputs?: Record<string, string>[];
  reference_lines?: number[] | null;
  min_data_points_formula?: string;
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

export interface TechnicalIndicatorQueryModel {
  symbol?: string;
  indicators?: string[];
  period?: number | null;
  start_date?: string | null;
  end_date?: string | null;
}

export interface MarketOverview {
  indices?: MarketIndexItem[];
  up_count?: number;
  down_count?: number;
  flat_count?: number;
  total_volume?: number | null;
  total_turnover?: number | null;
  top_gainers?: Record<string, unknown>[];
  top_losers?: Record<string, unknown>[];
  most_active?: Record<string, unknown>[];
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

export interface MarketOverviewStats {
  total_stocks?: number;
  rising_stocks?: number;
  falling_stocks?: number;
  avg_change_percent?: number;
}

export interface LongHuBangItem {
  symbol?: string;
  name?: string;
  net_amount?: number;
  reason?: string | null;
}

export interface ChipRaceItem {
  symbol?: string;
  name?: string;
  race_amount?: number;
  change_percent?: number;
}

export interface TopETFItem {
  symbol?: string;
  name?: string;
  latest_price?: number;
  change_percent?: number;
  volume?: number;
}

export interface MarketOverviewDetailedResponse {
  market_stats?: MarketOverviewStats;
  top_etfs?: TopETFItem[];
  chip_races?: ChipRaceItem[];
  long_hu_bang?: LongHuBangItem[];
  timestamp?: string;
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

export interface HeatmapStock {
  symbol?: string;
  name?: string;
  change_percent?: number;
  market_cap?: number | null;
}

export interface HeatmapResponse {
  sector?: string;
  stocks?: HeatmapStock[];
  avg_change?: number;
}

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
  keywords?: unknown[];
  importance_level?: number;
  data_source?: string;
  source_id?: string | null;
  sentiment?: string | null;
  impact_score?: number | null;
}

export interface AnnouncementStatsResponse {
  total_count?: number;
  today_count?: number;
  important_count?: number;
  by_source?: Record<string, unknown>;
  by_type?: Record<string, unknown>;
  by_sentiment?: Record<string, unknown>;
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

export interface FundFlowItem {
  trade_date?: string;
  main_net_inflow?: number;
  main_net_inflow_rate?: number;
  super_large_net_inflow?: number;
  large_net_inflow?: number;
  medium_net_inflow?: number;
  small_net_inflow?: number;
}

export interface FundFlowDataResponse {
  fund_flow?: FundFlowItem[];
  total?: number;
  symbol?: string | null;
  timeframe?: string | null;
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
  detail_data?: Dict | null;
  impact_score?: number | null;
}

export interface StockListResponse {
  success?: boolean;
  data?: Record<string, unknown>;
  timestamp?: string;
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
