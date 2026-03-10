
import type { MarketIndex } from './types-1.ts'

/**
 * Individual sector heatmap item
 */
export interface SectorHeatmapItem {
  sector_code: string;
  sector_name: string;
  sector_full_name?: string;

  // Performance data
  change_percent: number;
  volume_ratio: number;
  turnover_rate: number;
  market_cap: number;

  // Heatmap visualization
  color_intensity: number;  // 0-1 for color scaling
  color_hue: 'red' | 'green' | 'yellow' | 'neutral';

  // Position in heatmap
  row: number;
  col: number;

  // Drill-down data
  sub_sectors?: SubSectorHeatmapItem[];
  leading_stocks?: Array<{
    code: string;
    name: string;
    change_percent: number;
    contribution: number; // to sector performance
  }>;
}

/**
 * Sub-sector heatmap item
 */
export interface SubSectorHeatmapItem {
  code: string;
  name: string;
  change_percent: number;
  market_cap: number;
  color_intensity: number;
  color_hue: 'red' | 'green' | 'yellow' | 'neutral';
}

/**
 * Heatmap chart configuration
 */
export interface HeatmapConfig {
  // Layout options
  layout: 'grid' | 'tree' | 'circle' | 'treemap';
  color_scheme: 'red_green' | 'blue_red' | 'cool_warm' | 'custom';

  // Data options
  data_source: 'realtime' | 'daily' | 'weekly';
  sort_by: 'change_percent' | 'volume' | 'market_cap' | 'alphabetical';

  // Size options
  size_by: 'market_cap' | 'volume' | 'fixed';

  // Interaction options
  enable_drilldown: boolean;
  show_tooltips: boolean;
  clickable_sectors: boolean;
  enable_zoom: boolean;

  // Filter options
  min_market_cap?: number;
  max_market_cap?: number;
  min_volume?: number;
  include_st?: boolean;

  // Animation options
  enable_animation: boolean;
  animation_duration: number;
}

/**
 * Real-time stock quote
 */
export interface RealtimeQuote {
  symbol: string;
  name: string;
  full_name?: string;

  // Real-time prices
  current_price: number;
  change_amount: number;
  change_percent: number;

  // Trading data
  volume: number;
  amount: number;
  turnover_rate: number;

  // Price ranges
  open: number;
  high: number;
  low: number;
  close: number;
  prev_close: number;

  // Order book (simplified)
  bid_price?: number;
  bid_volume?: number;
  ask_price?: number;
  ask_volume?: number;

  // Market data
  market: string;
  sector?: string;
  industry?: string;
  market_cap?: number;
  pe_ratio?: number;
  pb_ratio?: number;

  // Status flags
  is_suspended?: boolean;
  is_st?: boolean;  // Special treatment
  limit_up?: boolean;
  limit_down?: boolean;

  // Timing
  timestamp: string;
  trade_time: string;
  update_time: string;
}

/**
 * Real-time quotes response
 */
export interface RealtimeQuotesResponse {
  quotes: RealtimeQuote[];
  total: number;
  page: number;
  page_size: number;

  // Market summary
  market_stats: {
    total_stocks: number;
    trading_stocks: number;
    up_stocks: number;
    down_stocks: number;
    flat_stocks: number;
    limit_up_stocks: number;
    limit_down_stocks: number;
  };

  // Turnover summary
  turnover_stats: {
    total_amount: number;
    total_volume: number;
    avg_turnover_rate: number;
  };

  // Update information
  last_update: string;
  data_source: string;
  update_frequency: string;
}

/**
 * Market depth data
 */
export interface MarketDepth {
  symbol: string;
  name?: string;
  timestamp: string;

  // Bid side (买盘)
  bids: OrderBookLevel[];

  // Ask side (卖盘)
  asks: OrderBookLevel[];

  // Spread analysis
  spread: {
    best_bid: number;
    best_ask: number;
    spread_amount: number;
    spread_percent: number;
  };

  // Depth summary
  summary: {
    bid_volume_total: number;
    ask_volume_total: number;
    bid_orders_total: number;
    ask_orders_total: number;
  };
}

/**
 * Order book level
 */
export interface OrderBookLevel {
  price: number;
  volume: number;
  orders: number;
  amount: number; // price * volume
}

/**
 * Recent trade record
 */
export interface RecentTrade {
  trade_id: string;
  symbol: string;
  timestamp: string;
  price: number;
  volume: number;
  amount: number;
  direction: 'buy' | 'sell' | 'neutral';
  trade_type?: 'auction' | 'continuous' | 'block';
}

/**
 * Market snapshot
 */
export interface MarketSnapshot {
  market: string;
  timestamp: string;
  last_update: string;

  // Index snapshots
  indices: MarketIndex[];

  // Sector statistics
  sectors: Array<{
    sector_code: string;
    sector_name: string;
    total_stocks: number;
    up_stocks: number;
    down_stocks: number;
    flat_stocks: number;
    avg_change_percent: number;
    total_volume: number;
    total_amount: number;
  }>;

  // Limit up/down statistics
  limit_stats: {
    limit_up_count: number;
    limit_down_count: number;
    limit_up_amount: number;
    limit_down_amount: number;
  };

  // Market-wide statistics
  market_stats: {
    total_amount: number;
    total_volume: number;
    avg_price: number;
    pe_ratio_avg?: number;
    turnover_rate_avg: number;
  };

  // Market health indicators
  health_indicators: {
    market_breadth: number;
    advance_decline_ratio: number;
    up_down_ratio: number;
    new_highs_new_lows_ratio: number;
  };
}
