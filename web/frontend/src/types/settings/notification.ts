/**
 * @fileoverview 设置-通知模块类型定义
 * @description 提供通知设置相关的类型定义
 * @module types/settings
 * @version 1.0.0
 */

import type { UnifiedResponse } from '../common/response';

/**
 * 通知类型
 */
export type NotificationType =
  | 'system'
  | 'trading'
  | 'alert'
  | 'reminder'
  | 'promotion';

/**
 * 通知优先级
 */
export type NotificationPriority = 'low' | 'medium' | 'high' | 'urgent';

/**
 * 通知渠道
 */
export type NotificationChannel = 'email' | 'push' | 'sms' | 'browser' | 'webhook';

/**
 * 通知设置
 */
export interface NotificationSettings {
  enabled: boolean;
  channels: NotificationChannel[];
  types: NotificationType[];
  priority: NotificationPriority;
  quietHours?: {
    start: string;
    end: string;
  };
  soundEnabled?: boolean;
}

/**
 * 通知设置响应
 */
export interface NotificationSettingsResponse extends UnifiedResponse<NotificationSettings> {}

/**
 * 更新通知设置请求
 */
export interface UpdateNotificationSettingsRequest {
  enabled?: boolean;
  channels?: NotificationChannel[];
  types?: NotificationType[];
  priority?: NotificationPriority;
  quietHours?: {
    start: string;
    end: string;
  };
  soundEnabled?: boolean;
}

/**
 * 通知项
 */
export interface NotificationItem {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  priority: NotificationPriority;
  channels: NotificationChannel[];
  data?: Record<string, any>;
  read: boolean;
  createdAt?: string;
  expiresAt?: string;
  actionUrl?: string;
  actionText?: string;
  icon?: string;
  category?: string;
}

/**
 * 通知列表响应
 */
export interface NotificationListResponse extends UnifiedResponse<NotificationItem[]> {}

/**
 * 标记已读请求
 */
export interface MarkAsReadRequest {
  notificationIds: string[];
  readAll?: boolean;
}

/**
 * 标记已读响应
 */
export interface MarkAsReadResponse extends UnifiedResponse<null> {}
