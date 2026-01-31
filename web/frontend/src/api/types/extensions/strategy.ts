/**
 * Strategy Domain Types
 *
 * Type definitions for trading strategies, backtesting, and performance analysis.
 * These types are frontend-specific ViewModel types that complement the auto-generated
 * strategy types from backend Pydantic schemas.
 */

// ========== Strategy Core Types ==========

/**
 * Main Strategy interface (ViewModel)
 */
export interface StrategyVM {
  id: string;
  name: string;
  description?: string;
  type: StrategyTypeVM;
  status: StrategyStatusVM;
  parameters: StrategyParametersVM;
  constraints?: StrategyConstraintsVM;
  risk_limits?: RiskLimitsVM;
  performance?: StrategyPerformanceVM;
  created_at: string;
  updated_at: string;
}

/**
 * Strategy type enumeration (ViewModel)
 */
export type StrategyTypeVM =
  | 'trend_following'      // 趋势跟踪
  | 'mean_reversion'       // 均值回归
  | 'momentum'            // 动量策略
  | 'breakout'            // 突破策略
  | 'arbitrage'           // 套利策略
  | 'statistical_arbitrage' // 统计套利
  | 'pairs_trading'       // 配对交易
  | 'market_neutral';     // 市场中性

/**
 * Strategy status enumeration (ViewModel)
 */
export type StrategyStatusVM =
  | 'draft'      // 草稿状态
  | 'testing'    // 测试中
  | 'active'     // 激活状态
  | 'inactive'   // 未激活
  | 'archived'   // 已归档
  | 'failed';    // 失败状态

/**
 * Backtest status enumeration
 */
export type BacktestStatus =
  | 'pending'      // 等待中
  | 'initializing' // 初始化中
  | 'running'      // 运行中
  | 'completed'    // 已完成
  | 'failed'       // 失败
  | 'cancelled';   // 已取消

// ========== Strategy Configuration Types ==========

/**
 * Strategy parameters interface (ViewModel)
 */
export interface StrategyParametersVM {
  // Technical indicators
  indicators?: IndicatorParametersVM;

  // Trading parameters
  trading?: TradingParametersVM;

  // Risk management parameters
  risk?: RiskParametersVM;

  // Custom parameters
  custom?: Record<string, any>;
}

/**
 * Indicator parameters (ViewModel)
 */
export interface IndicatorParametersVM {
  // Moving averages
  moving_average?: {
    fast_period: number;
    slow_period: number;
    signal_period?: number;
  };

  // RSI indicator
  rsi?: {
    period: number;
    overbought_level: number;
    oversold_level: number;
  };

  // MACD indicator
  macd?: {
    fast_period: number;
    slow_period: number;
    signal_period: number;
  };

  // Bollinger Bands
  bollinger_bands?: {
    period: number;
    standard_deviations: number;
  };

  // Additional indicators can be added here
  [key: string]: any;
}

/**
 * Trading parameters (ViewModel)
 */
export interface TradingParametersVM {
  // Position sizing
  position_size?: {
    type: 'fixed' | 'percentage' | 'kelly';
    value: number;
  };

  // Entry rules
  entry_rules?: TradeRuleVM[];

  // Exit rules
  exit_rules?: TradeRuleVM[];

  // Stop loss settings
  stop_loss?: {
    type: 'fixed' | 'trailing' | 'percentage';
    value: number;
  };

  // Take profit settings
  take_profit?: {
    type: 'fixed' | 'percentage' | 'ratio';
    value: number;
  };
}

/**
 * Risk management parameters
 */
export interface RiskParametersVM {
  // Risk management parameters
  max_position_size: number;
  max_portfolio_risk: number;
  max_drawdown_limit: number;
  max_volatility_limit: number;
  max_sector_concentration: number;
}

export interface TradeRuleVM {
  // Entry rules
  entry_conditions: string[];
  // Exit rules
  exit_conditions: string[];
  // Stop loss settings
  stop_loss_type: 'fixed' | 'trailing' | 'percentage';
  stop_loss_value: number;
  // Take profit settings
  take_profit_type: 'fixed' | 'percentage' | 'ratio';
  take_profit_value: number;
}

