
/**
 * 策略类型
 */
export enum StrategyType {
  /** 技术指标策略 */
  TECHNICAL = 'technical',

  /** 量化策略 */
  QUANTITATIVE = 'quantitative',

  /** 套利策略 */
  ARBITRAGE = 'arbitrage',

  /** 做市策略 */
  MARKET_MAKING = 'market_making',

  /** 趋势跟踪策略 */
  TREND_FOLLOWING = 'trend_following',

  /** 均值回归策略 */
  MEAN_REVERSION = 'mean_reversion',

  /** 自定义策略 */
  CUSTOM = 'custom',
}

/**
 * 策略状态
 */
export enum StrategyStatus {
  /** 草稿 */
  DRAFT = 'draft',

  /** 启用 */
  ENABLED = 'enabled',

  /** 禁用 */
  DISABLED = 'disabled',

  /** 运行中 */
  RUNNING = 'running',

  /** 已停止 */
  STOPPED = 'stopped',

  /** 已归档 */
  ARCHIVED = 'archived',
}

/**
 * 风险等级
 */
export enum RiskLevel {
  /** 低风险 */
  LOW = 'low',

  /** 中低风险 */
  MEDIUM_LOW = 'medium_low',

  /** 中等风险 */
  MEDIUM = 'medium',

  /** 中高风险 */
  MEDIUM_HIGH = 'medium_high',

  /** 高风险 */
  HIGH = 'high',
}

/**
 * 策略基础接口
 */
export interface Strategy {
  /** 策略ID */
  id: string;

  /** 策略名称 */
  name: string;

  /** 策略描述 */
  description: string;

  /** 策略类型 */
  type: StrategyType;

  /** 策略状态 */
  status: StrategyStatus;

  /** 风险等级 */
  riskLevel: RiskLevel;

  /** 策略参数 */
  params: StrategyParams;

  /** 策略规则 */
  rules: StrategyRule[];

  /** 适用的股票代码列表 */
  symbols: string[];

  /** 创建者 */
  creator: string;

  /** 创建时间 */
  createdAt: string;

  /** 更新时间 */
  updatedAt: string;

  /** 最后运行时间 */
  lastRunAt?: string;

  /** 版本号 */
  version: string;

  /** 标签 */
  tags?: string[];
}

/**
 * 策略参数
 */
export interface StrategyParams {
  /** 参数对象 */
  [key: string]: StrategyParamValue;
}

/**
 * 策略参数值类型
 */
export type StrategyParamValue =
  | string
  | number
  | boolean
  | string[]
  | number[]
  | ParamObject;

/**
 * 参数对象
 */
export interface ParamObject {
  /** 参数值 */
  value: StrategyParamValue;

  /** 参数名称 */
  name: string;

  /** 参数描述 */
  description?: string;
}

/**
 * 策略规则
 */
export interface StrategyRule {
  /** 规则ID */
  id: string;

  /** 规则名称 */
  name: string;

  /** 规则类型 */
  type: 'buy' | 'sell' | 'filter' | 'risk';

  /** 规则条件 */
  conditions: RuleCondition[];

  /** 规则动作 */
  actions: RuleAction[];

  /** 是否启用 */
  enabled: boolean;

  /** 优先级 */
  priority: number;
}

/**
 * 规则条件
 */
export interface RuleCondition {
  /** 条件ID */
  id: string;

  /** 条件类型 */
  type:
    | 'price_above'
    | 'price_below'
    | 'volume_above'
    | 'volume_below'
    | 'indicator_cross'
    | 'time_range'
    | 'custom';

  /** 条件参数 */
  params: Record<string, unknown>;

  /** 逻辑运算符 */
  operator: 'AND' | 'OR';
}

/**
 * 规则动作
 */
export interface RuleAction {
  /** 动作类型 */
  type: 'buy' | 'sell' | 'hold' | 'notify' | 'custom';

  /** 动作参数 */
  params: Record<string, unknown>;
}

/**
 * 回测配置
 */
