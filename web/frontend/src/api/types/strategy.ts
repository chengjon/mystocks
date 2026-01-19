// Auto-generated types for strategy domain
// Generated at: 2026-01-19T22:34:18.299421

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
