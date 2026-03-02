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
