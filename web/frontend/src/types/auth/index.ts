/**
 * @fileoverview 认证模块类型定义
 * @description 提供认证相关的类型定义
 * @module types/auth
 * @version 1.0.0
 */

import type { UnifiedResponse } from '../common/response';
import type { LoginResponse, UserProfile } from '../user';

/**
 * JWT令牌信息
 */
export interface TokenInfo {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token?: string;
}

/**
 * CSRF令牌
 */
export interface CsrfToken {
  token: string;
  expires_at?: string;
}

/**
 * 认证状态
 */
export type AuthStatus =
  | 'unauthenticated'
  | 'authenticated'
  | 'expired'
  | 'refreshing';

/**
 * 登录响应
 */
export interface AuthLoginResponse extends UnifiedResponse<TokenInfo> {}

/**
 * 登出请求
 */
export interface LogoutRequest {
  token?: string;
  allDevices?: boolean;
}

/**
 * 登出响应
 */
export interface LogoutResponse extends UnifiedResponse<null> {}

/**
 * 刷新令牌请求
 */
export interface RefreshTokenRequest {
  refresh_token: string;
}

/**
 * 刷新令牌响应
 */
export interface RefreshTokenResponse extends UnifiedResponse<TokenInfo> {}

/**
 * 获取CSRF令牌响应
 */
export interface GetCsrfTokenResponse extends UnifiedResponse<CsrfToken> {}
