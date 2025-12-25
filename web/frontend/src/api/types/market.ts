/**
 * Market Module Type Definitions
 *
 * Types for market data, overview, fund flow, and K-line data.
 * Compatible with UnifiedResponse v2.0.0 format.
 */

// ============================================
// Market Overview Type Definitions
// ============================================

/**
 * 市场概览统计数据
 */
export interface MarketStats {
  totalStocks: number;
  risingStocks: number;
  fallingStocks: number;
  avgChangePercent: number;
}

/**
 * 热门 ETF 项
 */
export interface TopETFItem {
  symbol: string;
  name: string;
  latestPrice: number;
  changePercent: number;
  volume: number;
}

/**
 * 筹码比拼项
 */
export interface ChipRaceItem {
  symbol: string;
  name: string;
  raceAmount: number;
  changePercent: number;
}

/**
 * 龙虎榜项
 */
export interface LongHuBangItem {
  symbol: string;
  name: string;
  netAmount: number;
  reason: string;
}

/**
 * 市场概览响应
 */
export interface MarketOverviewData {
  marketStats: MarketStats;
  topEtfs: TopETFItem[];
  chipRaces: ChipRaceItem[];
  longHuBang: LongHuBangItem[];
  timestamp: string;
}

/**
 * 市场概览 ViewModel（用于前端展示）
 */
export interface MarketOverviewVM {
  marketStats: MarketStats;
  topEtfs: TopETFItem[];
  chipRaces: ChipRaceItem[];
  longHuBang: LongHuBangItem[];
  lastUpdate: Date;
}

// ============================================
// Fund Flow Type Definitions
// ============================================

/**
 * 资金流向项
 */
export interface FundFlowItem {
  date: string;
  mainInflow: number;
  mainOutflow: number;
  netInflow: number;
}

/**
 * 资金流向图表数据点
 */
export interface FundFlowChartPoint {
  date: string;
  mainInflow: number;
  mainOutflow: number;
  netInflow: number;
  timestamp: number;
}

/**
 * 资金流向响应
 */
export interface FundFlowData {
  fundFlow: FundFlowItem[];
  total: number;
  symbol: string | null;
  timeframe: string | null;
}

// ============================================
// K-Line Data Type Definitions
// ============================================

/**
 * K线蜡烛
 */
export interface KlineCandle {
  datetime: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount: number | null;
}

/**
 * K线数据点
 */
export interface KlineDataPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount: number | null;
}

/**
 * K线图表数据
 */
export interface KLineChartData {
  categoryData: string[];
  values: number[][];
  volumes: number[];
}

/**
 * K线数据响应
 */
export interface KLineData {
  symbol: string;
  interval: string;
  data: KlineCandle[];
  startDate: string;
  endDate: string;
  total: number;
}
