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
  industry_name?: string;
  performance?: number;
  rank?: number;
}

export interface IndexQuote {
  symbol?: string;
  name?: string;
  price?: number;
  change?: number;
  change_percent?: number;
  volume?: number | null;
  amount?: number | null;
  updated_at?: string | null;
}

export interface IndexQuoteResponse {
  success?: boolean;
  data?: IndexQuote[];
  timestamp?: string;
}

export interface KLineCandleV2 {
  timestamp?: string;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  volume?: number;
  amount?: number | null;
}

export interface KLineRequestV2 {
  symbol?: string;
  period?: string;
  adjust?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  limit?: number;
}

export interface KLineResponseV2 {
  symbol?: string;
  period?: string;
  candles?: KLineCandleV2[];
  total?: number;
}

export interface KlineCandle {
  date?: string;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  volume?: number;
  amount?: number | null;
}

export interface KlineDataPoint {
  timestamp?: string;
  value?: number;
}

export interface KlineRequest {
  symbol?: string;
  period?: string;
  start_date?: string | null;
  end_date?: string | null;
}

export interface KlineResponse {
  success?: boolean;
  data?: KlineCandle[];
  points?: KlineDataPoint[];
  timestamp?: string;
}

export interface IndicatorSpec {
  name?: string;
  params?: Record<string, unknown>;
  output?: string[] | null;
}

export interface IndicatorResult {
  name?: string;
  values?: Record<string, number[] | null>;
  meta?: Record<string, unknown> | null;
}

export interface IndicatorValueOutput {
  key?: string;
  label?: string;
  values?: Array<number | null>;
}

export interface IndicatorInfo {
  name?: string;
  display_name?: string;
  category?: string;
  description?: string | null;
  default_params?: Record<string, unknown> | null;
  outputs?: IndicatorValueOutput[];
}

export interface IndicatorMetadata {
  total?: number;
  categories?: string[];
  supported_periods?: string[];
}

export interface IndicatorCalculateRequest {
  symbol?: string;
  indicators?: IndicatorSpec[];
  period?: string;
  start_date?: string | null;
  end_date?: string | null;
}

export interface IndicatorCalculateResponse {
  success?: boolean;
  symbol?: string;
  period?: string;
  results?: IndicatorResult[];
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
