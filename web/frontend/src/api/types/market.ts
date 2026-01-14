// Auto-generated types for market domain
// Generated at: 2026-01-14T14:57:47.574905

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

// ViewModel types for frontend adapters
// Redefine MarketOverviewVM to match adapter usage (camelCase fields)
export interface MarketOverviewVM {
  marketStats?: {
    totalStocks?: number;
    risingStocks?: number;
    fallingStocks?: number;
    avgChangePercent?: number;
  };
  topEtfs?: Array<{
    symbol?: string;
    name?: string;
    latestPrice?: number;
    changePercent?: number;
    volume?: number;
  }>;
  chipRaces?: ChipRaceItem[];
  longHuBang?: LongHuBangItem[];
  lastUpdate?: Date;
  marketIndex?: any;
}
export type MarketOverviewData = MarketOverview;

export interface FundFlowChartPoint {
  date?: string;
  net_inflow?: number;
  main_inflow?: number;
  retail_inflow?: number;
  mainInflow?: number;
  mainOutflow?: number;
  netInflow?: number;
  timestamp?: number;
}

export interface KLineChartData {
  symbol?: string;
  period?: string;
  data?: Array<{
    timestamp?: number;
    open?: number;
    high?: number;
    low?: number;
    close?: number;
    volume?: number;
  }>;
  categoryData?: string[];
  values?: number[][];
  volumes?: number[];
}

export interface ChipRaceItem {
  rank?: number;
  name?: string;
  net_buy?: number;
  net_sell?: number;
  net_amount?: number;
  symbol?: string;
  raceAmount?: number;
  changePercent?: number;
}

export interface LongHuBangItem {
  date?: string;
  dragon?: string; // 涨停（龙）
  tiger?: string; // 跌停（虎）
  symbol?: string;
  netAmount?: number;
  reason?: string;
}