export interface StrategyConstraintsVM {
  // Allowed trading symbols
  allowed_symbols: string[];
  // Allowed sectors
  allowed_sectors: string[];
  // Forbidden symbols
  forbidden_symbols: string[];
  // Trading time restrictions
  trading_hours: {
    start: string; // HH:mm format
    end: string;   // HH:mm format
  };
  // Market condition filters
  market_conditions: string[];
}

export interface RiskLimitsVM {
  // Daily P&L limits
  daily_pnl_limit: number;
  // Single stock loss limits
  single_stock_loss_limit: number;
  // Total drawdown limits
  total_drawdown_limit: number;
  // Maximum holding period
  max_holding_period_days: number;
  // Maximum consecutive losses
  max_consecutive_losses: number;
  // Maximum loss per trade
  max_loss_per_trade: number;
}

export interface StrategyPerformanceVM {
  // Return metrics
  total_return: number;
  annualized_return: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  // Risk metrics
  max_drawdown: number;
  volatility: number;
  value_at_risk: number;
  // Trading metrics
  total_trades: number;
  win_rate: number;
  profit_factor: number;
  average_win: number;
  average_loss: number;
  // Additional metrics
  calmar_ratio: number;
  information_ratio: number;
}

export interface BacktestRequestVM {
  strategy_id: string;
  symbol: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  parameters: Record<string, any>;
  // Additional fields for backtest task tracking
  status?: 'pending' | 'running' | 'completed' | 'failed';
  created_at?: string;
  progress?: number;
  startTime?: string;
  result?: BacktestResultVM;
  symbols?: string[];
}

export interface BacktestTradeVM {
  trade_id: string;
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  price: number;
  timestamp: string;
  commission: number;
  pnl?: number;
}

export interface CreateStrategyRequestVM {
  name: string;
  description: string;
  type: StrategyTypeVM;
  parameters: StrategyParametersVM;
  constraints: StrategyConstraintsVM;
  risk_limits: RiskLimitsVM;
}

export interface UpdateStrategyRequestVM {
  id: string;
  name?: string;
  description?: string;
  parameters?: Partial<StrategyParametersVM>;
  constraints?: Partial<StrategyConstraintsVM>;
  risk_limits?: Partial<RiskLimitsVM>;
  status?: StrategyStatusVM;
}

export interface StrategyListResponseVM {
  strategies: Array<{
    id: string;
    name: string;
    type: StrategyTypeVM;
    status: StrategyStatusVM;
    performance: StrategyPerformanceVM;
    last_updated: string;
  }>;
  total: number;
  page: number;
  page_size: number;
}

export interface StrategyComparisonDataVM {
  strategies: Array<{
    strategy_id: string;
    strategy_name: string;
    performance: StrategyPerformanceVM;
    trades: BacktestTradeVM[];
    equity_curve: Array<{ date: string; value: number }>;
  }>;
  comparison_metrics: {
    best_performer: string;
    worst_performer: string;
    average_return: number;
    risk_adjusted_rankings: Array<{ strategy_id: string; rank: number }>;
  };
}

export interface StrategyOptimizationRequestVM {
  strategy_id: string;
  optimization_target: 'sharpe_ratio' | 'total_return' | 'max_drawdown' | 'win_rate';
  parameter_ranges: Record<string, { min: number; max: number; step: number }>;
  max_iterations: number;
  cross_validation_folds: number;
}

export interface StrategyOptimizationResultVM {
  strategy_id: string;
  optimization_target: string;
  best_parameters: Record<string, number>;
  best_performance: StrategyPerformanceVM;
  parameter_sensitivity: Array<{
    parameter_name: string;
    impact_score: number; // -1 to 1, higher means more impact
    optimal_value: number;
    range_tested: {
      min: number;
      max: number;
    };
  }>;
}

// ========== Type Aliases for Backward Compatibility ==========

/**
 * Backward compatibility alias
 * Use BacktestResultVM instead in new code
 * @deprecated Use BacktestResultVM
 */
export type BacktestResultVM = BacktestRequestVM;

/**
 * Strategy type alias for simpler imports
 */
export type Strategy = StrategyVM;

/**
 * StrategyPerformance type alias
 */
export type StrategyPerformance = StrategyPerformanceVM;