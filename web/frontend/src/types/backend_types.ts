/**
 * @fileoverview Backend to Frontend Contract Type Adapter
 * @description 类型适配层，处理后端Python命名（snake_case）与前端TypeScript（camelCase）的字段名不匹配问题
 * @module types
 * @version 1.0.0
 * @updated 2026-01-31
 */

/**
 * 字段名映射配置
 * 定义后端snake_case字段与前端camelCase字段的映射关系
 */
export const FIELD_NAME_MAPPING = {
  // ============ Market Data Fields ============
  'full_name': 'fullName',
  'chinese_name': 'chineseName',
  'display_name': 'displayName',
  'panel_type': 'panelType',
  'sector_full_name': 'sectorFullName',
  'index_full_name': 'indexFullName',
  'concept_full_name': 'conceptFullName',

  // ============ Indicator Fields ============
  'indicator_type': 'indicatorType',
  'indicator_name': 'indicatorName',
  'sub_indicator_type': 'subIndicatorType',
  'base_indicator': 'baseIndicator',
  'overlay_indicator': 'overlayIndicator',
  'oscillator_indicator': 'oscillatorIndicator',
  'parameter_type': 'parameterType',
  'parameter_name': 'parameterName',
  'parameter_display_name': 'parameterDisplayName',
  'output_type': 'outputType',
  'output_name': 'outputName',
  'output_unit': 'outputUnit',
  'signal_type': 'signalType',
  'signal_name': 'signalName',
  'signal_direction': 'signalDirection',
  'signal_strength': 'signalStrength',

  // ============ Strategy Fields ============
  'strategy_type': 'strategyType',
  'strategy_name': 'strategyName',
  'strategy_abbreviation': 'strategyAbbreviation',
  'strategy_description': 'strategyDescription',
  'parameter_config_type': 'parameterConfigType',
  'initial_capital': 'initialCapital',
  'max_position_ratio': 'maxPositionRatio',
  'stop_loss_ratio': 'stopLossRatio',
  'take_profit_ratio': 'takeProfitRatio',
  'risk_level': 'riskLevel',

  // ============ Panel Fields ============
  'panel_type': 'panelType',
  'panel_name': 'panelName',
  'panel_abbreviation': 'panelAbbreviation',
  'panel_description': 'panelDescription',
  'panel_display_name': 'panelDisplayName',
  'panel_sort_order': 'panelSortOrder',
  'panel_is_default': 'panelIsDefault',
  'panel_is_collapsed': 'panelIsCollapsed',
  'panel_is_editable': 'panelIsEditable',
  'panel_is_removable': 'panelIsRemovable',
  'panel_icon': 'panelIcon',
  'panel_theme': 'panelTheme',
  'panel_layout_type': 'panelLayoutType',
  'panel_width': 'panelWidth',
  'panel_height': 'panelHeight',
  'panel_min_width': 'panelMinWidth',
  'panel_max_width': 'panelMaxWidth',
  'panel_background_color': 'panelBackgroundColor',
  'panel_border_color': 'panelBorderColor',
  'panel_text_color': 'panelTextColor',

  // ============ Trading Fields ============
  'trade_type': 'tradeType',
  'trade_status': 'tradeStatus',
  'trade_direction': 'tradeDirection',
  'entry_price': 'entryPrice',
  'exit_price': 'exitPrice',
  'entry_quantity': 'entryQuantity',
  'exit_quantity': 'exitQuantity',
  'entry_amount': 'entryAmount',
  'exit_amount': 'exitAmount',
  'entry_time': 'entryTime',
  'exit_time': 'exitTime',
  'order_type': 'orderType',
  'exchange': 'exchange',
  'commission': 'commission',
  'slippage': 'slippage',
  'tax': 'tax',
  'net_profit': 'netProfit',
  'net_profit_percent': 'netProfitPercent',
  'realized_pnl': 'realizedPnL',
  'unrealized_pnl': 'unrealizedPnL',
  'trading_account_id': 'tradingAccountId',
  'account_type': 'accountType',

  // ============ Time Series Fields ============
  'frequency': 'frequency',
  'start_date': 'startDate',
  'end_date': 'endDate',
  'time_period': 'timePeriod',
  'data_point_count': 'dataPointCount',
  'is_rolled': 'isRolled',
  'is_computed': 'isComputed',
  'is_forecast': 'isForecast',
  'smoothing_method': 'smoothingMethod',

  // ============ Portfolio Fields ============
  'portfolio_type': 'portfolioType',
  'portfolio_name': 'portfolioName',
  'portfolio_description': 'portfolioDescription',
  'asset_allocation': 'assetAllocation',
  'target_allocation': 'targetAllocation',
  'current_allocation': 'currentAllocation',
  'total_value': 'totalValue',
  'total_weight': 'totalWeight',
  'risk_level': 'riskLevel',
  'sharpe_ratio': 'sharpeRatio',
  'sortino_ratio': 'sortinoRatio',
  'max_drawdown': 'maxDrawdown',
  'beta': 'beta',
  'alpha': 'alpha',
  'tracking_error': 'trackingError',

  // ============ Order Fields ============
  'order_id': 'orderId',
  'order_status': 'orderStatus',
  'order_type': 'orderType',
  'order_side': 'orderSide',
  'order_class': 'orderClass',
  'order_time': 'orderTime',
  'execution_time': 'executionTime',
  'price': 'price',
  'quantity': 'quantity',
  'amount': 'amount',
  'filled_quantity': 'filledQuantity',
  'cancelled_quantity': 'cancelledQuantity',
  'commission': 'commission',
  'fees': 'fees',
  'slippage': 'slippage',
  'exchange': 'exchange',
  'account_id': 'accountId',
  'account_type': 'accountType'
} as const;

