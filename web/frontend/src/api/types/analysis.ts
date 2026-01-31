// Auto-generated types for analysis domain
// Generated at: 2026-01-29T13:43:35.808209

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
  confidence_intervals?: Record<string, any>;
  equity_curves?: Record<string, any>[];
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

export interface StressTestRequest {
  portfolio_id?: string;
  scenarios?: Record<string, any>[];
  initial_capital?: number;
}

export interface StressTestResponse {
  portfolio_id?: string;
  scenarios_tested?: number;
  results?: Record<string, any>[];
  recommendations?: string[];
}

export interface StressTestScenario {
  name?: string;
  shock_type?: string;
  severity?: number;
  duration_days?: number;
}
