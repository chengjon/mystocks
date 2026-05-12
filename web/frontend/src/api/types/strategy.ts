// Auto-generated types for strategy domain

export type NonBlankString = string;

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

export type BatchAnalysisOperation = 'batch_backtest' | 'batch_screening' | 'batch_monitoring';

export interface BatchAnalysisRequest {
  operation?: BatchAnalysisOperation;
  symbols?: string[];
  start_date?: string;
  end_date?: string;
  options?: Record<string, unknown>;
}

export type MLStrategyType = 'svm' | 'decision_tree' | 'naive_bayes' | 'lstm' | 'transformer';

export type MLWorkbenchModelFamily = 'svm' | 'lightgbm';

export interface MLWorkbenchPredictionRequest {
  model_id?: NonBlankString;
  symbol?: NonBlankString;
  prediction_horizon?: number;
}

export interface MLWorkbenchTrainingRequest {
  model_family?: MLWorkbenchModelFamily;
  symbol?: NonBlankString;
  start_date?: string;
  end_date?: string;
  feature_window?: number;
  prediction_horizon?: number;
  parameters?: Record<string, unknown>;
}

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
  prediction?: Record<string, unknown>;
  confidence?: number;
  timestamp?: string;
}

export interface StrategyTrainingRequest {
  strategy_type?: MLStrategyType;
  symbol?: string;
  start_date?: string;
  end_date?: string;
  parameters?: Record<string, unknown> | null;
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
  indicators?: Record<string, unknown>;
  calculated_at?: string;
  data_points?: number;
  window_start?: string;
  window_end?: string;
}
