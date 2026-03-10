export interface WatchlistItem {
  symbol?: string;
  name?: string | null;
  current_price?: number | null;
  change_percent?: number | null;
  note?: string | null;
  added_at?: string | null;
}

export interface WatchlistSummary {
  total_count?: number;
  items?: WatchlistItem[];
  avg_change_percent?: number | null;
}

export interface RiskAlertSummary {
  total_count?: number;
  unread_count?: number;
  critical_count?: number;
  alerts?: unknown[];
}

export interface PerformanceMetrics {
  total_return?: number;
  annual_return?: number;
  benchmark_return?: number | null;
  alpha?: number | null;
  beta?: number | null;
  sharpe_ratio?: number;
  max_drawdown?: number;
  volatility?: number;
  total_trades?: number;
  win_rate?: number;
  profit_factor?: number;
  calmar_ratio?: number | null;
  sortino_ratio?: number | null;
}

export interface OrderRequest {
  symbol?: string;
  direction?: string;
  order_type?: string;
  price?: number | null;
  quantity?: number;
}

export interface OrderResponse {
  order_id?: string;
  symbol?: string;
  direction?: string;
  order_type?: string;
  price?: number | null;
  quantity?: number;
  filled_quantity?: number;
  average_price?: number | null;
  status?: string;
  commission?: number | null;
  created_at?: string;
  updated_at?: string | null;
}

export interface CancelOrderRequest {
  order_id?: string;
}

export interface CancelOrderResponse {
  order_id?: string;
  success?: boolean;
  message?: string;
  cancelled_quantity?: number;
  remaining_quantity?: number;
  cancelled_at?: string;
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

export interface TradeRecord {
  trade_id?: number;
  symbol?: string;
  trade_date?: string;
  action?: string;
  price?: number;
  quantity?: number;
  amount?: number;
  commission?: number;
  profit_loss?: number | null;
}

export interface TradeHistoryItem {
  trade_id?: string;
  order_id?: string;
  symbol?: string;
  direction?: string;
  price?: number;
  quantity?: number;
  amount?: number;
  commission?: number;
  trade_time?: string;
  trade_type?: string;
}

export interface TradeHistoryResponse {
  trades?: TradeHistoryItem[];
  total_count?: number;
  total_amount?: number;
  total_commission?: number;
  page?: number;
  page_size?: number;
}

export interface TradeOrderModel {
  symbol?: string;
  order_type?: string;
  price?: number;
  quantity?: number;
  order_validity?: string | null;
}

export interface PortfolioSummary {
  total_market_value?: number;
  total_cost?: number;
  total_profit_loss?: number;
  total_profit_loss_percent?: number;
  position_count?: number;
  positions?: PositionItem[];
}

export interface AccountInfo {
  account_id?: string;
  account_type?: string;
  total_assets?: number;
  cash?: number;
  market_value?: number;
  frozen_cash?: number | null;
  total_profit_loss?: number;
  profit_loss_percent?: number;
  risk_level?: string;
  last_update?: string;
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

export interface RiskMetricsSummary {
  var_95_hist?: number | null;
  cvar_95?: number | null;
  beta?: number | null;
}

export interface RiskDashboardResponse {
  metrics?: RiskMetricsSummary;
  active_alerts?: unknown[];
  risk_history?: unknown[];
}

export interface DashboardResponse {
  user_id?: number;
  trade_date?: string;
  generated_at?: string;
  market_overview?: unknown | null;
  watchlist?: WatchlistSummary | null;
  portfolio?: PortfolioSummary | null;
  risk_alerts?: RiskAlertSummary | null;
  data_source?: string;
  cache_hit?: boolean;
}

export interface DashboardRequest {
  user_id?: number;
  trade_date?: string | null;
  include_market_overview?: boolean;
  include_watchlist?: boolean;
  include_portfolio?: boolean;
  include_risk_alerts?: boolean;
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

export interface RiskHistoryPoint {
  date?: string;
  var_95_hist?: number | null;
  cvar_95?: number | null;
  beta?: number | null;
}

export interface RiskMetricsHistoryResponse {
  metrics_history?: RiskHistoryPoint[];
}

export interface TradeHistoryRequest {
  start_date?: string | null;
  end_date?: string | null;
  symbol?: string | null;
  page?: number;
  page_size?: number;
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

export interface WatchlistResponse {
  id?: string;
  name?: string;
  description?: string | null;
  isDefault?: boolean;
  isPublic?: boolean;
  owner?: Record<string, string>;
  stocks?: WatchlistStockResponse[];
  statistics?: Record<string, unknown>;
  tags?: string[];
  createdAt?: string;
  updatedAt?: string;
  lastViewedAt?: string | null;
  sortOrder?: number;
}

export interface WatchlistStockResponse {
  symbol?: string;
  name?: string;
  market?: string;
  currentPrice?: number;
  changeAmount?: number;
  changePercent?: number;
  volume?: number;
  marketCap?: number;
  pe?: number | null;
  pb?: number | null;
  addedAt?: string;
  notes?: string | null;
  alerts?: Record<string, unknown>[];
  customFields?: Record<string, unknown> | null;
}
