// Auto-generated types for strategy domain
// Generated at: 2026-01-15T21:06:03.935517

import type { BacktestResultSummary, BacktestTrade } from './common';

export interface BacktestRequest {
  strategy_name?: string;
  symbols?: string[];
  start_date?: string;
  end_date?: string;
  initial_capital?: number;
  parameters?: Record<string, any>;
  strategy_id?: number;
  symbol?: string;
  position_size?: number;
  user_id?: number;
  commission_rate?: number;
  slippage_rate?: number;
  benchmark?: string | null;
  include_analysis?: boolean;
}

export interface BacktestResponse {
  task_id?: string;
  status?: string;
  summary?: BacktestResultSummary | null;
  equity_curve?: Record<string, any>[];
  trades?: BacktestTrade[];
  error_message?: string | null;
  strategy_id?: string;
  total_return?: number;
  annualized_return?: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  win_rate?: number;
  total_trades?: number;
  backtest_duration_ms?: number;
}

export type MLStrategyType = 'svm' | 'decision_tree' | 'naive_bayes' | 'lstm' | 'transformer';

export interface StrategyInfo {
  strategy_id?: string;
  strategy_type?: string;
  name?: string;
  description?: string;
  trained?: boolean;
  performance?: Record<string, number> | null;
  created_at?: string;
}

export interface StrategyPredictionRequest {
  strategy_id?: string;
  symbol?: string;
  prediction_horizon?: number;
}

export interface StrategyPredictionResponse {
  strategy_id?: string;
  symbol?: string;
  prediction?: Record<string, any>;
  confidence?: number;
  timestamp?: string;
}

export interface StrategyTrainingRequest {
  strategy_type?: MLStrategyType;
  symbol?: string;
  start_date?: string;
  end_date?: string;
  parameters?: Record<string, any> | null;
}

export interface StrategyTrainingResponse {
  strategy_id?: string;
  strategy_type?: string;
  training_accuracy?: number;
  validation_score?: number;
  feature_importance?: Record<string, number>;
  training_duration_ms?: number;
  model_size_bytes?: number;
}

export interface TechnicalIndicatorResponse {
  symbol?: string;
  indicators?: Record<string, any>;
  calculated_at?: string;
}

// ============================================
// ViewModel Types for Adapters and Components
// ============================================

// Backtest Result ViewModel (snake_case for API compatibility)
export interface BacktestResultVM {
  task_id?: string;
  strategy_id?: string;
  total_return?: number;
  annualized_return?: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  win_rate?: number;
  total_trades?: number;
  profit_factor?: number;
  equity_curve?: Array<{ date: string; value: number; drawdown?: number }>;
  trades?: Array<{
    id: string;
    symbol: string;
    type: 'buy' | 'sell';
    quantity: number;
    price: number;
    timestamp: Date;
    profitLoss?: number;
    profitLossPercent?: number;
  }>;
  performance_metrics?: {
    total_return?: number;
    annual_return?: number;
    monthly_return?: number;
    weekly_return?: number;
    daily_return?: number;
    sharpe_ratio?: number;
    sortino_ratio?: number;
    calmar_ratio?: number;
    max_drawdown?: number;
    avg_drawdown?: number;
    max_drawdown_duration?: number;
    win_rate?: number;
    profit_factor?: number;
    avg_profit?: number;
    avg_loss?: number;
    best_trade?: number;
    worst_trade?: number;
    total_trades?: number;
    winning_trades?: number;
    losing_trades?: number;
    avg_trade_duration?: number;
    expectency?: number;
  };
}

// Backtest Task ViewModel
export interface BacktestTask {
  task_id?: string;
  strategy_id?: string;
  status?: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
  started_at?: string;
  completed_at?: string | null;
  error?: string | null;
  result?: BacktestResultVM | null;
}

// Strategy Performance ViewModel (camelCase for frontend)
export interface StrategyPerformance {
  totalReturn?: number;
  annualizedReturn?: number;
  sharpeRatio?: number;
  maxDrawdown?: number;
  winRate?: number;
  profitLossRatio?: number;
  // Also support snake_case
  total_return?: number;
  annualized_return?: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  win_rate?: number;
  profit_loss_ratio?: number;
}

// Strategy ViewModel
export interface Strategy {
  id?: string;
  strategy_id?: string;
  name?: string;
  description?: string;
  type?: 'trend_following' | 'mean_reversion' | 'momentum';
  status?: 'active' | 'inactive' | 'testing';
  createdAt?: Date;
  updatedAt?: Date;
  parameters?: Record<string, any>;
  performance?: StrategyPerformance | null;
}

// Re-export from common.ts for convenience
import type {
  StrategyCreateRequest,
  StrategyUpdateRequest,
  StrategyListResponse,
  BacktestRequest as BacktestRequestFromCommon,
} from './common';
export type {
  StrategyCreateRequest as CreateStrategyRequest,
  StrategyUpdateRequest as UpdateStrategyRequest,
  StrategyListResponse,
  BacktestRequestFromCommon as BacktestParams,
};
