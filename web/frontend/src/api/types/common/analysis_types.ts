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

export interface KDJParams {
  n?: number;
  m1?: number;
  m2?: number;
}

export interface MACDParams {
  fast_period?: number;
  slow_period?: number;
  signal_period?: number;
}

export interface RSIParams {
  period?: number;
}

export interface TechnicalIndicatorQueryModel {
  symbol?: string;
  indicators?: string[];
  period?: number | null;
  start_date?: string | null;
  end_date?: string | null;
}

export interface VolumeField {
  volume?: number;
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

