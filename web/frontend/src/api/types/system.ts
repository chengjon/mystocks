// Auto-generated types for system domain
// Generated at: 2026-01-29T13:43:35.813369

export interface DataClassificationStats {
  description?: string;
  record_count?: number;
  storage_size_gb?: number;
  database?: string;
  compression_ratio?: number;
}

export interface DataRoutingRequest {
  data_category?: string;
  symbol?: string | null;
  date_range?: Record<string, string> | null;
}

export interface DataRoutingResponse {
  route_selected?: string;
  estimated_records?: number;
  query_complexity?: string;
  recommended_strategy?: string;
}

export interface DatabaseHealthResponse {
  database_type?: string;
  connection_status?: string;
  response_time_ms?: number;
  active_connections?: number;
  total_tables?: number;
  last_health_check?: string;
}
