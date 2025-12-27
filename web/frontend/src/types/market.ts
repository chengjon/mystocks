/**
 * Market Data Type Definitions
 *
 * 完整的市场数据类型定义，包括：
 * - 股票基础数据 (StockData)
 * - K线数据 (KLineData, OHLCV)
 * - 实时行情数据
 * - 市场概览数据
 * - 资金流向数据
 *
 * @module types/market
 */

// ============================================
// 基础类型定义
// ============================================

/**
 * A股市场颜色类型（红涨绿跌）
 */
export type MarketColorType = 'up' | 'down' | 'flat';

/**
 * 交易状态
 */
export type TradingStatus = 'trading' | 'suspended' | 'delisted' | 'pre-ipo';

/**
 * 市场板块
 */
export type MarketSector =
  | 'main' // 主板
  | 'chi-next'; // 创业板

/**
 * 股票列表（A股市场）
 */
export type StockList =
  | 'main-board' // 主板
  | 'chi-next'; // 创业板

/**
 * 时间周期
 */
export type TimePeriod =
  | '1m'
  | '5m'
  | '15m'
  | '30m'
  | '1h'
  | '4h'
  | '1d'
  | '1w'
  | '1M';

// ============================================
// 股票基础数据 (StockData)
// ============================================

/**
 * 股票基础信息
 */
export interface StockInfo {
  /** 股票代码 */
  symbol: string;

  /** 股票名称 */
  name: string;

  /** 市场板块 */
  sector: MarketSector;

  /** 所属列表 */
  list: StockList;

  /** 上市日期 */
  listDate: string;

  /** 总股本（万股） */
  totalShares: number;

  /** 流通股本（万股） */
  floatShares: number;

  /** 行业分类 */
  industry?: string;

  /** 概念标签 */
  tags?: string[];
}

/**
 * 股票实时价格数据
 */
export interface StockPrice {
  /** 股票代码 */
  symbol: string;

  /** 最新价 */
  price: number;

  /** 涨跌额 */
  change: number;

  /** 涨跌幅（%） */
  changePercent: number;

  /** 今开价 */
  open: number;

  /** 最高价 */
  high: number;

  /** 最低价 */
  low: number;

  /** 昨收价 */
  preClose: number;

  /** 成交量（手） */
  volume: number;

  /** 成交额（元） */
  amount: number;

  /** 市场状态 */
  status: TradingStatus;

  /** 时间戳 */
  timestamp: string;

  /** 涨跌颜色类型 */
  colorType: MarketColorType;
}

/**
 * 股票深度数据（五档行情）
 */
export interface StockDepth {
  /** 股票代码 */
  symbol: string;

  /** 买盘五档 */
  bids: DepthLevel[];

  /** 卖盘五档 */
  asks: DepthLevel[];

  /** 时间戳 */
  timestamp: string;
}

/**
 * 深度档位
 */
export interface DepthLevel {
  /** 价格 */
  price: number;

  /** 数量（手） */
  volume: number;
}

/**
 * 完整股票数据（StockData 主类型）
 */
export interface StockData {
  /** 股票基础信息 */
  info: StockInfo;

  /** 实时价格 */
  price: StockPrice;

  /** 深度数据 */
  depth?: StockDepth;

  /** 市场统计 */
  stats?: StockStats;
}

/**
 * 股票统计数据
 */
export interface StockStats {
  /** 市盈率（动态） */
  peDynamics: number;

  /** 市净率 */
  pb: number;

  /** 总市值（万元） */
  totalMarketCap: number;

  /** 流通市值（万元） */
  floatMarketCap: number;

  /** 换手率（%） */
  turnoverRate: number;

  /** 量比 */
  volumeRatio: number;
}

// ============================================
// K线数据 (KLineData, OHLCV)
// ============================================

/**
 * OHLCV 数据点（标准K线数据）
 */
export interface OHLCV {
  /** 日期时间 */
  datetime: string;

  /** 开盘价 */
  open: number;

  /** 最高价 */
  high: number;

  /** 最低价 */
  low: number;

  /** 收盘价 */
  close: number;

  /** 成交量 */
  volume: number;

  /** 成交额 */
  amount?: number;

  /** 持仓量（期货用） */
  openInterest?: number;
}

/**
 * K线蜡烛数据
 */
export interface KLineCandle extends OHLCV {
  /** 涨跌颜色类型 */
  colorType: MarketColorType;

  /** 涨跌幅 */
  changePercent?: number;
}

/**
 * K线数据响应（主类型）
 */
export interface KLineData {
  /** 股票代码 */
  symbol: string;

  /** 时间周期 */
  interval: TimePeriod;

  /** K线数据数组 */
  data: KLineCandle[];

