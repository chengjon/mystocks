
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

export type ParameterConfigType = 'default' | 'custom' | 'optimized';

