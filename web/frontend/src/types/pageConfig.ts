/**
 * @fileoverview 页面配置类型定义模块
 * @description 提供页面配置相关的类型定义
 * @module types
 * @version 1.0.0
 */

/**
 * 页面类型枚举
 */
export type PageConfigType = 'monolithic' | 'standard' | 'tabbed';

/**
 * 页面配置项
 */
export interface PageConfig {
  id: string;
  name: string;
  path: string;
  component?: string;
  icon?: string;
  meta?: Record<string, any>;
  permissions?: string[];
  layout?: 'dashboard' | 'sidebar' | 'full' | 'custom';
  cache?: boolean;
  prefetch?: boolean;
}

/**
 * Tab配置
 */
export interface TabConfig {
  id: string;
  label: string;
  path: string;
  icon?: string;
  disabled?: boolean;
  badge?: number | string;
  closable?: boolean;
}

/**
 * 页面配置响应
 */
export interface PageConfigResponse {
  pages: PageConfig[];
  tabs: TabConfig[];
  defaultPage?: string;
  layout?: 'dashboard' | 'sidebar' | 'full' | 'custom';
}

/**
 * 路由名称类型
 */
export type RouteName = string;

/**
 * 路由名称验证函数
 */
export function isRouteName(name: string): name is RouteName {
  const routeNames: string[] = [
    'dashboard',
    'market',
    'trading',
    'portfolio',
    'settings',
    'monitoring',
    'analysis'
  ];
  return routeNames.includes(name);
}
