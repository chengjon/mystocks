export type AlertLevel = 'info' | 'warning' | 'critical';

export interface AlertRecordResponse {
  id?: number;
  rule_id?: number | null;
  rule_name?: string | null;
  symbol?: string;
  stock_name?: string | null;
  alert_time?: string;
  alert_type?: string;
  alert_level?: string;
  alert_title?: string | null;
  alert_message?: string | null;
  alert_details?: Dict | null;
  snapshot_data?: Dict | null;
  is_read?: boolean;
  is_handled?: boolean;
  created_at?: string;
}

export interface AlertRuleCreate {
  rule_name?: string;
  rule_type?: AlertRuleType;
  description?: string | null;
  symbol?: string | null;
  stock_name?: string | null;
  parameters?: Dict;
  trigger_conditions?: Dict;
  notification_config?: Dict;
  priority?: number;
  is_active?: boolean;
}

export interface AlertRuleResponse {
  id?: number;
  rule_name?: string;
  rule_type?: string;
  description?: string | null;
  symbol?: string | null;
  stock_name?: string | null;
  parameters?: Dict;
  trigger_conditions?: Dict;
  notification_config?: Dict;
  is_active?: boolean;
  priority?: number;
  created_at?: string;
  updated_at?: string;
}

export type AlertRuleType = 'price_change' | 'volume_surge' | 'technical_break' | 'limit_up' | 'limit_down' | 'dragon_tiger';

export interface AlertRuleUpdate {
  rule_name?: string | null;
  description?: string | null;
  parameters?: Dict | null;
  trigger_conditions?: Dict | null;
  notification_config?: Dict | null;
  priority?: number | null;
  is_active?: boolean | null;
}

export interface MonitoringSummaryResponse {
  total_stocks?: number;
  limit_up_count?: number;
  limit_down_count?: number;
  strong_up_count?: number;
  strong_down_count?: number;
  avg_change_percent?: number | null;
  total_amount?: number | null;
  active_alerts?: number;
  unread_alerts?: number;
}

export interface NotificationResponse {
  id?: string;
  type?: string;
  title?: string;
  message?: string;
  data?: Record<string, any> | null;
  priority?: string;
  isRead?: boolean;
  createdAt?: string;
  expiresAt?: string | null;
  actionUrl?: string | null;
  actionText?: string | null;
  icon?: string | null;
  category?: string;
}

export interface NotificationTestRequest {
  notification_type?: string;
  config_data?: Record<string, any>;
}

export interface NotificationTestResponse {
  success?: boolean;
  message?: string;
}

export interface WatchlistItem {
  symbol?: string;
  name?: string | null;
  current_price?: number | null;
  change_percent?: number | null;
  note?: string | null;
  added_at?: string | null;
}

export interface WatchlistResponse {
  id?: string;
  name?: string;
  description?: string | null;
  isDefault?: boolean;
  isPublic?: boolean;
  owner?: Record<string, string>;
  stocks?: WatchlistStockResponse[];
  statistics?: Record<string, any>;
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
  alerts?: Record<string, any>[];
  customFields?: Record<string, any> | null;
}

export interface WatchlistSummary {
  total_count?: number;
  items?: WatchlistItem[];
  avg_change_percent?: number | null;
}

