/**
 * @fileoverview 设置-账户模块类型定义
 * @description 提供账户设置相关的类型定义
 * @module types/settings
 * @version 1.0.0
 */

import type { UnifiedResponse } from '../common/response';

/**
 * 账户设置
 */
export interface AccountSettings {
  userId?: string;
  username?: string;
  email?: string;
  displayName?: string;
  avatar?: string;
  theme?: 'light' | 'dark';
  language?: string;
  timezone?: string;
  dateFormat?: string;
  notifications?: {
    email?: boolean;
    push?: boolean;
    sms?: boolean;
    browser?: boolean;
  };
  preferences?: Record<string, any>;
}

/**
 * 账户设置响应
 */
export interface AccountSettingsResponse extends UnifiedResponse<AccountSettings> {}

/**
 * 更新账户设置请求
 */
export interface UpdateAccountSettingsRequest {
  displayName?: string;
  email?: string;
  avatar?: string;
  theme?: string;
  language?: string;
  timezone?: string;
  dateFormat?: string;
  notifications?: {
    email?: boolean;
    push?: boolean;
    sms?: boolean;
  };
  preferences?: Record<string, any>;
}

/**
 * 修改密码请求
 */
export interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

/**
 * 修改密码响应
 */
export interface ChangePasswordResponse extends UnifiedResponse<null> {}
