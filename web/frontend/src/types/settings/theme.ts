/**
 * @fileoverview 设置-主题模块类型定义
 * @description 提供主题设置相关的类型定义
 * @module types/settings
 * @version 1.0.0
 */

import type { UnifiedResponse } from '../common/response';

/**
 * 主题模式
 */
export type ThemeMode = 'light' | 'dark' | 'auto';

/**
 * 颜设方案
 */
export type ColorScheme = 'default' | 'blue' | 'green' | 'purple' | 'orange' | 'red';

/**
 * 主题配置
 */
export interface ThemeSettings {
  mode: ThemeMode;
  colorScheme: ColorScheme;
  primaryColor?: string;
  fontSize?: 'small' | 'medium' | 'large';
  density?: 'compact' | 'comfortable' | 'spacious';
  borderRadius?: number;
  customCss?: string;
}

/**
 * 主题设置响应
 */
export interface ThemeSettingsResponse extends UnifiedResponse<ThemeSettings> {}

/**
 * 更新主题设置请求
 */
export interface UpdateThemeSettingsRequest {
  mode?: ThemeMode;
  colorScheme?: ColorScheme;
  primaryColor?: string;
  fontSize?: 'small' | 'medium' | 'large';
  density?: 'compact' | 'comfortable' | 'spacious';
  borderRadius?: number;
  customCss?: string;
}

/**
 * 主题预设
 */
export interface ThemePreset {
  id: string;
  name: string;
  description?: string;
  settings: ThemeSettings;
  preview?: string;
}

/**
 * 主题预设列表响应
 */
export interface ThemePresetListResponse extends UnifiedResponse<ThemePreset[]> {}
