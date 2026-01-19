// Auto-generated types for admin domain
// Generated at: 2026-01-19T22:34:18.292675

export interface AuditLogResponse {
  log_id?: string;
  user_id?: string;
  action?: string;
  resource_type?: string;
  resource_id?: string;
  details?: Record<string, any>;
  ip_address?: string;
  user_agent?: string;
  timestamp?: string;
}

export interface LoginRequest {
  username?: string;
  password?: string;
}

export interface LoginResponse {
  access_token?: string;
  token_type?: string;
  expires_in?: number;
  user_id?: string;
  username?: string;
}

export interface OptimizationResponse {
  operation?: string;
  status?: string;
  duration_ms?: number;
  result?: Record<string, any>;
}

export interface TokenPayload {
  sub?: string;
  username?: string;
  exp?: string;
}