/**
 * 后端蛇形命名到前端驼峰命名的映射表
 * 用于在API响应处理时自动转换字段名
 */
export const SNAKE_TO_CAMEL_MAPPING: Record<string, string> = {
  // Market Data
  'full_name': 'fullName',
  'chinese_name': 'chineseName',
  'display_name': 'displayName',
  'panel_type': 'panelType',
  'sector_full_name': 'sectorFullName',
  'index_full_name': 'indexFullName',
  'concept_full_name': 'conceptFullName',

  // Indicator Data
  'indicator_type': 'indicatorType',
  'indicator_name': 'indicatorName',
  'sub_indicator_type': 'subIndicatorType',
  'base_indicator': 'baseIndicator',
  'overlay_indicator': 'overlayIndicator',
  'oscillator_indicator': 'oscillatorIndicator',
  'parameter_type': 'parameterType',
  'parameter_name': 'parameterName',
  'parameter_display_name': 'parameterDisplayName',
  'output_type': 'outputType',
  'output_name': 'outputName',
  'output_unit': 'outputUnit',
  'signal_type': 'signalType',
  'signal_name': 'signalName',
  'signal_direction': 'signalDirection',
  'signal_strength': 'signalStrength',

  // Strategy Data
  'strategy_type': 'strategyType',
  'strategy_name': 'strategyName',
  'strategy_abbreviation': 'strategyAbbreviation',
  'strategy_description': 'strategyDescription',
  'parameter_config_type': 'parameterConfigType',
  'initial_capital': 'initialCapital',
  'max_position_ratio': 'maxPositionRatio',
  'stop_loss_ratio': 'stopLossRatio',
  'take_profit_ratio': 'takeProfitRatio',
  'risk_level': 'riskLevel',

  // Panel Data
  'panel_type': 'panelType',
  'panel_name': 'panelName',
  'panel_abbreviation': 'panelAbbreviation',
  'panel_description': 'panelDescription',
  'panel_display_name': 'panelDisplayName',
  'panel_sort_order': 'panelSortOrder',
  'panel_is_default': 'panelIsDefault',
  'panel_is_collapsed': 'panelIsCollapsed',
  'panel_is_editable': 'panelIsEditable',
  'panel_is_removable': 'panelIsRemovable',
  'panel_icon': 'panelIcon',
  'panel_theme': 'panelTheme',
  'panel_layout_type': 'panelLayoutType',
  'panel_width': 'panelWidth',
  'panel_height': 'panelHeight',
  'panel_min_width': 'panelMinWidth',
  'panel_max_width': 'panelMaxWidth',
  'panel_background_color': 'panelBackgroundColor',
  'panel_border_color': 'panelBorderColor',
  'panel_text_color': 'panelTextColor',

  // Trading Data
  'trade_type': 'tradeType',
  'trade_status': 'tradeStatus',
  'trade_direction': 'tradeDirection',
  'entry_price': 'entryPrice',
  'exit_price': 'exitPrice',
  'entry_quantity': 'entryQuantity',
  'exit_quantity': 'exitQuantity',
  'entry_amount': 'entryAmount',
  'exit_amount': 'exitAmount',
  'entry_time': 'entryTime',
  'exit_time': 'exitTime',
  'order_type': 'orderType',
  'exchange': 'exchange',
  'commission': 'commission',
  'slippage': 'slippage',
  'tax': 'tax',
  'net_profit': 'netProfit',
  'net_profit_percent': 'netProfitPercent',
  'realized_pnl': 'realizedPnL',
  'unrealized_pnl': 'unrealizedPnL',
  'trading_account_id': 'tradingAccountId',
  'account_type': 'accountType',

  // Time Series Data
  'frequency': 'frequency',
  'start_date': 'startDate',
  'end_date': 'endDate',
  'time_period': 'timePeriod',
  'data_point_count': 'dataPointCount',
  'is_rolled': 'isRolled',
  'is_computed': 'isComputed',
  'is_forecast': 'isForecast',
  'smoothing_method': 'smoothingMethod',

  // Portfolio Data
  'portfolio_type': 'portfolioType',
  'portfolio_name': 'portfolioName',
  'portfolio_description': 'portfolioDescription',
  'asset_allocation': 'assetAllocation',
  'target_allocation': 'targetAllocation',
  'current_allocation': 'currentAllocation',
  'total_value': 'totalValue',
  'total_weight': 'totalWeight',
  'risk_level': 'riskLevel',
  'sharpe_ratio': 'sharpeRatio',
  'sortino_ratio': 'sortinoRatio',
  'max_drawdown': 'maxDrawdown',
  'beta': 'beta',
  'alpha': 'alpha',
  'tracking_error': 'trackingError',

  // Order Data
  'order_id': 'orderId',
  'order_status': 'orderStatus',
  'order_type': 'orderType',
  'order_side': 'orderSide',
  'order_class': 'orderClass',
  'order_time': 'orderTime',
  'execution_time': 'executionTime',
  'price': 'price',
  'quantity': 'quantity',
  'amount': 'amount',
  'filled_quantity': 'filledQuantity',
  'cancelled_quantity': 'cancelledQuantity',
  'commission': 'commission',
  'fees': 'fees',
  'slippage': 'slippage',
  'exchange': 'exchange',
  'account_id': 'accountId',
  'account_type': 'accountType'
} as const;

