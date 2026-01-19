// Auto-generated types for market domain
// Generated at: 2026-01-19T22:34:18.299047

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
