
export interface WencaiRefreshResponse {
  status?: string;
  message?: string;
  task_id?: string | null;
  query_name?: string;
}

export interface WencaiResultItem {
  data?: Record<string, any>;
  fetch_time?: string;
}

export interface WencaiResultsResponse {
  query_name?: string;
  total?: number;
  results?: Record<string, any>[];
  columns?: string[];
  latest_fetch_time?: string | null;
}

export interface WencaiStatsResponse {
  total_queries?: number;
  active_queries?: number;
  total_records?: number;
  last_refresh_time?: string | null;
}

