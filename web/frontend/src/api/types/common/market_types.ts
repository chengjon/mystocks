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

