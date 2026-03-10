import type { IndexQuote } from './market-data-core.ts';

export interface ChipRaceRequest {
  race_type?: string;
  trade_date?: string | null;
  min_race_amount?: number | null;
  limit?: number;
}

export interface ETFDataRequest {
  symbol?: string | null;
  keyword?: string | null;
  limit?: number;
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

export interface HotSector {
  sector_name?: string;
  change_percent?: number;
  leading_stock?: string | null;
  stock_count?: number;
}

export interface LongHuBangRequest {
  symbol?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  min_net_amount?: number | null;
  limit?: number;
}

export interface MarketDataQueryModel {
  symbol?: string;
  start_date?: string;
  end_date?: string;
  interval?: string | null;
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

export interface TdxDataRequest {
  stock_code?: string;
  market?: string;
}

export interface TdxDataResponse {
  code?: string;
  market?: string;
  data?: Record<string, unknown>[];
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
  server_info?: Record<string, unknown> | null;
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
  results?: Record<string, unknown>[];
  columns?: string[];
  fetch_time?: string;
}

export interface WencaiErrorResponse {
  success?: boolean;
  error?: string;
  message?: string;
  details?: Record<string, unknown> | null;
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
  data?: Record<string, unknown>;
  fetch_time?: string;
}

export interface WencaiResultsResponse {
  query_name?: string;
  total?: number;
  results?: Record<string, unknown>[];
  columns?: string[];
  latest_fetch_time?: string | null;
}

export interface WencaiStatsResponse {
  total_queries?: number;
  active_queries?: number;
  total_records?: number;
  last_refresh_time?: string | null;
}
