import { TradeRecord } from './trading-ops';

export interface StrategyConfig {
  strategy_id?: number | null;
  user_id?: number;
  strategy_name?: string;
  strategy_type?: string;
  description?: string | null;
  parameters?: StrategyParameter[];
  max_position_size?: number;
  stop_loss_percent?: number | null;
  take_profit_percent?: number | null;
  status?: string;
  created_at?: string | null;
  updated_at?: string | null;
  tags?: string[];
}

export interface StrategyCreateRequest {
  user_id?: number;
  strategy_name?: string;
  strategy_type?: string;
  description?: string | null;
  parameters?: StrategyParameter[];
  max_position_size?: number;
  stop_loss_percent?: number | null;
  take_profit_percent?: number | null;
  tags?: string[];
}

export interface StrategyUpdateRequest {
  strategy_name?: string | null;
  description?: string | null;
  parameters?: StrategyParameter[] | null;
  max_position_size?: number | null;
  stop_loss_percent?: number | null;
  take_profit_percent?: number | null;
  status?: string | null;
  tags?: string[] | null;
}

export interface StrategyParameter {
  name?: string;
  value?: unknown;
  description?: string | null;
  data_type?: string;
}

export interface BacktestExecuteRequest {
  strategy_id?: number;
  user_id?: number;
  symbols?: string[];
  start_date?: string;
  end_date?: string;
  initial_capital?: number;
  commission_rate?: number;
  slippage_rate?: number;
  benchmark?: string | null;
}

export interface BacktestResult {
  backtest_id?: number;
  strategy_id?: number;
  user_id?: number;
  symbols?: string[];
  start_date?: string;
  end_date?: string;
  initial_capital?: number;
  final_capital?: number;
  performance?: unknown;
  equity_curve?: unknown[];
  trades?: TradeRecord[];
  status?: string;
  created_at?: string;
  completed_at?: string | null;
  error_message?: string | null;
}

export interface BacktestResultSummary {
  total_return?: number;
  annualized_return?: number;
  max_drawdown?: number;
  sharpe_ratio?: number;
  win_rate?: number;
  total_trades?: number;
  backtest_id?: number;
  strategy_id?: number;
  strategy_name?: string;
  symbols?: string[];
  date_range?: string;
  status?: string;
  created_at?: string;
}

export interface BacktestTrade {
  symbol?: string;
  entry_date?: string;
  exit_date?: string;
  entry_price?: number;
  exit_price?: number;
  quantity?: number;
  pnl?: number;
  return_pct?: number;
}

export interface AlgorithmConfig {
  enable_gpu?: boolean;
  gpu_memory_limit_mb?: number | null;
  enable_validation?: boolean;
  random_seed?: number | null;
}

export interface AlgorithmInfo {
  type?: string;
  category?: string;
  description?: string;
  parameters?: Record<string, unknown>;
  use_cases?: string[];
  performance?: Record<string, unknown>;
}

export interface AlgorithmMetrics {
  accuracy?: number | null;
  precision?: number | null;
  recall?: number | null;
  f1_score?: number | null;
  training_time?: number | null;
  prediction_time?: number | null;
}

export interface AlgorithmResult {
  algorithm_id?: string;
  algorithm_type?: string;
  execution_timestamp?: string;
  status?: string;
  success?: boolean;
  message?: string | null;
  data?: Record<string, unknown> | null;
}

export interface AlgorithmTrainRequest {
  algorithm_type?: string;
  symbol?: string;
  features?: string[];
  labels?: string[] | null;
  config?: AlgorithmConfig;
  training_data?: Record<string, unknown> | null;
}

export interface ModelInfo {
  name?: string;
  path?: string;
  trained_at?: string;
  test_rmse?: number;
  test_r2?: number;
  train_samples?: number | null;
  test_samples?: number | null;
  feature_dim?: number | null;
  model_id?: string;
  algorithm_type?: string;
  symbol?: string;
  created_at?: string;
  metrics?: AlgorithmMetrics | null;
  config?: Record<string, unknown>;
  status?: string;
}

export interface ModelTrainRequest {
  stock_code?: string;
  market?: string;
  step?: number;
  test_size?: number;
  model_name?: string;
  model_params?: Record<string, unknown> | null;
}

export interface PredictionResult {
  date?: string;
  predicted_price?: number;
  confidence?: number | null;
  prediction?: unknown;
  probabilities?: Record<string, number> | null;
  metadata?: Record<string, unknown> | null;
}

export interface FeatureGenerationResponse {
  success?: boolean;
  message?: string;
  total_samples?: number;
  feature_dim?: number;
  step?: number;
  feature_columns?: string[];
  metadata?: Record<string, unknown>;
}

export interface TaskConfig {
  task_id?: string;
  task_name?: string;
  task_type?: string;
  task_module?: string;
  task_function?: string;
  description?: string | null;
  priority?: number;
  schedule?: unknown | null;
  params?: Record<string, unknown>;
  timeout?: number;
  retry_count?: number;
  retry_delay?: number;
  dependencies?: string[];
  tags?: string[];
  auto_restart?: boolean;
  stop_on_error?: boolean;
}

export interface TaskExecution {
  execution_id?: string;
  task_id?: string;
  status?: string;
  start_time?: string | null;
  end_time?: string | null;
  duration?: number | null;
  result?: Record<string, unknown> | null;
  error_message?: string | null;
  log_path?: string | null;
  retry_count?: number;
}

export interface TaskStatistics {
  task_id?: string;
  task_name?: string;
  total_executions?: number;
  success_count?: number;
  failed_count?: number;
  avg_duration?: number;
  last_execution_time?: string | null;
  last_status?: string | null;
  success_rate?: number;
}
