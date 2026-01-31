/**
 * @fileoverview 仪表板模块类型定义
 * @description 提供仪表板相关的类型定义
 * @module types/dashboard
 * @version 1.0.0
 */

import type { UnifiedResponse } from '../common/response';

/**
 * 仪表板卡片配置
 */
export interface DashboardCard {
  id: string;
  title: string;
  type: 'chart' | 'table' | 'metric' | 'list';
  size?: 'small' | 'medium' | 'large';
  position?: {
    x: number;
    y: number;
    w?: number;
    h?: number;
  };
  config?: Record<string, any>;
  refreshInterval?: number;
}

/**
 * 仪表板布局
 */
export interface DashboardLayout {
  id: string;
  name: string;
  cards: DashboardCard[];
  columns?: number;
  gridType?: 'auto' | 'fixed';
}

/**
 * 仪表板数据
 */
export interface DashboardData {
  layout?: DashboardLayout;
  widgets: DashboardCard[];
  timestamp?: string;
}

/**
 * 仪表板配置响应
 */
export interface DashboardConfigResponse extends UnifiedResponse<DashboardData> {}

/**
 * Widget组件
 */
export interface DashboardWidget {
  id: string;
  type: string;
  title: string;
  config?: Record<string, any>;
}

/**
 * Widget列表响应
 */
export interface WidgetListResponse extends UnifiedResponse<DashboardWidget[]> {}
