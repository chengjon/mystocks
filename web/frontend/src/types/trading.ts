/**
 * Trading Type Definitions
 *
 * 交易类型定义，包括：
 * - A股交易规则 (ATradingRule)
 * - 交易数据 (TradeData)
 * - 订单接口 (Order)
 * - 板板类型 (主板、创业板、科创板)
 *
 * @module types/trading
 */

// ============================================
// 基础类型定义
// ============================================

/**
 * A股市场板块类型
 */
export enum BoardType {
  /** 主板 */
  MAIN = 'main',

  /** 创业板 */
  CHI_NEXT = 'chi-next',

  /** 科创板 */
  STAR = 'star',

  /** 北交所 */
  BSE = 'bse',
}

/**
 * 订单状态
 */
export enum OrderStatus {
  /** 未提交 */
  DRAFT = 'draft',

  /** 待提交 */
  PENDING = 'pending',

  /** 已提交 */
  SUBMITTED = 'submitted',

  /** 部分成交 */
  PARTIAL_FILLED = 'partial_filled',

  /** 全部成交 */
  FILLED = 'filled',

  /** 已撤销 */
  CANCELLED = 'cancelled',

  /** 拒绝 */
  REJECTED = 'rejected',

  /** 失败 */
  FAILED = 'failed',
}

/**
 * 订单方向
 */
export enum OrderDirection {
  /** 买入 */
  BUY = 'buy',

  /** 卖出 */
  SELL = 'sell',
}

/**
 * 订单类型
 */
export enum OrderType {
  /** 限价单 */
  LIMIT = 'limit',

  /** 市价单 */
  MARKET = 'market',

  /** 止损单 */
  STOP_LOSS = 'stop_loss',

  /** 止盈单 */
  TAKE_PROFIT = 'take_profit',
}

// ============================================
// A股交易规则 (ATradingRule)
// ============================================

/**
 * A股交易规则
 */
export interface ATradingRule {
  /** 交易板块 */
  board: BoardType;

  /** 最小报价单位（元） */
  minPriceUnit: number;

  /** 最小交易数量（股） */
  minTradeUnit: number;

  /** 交易单位必须是100的整数倍 */
  tradeUnitMultiple: number;

  /** T+1 交易规则 */
  tPlusOne: boolean;

  /** 涨跌停限制（%） */
  limitPercent: number;

  /** 是否有ST标记 */
  isST: boolean;

  /** ST股票涨跌停限制（%） */
  stLimitPercent: number;

  /** 是否支持融资融券 */
  marginTrading: boolean;

  /** 交易时间规则 */
  tradingHours: TradingHours;

  /** 交易费用规则 */
  fees: TradingFees;
}

/**
 * 交易时间规则
 */
export interface TradingHours {
  /** 上午交易时段 */
  morning: {
    /** 开始时间 */
    start: string; // HH:mm 格式，如 "09:30"

    /** 结束时间 */
    end: string; // HH:mm 格式，如 "11:30"
  };

  /** 下午交易时段 */
  afternoon: {
    /** 开始时间 */
    start: string; // HH:mm 格式，如 "13:00"

    /** 结束时间 */
    end: string; // HH:mm 格式，如 "15:00"
  };
}

/**
 * 交易费用规则
 */
export interface TradingFees {
  /** 印花税率（%） */
  stampDuty: number;

  /** 佣金费率（%） */
  commission: number;

  /** 最低佣金（元） */
  minCommission: number;

  /** 过户费率（%） */
  transferFee: number;

  /** 经手费率（%） */
  handlingFee: number;

  /** 监管费率（%） */
  regulatoryFee: number;
}

/**
 * 预定义交易规则
 */
