/**
 * Type Definitions Barrel
 *
 * 统一导出所有类型定义，提供类型导入的单一入口点。
 *
 * @module types
 */

// ============================================
// Market Types (市场数据类型)
// ============================================

export * from './market';

// Re-export commonly used market types
export type {
  StockData,
  StockInfo,
  StockPrice,
  StockDepth,
  StockStats,
} from './market';

export type {
  OHLCV,
  KLineCandle,
  KLineData,
  KLineQuery,
} from './market';

export type {
  RealtimeQuote,
  BatchRealtimeQuotes,
  MarketStats,
  MarketOverview,
} from './market';

export type {
  FundFlowItem,
  FundFlowData,
  MarketColorType,
  TradingStatus,
  MarketSector,
  StockList,
  TimePeriod,
} from './market';

// ============================================
// Indicator Types (技术指标类型)
// ============================================

export * from './indicators';

export type {
  Indicator,
  IndicatorConfig,
  IndicatorResult,
  IndicatorDataPoint,
} from './indicators';

export type {
  IndicatorParam,
  IndicatorColors,
  IndicatorDisplayOptions,
  IndicatorResultMeta,
} from './indicators';

export type {
  IndicatorCategory,
  IndicatorPeriod,
  MAIndicator,
  MAConfig,
  MAResult,
} from './indicators';

export type {
  MACDIndicator,
  MACDConfig,
  MACDResult,
  KDJIndicator,
  KDJConfig,
  KDJResult,
} from './indicators';

export type {
  RSIIndicator,
  RSIConfig,
  RSIResult,
  BOLLIndicator,
  BOLLConfig,
  BOLLResult,
} from './indicators';

export type {
  IndicatorTemplate,
  IndicatorCalculateRequest,
  IndicatorCalculateResponse,
} from './indicators';

export type {
  IndicatorDataFormatter,
  IndicatorValidator,
  IndicatorCalculator,
} from './indicators';

// ============================================
// Trading Types (交易类型)
// ============================================

export * from './trading';

export type {
  ATradingRule,
  TradingHours,
  TradingFees,
  PREDEFINED_TRADING_RULES,
} from './trading';

export type {
  TradeData,
  OrderBook,
  OrderBookLevel,
  TickData,
} from './trading';

export type {
  Order,
  CreateOrderRequest,
  CancelOrderRequest,
  OrderQuery,
  OrderListResponse,
} from './trading';

export type {
  OrderStatus,
  OrderDirection,
  OrderType,
  BoardType,
} from './trading';

export type {
  Position,
  PositionSummary,
  Account,
} from './trading';

export type {
  TradingFeeCalculation,
  TradingFeeCalculator,
  OrderValidator,
} from './trading';

// ============================================
// Strategy Types (策略类型)
// ============================================

export * from './strategy';

export type {
  Strategy,
  StrategyParams,
  StrategyRule,
  RuleCondition,
  RuleAction,
} from './strategy';

export type {
  StrategyType,
  StrategyStatus,
  RiskLevel,
  StrategyParamValue,
  ParamObject,
} from './strategy';

export type {
  BacktestConfig,
  BacktestTimeRange,
  BacktestParams,
  SlippageConfig,
  RiskControlParams,
  TradingFeeConfig,
} from './strategy';

export type {
  BacktestResult,
  PerformanceMetrics,
  TradeRecord,
  PositionRecord,
  EquityCurvePoint,
  BacktestSummary,
} from './strategy';

export type {
  StrategyEvaluation,
  StrategyComparison,
  StrategyOptimization,
  StrategyMonitoring,
  StrategyAlert,
} from './strategy';

// ============================================
// AI Types (人工智能类型)
// ============================================

export * from './ai';

export type {
  PredictionResult,
  ProbabilityDistribution,
  FeatureImportance,
  ActualResult,
  BatchPredictions,
  PredictionStatistics,
} from './ai';

export type {
  PredictionDirection,
  PredictionHorizon,
  AIModelType,
  ModelStatus,
} from './ai';

export type {
  ModelMetadata,
  TrainingDataInfo,
  ModelPerformance,
  ModelHyperparameters,
  ModelFeature,
  ModelArchitecture,
} from './ai';

export type {
  ModelTrainingJob,
  TrainingParams,
  TrainingProgress,
  ModelEvaluationResult,
  EvaluationDataset,
  ConfusionMatrix,
  ClassificationReport,
  EvaluationVisualization,
} from './ai';

