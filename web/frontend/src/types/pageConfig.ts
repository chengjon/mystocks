/**
 * @fileoverview 页面配置类型定义模块
 * @description 提供页面配置相关的类型定义
 * @module types
 * @version 2.0.0
 * @updated 2026-02-03 - Extended with monolithic and standard page config types
 */

/**
 * 页面配置类型
 * - 'monolithic': 单体组件，包含多个 tab
 * - 'page': 标准页面配置
 */
export type PageConfigType = 'monolithic' | 'page';

/**
 * Tab 配置（用于 monolithic 组件）
 */
export interface TabConfig {
  id: string;
  apiEndpoint: string;
  wsChannel: string;
}

/**
 * Monolithic 页面配置
 * 用于包含多个 tab 的单体组件
 */
export interface MonolithicPageConfig {
  type: 'monolithic';
  routePath: string;
  title: string;
  description: string;
  component: string;
  tabs: TabConfig[];
  requiresAuth?: boolean;
}

/**
 * 标准页面配置
 * 用于单一功能的标准页面
 */
export interface StandardPageConfig {
  type: 'page';
  routePath: string;
  title: string;
  description: string;
  apiEndpoint: string;
  wsChannel: string;
  component: string;
  requiresAuth?: boolean;
}

/**
 * 页面配置联合类型（判别联合）
 */
export type PageConfig = MonolithicPageConfig | StandardPageConfig;

/**
 * 路由名称类型
 */
export type RouteName = string;

/**
 * 类型守卫：检查是否为 Monolithic 配置
 */
export function isMonolithicConfig(config: PageConfig): config is MonolithicPageConfig {
  return config.type === 'monolithic';
}

/**
 * 类型守卫：检查是否为 Standard 配置
 */
export function isStandardConfig(config: PageConfig): config is StandardPageConfig {
  return config.type === 'page';
}

/**
 * 路由名称验证函数
 */
export function isRouteName(name: string): name is RouteName {
  const routeNames: string[] = [
    'dashboard',
    'market-realtime',
    'market-overview',
    'market-analysis',
    'market-industry',
    'market-technical',
    'trading-signals',
    'trading-history',
    'trading-positions',
    'trading-performance',
    'trading-attribution',
    'strategy-design',
    'strategy-management',
    'strategy-backtest',
    'strategy-gpu-backtest',
    'strategy-optimization',
    'risk-overview',
    'risk-alerts',
    'risk-analysis',
    'portfolio-overview',
    'portfolio-analysis',
    'settings',
    'monitoring',
    'analysis'
  ];
  return routeNames.includes(name);
}
