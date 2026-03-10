// Analysis, Indicators & Quant Research Models

import type { IndicatorInfo, IndicatorSpec } from './market-data.ts';

export interface BOLLParams {
  period?: number;
  std_dev?: number;
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

export interface EMAParams {
  period?: number;
  price_type?: string;
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
  indicators?: Record<string, unknown>[];
  created_at?: string;
  updated_at?: string;
  last_used_at?: string | null;
}

export interface IndicatorConfigUpdateRequest {
  name?: string | null;
  indicators?: IndicatorSpec[] | null;
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
  data?: Record<string, unknown>[];
  params?: Record<string, unknown>;
}

export interface IntegrityVerificationResult {
  backup_id?: string;
  is_valid?: boolean;
  verification_details?: Record<string, unknown>;
  report_file_path?: string | null;
  verification_time?: string;
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

export interface MAParams {
  period?: number;
  price_type?: string;
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

export interface OscillatorIndicatorRequest {
  symbol?: string;
  indicator_type?: string;
  params?: Record<string, unknown> | null;
  start_date?: string | null;
  end_date?: string | null;
}

export interface OscillatorIndicatorResponse {
  symbol?: string;
  indicator_type?: string;
  indicator_name?: string;
  values?: OscillatorIndicatorValue[];
  params?: Record<string, unknown>;
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
  params?: Record<string, unknown>;
  start_date?: string | null;
  end_date?: string | null;
}

export interface OverlayIndicatorResponse {
  symbol?: string;
  indicator_type?: string;
  indicator_name?: string;
  values?: OverlayIndicatorValue[];
  params?: Record<string, unknown>;
  calculated_at?: string;
}

export interface OverlayIndicatorValue {
  timestamp?: number;
  value?: number;
  upper?: number | null;
  middle?: number | null;
  lower?: number | null;
}

export interface RSIParams {
  period?: number;
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
  rating_distribution?: Record<string, unknown>;
}
