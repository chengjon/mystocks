/**
 * @fileoverview 用户模块类型定义
 * @description 提供用户相关的类型定义
 * @module types/user
 * @version 1.0.0
 */

import type { UnifiedResponse, UnifiedPaginatedResponse } from '../common/response';

/**
 * 用户基本信息
 */
export interface UserProfile {
  userId?: string;
  username?: string;
  email?: string;
  displayName?: string;
  avatar?: string;
  role?: string;
  status?: string;
  preferences?: Record<string, any>;
  permissions?: Record<string, any>;
  subscription?: Record<string, any>;
  statistics?: Record<string, any>;
  createdAt?: string;
  lastLoginAt?: string;
  lastUpdateAt?: string;
}

/**
 * 用户权限
 */
export type UserPermission =
  | 'read'
  | 'write'
  | 'admin'
  | 'delete'
  | 'share';

/**
 * 用户角色
 */
export type UserRole =
  | 'admin'
  | 'user'
  | 'viewer'
  | 'guest';

/**
 * 用户状态
 */
export type UserStatus =
  | 'active'
  | 'inactive'
  | 'suspended'
  | 'pending';

/**
 * 用户偏好设置
 */
export interface UserPreferences {
  theme?: 'light' | 'dark';
  language?: 'zh-CN' | 'en-US';
  timezone?: string;
  dateFormat?: string;
  notifications?: {
    email?: boolean;
    push?: boolean;
    sms?: boolean;
  };
}

/**
 * 用户登录请求
 */
export interface LoginRequest {
  username: string;
  password: string;
  rememberMe?: boolean;
}

/**
 * 用户登录响应
 */
export interface LoginResponse extends UnifiedResponse<{
  access_token: string;
  token_type: string;
  expires_in: number;
  user?: UserProfile;
}> {}

/**
 * 用户注册请求
 */
export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  displayName?: string;
}

/**
 * 用户更新请求
 */
export interface UpdateUserRequest {
  displayName?: string;
  email?: string;
  avatar?: string;
  preferences?: UserPreferences;
}

/**
 * 用户列表响应
 */
export interface UsersListResponse extends UnifiedPaginatedResponse<UserProfile[]> {}

/**
 * 用户详情响应
 */
export interface UserDetailResponse extends UnifiedResponse<UserProfile> {}
