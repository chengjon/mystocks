// System Base & Common Infrastructure Types

export type Dict = Record<string, unknown>;
export type List<T = unknown> = T[];

export interface UnifiedResponse<T = unknown> {
  success: boolean;
  code: number;
  message: string;
  data: T;
  timestamp: string;
  request_id: string;
  process_time?: string;
  errors?: unknown;
}

export interface APIResponse {
  success?: boolean;
  data?: Record<string, unknown> | null;
  error?: ErrorDetail | null;
  timestamp?: string;
  code?: number;
  message?: string;
  request_id?: string;
}

export interface BaseResponse {
  success?: boolean;
  message?: string;
  data?: unknown | null;
  timestamp?: string;
  request_id?: string | null;
}

export interface StandardResponse {
  status?: string;
  code?: number;
  message?: string;
  timestamp?: string;
}

export interface ResponseModel {
  code?: string;
  message?: string;
  data?: unknown | null;
  timestamp?: number;
}

export interface MessageResponse {
  success?: boolean;
  message?: string;
  data?: Record<string, unknown> | null;
}

export type MessageStatus = 'pending' | 'in_progress' | 'success' | 'failed' | 'retry' | 'dead_letter';

export interface ErrorDetail {
  error_code?: string;
  error_message?: string;
  details?: Record<string, unknown> | null;
}

export interface ErrorResponse {
  error?: string;
  detail?: string | null;
  message?: string;
  error_code?: string;
  error_message?: string;
  details?: Record<string, unknown> | null;
  timestamp?: string;
  success?: 'False';
  path?: string | null;
  request_id?: string | null;
}

export interface ErrorResponseModel {
  code?: string;
  message?: string;
  details?: unknown | null;
  timestamp?: number;
}

export interface CommonError {
  code?: number;
  message?: string;
  data?: Record<string, unknown> | null;
  detail?: string | null;
}

export type OperationType = 'insert' | 'update' | 'delete' | 'bulk_insert';

export interface PaginationInfo {
  page?: number;
  page_size?: number;
  total?: number;
  pages?: number | null;
}

export interface PaginationModel {
  page?: number;
  page_size?: number;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
}

export interface PaginationRequest {
  page?: number;
  page_size?: number;
}

export interface PagedResponse<T = unknown> {
  success?: boolean;
  message?: string;
  data?: T[];
  total?: number;
  page?: number;
  page_size?: number;
  total_pages?: number;
  has_next?: boolean;
  has_prev?: boolean;
  timestamp?: string;
}

export interface PaginatedResponse<T = unknown> {
  items?: T[];
  total?: number;
  page?: number;
  page_size?: number;
  total_pages?: number;
  data?: T[];
}

export interface SortParams {
  sort_by?: string;
  order?: string;
}

export interface SortRequest {
  sort_by?: string | null;
  sort_order?: string | null;
}

export interface FilterParams {
}

export interface FilterRequest {
  filters?: Record<string, unknown> | null;
}

export interface DateField {
  date?: string;
}

export interface DateRangeModel {
  start_date?: string;
  end_date?: string;
}

export interface TimestampField {
  timestamp?: string;
}

export interface MillisecondTimestampField {
  timestamp?: number;
}

export interface CurrencyField {
  amount?: number;
}

export interface PercentageField {
  percentage?: number;
}

export interface PriceField {
  price?: number;
}

export interface VolumeField {
  volume?: number;
}

export interface StockSymbolField {
  symbol?: string;
}

export interface StockSymbolModel {
  symbol?: string;
}

export interface BatchOperation {
  operation?: string;
  data?: Record<string, unknown>;
  id?: string | null;
}

export interface BatchOperationRequest {
  operations?: BatchOperation[];
  parallel_execution?: boolean;
  max_concurrent?: number | null;
}

export interface BatchOperationResult {
  total_operations?: number;
  successful_operations?: number;
  failed_operations?: number;
  results?: unknown[];
  execution_time?: number;
  id?: string | null;
  success?: boolean;
  data?: unknown | null;
  error?: string | null;
}

export interface HealthCheckResponse {
  status?: string;
  version?: string;
  uptime?: number;
  timestamp?: string;
  services?: Record<string, unknown> | null;
}

export interface BaseEvent {
  event_type?: string;
  timestamp?: string;
  version?: string;
}

export interface WebSocketErrorMessage {
  type?: string;
  request_id?: string | null;
  error_code?: string;
  error_message?: string;
  error_details?: Record<string, unknown> | null;
  timestamp?: number;
  trace_id?: string | null;
}

export interface WebSocketHeartbeatMessage {
  type?: string;
  timestamp?: number;
  server_time?: number | null;
}

export interface WebSocketNotificationMessage {
  type?: string;
  room?: string;
  event?: string;
  data?: unknown;
  timestamp?: number;
  server_time?: number;
}

export interface WebSocketRequestMessage {
  type?: string;
  request_id?: string;
  action?: string;
  payload?: Record<string, unknown>;
  user_id?: string | null;
  timestamp?: number;
  trace_id?: string | null;
}

export interface WebSocketResponseMessage {
  type?: string;
  request_id?: string;
  success?: boolean;
  data?: unknown;
  timestamp?: number;
  server_time?: number;
  trace_id?: string | null;
}

export interface WebSocketSubscribeMessage {
  type?: string;
  request_id?: string;
  room?: string;
  user_id?: string | null;
  timestamp?: number;
}

export type EventType = 'task.created' | 'task.started' | 'task.progress' | 'task.completed' | 'task.failed' | 'indicator.calculation.started' | 'indicator.calculation.completed' | 'indicator.calculation.failed' | 'stock.indicators.completed' | 'market.data.update' | 'market.price.update' | 'system.heartbeat' | 'system.status_changed';

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

export type TaskPriority = 100 | 200 | 500 | 800 | 900;

export interface TaskResponse {
  success?: boolean;
  message?: string;
  data?: Record<string, unknown> | null;
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

export type TaskStatus = 'pending' | 'running' | 'success' | 'failed' | 'paused' | 'cancelled';

export type TaskType = 'cron' | 'supervisor' | 'manual' | 'data_sync' | 'indicator_calc' | 'market_fetch' | 'data_processing' | 'strategy_backtest' | 'cache_cleanup' | 'market_sync' | 'notification' | 'health_check' | 'cache_warmup' | 'report_generation';

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
  chartSettings?: Record<string, unknown>;
  notifications?: Record<string, boolean>;
  privacy?: Record<string, unknown>;
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

export type WebSocketMessageType = 'request' | 'subscribe' | 'unsubscribe' | 'ping' | 'response' | 'error' | 'notification' | 'pong';
