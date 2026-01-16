// Auto-generated types for trading domain
// Generated at: 2026-01-15T21:06:03.935874

export interface PositionCreate {
  symbol?: string;
  quantity?: number;
  price?: number;
}

export interface PositionItem {
  symbol?: string;
  name?: string | null;
  quantity?: number;
  avg_cost?: number;
  current_price?: number | null;
  market_value?: number | null;
  profit_loss?: number | null;
  profit_loss_percent?: number | null;
  position_percent?: number | null;
}

export interface PositionResponse {
  position_id?: string;
  symbol?: string;
  name?: string;
  quantity?: number;
  average_cost?: number;
  current_price?: number;
  market_value?: number;
  unrealized_pnl?: number;
  realized_pnl?: number;
  weight?: number;
  created_at?: string;
  updated_at?: string;
}

export interface PositionUpdate {
  quantity?: number | null;
  stop_loss?: number | null;
  take_profit?: number | null;
}

export interface TradingSessionCreate {
  symbol?: string;
  strategy_id?: string | null;
  initial_capital?: number;
  position_size?: number;
  risk_threshold?: number;
}

export interface TradingSessionResponse {
  session_id?: string;
  symbol?: string;
  strategy_id?: string | null;
  status?: string;
  current_capital?: number;
  current_positions?: number;
  daily_pnl?: number;
  total_pnl?: number;
  created_at?: string;
  updated_at?: string;
}

export interface TradingSessionUpdate {
  action?: string;
  reason?: string | null;
}
