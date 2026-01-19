/**
 * Common Utility Types
 *
 * Shared utility types used across different domains in the frontend.
 * These types provide common patterns for data handling, API responses,
 * and utility interfaces that are reused throughout the application.
 */

// ========== Core Type Aliases ==========

/**
 * Position item type alias (ViewModel)
 * Represents a trading position with essential fields
 */
export type PositionVM = {
  symbol: string;
  name: string;
  quantity: number;
  average_cost: number;
  current_price: number;
  market_value: number;
  unrealized_pnl: number;
  unrealized_pnl_percent: number;
  exchange: string;
  position_type: 'long' | 'short';
};

/**
 * List generic utility type
 * Provides type-safe array operations with metadata
 */
export type list<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
};

/**
 * Date type alias
 * Standardized date representation across the application
 */
export type date_type = string; // ISO 8601 format: "2025-01-19T10:30:00Z"

// ========== API Response Types ==========

/**
 * Standard API response wrapper
 */
export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error_code?: string;
  timestamp: string;
  request_id: string;
}

/**
 * Paginated API response
 */
export interface PaginatedResponse<T = any> extends APIResponse<list<T>> {
  pagination: {
    current_page: number;
    total_pages: number;
    total_items: number;
    items_per_page: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

/**
 * Error response structure
 */
export interface APIError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
  path?: string;
  method?: string;
}

// ========== Pagination and Filtering Types ==========

/**
 * Standard pagination parameters
 */
export interface PaginationParams {
  page?: number;
  page_size?: number;
  offset?: number;
  limit?: number;
}

/**
 * Search parameters
 */
export interface SearchParams {
  query?: string;
  fields?: string[];
  case_sensitive?: boolean;
  fuzzy?: boolean;
}

/**
 * Filter parameters
 */
export interface FilterParams {
  [key: string]: any;
}

/**
 * Standard API response wrapper (ViewModel)
 */
export interface APIResponseVM<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error_code?: string;
  timestamp: string;
  request_id: string;
}

/**
 * Paginated API response (ViewModel)
 */
