/**
 * Market Domain Types
 *
 * Type definitions for market data, charts, and trading information display.
 * These types are frontend-specific ViewModel types for market visualization
 * and trading interfaces that complement auto-generated market types.
 */

// ========== Market Overview Types ==========

/**
 * Market overview ViewModel for dashboard display
 */
export interface MarketOverviewVM {
  // Market status indicators
  market_status: 'bull' | 'bear' | 'sideways' | 'volatile' | 'panic';
  market_phase: 'accumulation' | 'markup' | 'distribution' | 'markdown';

  // Key market indices
  indices: {
    shanghai: MarketIndex;
    shenzhen: MarketIndex;
    chiNext: MarketIndex;
    startBoard?: MarketIndex;
    totalMarket?: MarketIndex;
  };

  // Market sentiment indicators
  sentiment: {
    advance_decline_ratio: number;
    up_down_volume_ratio: number;
    new_highs_new_lows_ratio: number;
    put_call_ratio?: number;
    vix_index?: number;
  };

  // Turnover and liquidity
  turnover: {
    total_value: number;
    total_volume: number;
    average_price: number;
    turnover_rate: number;
  };

  // Price distribution statistics
  price_distribution: {
    up_stocks: number;
    down_stocks: number;
    flat_stocks: number;
    limit_up: number;
    limit_down: number;
    total_stocks: number;
  };

  // Sector performance ranking
  sector_performance: SectorPerformance[];

  // Hot concepts/themes
  hot_concepts: ConceptPerformance[];

  // Capital flow analysis
  capital_flow: {
    northbound: CapitalFlow;
    southbound: CapitalFlow;
    institutional: CapitalFlow;
    retail: CapitalFlow;
    foreign: CapitalFlow;
  };

  // Technical market indicators
  technical_summary: {
    market_breadth: number;        // 市场宽度
    momentum_index: number;        // 动量指标
    fear_greed_index?: number;     // 恐贪指数
    put_call_ratio?: number;       // 期权持仓比
  };

  // Market timing information
  timestamp: string;
  last_update: string;
  next_trading_day?: string;
  market_session: 'pre_open' | 'open' | 'lunch_break' | 'afternoon' | 'close' | 'after_hours';
}

// ========== Market Index Types ==========

/**
 * Individual market index data
 */
export interface MarketIndex {
  code: string;
  name: string;
  full_name?: string;

  // Real-time prices
  current_price: number;
  change_amount: number;
  change_percent: number;

  // Trading volume
  volume: number;
  amount: number;

  // Price ranges
  open: number;
  high: number;
  low: number;
  close: number;
  prev_close: number;

  // Market metrics
  pe_ratio?: number;
  pb_ratio?: number;
  turnover_rate?: number;

  // Technical indicators
  ma5?: number;
  ma10?: number;
  ma20?: number;
  ma60?: number;

  // Status flags
  is_suspended?: boolean;
  limit_up?: boolean;
  limit_down?: boolean;
}

// ========== Sector and Concept Types ==========

/**
 * Sector performance data
 */
export interface SectorPerformance {
  sector_code: string;
  sector_name: string;
  sector_full_name?: string;

  // Performance metrics
  change_percent: number;
  volume_ratio: number;
  turnover_rate: number;
  market_cap: number;

  // Price data
  current_price: number;
  change_amount: number;

  // Market position
  rank: number;
  total_sectors: number;

  // Leading stocks in this sector
  leading_stocks: Array<{
    code: string;
    name: string;
    change_percent: number;
    weight: number; // in sector
  }>;

  // Sub-sectors (if applicable)
  sub_sectors?: SubSectorData[];
}

/**
 * Concept/Theme performance data
 */
export interface ConceptPerformance {
  concept_code: string;
  concept_name: string;
  concept_description?: string;

  // Performance metrics
  change_percent: number;
  volume_ratio: number;
  hot_rank: number;

  // Related stocks
  related_stocks: Array<{
    code: string;
    name: string;
    change_percent: number;
    weight: number; // in concept
  }>;

  // Concept metadata
  sector?: string;
  tags?: string[];
  popularity_score?: number;
}

/**
 * Sub-sector data
 */
export interface SubSectorData {
  code: string;
  name: string;
  change_percent: number;
  market_cap: number;
  leading_stocks: Array<{
    code: string;
    name: string;
    change_percent: number;
  }>;
}

// ========== Capital Flow Types ==========

/**
 * Capital flow data
 */
export interface CapitalFlow {
  // Net flow amounts
  inflow: number;
  outflow: number;
  net_flow: number;

  // Flow composition
  large_orders: {
    buy: number;
    sell: number;
    net: number;
  };

  big_orders: {
    buy: number;
    sell: number;
    net: number;
  };

  medium_orders: {
    buy: number;
    sell: number;
    net: number;
  };

  small_orders: {
    buy: number;
    sell: number;
    net: number;
  };

  // Flow metrics
  net_flow_ratio: number;  // net_flow / total_volume
  large_order_ratio: number; // large_orders.net / total_flow
}

