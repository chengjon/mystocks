/**
 * @fileoverview 设置-安全模块类型定义
 * @description 提供安全设置相关的类型定义
 * @module types/settings
 * @version 1.0.0
 */

import type { UnifiedResponse } from '../common/response';

/**
 * 安全级别
 */
export type SecurityLevel = 'low' | 'medium' | 'high' | 'critical';

/**
 * 双因素认证类型
 */
export type TwoFactorType = 'sms' | 'email' | 'totp' | 'app';

/**
 * 登录会话管理
 */
export interface SessionInfo {
  id: string;
  device: string;
  ip?: string;
  location?: string;
  createdAt: string;
  lastActivityAt: string;
  expiresAt: string;
}

/**
 * 安全设置
 */
export interface SecuritySettings {
  twoFactorEnabled?: boolean;
  twoFactorType?: TwoFactorType;
  sessionTimeout?: number;
  maxSessions?: number;
  ipWhitelist?: string[];
  loginAlerts?: {
    newDevice?: boolean;
    newLocation?: boolean;
  unusualActivity?: boolean;
  };
}

/**
 * 安全设置响应
 */
export interface SecuritySettingsResponse extends UnifiedResponse<SecuritySettings> {}

/**
 * 更新安全设置请求
 */
export interface UpdateSecuritySettingsRequest {
  twoFactorEnabled?: boolean;
  twoFactorType?: TwoFactorType;
  sessionTimeout?: number;
  maxSessions?: number;
  ipWhitelist?: string[];
  loginAlerts?: {
    newDevice?: boolean;
    newLocation?: boolean;
    unusualActivity?: boolean;
  };
}

/**
 * 会话列表响应
 */
export interface SessionListResponse extends UnifiedResponse<SessionInfo[]> {}

/**
 * 终止会话请求
 */
export interface TerminateSessionRequest {
  sessionId: string;
}

/**
 * 终止会话响应
 */
export interface TerminateSessionResponse extends UnifiedResponse<null> {}

/**
 * 安全日志项
 */
export interface SecurityLog {
  id: string;
  type: 'login' | 'logout' | 'session_created' | 'session_terminated' | 'settings_changed';
  timestamp: string;
  ip?: string;
  device?: string;
  location?: string;
  details?: Record<string, any>;
}

/**
 * 安全日志列表响应
 */
export interface SecurityLogListResponse extends UnifiedResponse<SecurityLog[]> {}
