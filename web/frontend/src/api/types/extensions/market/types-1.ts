
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