export interface BacktestConfig {
  /** 回测ID */
  id: string;

  /** 策略ID */
  strategyId: string;

  /** 回测名称 */
  name: string;

  /** 回测描述 */
  description?: string;

  /** 回测时间范围 */
  timeRange: BacktestTimeRange;

  /** 初始资金（元） */
  initialCapital: number;

  /** 适用的股票代码列表 */
  symbols: string[];

  /** 回测参数 */
  params: BacktestParams;

  /** 风险控制参数 */
  riskControls: RiskControlParams;

  /** 交易费用配置 */
  fees: TradingFeeConfig;

  /** 创建时间 */
  createdAt: string;
}

/**
 * 回测时间范围
 */
export interface BacktestTimeRange {
  /** 开始日期 */
  startDate: string;

  /** 结束日期 */
  endDate: string;
}

/**
 * 回测参数
 */
export interface BacktestParams {
  /** 是否使用复权数据 */
  useAdjustedPrice: boolean;

  /** 数据频率 */
  frequency: 'tick' | '1m' | '5m' | '15m' | '30m' | '1h' | '1d';

  /** 是否允许做空 */
  allowShort: boolean;

  /** 是否允许T+0（仅模拟） */
  allowT0: boolean;

  /** 滑点设置 */
  slippage: SlippageConfig;

  /** 最大持仓数量 */
  maxPositions?: number;
}

/**
 * 滑点配置
 */
export interface SlippageConfig {
  /** 是否启用滑点 */
  enabled: boolean;

  /** 滑点模式 */
  mode: 'fixed' | 'percentage' | 'custom';

  /** 固定滑点值（元） */
  fixedValue?: number;

  /** 百分比滑点（%） */
  percentageValue?: number;
}

/**
 * 风险控制参数
 */
export interface RiskControlParams {
  /** 单只股票最大仓位（%） */
  maxPositionPercent: number;

  /** 单笔交易最大金额（元） */
  maxTradeAmount: number;

  /** 止损比例（%） */
  stopLossPercent: number;

  /** 止盈比例（%） */
  takeProfitPercent: number;

  /** 最大回撤限制（%） */
  maxDrawdownPercent: number;
}

/**
 * 交易费用配置
 */
export interface TradingFeeConfig {
  /** 佣金费率（%） */
  commissionRate: number;

  /** 最低佣金（元） */
  minCommission: number;

  /** 印花税率（%） */
  stampDutyRate: number;

  /** 过户费率（%） */
  transferFeeRate: number;
}

/**
 * 回测结果
 */
export interface BacktestResult {
  /** 回测结果ID */
  id: string;

  /** 回测配置ID */
  configId: string;

  /** 回测状态 */
  status: 'pending' | 'running' | 'completed' | 'failed';

  /** 回测性能指标 */
  performance: PerformanceMetrics;

  /** 交易记录 */
  trades: TradeRecord[];

  /** 持仓记录 */
  positions: PositionRecord[];

  /** 权益曲线 */
  equityCurve: EquityCurvePoint[];

  /** 回测摘要 */
  summary: BacktestSummary;

  /** 开始时间 */
  startedAt: string;

  /** 完成时间 */
  completedAt?: string;

  /** 错误信息（如果失败） */
  error?: string;
}

/**
 * 性能指标
 */
export interface PerformanceMetrics {
  /** 总收益率（%） */
  totalReturn: number;

  /** 年化收益率（%） */
  annualizedReturn: number;

  /** 基准收益率（%） */
  benchmarkReturn: number;

  /** 超额收益率（%） */
  excessReturn: number;

  /** 波动率（%） */
  volatility: number;

  /** 夏普比率 */
  sharpeRatio: number;

  /** 最大回撤（%） */
  maxDrawdown: number;

  /** 胜率（%） */
  winRate: number;

  /** 盈亏比 */
  profitLossRatio: number;

  /** 总交易次数 */
  totalTrades: number;

  /** 获胜交易次数 */
  winningTrades: number;

  /** 失败交易次数 */
  losingTrades: number;
}

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