export interface PaginatedResponseVM<T = any> extends APIResponseVM<list<T>> {
  pagination: {
    current_page: number;
    total_pages: number;
    total_items: number;
    items_per_page: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

/**
 * Error response structure (ViewModel)
 */
export interface APIErrorVM {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
  path?: string;
  method?: string;
}

/**
 * Standard pagination parameters (ViewModel)
 */
export interface PaginationParamsVM {
  page?: number;
  page_size?: number;
  offset?: number;
  limit?: number;
}

/**
 * Search parameters (ViewModel)
 */
export interface SearchParamsVM {
  query?: string;
  fields?: string[];
  case_sensitive?: boolean;
  fuzzy?: boolean;
}

/**
 * Filter parameters (ViewModel)
 */
export interface FilterParamsVM {
  [key: string]: any;
}

/**
 * Sort parameters (ViewModel)
 */
export interface SortParamsVM {
  field: string;
  direction: 'asc' | 'desc';
}

// ========== Validation Types ==========

/**
 * Validation result
 */
export interface ValidationResult {
  is_valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

/**
 * Validation error
 */
export interface ValidationError {
  field: string;
  code: string;
  message: string;
  value?: any;
  expected_type?: string;
}

/**
 * Validation warning
 */
export interface ValidationWarning {
  field: string;
  code: string;
  message: string;
  suggestion?: string;
}

// ========== Upload and File Types ==========

/**
 * File upload result
 */
export interface UploadResult {
  file_id: string;
  filename: string;
  original_filename: string;
  size: number;
  mime_type: string;
  url: string;
  uploaded_at: date_type;
  checksum: string;
}

/**
 * Validation result (ViewModel)
 */
export interface ValidationResultVM {
  is_valid: boolean;
  errors: ValidationErrorVM[];
  warnings: ValidationWarningVM[];
}

/**
 * Validation error (ViewModel)
 */
export interface ValidationErrorVM {
  field: string;
  code: string;
  message: string;
  value?: any;
  expected_type?: string;
}

/**
 * Validation warning (ViewModel)
 */
export interface ValidationWarningVM {
  field: string;
  code: string;
  message: string;
  suggestion?: string;
}

/**
 * File upload result (ViewModel)
 */
export interface UploadResultVM {
  file_id: string;
  filename: string;
  original_filename: string;
  size: number;
  mime_type: string;
  url: string;
  uploaded_at: date_type;
  checksum: string;
}

/**
 * Upload progress (ViewModel)
 */
export interface UploadProgressVM {
  loaded: number;
  total: number;
  percentage: number;
  speed: number; // bytes per second
  remaining_time: number; // seconds
}

// ========== WebSocket Types ==========

/**
 * WebSocket message base (ViewModel)
 */
export interface WSMessageVM {
  type: string;
  timestamp: date_type;
  id: string;
}

/**
 * WebSocket subscription message (ViewModel)
 */
export interface WSSubscriptionVM extends WSMessageVM {
  type: 'subscribe' | 'unsubscribe';
  channel: string;
  params?: Record<string, any>;
}

/**
 * WebSocket data message (ViewModel)
 */
export interface WSDataMessageVM<T = any> extends WSMessageVM {
  type: 'data';
  channel: string;
  data: T;
}

/**
 * WebSocket error message (ViewModel)
 */
export interface WSErrorMessageVM extends WSMessageVM {
  type: 'error';
  code: string;
  message: string;
  details?: any;
}

/**
 * WebSocket subscription message
 */
export interface WSSubscription extends WSMessage {
  type: 'subscribe' | 'unsubscribe';
  channel: string;
  params?: Record<string, any>;
}

/**
 * WebSocket data message
 */
export interface WSDataMessage<T = any> extends WSMessage {
  type: 'data';
  channel: string;
  data: T;
}

/**
 * Validation result (ViewModel)
 */
export interface ValidationResultVM {
  is_valid: boolean;
  errors: ValidationErrorVM[];
  warnings: ValidationWarningVM[];
}

export interface ValidationErrorVM {
  field: string;
  code: string;
  message: string;
  value?: any;
  expected_type?: string;
}

export interface ValidationWarningVM {
  field: string;
  code: string;
  message: string;
  suggestion?: string;
}

export interface UploadResultVM {
  file_id: string;
  filename: string;
  original_filename: string;
  size: number;
  mime_type: string;
  url: string;
  uploaded_at: date_type;
  checksum: string;
}

export interface UploadProgressVM {
  loaded: number;
  total: number;
  percentage: number;
  speed: number; // bytes per second
  remaining_time: number; // seconds
}

export interface WSMessageVM {
  type: string;
  timestamp: date_type;
  id: string;
}

export interface WSSubscriptionVM extends WSMessageVM {
  type: 'subscribe' | 'unsubscribe';
  channel: string;
  params?: Record<string, any>;
}

export interface WSDataMessageVM<T = any> extends WSMessageVM {
  type: 'data';
  channel: string;
  data: T;
}

export interface WSErrorMessageVM extends WSMessageVM {
  type: 'error';
  code: string;
  message: string;
  details?: any;
}

// ========== Utility Types ==========

/**
 * Optional wrapper for conditional fields
 */
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

/**
 * Deep partial type for nested objects
 */
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

/**
 * Extract keys of certain type
 */
export type KeysOfType<T, U> = {
  [K in keyof T]: T[K] extends U ? K : never;
}[keyof T];

/**
 * Non-nullable type
 */
export type NonNullable<T> = T extends null | undefined ? never : T;

/**
 * Function type for async operations
 */
export type AsyncFunction<T = any, Args extends any[] = []> = (...args: Args) => Promise<T>;

/**
 * Timeout wrapper
 */
export interface TimeoutOptions {
  timeout_ms?: number;
  retries?: number;
  retry_delay_ms?: number;
}

// ========== Constants and Enums ==========

/**
 * HTTP methods
 */
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS';

/**
 * Data loading states
 */
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

/**
 * Theme modes
 */
export type ThemeMode = 'light' | 'dark' | 'auto';

/**
 * Language codes
 */
export type LanguageCode = 'zh-CN' | 'en-US' | 'zh-TW';

/**
 * Currency codes
 */
export type CurrencyCode = 'CNY' | 'USD' | 'HKD' | 'EUR' | 'JPY';