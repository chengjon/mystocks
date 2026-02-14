
export interface StockRatingItem {
  股票代码?: string;
  股票名称?: string;
  目标价?: string;
  最新评级?: string;
  评级机构?: string;
  分析师?: string;
  行业?: string;
  评级日期?: string;
  摘要?: string;
}

export interface StockRatingsHealthResponse {
  status?: string;
  last_successful_scrape?: string | null;
  average_response_time?: number;
  success_rate?: number;
  total_scrapes?: number;
  recent_errors?: string[];
}

export interface StockRatingsRequest {
  max_pages?: number | null;
}

export interface StockRatingsResponse {
  data?: StockRatingItem[];
  total_count?: number;
  pages_scraped?: number;
  max_pages?: number;
  timestamp?: string;
  source?: string;
}

export interface StockRatingsSummary {
  total_ratings?: number;
  unique_stocks?: number;
  rating_agencies?: number;
  industries?: number;
  latest_update?: string;
  rating_distribution?: Record<string, any>;
}

export interface StockSymbolField {
  symbol?: string;
}

export interface StockSymbolModel {
  symbol?: string;
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

export interface SubscriptionInfo {
  plan?: string;
  status?: string;
  startDate?: string;
  endDate?: string;
  trialEndDate?: string | null;
  autoRenew?: boolean;
  features?: string[];
  limits?: Record<string, number>;
  nextBillingAmount?: number | null;
  nextBillingDate?: string | null;
}

export type SyncDirection = 'tdengine_to_postgresql' | 'postgresql_to_tdengine' | 'bidirectional';

export interface TDenginePITRRequest {
  target_time?: string;
  target_tables?: string[] | null;
  restore_to_database?: string | null;
}

export interface TaskConfig {
  task_id?: string;
  task_name?: string;
  task_type?: TaskType;
  task_module?: string;
  task_function?: string;
  description?: string | null;
  priority?: TaskPriority;
  schedule?: TaskSchedule | null;
  params?: Record<string, any>;
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
  status?: TaskStatus;
  start_time?: string | null;
  end_time?: string | null;
  duration?: number | null;
  result?: Record<string, any> | null;
  error_message?: string | null;
  log_path?: string | null;
  retry_count?: number;
}

export type TaskPriority = 100 | 200 | 500 | 800 | 900;

export interface TaskResponse {
  success?: boolean;
  message?: string;
  data?: Record<string, any> | null;
  task_id?: string | null;
  execution_id?: string | null;
}

export interface TaskSchedule {
  schedule_type?: string;
  cron_expression?: string | null;
  interval_seconds?: number | null;
  start_time?: string | null;
  end_time?: string | null;
  enabled?: boolean;
}

export interface TaskStatistics {
  task_id?: string;
  task_name?: string;
  total_executions?: number;
  success_count?: number;
  failed_count?: number;
  avg_duration?: number;
  last_execution_time?: string | null;
  last_status?: TaskStatus | null;
  success_rate?: number;
}

export type TaskStatus = 'pending' | 'running' | 'success' | 'failed' | 'paused' | 'cancelled';

export type TaskType = 'cron' | 'supervisor' | 'manual' | 'data_sync' | 'indicator_calc' | 'market_fetch' | 'data_processing' | 'strategy_backtest' | 'cache_cleanup' | 'market_sync' | 'notification' | 'health_check' | 'cache_warmup' | 'report_generation';

export interface TdxDataRequest {
  stock_code?: string;
  market?: string;
}

export interface TdxDataResponse {
  code?: string;
  market?: string;
  data?: Record<string, any>[];
  total_records?: number;
}

export interface TdxExportRequest {
  stock_code?: string;
  market?: string;
  output_format?: string;
}

export interface TdxHealthResponse {
  status?: string;
  tdx_connected?: boolean;
  timestamp?: string;
  server_info?: Record<string, any> | null;
}

export interface TechnicalIndicatorQueryModel {
  symbol?: string;
  indicators?: string[];
  period?: number | null;
  start_date?: string | null;
  end_date?: string | null;
}

export interface TimestampField {
  timestamp?: string;
}

export interface TopETFItem {
  symbol?: string;
  name?: string;
  latest_price?: number;
  change_percent?: number;
  volume?: number;
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

export interface TradeHistoryRequest {
  start_date?: string | null;
  end_date?: string | null;
  symbol?: string | null;
  page?: number;
  page_size?: number;
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

export interface UserPermissions {
  canTrade?: boolean;
  canWithdraw?: boolean;
  canUseStrategies?: boolean;
  canAccessAdvancedFeatures?: boolean;
  canViewMarketData?: boolean;
  canExportData?: boolean;
  canManageUsers?: boolean;
  canViewAnalytics?: boolean;
  maxStrategies?: number;
  maxWatchlists?: number;
  maxApiCalls?: number;
}

export interface UserPreferences {
  theme?: string;
  language?: string;
  timezone?: string;
  dateFormat?: string;
  timeFormat?: string;
  defaultDashboard?: string;
  watchlistLayout?: string;
  chartSettings?: Record<string, any>;
  notifications?: Record<string, boolean>;
  privacy?: Record<string, any>;
}

export interface UserProfileResponse {
  userId?: string;
  username?: string;
  email?: string;
  displayName?: string | null;
  avatar?: string | null;
  role?: string;
  status?: string;
  preferences?: UserPreferences;
  permissions?: UserPermissions;
  subscription?: SubscriptionInfo;
  statistics?: UserStatistics;
  createdAt?: string;
  lastLoginAt?: string;
  lastUpdateAt?: string;
}

export interface UserStatistics {
  totalTrades?: number;
  winningTrades?: number;
  losingTrades?: number;
  winRate?: number;
  totalPnL?: number;
  totalPnLPercent?: number;
  averageReturn?: number;
  sharpeRatio?: number;
  maxDrawdown?: number;
  totalCommission?: number;
  joinDate?: string;
  activeStrategies?: number;
  activeWatchlists?: number;
  followers?: number;
  following?: number;
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

export interface VolumeField {
  volume?: number;
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

export type WebSocketErrorCode = 'AUTH_REQUIRED' | 'AUTH_FAILED' | 'AUTH_TOKEN_EXPIRED' | 'INVALID_MESSAGE_FORMAT' | 'INVALID_ACTION' | 'INVALID_SYMBOL' | 'INVALID_PARAMETERS' | 'PERMISSION_DENIED' | 'RATE_LIMIT_EXCEEDED' | 'ROOM_NOT_FOUND' | 'SUBSCRIPTION_FAILED' | 'ALREADY_SUBSCRIBED' | 'INTERNAL_ERROR' | 'SERVICE_UNAVAILABLE' | 'TIMEOUT';

export interface WebSocketErrorMessage {
  type?: WebSocketMessageType;
  request_id?: string | null;
  error_code?: string;
  error_message?: string;
  error_details?: Record<string, any> | null;
  timestamp?: number;
  trace_id?: string | null;
}

export interface WebSocketHeartbeatMessage {
  type?: WebSocketMessageType;
  timestamp?: number;
  server_time?: number | null;
}

export type WebSocketMessageType = 'request' | 'subscribe' | 'unsubscribe' | 'ping' | 'response' | 'error' | 'notification' | 'pong';

export interface WebSocketNotificationMessage {
  type?: WebSocketMessageType;
  room?: string;
  event?: string;
  data?: any;
  timestamp?: number;
  server_time?: number;
}

export interface WebSocketRequestMessage {
  type?: WebSocketMessageType;
  request_id?: string;
  action?: string;
  payload?: Record<string, any>;
  user_id?: string | null;
  timestamp?: number;
  trace_id?: string | null;
}

export interface WebSocketResponseMessage {
  type?: WebSocketMessageType;
  request_id?: string;
  success?: boolean;
  data?: any;
  timestamp?: number;
  server_time?: number;
  trace_id?: string | null;
}

export interface WebSocketSubscribeMessage {
  type?: WebSocketMessageType;
  request_id?: string;
  room?: string;
  user_id?: string | null;
  timestamp?: number;
}

export interface WencaiCustomQueryRequest {
  query_text?: string;
  pages?: number;
}

export interface WencaiCustomQueryResponse {
  success?: boolean;
  message?: string;
  query_text?: string;
  total_records?: number;
  results?: Record<string, any>[];
  columns?: string[];
  fetch_time?: string;
}

export interface WencaiErrorResponse {
  success?: boolean;
  error?: string;
  message?: string;
  details?: Record<string, any> | null;
}

export interface WencaiHistoryItem {
  date?: string;
  total_records?: number;
  fetch_count?: number;
}

export interface WencaiHistoryResponse {
  query_name?: string;
  date_range?: string[];
  history?: WencaiHistoryItem[];
  total_days?: number;
}

export interface WencaiQueryInfo {
  id?: number;
  query_name?: string;
  query_text?: string;
  description?: string | null;
  is_active?: boolean;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface WencaiQueryListResponse {
  queries?: WencaiQueryInfo[];
  total?: number;
}

export interface WencaiQueryRequest {
  query_name?: string;
  pages?: number;
}

export interface WencaiQueryResponse {
  success?: boolean;
  message?: string;
  query_name?: string;
  total_records?: number;
  new_records?: number;
  duplicate_records?: number;
  table_name?: string;
  fetch_time?: string;
}

export interface WencaiRefreshRequest {
  pages?: number;
  force?: boolean;
}

