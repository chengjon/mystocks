// Auto-generated types for strategy domain
// Generated at: 2026-01-14T14:57:47.575152

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

// ViewModel types for frontend adapters
// Redefine Strategy with additional fields used by adapter
export interface Strategy {
  id?: string;
  strategy_id?: string;
  strategy_type?: string;
  name?: string;
  description?: string;
  trained?: boolean;
  performance?: StrategyPerformance | Record<string, number> | null;
  created_at?: string;
  type?: 'trend_following' | 'mean_reversion' | 'momentum';
  status?: 'active' | 'inactive' | 'testing';
  createdAt?: Date;
  updatedAt?: Date;
  parameters?: Record<string, any> | null;
}

export interface StrategyPerformance {
  total_return?: number;
  totalReturn?: number;
  annualized_return?: number;
  annualReturn?: number;
  sharpe_ratio?: number;
  sharpeRatio?: number;
  max_drawdown?: number;
  maxDrawdown?: number;
  win_rate?: number;
  winRate?: number;
  total_trades?: number;
  profit_loss_ratio?: number;
  profitLossRatio?: number;
}

// Redefine BacktestTask with additional fields used by adapter
export interface BacktestTask {
  task_id?: string;
  taskId?: string;
  strategy_id?: string;
  strategyId?: string;
  start_date?: string;
  end_date?: string;
  initial_capital?: number;
  position_size?: number;
  status?: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
  startTime?: Date;
  endTime?: Date;
  result?: BacktestResult;
  error?: string;
}

// Redefine BacktestResult with additional fields used by adapter
export interface BacktestResult {
  strategy_id?: string;
  strategyId?: string;
  taskId?: string;
  total_return?: number;
  totalReturn?: number;
  annualized_return?: number;
  annualReturn?: number;
  sharpe_ratio?: number;
  sharpeRatio?: number;
  max_drawdown?: number;
  maxDrawdown?: number;
  win_rate?: number;
  winRate?: number;
  total_trades?: number;
  totalTrades?: number;
  profit_factor?: number;
  profitFactor?: number;
  equity_curve?: number[];
  trades?: any[];
  performance_metrics?: Record<string, any>;
  backtest_duration_ms?: number;
}

export type BacktestRequest = BacktestTask;
export type BacktestResponse = BacktestResult;

export interface StrategyListResponse {
  strategies?: StrategyInfo[];
  total_count?: number;
}

export interface CreateStrategyRequest {
  name?: string;
  description?: string;
  strategy_type?: string;
  parameters?: Record<string, any> | null;
}

export interface UpdateStrategyRequest {
  strategy_id?: string;
  name?: string;
  description?: string;
  parameters?: Record<string, any> | null;
}

export type BacktestParams = BacktestRequest;
