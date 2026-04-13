// Auto-generated types for analysis domain

export interface EquityCurveSummaryResponse {
  strategy_id?: string;
  period?: Record<string, string>;
  data_points?: number;
  final_value?: number;
  max_drawdown?: number;
  sharpe_ratio?: number;
}

export interface MonteCarloRequest {
  strategy_id?: string;
  symbol?: string;
  start_date?: string;
  end_date?: string;
  initial_capital?: number;
  iterations?: number;
}

export interface MonteCarloResponse {
  strategy_id?: string;
  symbol?: string;
  simulations_run?: number;
  return_distribution?: Record<string, number>;
  risk_metrics?: Record<string, number>;
  confidence_intervals?: Record<string, unknown>;
  equity_curves?: Record<string, unknown>[];
}

export interface PredefinedScenarioListResponse {
  scenarios?: PredefinedScenarioResponse[];
}

export interface PredefinedScenarioResponse {
  id?: string;
  name?: string;
  description?: string;
  shock_type?: string;
  severity?: number;
  duration_days?: number;
}

export interface SentimentRequest {
  symbol?: string;
  text?: string;
  source?: string | null;
}

export interface SentimentResponse {
  symbol?: string;
  sentiment?: string;
  confidence?: number;
  positive_score?: number;
  negative_score?: number;
  neutral_score?: number;
  key_phrases?: string[];
  analyzed_at?: string;
}

export interface StressTestHistoryItem {
  test_id?: string;
  date?: string;
  scenario?: string;
  impact?: number;
  passed?: boolean;
}

export interface StressTestHistoryResponse {
  portfolio_id?: string;
  tests?: StressTestHistoryItem[];
  total?: number;
}

export interface StressTestRequest {
  portfolio_id?: string;
  scenarios?: Record<string, unknown>[];
  initial_capital?: number;
}

export interface StressTestResponse {
  portfolio_id?: string;
  scenarios_tested?: number;
  results?: Record<string, unknown>[];
  recommendations?: string[];
}

export interface StressTestRunResponse {
  portfolio_id?: string;
  scenarios_tested?: number;
  results?: Record<string, unknown>[];
  recommendations?: string[];
}

export interface StressTestScenario {
  name?: string;
  shock_type?: string;
  severity?: number;
  duration_days?: number;
}