/**
 * 转换后端对象为前端类型
 * 自动将snake_case字段转换为camelCase字段
 *
 * @example
 * // 后端响应（Python风格）
 * {
 *   full_name: '上证综合指数',
 *   panel_type: 'overlay',
 *   chinese_name: '移动平均线'
 * }
 *
 * // 前端转换结果（TypeScript风格）
 * {
 *   fullName: '上证综合指数',
 *   panelType: 'overlay',
 *   chineseName: '移动平均线'
 * }
 */
export function transformContract<T extends Record<string, any>>(
  backendContract: T
): { [K in keyof T]: (backendContract[K] extends string ? FrontendContractField<T, K> : T[K]) } {
  const result = {} as any;
  
  // 遍历所有字段，检查是否需要转换
  for (const key in backendContract) {
    const value = backendContract[key];
    
    // 跳过null、undefined、数字、布尔值
    if (value === null || value === undefined || typeof value === 'number' || typeof value === 'boolean') {
      result[key] = value;
      continue;
    }
    
    // 只转换字符串值
    if (typeof value === 'string') {
      const frontendKey = SNAKE_TO_CAMEL_MAPPING[key];
      
      if (frontendKey && frontendKey !== key) {
        // 转换字段名
        result[frontendKey] = value;
      } else {
        // 保持原字段名
        result[key] = value;
      }
    }
  }
  
  return result as { [K in keyof T]: (backendContract[K] extends string ? FrontendContractField<T, K> : T[K]) };
}