// ========== Chart and Visualization Types ==========

/**
 * K-line chart data point
 */
export interface KLineChartData {
  timestamp: string;
  date: string;
  time?: string;

  // OHLC data
  open: number;
  high: number;
  low: number;
  close: number;

  // Volume data
  volume: number;
  amount: number;

  // Technical indicators (optional)
  indicators?: {
    // Moving averages
    ma5?: number;
    ma10?: number;
    ma20?: number;
    ma30?: number;
    ma60?: number;

    // Oscillators
    rsi6?: number;
    rsi12?: number;
    rsi14?: number;

    // MACD
    macd?: {
      dif: number;
      dea: number;
      histogram: number;
    };

    // Bollinger Bands
    boll?: {
      upper: number;
      middle: number;
      lower: number;
    };

    // KDJ
    kdj?: {
      k: number;
      d: number;
      j: number;
    };

    // Williams %R
    williams_r?: number;

    // Stochastic
    stoch?: {
      k: number;
      d: number;
    };
  };

  // Trading signals (optional)
  signals?: {
    buy?: boolean;
    sell?: boolean;
    hold?: boolean;
    strength?: 'weak' | 'medium' | 'strong';
    reason?: string;
  };

  // Additional metadata
  symbol: string;
  interval: string;
  is_suspended?: boolean;
}

/**
 * K-line chart configuration
 */
export interface KLineChartConfig {
  symbol: string;
  name?: string;
  period: '1m' | '5m' | '15m' | '30m' | '1h' | '1d' | '1w' | '1M';
  start_date?: string;
  end_date?: string;

  // Chart display options
  chart_options: {
    height: number;
    width: number;
    theme: 'light' | 'dark';
    show_volume: boolean;
    show_indicators: boolean;
    enable_zoom: boolean;
    enable_crosshair: boolean;
  };

  // Indicator settings
  indicators: {
    ma: boolean;
    rsi: boolean;
    macd: boolean;
    kdj: boolean;
    boll: boolean;
    williams_r: boolean;
    stoch: boolean;
  };

  // Signal settings
  signals: {
    show_buy_signals: boolean;
    show_sell_signals: boolean;
    signal_strength_filter: 'weak' | 'medium' | 'strong' | 'all';
  };

  // Data settings
  data_settings: {
    include_pre_market: boolean;
    include_after_hours: boolean;
    adjust_for_splits: boolean;
    adjust_for_dividends: boolean;
  };
}

// ========== Capital Flow Chart Types ==========

/**
 * Capital flow chart data point
 */
export interface FundFlowChartPoint {
  date: string;
  timestamp: number;

  // Main force (large institutions)
  main_force: {
    inflow: number;
    outflow: number;
    net_flow: number;
    ratio: number; // percentage of total
  };

  // Super large orders (>400,000 yuan)
  large_orders: {
    inflow: number;
    outflow: number;
    net_flow: number;
    ratio: number;
  };

  // Large orders (200,000-400,000 yuan)
  big_orders: {
    inflow: number;
    outflow: number;
    net_flow: number;
    ratio: number;
  };

  // Medium orders (40,000-200,000 yuan)
  medium_orders: {
    inflow: number;
    outflow: number;
    net_flow: number;
    ratio: number;
  };

  // Small orders (<40,000 yuan)
  small_orders: {
    inflow: number;
    outflow: number;
    net_flow: number;
    ratio: number;
  };

  // Market totals
  total_inflow: number;
  total_outflow: number;
  total_net_flow: number;

  // Market context
  market_index_change?: number;
  sector_rotation?: string[];
}

/**
 * Capital flow chart configuration
 */
export interface FundFlowChartConfig {
  symbol?: string;
  sector?: string;
  market: 'sh' | 'sz' | 'all';

  // Time period
  period: '1d' | '5d' | '10d' | '1M' | '3M' | '6M';

  // Chart settings
  chart_type: 'line' | 'bar' | 'area' | 'stacked';

  // Display options
  show_options: {
    main_force: boolean;
    large_orders: boolean;
    big_orders: boolean;
    medium_orders: boolean;
    small_orders: boolean;
    net_flow_only: boolean;
  };

  // Analysis options
  analysis_options: {
    show_trends: boolean;
    show_anomalies: boolean;
    highlight_large_flows: boolean;
  };

  // Date range
  date_range?: {
    start: string;
    end: string;
  };
}

// ========== Heatmap Types ==========

/**
 * Market heatmap data
 */
export interface MarketHeatmapData {
  timestamp: string;
  last_update: string;

  // Sector data
  sectors: SectorHeatmapItem[];

  // Overall market statistics
  summary: {
    total_sectors: number;
    up_sectors: number;
    down_sectors: number;
    flat_sectors: number;
    avg_change_percent: number;
  };
}

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

// ========== Real-time Quote Types ==========

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

// ========== Market Depth Types ==========

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

// ========== Recent Trades Types ==========

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

// ========== Market Snapshot Types ==========

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