export const PREDEFINED_TRADING_RULES: Record<BoardType, Omit<ATradingRule, 'board'>> = {
  [BoardType.MAIN]: {
    minPriceUnit: 0.01,
    minTradeUnit: 100,
    tradeUnitMultiple: 100,
    tPlusOne: true,
    limitPercent: 10,
    isST: false,
    stLimitPercent: 5,
    marginTrading: true,
    tradingHours: {
      morning: { start: '09:30', end: '11:30' },
      afternoon: { start: '13:00', end: '15:00' },
    },
    fees: {
      stampDuty: 0.1, // 仅卖出时收取
      commission: 0.03,
      minCommission: 5,
      transferFee: 0.001,
      handlingFee: 0.00487,
      regulatoryFee: 0.002,
    },
  },

  [BoardType.CHI_NEXT]: {
    minPriceUnit: 0.01,
    minTradeUnit: 100,
    tradeUnitMultiple: 100,
    tPlusOne: true,
    limitPercent: 20,
    isST: false,
    stLimitPercent: 10,
    marginTrading: true,
    tradingHours: {
      morning: { start: '09:30', end: '11:30' },
      afternoon: { start: '13:00', end: '15:00' },
    },
    fees: {
      stampDuty: 0.1,
      commission: 0.03,
      minCommission: 5,
      transferFee: 0.001,
      handlingFee: 0.00487,
      regulatoryFee: 0.002,
    },
  },

  [BoardType.STAR]: {
    minPriceUnit: 0.01,
    minTradeUnit: 200,
    tradeUnitMultiple: 200,
    tPlusOne: true,
    limitPercent: 20,
    isST: false,
    stLimitPercent: 10,
    marginTrading: true,
    tradingHours: {
      morning: { start: '09:30', end: '11:30' },
      afternoon: { start: '13:00', end: '15:00' },
    },
    fees: {
      stampDuty: 0.1,
      commission: 0.03,
      minCommission: 5,
      transferFee: 0.001,
      handlingFee: 0.00487,
      regulatoryFee: 0.002,
    },
  },

  [BoardType.BSE]: {
    minPriceUnit: 0.01,
    minTradeUnit: 100,
    tradeUnitMultiple: 100,
    tPlusOne: true,
    limitPercent: 30,
    isST: false,
    stLimitPercent: 10,
    marginTrading: false,
    tradingHours: {
      morning: { start: '09:30', end: '11:30' },
      afternoon: { start: '13:00', end: '15:00' },
    },
    fees: {
      stampDuty: 0.1,
      commission: 0.03,
      minCommission: 5,
      transferFee: 0.001,
      handlingFee: 0.00487,
      regulatoryFee: 0.002,
    },
  },
};

// ============================================
// 交易数据 (TradeData)
// ============================================

/**
 * 交易数据
 */
export interface TradeData {
  /** 股票代码 */
  symbol: string;

  /** 股票名称 */
  name: string;

  /** 交易板块 */
  board: BoardType;

  /** 当前价格 */
  price: number;

  /** 涨跌幅（%） */
  changePercent: number;

  /** 成交量（手） */
  volume: number;

  /** 成交额（万元） */
  amount: number;

  /** 买卖盘数据 */
  orderBook: OrderBook;

  /** 逐笔成交数据 */
  tickData: TickData[];

  /** 时间戳 */
  timestamp: string;
}

/**
 * 订单簿（五档行情）
 */
export interface OrderBook {
  /** 买盘五档 */
  bids: OrderBookLevel[];

  /** 卖盘五档 */
  asks: OrderBookLevel[];
}

/**
 * 订单簿档位
 */
export interface OrderBookLevel {
  /** 价格 */
  price: number;

  /** 数量（手） */
  volume: number;

  /** 位置（1-5） */
  position: number;
}

/**
 * 逐笔成交数据
 */
export interface TickData {
  /** 成交时间 */
  time: string;

  /** 成交价格 */
  price: number;

  /** 成交数量（手） */
  volume: number;

  /** 方向 */
  direction: 'buy' | 'sell' | 'neutral';
}

// ============================================
// 订单接口 (Order)
// ============================================

/**
 * 订单接口
 */
export interface Order {
  /** 订单ID */
  id: string;

  /** 股票代码 */
  symbol: string;

  /** 股票名称 */
  symbolName: string;

  /** 订单方向 */
  direction: OrderDirection;

  /** 订单类型 */
  type: OrderType;

  /** 订单数量（股） */
  quantity: number;

  /** 订单价格（元） */
  price: number;

  /** 订单状态 */
  status: OrderStatus;

  /** 已成交数量（股） */
  filledQuantity: number;

  /** 已成交金额（元） */
  filledAmount: number;

  /** 平均成交价格（元） */
  avgPrice: number;

  /** 手续费（元） */
  commission: number;

  /** 创建时间 */
  createdAt: string;

  /** 更新时间 */
  updatedAt: string;

  /** 备注 */
  note?: string;
}

/**
 * 创建订单请求
 */
