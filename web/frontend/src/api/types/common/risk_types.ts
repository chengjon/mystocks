export interface BetaRequest {
  entity_type?: string;
  entity_id?: number;
  market_index?: string;
}

export interface BetaResult {
  beta?: number | null;
  correlation?: number | null;
  entity_type?: string | null;
  entity_id?: number | null;
  market_index?: string | null;
}

export interface Position {
  symbol?: string;
  symbol_name?: string | null;
  quantity?: number;
  available_quantity?: number;
  cost_price?: number;
  current_price?: number | null;
  market_value?: number;
  profit_loss?: number;
  profit_loss_percent?: number;
  last_update?: string;
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

export interface PositionsResponse {
  positions?: Position[];
  total_count?: number;
  total_market_value?: number;
  total_profit_loss?: number;
  total_profit_loss_percent?: number;
}

export interface RiskAlert {
  alert_id?: number;
  alert_type?: string;
  alert_level?: string;
  symbol?: string | null;
  message?: string;
  triggered_at?: string;
  is_read?: boolean;
}

export interface RiskAlertCreate {
  name?: string;
  metric_type?: string;
  threshold_value?: number;
  condition?: string;
  entity_type?: string;
  entity_id?: number | null;
  is_active?: boolean;
  notification_channels?: string[];
}

export interface RiskAlertListResponse {
  alerts?: RiskAlertResponse[];
}

export interface RiskAlertResponse {
  id?: number;
  name?: string;
  metric_type?: string;
  threshold_value?: number;
  condition?: string;
  entity_type?: string;
  entity_id?: number | null;
  is_active?: boolean;
  notification_channels?: string[];
  created_at?: string;
  updated_at?: string | null;
}

export interface RiskAlertSummary {
  total_count?: number;
  unread_count?: number;
  critical_count?: number;
  alerts?: RiskAlert[];
}

export interface RiskAlertUpdate {
  name?: string | null;
  metric_type?: string | null;
  threshold_value?: number | null;
  condition?: string | null;
  entity_type?: string | null;
  entity_id?: number | null;
  is_active?: boolean | null;
  notification_channels?: string[] | null;
}

export interface RiskDashboardResponse {
  metrics?: RiskMetricsSummary;
  active_alerts?: ActiveAlert[];
  risk_history?: RiskHistoryPoint[];
}

export interface RiskHistoryPoint {
  date?: string;
  var_95_hist?: number | null;
  cvar_95?: number | null;
  beta?: number | null;
}

export interface RiskMetricsHistoryResponse {
  metrics_history?: RiskHistoryPoint[];
}

export interface RiskMetricsSummary {
  var_95_hist?: number | null;
  cvar_95?: number | null;
  beta?: number | null;
}

export interface VaRCVaRRequest {
  entity_type?: string;
  entity_id?: number;
  confidence_level?: number;
}

export interface VaRCVaRResult {
  var_95_hist?: number | null;
  var_95_param?: number | null;
  var_99_hist?: number | null;
  cvar_95?: number | null;
  cvar_99?: number | null;
  entity_type?: string | null;
  entity_id?: number | null;
  confidence_level?: number | null;
}

