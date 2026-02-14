
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