export interface CreateOrderRequest {
  /** 股票代码 */
  symbol: string;

  /** 订单方向 */
  direction: OrderDirection;

  /** 订单类型 */
  type: OrderType;

  /** 订单数量（股） */
  quantity: number;

  /** 订单价格（元，限价单必需） */
  price?: number;

  /** 备注 */
  note?: string;
}

/**
 * 撤单请求
 */
export interface CancelOrderRequest {
  /** 订单ID */
  orderId: string;

  /** 撤单原因 */
  reason?: string;
}

/**
 * 订单查询参数
 */
export interface OrderQuery {
  /** 订单状态筛选 */
  status?: OrderStatus;

  /** 股票代码筛选 */
  symbol?: string;

  /** 起始日期 */
  startDate?: string;

  /** 结束日期 */
  endDate?: string;

  /** 页码 */
  page?: number;

  /** 每页数量 */
  pageSize?: number;
}

/**
 * 订单列表响应
 */
export interface OrderListResponse {
  /** 订单列表 */
  orders: Order[];

  /** 总数 */
  total: number;

  /** 页码 */
  page: number;

  /** 每页数量 */
  pageSize: number;
}

// ============================================
// 持仓数据
// ============================================

/**
 * 持仓数据
 */
export interface Position {
  /** 持仓ID */
  id: string;

  /** 股票代码 */
  symbol: string;

  /** 股票名称 */
  symbolName: string;

  /** 持仓数量（股） */
  quantity: number;

  /** 可用数量（股） */
  availableQuantity: number;

  /** 持仓成本（元） */
  costPrice: number;

  /** 当前价格（元） */
  currentPrice: number;

  /** 市值（元） */
  marketValue: number;

  /** 浮动盈亏（元） */
  profitLoss: number;

  /** 盈亏比例（%） */
  profitLossPercent: number;

  /** 今日盈亏（元） */
  todayProfitLoss: number;

  /** 更新时间 */
  updatedAt: string;
}

/**
 * 持仓汇总
 */
export interface PositionSummary {
  /** 总持仓数 */
  totalPositions: number;

  /** 总市值（元） */
  totalMarketValue: number;

  /** 总成本（元） */
  totalCost: number;

  /** 总盈亏（元） */
  totalProfitLoss: number;

  /** 总盈亏比例（%） */
  totalProfitLossPercent: number;

  /** 今日盈亏（元） */
  todayProfitLoss: number;
}

// ============================================
// 资金账户数据
// ============================================

/**
 * 资金账户数据
 */
export interface Account {
  /** 账户ID */
  id: string;

  /** 账户名称 */
  name: string;

  /** 总资产（元） */
  totalAssets: number;

  /** 可用资金（元） */
  availableCash: number;

  /** 持仓市值（元） */
  positionValue: number;

  /** 总市值（元） */
  marketValue: number;

  /** 浮动盈亏（元） */
  profitLoss: number;

  /** 总盈亏（元） */
  totalProfitLoss: number;

  /** 更新时间 */
  updatedAt: string;
}

// ============================================
// 交易辅助工具类型
// ============================================

/**
 * 交易费用计算结果
 */
export interface TradingFeeCalculation {
  /** 印花税（元） */
  stampDuty: number;

  /** 佣金（元） */
  commission: number;

  /** 过户费（元） */
  transferFee: number;

  /** 经手费（元） */
  handlingFee: number;

  /** 监管费（元） */
  regulatoryFee: number;

  /** 总费用（元） */
  total: number;
}

/**
 * 交易费用计算器
 */
export interface TradingFeeCalculator {
  /**
   * 计算买入费用
   * @param amount 成交金额（元）
   * @param feeConfig 费用配置
   */
  calculateBuyFee(amount: number, feeConfig: TradingFees): TradingFeeCalculation;

  /**
   * 计算卖出费用
   * @param amount 成交金额（元）
   * @param feeConfig 费用配置
   */
  calculateSellFee(amount: number, feeConfig: TradingFees): TradingFeeCalculation;
}

/**
 * 订单验证器
 */
export interface OrderValidator {
  /**
   * 验证订单参数
   * @param order 订单请求
   * @param tradingRule 交易规则
   */
  validate(
    order: CreateOrderRequest,
    tradingRule: ATradingRule,
  ): {
    valid: boolean;
    errors?: string[];
  };
}
