/**
 * @fileoverview 设置-高级模块类型定义
 * @description 提供高级设置相关的类型定义
 * @module types/settings
 * @version 1.0.0
 */

import type { UnifiedResponse } from '../common/response';

/**
 * 高级设置
 */
export interface AdvancedSettings {
  apiRateLimit?: number;
  cacheTtl?: number;
  dataRefreshInterval?: number;
  debugMode?: boolean;
  performanceMonitoring?: boolean;
  customEndpoints?: Record<string, string>;
  experimentalFeatures?: string[];
  locale?: string;
}

/**
 * 高级设置响应
 */
export interface AdvancedSettingsResponse extends UnifiedResponse<AdvancedSettings> {}

/**
 * 更新高级设置请求
 */
export interface UpdateAdvancedSettingsRequest {
  apiRateLimit?: number;
  cacheTtl?: number;
  dataRefreshInterval?: number;
  debugMode?: boolean;
  performanceMonitoring?: boolean;
  customEndpoints?: Record<string, string>;
  experimentalFeatures?: string[];
  locale?: string;
}

/**
 * 系统配置项
 */
export interface SystemConfig {
  key: string;
  value: any;
  type: 'string' | 'number' | 'boolean' | 'object';
  description?: string;
  category?: string;
  editable?: boolean;
  requiresRestart?: boolean;
}

/**
 * 系统配置响应
 */
export interface SystemConfigResponse extends UnifiedResponse<SystemConfig[]> {}