/**
 * 快速字段名转换函数
 * 只转换单个字段名，不处理整个对象
 *
 * @example
 * transformFieldName('full_name') → 'fullName'
 */
export function transformFieldName(backendFieldName: string): string {
  return SNAKE_TO_CAMEL_MAPPING[backendFieldName] || backendFieldName;
}

/**
 * 转换数组中的字段名
 * 将后端API返回的对象数组转换为前端camelCase格式
 *
 * @param backendArray 后端对象数组
 * @returns 转换后的前端对象数组
 */
export function transformContractArray<T extends Record<string, any>>(
  backendArray: T[]
): Array<{ [K in keyof T]: (T[K] extends string ? FrontendContractField<T, K> : T[K]) }> {
  return backendArray.map(item => transformContract(item));
}

/**
 * 字段名转换类型
 * 用于标记转换后的字段类型
 */
export type FrontendContractField<T extends Record<string, any>, K extends string> = {
  fieldName: T[K];
  value: T[K] extends string ? string : T[K]
} & {
  [originalKey in K as T]: originalKey
}

/**
 * 检查字段是否需要转换
 * 用于运行时检查某个字段名是否在后端到前端的映射表中
 *
 * @example
 * needsTransformation('full_name') → true
 * needsTransformation('fullName') → false
 */
export function needsTransformation(backendFieldName: string): boolean {
  return backendFieldName in SNAKE_TO_CAMEL_MAPPING && 
         SNAKE_TO_CAMEL_MAPPING[backendFieldName] !== backendFieldName;
}

/**
 * 批量转换字段名
 * 转换多个字段名的数组
 *
 * @example
 * transformFieldNames(['full_name', 'panel_type', 'chinese_name'])
 * → ['fullName', 'panelType', 'chineseName']
 */
export function transformFieldNames(backendFieldNames: string[]): string[] {
  return backendFieldNames.map(name => transformFieldName(name));
}

/**
 * 获取字段名的映射关系
 * 返回后端字段名到前端字段名的映射
 *
 * @example
 * getFieldMapping('full_name') → { original: 'full_name', transformed: 'fullName' }
 */
export function getFieldMapping(backendFieldName: string): {
  original: string;
  transformed: string;
  needsTransform: boolean;
} {
  if (needsTransformation(backendFieldName)) {
    return {
      original: backendFieldName,
      transformed: transformFieldName(backendFieldName),
      needsTransform: true
    };
  }

  return {
    original: backendFieldName,
    transformed: backendFieldName,
    needsTransform: false
  };
}

/**
 * Contract类型定义（前端TypeScript）
 * 与后端Python风格对应的TypeScript接口
 */
export interface MarketDataContract {
  symbol: string;
  name: string;
  currentPrice: number;
  changePercent: number;
  volume: number;
  amount: number;
  high: number;
  low: number;
  open: number;
  preClose: number;
  timestamp: string;
}

export interface IndicatorMetadataContract {
  indicatorType: string;
  indicatorName: string;
  abbreviation: string;
  chineseName: string;
  category: string;
  description: string;
  panelType: string;
  parameters: ParameterContract[];
  outputs: OutputContract[];
  referenceLines: number[] | null;
  minDataPointsFormula: string;
}

