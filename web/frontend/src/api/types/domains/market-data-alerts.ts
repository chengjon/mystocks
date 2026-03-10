import { Dict } from './system-base.ts';

export interface AnnouncementBase {
  stock_code?: string;
  stock_name?: string | null;
  announcement_title?: string;
  announcement_type?: string | null;
  publish_date?: string;
  publish_time?: string | null;
  url?: string | null;
  content?: string | null;
  summary?: string | null;
  keywords?: unknown[];
  importance_level?: number;
  data_source?: string;
  source_id?: string | null;
  sentiment?: string | null;
  impact_score?: number | null;
}

export interface AnnouncementStatsResponse {
  total_count?: number;
  today_count?: number;
  important_count?: number;
  by_source?: Record<string, unknown>;
  by_type?: Record<string, unknown>;
  by_sentiment?: Record<string, unknown>;
}

export interface RealTimeQuoteResponse {
  code?: string;
  name?: string;
  price?: number;
  pre_close?: number;
  open?: number;
  high?: number;
  low?: number;
  volume?: number;
  amount?: number;
  bid1?: number;
  bid1_volume?: number;
  ask1?: number;
  ask1_volume?: number;
  timestamp?: string;
  change?: number | null;
  change_pct?: number | null;
}

export interface FundFlowItem {
  trade_date?: string;
  main_net_inflow?: number;
  main_net_inflow_rate?: number;
  super_large_net_inflow?: number;
  large_net_inflow?: number;
  medium_net_inflow?: number;
  small_net_inflow?: number;
}

export interface FundFlowDataResponse {
  fund_flow?: FundFlowItem[];
  total?: number;
  symbol?: string | null;
  timeframe?: string | null;
}

export interface DragonTigerListResponse {
  id?: number;
  symbol?: string;
  stock_name?: string | null;
  trade_date?: string;
  reason?: string | null;
  total_buy_amount?: number | null;
  total_sell_amount?: number | null;
  net_amount?: number | null;
  institution_buy_count?: number;
  institution_sell_count?: number;
  institution_net_amount?: number | null;
  detail_data?: Dict | null;
  impact_score?: number | null;
}

export interface StockListResponse {
  success?: boolean;
  data?: Record<string, unknown>;
  timestamp?: string;
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

export interface ChipRaceResponse {
  id?: number;
  symbol?: string;
  name?: string;
  trade_date?: string;
  race_type?: string;
  latest_price?: number;
  change_percent?: number;
  prev_close?: number;
  open_price?: number;
  race_amount?: number;
  race_amplitude?: number;
  race_commission?: number;
  race_transaction?: number;
  race_ratio?: number;
  created_at?: string | null;
}

export interface LongHuBangResponse {
  id?: number;
  symbol?: string;
  name?: string;
  trade_date?: string;
  reason?: string | null;
  buy_amount?: number;
  sell_amount?: number;
  net_amount?: number;
  turnover_rate?: number;
  institution_buy?: number | null;
  institution_sell?: number | null;
  created_at?: string | null;
}

export interface ActiveAlert {
  id?: number;
  name?: string;
  metric_type?: string;
  threshold_value?: number;
}

export type AlertLevel = 'info' | 'warning' | 'critical';

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

export type AlertRuleType =
  | 'price_change'
  | 'volume_surge'
  | 'technical_break'
  | 'limit_up'
  | 'limit_down'
  | 'dragon_tiger';

export interface AlertRuleUpdate {
  rule_name?: string | null;
  description?: string | null;
  parameters?: Dict | null;
  trigger_conditions?: Dict | null;
  notification_config?: Dict | null;
  priority?: number | null;
  is_active?: boolean | null;
}

export interface AnnouncementMonitorRecordResponse {
  id?: number;
  rule_id?: number;
  announcement_id?: number;
  matched_keywords?: unknown[];
  triggered_at?: string;
  notified?: boolean;
  notified_at?: string | null;
  notification_result?: string | null;
  rule_name?: string | null;
  announcement_title?: string | null;
}

export interface AnnouncementMonitorRuleBase {
  rule_name?: string;
  keywords?: unknown[];
  announcement_types?: unknown[];
  stock_codes?: unknown[];
  min_importance_level?: number;
  notify_enabled?: boolean;
  notify_channels?: unknown[];
}

export interface AnnouncementMonitorRuleUpdate {
  rule_name?: string | null;
  keywords?: unknown[] | null;
  announcement_types?: unknown[] | null;
  stock_codes?: unknown[] | null;
  min_importance_level?: number | null;
  notify_enabled?: boolean | null;
  notify_channels?: unknown[] | null;
  is_active?: boolean | null;
}

export interface AnnouncementSearchRequest {
  keywords?: string | null;
  stock_code?: string | null;
  announcement_type?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  min_importance_level?: number | null;
  data_source?: string | null;
  page?: number;
  page_size?: number;
}
