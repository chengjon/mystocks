/**
 * Strategy Module Type Definitions
 *
 * Types for strategy management, backtesting, and performance tracking.
 * Compatible with UnifiedResponse v2.0.0 format.
 */

// ============================================
// Strategy Type Definitions
// ============================================

/**
 * 策略类型枚举
 */
export type StrategyType = 'trend_following' | 'mean_reversion' | 'momentum';

/**
 * 策略状态枚举
 */
export type StrategyStatus = 'active' | 'inactive' | 'testing';

/**
 * 回测状态枚举
 */
export type BacktestStatus = 'pending' | 'running' | 'completed' | 'failed';

/**
 * 策略接口
 */
export interface Strategy {
  id: string;
  name: string;
  description: string;
  type: StrategyType;
  status: StrategyStatus;
  createdAt: Date;
  updatedAt: Date;
  parameters: Record<string, any>;
  performance?: StrategyPerformance;
}

/**
 * 策略性能指标
 */
export interface StrategyPerformance {
  totalReturn: number;        // 总收益率 (0.256 = 25.6%)
  annualReturn: number;       // 年化收益率
  sharpeRatio: number;        // 夏普比率
  maxDrawdown: number;        // 最大回撤 (负数，如 -0.124 = -12.4%)
  winRate: number;           // 胜率 (0.68 = 68%)
  profitLossRatio: number;   // 盈亏比
}

/**
 * 创建策略请求
 */
export interface CreateStrategyRequest {
  name: string;
  description: string;
  type: StrategyType;
  parameters: Record<string, any>;
}

/**
 * 更新策略请求
 */
export interface UpdateStrategyRequest {
  name?: string;
  description?: string;
  status?: StrategyStatus;
  parameters?: Record<string, any>;
}

/**
 * 策略列表响应
 */
export interface StrategyListResponse {
  strategies: Strategy[];
  total: number;
  page: number;
  pageSize: number;
}

// ============================================
// Backtest Type Definitions
// ============================================

/**
 * 回测参数
 */
export interface BacktestParams {
  startDate: string;      // YYYY-MM-DD
  endDate: string;        // YYYY-MM-DD
  initialCapital: number;
  symbols?: string[];
  benchmark?: string;
}

/**
 * 回测任务
 */
export interface BacktestTask {
  taskId: string;
  strategyId: string;
  status: BacktestStatus;
  progress: number;       // 0-100
  startTime: Date;
  endTime?: Date;
  result?: BacktestResult;
  error?: string;
}

/**
 * 回测结果
 */
export interface BacktestResult {
  taskId: string;
  strategyId: string;
  totalReturn: number;
  annualReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  totalTrades: number;
  profitFactor: number;
  equityCurve: EquityPoint[];
  trades: Trade[];
  performanceMetrics: PerformanceMetrics;
}

/**
 * 权益曲线点
 */
export interface EquityPoint {
  date: string;
  value: number;
  drawdown?: number;
}

/**
 * 交易记录
 */
export interface Trade {
  id: string;
  symbol: string;
  type: 'buy' | 'sell';
  quantity: number;
  price: number;
  timestamp: Date;
  profitLoss?: number;
  profitLossPercent?: number;
}

/**
 * 详细性能指标
 */
export interface PerformanceMetrics {
  totalReturn: number;
  annualReturn: number;
  monthlyReturn: number;
  weeklyReturn: number;
  dailyReturn: number;
  sharpeRatio: number;
  sortinoRatio: number;
  calmarRatio: number;
  maxDrawdown: number;
  avgDrawdown: number;
  maxDrawdownDuration: number;  // in days
  winRate: number;
  profitFactor: number;
  avgProfit: number;
  avgLoss: number;
  bestTrade: number;
  worstTrade: number;
  totalTrades: number;
  winningTrades: number;
  losingTrades: number;
  avgTradeDuration: number;      // in days
  expectency: number;            // 期望收益
}

// ============================================
// API Response Types (UnifiedResponse v2.0.0)
// ============================================

/**
 * 策略列表 API 响应
 */
export type StrategyListAPIResponse = {
  success: boolean;
  code: number;
  message: string;
  data: StrategyListResponse;
  timestamp: string;
  request_id: string;
  errors: null;
};

/**
 * 单个策略 API 响应
 */
export type StrategyAPIResponse = {
  success: boolean;
  code: number;
  message: string;
  data: Strategy;
  timestamp: string;
  request_id: string;
  errors: null;
};

/**
 * 回测任务 API 响应
 */
export type BacktestTaskAPIResponse = {
  success: boolean;
  code: number;
  message: string;
  data: BacktestTask;
  timestamp: string;
  request_id: string;
  errors: null;
};

// ============================================
// Utility Types
// ============================================

/**
 * 策略创建/更新表单数据
 */
export interface StrategyFormData {
  name: string;
  description: string;
  type: StrategyType;
  parameters: {
    [key: string]: string | number | boolean;
  };
}

/**
 * 策略类型选项
 */
export const STRATEGY_TYPE_OPTIONS: { label: string; value: StrategyType }[] = [
  { label: '趋势跟踪', value: 'trend_following' },
  { label: '均值回归', value: 'mean_reversion' },
  { label: '动量策略', value: 'momentum' }
];

/**
 * 策略状态选项
 */
export const STRATEGY_STATUS_OPTIONS: { label: string; value: StrategyStatus }[] = [
  { label: '运行中', value: 'active' },
  { label: '未激活', value: 'inactive' },
  { label: '测试中', value: 'testing' }
];

/**
 * 回测状态选项
 */
export const BACKTEST_STATUS_OPTIONS: { label: string; value: BacktestStatus; color: string }[] = [
  { label: '等待中', value: 'pending', color: 'gray' },
  { label: '运行中', value: 'running', color: 'blue' },
  { label: '已完成', value: 'completed', color: 'green' },
  { label: '失败', value: 'failed', color: 'red' }
];