export type {
  FeatureEngineeringConfig,
  FeatureTransform,
  FeatureCombination,
  ModelPredictionRequest,
  ModelComparison,
} from './ai';

// ============================================
// Utility Types (工具类型)
// ============================================

/**
 * 深度 Required 类型（必须包含的属性）
 */
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

/**
 * 深度 Partial 类型（可选属性）
 */
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

/**
 * 提取类型值的联合
 */
export type ValueOf<T> = T[keyof T];

/**
 * 使所有属性变为只读
 */
export type Immutable<T> = {
  readonly [P in keyof T]: T[P] extends object ? Immutable<T[P]> : T[P];
};

/**
 * 提取函数类型的参数
 */
export type Parameters<T extends (...args: any[]) => any> = T extends (
  ...args: infer P
) => any
  ? P
  : never;

/**
 * 提取函数类型的返回值
 */
export type ReturnType<T extends (...args: any[]) => any> = T extends (
  ...args: any[]
) => infer R
  ? R
  : any;

/**
 * 异步版本类型
 */
export type AsyncReturnType<T extends (...args: any[]) => Promise<any>> = T extends (
  ...args: any[]
) => Promise<infer R>
  ? R
  : any;

// ============================================
// Common Type Guards (通用类型守卫)
// ============================================

/**
 * 检查是否为 null 或 undefined
 */
export function isNotNullOrUndefined<T>(value: T | null | undefined): value is T {
  return value !== null && value !== undefined;
}

/**
 * 检查是否为空数组
 */
export function isEmptyArray(value: unknown[]): value is [] {
  return value.length === 0;
}

/**
 * 检查是否为对象
 */
export function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/**
 * 检查是否为数组
 */
export function isArray(value: unknown): value is unknown[] {
  return Array.isArray(value);
}

/**
 * 检查是否为字符串
 */
export function isString(value: unknown): value is string {
  return typeof value === 'string';
}

/**
 * 检查是否为数字
 */
export function isNumber(value: unknown): value is number {
  return typeof value === 'number' && !isNaN(value);
}

/**
 * 检查是否为布尔值
 */
export function isBoolean(value: unknown): value is boolean {
  return typeof value === 'boolean';
}

/**
 * 检查是否为日期
 */
export function isDate(value: unknown): value is Date {
  return value instanceof Date;
}

/**
 * 检查是否为函数
 */
export function isFunction(value: unknown): value is (...args: any[]) => any {
  return typeof value === 'function';
}

// ============================================
// Common Utility Functions (通用工具函数)
// ============================================

/**
 * 格式化日期为字符串
 */
export function formatDate(date: Date, format: string = 'YYYY-MM-DD'): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');

  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day);
}

/**
 * 解析日期字符串
 */
export function parseDate(dateString: string): Date {
  return new Date(dateString);
}

/**
 * 生成唯一ID
 */
export function generateId(prefix: string = ''): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 9);
  return prefix ? `${prefix}_${timestamp}${random}` : `${timestamp}${random}`;
}

/**
 * 深度克隆对象
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }

  if (obj instanceof Date) {
    return new Date(obj.getTime()) as T;
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => deepClone(item)) as T;
  }

  const clonedObj = {} as T;
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      (clonedObj as any)[key] = deepClone(obj[key]);
    }
  }

  return clonedObj;
}

/**
 * 安全的 JSON 解析
 */
export function safeJsonParse<T>(jsonString: string, defaultValue: T): T {
  try {
    return JSON.parse(jsonString) as T;
  } catch {
    return defaultValue;
  }
}

/**
 * 格式化数字为货币
 */
export function formatCurrency(
  amount: number,
  currency: string = '¥',
  decimals: number = 2,
): string {
  return `${currency}${amount.toFixed(decimals)}`;
}

/**
 * 格式化数字为百分比
 */
export function formatPercent(value: number, decimals: number = 2): string {
  return `${value.toFixed(decimals)}%`;
}

/**
 * 数字缩写（例如：1000 -> 1K, 1000000 -> 1M）
 */
export function abbreviateNumber(value: number): string {
  const absValue = Math.abs(value);

  if (absValue >= 1e9) {
    return `${(value / 1e9).toFixed(1)}B`;
  }

  if (absValue >= 1e6) {
    return `${(value / 1e6).toFixed(1)}M`;
  }

  if (absValue >= 1e3) {
    return `${(value / 1e3).toFixed(1)}K`;
  }

  return value.toString();
}
