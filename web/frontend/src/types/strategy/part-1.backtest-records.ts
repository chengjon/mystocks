/**
 * 交易记录
 */
export interface TradeRecord {
  /** 交易ID */
  id: string;

  /** 股票代码 */
  symbol: string;

  /** 交易方向 */
  direction: 'buy' | 'sell';

  /** 交易价格（元） */
  price: number;

  /** 交易数量（股） */
  quantity: number;

  /** 交易金额（元） */
  amount: number;

  /** 交易手续费（元） */
  commission: number;

  /** 交易时间 */
  timestamp: string;

  /** 盈亏（元，仅平仓时） */
  profitLoss?: number;
}

/**
 * 持仓记录
 */
export interface PositionRecord {
  /** 持仓ID */
  id: string;

  /** 股票代码 */
  symbol: string;

  /** 持仓数量（股） */
  quantity: number;

  /** 开仓价（元） */
  openPrice: number;

  /** 当前价（元） */
  currentPrice: number;

  /** 市值（元） */
  marketValue: number;

  /** 浮动盈亏（元） */
  profitLoss: number;

  /** 盈亏比例（%） */
  profitLossPercent: number;

  /** 开仓时间 */
  openedAt: string;

  /** 平仓时间（如果已平仓） */
  closedAt?: string;
}

/**
 * 权益曲线点
 */
export interface EquityCurvePoint {
  /** 时间戳 */
  timestamp: string;

  /** 权益值（元） */
  equity: number;

  /** 收益率（%） */
  return: number;
}
