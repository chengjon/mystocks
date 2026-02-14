
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

export type PredictionLabel = 'BUY' | 'SELL' | 'HOLD';

export interface PredictionResult {
  date?: string;
  predicted_price?: number;
  confidence?: number | null;
  prediction?: (string | number | List[number]);
  probabilities?: Record<string, number> | null;
  metadata?: Record<string, any> | null;
}

export interface PriceField {
  price?: number;
}

export interface RecoveryMetadata {
  backup_id?: string;
  recovery_type?: string;
  target_time?: string | null;
  target_tables?: string[] | null;
  dry_run?: boolean;
  success?: boolean;
  message?: string;
  start_time?: string;
  end_time?: string | null;
  duration_seconds?: number | null;
}

export interface RecoveryRequestBase {
  dry_run?: boolean;
  force?: boolean;
  backup_id?: string;
}

export interface RelationshipDefinition {
  from_symbol?: string;
  to_symbol?: string;
  delay?: number;
}

export interface ResponseModel {
  code?: string;
  message?: string;
  data?: any | null;
  timestamp?: number;
}

export interface ScheduledJobInfo {
  job_id?: string;
  job_type?: string;
  schedule?: string;
  next_run?: string | null;
  last_run?: string | null;
  status?: string;
  description?: string | null;
}

export interface SchedulerControlRequest {
  action?: 'start' | 'stop' | 'restart' | 'status';
  force?: boolean;
}

export interface SortParams {
  sort_by?: string;
  order?: string;
}

export interface SortRequest {
  sort_by?: string | null;
  sort_order?: string | null;
}

export interface StandardResponse {
  status?: string;
  code?: number;
  message?: string;
  timestamp?: string;
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

