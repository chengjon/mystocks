export interface AhoCorasickMatchRequest {
  automaton_id?: string;
  time_series?: number[];
  threshold?: number;
}

export interface AhoCorasickTrainRequest {
  patterns?: PatternDefinition[];
  market?: string;
}

export interface AlgorithmConfig {
  enable_gpu?: boolean;
  gpu_memory_limit_mb?: number | null;
  enable_validation?: boolean;
  random_seed?: number | null;
}

export interface AlgorithmHealthStatus {
  service?: string;
  status?: string;
  algorithms_loaded?: boolean;
  gpu_available?: boolean;
  supported_algorithms?: number;
  timestamp?: string;
}

export interface AlgorithmInfo {
  type?: string;
  category?: string;
  description?: string;
  parameters?: Record<string, any>;
  use_cases?: string[];
  performance?: Record<string, any>;
}

export interface AlgorithmInfoRequest {
  algorithm_type?: AlgorithmType;
}

export interface AlgorithmMetadata {
  algorithm_type?: AlgorithmType;
  algorithm_name?: string;
  version?: string;
  description?: string | null;
}

export interface AlgorithmMetrics {
  accuracy?: number | null;
  precision?: number | null;
  recall?: number | null;
  f1_score?: number | null;
  training_time?: number | null;
  prediction_time?: number | null;
}

export interface AlgorithmPredictRequest {
  model_id?: string;
  features_data?: (List[number] | List[List[number]]);
  prediction_config?: Record<string, any> | null;
}

export interface AlgorithmResult {
  algorithm_id?: string;
  algorithm_type?: string;
  execution_timestamp?: string;
  status?: AlgorithmStatus;
  success?: boolean;
  message?: string | null;
  data?: Record<string, any> | null;
}

export type AlgorithmStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface AlgorithmTrainRequest {
  algorithm_type?: AlgorithmType;
  symbol?: string;
  features?: string[];
  labels?: string[] | null;
  config?: AlgorithmConfig;
  training_data?: Record<string, any> | null;
}

export type AlgorithmType = 'svm' | 'decision_tree' | 'naive_bayes' | 'brute_force' | 'knuth_morris_pratt' | 'boyer_moore_horspool' | 'aho_corasick' | 'hidden_markov_model' | 'bayesian_network' | 'n_gram' | 'neural_network';

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

export interface BacktestListResponse {
  total_count?: number;
  backtests?: BacktestResultSummary[];
  page?: number;
  page_size?: number;
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
  performance?: PerformanceMetrics;
  equity_curve?: EquityCurvePoint[];
  trades?: TradeRecord[];
  status?: BacktestStatus;
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
  status?: BacktestStatus;
  created_at?: string;
}

export type BacktestStatus = 'pending' | 'running' | 'completed' | 'failed';

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

export interface BayesianNetworkBuildRequest {
  symbols?: string[];
  relationships?: RelationshipDefinition[];
  time_window?: number;
}

export interface BayesianNetworkInferRequest {
  network_id?: string;
  trigger_event?: Record<string, any>;
  max_delay?: number;
}

export interface HMMPredictRequest {
  model_id?: string;
  current_observations?: string[];
}

export interface HMMTrainRequest {
  symbol?: string;
  observations?: string[];
  hmm_config?: HMMConfig;
}

export interface NGramPredictRequest {
  model_id?: string;
  current_sequence?: number[];
  n?: number;
}

export interface NGramTrainRequest {
  symbol?: string;
  n?: number;
  sequence_type?: string;
  window_size?: number;
}

export interface NeuralNetworkPredictRequest {
  model_id?: string;
  current_data?: Record<string, List[number]>;
}

export interface NeuralNetworkTrainRequest {
  symbol?: string;
  input_features?: string[];
  prediction_horizon?: number;
  lookback_window?: number;
  nn_config?: NeuralNetworkConfig;
}

export interface StrategyConfig {
  strategy_id?: number | null;
  user_id?: number;
  strategy_name?: string;
  strategy_type?: StrategyType;
  description?: string | null;
  parameters?: StrategyParameter[];
  max_position_size?: number;
  stop_loss_percent?: number | null;
  take_profit_percent?: number | null;
  status?: StrategyStatus;
  created_at?: string | null;
  updated_at?: string | null;
  tags?: string[];
}

export interface StrategyCreateRequest {
  user_id?: number;
  strategy_name?: string;
  strategy_type?: StrategyType;
  description?: string | null;
  parameters?: StrategyParameter[];
  max_position_size?: number;
  stop_loss_percent?: number | null;
  take_profit_percent?: number | null;
  tags?: string[];
}

export interface StrategyErrorResponse {
  error_code?: string;
  error_message?: string;
  details?: Record<string, any> | null;
  timestamp?: string;
}

export interface StrategyListResponse {
  total_count?: number;
  strategies?: StrategyConfig[];
  page?: number;
  page_size?: number;
}

export interface StrategyParameter {
  name?: string;
  value?: any;
  description?: string | null;
  data_type?: string;
}

export type StrategyStatus = 'draft' | 'active' | 'paused' | 'archived';

export type StrategyType = 'momentum' | 'mean_reversion' | 'breakout' | 'grid' | 'custom';

export interface StrategyUpdateRequest {
  strategy_name?: string | null;
  description?: string | null;
  parameters?: StrategyParameter[] | null;
  max_position_size?: number | null;
  stop_loss_percent?: number | null;
  take_profit_percent?: number | null;
  status?: StrategyStatus | null;
  tags?: string[] | null;
}

