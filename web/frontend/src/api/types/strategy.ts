// Auto-generated types for strategy domain
// Generated at: 2026-02-13T09:26:31.505160

export interface BacktestRequest {
  strategy_id?: string;
  symbol?: string;
  start_date?: string;
  end_date?: string;
  initial_capital?: number;
  position_size?: number;
}

export interface BacktestResponse {
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
