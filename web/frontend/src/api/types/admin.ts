// Auto-generated types for admin domain

export interface AuditLogResponse {
  log_id?: string;
  user_id?: string | null;
  action?: string;
  resource_type?: string;
  resource_id?: string;
  details?: Record<string, unknown>;
  ip_address?: string;
  user_agent?: string;
  timestamp?: string;
}

export interface OptimizationResponse {
  operation?: string;
  status?: string;
  duration_ms?: number;
  result?: Record<string, unknown>;
}
