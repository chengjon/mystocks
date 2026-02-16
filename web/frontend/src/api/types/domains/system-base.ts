// System Base & Common Infrastructure Types

export type Dict = Record<string, any>;
export type List<T = any> = T[];

export interface UnifiedResponse<T = any> {
  success: boolean;
  code: number;
  message: string;
  data: T;
  timestamp: string;
  request_id: string;
  errors?: any;
}

export interface APIResponse {
  success?: boolean;
  data?: Record<string, any> | null;
  error?: ErrorDetail | null;
  timestamp?: string;
  code?: number;
  message?: string;
  request_id?: string;
}

export interface BaseResponse {
  success?: boolean;
  message?: string;
  data?: any | null;
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
  data?: any | null;
  timestamp?: number;
}

export interface MessageResponse {
  success?: boolean;
  message?: string;
  data?: Record<string, any> | null;
}

export type MessageStatus = 'pending' | 'in_progress' | 'success' | 'failed' | 'retry' | 'dead_letter';

export interface ErrorDetail {
  error_code?: string;
  error_message?: string;
  details?: Record<string, any> | null;
}

export interface ErrorResponse {
  error?: string;
  detail?: string | null;
  message?: string;
  error_code?: string;
  error_message?: string;
  details?: Record<string, any> | null;
  timestamp?: string;
  success?: 'False';
  path?: string | null;
  request_id?: string | null;
}

export interface ErrorResponseModel {
  code?: string;
  message?: string;
  details?: any | null;
  timestamp?: number;
}

export interface CommonError {
  code?: number;
  message?: string;
  data?: Record<string, any> | null;
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

export interface PagedResponse<T = any> {
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

export interface PaginatedResponse<T = any> {
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
  filters?: Record<string, any> | null;
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
  data?: Record<string, any>;
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
  results?: any[];
  execution_time?: number;
  id?: string | null;
  success?: boolean;
  data?: any | null;
  error?: string | null;
}

export interface HealthCheckResponse {
  status?: string;
  version?: string;
  uptime?: number;
  timestamp?: string;
  services?: Record<string, any> | null;
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
  error_details?: Record<string, any> | null;
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
  data?: any;
  timestamp?: number;
  server_time?: number;
}

export interface WebSocketRequestMessage {
  type?: string;
  request_id?: string;
  action?: string;
  payload?: Record<string, any>;
  user_id?: string | null;
  timestamp?: number;
  trace_id?: string | null;
}

export interface WebSocketResponseMessage {
  type?: string;
  request_id?: string;
  success?: boolean;
  data?: any;
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
