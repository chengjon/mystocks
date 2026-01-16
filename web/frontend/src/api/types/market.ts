// Auto-generated types for market domain
// Generated at: 2026-01-15T21:06:03.935353

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

// ============================================
// ViewModel Types for Adapters (camelCase naming)
// ============================================

export interface MarketOverviewVM {
  indices?: MarketIndexItem[];
  upCount?: number;
  downCount?: number;
  flatCount?: number;
  totalVolume?: number | null;
  totalTurnover?: number | null;
  topGainers?: Record<string, any>[];
  topLosers?: Record<string, any>[];
  mostActive?: Record<string, any>[];
  marketStats?: Record<string, any>;
  topEtfs?: Array<{ symbol: string; name: string; latestPrice?: number; changePercent?: number; volume?: number }>;
  chipRaces?: ChipRaceItemVM[];
  longHuBang?: LongHuBangItemVM[];
  lastUpdate?: string | Date;
  marketIndex?: Record<string, any>;
}

export interface FundFlowChartPoint {
  time?: string;
  mainNetInflow?: number;
  smallNetInflow?: number;
  date?: string;
  value?: number;
  mainInflow?: number;
  mainOutflow?: number;
  netInflow?: number;
  timestamp?: number;
}

export interface KLineChartData {
  dates?: string[];
  open?: number[];
  high?: number[];
  low?: number[];
  close?: number[];
  volume?: number[];
  volumes?: number[];
  categoryData?: string[];
  values?: number[][] | number[];
}

// VM suffix to avoid conflict with common.ts types
export interface ChipRaceItemVM {
  symbol?: string;
  name?: string;
  cost?: number;
  ratio?: number;
  price?: number;
}

// VM suffix to avoid conflict with common.ts types
export interface LongHuBangItemVM {
  symbol?: string;
  name?: string;
  longAmount?: number;
  shortAmount?: number;
  netAmount?: number;
  close?: number;
  changePercent?: number;
}

// Alias for backward compatibility
export type { ChipRaceItemVM as ChipRaceItem, LongHuBangItemVM as LongHuBangItem };