export interface ParameterContract {
  name: string;
  type: 'int' | 'float' | 'string' | 'bool';
  default: number | string | boolean;
  min?: number;
  max?: number;
  step?: number;
  description: string;
}

export interface OutputContract {
  name: string;
  description: string;
  unit?: string;
}

export interface SignalContract {
  symbol: string;
  type: SignalType;
  strength: SignalStrength;
  price?: number;
  indicatorType: string;
  indicatorValue?: number;
  timestamp: string;
  description?: string;
  confidence?: number;
}

export interface StrategyContract {
  strategyType: StrategyType;
  strategyName: string;
  abbreviation: string;
  description: string;
  parameterConfigType: ParameterConfigType;
  initialCapital: number;
  maxPositionRatio: number;
  stopLossRatio: number;
  takeProfitRatio: number;
  riskLevel: RiskLevel;
}

export interface BacktestContract {
  id: string;
  name: string;
  strategy: StrategyContract;
  startDate: string;
  endDate: string;
  initialCapital: number;
  finalCapital: number;
  totalReturn: number;
  annualizedReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  volatility: number;
  winRate: number;
  trades: TradeContract[];
}

export interface TradeContract {
  id: string;
  symbol: string;
  type: TradeType;
  status: TradeStatus;
  direction: TradeDirection;
  entryPrice: number;
  exitPrice: number;
  entryTime: string;
  exitTime: string;
  entryQuantity: number;
  exitQuantity: number;
  entryAmount: number;
  exitAmount: number;
  commission: number;
  slippage: number;
  pnl: number;
  pnlPercent: number;
}

/**
 * 类型定义（与types/indicator.ts中的类型对应）
 */
export type IndicatorCategory = 'trend' | 'momentum' | 'volatility' | 'volume' | 'candlestick';

export type PanelType = 'overlay' | 'oscillator';

export type ParameterType = 'int' | 'float' | 'string' | 'bool';

export type SignalType = 'buy' | 'sell' | 'hold' | 'strong_buy' | 'strong_sell';

export type SignalStrength = 'weak' | 'medium' | 'strong';

export type StrategyType = 'trend' | 'mean_reversion' | 'momentum' | 'arbitrage' | 'market_neutral';

export type TradeType = 'long' | 'short' | 'spread';

export type TradeStatus = 'pending' | 'open' | 'filled' | 'cancelled' | 'partial';

export type TradeDirection = 'long' | 'short';

export type RiskLevel = 'low' | 'medium' | 'high' | 'extreme';

  /**
   * Contract类型定义（前端TypeScript）
   * 与后端Python风格对应的TypeScript接口
   */

export interface ParameterContract {
  name: string;
  type: 'int' | 'float' | 'string' | 'bool';
  default: number | string | boolean;
  min?: number;
  max?: number;
  step?: number;
  description: string;
}

export interface OutputContract {
  name: string;
  description: string;
  unit?: string;
}

export interface SignalContract {
  symbol: string;
  type: SignalType;
  strength?: SignalStrength;
  price?: number;
  indicatorType?: string;
  indicatorValue?: number;
  timestamp: string;
  description?: string;
  confidence?: number;
}

export interface BacktestContract {
  id: string;
  name: string;
  strategy: StrategyContract;
  startDate: string;
  endDate: string;
  initialCapital: number;
  finalCapital: number;
  totalReturn: number;
  annualizedReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  volatility: number;
  winRate: number;
  trades: TradeContract[];
}

export interface TradeContract {
  id: string;
  symbol: string;
  type: TradeType;
  status: TradeStatus;
  direction: TradeDirection;
  entryPrice: number;
  exitPrice: number;
  entryTime: string;
  exitTime: string;
  entryQuantity: number;
  exitQuantity: number;
  entryAmount: number;
  exitAmount: number;
  commission: number;
  slippage: number;
  tax: number;
  pnl: number;
  pnlPercent: number;
}