  /** 起始日期 */
  startDate: string;

  /** 结束日期 */
  endDate: string;

  /** 数据总数 */
  total: number;

  /** 是否有更多数据 */
  hasMore: boolean;
}

/**
 * K线数据查询参数
 */
export interface KLineQuery {
  /** 股票代码 */
  symbol: string;

  /** 时间周期 */
  interval: TimePeriod;

  /** 起始日期 */
  startDate: string;

  /** 结束日期 */
  endDate: string;

  /** 数据限制 */
  limit?: number;
}

// ============================================
// 实时行情数据
// ============================================

/**
 * 实时行情快照
 */
export interface RealtimeQuote {
  /** 股票代码 */
  symbol: string;

  /** 最新价 */
  price: number;

  /** 涨跌幅 */
  changePercent: number;

  /** 成交量 */
  volume: number;

  /** 时间戳 */
  timestamp: number;

  /** 延迟（毫秒） */
  delay: number;
}

/**
 * 批量实时行情
 */
export interface BatchRealtimeQuotes {
  /** 行情数据数组 */
  quotes: RealtimeQuote[];

  /** 更新时间 */
  updateTime: string;
}

// ============================================
// 市场概览数据
// ============================================

/**
 * 市场统计数据
 */
export interface MarketStats {
  /** 总股票数 */
  totalStocks: number;

  /** 上涨股票数 */
  risingStocks: number;

  /** 下跌股票数 */
  fallingStocks: number;

  /** 平盘股票数 */
  flatStocks: number;

  /** 平均涨跌幅（%） */
  avgChangePercent: number;

  /** 涨停板数 */
  limitUpCount: number;

  /** 跌停板数 */
  limitDownCount: number;
}

/**
 * 指数数据
 */
export interface IndexData {
  /** 指数代码 */
  code: string;

  /** 指数名称 */
  name: string;

  /** 最新点位 */
  value: number;

  /** 涨跌点数 */
  change: number;

  /** 涨跌幅（%） */
  changePercent: number;

  /** 成交额（亿元） */
  amount: number;

  /** 时间戳 */
  timestamp: string;
}

/**
 * 热门股票项
 */
export interface HotStockItem {
  /** 股票代码 */
  symbol: string;

  /** 股票名称 */
  name: string;

  /** 最新价 */
  price: number;

  /** 涨跌幅（%） */
  changePercent: number;

  /** 成交量 */
  volume: number;

  /** 换手率（%） */
  turnoverRate: number;
}

/**
 * 市场概览数据
 */
export interface MarketOverview {
  /** 市场统计 */
  stats: MarketStats;

  /** 主要指数 */
  indices: IndexData[];

  /** 热门股票 */
  hotStocks: HotStockItem[];

  /** 更新时间 */
  timestamp: string;
}

// ============================================
// 资金流向数据
// ============================================

/**
 * 资金流向数据点
 */
export interface FundFlowItem {
  /** 日期 */
  date: string;

  /** 主力流入（万元） */
  mainInflow: number;

  /** 主力流出（万元） */
  mainOutflow: number;

  /** 净流入（万元） */
  netInflow: number;

  /** 净流入占比（%） */
  netInflowRatio?: number;
}

/**
 * 资金流向数据响应
 */
export interface FundFlowData {
  /** 股票代码 */
  symbol: string;

  /** 资金流向数据 */
  data: FundFlowItem[];

  /** 数据总数 */
  total: number;

  /** 起始日期 */
  startDate: string;

  /** 结束日期 */
  endDate: string;
}

// ============================================
// 类型守卫和工具函数
// ============================================

/**
 * 判断是否为上涨
 */
export function isUp(colorType: MarketColorType): boolean {
  return colorType === 'up';
}

/**
 * 判断是否为下跌
 */
export function isDown(colorType: MarketColorType): boolean {
  return colorType === 'down';
}

/**
 * 判断是否为平盘
 */
export function isFlat(colorType: MarketColorType): boolean {
  return colorType === 'flat';
}

/**
 * 计算市场颜色类型
 */
export function calculateColorType(changePercent: number): MarketColorType {
  if (changePercent > 0) return 'up';
  if (changePercent < 0) return 'down';
  return 'flat';
}

/**
 * 格式化K线数据为图表格式
 */
export function formatKLineForChart(kline: KLineData): {
  categoryData: string[];
  values: number[][];
  volumes: number[];
} {
  return {
    categoryData: kline.data.map((candle) => candle.datetime),
    values: kline.data.map((candle) => [
      candle.open,
      candle.close,
      candle.low,
      candle.high,
    ]),
    volumes: kline.data.map((candle) => candle.volume),
  };
}
